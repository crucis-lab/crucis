from crucis.core.paths import ROOT as DATA_ROOT
"""Bundle B5 (DLV-09, DLV-10): the existing audits through the package. One command writes the comparison table and a
report + certificate per system; every stored number is reproduced within 0.001; certificates verify. Plus the live
path for the data-only baselines: PC run live through the adapter and the harness's shuffle gives the stored AB-01 graph
(skipped where causal-learn is not installed, as in the VM)."""
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

HAVE_DATA = (DATA_ROOT / "runs" / "ab06").is_dir() and (DATA_ROOT / "external" / "causalarena").is_dir()
HAVE_CL = importlib.util.find_spec("causallearn") is not None


@unittest.skipUnless(HAVE_DATA, "recorded runs and CausalArena files are kept outside git")
class TestRerun(unittest.TestCase):
    def test_one_command_reproduces_and_certifies(self):
        from crucis import run as RN
        from crucis.rerun import existing as E
        from crucis.report import certificate as CERT
        with tempfile.TemporaryDirectory() as d:
            rc = E.main(d, ("B1", "B2", "B3"), reports=True)
            self.assertEqual(rc, 0)
            comp = json.loads((Path(d) / "comparison.json").read_text(encoding="utf-8"))
            self.assertTrue(comp["summary"]["all"]["pass"])
            self.assertGreaterEqual(comp["summary"]["all"]["compared"], 1290)
            self.assertLessEqual(comp["summary"]["all"]["max_abs_diff"], 0.001)
            self.assertEqual(set(comp["reports"]), set(RN.AUDITS))
            for name in ("causaliq", "causal_copilot@main", "gies@formula"):
                cert = json.loads(Path(comp["reports"][name]["certificate"]).read_text(encoding="utf-8"))
                v = CERT.verify(cert, lambda n, s: RN.audit(RN.spec_from_json(s), n))
                self.assertTrue(v["pass"], (name, v["number_mismatches"][:3], v["verdict_changes"]))


@unittest.skipUnless(HAVE_DATA and HAVE_CL, "needs causal-learn (Uzair's machine or a container) and CausalArena files")
class TestLiveBaseline(unittest.TestCase):
    def test_pc_live_equals_stored_row(self):
        from crucis.core import adapter as A, battery as B, harness as H
        ad = A.get("pc")
        for item in B.ca_family("semantic").items[:2]:
            p, perm = H.present(item)
            live = H.map_back(ad.run(p, None, None, mode="live"), perm)
            self.assertEqual(live.graph, ad.recorded(item, "shuffled").graph, item.item_id)


if __name__ == "__main__":
    unittest.main()
