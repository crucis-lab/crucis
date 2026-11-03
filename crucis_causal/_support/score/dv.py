"""DV-1: "if I set T, does Y move?" (D0.4). Same rule as AB-04 (analysis/decision_value_v2.py), restated here.

For every intervention target T and every other variable Y the graph claims
  yes   Y is reachable from T through committed arrows,
  no    Y is not reachable from T even through undecided pairs,
and abstains otherwise. A claim is checked against the true graph's descendants of T.
Pooled over files: coverage = committed claims / (targets x (n - 1)); precision = correct committed / committed.
The empty graph ("nothing moves") claims "no" everywhere; its precision on the same files is the floor a graph must clear.

Selective view (B4): each claim carries a confidence; at cost ratio c/g a "yes" is worth acting on only when
P(correct) > c / (g + c) (AB-04's usefulness threshold). The view keeps claims whose confidence clears a threshold and
reports realised precision at the resulting coverage.
"""
from . import graph


def claims(n, directed, undecided, targets):
    """{(t, y): True (moves) | False (does not move)}; abstentions absent."""
    definite = graph.reach(n, directed)
    possible = graph.reach(n, directed, undecided)
    out = {}
    for t in targets:
        for y in range(n):
            if y == t:
                continue
            if y in definite[t]:
                out[(t, y)] = True
            elif y not in possible[t]:
                out[(t, y)] = False
    return out


def check(cl, true_desc):
    """[(t, y, claim, correct)] for committed claims."""
    return [(t, y, v, (y in true_desc[t]) == v) for (t, y), v in sorted(cl.items())]


def pooled(per_file):
    """per_file: {file: (checked_claims, n_pairs)} -> pooled coverage and precision (AB-04 definitions)."""
    pairs = yes = yes_t = no = no_t = 0
    for checked, npairs in per_file.values():
        pairs += npairs
        for _, _, v, ok in checked:
            if v:
                yes += 1
                yes_t += ok
            else:
                no += 1
                no_t += ok
    com = yes + no
    return {"files": len(per_file), "pairs": pairs, "committed": com,
            "coverage": com / pairs if pairs else None,
            "precision": (yes_t + no_t) / com if com else None,
            "precision_yes": yes_t / yes if yes else None, "precision_no": no_t / no if no else None,
            "yes_rate": yes / pairs if pairs else None}


def n_pairs(n, targets):
    return len(targets) * (n - 1)


def usefulness_threshold(cost_ratio):
    """Acting on a 'yes' beats doing nothing iff precision_yes > c / (g + c); cost_ratio = c / g."""
    return cost_ratio / (1.0 + cost_ratio)


def selective(scored, coverage_target=None, min_confidence=None):
    """scored: [(confidence, correct)] over all candidate claims of a pool (abstentions excluded).
    Keep the most confident claims, either the top share `coverage_target` of the pool (ties kept together) or every
    claim with confidence >= min_confidence. Returns kept count, share kept and realised precision."""
    if not scored:
        return {"kept": 0, "share": 0.0, "precision": None}
    s = sorted(scored, key=lambda t: -t[0])
    if min_confidence is not None:
        kept = [x for x in s if x[0] >= min_confidence]
    else:
        k = max(1, int(round(coverage_target * len(s))))
        cut = s[k - 1][0]
        kept = [x for x in s if x[0] >= cut]
    return {"kept": len(kept), "share": len(kept) / len(s), "precision": sum(ok for _, ok in kept) / len(kept) if kept else None}
