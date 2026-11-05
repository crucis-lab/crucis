"""B10 historical interpretation remains read-only and scoped to declared roles."""

from decimal import Decimal
from hashlib import sha256
import unittest

from crucis_causal.measurement import LegacyAttribution, capture_legacy


def mapped(raw, route, selector=()):
    return capture_legacy(raw, LegacyAttribution(route, sha256(raw).hexdigest(),
                                                 "frozen fixture source", selector))


class MeasurementLegacyCases(unittest.TestCase):
    def test_graph_reference_and_arm_rules_keep_historical_meanings(self):
        payload = b'{"l0":{"adj_f1":0.80,"dir_f1@expect":0.4,"dir_f1@committed":0.2}}'
        graph = mapped(payload, "legacy.l0.graph.v1", ("l0",))
        self.assertEqual(graph.state, "interpreted")
        self.assertEqual(graph.reported_payload["adj_f1"].as_tuple(), Decimal("0.80").as_tuple())
        self.assertEqual(dict(graph.rule.semantics)["adjacency"], "historical_adjacency_f1")
        self.assertEqual(graph.raw, payload)
        arm = mapped(b'{"runs":4,"ok":2,"executed":3,"statuses":{"FAILED":1}}', "legacy.l0.arm.v1")
        self.assertEqual(dict(arm.rule.semantics)["delivered"], "historical_executed_failure_as_zero")
        reference = mapped(b'{"tier":"T4","path":"old","seed_name":"seed"}', "legacy.l0.reference.v1")
        self.assertEqual(reference.reported_payload["tier"], "T4")

    def test_pair_interval_and_missing_values_keep_original_scope(self):
        raw = b'{"point":null,"lo":null,"hi":null,"units":0,"clusters":0,"B":2000,"seed":20261014}'
        capture = mapped(raw, "legacy.paired.cluster.v1")
        self.assertEqual(capture.state, "interpreted")
        self.assertIsNone(capture.reported_payload["point"])
        self.assertEqual(dict(capture.rule.semantics)["frame"], "historical_common_keys")
        self.assertEqual(dict(capture.rule.semantics)["interval"], "historical_cluster_bootstrap")

    def test_opaque_changed_and_incomplete_artifacts_have_distinct_dispositions(self):
        raw = b'{"score":0.91}'
        self.assertEqual(capture_legacy(raw).state, "opaque")
        changed = capture_legacy(raw, LegacyAttribution("legacy.report.v1", "0" * 64, "old"))
        self.assertEqual((changed.state, changed.reason), ("held", "historical_bytes_changed"))
        self.assertEqual(mapped(raw, "legacy.report.v1").reason, "historical_payload_unestablished")
        duplicate = b'{"body":{},"sha256":"a","sha256":"b"}'
        self.assertEqual(mapped(duplicate, "legacy.certificate.v1").state, "held")
        self.assertIsNone(changed.reported_payload)

    def test_calibration_ranking_and_certificate_reported_identity(self):
        for raw, route in (
            (b'{"calibration":{"ece":0.1}}', "legacy.calibration.v1"),
            (b'{"ranking":{"ac_at_3":0.5}}', "legacy.ranking.v1"),
            (b'{"body":{"audit":"fixture"},"sha256":"unverified"}', "legacy.certificate.v1"),
        ):
            with self.subTest(route=route):
                capture = mapped(raw, route)
                self.assertEqual(capture.state, "interpreted")
                self.assertEqual(capture.reason, "reported_legacy_scope")
                self.assertEqual(capture.raw, raw)
