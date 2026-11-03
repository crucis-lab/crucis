"""Causal-Copilot (Lancelot39/Causal-Copilot at a31aa7c, and our fork's branches), run unmodified through
harness/run_traced.py (the observation-only recorder) inside Docker.

Takes a CSV in a dataset folder (the header is the names), and a query text. Gives a Causal-Copilot matrix (codes 1-7,
PAG marks included). Exposes no per-edge source; the recorder makes it a glass box: S0 the algorithm's graph, S1 after the
bootstrap edits, S2 after the LLM review, S3 after KCI pruning, S4 after the cycle step (trace/cc_stages.py rebuilds them).

Recorded sources (one adapter instance per system version; the version is part of the system's identity):
  bnd08    unmodified a31aa7c, gpt-4o, first image (11 Oct, BND-08)        analysis/results/stability_s2/bnd08_summary.json
  ab06cc   unmodified a31aa7c, gpt-4o-mini, first image (13 Oct, RQ-17)    analysis/results/ab06_cc/partial_stages.json
  main     fork main = a31aa7c, gpt-4o, rebuilt image (21 Oct, BLD-06)     plans/results/fork_bld06_live_main.capped.json
  bld06    fork bld-06-refinement-v2 55a490a, same image and day (BLD-06)  plans/results/fork_bld06_live.capped.json
Live mode is cc.ps1 on Uzair's machine (it spends); this adapter only writes the command.
"""
import glob
import json
from pathlib import Path

from ..core.adapter import Adapter, Capabilities, register
from ..core.canon import sha256_file
from ..core.graph import Graph
from ..core.paths import ROOT, rel
from ..core.runs import FAILED, NOT_RUN, RunRecord, host_error

SOURCES = {
    "bnd08": {"file": "analysis/results/stability_s2/bnd08_summary.json", "kind": "bnd08", "commit": "a31aa7c",
              "model": "gpt-4o-2024-08-06", "image": "first image (11 Oct)"},
    "ab06cc": {"file": "analysis/results/ab06_cc/partial_stages.json", "kind": "partial", "commit": "a31aa7c",
               "model": "gpt-4o-mini", "image": "first image (13 Oct)"},
    "main": {"file": "plans/results/fork_bld06_live_main.capped.json", "kind": "capped", "commit": "a31aa7c (fork main)",
             "model": "gpt-4o", "image": "rebuilt image (21 Oct)"},
    "bld06": {"file": "plans/results/fork_bld06_live.capped.json", "kind": "capped",
              "commit": "55a490a (bld-06-refinement-v2)", "model": "gpt-4o", "image": "rebuilt image (21 Oct)"},
}


def _arr(x):
    import numpy as np
    if isinstance(x, dict) and x.get("__ndarray__"):
        return np.array(x["data"])
    return None if x is None else np.asarray(x)


def last_state(run_id):
    """The state file analysis/bld06_live_compare.py::last_state reads: 99_final, else the last snapshot."""
    fs = sorted(glob.glob(str(ROOT / "runs" / run_id / "state" / "*.json")))
    fin = [f for f in fs if f.endswith("99_final.json")]
    if not fs:
        return None, None, False
    f = Path(fin[-1] if fin else fs[-1])
    return json.loads(f.read_text(encoding="utf-8")), f, bool(fin)


