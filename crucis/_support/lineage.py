"""Edge lineage for one traced Causal-Copilot run.

Reconstructs the graph after each refinement step from the recorded evidence, checks the
reconstruction against the matrices the run actually produced, attributes every change to a step,
and scores each stage against ground truth when the run has one (or a reference graph if given).

  python lineage.py <run_dir> [--reference path/to/graph.npy] [--out DIR]

Needs the repo importable only to unpickle artifacts:  --repo PATH (default $CC_REPO or ~/cc).

Acceptance gates (all must hold, otherwise exit code 1):
  A  S0 (graph handed to refinement) equals the state's converted_graph
  B  S2 rebuilt from S0 + bootstrap buckets + LLM decisions equals the graph handed to the KCI step
  C  S3 rebuilt from S2 + KCI removals equals the graph handed to the cycle step
  D  the cycle step's output equals the state's revised_graph
  E  every cell that changed between consecutive stages is covered by that step's recorded evidence
  F  every LLM answer recorded refers to variables of this dataset
"""
import argparse
import glob
import json
import os
import pickle
import sys
from collections import Counter
from pathlib import Path

import numpy as np

from crucis._support import cc_graph as G  # noqa: E402

PROB_KEYS = [("certain_edges", "directed"), ("uncertain_edges", "undirected"), ("bi_edges", "bidirected"),
             ("half_certain_edges", "o->"), ("half_uncertain_edges", "o-"), ("none_edges", "o-o"),
             ("none_existence", "no edge")]


def load_run(run_dir, repo):
    pass  # Standalone package: no external source-path injection.
    arts = {}
    for f in sorted(glob.glob(os.path.join(run_dir, "artifacts", "*.pkl"))):
        with open(f, "rb") as fh:
            a = pickle.load(fh)
        arts.setdefault(a["name"], []).append(a)
    finals = sorted(glob.glob(os.path.join(run_dir, "state", "*99_final.pkl")))
    if not finals:
        raise SystemExit("run has no final state snapshot (did it complete?)")
    with open(finals[0], "rb") as fh:
        state = pickle.load(fh)
    meta = json.load(open(os.path.join(run_dir, "meta.json"), encoding="utf-8"))
    return arts, state, meta


def step_bootstrap(S0, buckets):
    """Independent re-statement of postprocess/judge.py:68-86."""
    S = S0.copy()
    added, deleted = [], []
    for i, j in buckets["high_prob_edges"]["non-exist"]:
        S[i, j] = 1
        S[j, i] = 0
        added.append((int(i), int(j)))
    for i, j in buckets["low_prob_edges"]["exist"]:
        S[i, j] = 0
        S[j, i] = 0
        deleted.append((int(i), int(j)))
    return S, added, deleted


def step_llm(S1, direct, forbid):
    """Independent re-statement of postprocess/judge.py:104-118."""
    S = S1.copy()
    for (j, i) in direct:
        if S[i, j] != 1 or S[j, i] != 0:
            S[i, j] = 1
            S[j, i] = 0
    for (j, i) in forbid:
        if S[i, j] != 0 or S[j, i] != 0:
            S[i, j] = S[j, i] = 0
    return S


def step_kci(S2, kci_removed):
    """Independent re-statement of postprocess/judge.py:124-125."""
    S = S2.copy()
    for (a, b) in kci_removed:
        S[b, a] = S[a, b] = 0
    return S


def changed_pairs(X, Y):
    p = X.shape[0]
    return [(a, b) for a, b in G.pairs(p) if X[a, b] != Y[a, b] or X[b, a] != Y[b, a]]


def parse_llm_letters(arts, cols):
    """All letters the LLM returned, keyed by unordered index pair. Returns (answers, unknown_names)."""
    low = [c.lower() for c in cols]
    out, unknown = [], []
    for a in arts.get("call_llm_new", []):
        ret = a.get("ret") or {}
        main_node = None
        try:
            prompt = a["args_before"]["args"][1]
            key = "about node "
            k = prompt.find(key)
            if k >= 0:
                main_node = prompt[k + len(key):].split(" from a domain knowledge", 1)[0].strip()
        except Exception:
            pass
        for pair, v in ret.items():
            try:
                left, right = [x.strip().strip('"').strip("'") for x in pair.strip("()").split(",")]
                il, ir = low.index(left.lower()), low.index(right.lower())
            except Exception:
                unknown.append(pair)
                continue
            out.append({"left": il, "right": ir, "letter": str(v.get("result", "")).strip(),
                        "explanation": v.get("explanation", ""), "main_node": main_node, "call_seq": a["seq"]})
    return out, unknown


