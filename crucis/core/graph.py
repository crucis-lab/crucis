"""The typed mark graph every adapter returns (protocol v1, section 2.2).

A Graph over n variables holds
  directed    set of (cause, effect) index pairs the system commits to; a pair committed both ways (Causal-Copilot's
              "conflict") appears as both arrows
  undirected  set of (a, b) with a < b: adjacent, direction left open
  bidirected  set of (a, b) with a < b: <-> (latent confounding claimed)
  partial     set of (a, b, mark) with a < b for PAG and other marks that commit no direction: "a o-> b", "b o-> a",
              "a o- b", "b o- a", "o-o", "associated", "mixed(x,y)"
The undecided pairs (what the expectation rule orients at random) are undirected | bidirected | partial pairs.

Converters keep each source's own convention, stated once here:
  from_cc_matrix   Causal-Copilot / ground-truth matrices: M[i, j] = 1 means j -> i (analysis/cc_graph.py); the original
                   matrix is kept (raw) so to_cc_matrix gives it back exactly
  from_probe       harness/agent_probe.py result.json: directed [{from_idx, to_idx, source}], undecided [{a_idx, b_idx}]
                   or [[a, b]], over ORIGINAL column indices
  from_edges       edge lists: directed [[a, b]], undecided [[a, b, ...]] (method rows, result.json variants)
"""
from dataclasses import dataclass, field

import numpy as np

from .paths import import_paths

import_paths()
from crucis._support import cc_graph as CG  # noqa: E402


def _pair(a, b):
    a, b = int(a), int(b)
    return (a, b) if a < b else (b, a)


@dataclass(frozen=True)
class Graph:
    n: int
    directed: frozenset = frozenset()
    undirected: frozenset = frozenset()
    bidirected: frozenset = frozenset()
    partial: frozenset = frozenset()
    raw: tuple = field(default=None, compare=False, repr=False)       # original CC matrix (as nested tuples), if any

    # ------------------------------------------------------------------ constructors
    @staticmethod
    def from_edges(n, directed=(), undecided=(), bidirected=()):
        D = frozenset((int(e[0]), int(e[1])) for e in directed)
        U = frozenset(_pair(u[0], u[1]) for u in undecided)
        B = frozenset(_pair(u[0], u[1]) for u in bidirected)
        return Graph(int(n), D, U - B, B)

    @staticmethod
    def from_probe(n, res):
        """result.json of harness/agent_probe.py (directed dicts or pairs; undecided dicts or pairs)."""
        D, U = [], []
        for e in res.get("directed") or []:
            D.append((e["from_idx"], e["to_idx"]) if isinstance(e, dict) else (e[0], e[1]))
        for u in res.get("undecided") or []:
            U.append((u["a_idx"], u["b_idx"]) if isinstance(u, dict) else (u[0], u[1]))
        return Graph.from_edges(n, D, U)

    @staticmethod
    def from_cc_matrix(M):
        M = np.asarray(M)
        p = M.shape[0]
        D, U, B, P = set(), set(), set(), set()
        for a, b in CG.pairs(p):
            t = CG.pair_type(M, a, b)
            if t == "none":
                continue
            if t == "a->b":
                D.add((a, b))
            elif t == "b->a":
                D.add((b, a))
            elif t.startswith("conflict"):
                D |= {(a, b), (b, a)}
            elif t == "undirected":
                U.add((a, b))
            elif t == "bidirected":
                B.add((a, b))
            else:
                P.add((a, b, t))
        raw = tuple(tuple(int(x) for x in row) for row in M)
        return Graph(p, frozenset(D), frozenset(U), frozenset(B), frozenset(P), raw)

    # ------------------------------------------------------------------ views
    def undecided(self):
        """Adjacent pairs without one committed direction (the expectation rule orients these at random)."""
        return set(self.undirected) | set(self.bidirected) | {(a, b) for a, b, _ in self.partial}

    def committed(self):
        """Committed arrows, excluding pairs committed both ways."""
        return {e for e in self.directed if (e[1], e[0]) not in self.directed}

    def adjacencies(self):
        return {frozenset(e) for e in self.directed} | {frozenset(u) for u in self.undecided()}

    def marks(self):
        """The mark types this graph uses (checked against an adapter's declared capabilities)."""
        m = set()
        if self.directed:
            m.add("->")
        if self.undirected:
            m.add("--")
        if self.bidirected:
            m.add("<->")
        for _, _, t in self.partial:
            m.add({"associated": "~", "o-o": "o-o"}.get(t, "o->" if "o->" in t else "o-" if "o-" in t else "mixed"))
        return m

    def to_cc_matrix(self):
        """Causal-Copilot encoding (M[i, j] = 1 means j -> i). Exact inverse of from_cc_matrix; for other graphs:
        arrows 1, undirected 2 in both cells, bidirected 3 in both cells (partial marks need a raw matrix)."""
        if self.raw is not None:
            return np.array(self.raw, dtype=int)
        if self.partial:
            raise ValueError("partial marks without a raw matrix have no unique Causal-Copilot encoding")
        M = np.zeros((self.n, self.n), dtype=int)
        for c, e in self.directed:
            M[e, c] = 1
        for a, b in self.undirected:
            M[a, b] = M[b, a] = 2
        for a, b in self.bidirected:
            M[a, b] = M[b, a] = 3
        return M

    def mapped(self, perm):
        """Graph over shown positions -> graph over original columns: shown position k is original column perm[k]."""
        f = lambda i: int(perm[int(i)])  # noqa: E731
        return Graph(self.n, frozenset((f(a), f(b)) for a, b in self.directed),
                     frozenset(_pair(f(a), f(b)) for a, b in self.undirected),
                     frozenset(_pair(f(a), f(b)) for a, b in self.bidirected),
                     frozenset(self._map_partial(f)))

    def _map_partial(self, f):
        out = set()
        for a, b, t in self.partial:
            x, y = f(a), f(b)
            if x > y and t[:2] in ("a ", "b "):                     # positional marks swap their letters
                t = t.replace("a", "\0").replace("b", "a").replace("\0", "b")
            out.add((min(x, y), max(x, y), t))
        return out

    def canonical(self):
        return {"n": self.n, "directed": sorted(map(list, self.directed)), "undirected": sorted(map(list, self.undirected)),
                "bidirected": sorted(map(list, self.bidirected)), "partial": sorted(map(list, self.partial))}

    @staticmethod
    def from_canonical(d):
        return Graph(int(d["n"]), frozenset(map(tuple, d["directed"])), frozenset(map(tuple, d["undirected"])),
                     frozenset(map(tuple, d["bidirected"])), frozenset((int(a), int(b), t) for a, b, t in d["partial"]))
