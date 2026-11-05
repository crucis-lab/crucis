"""B01 wire-only contracts. Symbolic sources make no qualification claim."""

from dataclasses import fields, replace
from hashlib import sha256
import json
from pathlib import Path
import unittest

from crucis_causal.measurement import Limits, WireError, dumps, inspect
from s4_wire_examples import EXAMPLES, expected_bytes, local, rational


GOLDENS = Path(__file__).with_name("fixtures") / "s4-wire"


def record(package, ident):
    return next(r for r in package["records"] if r["id"] == ident)


class MeasurementWireTests(unittest.TestCase):
    def reject(self, data, code, limits=Limits()):
        with self.assertRaises(WireError) as ctx:
            inspect(data, limits)
        self.assertEqual(ctx.exception.code, "s4." + code)

    def test_worked_packages_round_trip_exact_golden_bytes(self):
        for name, example in EXAMPLES.items():
            with self.subTest(name=name):
                expected = (GOLDENS / (name + ".json")).read_bytes()
                observed = inspect(expected)
                self.assertEqual(observed.snapshot_id, "snapshot." + name)
                self.assertEqual(observed.digest, sha256(expected).hexdigest())
                self.assertEqual(observed.package, example())
                self.assertEqual(dumps(observed.package), expected)

    def test_decoded_package_mutation_cannot_change_the_frozen_bytes(self):
        raw = expected_bytes(EXAMPLES["graph"]())
        view = inspect(raw)
        view.package["records"].clear()
        self.assertEqual(view.source_bytes, raw)
        self.assertTrue(view.package["records"])

    def test_empty_undefined_and_held_are_separate_roles(self):
        view = inspect((GOLDENS / "local.json").read_bytes()).package
        self.assertEqual(record(view, "val.coverage.coverage")["payload"]["outcome"],
                         {"tag": "defined", "value": rational(0, 1)})
        undefined = record(view, "val.ratio.agreement")["payload"]
        self.assertEqual(undefined["outcome"]["tag"], "undefined")
        self.assertEqual(undefined["origin"]["calculation"]["target_id"], "calc.ratio")
        held = record(view, "held.missing.agreement")["payload"]
        self.assertEqual(held["outcome"]["tag"], "held")
        self.assertFalse(any(r["id"] == "calc.missing" for r in view["records"]))

    def test_canonical_utf8_and_no_bare_numbers_null_or_duplicate_properties(self):
        raw = expected_bytes(EXAMPLES["graph"]())
        self.reject(raw + b"\n", "noncanonical_bytes")
        self.reject(b'{"a":null}', "structural_null_or_number")
        self.reject(b'{"a":1}', "tagged_numeric_value_required")
        self.reject(b'{"a":NaN}', "tagged_numeric_value_required")
        self.reject(b'{"a":true,"a":false}', "duplicate_property")
        self.reject(b'{"a":"\\ud800"}', "invalid_unicode_scalar")
        self.reject(b'{"a":"\xff"}', "invalid_json_or_unicode")
        self.reject(raw.decode(), "immutable_bytes_required")

    def test_exact_version_and_closed_shapes(self):
        package = EXAMPLES["graph"]()
        package["format"]["version"] = "future"
        self.reject(expected_bytes(package), "shape")
        package = EXAMPLES["graph"]()
        package["snapshot_id"] += "\n"
        self.reject(expected_bytes(package), "shape")
        package = EXAMPLES["graph"]()
        record(package, "src")["payload"]["credential"] = "not-a-declared-field"
        self.reject(expected_bytes(package), "shape")

    def test_fraction_spelling_and_interval_order(self):
        for ratio, code in ((rational(2, 2), "noncanonical_rational"),
                            (rational("-0", 1), "shape"),
                            (rational(1, 0), "shape"),
                            (rational(1, "2\n"), "shape")):
            with self.subTest(ratio=ratio):
                package = EXAMPLES["graph"]()
                record(package, "val.graph.covered")["payload"]["outcome"]["value"] = ratio
                self.reject(expected_bytes(package), code)
        package = EXAMPLES["paired"]()
        value = record(package, "val.bound.outer_bound")["payload"]["outcome"]["value"]
        value["lower"], value["upper"] = value["upper"], value["lower"]
        self.reject(expected_bytes(package), "reversed_interval")

    def test_records_and_keyed_results_preserve_unique_canonical_keys(self):
        package = EXAMPLES["graph"]()
        package["records"].append(package["records"][-1])
        self.reject(expected_bytes(package), "duplicate_key")
        package = EXAMPLES["graph"]()
        package["records"].reverse()
        self.reject(expected_bytes(package), "noncanonical_key_order")
        package = EXAMPLES["posterior"]()
        vector = record(package, "val.posterior.posterior")["payload"]["outcome"]["value"]
        vector["entries"][1]["key"] = vector["entries"][0]["key"]
        self.reject(expected_bytes(package), "duplicate_key")

    def test_ref_contract_pin_selector_and_cycles(self):
        package = EXAMPLES["graph"]()
        package["roots"] = [local("acct", "source")]
        self.reject(expected_bytes(package), "reference_target")
        package = EXAMPLES["graph"]()
        package["roots"] = [local("missing", "account")]
        self.reject(expected_bytes(package), "reference_target")
        package = EXAMPLES["graph"]()
        package["audience"]["dependency_key"] = "missing"
        self.reject(expected_bytes(package), "undeclared_dependency")
        package = EXAMPLES["graph"]()
        package["dependencies"][0]["package_id"] = package["snapshot_id"]
        self.reject(expected_bytes(package), "duplicate_or_self_dependency")
        package = EXAMPLES["graph"]()
        record(package, "src")["payload"]["basis"] = [local("src", "source")]
        self.reject(expected_bytes(package), "proof_cycle")
        package = EXAMPLES["posterior"]()
        target = local("val.posterior.posterior", "result")
        target["selector"] = {"selector_kind": "member", "key": "h1"}
        record(package, "inference")["payload"]["result"] = target
        inspect(expected_bytes(package))
        target["selector"]["key"] = "h9"
        self.reject(expected_bytes(package), "selector_target")

    def test_double_emission_and_unplanned_emission_fail(self):
        package = EXAMPLES["graph"]()
        calc = record(package, "calc.graph")["payload"]
        calc["emissions"].append(calc["emissions"][-1])
        self.reject(expected_bytes(package), "duplicate_key")
        package = EXAMPLES["graph"]()
        record(package, "calc.graph")["payload"]["emissions"][0]["subject_key"] = "wrong"
        self.reject(expected_bytes(package), "unplanned_emission")

    def test_origin_association_and_artifact_range_must_match(self):
        package = EXAMPLES["graph"]()
        record(package, "val.graph.covered")["payload"]["origin"]["emission_key"] = "judged_count"
        self.reject(expected_bytes(package), "calculation_origin_mismatch")
        package = EXAMPLES["graph"]()
        implementation = record(package, "proc.graph")["payload"]["implementation"]
        implementation["selector"] = {"selector_kind": "byte_range",
                                      "start": "0", "end_exclusive": "13"}
        self.reject(expected_bytes(package), "artifact_selector_extent")

    def test_bounded_wire_accepts_exact_byte_limit_and_enforces_lower_limits(self):
        package = EXAMPLES["graph"]()
        raw = expected_bytes(package)
        inspect(raw, Limits(snapshot_bytes=len(raw)))
        self.assertEqual(dumps(package, Limits(snapshot_bytes=len(raw))), raw)
        with self.assertRaisesRegex(WireError, "manifest_limit"):
            dumps(package, Limits(snapshot_bytes=len(raw) - 1))
        for limits, code in (
            (Limits(snapshot_bytes=len(raw) - 1), "manifest_limit"),
            (Limits(depth=4), "depth_limit"),
            (Limits(records=1), "record_limit"),
            (Limits(collection_items=3), "collection_limit"),
            (Limits(scalar_bytes=8), "scalar_limit"),
            (Limits(reference_nodes=1), "reference_count_limit"),
            (Limits(reference_visits=1), "reference_visit_limit"),
            (Limits(external_snapshots=1), "dependency_limit"),
            (Limits(integer_digits=1), "integer_digit_limit"),
        ):
            with self.subTest(limits=limits):
                self.reject(raw, code, limits)
        caps = Limits()
        for field in fields(caps):
            with self.subTest(limit=field.name), self.assertRaises(WireError):
                replace(caps, **{field.name: getattr(caps, field.name) + 1})

    def test_known_empty_capture_keeps_source_report_without_numeric_result(self):
        package = EXAMPLES["local"]()
        source = record(package, "src")["payload"]
        source["extent"] = "known_empty"
        decoded = inspect(expected_bytes(package)).package
        self.assertEqual(record(decoded, "src")["payload"]["extent"], "known_empty")
        self.assertEqual(json.loads(expected_bytes(package)), decoded)
