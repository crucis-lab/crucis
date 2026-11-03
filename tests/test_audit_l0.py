from crucis_causal.core.paths import ROOT as DATA_ROOT
"""Bundle B1 (DLV-09): L0 metrics route to the research repository's scorers and agree with every other copy of the
rule; MATMCD audited end to end (recorded) equals AB-06; the whole B1 rerun gate holds (<= 0.001)."""
import random
import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from crucis_causal.core.graph import Graph  # noqa: E402
from crucis_causal.metrics import l0  # noqa: E402
from crucis_causal._support import probe_io as PIO  # noqa: E402  (on sys.path through audit.core.paths)
from crucis_causal._support import causalarena_io as CA  # noqa: E402

HAVE_DATA = (DATA_ROOT / "runs" / "ab06").is_dir() and (DATA_ROOT / "external" / "causalarena").is_dir()


class TestRulesAgree(unittest.TestCase):
    def test_expectation_rule_equals_probe_and_causalarena_io(self):
        rng = random.Random(7)
        for k in range(200):
            n = rng.randint(3, 12)
            truth = {(a, b) for a in range(n) for b in range(n) if a < b and rng.random() < 0.25}
            D = {(a, b) for a in range(n) for b in range(n) if a != b and rng.random() < 0.1}
            U = {tuple(sorted((a, b))) for a in range(n) for b in range(a + 1, n) if rng.random() < 0.1} - {tuple(sorted(e)) for e in D}
            name = "file_%d.npz" % k
            tr = {"n": n, "T": truth, "seed_name": name, "targets": None}
            mine = l0.score_graph(Graph.from_edges(n, D, U), tr)
            ref = PIO.score_graph(D, U, truth, n, PIO.score_seed(name))["random"]
            self.assertAlmostEqual(mine["dir_f1@expect"], ref["f1"], places=6)
            ref2 = CA.directed_scores(D, {frozenset(u) for u in U}, truth, n, "random", seed=PIO.score_seed(name))
            self.assertAlmostEqual(mine["dir_f1@expect"], ref2["f1"], places=12)

    def test_tier_rules(self):
        class It:
            def ref(self, arm, tier):
                return ("npz:g", "x") if tier == "T4" else None
        with self.assertRaises(l0.TierRefused):
            l0.truth(It(), "swapped", "T4")


@unittest.skipUnless(HAVE_DATA, "AB-06 runs and CausalArena files are kept outside git")
class TestEndToEnd(unittest.TestCase):
    def test_matmcd_l0_equals_ab06(self):
        import json
        from crucis_causal.collect import collect, l0_table, score_all
        from crucis_causal.core import adapter as A, battery as B
        ref = json.loads((DATA_ROOT / "analysis" / "results" / "ab06" / "ab06.json").read_text())["agents"]["matmcd"]
        b = B.ca_ab06()
        recs = collect(A.get("matmcd"), b, ("real", "neutral", "swapped"))
        t = l0_table(recs, score_all(recs, b), ("real", "neutral", "swapped"))
        for arm in ("real", "neutral", "swapped"):
            self.assertEqual(t[arm]["ok"], ref[arm]["ok"])
            self.assertLessEqual(abs(t[arm]["dir_f1@expect"] - ref[arm]["f1_mean"]), 0.001)
            self.assertLessEqual(abs(t[arm]["dv1"]["precision"] - ref[arm]["dv1_precision"]), 0.001)
            self.assertLessEqual(abs(t[arm]["dv1"]["coverage"] - ref[arm]["dv1_coverage"]), 0.001)

    def test_b1_gate(self):
        from crucis_causal.rerun import existing as E
        t, _ = E.run(("B1",))
        s = t.summary("B1")
        self.assertTrue(s["pass"], [(r["audit"], r["system"], r["metric"], r["stored"], r["recomputed"]) for r in s["failed"]][:5])
        self.assertGreaterEqual(s["compared"], 180)


if __name__ == "__main__":
    unittest.main()
