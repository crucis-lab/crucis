"""B03 local lifecycle, effect evidence and lost-reply recovery."""

from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
import json
import os
from pathlib import Path
import tempfile
import unittest

from crucis_causal.execution import api
from crucis_causal.execution.journal import Journal
from crucis_causal.execution.model import Builder, contract, identity, index, scope, unknown, unknown_ref
from crucis_causal.measurement import Coordinator, Evaluator, Limits, exact_number
from s4_wire_examples import local
from test_audit_measurement_planning import bound, scenario


PLAN = local("plan.graph", "plan")


class DroppedReply(Exception):
    pass


@contextmanager
def work_fixture():
    parent = Path(os.environ.get("CRUCIS_TEST_TEMP", tempfile.gettempdir())).resolve()
    with tempfile.TemporaryDirectory(prefix="crucis-s4-work-", dir=parent) as tmp:
        root = Path(tmp).resolve()
        assert root.parent == parent
        journal = Journal(root)
        b = Builder("S4 local journal fixture")
        target = b.add("target", {"definition": contract("s4.fixture"), "scope": scope(),
                                   "subjects": index(), "requirements": index(), "relations": index()})
        account = b.add("account", {"purpose": "execute", "target": target,
                                     "related_accounts": index()})
        audience = b.add("audience", {
            "purpose": contract("s4.fixture"), "recipients": index(),
            "disclosure_policy": unknown_ref("s1.policy"), "authority": unknown(),
        })
        projection = b.add("projection_view", {
            "view_role": "audience_projection", "audience": audience,
            "projection_contract": contract("s4.fixture"), "members": index([account]),
            "claims": index(), "limits": index(),
        })
        initial = b.package(projection)
        context = api.RuntimeContext(api.PinnedReadContext((), api.supplied_read(()), None,
                                                           api.Limits()), journal.control(account))
        opened = journal.append(account, "0", identity(),
                                api.CommitDelta(tuple(initial["records"]), (projection,)), context)
        assert opened.state == "completed", opened.issues
        yield root, journal, account, context


def work_inputs(*, limits=Limits(), callback=None, local_hold=False):
    package, supplied, registry, _ = scenario(local_hold=local_hold)
    view = bound(package, supplied, limits=limits)
    from s4_wire_examples import contract as s4_contract
    descriptor = registry.get(s4_contract("s4.q01"))
    calls = []

    def calculate(output, budget):
        calls.append(output.key)
        if callback is not None:
            return callback(output, budget)
        value = budget.divide(2, 2) if output.key == "covered" else budget.add(1, 1).numerator
        return {"tag": "defined", "value": exact_number(value)}

    return view, Evaluator(descriptor, b'{"example":true}', calculate), calls


