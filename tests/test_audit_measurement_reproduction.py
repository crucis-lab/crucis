"""B08 recorded original and replay evidence, exact scope and disagreement."""

from dataclasses import replace
from fractions import Fraction
import unittest

from crucis_causal.execution.api import supplied_read
from crucis_causal.measurement import (
    Coordinator, Evaluator, ExactComparator, ReplayGoal, compare, exact_number, resolve,
)
from s4_wire_examples import keyed, local
from test_audit_measurement_planning import bound, scenario
from test_audit_measurement_wire import record
from test_audit_measurement_work import DroppedReply, PLAN, work_fixture


def replay_case(with_mask=False):
    package, sources, registry, _ = scenario()
    package["records"] = [row for row in package["records"]
                          if row["id"] != "calc.graph" and not row["id"].startswith("val.graph.")]
    if with_mask:
        for item in (record(package, "def.graph")["payload"]["output_roles"][1],
                     record(package, "proc.graph")["payload"]["output_roles"][1],
                     record(package, "intent.graph")["payload"]["goals"][1],
                     record(package, "plan.graph")["payload"]["outputs"][1]):
            item["key"] = "judgment_mask"
            if "output_role" in item:
                item["output_role"] = "judgment_mask"
        from crucis_causal.measurement import ProcedureDescriptor, Registry
        proc = record(package, "proc.graph")["payload"]
        registry = Registry([ProcedureDescriptor.from_declaration(
            proc["definition"], proc["implementation"]["content_pin"]["digest"],
            proc["slots"], proc["output_roles"],
        )])
    return bound(package, sources), registry, package, sources


def evaluator_for(registry, *, alternate=False, diagnostic=False):
    descriptor = registry.get({"name": "s4.q01", "version": "0.1.0-proposal.1"})

    def call(output, budget):
        if output.output_role == "judgment_mask":
            observed = {"AB": {"value_kind": "boolean", "value": True}}
            if not alternate:
                observed["BC"] = {"value_kind": "boolean", "value": True}
            return {"tag": "defined", "value": keyed(**observed)}
        if diagnostic:
            return {"tag": "undefined", "reason": "zero_judged_denominator",
                    "basis": [local("src", "source")]}
        return {"tag": "defined", "value": exact_number(1 if alternate else Fraction(1))}

    return Evaluator(descriptor, b'{"example":true}', call)


def run(service, invocation, view):
    report = service.execute(PLAN, invocation, view)
    assert report.state == "completed", report
    assert service.record(report).state == "committed"
    return report


class ReproductionCases(unittest.TestCase):
    def test_exact_quantity_agreement_requires_distinct_work(self):
        view, registry, _, _ = replay_case()
        with work_fixture() as (_, journal, account, context):
            a = Coordinator(journal, account, context, [evaluator_for(registry)])
            b = Coordinator(journal, account, context, [evaluator_for(registry, alternate=True)])
            left, right = run(a, "original", view), run(b, "replay", view)
            goal = ReplayGoal.bind(PLAN, "original", "replay", left.basis_digest, right.basis_digest,
                                   ExactComparator("covered"))
            report = compare(goal, view, registry, a, b)
            self.assertEqual(report.state, "agreement")
            self.assertNotEqual(report.original_occurrence, report.replay_occurrence)
            repeated = replace(goal, replay_invocation="original")
            self.assertEqual(compare(repeated, view, registry, a, a).reason, "separate_replay_required")

    def test_same_scalar_and_different_rederived_mask_disagree(self):
        view, registry, _, _ = replay_case(with_mask=True)
        with work_fixture() as (_, journal, account, context):
            a = Coordinator(journal, account, context, [evaluator_for(registry)])
            b = Coordinator(journal, account, context, [evaluator_for(registry, alternate=True)])
            left, right = run(a, "orig-mask", view), run(b, "replay-mask", view)
            goal = ReplayGoal.bind(PLAN, "orig-mask", "replay-mask", left.basis_digest, right.basis_digest,
                                   ExactComparator("covered", ("judgment_mask",), "mask_derivation"))
            report = compare(goal, view, registry, a, b)
            self.assertEqual(report.state, "disagreement")
            self.assertEqual(report.differences, ("judgment_mask",))
            too_narrow = replace(goal, comparator=ExactComparator("covered", boundary="mask_derivation"))
            self.assertEqual(compare(too_narrow, view, registry, a, b).reason,
                             "derived_mask_comparator_required")
            score_only = replace(goal, comparator=ExactComparator("covered", boundary="score_only"))
            self.assertEqual(compare(score_only, view, registry, a, b).reason,
                             "pinned_input_mask_required")

    def test_changed_basis_and_denied_original_access(self):
        view, registry, package, sources = replay_case()
        package["snapshot_id"] = "snapshot.changed"
        newer = bound(package, sources)
        with work_fixture() as (_, journal, account, context):
            service = Coordinator(journal, account, context, [evaluator_for(registry)])
            left, right = run(service, "old", view), run(service, "changed", newer)
            goal = ReplayGoal.bind(PLAN, "old", "changed", left.basis_digest, right.basis_digest,
                                   ExactComparator("covered"))
            self.assertEqual(compare(goal, view, registry, service, service).state, "basis_mismatch")
            hidden = resolve(view.snapshot, sources, supplied_read([view.snapshot.snapshot_id]))
            report = compare(goal, hidden, registry, service, service)
            self.assertEqual((report.state, report.reason), ("held", "original_basis_unavailable"))

    def test_incomplete_work_and_diagnostic_comparator(self):
        view, registry, _, _ = replay_case()
        with work_fixture() as (_, journal, account, context):
            selected = evaluator_for(registry, diagnostic=True)
            service = Coordinator(journal, account, context, [selected])
            left = run(service, "diag", view)

            def interrupt(label):
                if label == "after_entry":
                    raise DroppedReply()

            interrupted = Coordinator(journal, account, context, [selected], fault=interrupt)
            with self.assertRaises(DroppedReply):
                interrupted.execute(PLAN, "interrupted-replay", view)
            goal = ReplayGoal.bind(PLAN, "diag", "interrupted-replay", left.basis_digest,
                                   left.basis_digest, ExactComparator("covered"))
            self.assertEqual(compare(goal, view, registry, service, service).state, "incomplete")
            second = run(service, "diag-replay", view)
            finished = replace(goal, replay_invocation="diag-replay", replay_basis=second.basis_digest)
            self.assertEqual(compare(finished, view, registry, service, service).reason,
                             "diagnostic_comparator_required")
            admitted = replace(finished, comparator=ExactComparator("covered", compare_undefined=True))
            self.assertEqual(compare(admitted, view, registry, service, service).state, "agreement")
