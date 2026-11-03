"""B0 gate for D0.4: the scorer reproduces the audit chapter's numbers to 0.001 before anything is scored with it.

  python -m score.repro [--out analysis/results/q2_b0/scorer_repro.json]

Recomputes, from the stored per-file method rows and the released files:
  AB-01 controlled scoreboard (analysis/results/rescore_v2/rescore_v2.json): S, c, q, a, F1 under the expectation
        rule, released and shuffled, for PC maxP, GES (BIC), GIES with targets, on semantic and formula;
  AB-04 DV-1 (analysis/results/decision_value_v2/decision_value_v2.json): coverage and precision of committed claims,
        released and shuffled, for the same methods plus the empty graph on the same files.
Pass: every recomputed number within 0.001 of the stored one. Writes the comparison table. No model calls.
Tickets: BLD-02, EVL-03
"""
import argparse, json, statistics as st, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
from crucis._support.score import bench, dv, graph  # noqa: E402

AB01 = {"PC (upstream, maxP)": {f: ("pc_upstream_maxp_%s_obs_rel" % f, "pc_upstream_maxp_%s_obs_shuf" % f) for f in bench.FAMILIES},
        "GES (BIC)": {"semantic": ("gesbic_semantic_obs", "gesbic_semantic_obs_shuf"), "formula": ("gesbic_formula_obs_rel", "gesbic_formula_obs_shuf")},
        "GIES with targets (D+I)": {f: ("gies_targets_%s_obsint_rel" % f, "gies_targets_%s_obsint_shuf" % f) for f in bench.FAMILIES}}
AB04 = {"PC, upstream maxP": "PC (upstream, maxP)", "GES (BIC)": "GES (BIC)", "GIES with targets (D+I)": "GIES with targets (D+I)"}
TOL = 0.001


def ok_rows(name):
    return {f: r for f, r in bench.method_rows(name).items() if not r.get("failed")}


def ab01(fam, rel, shuf):
    R, S = ok_rows(rel), ok_rows(shuf)
    common = sorted(set(R) & set(S))
    out = {}
    for arm, rows in (("released", R), ("shuffled", S)):
        xs = []
        for f in common:
            T = bench.truth_info(fam, f)["T"]
            D, U = bench.row_graph(rows[f])
            c = graph.coords(D, U, T)
            c["F1_random"] = graph.directed_f1(D, U, T, graph.file_seed(f))["f1"]
            xs.append(c)
        out[arm] = {k: round(st.mean([x[k] for x in xs if x[k] is not None]), 4) for k in ("S", "c", "q", "a", "F1_random")}
    out["files_paired"] = len(common)
    return out


def ab04(fam, name):
    rows = ok_rows(name)
    per, empty = {}, {}
    for f, r in rows.items():
        I = bench.truth_info(fam, f)
        D, U = bench.row_graph(r)
        npairs = dv.n_pairs(I["n"], I["targets"])
        per[f] = (dv.check(dv.claims(I["n"], D, U, I["targets"]), I["desc"]), npairs)
        empty[f] = (dv.check(dv.claims(I["n"], set(), set(), I["targets"]), I["desc"]), npairs)
    p, e = dv.pooled(per), dv.pooled(empty)
    return {"files": p["files"], "coverage": round(p["coverage"], 4), "precision_committed": round(p["precision"], 4),
            "empty_precision": round(e["precision"], 4)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "analysis" / "results" / "q2_b0" / "scorer_repro.json"))
    a = ap.parse_args()
    ref01 = json.load(open(ROOT / "analysis" / "results" / "rescore_v2" / "rescore_v2.json"))["methods"]
    ref04 = json.load(open(ROOT / "analysis" / "results" / "decision_value_v2" / "decision_value_v2.json"))["families"]
    comps = []
    for label, fams in AB01.items():
        for fam, (rel, shuf) in fams.items():
            mine, ref = ab01(fam, rel, shuf), ref01[label][fam]
            for arm in ("released", "shuffled"):
                for k in ("S", "c", "q", "a", "F1_random"):
                    comps.append({"table": "AB-01", "method": label, "family": fam, "arm": arm, "metric": k,
                                  "stored": ref[arm][k], "recomputed": mine[arm][k]})
            comps.append({"table": "AB-01", "method": label, "family": fam, "arm": "both", "metric": "files_paired",
                          "stored": ref["files_paired"], "recomputed": mine["files_paired"]})
    for lab4, lab1 in AB04.items():
        for fam in bench.FAMILIES:
            for arm, name in zip(("released", "shuffled"), AB01[lab1][fam]):
                ref = ref04[fam][lab4][arm]
                mine = ab04(fam, name)
                for k in ("coverage", "precision_committed"):
                    comps.append({"table": "AB-04", "method": lab4, "family": fam, "arm": arm, "metric": k, "stored": ref[k], "recomputed": mine[k]})
                comps.append({"table": "AB-04", "method": lab4, "family": fam, "arm": arm, "metric": "files", "stored": ref["files"], "recomputed": mine["files"]})
                comps.append({"table": "AB-04", "method": "empty graph (same files)", "family": fam, "arm": arm, "metric": "precision_committed",
                              "stored": None, "recomputed": mine["empty_precision"]})
    for c in comps:
        c["diff"] = None if c["stored"] is None else round(abs(c["recomputed"] - c["stored"]), 6)
    checked = [c for c in comps if c["diff"] is not None]
    worst = max(c["diff"] for c in checked)
    res = {"tickets": ["BLD-02", "EVL-03"], "gate": "D0.4: every recomputed number within %.3f of the stored one" % TOL,
           "compared": len(checked), "max_abs_diff": worst, "pass": worst <= TOL, "rows": comps}
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    json.dump(res, open(a.out, "w"), indent=1)
    print("compared %d numbers; max |diff| %.6f; %s" % (len(checked), worst, "PASS" if res["pass"] else "FAIL"))
    for c in checked:
        if c["diff"] > TOL:
            print("  ", c)
    sys.exit(0 if res["pass"] else 1)


if __name__ == "__main__":
    main()
