"""Bundle B5: the existing audits rerun through the package. Each check reads RAW outputs (result.json, summary.json,
state snapshots, method rows, recorded artifacts) through an adapter, scores them with audit.metrics, and compares with the
stored number by file and JSON pointer. It never reads the stored aggregate it is compared with (failure mode 15).

  python -m crucis_causal rerun [--out DIR] [--bundle B1,B2,B3]

  B1  L0: AB-06 (4 agents x 3 arms), AB-01 (PC, GES, GIES: S c q a F1, released and shuffled, paired files),
          AB-04 (DV-1 coverage and precision), BLD-06 L0 (Causal-Copilot main and refinement v2)
  B2  L1: AB-06 name reliance and P9, data-only floor and P10; AB-01 layout differences; BLD-06 paired branch - main
  B3  L2: BND-08 stages (S0, S1, S3 per run), crashes and their stage, M1, M3 (N1); AB-06 Causal-Copilot rows (gpt-4o and
          gpt-4o-mini) from S3; BLD-06 S0 -> final link loss
"""
import statistics as st

from ..collect import collect, l0_table, score_all
from ..core import adapter as A
from ..core import battery as B
from ..core.evidence import pointer as P
from ..metrics.l0 import pooled_dv1
from .table import Table

AB06 = "analysis/results/ab06/ab06.json"
AB01 = "analysis/results/rescore_v2/rescore_v2.json"
AB04 = "analysis/results/decision_value_v2/decision_value_v2.json"
BLD06 = "analysis/results/fork/bld06_live_compare.json"
NAME_ARMS = ("real", "neutral", "swapped")
AGENTS = ("causaliq", "matmcd", "pywhyllm", "vashishtha")
METHODS = {"pc": ("PC (upstream, maxP)", "PC, upstream maxP"), "ges": ("GES (BIC)", "GES (BIC)"),
           "gies": ("GIES with targets (D+I)", "GIES with targets (D+I)")}


class Cache:
    """One collection per (system, battery), shared by every check."""
    def __init__(self):
        self.c = {}

    def get(self, system, battery_id, arms, **kw):
        key = (system, battery_id, tuple(sorted(kw.items())))
        if key not in self.c:
            ad = A.get(system, **kw)
            b = B.get(battery_id)
            recs = collect(ad, b, arms)
            self.c[key] = (ad, b, recs, score_all(recs, b))
        return self.c[key]


