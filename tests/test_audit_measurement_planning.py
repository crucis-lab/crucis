"""B02 bindings and plans using actual predecessor-format fixture bytes."""

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import unittest

from crucis_causal.connections.codec import dumps as dump_s1
from crucis_causal.connections.evidence import capture_bytes
from crucis_causal.connections.model import Builder as SourceBuilder
from crucis_causal.execution.api import Limits as ExecutionLimits, supplied_read
from crucis_causal.execution.codec import dumps as dump_s3
from crucis_causal.execution.model import Builder, contract as s3_contract, index, unknown, unknown_ref
from crucis_causal.measurement import (
    Limits, ProcedureDescriptor, Registry, ResolutionError, dumps, inspect, plan, resolve,
)
from crucis_causal.execution.model import walk
from s4_wire_examples import EXAMPLES, local, pin
from test_audit_measurement_wire import record


def predecessor_bytes():
    source = SourceBuilder("S4 binding fixture")
    artifact = capture_bytes(source, b'{"example":true}')
    s1_package = source.package([artifact])
    raw_s1 = dump_s1(s1_package)

    execution = Builder("S4 audience fixture")
    audience = execution.add("audience", {
        "purpose": s3_contract("fixture_measurement"), "recipients": index(),
        "disclosure_policy": unknown_ref("s1.policy"), "authority": unknown(),
    })
    root = execution.add("projection_view", {
        "view_role": "audience_projection", "audience": audience,
        "projection_contract": s3_contract("fixture_projection"),
        "members": index(), "claims": index(), "limits": index(),
    })
    s3_package = execution.package(root)
    raw_s3 = dump_s3(s3_package, ExecutionLimits())

    file = Path(__file__).with_name("audit_fixtures") / "sc2" / "A-s2-receipts.json"
    raw_s2 = file.read_bytes()
    s2_package = json.loads(raw_s2)
    case = next(r for r in s2_package["records"] if r["record_type"] == "s2.case_revision")
    return {
        "execution": (s3_package, raw_s3, {"audience": audience["target"]}),
        "source": (s1_package, raw_s1, {
            "observer": source.producer["target"], "original": artifact["target"],
        }),
        "experiment": (s2_package, raw_s2, {"case": case["id"]}),
    }, case["contract"]


def scenario(*, local_hold=False, restricted_role=False):
    package = EXAMPLES["graph"]()
    sources, case_contract = predecessor_bytes()
    entries = []
    for key, (value, raw, _) in sorted(sources.items()):
        entries.append({"key": key, "format": value["format"], "package_id": value["package_id"],
                        "pin": pin(sha256(raw).hexdigest(), len(raw))})
    package["dependencies"] = entries
    for _, value, _ in walk(package):
        if isinstance(value, dict) and value.get("ref_kind") == "external":
            _, _, aliases = sources[value["dependency_key"]]
            value["target_id"] = aliases.get(value["target_id"], value["target_id"])
        if isinstance(value, dict) and value.get("ref_kind") == "artifact":
            native = b'{"example":true}'
            value["content_pin"] = pin(sha256(native).hexdigest(), len(native))
    _, _, aliases = sources["experiment"]
    case = {"ref_kind": "external", "dependency_key": "experiment",
            "target_id": aliases["case"], "expected_contract": case_contract}
    proc = record(package, "proc.graph")["payload"]
    primary = record(package, "plan.graph")["payload"]
    role_def = record(package, "def.graph")["payload"]
    if local_hold or restricted_role:
        requirement = record(package, "req.missing_label")["payload"]
        requirement["subject_slots"][0]["key"] = "scope"
        requirement["subject_slots"][0]["contract"]["name"] = "s4.scope"
        assessment = record(package, "prem.missing_label")["payload"]
        assessment["subjects"] = [{"key": "scope", "values": [local("scope.full", "scope")]}]
        primary["premises"].append({"key": "missing_label", "assessment": local(
            "prem.missing_label", "premise_assessment")})
        role_def["output_roles"][1]["requirements"] = [local("req.missing_label", "requirement")]
        primary["outputs"][1]["scope"] = local("scope.full", "scope")
        record(package, "intent.graph")["payload"]["goals"][1]["scope"] = local("scope.full", "scope")
        if restricted_role:
            assessment["determination"] = "supported"
            assessment["gaps"] = []
            assessment["support"] = [case]
    descriptor = ProcedureDescriptor.from_declaration(
        proc["definition"], proc["implementation"]["content_pin"]["digest"],
        proc["slots"], proc["output_roles"],
    )
    supplied = {value["package_id"]: raw for value, raw, _ in sources.values()}
    return package, supplied, Registry([descriptor]), case


def bound(package, supplied, *, deny=(), limits=Limits()):
    snapshot = inspect(dumps(package, limits), limits)
    cap = supplied_read({snapshot.snapshot_id, *(set(supplied) - set(deny))})
    return resolve(snapshot, supplied, cap, limits)


