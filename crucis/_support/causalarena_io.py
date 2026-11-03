"""Read CausalArena released sample files and score graphs in the scoreboard's units.

File layout (verified on all 50 public semantic scenarios, see reports/bundle1_results.md section 7):
  x         (n, d, 2) float32   x[:, :, 0] values (standardised), x[:, :, 1] 1.0 where that cell was intervened on
  g         (d, d)              g[i, j] == 1 means node_ids[i] -> node_ids[j]      (row = cause)
  node_ids  (d,)                variable names
  n_obs, n_int                  row counts; observational rows come first
Causal-Copilot's own convention is the transpose: M[i, j] == 1 means j -> i (row = effect).
"""
import json

import numpy as np


def load(path):
    z = np.load(path, allow_pickle=False)
    x = z["x"]
    return {"values": x[:, :, 0].astype(float), "intervened": x[:, :, 1] > 0, "g": (z["g"] != 0).astype(int),
            "node_ids": [str(s) for s in z["node_ids"]], "n_obs": int(z["n_obs"][0]), "n_int": int(z["n_int"][0]),
            "meta": json.loads(str(z["metadata_json"]))}


def true_edges(g):
    """Set of (cause, effect) index pairs."""
    return {(int(i), int(j)) for i, j in np.argwhere(np.asarray(g) != 0)}


def to_repo_matrix(g):
    """Reference graph in the convention the pipeline and cc_graph use (M[i, j] == 1 means j -> i)."""
    return (np.asarray(g) != 0).astype(int).T


def directed_scores(pred_directed, undirected, truth, d, rule, seed=None):
    """Directed-edge precision / recall / F1 and SHD for a graph given as committed arrows plus undecided pairs.

    pred_directed  set of (cause, effect); undirected  set of frozenset({a, b}); truth  set of (cause, effect)
    rule  how an undecided pair is turned into a prediction before scoring:
      "drop"   it is no prediction at all
      "both"   it predicts both directions
      "lower"  it predicts earlier column -> later column (this READS the column order; see causalarena_order_baseline.py)
      "random" it predicts one direction chosen by a random generator seeded per file (pass seed=...). This is the
               rule CausalArena states for PC and GIES (arXiv 2609.11897v1, Appendix B.2 and B.4).
    SHD counts one for every unordered pair whose predicted arrows differ from the true arrow(s).
    """
    pred = set(pred_directed)
    rng = np.random.default_rng(seed) if rule == "random" else None
    if rule == "random" and seed is None:
        raise ValueError("rule 'random' needs a seed")
    for pr in sorted(tuple(sorted(x)) for x in undirected):
        a, b = pr
        if rule == "random":
            pred.add((a, b) if rng.integers(2) == 0 else (b, a))
        elif rule == "both":
            pred |= {(a, b), (b, a)}
        elif rule == "lower":
            pred.add((a, b))
        elif rule != "drop":
            raise ValueError(rule)
    tp = len(pred & truth)
    prec = tp / len(pred) if pred else 0.0
    rec = tp / len(truth) if truth else 0.0
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
    shd = 0
    for a in range(d):
        for b in range(a + 1, d):
            if {e for e in pred if set(e) == {a, b}} != {e for e in truth if set(e) == {a, b}}:
                shd += 1
    return {"precision": prec, "recall": rec, "f1": f1, "shd": shd, "predicted": len(pred)}