# --------------------------------------------------------------------------------------------------------------- B1
def b1(t, cache):
    for ag in AGENTS:
        ad, b, recs, sc = cache.get(ag, "ca-ab06", NAME_ARMS)
        tab = l0_table(recs, sc, NAME_ARMS)
        for arm in NAME_ARMS:
            T = tab[arm]
            base = ("agents", ag, arm)
            t.add("B1", "AB-06", ag, arm, "runs", T["runs"], AB06, P(*base, "runs"), exact=True)
            t.add("B1", "AB-06", ag, arm, "ok runs", T["ok"], AB06, P(*base, "ok"), exact=True)
            t.add("B1", "AB-06", ag, arm, "dir_f1@expect mean (completed)", T["dir_f1@expect"], AB06, P(*base, "f1_mean"))
            dv = T.get("dv1") or {}
            t.add("B1", "AB-06", ag, arm, "DV-1 precision", dv.get("precision"), AB06, P(*base, "dv1_precision"))
            t.add("B1", "AB-06", ag, arm, "DV-1 coverage", dv.get("coverage"), AB06, P(*base, "dv1_coverage"))
            t.add("B1", "AB-06", ag, arm, "USD (sum)", round(T["usd"], 3), AB06, P(*base, "usd"))
    for sysn, (l1, l4) in METHODS.items():
        for fam in ("semantic", "formula"):
            ad, b, recs, sc = cache.get(sysn, "ca-%s" % fam, ("released", "shuffled"))
            ok = {arm: {r.item for r in recs if r.arm == arm and r.status == "ok"} for arm in ("released", "shuffled")}
            common = ok["released"] & ok["shuffled"]
            t.add("B1", "AB-01", sysn, "both", "files paired (%s)" % fam, len(common), AB01, P("methods", l1, fam, "files_paired"), exact=True)
            for arm in ("released", "shuffled"):
                for k, mk in (("S", "S"), ("c", "c"), ("q", "q"), ("a", "a"), ("F1_random", "dir_f1@expect")):
                    xs = [sc[(f, arm)]["metrics"][mk] for f in common if sc[(f, arm)]["metrics"][mk] is not None]
                    t.add("B1", "AB-01", sysn, arm, "%s (%s)" % (k, fam), st.mean(xs), AB01, P("methods", l1, fam, arm, k))
                p = pooled_dv1([sc[(f, arm)]["metrics"] for f in ok[arm]])
                t.add("B1", "AB-04", sysn, arm, "DV-1 files (%s)" % fam, len(ok[arm]), AB04, P("families", fam, l4, arm, "files"), exact=True)
                t.add("B1", "AB-04", sysn, arm, "DV-1 coverage (%s)" % fam, p["coverage"], AB04, P("families", fam, l4, arm, "coverage"))
                t.add("B1", "AB-04", sysn, arm, "DV-1 precision (%s)" % fam, p["precision"], AB04,
                      P("families", fam, l4, arm, "precision_committed"))
    for src, key in (("main", "main"), ("bld06", "branch")):
        ad, b, recs, sc = cache.get("causal_copilot", "q1s2", NAME_ARMS, source=src)
        t.add("B1", "BLD-06", "causal_copilot@" + src, "all", "runs completed", sum(r.status == "ok" for r in recs), BLD06,
              P("completed", key), exact=True)
        t.add("B1", "BLD-06", "causal_copilot@" + src, "all", "USD (sum)", round(sum(r.cost.get("usd") or 0 for r in recs), 4),
              BLD06, P("usd", key))
    for k, v in bld06_means(cache).items():
        sysn, metric = k
        t.add("B1", "BLD-06", "causal_copilot@" + sysn, "all", metric, v, BLD06, P("means", {"main": "main", "bld06": "branch"}[sysn], metric))


def bld06_runs(cache):
    """Per arm code, per version: S0 and final scores (committed rule, T1 by data) and completion."""
    out = {}
    for src in ("main", "bld06"):
        ad, b, recs, sc = cache.get("causal_copilot", "q1s2", NAME_ARMS, source=src)
        for r in recs:
            s = sc.get((r.item, r.arm))
            code = b.item(r.item).m("arm_code:%s" % r.arm)
            row = {"family": r.item, "completed": r.status == "ok"}
            if s:
                v = s["variants"].get("S0")
                if v:
                    row["S0_adj_f1"], row["S0_dir_f1"] = v["adj_f1"], v["dir_f1@committed"]
                if s["metrics"]:
                    row["final_adj_f1"], row["final_dir_f1"] = s["metrics"]["adj_f1"], s["metrics"]["dir_f1@committed"]
            row["delivered_dir_f1"] = row.get("final_dir_f1") or 0.0
            out.setdefault(src, {})[code] = row
    return out


def bld06_means(cache):
    R = bld06_runs(cache)
    arms = sorted(set(R["main"]) & set(R["bld06"]))
    both = [a for a in arms if R["main"][a]["completed"] and R["bld06"][a]["completed"]]
    out = {}
    for src in ("main", "bld06"):
        for k in ("S0_adj_f1", "S0_dir_f1", "final_adj_f1", "final_dir_f1", "delivered_dir_f1"):
            ks = both if k.startswith("final") else arms
            xs = [R[src][a][k] for a in ks if R[src][a].get(k) is not None]
            out[(src, k)] = st.mean(xs)
    return out


