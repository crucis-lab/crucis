from crucis_causal.core.paths import ROOT as DATA_ROOT
"""SC-1 structural encoding/reference obligations (DLV-08, DLV-09)."""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from crucis_causal.connections.codec import WireError, dumps, loads
from crucis_causal.connections.schema import PAYLOAD_FIELDS, schema
from crucis_causal.connections.validation import validate_wire


def specimen():
    return loads((ROOT / "crucis_causal/docs/system-connections-sc1-example-2026-11-01.json").read_bytes())


class SchemaConformance(unittest.TestCase):
    def test_approved_wire_example_and_meta_schema(self):
        from jsonschema import Draft202012Validator
        Draft202012Validator.check_schema(schema())
        self.assertEqual(len(PAYLOAD_FIELDS), 36)
        report = validate_wire(specimen())
        self.assertTrue(report.ok, report.to_json())
        self.assertEqual(report.to_json()["scientific_correctness"], "not_assessed")

    def test_duplicate_keys_rejected_before_overwrite(self):
        with self.assertRaises(WireError):
            loads(b'{"record_type":"s1.output","record_type":"s1.attempt"}')
        with self.assertRaises(WireError):
            loads(b'{"nested":{"x":1,"x":2}}')

    def test_unicode_and_native_bytes_boundary(self):
        with self.assertRaises(WireError): loads(b'"\\ud800"')
        with self.assertRaises(WireError): loads(b'"\xff"')
        text = 'e\u0301\r\n\u00e9'
        self.assertEqual(loads(dumps({"x":text}))["x"], text)

    def test_nonstandard_numeric_tokens_are_not_missing_values(self):
        for token in ("NaN", "Infinity", "-Infinity"):
            with self.assertRaises(WireError): loads(token)

    def test_duplicate_ids_and_wrong_target_types(self):
        package = specimen()
        package["records"].append(copy.deepcopy(package["records"][0]))
        self.assertFalse(validate_wire(package).reference_ok)
        package = specimen()
        package["roots"][0]["target_type"] = "s1.output"
        self.assertFalse(validate_wire(package).reference_ok)

    def test_unknown_is_not_null_or_fake_native_run(self):
        package = specimen()
        self.assertFalse(any(r["record_type"] == "s1.attempt" for r in package["records"]))
        package["records"][-1]["payload"]["request"] = None
        self.assertFalse(validate_wire(package).structural_ok)

    def test_closed_envelope_and_reserved_discriminant(self):
        package = specimen()
        package["records"][0]["native_extra"] = "not an extension"
        self.assertFalse(validate_wire(package).structural_ok)

    def test_calendar_precision_and_base64(self):
        package = specimen()
        package["records"][0]["created_at"]["value"]["value"] = "2026-02-30T00:00:00Z"
        self.assertFalse(validate_wire(package).ok)
        package = specimen()
        payload = package["records"][1]["payload"]
        payload["content"] = {"content_form":"inline_base64", "data":"//4="}
        self.assertTrue(validate_wire(package).ok)
        payload["content"]["data"] = "//4"
        self.assertFalse(validate_wire(package).ok)

    def test_reference_associations_can_cycle(self):
        package = specimen()  # component producer/clock references itself
        self.assertTrue(validate_wire(package).reference_ok)

    def test_unknown_critical_extension_preserves_but_cannot_satisfy_guarantee(self):
        package = specimen()
        package["extensions"][0]["critical_for"] = ["s1.graph_preservation"]
        report = validate_wire(package)
        self.assertTrue(report.ok, report.to_json())
        with self.assertRaises(WireError): report.require(["s1.graph_preservation"])
        self.assertTrue(report.withheld)


if __name__ == "__main__": unittest.main()
