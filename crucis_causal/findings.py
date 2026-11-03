"""Typed findings (protocol v1, section 1.5): effects -> verdicts under protocol/thresholds_v1.json.

evaluate(ctx) takes one system's collected audit (records, scores, battery, adapter, optional round context) and returns
one finding per kind in the closed list, each with a typed verdict:
  fires | clear | inconclusive (too few units, or the interval straddles where the rule uses it) |
  not_checkable (the system lacks the capability; the reason is stated) | not_run (control defined, not executed here)
Labels: 'confirmatory' when the kind's threshold was registered before the runs it judges, otherwise 'exploratory
(threshold set after the data)'.
"""
from .controls import effects as E, l1
from .core.paths import import_paths
from .core.runs import OK, all_runs
from .protocol import kinds as K

import_paths()
from crucis_causal._support.score import dv  # noqa: E402


def _f(kind_id, verdict, effect=None, reason=None, runs_date=None, **extra):
    k = K.BY_ID[kind_id]
    th = K.thresholds()[kind_id]
    out = {"id": kind_id, "kind": k["kind"], "level": k["level"], "control": k["control"], "statistic": k["statistic"],
           "threshold": th, "verdict": verdict, "label": K.label(kind_id, runs_date), "effect": _slim(effect), "reason": reason}
    out.update(extra)
    assert verdict in K.VERDICTS
    return out


def _slim(e):
    if not isinstance(e, dict):
        return e
    return {k: v for k, v in e.items() if k != "per_unit"}


def _interval_rule(e, min_units, fires, clear_only_if=None):
    if e is None or e.get("point") is None or e.get("units", 0) < min_units:
        return "inconclusive"
    return "fires" if fires(e) else "clear"


