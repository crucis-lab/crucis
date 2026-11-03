"""Per-edge lineage across a system's stages (L2) and the stage finding kinds K10-K12.

A trace is [(stage name, Graph)] over the item's original columns, first the data stage. For every unordered pair the
type at each stage is read with analysis/cc_graph.pair_type ("none", "a->b", "b->a", "undirected", ...), so a change is
one of: added (none -> adjacent), deleted (adjacent -> none), flipped (a->b <-> b->a), oriented (undecided -> committed),
unoriented (committed -> undecided), retyped (any other change).
"set by" of a final pair is the last stage that changed its type (the rule of analysis/lineage.py); "algorithm" if none.
"""
from ..core.paths import import_paths
from ..metrics import l0

import_paths()
from crucis._support import cc_graph as CG  # noqa: E402

DIRECTED = ("a->b", "b->a")


def pair_types(g):
    M = g.to_cc_matrix()
    return {(a, b): CG.pair_type(M, a, b) for a, b in CG.pairs(g.n)}


def change(t0, t1):
    if t0 == t1:
        return None
    if t0 == "none":
        return "added"
    if t1 == "none":
        return "deleted"
    if t0 in DIRECTED and t1 in DIRECTED:
        return "flipped"
    if t1 in DIRECTED:
        return "oriented"
    if t0 in DIRECTED:
        return "unoriented"
    return "retyped"


def lineage(trace):
    """{pair: {"types": [...], "events": [(stage, kind)], "set_by": stage name or "algorithm"}} plus counts per stage."""
    types = [pair_types(g) for _, g in trace]
    names = [n for n, _ in trace]
    out, counts = {}, {n: {} for n in names[1:]}
    for p in types[0]:
        ts = [t[p] for t in types]
        ev = []
        for k in range(1, len(ts)):
            c = change(ts[k - 1], ts[k])
            if c:
                ev.append((names[k], c))
                counts[names[k]][c] = counts[names[k]].get(c, 0) + 1
        last = next((names[k] for k in range(len(ts) - 1, 0, -1) if ts[k] != ts[k - 1]), "algorithm")
        out[p] = {"types": ts, "events": ev, "set_by": last}
    return out, counts


def stage_scores(trace, tr):
    """L0 numbers of every stage graph against one reference."""
    return [(n, l0.score_graph(g, tr)) for n, g in trace]


def set_by_stage(trace, k):
    """Directed final arrows whose type was set at stage k and not changed afterwards (stability.py's N1 rule:
    type at k-1 differs from the final type, type at k equals it)."""
    tk1, tk, tf = pair_types(trace[k - 1][1]), pair_types(trace[k][1]), pair_types(trace[-1][1])
    out = []
    for (a, b), t in tf.items():
        if t not in DIRECTED or tk1[(a, b)] == t or tk[(a, b)] != t:
            continue
        out.append((a, b) if t == "a->b" else (b, a))
    return out


def follows_names(arrows, T_data, T_label):
    """Classify arrows by which reference has their pair adjacent: 'labels only' (T4), 'data only' (T1), both, neither."""
    ad, al = {frozenset(e) for e in T_data}, {frozenset(e) for e in T_label}
    out = {}
    for c, e in arrows:
        k = frozenset((c, e))
        out[(c, e)] = "both" if (k in ad and k in al) else "labels only" if k in al else "data only" if k in ad else "neither"
    return out


def direction_flips(g_in, g_out, T):
    """K12 inputs on true adjacencies the input committed: right->wrong and wrong->right flips."""
    T = set(T)
    ti, to = pair_types(g_in), pair_types(g_out)
    rw = wr = 0
    for (a, b), t in ti.items():
        if t not in DIRECTED or to[(a, b)] not in DIRECTED or to[(a, b)] == t:
            continue
        want = "a->b" if (a, b) in T else "b->a" if (b, a) in T else None
        if want is None:
            continue
        if t == want:
            rw += 1
        elif to[(a, b)] == want:
            wr += 1
    return {"right_to_wrong": rw, "wrong_to_right": wr}
