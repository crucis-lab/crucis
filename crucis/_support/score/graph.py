"""Graph scores in the scoreboard's units (D0.4).

A predicted graph is (directed, undecided): directed is a set of (cause, effect) index pairs the method commits to;
undecided is a set of unordered pairs (frozenset or 2-tuple) the method found adjacent but left unoriented.
Truth is a set of (cause, effect) pairs.

Expectation rule (the controlled scoreboard's rule, CausalArena Appendix B): every undecided pair is oriented at random
by a generator seeded per file (seed = crc32(file name)), pairs taken in sorted order. This is identical to
analysis/causalarena_io.directed_scores(rule="random"); tests/test_score.py checks the two agree on random graphs.
"""
import zlib

import numpy as np


def file_seed(file_name):
    return zlib.crc32(file_name.encode())


def _pairs(undecided):
    return sorted(tuple(sorted(tuple(p))) for p in undecided)


def directed_f1(directed, undecided, truth, seed):
    """Directed-edge precision, recall, F1 with undecided pairs oriented at random (per-file seed)."""
    pred = set(map(tuple, directed))
    rng = np.random.default_rng(seed)
    for a, b in _pairs(undecided):
        pred.add((a, b) if rng.integers(2) == 0 else (b, a))
    truth = set(map(tuple, truth))
    tp = len(pred & truth)
    prec = tp / len(pred) if pred else 0.0
    rec = tp / len(truth) if truth else 0.0
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
    return {"precision": prec, "recall": rec, "f1": f1, "predicted": len(pred)}


def coords(directed, undecided, truth):
    """Skeleton F1 S, commit rate c, commit accuracy q, direction accuracy a = c q + (1 - c)/2 (AB-01 definitions)."""
    directed = set(map(tuple, directed))
    truth = set(map(tuple, truth))
    tadj = {frozenset(e) for e in truth}
    padj = {frozenset(e) for e in directed} | {frozenset(tuple(u)) for u in undecided}
    tp = len(tadj & padj)
    P = tp / len(padj) if padj else 0.0
    R = tp / len(tadj) if tadj else 0.0
    S = 2 * P * R / (P + R) if P + R else 0.0
    right = sum(1 for e in directed if e in truth)
    wrong = sum(1 for e in directed if (e[1], e[0]) in truth)
    c = (right + wrong) / tp if tp else 0.0
    q = right / (right + wrong) if right + wrong else None
    a = (right + 0.5 * (tp - right - wrong)) / tp if tp else 0.0
    return {"S": S, "skeleton_precision": P, "skeleton_recall": R, "c": c, "q": q, "a": a}


def reach(n, directed, undirected=()):
    """Descendants of every node through committed arrows (and, if given, undirected pairs in both directions)."""
    nxt = {i: set() for i in range(n)}
    for a, b in directed:
        nxt[a].add(b)
    for a, b in (tuple(u) for u in undirected):
        nxt[a].add(b)
        nxt[b].add(a)
    out = {}
    for s in range(n):
        stack, seen = [s], set()
        while stack:
            u = stack.pop()
            for v in nxt[u]:
                if v not in seen:
                    seen.add(v)
                    stack.append(v)
        out[s] = seen - {s}
    return out


def cpdag(truth, n):
    """CPDAG of a DAG given as (cause, effect) pairs: (compelled directed set, undirected pair set). Meek R1-R3 closure
    from the v-structures (R4 cannot fire from a DAG's v-structures alone)."""
    truth = set(map(tuple, truth))
    adj = {frozenset(e) for e in truth}
    parents = {v: {c for c, e in truth if e == v} for v in range(n)}
    directed = set()
    for e in range(n):
        ps = sorted(parents[e])
        for i in range(len(ps)):
            for j in range(i + 1, len(ps)):
                if frozenset((ps[i], ps[j])) not in adj:
                    directed |= {(ps[i], e), (ps[j], e)}
    und = {tuple(sorted(e)) for e in adj} - {tuple(sorted(d)) for d in directed}
    changed = True
    while changed:
        changed = False
        for (x, y) in sorted(und):
            for (u, v) in ((x, y), (y, x)):
                others = [w for w in range(n) if w not in (u, v)]
                r1 = any((w, u) in directed and frozenset((w, v)) not in adj for w in others)
                r2 = any((u, w) in directed and (w, v) in directed for w in others)
                r3 = any(tuple(sorted((u, a))) in und and tuple(sorted((u, b))) in und and (a, v) in directed and (b, v) in directed
                         and frozenset((a, b)) not in adj for a in others for b in others if a < b)
                if r1 or r2 or r3:
                    directed.add((u, v))
                    und.discard((x, y))
                    changed = True
                    break
    return directed, und