# --------------------------------------------------------------------------------------------------------------- B2
def b2(t, cache):
    from ..controls import l1
    for ag in AGENTS:
        ad, b, recs, sc = cache.get(ag, "ca-ab06", NAME_ARMS)
        ne = l1.name_effects(recs, sc, b)
        t.add("B2", "AB-06", ag, "real-swapped", "K04 name reliance: paired mean dF1", ne["K04"]["point"], AB06,
              P("agents", ag, "name_reliance_real_minus_swapped", "mean"))
        t.add("B2", "AB-06", ag, "real-swapped", "K04 paired scenarios", ne["K04"]["units"], AB06,
              P("agents", ag, "name_reliance_real_minus_swapped", "paired_scenarios"), exact=True)
        t.add("B2", "AB-06", ag, "real-neutral", "real - neutral: paired mean dF1", ne["real_minus_neutral"]["point"], AB06,
              P("agents", ag, "real_minus_neutral", "mean"))
        var = ad.capabilities.variants.get("data_only")
        if var:
            e = l1.data_only_effect(recs, sc, b, var)
            base = ("agents", ag, "data_only_floor_real_arm")
            t.add("B2", "AB-06", ag, "real", "K07 items with a data-only graph", e["units"], AB06, P(*base, "scenarios"), exact=True)
            for k in ("dv1_precision_final", "dv1_precision_data_only", "f1_final", "f1_data_only"):
                t.add("B2", "AB-06", ag, "real", "K07 " + k, e[k], AB06, P(*base, k))
    have = [ag for ag in AGENTS if A.get(ag).capabilities.variants.get("data_only")]
    below = []
    for ag in have:
        ad, b, recs, sc = cache.get(ag, "ca-ab06", NAME_ARMS)
        e = l1.data_only_effect(recs, sc, b, ad.capabilities.variants["data_only"])
        if e["dv1_precision_final"] < e["dv1_precision_data_only"]:
            below.append(ag)
    t.add("B2", "AB-06", "round", "real", "P10 agents with a data-only mode", have, AB06, P("P10", "agents_with_data_only_mode"))
    t.add("B2", "AB-06", "round", "real", "P10 below own data-only", below, AB06, P("P10", "below_own_data_only"))
    t.add("B2", "AB-06", "round", "real", "P10 verdict", "supported" if below else "refuted", AB06, P("P10", "verdict"))
    for sysn, (l1n, _) in METHODS.items():
        for fam in ("semantic", "formula"):
            ad, b, recs, sc = cache.get(sysn, "ca-%s" % fam, ("released", "shuffled"))
            for k, mk in (("F1_random", "dir_f1@expect"), ("S", "S"), ("a", "a")):
                e = l1.layout_effect(recs, sc, b, mk)
                t.add_derived("B2", "AB-01", sysn, "released-shuffled", "K06 layout: paired mean d%s (%s)" % (k, fam), e["point"],
                              [(AB01, P("methods", l1n, fam, "released", k)), (AB01, P("methods", l1n, fam, "shuffled", k))],
                              lambda x, y: x - y, note="stored means are rounded to 4 decimals")
    R = bld06_runs(cache)
    from ..controls import effects as EF
    arms = sorted(set(R["main"]) & set(R["bld06"]))
    both = [a for a in arms if R["main"][a]["completed"] and R["bld06"][a]["completed"]]
    fam = lambda a: R["main"][a]["family"]  # noqa: E731
    for name, key, ks in (("L1", "delivered_dir_f1", arms), ("L2", "final_adj_f1", both), ("L2_dir", "final_dir_f1", both),
                          ("L3", "S0_adj_f1", arms)):
        e = EF.paired({a: R["bld06"][a][key] for a in ks if R["bld06"][a].get(key) is not None},
                      {a: R["main"][a][key] for a in ks if R["main"][a].get(key) is not None}, fam)
        for part in ("point", "lo", "hi"):
            t.add("B2", "BLD-06", "causal_copilot@bld06 - @main", "paired", "%s %s (%s)" % (name, part, key), e[part], BLD06,
                  P("paired_branch_minus_main", name, part))


# --------------------------------------------------------------------------------------------------------------- B3
PS = {"bnd08": "analysis/results/stability_s2/partial_stages.json", "ab06cc": "analysis/results/ab06_cc/partial_stages.json"}
BND08 = "analysis/results/stability_s2/bnd08_summary.json"
CC_AB06 = {"bnd08": "causal_copilot_gpt4o", "ab06cc": "causal_copilot_gpt4omini"}


def _label_ref(item, role):
    """The by-label reference partial_stages.py scored with: the T4 label graph for swapped names; for real names the
    mapping names the by-data file (the same graph); neutral names have none."""
    if role == "neutral":
        return None
    return item.ref(role, "T4") or item.ref(role, "T1")


