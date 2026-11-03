from crucis.core.paths import ROOT as DATA_ROOT
"""Bundle B2 (DLV-09): L1 controls. Transform invariants; the effect helpers equal score/paired.py and the M3 bound;
MATMCD's name reliance and data-only floor and PC's layout effect equal AB-06 / AB-01; the B2 rerun gate holds."""
import json
import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from crucis.controls import effects as E, transforms as T  # noqa: E402
from crucis.core.graph import Graph  # noqa: E402

HAVE_DATA = (DATA_ROOT / "runs" / "ab06").is_dir() and (DATA_ROOT / "external" / "causalarena").is_dir()
HAVE_Q1 = (DATA_ROOT / "datasets" / "suite_q1s2" / "MAPPING.json").exists()


class TestTransforms(unittest.TestCase):
    def test_neutral_names_unique_and_carry_no_order(self):
        names = ["n%d" % i for i in range(23)]
        m = T.neutral_names(names, 5)
        self.assertEqual(len(set(m.values())), 23)
        self.assertNotEqual([m[n] for n in names], sorted(m.values()))
        self.assertEqual(m, T.neutral_names(names, 5))

    def test_derangement_has_no_fixed_point(self):
        for seed in range(20):
            names = ["n%d" % i for i in range(7)]
            m = T.derangement(names, seed)
            self.assertTrue(all(m[n] != n for n in names))
            self.assertEqual(sorted(m.values()), sorted(names))

    def test_column_order_and_reference_move_with_columns(self):
        d = 9
        perm = T.column_order("some_file.npz", d, "shuffled")
        self.assertEqual(sorted(perm), list(range(d)))
        self.assertEqual(T.column_order("some_file.npz", d, "released"), list(range(d)))
        Tt = {(0, 3), (3, 5), (2, 8)}
        shown = T.move_reference(Tt, perm)
        self.assertEqual(Graph.from_edges(d, shown).mapped(perm).directed, Tt)

    def test_path_labels(self):
        self.assertEqual(T.path_label("semantic_x__rep000.npz", "plain"), "semantic_x__rep000")
        self.assertNotIn("semantic", T.path_label("semantic_x__rep000.npz", "opaque"))

    def test_subsample_and_noise_are_seeded(self):
        X = np.arange(200.0).reshape(50, 4)
        S = T.subsample(X, 20, 3)
        self.assertEqual(S.shape, (20, 4))
        self.assertTrue(set(map(tuple, S)) <= set(map(tuple, X)))
        self.assertTrue(np.array_equal(S, T.subsample(X, 20, 3)))
        self.assertTrue(np.array_equal(T.add_noise(X, 0.1, 4), T.add_noise(X, 0.1, 4)))

    def test_knowledge_suppliers(self):
        Tt = {(0, 1), (1, 2), (0, 3), (3, 2)}
        o = T.oracle_order(Tt, 4)
        self.assertTrue(all(o.index(c) < o.index(e) for c, e in Tt))
        w = T.wrong_supplier(Tt, 0.5, 1)
        self.assertEqual(len(w), 4)
        self.assertEqual(sum((e, c) in w for c, e in Tt), 2)

    @unittest.skipUnless(HAVE_Q1, "suite_q1s2")
    def test_name_arms_leave_data_unchanged(self):
        from crucis.core import battery as B
        for item in B.q1s2().items:
            hs = {T.data_body_sha256(DATA_ROOT / p) for _, p in item.files}
            self.assertEqual(len(hs), 1, item.item_id)

    @unittest.skipUnless(HAVE_DATA, "AB-06 runs")
    def test_recorded_name_maps_are_what_agents_saw(self):
        from crucis.core import battery as B, harness as H
        for item in B.ca_ab06().items[:4]:
            for arm in ("neutral", "swapped"):
                m = T.recorded_names_map(item.cluster, arm)
                self.assertIsNotNone(m)
                p, _ = H.present(item, arm, names_map=m)
                self.assertEqual(len(set(p.names)), item.n)
                if arm == "swapped":
                    self.assertEqual(sorted(m.values()), sorted(m.keys()))


class TestEffects(unittest.TestCase):
    def test_paired_equals_score_paired(self):
        from crucis._support.score import paired as SP
        rng = np.random.default_rng(1)
        a = {"f%d" % i: float(rng.random()) for i in range(12)}
        b = {"f%d" % i: float(rng.random()) for i in range(12)}
        cl = lambda u: int(u[1:]) // 3  # noqa: E731
        mine = E.paired(a, b, cl)
        ref = SP.paired_diff(a, b, cl)
        for k in ("point", "lo", "hi"):
            self.assertAlmostEqual(mine[k], ref[k], places=12)

    def test_bounds(self):
        self.assertEqual(E.binom_q95(101), 59)            # BND-08 M3's stored bound
        q = E.binom_q05(101)
        self.assertLessEqual(E.binom_cdf(q, 101), 0.05)
        self.assertGreater(E.binom_cdf(q + 1, 101), 0.05)
        w = E.wilson(8, 30)
        self.assertTrue(w["lo"] < 8 / 30 < w["hi"])


@unittest.skipUnless(HAVE_DATA, "AB-06 runs and CausalArena files")
class TestEndToEnd(unittest.TestCase):
    def test_matmcd_l1_equals_ab06(self):
        from crucis.collect import collect, score_all
        from crucis.controls import l1
        from crucis.core import adapter as A, battery as B
        ref = json.loads((DATA_ROOT / "analysis" / "results" / "ab06" / "ab06.json").read_text())["agents"]["matmcd"]
        b = B.ca_ab06()
        ad = A.get("matmcd")
        recs = collect(ad, b, ("real", "neutral", "swapped"))
        sc = score_all(recs, b)
        ne = l1.name_effects(recs, sc, b)
        self.assertLessEqual(abs(ne["K04"]["point"] - ref["name_reliance_real_minus_swapped"]["mean"]), 0.001)
        self.assertTrue(ne["K04"]["lo"] <= ne["K04"]["point"] <= ne["K04"]["hi"])
        e = l1.data_only_effect(recs, sc, b, ad.capabilities.variants["data_only"])
        self.assertLessEqual(abs(e["dv1_precision_data_only"] - ref["data_only_floor_real_arm"]["dv1_precision_data_only"]), 0.001)
        self.assertLess(e["point"], 0)                    # P10: below its own data-only graph

    def test_b2_gate(self):
        from crucis.rerun import existing as E2
        t, _ = E2.run(("B2",))
        s = t.summary("B2")
        self.assertTrue(s["pass"], [(r["audit"], r["system"], r["metric"], r["stored"], r["recomputed"]) for r in s["failed"]][:5])


if __name__ == "__main__":
    unittest.main()
