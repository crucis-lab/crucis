
"""B02 uses exact S1, S2, S3 and S4 source packages."""

from copy import deepcopy
from hashlib import sha256
import unittest

from crucis_causal.execution.api import supplied_read
from crucis_causal.finding import dumps, inspect
from crucis_causal.finding.planning import RuleDescriptor, RuleRegistry, prepare
from crucis_causal.finding.resolution import resolve
from crucis_causal.measurement import dumps as dump_s4

from test_audit_finding_wire import contract, dep, example, external, local, payload, pin
from test_audit_measurement_planning import predecessor_bytes, scenario


REQUEST = local("assessment", "assessment")
CODE = b'{"example":true}'


def _by_id(package, record_id):
    return next(row for row in package["records"] if row["id"] == record_id)


def _ref(key, package, ident):
    record = _by_id(package, ident)
    expected = record["contract"]
    return external(key, ident, expected["name"], expected["version"])


def case(*, held=False, check=None):
    package = example("held")
    predecessors, _ = predecessor_bytes()
    measurement, _, _, _ = scenario()
    result = next(row for row in measurement["records"] if row["kind"] == "s4.result")
    experiment, raw_experiment, exp_ids = predecessors["experiment"]
    run, raw_run, run_ids = predecessors["execution"]
    source, raw_source, source_ids = predecessors["source"]
    sources = {
        "code": (source, raw_source), "study": (experiment, raw_experiment),
        "run": (run, raw_run), "measurement": (measurement, dump_s4(measurement)),
    }
    package["dependencies"] = [dep(key, view.get("package_id", view.get("snapshot_id")), view["format"], raw)
                               for key, (view, raw) in sorted(sources.items())]
    supplied = {entry["package_id"]: sources[entry["key"]][1] for entry in package["dependencies"]}
    aud = _ref("run", run, run_ids["audience"])
    scope = _ref("study", experiment, exp_ids["case"])
    observer = _ref("code", source, source_ids["observer"])
    selected = _ref("measurement", measurement, result["id"])
    package["audience"] = aud
    package["frontier"][0]["position"] = aud
    question = payload(package, "question")
    question.update(subject=observer, scope=scope)
    basis = payload(package, "basis")
    basis["selection"] = scope
    basis["entries"][0]["evidence"]["reference"] = aud
    if not held:
        basis["entries"][1]["evidence"] = {"state": "selected", "reference": selected}
        payload(package, "assessment")["sufficiency"] = {"state": "unevaluated", "reason": "preflight"}
        payload(package, "assessment")["decision"] = {"state": "unevaluated", "reason": "preflight"}
    rule = payload(package, "rule")
    rule["operands"][0]["key"] = "full-frame"
    rule["clauses"][0]["operand"] = "full-frame"
    rule["prerequisites"] = ["control"]
    rule["implementation"] = {"ref_kind": "artifact",
                              "artifact_record": _ref("code", source, source_ids["original"]),
                              "content_pin": pin(CODE)}

    def fixture_check(reader, candidate, selected_basis, values):
        chosen = {item.key: item.material for item in values}
        return (candidate.value["payload"]["scope"] == scope
                and selected_basis.value["payload"]["selection"] == scope
                and chosen["full-frame"].record_id == result["id"]
                and chosen["control"].record_id == run_ids["audience"])

    registry = RuleRegistry([RuleDescriptor.bind(rule, CODE, check or fixture_check)])
    return package, supplied, registry


def view(package, supplied, *, denied=()):
    snap = inspect(dumps(package))
    return resolve(snap, supplied, supplied_read({snap.snapshot_id, *set(supplied).difference(denied)}))


class FindingPlanningCases(unittest.TestCase):
    def test_prepares_only_exact_actual_predecessor_records(self):
        package, supplied, registry = case()
        v = view(package, supplied)
        ready = prepare(REQUEST, v, registry)
        self.assertEqual(ready.state, "ready", ready.issues)
        self.assertEqual(ready, prepare(REQUEST, v, registry))
        self.assertEqual(len(ready.basis_digest), 64)
        self.assertEqual([row.material.contract["name"] for row in ready.selection],
                         ["s3.audience", "s4.result"])
        a = v.read(payload(package, "question")["subject"])
        s = v.read(payload(package, "question")["scope"])
        self.assertTrue(a.contract["name"].startswith("s1."))
        self.assertEqual(s.contract["name"], "s2.case_revision")

    def test_missing_operand_and_exact_gap_remain_scoped(self):
        package, supplied, registry = case(held=True)
        v = view(package, supplied)
        h = prepare(REQUEST, v, registry)
        self.assertEqual(h.issues, ("required_operand_unresolved",))
        self.assertIsNotNone(h.basis_digest)
        gap = payload(package, "assessment")["decision"]["basis"]
        self.assertEqual(v.read(gap).value["evidence"]["reason"], "two_unresolved_pairs")

    def test_denied_or_changed_bytes_never_satisfy_pin(self):
        package, supplied, registry = case()
        identity = next(dep["package_id"] for dep in package["dependencies"] if dep["key"] == "measurement")
        denied = prepare(REQUEST, view(package, supplied, denied={identity}), registry)
        self.assertEqual(denied.selection[1].reason, "s5.read_denied")
        raw = supplied[identity]
        changed = dict(supplied, **{identity: raw[:-1] + (b"x" if raw[-1:] != b"x" else b"y")})
        other = prepare(REQUEST, view(package, changed), registry)
        self.assertEqual(other.selection[1].reason, "s5.integrity_mismatch")
        self.assertEqual((denied.state, other.state), ("held", "held"))
        self.assertNotEqual(denied.basis_digest, other.basis_digest)

    def test_rule_pin_and_target_are_exact(self):
        package, supplied, registry = case()
        changed = deepcopy(package)
        payload(changed, "rule")["clauses"][0]["operator"] = "gt"
        got = prepare(REQUEST, view(changed, supplied), registry)
        self.assertEqual(got.issues, ("s5.rule_identity_mismatch",))
        payload(package, "question")["quantity"] = contract("fixture.other")
        got = prepare(REQUEST, view(package, supplied), registry)
        self.assertEqual(got.issues, ("s5.rule_target_mismatch",))

    def test_preflight_dispositions_remain_separate(self):
        for axis, status in (("applicability", "inapplicable"), ("applicability", "disputed"),
                             ("execution", "unrun"), ("execution", "deviated")):
            with self.subTest(status=status):
                package, supplied, registry = case()
                assessment = payload(package, "assessment")
                assessment[axis]["state"] = status
                if axis == "applicability":
                    assessment[axis]["reason"] = "fixture_scope"
                got = prepare(REQUEST, view(package, supplied), registry)
                self.assertEqual((got.state, got.issues), ("held", (status,)))