class MeasurementWorkTests(unittest.TestCase):
    def test_completed_work_is_recorded_and_cold_reopened_without_reexecution(self):
        view, evaluator, calls = work_inputs()
        with work_fixture() as (root, journal, account, context):
            service = Coordinator(journal, account, context, [evaluator])
            result = service.execute(PLAN, "run1", view)
            self.assertEqual(result.state, "completed")
            self.assertEqual(calls, ["covered", "judged_count"])
            self.assertEqual(service.record(result).state, "committed")
            reopened = Journal(root)
            cold = Coordinator(reopened, account, replace(context, control=reopened.control(account)), [])
            recovered = cold.recover("run1", result.basis_digest)
            self.assertEqual(recovered.state, "recorded")
            self.assertEqual(recovered.occurrence_id, result.occurrence_id)
            event = json.loads(recovered.event_bytes)
            self.assertEqual([e["key"] for e in event["emissions"]], calls)
            covered = event["plan_evidence"]["outputs"][0]
            self.assertEqual((covered["binding"]["record_id"], covered["scope"]["record_id"]),
                             ("bind.graph", "scope.covered"))
            self.assertEqual(cold.record(result).state, "committed")
            self.assertEqual(calls, ["covered", "judged_count"])

    def test_record_commit_reply_loss_does_not_call_the_evaluator_again(self):
        view, evaluator, calls = work_inputs()
        with work_fixture() as (root, journal, account, context):
            count = 0

            def lose_third_ack(label):
                nonlocal count
                if label == "after_journal_commit":
                    count += 1
                    if count == 3:
                        raise DroppedReply()

            service = Coordinator(journal, account, replace(context, fault=lose_third_ack), [evaluator])
            result = service.execute(PLAN, "run2", view)
            self.assertEqual(service.record(result).state, "unknown")
            self.assertEqual(service.recover("run2", result.basis_digest).state, "recorded")
            self.assertEqual(service.record(result).state, "committed")
            self.assertEqual(calls, ["covered", "judged_count"])

    def test_loss_of_intent_reply_never_starts_the_evaluator(self):
        view, evaluator, calls = work_inputs()
        with work_fixture() as (_, journal, account, context):
            def lose_ack(label):
                if label == "after_journal_commit":
                    raise DroppedReply()

            service = Coordinator(journal, account, replace(context, fault=lose_ack), [evaluator])
            report = service.execute(PLAN, "run3", view)
            self.assertEqual(report.state, "admission_unconfirmed")
            self.assertEqual(service.recover("run3", report.basis_digest).state, "intent_observed")
            self.assertEqual(service.execute(PLAN, "run3", view).state, "held")
            self.assertEqual(calls, [])

    def test_interruption_after_entry_preserves_uncertain_outcome_and_allows_fresh_id(self):
        view, evaluator, calls = work_inputs()
        with work_fixture() as (root, journal, account, context):
            def interruption(label):
                if label == "after_entry":
                    raise DroppedReply()

            first = Coordinator(journal, account, context, [evaluator], fault=interruption)
            with self.assertRaises(DroppedReply):
                first.execute(PLAN, "interrupted", view)
            reopened = Journal(root)
            next_service = Coordinator(reopened, account, replace(context, control=reopened.control(account)),
                                       [evaluator])
            report = next_service.execute(PLAN, "interrupted", view)
            self.assertEqual(report.state, "held")
            observed = next_service.recover("interrupted", report.basis_digest)
            self.assertEqual(observed.state, "entry_observed")
            self.assertEqual(calls, [])
            fresh = next_service.execute(PLAN, "fresh", view)
            self.assertNotEqual(fresh.occurrence_id, observed.occurrence_id)
            self.assertEqual(calls, ["covered", "judged_count"])

    def test_wrong_basis_and_read_only_context_do_not_run(self):
        view, evaluator, calls = work_inputs()
        with work_fixture() as (_, journal, account, context):
            read_only = replace(context, control=journal.control(account, rights=("read",)))
            deny = Coordinator(journal, account, read_only, [evaluator])
            self.assertEqual(deny.execute(PLAN, "denied", view).state, "held")
            self.assertEqual(calls, [])
            live = Coordinator(journal, account, context, [evaluator])
            report = live.execute(PLAN, "run4", view)
            self.assertEqual(live.recover("run4", "0" * 64).state, "disputed")
            self.assertEqual(live.record(replace(report, basis_digest="0" * 64)).state, "held")
            self.assertEqual(calls, ["covered", "judged_count"])

    def test_concurrent_admission_of_the_same_invocation_has_one_evaluator_call_per_role(self):
        view, evaluator, calls = work_inputs()
        with work_fixture() as (_, journal, account, context):
            services = [Coordinator(journal, account, context, [evaluator]) for _ in range(2)]
            with ThreadPoolExecutor(max_workers=2) as pool:
                outcomes = list(pool.map(lambda service: service.execute(PLAN, "shared", view),
                                         services))
            self.assertEqual(sorted(report.state for report in outcomes), ["completed", "held"])
            self.assertEqual(calls, ["covered", "judged_count"])

    def test_role_hold_can_coexist_with_emission_and_failed_work_has_zero_emissions(self):
        view, evaluator, _ = work_inputs(limits=Limits(rational_operations=1))
        with work_fixture() as (_, journal, account, context):
            service = Coordinator(journal, account, context, [evaluator])
            partial = service.execute(PLAN, "partial", view)
            self.assertEqual(partial.state, "partial")
            self.assertEqual([row.output_key for row in partial.emissions.emissions], ["covered"])
            self.assertEqual(partial.issues[0].code, "s4.arithmetic_operation_limit")
            self.assertEqual(service.record(partial).state, "committed")

            def bad(output, budget):
                return {"tag": "defined", "value": 0}

            invalid = Evaluator(evaluator.descriptor, evaluator.implementation, bad)
            another = Coordinator(journal, account, context, [invalid])
            failed = another.execute(PLAN, "failed", view)
            self.assertEqual(failed.state, "failed")
            self.assertEqual(failed.emissions.emissions, ())
            self.assertEqual(another.record(failed).state, "committed")
