"""A toy Python 'system' for the L2 recorder tests: a data stage, a pruning stage that deletes one true link, and a cycle
stage that raises on a cycle. Deterministic, so a hooked run must give exactly the unhooked output."""
import numpy as np


def discover(X):
    C = np.corrcoef(X, rowvar=False)
    d = C.shape[0]
    return {(i, j) for i in range(d) for j in range(i + 1, d) if abs(C[i, j]) > 0.3}


def prune(edges):
    return set(sorted(edges)[1:])            # drops the first edge, whatever it is


def break_cycles(edges, fail=False):
    if fail:
        raise KeyError("nodes")
    return set(edges)


def pipeline(X, fail=False):
    return break_cycles(prune(discover(X)), fail=fail)
