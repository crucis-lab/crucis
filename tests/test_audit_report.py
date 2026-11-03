from crucis.core.paths import ROOT as DATA_ROOT
"""Bundle B4 (DLV-09): findings, reports, certificates and the sealed battery. The certificate is deterministic, every
number in it has a derivation, verify catches a changed number and a changed raw file, a ranking across regimes is
refused, the sealed seed store cannot sit in the shared folder, a second sealed read is refused; MATMCD end to end."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from crucis.core import sealed  # noqa: E402
from crucis.protocol import kinds as K, regimes as R  # noqa: E402
from crucis.report import build, certificate as CERT  # noqa: E402

HAVE_DATA = (DATA_ROOT / "runs" / "ab06").is_dir() and (DATA_ROOT / "external" / "causalarena").is_dir()
_CACHE = {}


def matmcd():
    if "r" not in _CACHE:
        from crucis import run as RN
        _CACHE["r"] = RN.audit(RN.AUDITS["matmcd"], "matmcd")
    return _CACHE["r"]


class TestRanking(unittest.TestCase):
    def test_cross_regime_ranking_refused(self):
        with self.assertRaises(R.CrossRegime):
            build.ranking([{"regime": "D", "k_source": "none", "score": 1}, {"regime": "D+K", "k_source": "names_real", "score": 2}])
        self.assertEqual(len(build.ranking([{"regime": "D", "k_source": "none", "score": 1}] * 2)), 2)


class TestSealedRules(unittest.TestCase):
    def test_store_must_be_outside_the_shared_folder(self):
        with self.assertRaises(PermissionError):
            sealed.guard_store(ROOT / "anything")
        with self.assertRaises(PermissionError):
            sealed.guard_store(ROOT.parent / "seeds")

    def test_one_read_per_version_and_rotation(self):
        with tempfile.TemporaryDirectory() as d:
            log = Path(d) / "READS.jsonl"
            sealed.record_read("sysA", "v1", "h1", "r1", "2026-11-01T00:00:00Z", log)
            ok, why = sealed.read_allowed("sysA", "v1", "h1", log)
            self.assertFalse(ok)
            with self.assertRaises(PermissionError):
                sealed.record_read("sysA", "v1", "h1", "r2", "2026-11-01T00:00:01Z", log)
            for i in range(2, 6):
                sealed.record_read("sysA", "v%d" % i, "h1", "r", "t", log)
            ok, why = sealed.read_allowed("sysB", "v1", "h1", log)
            self.assertFalse(ok)
            self.assertIn("rotate", why)
            self.assertTrue(sealed.read_allowed("sysB", "v1", "h2", log)[0])

    @unittest.skipUnless((DATA_ROOT / "external" / "causalarena").is_dir(), "CausalArena files")
    def test_commit_then_check(self):
        with tempfile.TemporaryDirectory() as d:
            man = sealed.commit("sealed-test", store=d, rhos=(0.5,), tracks=("linear",), reps=1, master_seed=7,
                                slugs=["backup_frequency_ransomware_loss"], manifest_out=Path(d) / "m.json")
            self.assertEqual(len(man["items"]), 1)
            self.assertNotIn("master_seed", json.dumps(man))
            ok, why = sealed.check(man, store=d)
            self.assertTrue(ok, why)
            bad = dict(man, seed_file_sha256="0" * 64)
            self.assertFalse(sealed.check(bad, store=d)[0])

    def test_aggregate_only_leaves_no_runs(self):
        res = {"audit": "x", "battery": {}, "protocol": {}, "system": {"id": "s", "identity": {}},
               "l0": {"real": {"dir_f1@expect": 0.123456, "per_unit": {"a": 1}}}, "runs": [{"item": "secret"}],
               "findings": [{"id": "K04", "kind": "name_reliance", "verdict": "fires", "effect": {"point": 0.15555}}]}
        agg = sealed.aggregate_only(res)
        self.assertNotIn("runs", agg)
        self.assertEqual(agg["l0"]["real"]["dir_f1@expect"], 0.12)
        self.assertNotIn("per_unit", agg["l0"]["real"])


@unittest.skipUnless(HAVE_DATA, "AB-06 runs and CausalArena files are kept outside git")
class TestCertificate(unittest.TestCase):
    def test_one_finding_per_kind_with_typed_verdicts(self):
        fs = matmcd()["findings"]
        self.assertEqual([f["id"] for f in fs], [k["id"] for k in K.KINDS])
        self.assertTrue(all(f["verdict"] in K.VERDICTS for f in fs))
        self.assertTrue(all(f["reason"] for f in fs if f["verdict"] in ("not_checkable", "not_run")))
        by = {f["id"]: f for f in fs}
        self.assertEqual(by["K04"]["label"], "confirmatory")          # P9, hashed before the grid
        self.assertTrue(by["K15"]["label"].startswith("exploratory"))

    def test_deterministic_and_sourced(self):
        a = CERT.make(matmcd(), "cmd")
        b = CERT.make(copy.deepcopy(matmcd()), "cmd")
        self.assertEqual(a["sha256"], b["sha256"])
        self.assertGreater(len(a["body"]["numbers"]), 100)
        self.assertTrue(all(v["derivation"] for v in a["body"]["numbers"].values()))
        self.assertTrue(all(f["path"] and f["sha256"] for r in a["body"]["runs"] for f in r["files"].values()))

    def test_verify_passes_and_catches_tampering(self):
        from crucis import run as RN
        recompute = lambda name, spec: RN.audit(RN.spec_from_json(spec), name)  # noqa: E731
        cert = CERT.make(matmcd(), "cmd")
        self.assertTrue(CERT.verify(cert, recompute)["pass"])
        t = copy.deepcopy(cert)
        k = next(p for p in t["body"]["numbers"] if p.startswith("/l0/real/dir_f1@expect"))
        t["body"]["numbers"][k]["value"] += 0.01
        v = CERT.verify(t, recompute)
        self.assertFalse(v["hash_ok"])
        self.assertEqual([m["pointer"] for m in v["number_mismatches"]], [k])
        t2 = copy.deepcopy(cert)
        t2["body"]["runs"][0]["files"]["summary"]["sha256"] = "0" * 64
        self.assertIn(t2["body"]["runs"][0]["files"]["summary"]["path"], CERT.verify(t2, recompute)["files_changed"])

    def test_report_files(self):
        with tempfile.TemporaryDirectory() as d:
            out = build.write(matmcd(), d)
            md = Path(out["markdown"]).read_text(encoding="utf-8")
            self.assertIn("K04 | name_reliance | **fires**", md)
            self.assertIn("Typed gaps", md)
            rep = json.loads(Path(out["report"]).read_text(encoding="utf-8"))
            from crucis.core.evidence import pointer_get
            cert = json.loads(Path(out["certificate"]).read_text(encoding="utf-8"))
            for p, rec in list(cert["body"]["numbers"].items())[:200]:
                self.assertEqual(pointer_get(rep, p), rec["value"])       # every certified number is in report.json there


if __name__ == "__main__":
    unittest.main()
