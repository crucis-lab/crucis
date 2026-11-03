"""L1: effects of the metamorphic controls on one system (protocol v1, kinds K04-K09). Each function returns effect dicts
{kind, metric, arms, point, lo, hi, units, clusters, per_unit}; findings.py turns them into verdicts under the thresholds.

Units and clusters: a unit is what is paired (a scenario for name arms, a file for layout); the interval resamples
scenario clusters. Where a system has several runs of one (cluster, arm), their mean is the unit value.
"""
import statistics as st

from ..core.runs import OK
from . import effects as E


def by_cluster(records, scored, battery, arm, metric="dir_f1@expect", source="final"):
    """{cluster: mean metric} over ok runs of one arm. source 'final' or a variant / stage name."""
    acc = {}
    for r in records:
        if r.arm != arm:
            continue
        s = scored.get((r.item, r.arm))
        if not s:
            continue
        m = s["metrics"] if source == "final" else s["variants"].get(source)
        if m is None or (source == "final" and r.status != OK) or m.get(metric) is None:
            continue
        acc.setdefault(battery.item(r.item).cluster, []).append(m[metric])
    return {c: st.mean(v) for c, v in acc.items()}


def name_effects(records, scored, battery, metric="dir_f1@expect", source="final"):
    real, neu, swp = (by_cluster(records, scored, battery, a, metric, source) for a in ("real", "neutral", "swapped"))
    out = {"K04": dict(E.paired(real, swp), kind="name_reliance", metric=metric, arms=("real", "swapped"), source=source),
           "K05": dict(E.paired(neu, swp), kind="wrong_knowledge_harm", metric=metric, arms=("neutral", "swapped"), source=source),
           "real_minus_neutral": dict(E.paired(real, neu), metric=metric, arms=("real", "neutral"), source=source)}
    return out


def data_only_effect(records, scored, battery, data_only_variant, arm="real"):
    """K07: pooled DV-1 precision of the final graph minus that of the system's own data-only variant, on the ok runs
    of the real arm that expose the variant (P10's statistic), with a cluster interval; plus mean F1 of both."""
    fin, dat, f1f, f1d = {}, {}, [], []
    for r in records:
        if r.arm != arm or r.status != OK:
            continue
        s = scored.get((r.item, r.arm))
        v = s and s["variants"].get(data_only_variant)
        if not v or "dv1_committed" not in v:
            continue
        m = s["metrics"]
        fin[r.item], dat[r.item] = (m["dv1_ok"], m["dv1_committed"]), (v["dv1_ok"], v["dv1_committed"])
        f1f.append(m["dir_f1@expect"])
        f1d.append(v["dir_f1@expect"])
    if not fin:
        return {"kind": "knowledge_degrades_data", "point": None, "units": 0, "checkable": False}
    cl = lambda u: battery.item(u).cluster  # noqa: E731
    eff = E.pooled_ratio_diff(fin, dat, cl)
    pf = sum(a for a, _ in fin.values()) / max(1, sum(b for _, b in fin.values()))
    pd = sum(a for a, _ in dat.values()) / max(1, sum(b for _, b in dat.values()))
    return dict(eff, kind="knowledge_degrades_data", metric="dv1_precision", variant=data_only_variant, checkable=True,
                dv1_precision_final=pf, dv1_precision_data_only=pd, f1_final=st.mean(f1f), f1_data_only=st.mean(f1d))


def layout_effect(records, scored, battery, metric="dir_f1@expect", arms=("released", "shuffled")):
    """K06: paired by file over files ok in both arms, clustered by scenario."""
    a = {r.item: scored[(r.item, r.arm)]["metrics"][metric] for r in records
         if r.arm == arms[0] and r.status == OK and scored[(r.item, r.arm)]["metrics"].get(metric) is not None}
    b = {r.item: scored[(r.item, r.arm)]["metrics"][metric] for r in records
         if r.arm == arms[1] and r.status == OK and scored[(r.item, r.arm)]["metrics"].get(metric) is not None}
    return dict(E.paired(a, b, lambda u: battery.item(u).cluster), kind="layout_reliance", metric=metric, arms=arms)


def crash_effect(records):
    """K01 inputs: failed / executed, with Wilson interval; infrastructure statuses counted separately."""
    from ..core.runs import FAILED, INFRA, all_runs
    records = list(all_runs(records))
    ex = [r for r in records if r.status in (OK, FAILED)]
    k = sum(r.status == FAILED for r in ex)
    out = dict(E.wilson(k, len(ex)), kind="crash", infrastructure=sum(r.status in INFRA for r in records))
    def where(f):
        f = f or {}
        frame = f.get("innermost_agent_frame") or f.get("repo_frame") or f.get("where") or f.get("innermost_frame")
        return "%s%s: %s" % (("stage %s at " % f["stage"]) if f.get("stage") else "", frame or "?",
                             ("%s %s" % (f.get("type", ""), f.get("message", ""))).strip()[:120])
    out["where"] = sorted({where(r.failure) for r in records if r.status == FAILED})
    return out