def cc_stage_rows(cache, src):
    """Per run of one Causal-Copilot source: the partial_stages.py row, rebuilt from artifacts by trace/cc_stages.py."""
    import numpy as np
    from ..core.paths import ROOT
    from ..metrics import l0
    ad, b, recs, sc = cache.get("causal_copilot", "q1s2", NAME_ARMS, source=src)
    from ..core.runs import all_runs
    rows = {}
    for r in all_runs(recs):
        if r.status == "not_run":
            continue
        item = b.item(r.item)
        row = {"completed": r.status == "ok", "reached": r.notes.get("reached"), "family": r.item, "role": r.arm, "status": r.status}
        if r.notes.get("reached") in ("S3", "S4"):
            row["reached"] = "S4" if row["completed"] else "S3"
            row["cycle_in_S3"] = r.notes["cycle_in_S3_pipeline_test"]
            row["cycle_in_S3_committed_directions_only"] = r.notes["cycle_in_S3_committed_only"]
            row["crashed_in_cycle_step"] = r.notes["crashed_in_cycle_step"]
            row["llm_set_cells"] = r.notes["llm_set_cells"]
            refs = {"data": item.ref(r.arm, "T1"), "label": _label_ref(item, r.arm)}
            for tag, ref in refs.items():
                if ref is None:
                    continue
                from crucis_causal._support import cc_graph as CG
                E = CG.truth_edges(np.load(ROOT / ref[1]))
                for st_ in ("S0", "S1", "S3"):
                    s_ = l0.score_graph(r.variants[st_], {"n": item.n, "T": E, "seed_name": item.item_id})
                    row["%s_adj_f1_by_%s" % (st_, tag)] = s_["adj_f1"]
                    row["%s_dir_f1_by_%s" % (st_, tag)] = s_["dir_f1@committed"]
        rows[r.notes["run_id"]] = row
    return rows, recs, b, sc