@register
class CausalCopilot(Adapter):
    name, version = "causal_copilot", "1"
    capabilities = Capabilities(takes=frozenset({"data", "names", "context"}),
                                marks=frozenset({"->", "--", "<->", "o->", "o-o", "o-", "~", "mixed"}),
                                variants={"data_only": "S0"},
                                glass_box={"entry": "main:main (harness/run_traced.py, harness/cc_trace.py hooks)",
                                           "stages": ["S0", "S1", "S2", "S3", "S4"]},
                                modes=frozenset({"recorded", "live"}), cost="llm")

    def __init__(self, source="bnd08", with_stages=True):
        self.source = source
        self.with_stages = with_stages
        self.spec = SOURCES[source]

    @property
    def system_id(self):
        return "causal_copilot@%s" % self.source

    def identity(self):
        out = super().identity()
        out.update({"system_repo": "https://github.com/uzairgheewala/Causal-Copilot", "system_commit": self.spec["commit"],
                    "model": self.spec["model"], "image": self.spec["image"], "source": self.source,
                    "source_file": self.spec["file"], "source_sha256": sha256_file(ROOT / self.spec["file"])})
        return out

    def runs(self):
        """arm code (q011 ...) -> [{run_id, usd}] in run order (run ids start with their UTC start time)"""
        d = json.loads((ROOT / self.spec["file"]).read_text(encoding="utf-8"))
        if self.spec["kind"] == "capped":
            rs = [(Path(r["dataset"]).parent.name, {"run_id": r["run_id"], "usd": r.get("usd")}) for r in d["runs"].values()]
        else:
            rs = [(r["arm"], {"run_id": r["run_id"], "usd": None}) for r in (d["runs"] if self.spec["kind"] == "bnd08" else d["rows"])]
        out = {}
        for arm, r in rs:
            out.setdefault(arm, []).append(r)
        return {k: sorted(v, key=lambda r: r["run_id"]) for k, v in out.items()}

    def recorded(self, item, arm, **_):
        """The last run of the arm; earlier runs of it are kept as replicates."""
        code = item.m("arm_code:%s" % arm)
        rs = self.runs().get(code)
        if not rs:
            return RunRecord(self.system_id, item.item_id, arm, NOT_RUN)
        rec = self._one(item, arm, code, rs[-1])
        rec.notes["replicates"] = [self._one(item, arm, code, r) for r in rs[:-1]]
        return rec

    def _one(self, item, arm, code, r):
        st, f, completed = last_state(r["run_id"])
        if st is None:
            return RunRecord(self.system_id, item.item_id, arm, NOT_RUN, notes={"run_id": r["run_id"]})
        meta_p = ROOT / "runs" / r["run_id"] / "meta.json"
        meta = json.loads(meta_p.read_text(encoding="utf-8")) if meta_p.exists() else {}
        res = st.get("results") or {}
        S0 = _arr(res.get("converted_graph"))
        variants = {"S0": Graph.from_cc_matrix(S0)} if S0 is not None else {}
        files = {"state": {"path": rel(f), "sha256": sha256_file(f)}}
        if meta_p.exists():
            files["meta"] = {"path": rel(meta_p), "sha256": sha256_file(meta_p)}
        cost = {"usd": r.get("usd"), "seconds": meta.get("wall_time_s")}
        notes = {"run_id": r["run_id"], "arm_code": code}
        stages = None
        if self.with_stages:                      # L2: S0-S4 rebuilt from the recorded artifacts (trace/cc_stages.py)
            from ..trace import cc_stages
            tr = cc_stages.stages(r["run_id"])
            stages = tr["stages"] or None
            for k, g in tr["stages"]:
                if k == "S0" and "S0" in variants:          # lineage gate A: the artifact's S0 is the state's converted_graph
                    tr["gates"]["S0_artifact_equals_state_converted_graph"] = g == variants["S0"]
                    continue
                variants[k] = g
            notes.update({"reached": tr["reached"], "stage_gates": tr["gates"],
                          "cycle_in_S3_pipeline_test": tr.get("cycle_in_S3_pipeline_test"),
                          "cycle_in_S3_committed_only": tr.get("cycle_in_S3_committed_only"),
                          "llm_set_cells": tr.get("llm_set_cells"),
                          "crashed_in_cycle_step": cc_stages.crashed_in_cycle_step(meta)})
        if not completed:
            status = "host_error" if host_error(meta.get("failure")) else FAILED
            return RunRecord(self.system_id, item.item_id, arm, status, variants=variants, cost=cost, stages=stages,
                             failure=meta.get("failure") or {"where": "no final state"}, files=files, notes=notes)
        fin = _arr(res.get("revised_graph"))
        return RunRecord(self.system_id, item.item_id, arm, "ok", graph=Graph.from_cc_matrix(fin), variants=variants,
                         cost=cost, files=files, notes=notes, stages=stages)

    def command(self, item, arm, mode="live"):
        code = item.m("arm_code:%s" % arm)
        return {"argv": ["pwsh", "cc.ps1", "plan", "<plan with dataset research:datasets/suite_q1s2/%s/%s.csv>" % (code, code)],
                "mode": mode, "note": "live spends: Uzair runs it"}

