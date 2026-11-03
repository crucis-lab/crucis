from crucis.core.paths import ROOT as DATA_ROOT
"""Bundle B1 of the audit package (DLV-09): graph type, canonical hashing, batteries, regimes, the adapter interface and
its conformance suite. NumPy only; tests that need data kept outside git (external/, runs/) skip when it is absent.

  python tests/run_tests.py --out <file outside the repo> --pattern test_audit_*.py
"""
import random
import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from crucis.core.graph import Graph  # noqa: E402
from crucis.core import canon, adapter as A, battery as B, harness as H  # noqa: E402
from crucis.core.runs import RunRecord  # noqa: E402
from crucis.protocol import regimes as R, kinds as K  # noqa: E402

HAVE_CA = (DATA_ROOT / "external" / "causalarena" / "scm" / "semantic" / "data").is_dir()
HAVE_AB06 = (DATA_ROOT / "runs" / "ab06").is_dir()
HAVE_Q1 = (DATA_ROOT / "datasets" / "suite_q1s2" / "MAPPING.json").exists()


def random_dag(n, p, rng):
    order = list(range(n))
    rng.shuffle(order)
    return {(order[i], order[j]) for i in range(n) for j in range(i + 1, n) if rng.random() < p}


def random_cc_matrix(n, rng):
    M = np.zeros((n, n), dtype=int)
    for a in range(n):
        for b in range(a + 1, n):
            r = rng.random()
            if r < 0.15:
                M[b, a] = 1                    # a -> b
            elif r < 0.25:
                M[a, b] = 1                    # b -> a
            elif r < 0.30:
                M[a, b] = M[b, a] = 2
            elif r < 0.33:
                M[a, b] = M[b, a] = 3
            elif r < 0.36:
                M[a, b] = 4                    # b o-> a
            elif r < 0.38:
                M[a, b] = M[b, a] = 6
            elif r < 0.40:
                M[a, b] = M[b, a] = 1          # conflict
    return M


class TestGraph(unittest.TestCase):
    def test_cc_matrix_round_trip_exact(self):
        rng = random.Random(1)
        for _ in range(50):
            M = random_cc_matrix(9, rng)
            g = Graph.from_cc_matrix(M)
            self.assertTrue(np.array_equal(g.to_cc_matrix(), M))

    def test_cc_convention(self):
        M = np.zeros((3, 3), dtype=int)
        M[1, 0] = 1                            # M[i, j] = 1 means j -> i: 0 -> 1
        M[1, 2] = M[2, 1] = 2
        g = Graph.from_cc_matrix(M)
        self.assertEqual(g.directed, {(0, 1)})
        self.assertEqual(g.undecided(), {(1, 2)})

    def test_conflict_counts_both_arrows(self):
        M = np.zeros((2, 2), dtype=int)
        M[0, 1] = M[1, 0] = 1
        g = Graph.from_cc_matrix(M)
        self.assertEqual(g.directed, {(0, 1), (1, 0)})
        self.assertEqual(g.committed(), set())

    def test_probe_result_and_edges_agree(self):
        res = {"directed": [{"from_idx": 2, "to_idx": 0, "source": "llm"}], "undecided": [{"a_idx": 3, "b_idx": 1}]}
        self.assertEqual(Graph.from_probe(4, res), Graph.from_edges(4, [(2, 0)], [(1, 3)]))
        self.assertEqual(Graph.from_probe(4, {"directed": [[2, 0]], "undecided": [[3, 1]]}), Graph.from_edges(4, [(2, 0)], [(1, 3)]))

    def test_mapped_is_a_relabelling(self):
        rng = random.Random(2)
        for _ in range(30):
            n = 8
            M = random_cc_matrix(n, rng)
            g = Graph.from_cc_matrix(M)
            perm = list(range(n))
            rng.shuffle(perm)
            h = g.mapped(perm)
            Mp = np.zeros_like(M)                 # relabel the matrix directly: shown k -> original perm[k]
            for i in range(n):
                for j in range(n):
                    Mp[perm[i], perm[j]] = M[i, j]
            self.assertEqual(h, Graph.from_cc_matrix(Mp))

    def test_canonical_round_trip_and_hash(self):
        rng = random.Random(3)
        g = Graph.from_cc_matrix(random_cc_matrix(7, rng))
        self.assertEqual(Graph.from_canonical(g.canonical()), g)
        self.assertEqual(canon.sha256_obj(g.canonical()), canon.sha256_obj(Graph.from_canonical(g.canonical()).canonical()))

    def test_marks(self):
        g = Graph.from_edges(4, [(0, 1)], [(2, 3)], [(1, 2)])
        self.assertEqual(g.marks(), {"->", "--", "<->"})


class TestCanon(unittest.TestCase):
    def test_order_independent(self):
        self.assertEqual(canon.sha256_obj({"b": [1, 2], "a": {3, 1}}), canon.sha256_obj({"a": {1, 3}, "b": [1, 2]}))
        self.assertNotEqual(canon.sha256_obj({"a": 1}), canon.sha256_obj({"a": 1.0000001}))


class TestRegimes(unittest.TestCase):
    def test_regimes(self):
        self.assertEqual(R.regime({"data", "names", "context"}, R.name_arm_offer("real")), "D+K")
        self.assertEqual(R.regime({"data", "names", "context"}, R.name_arm_offer("neutral")), "D")
        self.assertEqual(R.regime({"names", "context"}, R.name_arm_offer("neutral")), "none")
        self.assertEqual(R.regime({"names", "context"}, R.name_arm_offer("swapped")), "K")
        self.assertEqual(R.regime({"data", "interventions"}, {"data", "interventions"}), "D+I")

    def test_cross_regime_ranking_refused(self):
        with self.assertRaises(R.CrossRegime):
            R.check_comparable([{"regime": "D", "k_source": "none"}, {"regime": "D+K", "k_source": "names_real"}])


