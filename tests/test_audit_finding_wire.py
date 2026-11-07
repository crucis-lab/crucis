
"""B01 strict wire and exact worked S5 specimens (DLV-08/09)."""

from copy import deepcopy
from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path
import unittest

from crucis_causal.execution.model import canonical
from crucis_causal.finding import FORMAT, VERSION, Limits, WireError, dumps, inspect


GOLDENS = Path(__file__).with_name("fixtures") / "s5-wire"
CASES = ("held", "inconclusive", "corrected", "restricted")


def contract(name, version=VERSION):
    return {"name": name, "version": version}


def local(ident, kind, member=None):
    ref = {"ref_kind": "local", "target_id": ident, "expected_contract": contract("s5." + kind)}
    if member is not None:
        ref["selector"] = {"selector_kind": "member", "key": member}
    return ref


def external(dependency, ident, name, version=VERSION):
    return {"ref_kind": "external", "dependency_key": dependency, "target_id": ident,
            "expected_contract": contract(name, version)}


def pin(data):
    return {"algorithm": "sha256", "digest": sha256(data).hexdigest(),
            "length": str(len(data)), "extent": {"extent_kind": "whole"}}


def dep(key, package_id, fmt, data):
    return {"key": key, "package_id": package_id, "format": fmt, "pin": pin(data)}


def record(ident, kind, **payload):
    name = "s5." + kind
    return {"id": ident, "kind": name, "contract": contract(name), "payload": payload}


def rational(n, d):
    return {"number_kind": "rational", "numerator": str(n), "denominator": str(d)}


def sort_refs(*refs):
    return sorted(refs, key=canonical)