def evaluate(ctx):
    """ctx: {adapter, battery, records, scored, arms, runs_date, stage_names (optional), round (optional)}"""
    ad, b, recs, sc = ctx["adapter"], ctx["battery"], ctx["records"], ctx["scored"]
    arms, date = ctx["arms"], ctx.get("runs_date")
    caps = ad.capabilities
    th = K.thresholds()
    out = []

    # K01 crash
    ce = l1.crash_effect(recs)
    out.append(_f("K01", "not_run" if ce["n"] == 0 else ("fires" if ce["k"] >= 1 else "clear"), ce, runs_date=date))

    # K02 no better than the empty graph (DV-1, needs released intervention targets)
    sysd, empd = {}, {}
    from .metrics import l0
    head_arm = "real" if "real" in arms else None        # judged on the system's own setting, like K15
    for r in recs:
        if (head_arm and r.arm != head_arm) or r.status != OK or (r.item, r.arm) not in sc \
                or "dv1_committed" not in sc[(r.item, r.arm)]["metrics"]:
            continue
        m = sc[(r.item, r.arm)]["metrics"]
        tr = l0.truth(b.item(r.item), r.arm)
        chk = dv.check(dv.claims(tr["n"], set(), set(), tr["targets"]), tr["desc"])
        key = (r.item, r.arm)
        sysd[key], empd[key] = (m["dv1_ok"], m["dv1_committed"]), (sum(ok for *_, ok in chk), len(chk))
    if sysd:
        e = E.pooled_ratio_diff(sysd, empd, lambda u: b.item(u[0]).cluster)
        v = _interval_rule(e, 0, lambda e: e["lo"] <= 0) if e["clusters"] >= th["K02"]["min_clusters"] else "inconclusive"
        out.append(_f("K02", v, dict(e, arm=head_arm or "all arms"), runs_date=date))
    else:
        out.append(_f("K02", "not_checkable", reason="no released intervention targets in this battery", runs_date=date))

    # K03 cost outlier: a round-level comparison
    rnd = ctx.get("round") or {}
    if rnd.get("usd_per_run") and len(rnd["usd_per_run"]) >= th["K03"]["min_systems"]:
        import statistics as st
        mine = rnd["usd_per_run"].get(ctx["system_id"])
        med = st.median(rnd["usd_per_run"].values())
        ratio = mine / med if (mine is not None and med) else None
        out.append(_f("K03", "inconclusive" if ratio is None else ("fires" if ratio >= 10 else "clear"),
                      {"usd_per_run": mine, "round_median": med, "ratio": ratio, "systems": len(rnd["usd_per_run"])}, runs_date=date))
    else:
        out.append(_f("K03", "not_run", reason="needs a round of at least 3 LLM systems on the same battery", runs_date=date))

    # K04 / K05 names
    stage_src = ctx.get("name_source", "final")
    metric = ctx.get("name_metric", "dir_f1@expect")
    if {"real", "swapped"} <= set(arms):
        ne = l1.name_effects(recs, sc, b, metric, stage_src)
        e4 = ne["K04"]
        out.append(_f("K04", _interval_rule(e4, th["K04"]["min_pairs"], lambda e: e["point"] >= 0.10), e4, runs_date=date,
                      measured_on=stage_src))
        if "data" not in caps.takes:
            out.append(_f("K05", "not_checkable", reason="names-only system: neutral names offer it nothing (regime none)",
                          runs_date=date))
        else:
            e5 = ne["K05"]
            out.append(_f("K05", _interval_rule(e5, th["K05"]["min_pairs"], lambda e: e["point"] >= 0.05 and e["lo"] > 0), e5,
                          runs_date=date, measured_on=stage_src))
    else:
        out += [_f("K04", "not_run", reason="battery has no names arms", runs_date=date),
                _f("K05", "not_run", reason="battery has no names arms", runs_date=date)]

    # K06 layout
    if {"released", "shuffled"} <= set(arms):
        e6 = l1.layout_effect(recs, sc, b)
        v = _interval_rule(e6, 0, lambda e: abs(e["point"]) >= 0.05 and (e["lo"] > 0 or e["hi"] < 0))
        out.append(_f("K06", v if e6["clusters"] >= th["K06"]["min_clusters"] else "inconclusive", e6, runs_date=date))
    else:
        out.append(_f("K06", "not_run", reason="battery has no layout arms (columns were always shuffled)", runs_date=date))

    # K07 knowledge degrades data
    var = caps.variants.get("data_only")
    if var and "data" in caps.takes and "names" in caps.takes and "real" in arms:
        e7 = l1.data_only_effect(recs, sc, b, var)
        if not e7.get("checkable"):
            out.append(_f("K07", "not_checkable", reason="no ok run exposes the data-only variant with DV-1 targets", runs_date=date))
        else:
            out.append(_f("K07", "inconclusive" if e7["units"] < th["K07"]["min_items"] else ("fires" if e7["point"] < 0 else "clear"),
                          e7, runs_date=date))
    else:
        out.append(_f("K07", "not_checkable", reason="no data-only variant exposed, or not a hybrid of data and names",
                      runs_date=date))

    # K08 / K09 defined, not run in v1
    out.append(_f("K08", "not_run", reason="robustness transforms are defined (controls/transforms.py); not run in v1",
                  runs_date=date))
    out.append(_f("K09", "not_run", reason="oracle and wrong suppliers are defined; not run in v1", runs_date=date))

    # K10 / K12 stages
    stages = ctx.get("stage_names") or ([var, "final"] if var else None)
    head = "real" if "real" in arms else None          # stage kinds are judged on the system's own setting (real names)
    if stages:
        trans = stage_effects([r for r in recs if head is None or r.arm == head], sc, b, stages)
        by_arm = {a: [{"stage": t["stage"], "adj_point": t["adj"]["point"], **t["flips"]} for t in stage_effects(
            [r for r in recs if r.arm == a], sc, b, stages)] for a in arms} if head else None
        worst = min((t for t in trans if t["adj"]["point"] is not None), key=lambda t: t["adj"]["point"], default=None)
        if worst is None:
            out.append(_f("K10", "inconclusive", reason="no stage pair with scores", runs_date=date))
        else:
            v = _interval_rule(worst["adj"], th["K10"]["min_runs"], lambda e: e["point"] <= -0.10 and e["hi"] < 0)
            out.append(_f("K10", v, worst["adj"], runs_date=date, stage=worst["stage"], judged_on=head or "all arms",
                          per_stage=[{"stage": t["stage"], "adj": _slim(t["adj"])} for t in trans], per_arm=by_arm))
        flips = [t for t in trans if t["flips"]["right_to_wrong"] + t["flips"]["wrong_to_right"] > 0]
        best = max(flips, key=lambda t: t["flips"]["right_to_wrong"] - t["flips"]["wrong_to_right"], default=None)
        if best is None:
            out.append(_f("K12", "inconclusive", reason="no direction flips on true adjacencies", runs_date=date))
        else:
            rw, wr = best["flips"]["right_to_wrong"], best["flips"]["wrong_to_right"]
            p = E.sign_test(rw, wr)
            eff = {"right_to_wrong": rw, "wrong_to_right": wr, "net": rw - wr, "sign_p": p, "units": rw + wr}
            v = "inconclusive" if rw + wr < th["K12"]["min_flips"] else ("fires" if rw > wr and p < 0.05 else "clear")
            out.append(_f("K12", v, eff, runs_date=date, stage=best["stage"], judged_on=head or "all arms",
                          per_stage=[{"stage": t["stage"], **t["flips"]} for t in trans], per_arm=by_arm))
    else:
        out += [_f("K10", "not_checkable", reason="no stage graphs (black box with no intermediate graph)", runs_date=date),
                _f("K12", "not_checkable", reason="no stage graphs", runs_date=date)]

    # K11 stage follows names
    k11 = ctx.get("k11") or (k11_counts(recs, b, ctx["stage_names"], ctx.get("k11_stage", 2)) if ctx.get("stage_names") else None)
    if k11:
        q = E.binom_q05(k11["n"])
        v = "inconclusive" if k11["n"] < th["K11"]["min_decided"] else ("fires" if k11["data_only"] <= q else "clear")
        out.append(_f("K11", v, dict(k11, binom_q05=q), runs_date=date))
    else:
        out.append(_f("K11", "not_checkable", reason="needs stage traces and a T4 label reference for the swapped arm",
                      runs_date=date))

    # K13 unsourced claims
    if caps.edge_source:
        known = {"data", "llm", "llm_order", "knowledge"}
        tot = uns = 0
        for r in recs:
            if r.status == OK:
                for e in r.graph.committed():
                    tot += 1
                    uns += r.edge_source.get(e) not in known
        out.append(_f("K13", "inconclusive" if tot == 0 else ("fires" if uns > 0 else "clear"),
                      {"unsourced": uns, "committed": tot, "share": uns / tot if tot else None, "units": tot}, runs_date=date))
    else:
        out.append(_f("K13", "not_checkable", reason="the system exposes no per-edge source (L2 attribution is K10-K12)",
                      runs_date=date))

    # K14 overconfident
    if caps.confidence and any(r.confidence for r in recs):
        out.append(_f("K14", "not_run", reason="calibration of stated confidences: implemented in a later version", runs_date=date))
    elif caps.confidence:
        out.append(_f("K14", "not_checkable", reason="the system states probabilities, but the recorded runs keep only the "
                                                     "decided graph (the probabilities are in calls.jsonl, not parsed in v1)",
                      runs_date=date))
    else:
        out.append(_f("K14", "not_checkable", reason="the system states no confidence", runs_date=date))

    # K15 never abstains (real arm when there is one: the system's own setting)
    arm = "real" if "real" in arms else arms[0]
    ms = [sc[(r.item, r.arm)]["metrics"] for r in recs if r.arm == arm and r.status == OK and (r.item, r.arm) in sc
          and "dv1_committed" in (sc[(r.item, r.arm)]["metrics"] or {})]
    if len(ms) >= th["K15"]["min_items"]:
        p = l0.pooled_dv1(ms)
        out.append(_f("K15", "fires" if (p["coverage"] >= 0.99 and p["precision"] < 0.90) else "clear",
                      dict(p, arm=arm, units=len(ms)), runs_date=date))
    elif ms:
        out.append(_f("K15", "inconclusive", {"units": len(ms)}, runs_date=date))
    else:
        out.append(_f("K15", "not_checkable", reason="no DV-1 targets in this battery", runs_date=date))
    out.sort(key=lambda f: f["id"])
    assert [f["id"] for f in out] == [k["id"] for k in K.KINDS], "one finding per kind of the closed list"
    return out


