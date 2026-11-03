"""Scores through stage S3 for EVERY run that reached refinement, including runs that crashed in the cycle step.

Why: `lineage.py` needs a completed run. In bundle 1, 7 of 48 runs crashed inside the cycle-breaking step
(postprocess/judge_functions.py:562). A run reaches that code only when the graph handed to the cycle step is
cyclic by the pipeline's test, so completed runs are a selected sample. S3 (the
graph handed to the cycle step) exists for both groups, so comparing S3 over "completed" and over "all" shows
how much the selection matters.

  python partial_stages.py --runs-dir RUNS --label b1 --mapping datasets/suite_b1/MAPPING.json --repo ~/cc --out DIR

Gates
  Q1  rebuilt S2 and S3 equal the graphs the pipeline recorded (into KCI, into the cycle step) in every run that has them
  Q2  a run crashed in the cycle step only if S3 is cyclic by the pipeline's own test, and cycle-step LLM calls
      exist only in runs whose S3 is cyclic by that test
  Q3  every run with the label is accounted for (completed / S3 only / no graph), none silently dropped
"""
import argparse
import glob
import json
import os
import pickle
import statistics as st
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
from crucis._support import cc_graph as G  # noqa: E402
from crucis._support.lineage import step_bootstrap, step_kci, step_llm  # noqa: E402
from crucis._support.stability import ROLE_ORDER, arm_of, family_role  # noqa: E402


def _cyclic(p, arcs):
    out = {a: [] for a in range(p)}
    for u, v in arcs:
        out[u].append(v)
    colour = [0] * p

    def visit(u):
        colour[u] = 1
        for v in out[u]:
            if colour[v] == 1 or (colour[v] == 0 and visit(v)):
                return True
        colour[u] = 2
        return False
    return any(colour[u] == 0 and visit(u) for u in range(p))


def cycle_committed(M):
    """Cycle among committed directions only: code 1 at M[i,j] with an empty mirror cell means j -> i."""
    return _cyclic(M.shape[0], [(int(j), int(i)) for i, j in np.argwhere(M == 1) if M[j, i] == 0])


def cycle_as_pipeline(M):
    """The test postprocess/judge_functions.py:566-575 applies: zero the mirror cell of every 1, then read EVERY
    remaining non-zero cell as an arrow (whatever its code), and ask whether that directed graph is acyclic."""
    C = np.asarray(M).copy()
    ones = np.where(M == 1)
    C[(ones[1], ones[0])] = 0
    return _cyclic(C.shape[0], [(int(i), int(j)) for i, j in np.argwhere(C != 0)])


def load_artifacts(run_dir):
    arts = {}
    for f in sorted(glob.glob(os.path.join(run_dir, "artifacts", "*.pkl"))):
        with open(f, "rb") as fh:
            a = pickle.load(fh)
        arts.setdefault(a["name"], []).append(a)
    return arts


def cycle_calls(run_dir):
    """Every cycle-step request and the keys of the JSON object the model returned."""
    out = []
    f = Path(run_dir) / "llm_calls.jsonl"
    if not f.exists():
        return out
    for line in open(f, encoding="utf-8"):
        d = json.loads(line)
        if d.get("level") != "client" or not any("LLM_remove_cycles" in c for c in (d.get("caller") or [])):
            continue
        res = d.get("result")
        out.append({"cycle": (d.get("args") or {}).get("prompt"),
                    "answer_keys": sorted(res.keys()) if isinstance(res, dict) else None,
                    "answer": res if isinstance(res, dict) else str(res)[:200]})
    return out


