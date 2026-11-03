"""Collect and score one system on one battery (the L0 pass every level builds on).

  records = collect(adapter, battery, arms, mode="recorded")
  scored  = score_all(records, battery)          # {(item, arm): score_record}
  table   = l0_table(records, scored, arms)      # per arm: completion, means (both run sets), DV-1, cost
Live and replay modes are not run from here in this package version: they are run-sheet jobs (Uzair's machine).
"""
from .core.runs import OK
from .metrics import l0


def collect(adapter, battery, arms, mode="recorded", refs=None):
    if mode != "recorded":
        raise NotImplementedError("live and replay runs are run-sheet jobs; collect reads recorded runs")
    out = []
    for item in battery.items:
        for arm in arms:
            if arm not in item.arms:
                continue
            out.append(adapter.recorded(item, arm, **((refs or {}).get((item.item_id, arm), {}))))
    return out


def score_all(records, battery, tier="T1"):
    out = {}
    for r in records:
        item = battery.item(r.item)
        if r.status == OK or r.variants:
            s = l0.score_record(r, item, tier) if r.graph is not None else _variants_only(r, item, tier)
            if s:
                out[(r.item, r.arm)] = s
    return out


def _variants_only(r, item, tier):
    """A failed run can still carry the system's earlier graphs (Causal-Copilot's S0); score those, no final graph."""
    tr = l0.truth(item, r.arm, tier)
    if tr is None:
        return {}
    if r.notes.get("file_read"):
        tr = dict(tr, seed_name=r.notes["file_read"])
    return {"tier": tier, "word": l0.TIER_WORD[tier], "metrics": None,
            "variants": {k: l0.score_graph(g, tr) for k, g in r.variants.items()}}


def l0_table(records, scored, arms):
    t = {}
    for arm in arms:
        rs = [r for r in records if r.arm == arm]
        if not rs:
            continue
        sc = {r.item: scored[(r.item, arm)] for r in rs if (r.item, arm) in scored and scored[(r.item, arm)]["metrics"]}
        t[arm] = l0.summarise_arm(rs, sc)
    return t