def example(case):
    author = {"mode": "attributed", "issuer": "S5 design fixture"}
    s3 = "0.1.0-proposal.3"
    # External bodies here are pin subjects for B01 only. B02 checks predecessor codecs.
    deps = [
        dep("run", "fixture-run", contract("s3.account_package", s3), b"fixture execution"),
    ]
    audience = external("run", "audience", "s3.audience", s3)
    cutoff = external("run", "cutoff", "s3.diagnostic", s3)
    rows, profiles, history = [], [], []
    if case == "restricted":
        statement = local("statement", "capture")
        result = local("public-view", "handoff")
        rows.extend([
            record("statement", "capture", origin=author, extent="complete",
                   availability={"state": "selected", "reference": cutoff},
                   reported=[{"key": "finding", "text": "The stated threshold was met."}]),
            record("public-view", "handoff", authority=cutoff, statements=[{
                "key": "finding", "scope": contract("fixture.public_aggregate"), "origin": author,
                "assertion": "The audit team reports a threshold meet.",
                "assurance": {"mode": "attributed", "source": statement,
                              "verification": "statement_integrity"},
                "limitations": ["restricted_derivation"],
            }]),
            record("profile", "profile_claim", profile="handoff", target=result,
                   criterion=contract("fixture.statement_integrity"),
                   outcome={"state": "established", "evidence": [statement]}),
        ])
    else:
        utility = case == "inconclusive"
        held = case == "held"
        quantity = contract("fixture.delivery_utility" if utility else "fixture.directed_f1")
        deps.extend([
            dep("code", "fixture-code", contract("s1.evidence_package"), b"fixture source"),
            dep("measurement", "fixture-measurement", contract("s4.measurement_package"), b"fixture result"),
            dep("study", "fixture-study", contract("s2.experiment_package"), b"fixture study"),
        ])
        code = {"ref_kind": "artifact",
                "artifact_record": external("code", "artifact", "s1.artifact_snapshot"),
                "content_pin": pin(b"bounded rule")}
        selected = external("measurement", "contrast", "s4.result")
        subject = external("code", "system", "s1.system")
        scope = external("study", "frame", "s2.population")
        binding = {"question": local("question", "question"), "rule": local("rule", "rule"),
                   "basis": local("basis", "basis")}
        gap = local("basis", "basis", "full-frame")
        observed = {"state": "established", "basis": binding["basis"]}
        entries = [{"key": "control", "role": "control",
                    "evidence": {"state": "selected", "reference": cutoff}}]
        entries.append({"key": "full-frame", "role": "contrast", "evidence":
                        {"state": "unavailable", "reason": "two_unresolved_pairs"}
                        if held else {"state": "selected", "reference": selected}})
        result = local("assessment", "assessment")
        decision = ({"state": "held", "reason": "full_frame_unresolved", "basis": gap}
                    if held else {"state": "completed", "decision": local("decision", "decision")})
        rows.extend([
            record("question", "question", finding_kind=contract("fixture.name_control"),
                   subject=subject, scope=scope, quantity=quantity),
            record("rule", "rule", definition=contract("fixture.r1"), target=quantity,
                   evidence_policy=contract("fixture.qualified"), implementation=code,
                   partial="require_all", operands=[{
                       "key": "contrast", "quantity": quantity, "unit": contract("fixture.unitless"),
                       "evidence_contract": contract("s4.result"), "form": "outer_bound" if utility else "point",
                   }], clauses=[{"key": "limit", "kind": "compare", "operand": "contrast",
                                 "operator": "ge", "threshold": rational(1, 10)}],
                   decision_policy={"kind": "predicate", "root": "limit"}),
            record("basis", "basis", question=binding["question"], rule=binding["rule"],
                   selection=scope, entries=entries),
            record("assessment", "assessment", **binding, origin=author,
                   applicability={"state": "applicable", "basis": binding["basis"]},
                   execution=observed,
                   sufficiency={"state": "held", "reason": "two_unresolved_pairs", "basis": gap}
                   if held else {"state": "sufficient", "basis": binding["basis"]},
                   decision=decision, registration={"state": "unrequested"}),
            record("profile", "profile_claim", profile="scoped_assessment" if held else "rule_decision",
                   target=result if held else local("decision", "decision"), criterion=contract("fixture.review"),
                   outcome={"state": "established", "evidence": [binding["basis"]]}),
        ])
        if not held:
            rows.append(record("decision", "decision", **binding, work=cutoff,
                               outcome={"state": "inconclusive", "branch": "enclosure_straddles_cutoff"}
                               if utility else {"state": "missed"}, trace=[{
                                   "key": "limit", "state": "inconclusive" if utility else "false",
                                   "evidence": [selected],
                               }]))
        if case == "corrected":
            deps.append(dep("prior", "fixture-prior", contract(FORMAT), b"fixture prior assessment"))
            prior = external("prior", "assessment.a2", "s5.assessment")
            rows.append(record("history", "history", subject=result, related=[prior],
                               relationship="correction", dimensions=["basis", "decision"],
                               adjudication=[cutoff]))
            history.append(local("history", "history"))
    profiles.append(local("profile", "profile_claim"))
    rows.append(record("account", "account", origin=author, items=[result],
                       profiles=profiles, **({"history": history} if history else {})))
    return {"format": contract(FORMAT), "account_id": "review", "snapshot_id": "snapshot." + case,
            "audience": audience, "frontier": [{"key": "cutoff", "position": cutoff}],
            "roots": [local("account", "account")], "records": sorted(rows, key=lambda x: x["id"]),
            "dependencies": sorted(deps, key=lambda x: x["key"])}


def payload(package, ident):
    return next(row["payload"] for row in package["records"] if row["id"] == ident)


