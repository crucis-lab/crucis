"""Graph encoding helpers shared by the analysis scripts (no repo imports needed).

Causal-Copilot adjacency convention (postprocess/visualization.py::convert_to_edges):
  M[i, j] = 1  ->  j -> i          2 -> undirected      3 -> bidirected
  M[i, j] = 4  ->  j o-> i         5 -> j o- i          6 -> o-o        7 -> "associated"
Ground-truth files use M[i, j] = 1 for j -> i as well (other values are ignored).
"""
import itertools

import numpy as np

CODE_NAMES = {1: "directed", 2: "undirected", 3: "bidirected", 4: "o->", 5: "o-", 6: "o-o", 7: "associated"}


def pair_type(M, a, b):
    """Typed relation of the unordered pair (a < b), as a short string using positions a and b."""
    x, y = int(M[a, b]), int(M[b, a])          # x: mark stored in row a (b -> a for code 1); y: row b
    if x == 0 and y == 0:
        return "none"
    if x == 1 and y == 1:
        return "conflict(both directions)"
    if x == 1 and y == 0:
        return "b->a"
    if y == 1 and x == 0:
        return "a->b"
    codes = {c for c in (x, y) if c != 0}
    if codes == {2}:
        return "undirected"
    if codes == {3}:
        return "bidirected"
    if codes == {6}:
        return "o-o"
    if codes == {7}:
        return "associated"
    if x == 4 and y == 0:
        return "b o-> a"
    if y == 4 and x == 0:
        return "a o-> b"
    if x == 5 and y == 0:
        return "b o- a"
    if y == 5 and x == 0:
        return "a o- b"
    return "mixed(%d,%d)" % (x, y)


def named(ptype, na, nb):
    """Render a pair type with variable names."""
    if ptype == "none":
        return "%s   %s (no edge)" % (na, nb)
    if ptype in ("a->b", "b->a", "a o-> b", "b o-> a", "a o- b", "b o- a"):     # positional patterns only
        return ptype.replace("a", "\0").replace("b", "\1").replace("\0", na).replace("\1", nb)
    sym = {"undirected": "---", "bidirected": "<->", "o-o": "o-o", "associated": "~~~"}.get(ptype, ptype)
    return "%s %s %s" % (na, sym, nb)


def pairs(p):
    return list(itertools.combinations(range(p), 2))


def is_adjacent(M, a, b):
    return bool(M[a, b] != 0 or M[b, a] != 0)


def truth_edges(T):
    """Directed truth edges as (cause, effect) index pairs: T[i, j] == 1 means j -> i."""
    T = np.asarray(T)
    return {(int(j), int(i)) for i, j in np.argwhere(T == 1)}


def truth_matrix(edges, p):
    M = np.zeros((p, p), dtype=int)
    for c, e in edges:
        M[e, c] = 1
    return M


def cpdag_of(edges, p):
    """CPDAG of a DAG given as (cause, effect) pairs, in the Causal-Copilot encoding.
    Pure-python Meek-rule implementation (no external dependency)."""
    adj = {frozenset(e) for e in edges}
    parents = {v: {c for c, e in edges if e == v} for v in range(p)}
    directed = set()
    # v-structures: c1 -> e <- c2 with c1, c2 non-adjacent
    for e in range(p):
        for c1, c2 in itertools.combinations(sorted(parents[e]), 2):
            if frozenset((c1, c2)) not in adj:
                directed.add((c1, e))
                directed.add((c2, e))
    und = {tuple(sorted(e)) for e in adj} - {tuple(sorted(d)) for d in directed}
    changed = True

    def has_dir(x, y):
        return (x, y) in directed

    def is_und(x, y):
        return tuple(sorted((x, y))) in und

    def adjacent(x, y):
        return frozenset((x, y)) in adj

    while changed:
        changed = False
        for (x, y) in list(und):
            for (u, v) in ((x, y), (y, x)):          # try to orient u -> v
                r1 = any(has_dir(w, u) and not adjacent(w, v) for w in range(p) if w not in (u, v))
                r2 = any(has_dir(u, w) and has_dir(w, v) for w in range(p) if w not in (u, v))
                r3 = False
                ws = [w for w in range(p) if w not in (u, v) and is_und(u, w) and has_dir(w, v)]
                for w1, w2 in itertools.combinations(ws, 2):
                    if not adjacent(w1, w2):
                        r3 = True
                if r1 or r2 or r3:
                    # only orient in the direction consistent with the DAG
                    if (u, v) in edges:
                        directed.add((u, v))
                        und.discard(tuple(sorted((u, v))))
                        changed = True
                        break
    M = np.zeros((p, p), dtype=int)
    for c, e in directed:
        M[e, c] = 1
    for x, y in und:
        M[x, y] = M[y, x] = 2
    return M


def score(M, edges, p):
    """Algorithm-agnostic scores of an estimate M against directed truth edges."""
    M = np.asarray(M)
    tadj = {frozenset(e) for e in edges}
    tp = fp = fn = 0
    correct = reversed_ = unoriented = 0
    for a, b in pairs(p):
        est = is_adjacent(M, a, b)
        tru = frozenset((a, b)) in tadj
        if est and tru:
            tp += 1
            t = pair_type(M, a, b)
            want = "a->b" if (a, b) in edges else "b->a"
            if t == want:
                correct += 1
            elif t in ("a->b", "b->a"):
                reversed_ += 1
            else:
                unoriented += 1
        elif est and not tru:
            fp += 1
        elif tru and not est:
            fn += 1
    prec = tp / (tp + fp) if tp + fp else None
    rec = tp / (tp + fn) if tp + fn else None
    f1 = (2 * prec * rec / (prec + rec)) if prec and rec else (0.0 if (tp + fp + fn) else None)
    # Directed-edge scores against the true DAG (the convention of DAG-level scoreboards such as
    # CausalArena): only a mark that commits to a direction counts as a prediction, so an honest
    # "adjacent, direction not identified" scores as a miss here. Reported next to the adjacency
    # scores on purpose; the gap between the two is the price of that convention.
    pred_dir = set()
    for a, b in pairs(p):
        t = pair_type(M, a, b)
        if t == "a->b":
            pred_dir.add((a, b))
        elif t == "b->a":
            pred_dir.add((b, a))
        elif t.startswith("conflict"):
            pred_dir.update({(a, b), (b, a)})
    dtp = len(pred_dir & set(edges))
    dprec = dtp / len(pred_dir) if pred_dir else None
    drec = dtp / len(edges) if edges else None
    df1 = (2 * dprec * drec / (dprec + drec)) if dprec and drec else (0.0 if (pred_dir or edges) else None)
    C = cpdag_of(set(edges), p)
    shd_cpdag = sum(1 for a, b in pairs(p) if _cmp_type(M, a, b) != _cmp_type(C, a, b))
    return {"adj_tp": tp, "adj_fp": fp, "adj_fn": fn, "adj_precision": prec, "adj_recall": rec, "adj_f1": f1,
            "true_edges_correctly_directed": correct, "true_edges_reversed": reversed_,
            "true_edges_present_but_not_directed": unoriented,
            "dir_predicted": len(pred_dir), "dir_tp": dtp, "dir_precision": dprec, "dir_recall": drec, "dir_f1": df1,
            "shd_vs_true_dag": fn + fp + reversed_ + unoriented, "shd_vs_true_cpdag": shd_cpdag}


def _cmp_type(M, a, b):
    t = pair_type(M, a, b)
    return t if t in ("none", "a->b", "b->a", "undirected") else "other:" + t