def evidence_for(boot, a, b):
    """Bootstrap frequencies for the pair, expressed with a and b."""
    ev = {}
    ev["a->b"] = float(boot["certain_edges"][b, a])
    ev["b->a"] = float(boot["certain_edges"][a, b])
    for key, name in PROB_KEYS[1:]:
        if key in ("half_certain_edges", "half_uncertain_edges"):
            ev["a %s b" % name] = float(boot[key][b, a])
            ev["b %s a" % name] = float(boot[key][a, b])
        else:
            ev[name] = float(max(boot[key][a, b], boot[key][b, a]))
    return ev


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir")
    ap.add_argument("--repo", default=os.environ.get("CC_REPO", os.path.expanduser("~/cc")))
    ap.add_argument("--reference", default=None, help=".npy graph with M[i,j]==1 meaning j->i (used when the run has no ground truth)")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    run_dir = os.path.abspath(a.run_dir)
    arts, state, meta = load_run(run_dir, a.repo)
    cols = [str(c) for c in state.user_data.processed_data.columns]
    p = len(cols)

    qj = arts["quality_judge"][0]
    S0 = np.asarray(qj["args_before"]["kwargs"]["full_graph"]).copy()
    boot = arts["bootstrap"][0]["ret"][1]
    buckets = arts["bootstrap_recommend"][0]["ret"]
    direct, forbid = arts["llm_evaluation_new"][0]["ret"]
    kci = arts["kci_pruning"][0]
    cyc = arts["check_cycle"][0]
    S2_rec = np.asarray(kci["args_before"]["args"][1])
    S3_rec = np.asarray(cyc["args_before"]["args"][2])
    S4_rec = np.asarray(cyc["ret"])
    final = np.asarray(state.results.revised_graph)
    conv = np.asarray(state.results.converted_graph)

    S1, boot_added, boot_deleted = step_bootstrap(S0, buckets)
    S2 = step_llm(S1, direct, forbid)
    S3 = step_kci(S2, kci["ret"])
    letters, unknown = parse_llm_letters(arts, cols)

    gates = {
        "A_S0_equals_state_converted_graph": bool(conv.shape == S0.shape and np.array_equal(conv, S0)),
        "B_rebuilt_S2_equals_graph_into_KCI": bool(np.array_equal(S2, S2_rec)),
        "C_rebuilt_S3_equals_graph_into_cycle_step": bool(np.array_equal(S3, S3_rec)),
        "D_cycle_output_equals_state_revised_graph": bool(np.array_equal(S4_rec, final)),
    }
    # gate E: coverage of changes by recorded evidence
    boot_pairs = {tuple(sorted(x)) for x in boot_added + boot_deleted}
    llm_pairs = {tuple(sorted((int(i), int(j)))) for (i, j) in list(direct) + list(forbid)}
    kci_pairs = {tuple(sorted((int(i), int(j)))) for (i, j) in kci["ret"]}
    cov = {"bootstrap": set(changed_pairs(S0, S1)) <= boot_pairs,
           "llm": set(changed_pairs(S1, S2_rec)) <= llm_pairs,
           "kci": set(changed_pairs(S2_rec, S3_rec)) <= kci_pairs}
    gates["E_every_change_covered_by_step_evidence"] = bool(all(cov.values()))
    gates["F_all_llm_answers_name_dataset_variables"] = (len(unknown) == 0)

    stages = [("S0 algorithm output", S0), ("S1 after bootstrap edits", S1), ("S2 after LLM review", S2_rec),
              ("S3 after KCI pruning", S3_rec), ("S4 final (after cycle step)", S4_rec)]

    # truth / reference
    truth, truth_kind = None, None
    if getattr(state.user_data, "ground_truth", None) is not None:
        truth, truth_kind = np.asarray(state.user_data.ground_truth), "ground truth loaded by the pipeline"
    elif a.reference:
        truth, truth_kind = np.load(a.reference), "reference graph %s (not loaded by the pipeline)" % os.path.basename(a.reference)
    scores = None
    if truth is not None:
        E = G.truth_edges(truth)
        scores = {name: G.score(M, E, p) for name, M in stages}

    # per-pair lineage
    by_pair_letters = {}
    for x in letters:
        if x["left"] != x["right"]:
            by_pair_letters.setdefault(tuple(sorted((x["left"], x["right"]))), []).append(x)
    rows = []
    for (x, y) in G.pairs(p):
        types = [G.pair_type(M, x, y) for _, M in stages]
        if all(t == "none" for t in types) and (x, y) not in by_pair_letters:
            continue
        ev = evidence_for(boot, x, y)
        ans = [{"asked_as": "(%s, %s)" % (cols[l["left"]], cols[l["right"]]), "letter": l["letter"],
                "explanation": l["explanation"]} for l in by_pair_letters.get((x, y), [])]
        changes = []
        for k in range(1, len(stages)):
            if types[k] != types[k - 1]:
                changes.append({"step": ["bootstrap", "llm", "kci", "cycle"][k - 1],
                                "from": G.named(types[k - 1], cols[x], cols[y]), "to": G.named(types[k], cols[x], cols[y])})
        rows.append({"pair": [cols[x], cols[y]], "types": [G.named(t, cols[x], cols[y]) for t in types],
                     "changed": bool(changes), "changes": changes, "bootstrap_frequency": ev,
                     "kci_p_value_if_removed": next((float(v) for (i, j), v in kci["ret"].items()
                                                     if tuple(sorted((int(i), int(j)))) == (x, y)), None),
                     "llm_answers": ans,
                     "truth": (None if truth is None else
                               ("%s -> %s" % (cols[x], cols[y]) if (x, y) in G.truth_edges(truth) else
                                "%s -> %s" % (cols[y], cols[x]) if (y, x) in G.truth_edges(truth) else "no edge"))})

    # counters
    letter_hist = Counter(l["letter"] for l in letters if l["left"] != l["right"])
    self_pairs = sum(1 for l in letters if l["left"] == l["right"])
    asked_pairs = len(by_pair_letters)
    stable_nondirected_deleted = []
    for (i, j) in boot_deleted:
        x, y = sorted((i, j))
        ev = evidence_for(boot, x, y)
        best = max(((k, v) for k, v in ev.items() if k not in ("no edge", "a->b", "b->a")), key=lambda kv: kv[1])
        if G.is_adjacent(S0, x, y) and best[1] >= 0.5:
            stable_nondirected_deleted.append({"pair": [cols[x], cols[y]], "was": G.named(G.pair_type(S0, x, y), cols[x], cols[y]),
                                               "most_frequent_bootstrap_status": best[0].replace("a", cols[x]).replace("b", cols[y])
                                               if best[0][:1] in "ab" else best[0], "frequency": best[1]})
    llm_added, llm_added_vs_absence, llm_removed, llm_reoriented = [], [], [], []
    for (x, y) in changed_pairs(S1, S2_rec):
        t1, t2 = G.pair_type(S1, x, y), G.pair_type(S2_rec, x, y)
        ev = evidence_for(boot, x, y)
        item = {"pair": [cols[x], cols[y]], "from": G.named(t1, cols[x], cols[y]), "to": G.named(t2, cols[x], cols[y]),
                "adjacent_in_algorithm_output": G.is_adjacent(S0, x, y), "bootstrap_no_edge_frequency": ev["no edge"]}
        if t1 == "none":
            llm_added.append(item)
            if ev["no edge"] >= 0.9:
                llm_added_vs_absence.append(item)
        elif t2 == "none":
            llm_removed.append(item)
        else:
            llm_reoriented.append(item)
    final_edges = []
    for (x, y) in G.pairs(p):
        t = G.pair_type(S4_rec, x, y)
        if t == "none":
            continue
        last = None
        for k in range(len(stages) - 1, 0, -1):
            if G.pair_type(stages[k][1], x, y) != G.pair_type(stages[k - 1][1], x, y):
                last = ["bootstrap", "llm", "kci", "cycle"][k - 1]
                break
        final_edges.append({"edge": G.named(t, cols[x], cols[y]), "set_by": last or "algorithm (unchanged)",
                            "adjacent_in_algorithm_output": G.is_adjacent(S0, x, y),
                            "same_as_algorithm_output": G.pair_type(S0, x, y) == t,
                            "bootstrap_no_edge_frequency": evidence_for(boot, x, y)["no edge"]})

    out = {
        "run_id": meta.get("run_id"), "dataset": meta.get("dataset"), "stub_llm": meta.get("stub_llm"),
        "algorithm": getattr(state.algorithm, "selected_algorithm", None),
        "hyperparameters_used": state.algorithm.algorithm_arguments,
        "hyperparameters_proposed_by_llm_but_not_used": sorted(
            set((state.algorithm.algorithm_arguments_json or {}).get("hyperparameters", {})) - set(state.algorithm.algorithm_arguments or {})),
        "variables": cols, "n_pairs": len(G.pairs(p)), "gates": gates, "all_gates_pass": all(gates.values()),
        "bootstrap_iterations": len(arts.get("bootstrap_iteration", [])),
        "counts": {
            "edges_by_stage": {name: int(sum(1 for x, y in G.pairs(p) if G.is_adjacent(M, x, y))) for name, M in stages},
            "bootstrap_added": len(boot_added), "bootstrap_deleted": len({tuple(sorted(x)) for x in boot_deleted}),
            "existing_edges_deleted_by_bootstrap_whose_commonest_resampled_status_was_a_nondirected_edge": len(stable_nondirected_deleted),
            "llm_calls": len(arts.get("call_llm_new", [])), "llm_distinct_pairs_answered": asked_pairs,
            "llm_self_pairs_answered": self_pairs, "llm_letters": dict(letter_hist),
            "llm_added": len(llm_added), "llm_added_where_bootstrap_no_edge_frequency_ge_0.9": len(llm_added_vs_absence),
            "llm_removed": len(llm_removed), "llm_reoriented": len(llm_reoriented),
            "kci_removed": len(kci_pairs), "cycle_step_changes": len(changed_pairs(S3_rec, S4_rec)),
            "final_edges": len(final_edges),
            "final_edges_set_by": dict(Counter(e["set_by"] for e in final_edges)),
            "final_edges_identical_to_algorithm_output": sum(1 for e in final_edges if e["same_as_algorithm_output"]),
            "final_edges_with_no_adjacency_in_algorithm_output": sum(1 for e in final_edges if not e["adjacent_in_algorithm_output"]),
        },
        "stable_nondirected_edges_deleted_by_bootstrap": stable_nondirected_deleted,
        "llm_added": llm_added, "llm_removed": llm_removed, "llm_reoriented": llm_reoriented,
        "final_edges": final_edges, "truth_kind": truth_kind, "scores_by_stage": scores, "pairs": rows,
        "unparsed_llm_pairs": unknown,
        "matrices": {name: M.astype(int).tolist() for name, M in stages},
    }
    out_dir = Path(a.out) if a.out else Path(run_dir) / "analysis"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "lineage.json").write_text(json.dumps(out, indent=1, default=float), encoding="utf-8")
    (out_dir / "lineage.md").write_text(render(out), encoding="utf-8")
    print(render(out, brief=True))
    sys.exit(0 if out["all_gates_pass"] else 1)