class FindingWireCases(unittest.TestCase):
    def test_four_canonical_packages(self):
        for case in CASES:
            with self.subTest(case=case):
                raw = (GOLDENS / (case + ".json")).read_bytes()
                view = inspect(raw)
                self.assertEqual(raw, dumps(example(case)))
                self.assertEqual(raw, dumps(view.package))
                self.assertEqual(view.digest, sha256(raw).hexdigest())
                view.package["snapshot_id"] = "changed"
                self.assertEqual(view.package["snapshot_id"], "snapshot." + case)

    def test_hold_and_completed_inconclusive_are_different_shapes(self):
        held = example("held")
        self.assertEqual(payload(held, "assessment")["decision"]["state"], "held")
        self.assertNotIn("decision", {row["id"] for row in held["records"]})
        complete = example("inconclusive")
        self.assertEqual(payload(complete, "decision")["outcome"]["state"], "inconclusive")
        payload(complete, "decision")["outcome"].pop("branch")
        with self.assertRaisesRegex(WireError, "shape"):
            dumps(complete)

    def test_strict_input_and_version(self):
        raw = dumps(example("held"))
        for bad in (raw + b"\n", b'{"a":true,"a":false}', b'{"n":1}',
                    b'{"n":null}', b'{"x":"\\ud800"}', b'\xff', b'{"n":NaN}'):
            with self.subTest(bad=bad), self.assertRaises(WireError):
                inspect(bad)
        package = example("held")
        package["format"]["version"] = "2"
        with self.assertRaisesRegex(WireError, "shape"):
            dumps(package)

    def test_exact_values_and_caps(self):
        package = example("held")
        raw = dumps(package)
        limits = Limits()
        exact = replace(limits, wire=replace(limits.wire, snapshot_bytes=len(raw)))
        self.assertEqual(inspect(raw, exact).source_bytes, raw)
        for option, value in (("snapshot_bytes", len(raw) - 1), ("depth", 3), ("records", 2),
                              ("external_snapshots", 1), ("reference_nodes", 1),
                              ("reference_visits", 1), ("scalar_bytes", 4), ("collection_items", 2)):
            with self.subTest(option=option), self.assertRaises(WireError):
                inspect(raw, replace(limits, wire=replace(limits.wire, **{option: value})))
        threshold = payload(package, "rule")["clauses"][0]["threshold"]
        for patch in ({"numerator": "-0"}, {"denominator": "01"}, {"numerator": "2", "denominator": "20"},
                      {"numerator": "1" * 257}):
            bad = deepcopy(package)
            payload(bad, "rule")["clauses"][0]["threshold"] = {**threshold, **patch}
            with self.subTest(patch=patch), self.assertRaises(WireError):
                dumps(bad)

    def test_proof_links_selectors_and_predicate_cycles(self):
        package = example("held")
        payload(package, "assessment")["decision"]["basis"]["selector"]["key"] = "absent"
        with self.assertRaisesRegex(WireError, "selector_target"):
            dumps(package)
        package = example("held")
        payload(package, "basis")["entries"][0]["evidence"]["reference"] = local("assessment", "assessment")
        with self.assertRaisesRegex(WireError, "proof_cycle"):
            dumps(package)
        package = example("held")
        rule = payload(package, "rule")
        rule["clauses"].append({"key": "loop", "kind": "and", "children": ["limit", "loop"]})
        rule["decision_policy"]["root"] = "loop"
        with self.assertRaisesRegex(WireError, "predicate_cycle"):
            dumps(package)
        with self.assertRaisesRegex(WireError, "predicate_node_limit"):
            dumps(package, Limits(predicate_nodes=1))
        with self.assertRaisesRegex(WireError, "predicate_depth_limit"):
            dumps(package, Limits(predicate_depth=1))

    def test_history_adjudication_and_restricted_public_structure(self):
        package = example("corrected")
        del payload(package, "history")["adjudication"]
        with self.assertRaisesRegex(WireError, "history_adjudication_required"):
            dumps(package)
        public = inspect(dumps(example("restricted"))).package
        self.assertEqual([item["key"] for item in public["dependencies"]], ["run"])
        self.assertEqual(payload(public, "public-view")["statements"][0]["assurance"]["mode"], "attributed")
