"""Shared base for the four LLM agents run by harness/agent_probe.py (AB-05 / AB-06).

recorded  reads the run folder a plan names (plans/ab06/<agent>__<scenario>__<arm>.json -> run.out): result.json
          (graph over ORIGINAL indices, per-arrow source, variants) and summary.json (status, cost)
replay    the probe runner resumes into a copy of a recorded folder and answers every identical request from calls.jsonl;
          caps calls = recorded calls and usd = 0, so any request that differs stops at the cap instead of spending
live      the probe runner itself; refused here without allow_spend (Uzair's go, caps from the plan)
"""
import json
from pathlib import Path

from ..core.adapter import Adapter
from ..core.canon import sha256_file
from ..core.graph import Graph
from ..core.paths import HARNESS, ROOT, rel, research_path
from ..core.runs import NOT_RUN, RunRecord

PLANS = ROOT / "plans" / "ab06"
_STATUS = {"ok": "ok", "failed": "failed", "aborted_cap": "aborted_cap", "aborted_quota": "aborted_quota",
           "interrupted": "interrupted"}


class ProbeAgent(Adapter):
    plan_dir = PLANS

    def plan(self, item, arm):
        p = self.plan_dir / ("%s__%s__%s.json" % (self.name, item.cluster, arm))
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None

    def identity(self):
        reg = json.loads((HARNESS / "agents" / "registry.json").read_text())[self.name]
        out = super().identity()
        out.update({"system_repo": reg["url"], "system_commit_pinned": reg["commit"], "licence": reg["licence"],
                    "runner_sha256": {p: sha256_file(HARNESS / p) for p in
                                      ("agent_probe.py", "probe_llm.py", "probe_io.py", "agents/%s.py" % self.name)}})
        return out

    def recorded(self, item, arm, out=None, **_):
        pl = self.plan(item, arm)
        out = Path(out) if out else (research_path(pl["run"]["out"]) if pl else None)
        sp, rp = (out / "summary.json", out / "result.json") if out else (None, None)
        if not sp or not sp.exists():
            return RunRecord(self.name, item.item_id, arm, NOT_RUN, notes={"plan": rel(self.plan_dir) if pl else None})
        s = json.loads(sp.read_text(encoding="utf-8"))
        r = json.loads(rp.read_text(encoding="utf-8")) if rp.exists() else None
        files = {"summary": {"path": rel(sp), "sha256": sha256_file(sp)}}
        if r is not None:
            files["result"] = {"path": rel(rp), "sha256": sha256_file(rp)}
        status = _STATUS[s["status"]]
        cost = {"usd": s.get("est_usd_at_served_prices"), "calls": s.get("calls"), "seconds": s.get("wall_seconds"),
                "new_api_calls": s.get("new_api_calls"), "models": s.get("served_models")}
        if status != "ok" or r is None or "directed" not in r:
            return RunRecord(self.name, item.item_id, arm, status if status != "ok" else "failed", cost=cost,
                             failure=s.get("failure_point"), files=files)
        n = item.n
        src = {(int(e["from_idx"]), int(e["to_idx"])): e.get("source", "unrecorded") for e in r["directed"]}
        variants = {k: Graph.from_edges(n, v.get("directed") or [], v.get("undecided") or [])
                    for k, v in (r.get("variants") or {}).items() if isinstance(v, dict) and "directed" in v}
        return RunRecord(self.name, item.item_id, arm, "ok", graph=Graph.from_probe(n, r), variants=variants, edge_source=src,
                         cost=cost, files=files, notes={"runner_f1": s.get("directed_f1_random_rule"),
                                                        "scenario_file": r.get("scenario"), "shown_order": r.get("perm")})

    def command(self, item, arm, out, mode):
        """The probe runner command for the run sheet (replay or live); never executed by this package."""
        pl = self.plan(item, arm)
        argv = ["{python}", "/research/harness/agent_probe.py", "--plan", "/research/" + rel(self.plan_dir / (
            "%s__%s__%s.json" % (self.name, item.cluster, arm)))]
        if mode == "replay":
            argv += ["--max-calls", "{recorded_calls}", "--max-usd", "0"]
        return {"argv": argv, "out": out, "mode": mode, "plan_caps": pl["run"] and {k: pl["run"][k] for k in ("max_calls", "max_usd")}}