def render(o, brief=False):
    L = ["# Edge lineage: %s" % o["run_id"], "",
         "Dataset `%s`, algorithm **%s** %s. %d variables, %d pairs. %d bootstrap resamples.%s" % (
             o["dataset"], o["algorithm"], json.dumps(o["hyperparameters_used"]), len(o["variables"]), o["n_pairs"],
             o["bootstrap_iterations"], "  **STUB LLM: plumbing only.**" if o["stub_llm"] else ""), ""]
    if o["hyperparameters_proposed_by_llm_but_not_used"]:
        L += ["Hyperparameters the LLM proposed that were not passed to the algorithm: %s" % o["hyperparameters_proposed_by_llm_but_not_used"], ""]
    L += ["## Gates", ""]
    for k, v in o["gates"].items():
        L.append("- %s: **%s**" % (k, "PASS" if v else "FAIL"))
    c = o["counts"]
    L += ["", "## Edges by stage", "", "| Stage | Adjacent pairs |" + (" adj P | adj R | adj F1 | true edges directed correctly | reversed | present, not directed | SHD vs CPDAG |" if o["scores_by_stage"] else ""),
          "|---|---|" + ("---|---|---|---|---|---|---|" if o["scores_by_stage"] else "")]
    for name, n in c["edges_by_stage"].items():
        row = "| %s | %d |" % (name, n)
        if o["scores_by_stage"]:
            s = o["scores_by_stage"][name]
            f = lambda v: "n/a" if v is None else "%.2f" % v
            row += " %s | %s | %s | %d | %d | %d | %d |" % (f(s["adj_precision"]), f(s["adj_recall"]), f(s["adj_f1"]),
                                                          s["true_edges_correctly_directed"], s["true_edges_reversed"],
                                                          s["true_edges_present_but_not_directed"], s["shd_vs_true_cpdag"])
        L.append(row)
    if o["truth_kind"]:
        L += ["", "Scored against: %s." % o["truth_kind"]]
    L += ["", "## What each step did", "",
          "- Bootstrap step: added %d, deleted %d. Of the deleted, %d were existing edges whose most frequent status across resamples was a non-directed edge (frequency >= 0.5)." % (
              c["bootstrap_added"], c["bootstrap_deleted"], c["existing_edges_deleted_by_bootstrap_whose_commonest_resampled_status_was_a_nondirected_edge"]),
          "- LLM review: %d calls, %d distinct pairs answered out of %d, plus %d self-pairs. Letters: %s." % (
              c["llm_calls"], c["llm_distinct_pairs_answered"], o["n_pairs"], c["llm_self_pairs_answered"], json.dumps(c["llm_letters"], sort_keys=True)),
          "- LLM effect: added %d (of which %d where the resamples showed no edge at frequency >= 0.9), removed %d, re-oriented %d." % (
              c["llm_added"], c["llm_added_where_bootstrap_no_edge_frequency_ge_0.9"], c["llm_removed"], c["llm_reoriented"]),
          "- KCI step removed %d. Cycle step changed %d." % (c["kci_removed"], c["cycle_step_changes"]),
          "- Final graph: %d edges; set by %s; %d identical to the algorithm's output; %d between pairs the algorithm did not connect." % (
              c["final_edges"], json.dumps(c["final_edges_set_by"]), c["final_edges_identical_to_algorithm_output"],
              c["final_edges_with_no_adjacency_in_algorithm_output"]), ""]
    if brief:
        return "\n".join(L)
    L += ["## Final edges", "", "| Edge | Set by | Adjacent in algorithm output | Resample frequency of 'no edge' |", "|---|---|---|---|"]
    for e in o["final_edges"]:
        L.append("| %s | %s | %s | %.2f |" % (e["edge"], e["set_by"], "yes" if e["adjacent_in_algorithm_output"] else "no", e["bootstrap_no_edge_frequency"]))
    L += ["", "## Pairs that changed", "", "| Pair | S0 | S1 | S2 | S3 | S4 | Truth/reference | LLM answers |", "|---|---|---|---|---|---|---|---|"]
    for r in o["pairs"]:
        if not r["changed"]:
            continue
        ans = "; ".join("%s=%s" % (x["asked_as"], x["letter"]) for x in r["llm_answers"]) or "-"
        L.append("| %s, %s | %s | %s | %s |" % (r["pair"][0], r["pair"][1], " | ".join(r["types"]), r["truth"] or "-", ans))
    L += ["", "Full per-pair evidence (resample frequencies by edge type, LLM explanations, KCI p-values) is in `lineage.json`.", ""]
    return "\n".join(L)


if __name__ == "__main__":
    main()