def b3(t, cache):
    from ..controls import effects as EF, l1
    from ..core.evidence import load_json
    from ..trace import stages as STG
    for src, path in PS.items():
        rows, recs, b, sc = cc_stage_rows(cache, src)
        stored_rows = load_json(path)["rows"]
        sysn = "causal_copilot@" + src
        for i, sr in enumerate(stored_rows):
            mine = rows.get(sr["run_id"], {})
            for k, v in sr.items():
                if k in ("run_id", "arm", "family", "role", "failure", "cycle_llm_calls", "cycle_llm_answers"):
                    continue                     # identifiers; the cycle-step model calls need llm_calls.jsonl (not read here)
                exact = not isinstance(v, float)
                t.add("B3", "BND-08 stages" if src == "bnd08" else "RQ-17 stages", sysn, sr["role"], "%s %s" % (sr["arm"], k),
                      mine.get(k), path, P("rows", i, k), exact=exact)
        # crash localisation (K01 with its stage)
        allr = [r for r in rows.values() if "S3_adj_f1_by_data" in r]
        cyc = [r for r in allr if r["cycle_in_S3"]]
        cs = load_json(path)["cycle_step"]
        for k, v in (("runs_cyclic_by_pipeline_test", len(cyc)),
                     ("of_which_cyclic_among_committed_directions", sum(r["cycle_in_S3_committed_directions_only"] for r in cyc)),
                     ("of_which_completed", sum(r["completed"] for r in cyc))):
            t.add("B3", "BND-08 crashes" if src == "bnd08" else "RQ-17 crashes", sysn, "all", "K01 " + k, v, path, P("cycle_step", k), exact=True)
        for role in NAME_ARMS:
            t.add("B3", "BND-08 crashes" if src == "bnd08" else "RQ-17 crashes", sysn, role, "K01 cyclic runs by role",
                  sum(r["role"] == role for r in cyc), path, P("cycle_step", "by_role", role), exact=True)
        # by-role stage table (K10: the review loses links)
        for role in NAME_ARMS:
            rr = [r for r in allr if r["role"] == role]
            comp = [r for r in rr if r["completed"]]
            m3 = lambda xs: round(st.mean(xs), 3) if xs else None  # noqa: E731  (partial_stages.py rounds to 3 decimals)
            vals = {"with_S3": len(rr), "completed": len(comp),
                    "S3_below_S0_adj_all": sum(r["S3_adj_f1_by_data"] < r["S0_adj_f1_by_data"] for r in rr),
                    "S0_adj_all": m3([r["S0_adj_f1_by_data"] for r in rr]), "S3_adj_completed": m3([r["S3_adj_f1_by_data"] for r in comp]),
                    "S3_adj_all": m3([r["S3_adj_f1_by_data"] for r in rr]), "S0_dir_all": m3([r["S0_dir_f1_by_data"] for r in rr]),
                    "S3_dir_completed": m3([r["S3_dir_f1_by_data"] for r in comp]), "S3_dir_all": m3([r["S3_dir_f1_by_data"] for r in rr])}
            for k, v in vals.items():
                t.add("B3", "BND-08 by role" if src == "bnd08" else "RQ-17 by role", sysn, role, "K10 " + k, v, path,
                      P("by_role", role, k), exact=isinstance(v, int))
        # AB-06's Causal-Copilot rows: name reliance on S3 (the graph handed to the cycle step), committed rule, by data
        ne = l1.name_effects(recs, sc, b, metric="dir_f1@committed", source="S3")
        name = CC_AB06[src]
        for arm in NAME_ARMS:
            fam = l1.by_cluster(recs, sc, b, arm, "dir_f1@committed", "S3")
            t.add("B3", "AB-06", sysn, arm, "S3 dir F1 by data, mean over families", st.mean(fam.values()), AB06,
                  P("causal_copilot", name, arm, "f1_mean"))
            t.add("B3", "AB-06", sysn, arm, "families", len(fam), AB06, P("causal_copilot", name, arm, "families"), exact=True)
        t.add("B3", "AB-06", sysn, "real-swapped", "K04 name reliance on S3", ne["K04"]["point"], AB06,
              P("causal_copilot", name, "name_reliance_real_minus_swapped", "mean"))
        t.add("B3", "AB-06", sysn, "real-swapped", "K04 paired families", ne["K04"]["units"], AB06,
              P("causal_copilot", name, "name_reliance_real_minus_swapped", "paired_scenarios"), exact=True)
        t.add("B3", "AB-06", sysn, "real-neutral", "real - neutral on S3", ne["real_minus_neutral"]["point"], AB06,
              P("causal_copilot", name, "real_minus_neutral", "mean"))
    # P9 over the systems that enter (agents + Causal-Copilot gpt-4o; gpt-4o-mini reported, not counted)
    systems = {}
    for ag in AGENTS:
        ad, b, recs, sc = cache.get(ag, "ca-ab06", NAME_ARMS)
        systems[ag] = l1.name_effects(recs, sc, b)["K04"]
    rows, recs, b, sc = cc_stage_rows(cache, "bnd08")
    systems["causal_copilot_gpt4o"] = l1.name_effects(recs, sc, b, metric="dir_f1@committed", source="S3")["K04"]
    entered = sorted(k for k, v in systems.items() if v["units"] >= 5)
    losers = sorted(k for k in entered if systems[k]["point"] >= 0.10)
    t.add("B3", "AB-06", "round", "P9", "systems entered", entered, AB06, P("P9", "systems_entered"))
    t.add("B3", "AB-06", "round", "P9", "systems losing >= 0.10", losers, AB06, P("P9", "losing_ge_0.10"))
    t.add("B3", "AB-06", "round", "P9", "verdict", "supported" if len(losers) >= 3 else ("refuted" if not losers else "inconclusive"),
          AB06, P("P9", "verdict"))
    # M3 (stability N1): in swapped arms, distinct (family, edge) arrows the LLM step set, by which reference has them
    from ..findings import k11_counts
    k = k11_counts(recs, b, ["S0", "S1", "S2", "S3", "S4"], 2)
    lab, dat, nei = range(k["labels_only"]), range(k["data_only"]), range(k["neither"])
    n = len(lab) + len(dat)
    for k, v in (("labels_only", len(lab)), ("data_only", len(dat)), ("neither", len(nei)), ("n", n)):
        t.add("B3", "BND-08 M3", "causal_copilot@bnd08", "swapped", "K11 " + k, v, BND08, P("M3", k), exact=True)
    t.add("B3", "BND-08 M3", "causal_copilot@bnd08", "swapped", "K11 share following labels", len(lab) / n, BND08, P("M3", "share"))
    t.add("B3", "BND-08 M3", "causal_copilot@bnd08", "swapped", "binomial q95 of data-only", EF.binom_q95(n), BND08,
          P("M3", "binomial_q95_data_only"), exact=True)


