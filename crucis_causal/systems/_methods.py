"""Shared base for the data-only algorithms whose per-file outputs the audit chapter stored (analysis/results/methods).

recorded  one row per file from analysis/results/methods/<name>.json: committed arrows and undecided pairs over ORIGINAL
          column indices (the runner mapped shuffled columns back), plus the failure message when the method failed
live      the algorithm on the shown matrix (needs causal-learn / ges; Uzair's machine or a container: the VM has no SciPy)
Arms: "released" (columns in the file's own order) and "shuffled" (seed 20261010), the AB-01 layout control.
"""
import json
from functools import lru_cache

import numpy as np

from ..core.adapter import Adapter
from ..core.canon import sha256_file
from ..core.graph import Graph
from ..core.paths import ROOT, import_paths, rel
from ..core.runs import FAILED, NOT_RUN, RunRecord

METHODS = ROOT / "analysis" / "results" / "methods"


@lru_cache(maxsize=None)
def _rows(name):
    p = METHODS / (name + ".json")
    d = json.loads(p.read_text(encoding="utf-8"))
    return {r["file"].replace("_obs_int__", "_obs_only__"): r for r in d["rows"]}, d.get("header", {}), rel(p), sha256_file(p)


def marks_graph(A):
    """causal-learn endpoint matrix (A[i, j] = mark at i: -1 tail, 1 arrowhead, 2 circle) -> Graph, by the rule of
    analysis/causalarena_methods.marks_to_graph: tail-arrowhead is committed, every other mark pair is undecided."""
    A = np.asarray(A)
    d = A.shape[0]
    D, U, B = [], [], []
    for i in range(d):
        for j in range(i + 1, d):
            mi, mj = int(A[i, j]), int(A[j, i])
            if mi == 0 and mj == 0:
                continue
            if mi == -1 and mj == 1:
                D.append((i, j))
            elif mi == 1 and mj == -1:
                D.append((j, i))
            elif mi == 1 and mj == 1:
                B.append((i, j))
            else:
                U.append((i, j))
    return Graph.from_edges(d, D, U, B)


class StoredMethod(Adapter):
    rows = {}            # (family, arm) -> stored method name

    def identity(self):
        out = super().identity()
        hdr = {k: _rows(v)[1] for k, v in sorted(self.rows.items(), key=lambda kv: str(kv[0]))[:1]}
        out["engine"] = next(iter(hdr.values()), {}).get("engine") or next(iter(hdr.values()), {}).get("causal_learn")
        return out

    def recorded(self, item, arm, **_):
        name = self.rows.get((item.family, arm))
        if name is None:
            return RunRecord(self.name, item.item_id, arm, NOT_RUN)
        rows, hdr, path, sha = _rows(name)
        r = rows.get(item.item_id)
        files = {"rows": {"path": path, "sha256": sha, "pointer": item.item_id}}
        if r is None:
            return RunRecord(self.name, item.item_id, arm, NOT_RUN, files=files)
        cost = {"usd": 0.0, "seconds": (r.get("metrics") or {}).get("seconds")}
        if r.get("failed"):
            status = "aborted_cap" if str(r["failed"]).startswith("TimeoutError") else FAILED   # the runner's time cap
            return RunRecord(self.name, item.item_id, arm, status, cost=cost, failure={"message": r["failed"]}, files=files)
        g = Graph.from_edges(item.n, [tuple(e) for e in r["directed_edges"]], [tuple(u[:2]) for u in r["undecided_pairs"]])
        return RunRecord(self.name, item.item_id, arm, "ok", graph=g, cost=cost, files=files,
                         notes={"stored_method": name, "engine": hdr.get("engine") or hdr.get("causal_learn"),
                                "file_read": r["file"]})

    def run(self, presented, budget, out_dir, mode="live", allow_spend=False):
        import time
        import_paths()
        t = time.time()
        try:
            A = self.algorithm(np.asarray(presented.data, dtype=float), presented)
        except Exception as e:  # noqa: BLE001  a method failure is a run status, never an exception to the caller
            return RunRecord(self.name, presented.file_label, "live", FAILED, failure={"type": type(e).__name__, "message": str(e)[:300]},
                             cost={"usd": 0.0, "seconds": time.time() - t})
        return RunRecord(self.name, presented.file_label, "live", "ok", graph=marks_graph(A), cost={"usd": 0.0, "seconds": time.time() - t})
