"""Recompute the facts the W2 rebase (crucis/docs/project/w2-rebase-2026-10-31.md) rests on. Read-only; NumPy only.

  python crucis/docs/checks/rebase_facts.py [--reports crucis/results/rerun_v1] [--out FILE]

Prints one JSON object. Every value below is quoted in the rebase or in section 2a of the W1 checkpoint doc; a run that
prints different values means the ground moved and the rebase must be re-read before any design work continues.
  rerun        comparison.json summary (expect 1298 compared, all pass, max_abs_diff <= 0.001)
  grid         verdict counts over 15 kinds x 14 audits (expect 79 measured: 30 fires, 43 clear, 6 inconclusive)
  stages       Causal-Copilot adjacency F1 per stage, paired over completed runs, fork main and BND-08
               (expect main S0->S1 -0.270 [-0.327, -0.200], S1->S2 +0.007 [-0.027, +0.042], n = 22)
  cycle_step   fork main: runs entering the cycle step, crashed there, completed (expect 8, 8, 0)
  overlap      scenarios shared by ca-ab06 and q1s2 (expect 0); q1s2 scenarios with a CausalArena obs_int twin (expect 10)
  causaliq_probabilities   whether calls.jsonl responses carry per-edge existence/orientation probabilities (expect true)
"""
import argparse
import collections
import glob
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))


def rerun_and_grid(reports):
    comp = json.loads((Path(reports) / "comparison.json").read_text(encoding="utf-8"))
    out = {"rerun": {k: comp["summary"]["all"][k] for k in ("compared", "passed", "max_abs_diff", "pass")}}
    tot, gaps = collections.Counter(), collections.Counter()
    for name, r in comp.get("reports", {}).items():
        p = Path(r["report"])
        p = p if p.is_absolute() and p.exists() else ROOT / r["report"]
        if not p.exists():                                    # reports written on another host: resolve by folder name
            p = Path(reports) / "reports" / name.replace("@", "_") / "report.json"
        rep = json.loads(p.read_text(encoding="utf-8"))
        for f in rep["findings"]:
            tot[f["verdict"]] += 1
            if f["verdict"] in ("not_checkable", "not_run"):
                gaps[(f["id"], f["verdict"], (f.get("reason") or "")[:70])] += 1
    out["grid"] = {"cells": sum(tot.values()), "verdicts": dict(tot),
                   "measured": tot["fires"] + tot["clear"] + tot["inconclusive"],
                   "gap_reasons": [{"kind": k, "verdict": v, "reason": r, "cells": n} for (k, v, r), n in sorted(gaps.items())]}
    return out


def stages():
    from crucis.rerun.existing import Cache, NAME_ARMS
    from crucis.controls import effects as E
    c, out = Cache(), {}
    for src in ("main", "bnd08"):
        ad, b, recs, sc = c.get("causal_copilot", "q1s2", NAME_ARMS, source=src)
        stg = ["S0", "S1", "S2", "S3", "S4"]
        comp = [r for r in recs if r.status == "ok" and all(s in r.variants for s in stg)]
        trans = []
        for a, z in zip(stg[:-1], stg[1:]):
            e = E.paired({(r.item, r.arm): sc[(r.item, r.arm)]["variants"][z]["adj_f1"] for r in comp},
                         {(r.item, r.arm): sc[(r.item, r.arm)]["variants"][a]["adj_f1"] for r in comp}, lambda u: u[0])
            trans.append({"stage": "%s->%s" % (a, z), "point": round(e["point"], 3), "lo": round(e["lo"], 3),
                          "hi": round(e["hi"], 3), "n": e["units"]})
        allr = [r for r in recs if "S0" in r.variants]
        s0_all = sum(sc[(r.item, r.arm)]["variants"]["S0"]["adj_f1"] for r in allr) / len(allr)
        fin = sum(sc[(r.item, r.arm)]["variants"]["S4"]["adj_f1"] for r in comp) / len(comp)
        out[src] = {"runs": len(recs), "completed": len(comp), "S0_adj_all_runs": round(s0_all, 3),
                    "final_adj_completed": round(fin, 3), "transitions": trans,
                    "cycle_step": {"entering": sum(bool(r.notes.get("cycle_in_S3_pipeline_test")) for r in recs),
                                   "crashed_there": sum(bool(r.notes.get("crashed_in_cycle_step")) for r in recs),
                                   "entering_and_completed": sum(r.status == "ok" for r in recs
                                                                 if r.notes.get("cycle_in_S3_pipeline_test"))}}
    return out


def overlap():
    m = json.loads((ROOT / "datasets" / "suite_q1s2" / "MAPPING.json").read_text(encoding="utf-8"))
    q = sorted({a["scenario_id"] for a in m["arms"].values()})
    ab = sorted({json.loads(Path(p).read_text(encoding="utf-8"))["scenario_id"] for p in glob.glob(str(ROOT / "plans" / "ab06" / "*__*__*.json"))})
    twins = [s for s in q if glob.glob(str(ROOT / "external" / "causalarena" / "scm" / "semantic" / "data" / "semantic_obs_int" /
                                           ("*%s__semantic_obs_int__rep000.npz" % s)))]
    return {"q1s2_scenarios": len(q), "ab06_scenarios": len(ab), "shared": len(set(q) & set(ab)), "q1s2_with_obs_int_twin": len(twins)}


def causaliq_probabilities():
    fs = sorted(glob.glob(str(ROOT / "runs" / "ab06" / "causaliq" / "*" / "real" / "calls.jsonl")))
    if not fs:
        return {"checked": 0, "note": "runs/ab06 not on this machine"}
    has = 0
    for f in fs:
        for line in open(f, encoding="utf-8"):
            t = json.loads(line).get("response_text") or ""
            has += '"existence"' in t and '"orientation"' in t
            break
    return {"checked": len(fs), "with_probabilities": has}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reports", default=str(ROOT / "crucis" / "results" / "rerun_v1"))
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    out = rerun_and_grid(a.reports)
    out["stages"] = stages()
    out["overlap"] = overlap()
    out["causaliq_probabilities"] = causaliq_probabilities()
    s = json.dumps(out, indent=1)
    if a.out:
        Path(a.out).write_text(s, encoding="utf-8")
    print(s)


if __name__ == "__main__":
    main()
