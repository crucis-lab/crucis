"""B11 normal CLI and scientific work-to-record integration."""

from fractions import Fraction
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

from crucis_causal.connections.codec import dumps as dump_s1
from crucis_causal.connections.evidence import capture_bytes
from crucis_causal.connections.model import Builder
from crucis_causal.execution.api import supplied_read
from crucis_causal.measurement import (
    Coordinator, Evaluator, ProcedureDescriptor, ProfileCriterion, Registry, assess, dumps,
    evaluate_posterior, materialize_recorded,
)
from crucis_causal.measurement import posterior as posterior_module
from crucis_causal.measurement.procedure_inputs import exact
from s4_wire_examples import VERSION, category, contract, external, keyed, local, pin, rational
from test_audit_measurement_planning import bound, scenario
from test_audit_measurement_wire import GOLDENS, record
from test_audit_measurement_work import PLAN, work_fixture


def actual_posterior():
    package, supplied, _, _ = scenario()
    package["records"] = [r for r in package["records"]
                          if r["id"] != "calc.graph" and not r["id"].startswith("val.graph.")]
    raw = Path(posterior_module.__file__).read_bytes()
    b = Builder("Selected Q06 implementation artifact")
    artifact = capture_bytes(b, raw)
    oracle = b'{"conditional_on":"model-and-event-d","h0":"1/5","h1":"4/5"}'
    receipt = capture_bytes(b, oracle)
    source = b.package([artifact, receipt])
    code = dump_s1(source)
    supplied[source["package_id"]] = code
    package["dependencies"] = [
        {"key": "code", "package_id": source["package_id"], "format": source["format"],
         "pin": pin(sha256(code).hexdigest(), len(code))},
        *package["dependencies"],
    ]
    procedure = record(package, "proc.graph")["payload"]
    procedure["definition"] = contract("s4.q06")
    procedure["implementation"] = {
        "ref_kind": "artifact", "artifact_record": external(
            "code", artifact["target"], "s1.artifact_snapshot", VERSION),
        "content_pin": pin(sha256(raw).hexdigest(), len(raw)),
    }
    selected_binding = local("bind.graph", "binding")
    selected_scope = local("scope.covered", "scope")
    package["records"].append({
        "id": "qualified.posterior", "kind": "s4.qualification", "contract": contract("s4.qualification"),
        "payload": {"procedure": local("proc.graph", "procedure"), "scope": selected_scope,
                    "receipt": {"ref_kind": "artifact", "artifact_record": external(
                        "code", receipt["target"], "s1.artifact_snapshot", VERSION),
                        "content_pin": pin(sha256(oracle).hexdigest(), len(oracle))},
                    "outcome": "pass"},
    })
    scope = record(package, "scope.covered")["payload"]
    scope.update(scope_kind="model", quantity=contract("s4.finite_model_posterior"))
    for field in ("universe", "mask", "numerator", "denominator"):
        scope.pop(field, None)
    model = keyed(h0=keyed(likelihood=rational(1, 5), prior=rational(1, 2)),
                  h1=keyed(likelihood=rational(4, 5), prior=rational(1, 2)))
    inputs = {"model": model, "observation": {"value_kind": "boolean", "value": True},
              "partition": category("established")}
    input_binding = local("bind.inputs", "binding")
    package["records"].extend([
        {"id": "def.inputs", "kind": "s4.question_definition", "contract": contract("s4.question_definition"),
         "payload": {"target": contract("s4.supplied_model_basis"), "slots": [], "output_roles": [
             {"key": key, "value_contract": contract("fixture." + key), "requirements": []}
             for key in sorted(inputs)]}},
        {"id": "q.inputs", "kind": "s4.question_instance", "contract": contract("s4.question_instance"),
         "payload": {"definition": local("def.inputs", "question_definition"), "target_slots": []}},
        {"id": "bind.inputs", "kind": "s4.binding", "contract": contract("s4.binding"),
         "payload": {"question": local("q.inputs", "question_instance"), "slots": [],
                     "selection": local("src", "source"), "frontier": package["frontier"]}},
    ])
    procedure["slots"] = []
    record(package, "bind.graph")["payload"]["slots"] = []
    for key, value in sorted(inputs.items()):
        ident = "input." + key
        package["records"].append({"id": ident, "kind": "s4.result", "contract": contract("s4.result"),
            "payload": {"binding": input_binding, "output_role": key, "subject_key": "event-d",
                        "scope": selected_scope, "origin": {"origin_kind": "reported",
                        "source": local("src", "source")}, "premises": [],
                        "outcome": {"tag": "defined", "value": value}}})
        procedure["slots"].append({"key": key, "role_class": "evidence",
            "contract": contract("s4.result"), "minimum": "1", "maximum": "1", "collection": "single"})
        record(package, "bind.graph")["payload"]["slots"].append(
            {"key": key, "values": [local(ident, "result")]})
    definition = record(package, "def.graph")["payload"]
    procedure["output_roles"] = [{"key": "posterior", "value_contract": contract("s4.finite_distribution"),
                                  "requirements": []}]
    definition["slots"], definition["output_roles"] = procedure["slots"], procedure["output_roles"]
    definition["target"] = contract("s4.finite_model_posterior")
    record(package, "intent.graph")["payload"]["goals"] = [{
        "key": "posterior", "question": local("q.graph", "question_instance"),
        "output_role": "posterior", "scope": selected_scope, "profiles": ["p4"],
        "binding": selected_binding,
    }]
    selection = record(package, "plan.graph")["payload"]
    selection["goal"]["goal_key"] = "posterior"
    selection["outputs"] = [{"key": "posterior", "binding": selected_binding,
                              "output_role": "posterior", "subject_key": "event-d",
                              "scope": selected_scope}]
    selection["premises"] = []
    package["records"].sort(key=lambda row: row["id"])
    descriptor = ProcedureDescriptor.from_declaration(
        procedure["definition"], sha256(raw).hexdigest(), procedure["slots"], procedure["output_roles"],
    )
    return package, supplied, descriptor, Evaluator(descriptor, raw, evaluate_posterior)