class MeasurementPlanningTests(unittest.TestCase):
    def test_real_predecessor_formats_and_immutable_scoped_reads(self):
        package, supplied, registry, case = scenario()
        view = bound(package, supplied)
        found = view.read(case)
        self.assertEqual(found.contract["name"], "s2.case_revision")
        found.value.clear()
        self.assertIn("payload", found.value)
        self.assertEqual(view.read(package["audience"]).contract["name"], "s3.audience")
        artifact = record(package, "proc.graph")["payload"]["implementation"]
        self.assertEqual(view.read(artifact).source_bytes, b'{"example":true}')
        self.assertEqual(plan(local("plan.graph", "plan"), view, registry).state, "ready")

    def test_ready_preparation_has_stable_basis_and_no_work_or_write(self):
        package, supplied, registry, _ = scenario()
        view = bound(package, supplied)
        before = view.snapshot.source_bytes
        first = plan(local("plan.graph", "plan"), view, registry)
        second = plan(local("plan.graph", "plan"), view, registry)
        self.assertEqual(first, second)
        self.assertEqual(first.state, "ready")
        self.assertEqual([o.output_role for o in first.outputs], ["covered", "judged_count"])
        self.assertIsNotNone(first.basis_digest)
        self.assertEqual(view.snapshot.source_bytes, before)
        shifted = deepcopy(package)
        shifted["snapshot_id"] = "snapshot.later"
        new_position = deepcopy(shifted["frontier"][0])
        new_position["key"] = "later-source-position"
        shifted["frontier"] = [new_position, *shifted["frontier"]]
        record(shifted, "bind.graph")["payload"]["frontier"] = shifted["frontier"]
        later = plan(local("plan.graph", "plan"), bound(shifted, supplied), registry)
        self.assertEqual(later.state, "ready")
        self.assertNotEqual(first.basis_digest, later.basis_digest)

    def test_local_premise_holds_its_output_only(self):
        package, supplied, registry, _ = scenario(local_hold=True)
        report = plan(local("plan.graph", "plan"), bound(package, supplied), registry)
        self.assertEqual(report.state, "partial")
        self.assertEqual([row.key for row in report.outputs], ["covered"])
        self.assertEqual((report.held[0].key, report.held[0].issue.code),
                         ("judged_count", "s4.premise_unresolved"))

    def test_restricted_source_is_local_or_global_by_declared_scope(self):
        package, supplied, registry, case = scenario(restricted_role=True)
        experiment = next(d["package_id"] for d in package["dependencies"] if d["key"] == "experiment")
        report = plan(local("plan.graph", "plan"), bound(package, supplied, deny=[experiment]), registry)
        self.assertEqual(report.state, "partial")
        self.assertEqual(report.held[0].issue.code, "s4.read_denied")
        record(package, "proc.graph")["payload"]["dependencies"] = [case]
        global_hold = plan(local("plan.graph", "plan"),
                           bound(package, supplied, deny=[experiment]), registry)
        self.assertEqual(global_hold.state, "held")
        self.assertEqual(global_hold.issues[0].code, "s4.read_denied")

    def test_changed_bytes_at_original_identity_are_rejected(self):
        package, supplied, registry, _ = scenario()
        source = next(d["package_id"] for d in package["dependencies"] if d["key"] == "source")
        supplied[source] = bytes([supplied[source][0] ^ 1]) + supplied[source][1:]
        report = plan(local("plan.graph", "plan"), bound(package, supplied), registry)
        self.assertEqual(report.state, "held")
        self.assertEqual(report.issues[0].code, "s4.integrity_mismatch")

    def test_unavailable_registry_or_wrong_scope_never_prepares_work(self):
        package, supplied, registry, _ = scenario()
        hold = plan(local("plan.graph", "plan"), bound(package, supplied), Registry())
        self.assertEqual(hold.issues[0].code, "s4.procedure_unavailable")
        record(package, "plan.graph")["payload"]["outputs"][0]["scope"] = local("scope.full", "scope")
        hold = plan(local("plan.graph", "plan"), bound(package, supplied), registry)
        self.assertEqual(hold.issues[0].code, "s4.primary_goal_output_missing")

    def test_declared_slot_needs_the_exact_predecessor_record_contract(self):
        package, supplied, _, case = scenario()
        spec = {"key": "case", "role_class": "evidence", "contract": case["expected_contract"],
                "minimum": "1", "maximum": "1", "collection": "single"}
        proc = record(package, "proc.graph")["payload"]
        proc["slots"] = [spec]
        record(package, "def.graph")["payload"]["slots"] = [spec]
        selected = {"key": "case", "values": [case]}
        record(package, "bind.graph")["payload"]["slots"] = [selected]
        registry = Registry([ProcedureDescriptor.from_declaration(
            proc["definition"], proc["implementation"]["content_pin"]["digest"],
            proc["slots"], proc["output_roles"],
        )])
        ready = plan(local("plan.graph", "plan"), bound(package, supplied), registry)
        self.assertEqual(ready.state, "ready")
        self.assertEqual(ready.outputs[0].slots[0].values[0].record_id, case["target_id"])
        selected["values"] = [package["audience"]]
        wrong = plan(local("plan.graph", "plan"), bound(package, supplied), registry)
        self.assertEqual(wrong.state, "held")
        self.assertTrue(all(output.issue.code == "s4.slot_contract" for output in wrong.held))

    def test_invalid_supplied_reference_and_bounds(self):
        package, supplied, registry, _ = scenario()
        root = dumps(package)
        limits = Limits(closure_bytes=len(root))
        view = bound(package, supplied, limits=limits)
        with self.assertRaisesRegex(ResolutionError, "invalid_reference"):
            view.read({"ref_kind": "external"})
        report = plan(local("plan.graph", "plan"), view, registry)
        self.assertEqual(report.issues[0].code, "s4.closure_byte_limit")