def stage_effects(recs, sc, b, stages):
    """Per consecutive stage pair: paired adjacency F1 (out - in) over runs that have both, and direction flips on true
    adjacencies. 'final' is the delivered graph."""
    from .metrics import l0
    from .trace import stages as S
    out = []
    for s_in, s_out in zip(stages[:-1], stages[1:]):
        a, c = {}, {}
        rw = wr = 0
        for r in recs:
            s = sc.get((r.item, r.arm))
            if s is None:
                continue
            m_in = s["metrics"] if s_in == "final" else s["variants"].get(s_in)
            m_out = s["metrics"] if s_out == "final" else s["variants"].get(s_out)
            if not m_in or not m_out:
                continue
            key = (r.item, r.arm)
            a[key], c[key] = m_out["adj_f1"], m_in["adj_f1"]
            g_in = r.graph if s_in == "final" else r.variants[s_in]
            g_out = r.graph if s_out == "final" else r.variants[s_out]
            fl = S.direction_flips(g_in, g_out, l0.truth(b.item(r.item), r.arm)["T"])
            rw += fl["right_to_wrong"]
            wr += fl["wrong_to_right"]
        eff = E.paired({k: v for k, v in a.items() if v is not None}, {k: v for k, v in c.items() if v is not None},
                       lambda u: b.item(u[0]).cluster)
        out.append({"stage": "%s -> %s" % (s_in, s_out), "adj": eff, "flips": {"right_to_wrong": rw, "wrong_to_right": wr}})
    return out


