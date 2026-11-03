"""AB-05 (AUD-37) agent probes: scenario loading, column shuffle and scoring.

`load`, `true_edges` and `directed_scores` are COPIED UNCHANGED from analysis/causalarena_io.py
(sha256 39f416b38e7916394963a2d643425e37eca539b454ab82e4502939f12fc5b087 at copy time, 2026-10-12) so the probe runner works
inside the container without depending on the analysis folder. tests/test_agent_probe.py checks that the copy still
agrees with the original when the original is importable.

Shuffle convention (same as analysis/causalarena_methods.py and baseline_variants_run.py):
    key  = basename of the scenario file
    perm = numpy.random.default_rng(shuffle_seed + crc32(key)).permutation(d)
    the agent sees column k = original column perm[k]; graphs are mapped back with perm.
Undecided pairs are scored under the "random" rule with seed crc32(key) (CausalArena's stated rule for PC/GIES).
"""
import json
import os
import zlib

import numpy as np

SOURCE_SHA256 = "39f416b38e7916394963a2d643425e37eca539b454ab82e4502939f12fc5b087"


def load(path):
    z = np.load(path, allow_pickle=False)
    x = z["x"]
    return {"values": x[:, :, 0].astype(float), "intervened": x[:, :, 1] > 0, "g": (z["g"] != 0).astype(int),
            "node_ids": [str(s) for s in z["node_ids"]], "n_obs": int(z["n_obs"][0]), "n_int": int(z["n_int"][0]),
            "meta": json.loads(str(z["metadata_json"]))}


def true_edges(g):
    """Set of (cause, effect) index pairs."""
    return {(int(i), int(j)) for i, j in np.argwhere(np.asarray(g) != 0)}


def directed_scores(pred_directed, undirected, truth, d, rule, seed=None):
    """Directed-edge precision / recall / F1 and SHD (copied unchanged from analysis/causalarena_io.py)."""
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


# ---------------------------------------------------------------------------------------------------- probe helpers

def file_key(path):
    return os.path.basename(path)


def shuffle_perm(path, d, shuffle_seed):
    """perm[k] = original column index shown to the agent at position k."""
    return [int(i) for i in np.random.default_rng(int(shuffle_seed) + zlib.crc32(file_key(path).encode())).permutation(d)]


def score_seed(path):
    return zlib.crc32(file_key(path).encode())


def domain_context(meta):
    """Coarse domain text given to agents that take a context/theme string: the scenario's domain_id, humanised
    (e.g. 'cybersecurity and it operations'). It names the field only; it carries no edge or order information."""
    return str(meta.get("domain_id") or "").replace("_", " ").strip()


def score_graph(directed, undirected, truth, d, seed):
    """Scores under the random rule (headline) plus drop and both, for reference."""
    out = {}
    for rule in ("random", "drop", "both"):
        s = directed_scores(set(directed), {frozenset(p) for p in undirected}, truth, d, rule, seed=seed)
        out[rule] = {k: (round(v, 6) if isinstance(v, float) else v) for k, v in s.items()}
    return out