def mean(xs):
    xs = [x for x in xs if x is not None]
    return round(st.mean(xs), 3) if xs else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs-dir", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--mapping", required=True)
    ap.add_argument("--repo", default=os.path.expanduser("~/cc"))
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    pass  # Standalone package: no external source-path injection.
    mapping = json.load(open(a.mapping, encoding="utf-8"))
    mdir = Path(a.mapping).resolve().parent
    rows, q1_bad, q2_bad = [], [], []
    for meta_f in sorted(Path(a.runs_dir).glob("*/meta.json")):
        meta = json.load(open(meta_f, encoding="utf-8"))
        if meta.get("label") != a.label or meta.get("stub_llm"):
            continue
        run_dir = meta_f.parent
        arm, spec = arm_of(meta, mapping)
        fam, role = family_role(arm, spec)
        fail = meta.get("failure") or None
        row = {"run_id": meta["run_id"], "arm": arm, "family": fam, "role": role,
               "completed": fail is None, "failure": (fail or {}).get("where") or (str(fail)[:160] if fail else None)}
        arts = load_artifacts(str(run_dir))
        need = ("quality_judge", "bootstrap_recommend", "llm_evaluation_new", "kci_pruning")
        if not all(k in arts for k in need) or arts["kci_pruning"][0].get("ret") is None:
            row["reached"] = "no refinement graph"
            rows.append(row)
            continue
        S0 = np.asarray(arts["quality_judge"][0]["args_before"]["kwargs"]["full_graph"]).copy()
        S1, _, _ = step_bootstrap(S0, arts["bootstrap_recommend"][0]["ret"])
        direct, forbid = arts["llm_evaluation_new"][0]["ret"]
        S2 = step_llm(S1, direct, forbid)
        S3 = step_kci(S2, arts["kci_pruning"][0]["ret"])
        S2_rec = np.asarray(arts["kci_pruning"][0]["args_before"]["args"][1])
        ok = np.array_equal(S2, S2_rec)
        if "check_cycle" in arts:
            ok = ok and np.array_equal(S3, np.asarray(arts["check_cycle"][0]["args_before"]["args"][2]))
        if not ok:
            q1_bad.append(meta["run_id"])
        row["reached"] = "S4" if row["completed"] else "S3"
        row["cycle_in_S3"] = bool(cycle_as_pipeline(S3))
        row["cycle_in_S3_committed_directions_only"] = bool(cycle_committed(S3))
        row["crashed_in_cycle_step"] = bool(fail) and "LLM_remove_cycles" in json.dumps(fail)
        if row["crashed_in_cycle_step"] != (row["cycle_in_S3"] and not row["completed"]):
            q2_bad.append(meta["run_id"])
        cyc_calls = cycle_calls(run_dir)
        row["cycle_llm_calls"] = len(cyc_calls)
        row["cycle_llm_answers"] = cyc_calls
        if bool(cyc_calls) != row["cycle_in_S3"]:
            q2_bad.append(meta["run_id"] + " (cycle-step LLM calls do not match the cycle test)")
        row["llm_set_cells"] = int(len(direct))
        p = S0.shape[0]
        for tag, key in (("data", "reference_by_data"), ("label", "reference_by_label")):
            if not spec.get(key):                      # neutral labels have no by-label reference
                continue
            E = G.truth_edges(np.load(mdir / spec[key]))
            for name, M in (("S0", S0), ("S1", S1), ("S3", S3)):
                s = G.score(M, E, p)
                row["%s_adj_f1_by_%s" % (name, tag)] = s["adj_f1"]
                row["%s_dir_f1_by_%s" % (name, tag)] = s["dir_f1"]
        rows.append(row)

    arms = {}
    for r in rows:
        arms.setdefault((r["family"], ROLE_ORDER.get(r["role"], 9), r["arm"], r["role"]), []).append(r)
    table = []
    for (fam, _, arm, role), rs in sorted(arms.items()):
        comp = [r for r in rs if r["completed"] and "S3_adj_f1_by_data" in r]
        allr = [r for r in rs if "S3_adj_f1_by_data" in r]
        table.append({
            "arm": arm, "family": fam, "role": role, "runs": len(rs), "completed": len(comp), "with_S3": len(allr),
            "cycle_in_S3_runs": sum(1 for r in allr if r["cycle_in_S3"]),
            "cycle_committed_runs": sum(1 for r in allr if r["cycle_in_S3_committed_directions_only"]),
            "S0_adj_all": mean([r["S0_adj_f1_by_data"] for r in allr]),
            "S3_adj_completed": mean([r["S3_adj_f1_by_data"] for r in comp]),
            "S3_adj_all": mean([r["S3_adj_f1_by_data"] for r in allr]),
            "S0_dir_all": mean([r["S0_dir_f1_by_data"] for r in allr]),
            "S3_dir_completed": mean([r["S3_dir_f1_by_data"] for r in comp]),
            "S3_dir_all": mean([r["S3_dir_f1_by_data"] for r in allr]),
            "S3_adj_all_by_label": mean([r.get("S3_adj_f1_by_label") for r in allr]),
            "S3_dir_all_by_label": mean([r.get("S3_dir_f1_by_label") for r in allr]),
        })
    by_role = {}
    for role in ("real", "neutral", "swapped"):
        allr = [r for r in rows if r["role"] == role and "S3_adj_f1_by_data" in r]
        comp = [r for r in allr if r["completed"]]
        by_role[role] = {
            "with_S3": len(allr), "completed": len(comp),
            "S3_below_S0_adj_all": sum(1 for r in allr if r["S3_adj_f1_by_data"] < r["S0_adj_f1_by_data"]),
            "S0_adj_all": mean([r["S0_adj_f1_by_data"] for r in allr]),
            "S3_adj_completed": mean([r["S3_adj_f1_by_data"] for r in comp]),
            "S3_adj_all": mean([r["S3_adj_f1_by_data"] for r in allr]),
            "S0_dir_all": mean([r["S0_dir_f1_by_data"] for r in allr]),
            "S3_dir_completed": mean([r["S3_dir_f1_by_data"] for r in comp]),
            "S3_dir_all": mean([r["S3_dir_f1_by_data"] for r in allr])}
    reached = {}
    for r in rows:
        reached[r["reached"]] = reached.get(r["reached"], 0) + 1
    calls = [c for r in rows for c in r.get("cycle_llm_answers", [])]
    keys = {}
    for c in calls:
        k = ",".join(c["answer_keys"]) if c["answer_keys"] is not None else "(not a JSON object)"
        keys[k] = keys.get(k, 0) + 1
    cyc_runs = [r for r in rows if r.get("cycle_in_S3")]
    cycle_summary = {"runs_cyclic_by_pipeline_test": len(cyc_runs),
                     "of_which_cyclic_among_committed_directions": sum(1 for r in cyc_runs if r["cycle_in_S3_committed_directions_only"]),
                     "of_which_completed": sum(1 for r in cyc_runs if r["completed"]),
                     "by_role": {role: sum(1 for r in cyc_runs if r["role"] == role) for role in ("real", "neutral", "swapped")},
                     "cycle_step_llm_calls": len(calls), "answer_keys": keys}
    gates = {"Q1_rebuilt_S2_S3_equal_recorded": not q1_bad, "Q2_cycle_crashes_have_cycle_in_S3": not q2_bad,
             "Q3_all_runs_accounted": sum(reached.values()) == len(rows) and len(rows) > 0}
    out = {"label": a.label, "runs": len(rows), "reached": reached, "gates": gates, "q1_bad": q1_bad, "q2_bad": q2_bad,
           "cycle_step": cycle_summary, "by_arm": table, "by_role": by_role, "rows": rows}
    os.makedirs(a.out, exist_ok=True)
    json.dump(out, open(os.path.join(a.out, "partial_stages.json"), "w", encoding="utf-8"), indent=1)
    L = ["# Scores through S3 for all runs that reached refinement (label %s)" % a.label, "",
         "Runs: %d. Reached: %s." % (len(rows), ", ".join("%s %d" % kv for kv in sorted(reached.items()))), "",
         "Gates: " + "; ".join("%s %s" % (k, "PASS" if v else "FAIL") for k, v in gates.items()), "",
         "Scores are against the by-data reference unless a column says by label. S3 is the graph handed to the cycle step.", "",
         "| arm | family | role | runs | completed | with S3 | S3 cyclic by the pipeline's test | of which cyclic among committed directions | adjacency F1 S0 | S3 (completed) | S3 (all) | directed F1 S0 | S3 (completed) | S3 (all) | S3 all, by label: adjacency | directed |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for t in table:
        L.append("| %s |" % " | ".join(str(t[k]) for k in ("arm", "family", "role", "runs", "completed", "with_S3", "cycle_in_S3_runs", "cycle_committed_runs",
                 "S0_adj_all", "S3_adj_completed", "S3_adj_all", "S0_dir_all", "S3_dir_completed", "S3_dir_all",
                 "S3_adj_all_by_label", "S3_dir_all_by_label")))
    L += ["", "| role | with S3 | completed | S3 adjacency F1 below S0 (all) | adjacency F1 S0 | S3 (completed) | S3 (all) | directed F1 S0 | S3 (completed) | S3 (all) |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for role, t in by_role.items():
        L.append("| %s | %s |" % (role, " | ".join(str(t[k]) for k in ("with_S3", "completed", "S3_below_S0_adj_all", "S0_adj_all",
                 "S3_adj_completed", "S3_adj_all", "S0_dir_all", "S3_dir_completed", "S3_dir_all"))))
    L += ["", "Cycle step: " + json.dumps(cycle_summary)]
    open(os.path.join(a.out, "partial_stages.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))
    sys.exit(0 if all(gates.values()) else 1)


if __name__ == "__main__":
    main()