BUNDLES = {"B1": b1, "B2": b2, "B3": b3}


def run(bundles=("B1",)):
    t, cache = Table(), Cache()
    for bname in bundles:
        BUNDLES[bname](t, cache)
    return t, cache


# --------------------------------------------------------------------------------------------------------------- B5
def round_context(cache):
    """K03 needs a round: USD per executed run of every LLM system on the same battery (the AB-06 round)."""
    usd = {}
    for ag in AGENTS:
        ad, b, recs, sc = cache.get(ag, "ca-ab06", NAME_ARMS)
        ex = [r for r in recs if r.status in ("ok", "failed")]
        if ex:
            usd[ag] = sum(r.cost.get("usd") or 0 for r in ex) / len(ex)
    return {"battery": "ca-ab06", "usd_per_run": usd}


def main(out, bundles=("B1", "B2", "B3"), reports=True):
    import json
    from pathlib import Path
    from .. import run as RN
    from ..report import build
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    t, cache = run(bundles)
    summ = {b: {k: v for k, v in t.summary(b).items() if k != "failed"} for b in bundles}
    summ["all"] = {k: v for k, v in t.summary().items() if k != "failed"}
    rep = {}
    if reports:
        rnd = round_context(cache)
        for name, spec in RN.AUDITS.items():
            spec = dict(spec, round=rnd if spec["battery"] == "ca-ab06" else None)
            res = RN.audit(spec, name, cache)
            d = out / "reports" / name.replace("@", "_")
            rep[name] = build.write(res, d, "python -m crucis_causal verify <this folder>/certificate.json")
            rep[name]["verdicts"] = {f["id"]: f["verdict"] for f in res["findings"]}
    (out / "comparison.json").write_text(json.dumps({"summary": summ, "rows": t.rows, "reports": rep}, indent=1, default=str),
                                         encoding="utf-8")
    (out / "comparison.md").write_text(comparison_md(t, summ, rep), encoding="utf-8")
    print(json.dumps(summ, indent=1, default=str))
    return 0 if summ["all"]["pass"] else 1


def comparison_md(t, summ, rep):
    L = ["# Existing audits rerun through the audit package", "",
         "Every stored number recomputed from raw outputs (result.json, summary.json, state snapshots, method rows, recorded "
         "artifacts) and compared with the stored file at its JSON pointer. Gate: |difference| <= 0.001; counts and verdicts exact.", "",
         "| Bundle | Compared | Passed | Max abs difference |", "|---|---|---|---|"]
    for b, s in summ.items():
        L.append("| %s | %d | %d | %s |" % (b, s["compared"], s["passed"], "%.2g" % s["max_abs_diff"] if s["max_abs_diff"] is not None else "-"))
    L += ["", "## By audit", "", "| Bundle | Audit | Numbers | Max abs difference | All pass |", "|---|---|---|---|---|"]
    groups = {}
    for r in t.rows:
        groups.setdefault((r["bundle"], r["audit"]), []).append(r)
    for (b, a), rs in sorted(groups.items()):
        ds = [r["abs_diff"] for r in rs if isinstance(r["abs_diff"], float)]
        L.append("| %s | %s | %d | %s | %s |" % (b, a, len(rs), "%.2g" % max(ds) if ds else "-", all(r["pass"] for r in rs)))
    if rep:
        L += ["", "## Findings per system (protocol v1; F fires, c clear, i inconclusive, - not checkable, . not run)", "",
              "| Audit | " + " | ".join("K%02d" % i for i in range(1, 16)) + " |", "|---|" + "---|" * 15]
        sym = {"fires": "**F**", "clear": "c", "inconclusive": "i", "not_checkable": "-", "not_run": "."}
        for name, r in rep.items():
            L.append("| %s | %s |" % (name, " | ".join(sym[r["verdicts"]["K%02d" % i]] for i in range(1, 16))))
    return "\n".join(L) + "\n"
