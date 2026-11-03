"""The sealed battery (protocol v1, section 1.6): commit, then reveal once per declared system version.

  commit   (M step, Uzair's machine) draws a secret master seed and a secret subset of scenarios, generates the items with
           the AB-08 generator (analysis/b2_generator.py: names suggest G_N, data follow G_D, a share rho of edges broken)
           into a seed store OUTSIDE the DSC 180A folder, and writes only a public manifest: generator code sha256 and the
           public parameters, the seed file's sha256, and each item's sha256. Nothing in it reveals a graph.
  check    regenerates every item from the stored seeds into a temporary folder and compares its sha256 with the manifest.
  read     one read per (system, version, battery): refused if READS.jsonl already has it, or after MAX_READS reads of the
           battery (then rotate to a new battery with new seeds). Only aggregates rounded to two decimals leave the store.
Why outside the folder: every chat of the project can read DSC 180A, W3 (the system's developers) included.
"""
import json
import os
import secrets
import tempfile
from pathlib import Path

from .canon import sha256_file, sha256_obj
from .paths import ANALYSIS, ROOT, import_paths

READS = ROOT / "crucis_causal" / "sealed" / "READS.jsonl"
MAX_READS = 5
SHARED = ROOT.parent                     # the DSC 180A folder


def default_store():
    home = os.environ.get("USERPROFILE") or os.path.expanduser("~")
    return Path(home) / ".causal-audit" / "sealed"


def guard_store(store):
    s = Path(store).resolve()
    if s == SHARED.resolve() or SHARED.resolve() in s.parents:
        raise PermissionError("the seed store must be outside %s (every project chat can read it)" % SHARED)
    return s


def _gen():
    import_paths()
    import sys
    if str(ANALYSIS) not in sys.path:
        pass  # Standalone package: no external source-path injection.
    from crucis_causal._support import b2_generator
    return b2_generator


def commit(battery_id, store=None, n_scenarios=20, rhos=(0.25, 0.5), tracks=("linear", "nonlinear"), reps=1,
           master_seed=None, slugs=None, manifest_out=None):
    """Generate a sealed battery. Returns the public manifest. Run by Uzair (M step); master_seed / slugs are for tests."""
    store = guard_store(store or default_store()) / battery_id
    store.mkdir(parents=True, exist_ok=True)
    G = _gen()
    seed = int(master_seed if master_seed is not None else secrets.randbits(62))
    if slugs is None:
        allslugs = sorted(s for s, _, _ in G.sources(str(ROOT / "external" / "causalarena"), str(ROOT / "plans" / "splits.json")))
        rng = __import__("numpy").random.default_rng(seed)
        slugs = sorted(rng.choice(allslugs, n_scenarios, replace=False).tolist())
    m, _ = G.generate(str(ROOT / "external" / "causalarena"), str(store / "items"), tuple(rhos), tuple(tracks), reps, seed,
                      str(ROOT / "plans" / "splits.json"), slugs=set(slugs), quiet=True)
    secret = {"battery_id": battery_id, "master_seed": seed, "slugs": list(slugs)}
    (store / "SECRET_seeds.json").write_text(json.dumps(secret, indent=1), encoding="utf-8")
    public = {"battery_id": battery_id, "version": "1", "visibility": "sealed",
              "generator": {"code_path": "analysis/b2_generator.py", "code_sha256": G.script_sha256(), "version": G.VERSION,
                            "public_params": {"rhos": list(rhos), "tracks": list(tracks), "reps": reps, "n_scenarios": len(slugs)}},
              "seed_file_sha256": sha256_file(store / "SECRET_seeds.json"),
              "items": [{"item_id": "s%03d" % i, "sha256": h} for i, (_, h) in enumerate(sorted(m["files"].items()))]}
    public["hash"] = sha256_obj({k: v for k, v in public.items() if k != "hash"})
    out = Path(manifest_out) if manifest_out else ROOT / "crucis_causal" / "sealed" / ("%s.manifest.json" % battery_id)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(public, indent=1, sort_keys=True), encoding="utf-8")
    return public


def check(manifest, store=None):
    """Regenerate every item from the stored seeds and compare with the public manifest's item hashes."""
    store = guard_store(store or default_store()) / manifest["battery_id"]
    sec_p = store / "SECRET_seeds.json"
    if sha256_file(sec_p) != manifest["seed_file_sha256"]:
        return False, "seed file does not match the manifest"
    sec = json.loads(sec_p.read_text(encoding="utf-8"))
    G = _gen()
    if G.script_sha256() != manifest["generator"]["code_sha256"]:
        return False, "generator code changed since the commit"
    p = manifest["generator"]["public_params"]
    with tempfile.TemporaryDirectory(dir=str(store)) as tmp:
        m, _ = G.generate(str(ROOT / "external" / "causalarena"), tmp, tuple(p["rhos"]), tuple(p["tracks"]), p["reps"],
                          sec["master_seed"], str(ROOT / "plans" / "splits.json"), slugs=set(sec["slugs"]), quiet=True)
    got = [h for _, h in sorted(m["files"].items())]
    want = [i["sha256"] for i in manifest["items"]]
    return got == want, "ok" if got == want else "regenerated items differ from the manifest"


def reads(path=None):
    p = Path(path or READS)
    if not p.exists():
        return []
    return [json.loads(line) for line in p.read_text(encoding="utf-8").splitlines() if line.strip()]


def read_allowed(system, version, battery_hash, path=None):
    rs = [r for r in reads(path) if r["battery_hash"] == battery_hash]
    if any(r["system"] == system and r["version"] == version for r in rs):
        return False, "this system version has already read this sealed battery"
    if len(rs) >= MAX_READS:
        return False, "battery has had %d reads: rotate to a new sealed battery" % len(rs)
    return True, "allowed (%d earlier reads of this battery)" % len(rs)


def record_read(system, version, battery_hash, report_sha256, utc, path=None):
    ok, why = read_allowed(system, version, battery_hash, path)
    if not ok:
        raise PermissionError(why)
    p = Path(path or READS)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as fh:
        fh.write(json.dumps({"system": system, "version": version, "battery_hash": battery_hash, "report_sha256": report_sha256,
                             "utc": utc}, sort_keys=True) + "\n")


def aggregate_only(result):
    """What leaves the seed store after a sealed read: per-arm aggregates and finding verdicts, two decimals, no runs."""
    def r2(x):
        if isinstance(x, float):
            return round(x, 2)
        if isinstance(x, dict):
            return {k: r2(v) for k, v in x.items() if k not in ("per_unit", "where")}
        if isinstance(x, list):
            return [r2(v) for v in x]
        return x
    return {"audit": result["audit"], "battery": result["battery"], "protocol": result["protocol"],
            "system": {"id": result["system"]["id"], "identity": result["system"]["identity"]},
            "l0": r2(result["l0"]), "findings": [{"id": f["id"], "kind": f["kind"], "verdict": f["verdict"],
                                                    "point": r2((f.get("effect") or {}).get("point"))} for f in result["findings"]]}