def k11_counts(recs, b, stage_names, k):
    """K11 (BND-08 M3 / stability N1): in swapped arms, final arrows that stage k set (and no later stage changed),
    as distinct (family, 'shown name -> shown name'), by which reference has the pair adjacent: T4 labels or T1 data."""
    import numpy as np
    from .core.paths import ROOT
    from .trace import stages as S
    from crucis_causal._support import cc_graph as CG
    lab, dat, nei, both = set(), set(), set(), set()
    seen = False
    for r in recs:
        if r.arm != "swapped" or r.status != OK or not all(s in r.variants for s in stage_names):
            continue
        item = b.item(r.item)
        if item.ref("swapped", "T4") is None:
            continue
        seen = True
        names = item.m("labels:swapped")
        Td = CG.truth_edges(np.load(ROOT / item.ref("swapped", "T1")[1]))
        Tl = CG.truth_edges(np.load(ROOT / item.ref("swapped", "T4")[1]))
        tr = [(s, r.variants[s]) for s in stage_names]
        for (c, e), kind in S.follows_names(S.set_by_stage(tr, k), Td, Tl).items():
            {"labels only": lab, "data only": dat, "neither": nei, "both": both}[kind].add((item.item_id, "%s->%s" % (names[c], names[e])))
    if not seen:
        return None
    return {"stage": stage_names[k], "labels_only": len(lab), "data_only": len(dat), "neither": len(nei), "both": len(both),
            "n": len(lab) + len(dat), "share_following_labels": len(lab) / (len(lab) + len(dat)) if (lab or dat) else None,
            "units": len(lab) + len(dat)}