class MeasurementReleaseCases(unittest.TestCase):
    def test_actual_posterior_evaluator_to_committed_s4_output(self):
        package, supplied, descriptor, evaluator = actual_posterior()
        original = bound(package, supplied)
        registry = Registry([descriptor])
        with work_fixture() as (_, journal, account, context):
            service = Coordinator(journal, account, context, [evaluator])
            observed = service.execute(PLAN, "qualified-fixture", original)
            self.assertEqual(observed.state, "completed", observed.issues)
            self.assertEqual(service.record(observed).state, "committed")
            preserved = materialize_recorded(PLAN, original, registry, service, "qualified-fixture",
                                             observed.basis_digest, "snapshot.observed-posterior")
            self.assertEqual(len(preserved.results), 1)
            result = preserved.view.read(local(preserved.results[0], "result")).value["payload"]
            self.assertEqual(result["origin"]["calculation"], preserved.calculation)
            self.assertEqual([(row["key"], exact(row["value"]))
                              for row in result["outcome"]["value"]["entries"]],
                             [("h0", Fraction(1, 5)), ("h1", Fraction(4, 5))])
            calc = preserved.view.read(preserved.calculation).value["payload"]
            journal_event = preserved.view.read(calc["observations"][0]).value["payload"]
            self.assertEqual(journal_event["code"], "s4.work.result")
            self.assertEqual(json.loads(journal_event["details"])["basis_digest"], observed.basis_digest)
            snapshot = preserved.snapshot.package
            original_key = calc["procedure"]["dependency_key"]
            assessment = {
                "target": local(preserved.results[0], "result"), "audience": snapshot["audience"],
                "frontier": snapshot["frontier"], "premises": [],
                "qualifications": [external(original_key, "qualified.posterior", "s4.qualification", VERSION)],
                "basis": calc["observations"],
            }

            def conditional(reader, selected, audience, premises, qualifications, basis):
                measured = selected.value["payload"]
                work = basis[0].value["payload"]
                qualified = qualifications[0]
                q = qualified.value["payload"]
                procedure = reader.read(q["procedure"], qualified.package_id)
                scope = reader.read(q["scope"], qualified.package_id)
                oracle = json.loads(reader.read(q["receipt"], qualified.package_id).source_bytes)
                computation = reader.read(measured["origin"]["calculation"], selected.package_id)
                calc = computation.value["payload"]
                expected = {row["key"]: str(exact(row["value"]))
                            for row in measured["outcome"]["value"]["entries"]}
                return (oracle == {"conditional_on": "model-and-event-d", **expected}
                        and measured["subject_key"] == "event-d"
                        and scope == reader.read(measured["scope"], selected.package_id)
                        and procedure == reader.read(calc["procedure"], computation.package_id)
                        and work["code"] == "s4.work.result"
                        and json.loads(work["details"])["occurrence_id"] == observed.occurrence_id)

            access = supplied_read({preserved.snapshot.snapshot_id,
                                    *(row["package_id"] for row in snapshot["dependencies"]),
                                    *supplied})
            criterion = ProfileCriterion("fixture.finite_posterior", VERSION, "p4", conditional)
            assessed = assess(assessment, preserved.view, criterion, access)
            self.assertEqual(assessed.outcome, "established", assessed.issue)

    def test_assessment_does_not_promote_missing_qualification_or_restricted_evidence(self):
        package, supplied, _, _ = actual_posterior()
        original = bound(package, supplied)
        target = {"target": local("src", "source"), "audience": package["audience"],
                  "frontier": package["frontier"], "premises": [], "qualifications": [],
                  "basis": [local("src", "source")]}
        access = supplied_read({package["snapshot_id"], *supplied})
        seen = []

        def check(reader, selected, audience, premises, qualifications, basis):
            seen.append(selected.record_id)
            return basis == (selected,)

        preservation = ProfileCriterion("fixture.preservation", VERSION, "p0", check)
        qualified = ProfileCriterion("fixture.conditional", VERSION, "p4", check)
        held = assess(target, original, qualified, access)
        self.assertEqual(held.issue.code, "s4.assessment_basis_missing")
        self.assertEqual(seen, [])
        established = assess(target, original, preservation, access)
        self.assertEqual(established.outcome, "established", established.issue)
        self.assertEqual(established.payload["target"], target["target"])
        denied = assess(target, original, preservation, supplied_read({package["snapshot_id"]}))
        self.assertEqual(denied.issue.code, "s4.read_denied")
        self.assertIsNone(denied.payload)
        self.assertEqual(seen, ["src"])

    def test_normal_cli_inspects_and_plans_without_work(self):
        package, sources, descriptor, _ = actual_posterior()
        env = os.environ.copy()
        env.pop("CRUCIS_DATA_ROOT", None)
        env.pop("PYTHONPATH", None)
        cwd = Path(__file__).resolve().parents[1]

        def command(*args):
            result = subprocess.run([sys.executable, "-B", "-m", "crucis_causal.measurement", *map(str, args)],
                                    cwd=cwd, env=env, check=True, capture_output=True, text=True)
            return json.loads(result.stdout)

        observed = command("inspect", GOLDENS / "graph.json")
        self.assertEqual(observed["state"], "valid_wire")
        with work_fixture() as (root, _, _, _):
            path = root / "plan.json"
            path.write_bytes(dumps(package))
            metadata = root / "descriptor.json"
            metadata.write_text(json.dumps({
                "contract": contract(descriptor.name, descriptor.version),
                "implementation_sha256": descriptor.implementation_digest,
                "slots": json.loads(descriptor.slots_bytes),
                "output_roles": json.loads(descriptor.output_roles_bytes),
            }), encoding="utf-8")
            args = []
            for i, (identity, raw) in enumerate(sources.items()):
                source = root / f"dependency-{i}.json"
                source.write_bytes(raw)
                args += ["--dependency", f"{identity}={source}"]
            ready = command("plan", path, "plan.graph", "--descriptor", metadata, *args)
            self.assertEqual(ready["state"], "ready", ready)
            self.assertEqual(ready["ready"], ["posterior"])
            self.assertFalse(ready["work_performed"])