class TestProtocolData(unittest.TestCase):
    def test_closed_list(self):
        th = K.thresholds()
        ids = [k["id"] for k in K.KINDS]
        self.assertEqual(ids, ["K%02d" % i for i in range(1, 16)])
        self.assertEqual(len({k["kind"] for k in K.KINDS}), 15)
        for i in ids:
            self.assertIn(i, th, "every kind has a threshold")
        self.assertEqual(K.label("K04", "2026-10-14"), "confirmatory")
        self.assertTrue(K.label("K10", "2026-10-11").startswith("exploratory"))


class TestCapabilities(unittest.TestCase):
    def test_undeclared_values_refused(self):
        with self.assertRaises(ValueError):
            A.Capabilities(takes=frozenset({"data", "telepathy"}), marks=frozenset({"->"}))

    def test_live_llm_refused_without_go(self):
        ad = A.get("matmcd")
        with self.assertRaises(A.SpendRefused):
            ad.run(None, None, None, mode="live")


class TestStatuses(unittest.TestCase):
    def test_status_typed(self):
        with self.assertRaises(ValueError):
            RunRecord("x", "i", "a", "crashed")
        with self.assertRaises(ValueError):
            RunRecord("x", "i", "a", "ok")


# -------------------------------------------------------------------------------------------- conformance (frozen v1)
class Oracle(A.Adapter):
    """A planted perfect system: returns the true graph in SHOWN positions (it is handed the truth for the test only)."""
    name, version = "oracle_test", "0"
    capabilities = A.Capabilities(takes=frozenset({"data"}), marks=frozenset({"->"}))

    def __init__(self, truth, reverse=False):
        self.truth, self.reverse = truth, reverse

    def run(self, presented, budget, out_dir, mode="live", allow_spend=False):
        inv = H.inverse(self._perm)
        D = [(inv[c], inv[e]) for c, e in self.truth]
        if self.reverse:
            D = [(b, a) for a, b in D]
        return RunRecord(self.name, presented.file_label, "live", "ok", graph=Graph.from_edges(len(inv), D))


@unittest.skipUnless(HAVE_CA, "CausalArena files are kept outside git")
class TestConformance(unittest.TestCase):
    def test_planted_oracle_and_reversed(self):
        from crucis.metrics import l0
        b = B.ca_ab06()
        for item in b.items[:3]:
            tr = l0.truth(item, "real")
            for rev, want in ((False, 1.0), (True, 0.0)):
                o = Oracle(tr["T"], rev)
                p, perm = H.present(item)
                o._perm = perm
                rec = H.map_back(o.run(p, None, None), perm)
                rec.item, rec.arm = item.item_id, "real"
                self.assertAlmostEqual(l0.score_record(rec, item)["metrics"]["dir_f1@expect"], want)

    def test_shown_view_hides_the_order(self):
        b = B.ca_ab06()
        item = b.items[0]
        p, perm = H.present(item)
        self.assertNotEqual(perm, sorted(perm))
        self.assertEqual(sorted(perm), list(range(item.n)))

    @unittest.skipUnless(HAVE_AB06, "AB-06 run folders are kept outside git")
    def test_recorded_adapters_conform(self):
        """Every recorded adapter: marks within its declared marks; declared variants present in ok runs; identity stable;
        the agents saw exactly the harness's shuffle."""
        cases = [(n, "ca-ab06", ("real", "neutral", "swapped"), {}) for n in ("matmcd", "vashishtha", "pywhyllm", "causaliq")]
        cases += [(n, "ca-semantic", ("released", "shuffled"), {}) for n in ("pc", "ges", "gies")]
        if HAVE_Q1:
            cases += [("causal_copilot", "q1s2", ("real", "neutral", "swapped"), {"source": s}) for s in ("bnd08", "main", "bld06")]
        for name, bid, arms, kw in cases:
            ad = A.get(name, **kw)
            self.assertEqual(ad.identity(), ad.identity())
            b = B.get(bid)
            n_ok = 0
            for item in b.items[:12]:
                for arm in arms:
                    rec = ad.recorded(item, arm)
                    if rec.status != "ok":
                        continue
                    n_ok += 1
                    self.assertLessEqual(rec.graph.marks(), set(ad.capabilities.marks), (name, item.item_id))
                    for role, vname in ad.capabilities.variants.items():
                        if name == "causaliq":      # library_greedy_dag is reported only when the PDG had edges
                            continue
                        self.assertIn(vname, rec.variants, (name, role))
                    if rec.notes.get("shown_order") is not None:
                        self.assertEqual(rec.notes["shown_order"], H.perm_for(item.item_id, item.n))
            self.assertGreater(n_ok, 0, name)


@unittest.skipUnless(HAVE_CA, "CausalArena files are kept outside git")
class TestBattery(unittest.TestCase):
    def test_hash_stable_and_sensitive(self):
        b = B.ca_ab06()
        h = b.hash()
        self.assertEqual(h, B.Battery(b.battery_id, b.version, b.visibility, list(b.items), about=b.about).hash())
        m = b.manifest(False)
        m["items"][0]["n"] += 1
        self.assertNotEqual(canon.sha256_obj(m), canon.sha256_obj(b.manifest(False)))
        self.assertEqual(len(b.items), 10)
        self.assertEqual(len(b.clusters()), 10)


if __name__ == "__main__":
    unittest.main()
