from crucis.core.paths import ROOT as DATA_ROOT
"""Bundle B3 (DLV-09): L2. The recorder is observation-only (hooked output == unhooked output; hooks removed after an
exception) and localises a crash to its stage; lineage classifies every change; the restricted unpickler runs no pickled
code; Causal-Copilot's stages rebuilt from artifacts equal partial_stages.py, and the B3 gate holds."""
import os
import pickle
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from crucis.core.graph import Graph  # noqa: E402
from crucis.trace import cc_stages, stages as S  # noqa: E402
from crucis.trace.recorder import Recorder  # noqa: E402
from audit_fixtures import toy_pipeline as TP  # noqa: E402

HAVE_RUNS = ((DATA_ROOT / "runs" / "20261011T184856Z_s2_q011_r01_b3a03d" / "artifacts").is_dir()
             and (DATA_ROOT / "analysis" / "results" / "stability_s2" / "partial_stages.json").exists())


def g_of(edges, n=4):
    return Graph.from_edges(n, [], sorted(edges))


class TestRecorder(unittest.TestCase):
    def setUp(self):
        rng = np.random.default_rng(0)
        z = rng.standard_normal((300, 1))
        self.X = np.hstack([z, z + 0.5 * rng.standard_normal((300, 1)), rng.standard_normal((300, 1)), -z])

    def hooks(self, rec):
        m = "audit_fixtures.toy_pipeline"
        rec.hook(m + ":discover", stage="data", graph_from=lambda ret, a, k: g_of(ret))
        rec.hook(m + ":prune", stage="prune", graph_from=lambda ret, a, k: g_of(ret))
        rec.hook(m + ":break_cycles", stage="cycle_in", graph_from=lambda ret, a, k: g_of(a[0]), when="call")

    def test_observation_only(self):
        plain = TP.pipeline(self.X)
        with Recorder(system_root=str(ROOT / "tests" / "audit_fixtures")) as rec:
            self.hooks(rec)
            hooked = TP.pipeline(self.X)
        self.assertEqual(plain, hooked)
        self.assertEqual([s for s, _ in rec.stages], ["data", "prune", "cycle_in"])
        self.assertFalse(hasattr(TP.discover, "__wrapped__"))                    # hooks removed on exit

    def test_crash_localised_and_hooks_removed(self):
        orig = TP.break_cycles
        rec = Recorder(system_root=str(ROOT / "tests" / "audit_fixtures"))
        with self.assertRaises(KeyError):
            with rec:
                self.hooks(rec)
                TP.pipeline(self.X, fail=True)
        self.assertIs(TP.break_cycles, orig)
        self.assertEqual(rec.errors[0]["stage"], "cycle_in")
        self.assertIn("toy_pipeline.py", rec.errors[0]["innermost_system_frame"])
        self.assertEqual([s for s, _ in rec.stages], ["data", "prune", "cycle_in"])   # the input to the failing step is kept

    def test_toy_trace_finds_the_deleted_link(self):
        with Recorder() as rec:
            self.hooks(rec)
            TP.pipeline(self.X)
        lin, counts = S.lineage(rec.stages)
        self.assertEqual(counts["prune"], {"deleted": 1})
        self.assertEqual(sum(v["set_by"] == "prune" for v in lin.values()), 1)


class TestLineage(unittest.TestCase):
    def test_change_kinds(self):
        a = Graph.from_edges(4, [(0, 1), (1, 2)], [(2, 3)])
        b = Graph.from_edges(4, [(1, 0), (2, 3)], [(0, 3)])
        lin, counts = S.lineage([("in", a), ("out", b)])
        self.assertEqual(counts["out"], {"flipped": 1, "deleted": 1, "oriented": 1, "added": 1})

    def test_set_by_stage_and_names(self):
        s0 = Graph.from_edges(3, [], [(0, 1)])
        s1 = Graph.from_edges(3, [(0, 1)], [])
        s2 = Graph.from_edges(3, [(0, 1), (1, 2)], [])
        self.assertEqual(sorted(S.set_by_stage([("a", s0), ("b", s1), ("c", s2)], 1)), [(0, 1)])
        cls = S.follows_names([(0, 1), (1, 2)], T_data={(1, 0)}, T_label={(2, 1)})
        self.assertEqual(cls, {(0, 1): "data only", (1, 2): "labels only"})

    def test_direction_flips(self):
        a = Graph.from_edges(3, [(0, 1), (2, 1)])
        b = Graph.from_edges(3, [(1, 0), (1, 2)])
        self.assertEqual(S.direction_flips(a, b, {(0, 1), (1, 2)}), {"right_to_wrong": 1, "wrong_to_right": 1})


class _Evil:
    def __reduce__(self):
        return (os.system, ("echo pwned > %s" % os.path.join(tempfile.gettempdir(), "audit_pwned_marker"),))


class _EvilEval:
    def __reduce__(self):
        return (eval, ("__import__('os').getcwd()",))


class TestSafeUnpickler(unittest.TestCase):
    def test_builtins_eval_is_not_allowed(self):
        obj = pickle.loads(pickle.dumps({"x": _EvilEval()}))   # sanity: plain pickle WOULD run eval
        self.assertIsInstance(obj["x"], str)
        import io
        safe = cc_stages.SafeUnpickler(io.BytesIO(pickle.dumps({"x": _EvilEval(), "s": {1, 2}}))).load()
        self.assertNotIsInstance(safe["x"], str)
        self.assertEqual(safe["s"], {1, 2})

    def test_no_pickled_code_runs(self):
        marker = os.path.join(tempfile.gettempdir(), "audit_pwned_marker")
        if os.path.exists(marker):
            self.skipTest("marker from an earlier run exists and cannot be deleted here")
        with tempfile.NamedTemporaryFile(suffix=".pkl", delete=False) as fh:
            pickle.dump({"name": "x", "a": np.arange(3), "bad": _Evil()}, fh)
        obj = cc_stages.safe_load(fh.name)
        self.assertTrue(np.array_equal(obj["a"], np.arange(3)))
        self.assertFalse(os.path.exists(marker))


@unittest.skipUnless(HAVE_RUNS, "recorded Causal-Copilot runs are kept outside git")
class TestCausalCopilotStages(unittest.TestCase):
    def test_stage_rebuild_gates(self):
        tr = cc_stages.stages("20261011T184856Z_s2_q011_r01_b3a03d")
        self.assertEqual(tr["reached"], "S3")              # crashed in the cycle step
        self.assertTrue(all(tr["gates"].values()))
        self.assertTrue(tr["cycle_in_S3_pipeline_test"])

    def test_b3_gate(self):
        from crucis.rerun import existing as E
        t, _ = E.run(("B3",))
        s = t.summary("B3")
        self.assertTrue(s["pass"], [(r["audit"], r["system"], r["metric"], r["stored"], r["recomputed"]) for r in s["failed"]][:5])
        self.assertGreaterEqual(s["compared"], 1000)


if __name__ == "__main__":
    unittest.main()
