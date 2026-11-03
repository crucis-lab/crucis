"""L0 output scoring (protocol v1, section 1.4). Every metric is computed by the research repository's own scorer; this
module only routes a Graph to it and names the rule in the metric's name.

  dir_f1@expect      score.graph.directed_f1 (undecided pairs oriented at random, seed crc32(file name), sorted pairs);
                     identical to harness/probe_io.score_graph["random"] and analysis/causalarena_io (rule "random")
  S, c, q, a         score.graph.coords (skeleton F1, commit rate, commit accuracy, direction accuracy)
  adj_f1, dir_f1@committed   analysis/cc_graph.score (only committed marks count; a both-ways mark counts both)
  dv1                score.dv (claims "if I set T, does Y move?" on released targets; checked against true descendants)
Tiers (rule R3): numbers on T1 references are accuracy; on T2/T3 agreement; T4 is refused here (controls only).
"""
import zlib

import numpy as np

from ..core.paths import ROOT, import_paths

import_paths()
from crucis_causal._support import cc_graph as CG  # noqa: E402
from crucis_causal._support.score import bench, dv, graph as SG  # noqa: E402

TIER_WORD = {"T1": "accuracy", "T2": "agreement", "T3": "agreement"}


class TierRefused(ValueError):
    pass


def truth(item, arm, tier="T1", allow_mismatched=False):
    """Reference of one item arm: {n, T (cause, effect) set, desc, targets (or None), seed_name, tier}."""
    if tier == "T4" and not allow_mismatched:
        raise TierRefused("a T4 (mismatched) reference is never scored on its own (rule R3)")
    r = item.ref(arm, tier)
    if r is None:
        return None
    kind, path = r
    if kind == "npz:g":
        I = bench.truth_info(item.family, item.item_id)
        return {"n": I["n"], "T": set(I["T"]), "desc": I["desc"], "targets": list(I["targets"]) if I["released_targets"] else None,
                "seed_name": item.item_id, "tier": tier, "path": path}
    if kind == "npy:cc":
        T = CG.truth_edges(np.load(ROOT / path))
        return {"n": item.n, "T": T, "desc": SG.reach(item.n, T), "targets": None, "seed_name": item.item_id, "tier": tier,
                "path": path}
    raise ValueError(kind)


def seed_of(name):
    return zlib.crc32(name.encode())


def score_graph(g, tr):
    """All L0 numbers of one graph against one reference."""
    U = g.undecided()
    f = SG.directed_f1(g.directed, U, tr["T"], seed_of(tr["seed_name"]))
    co = SG.coords(g.directed, U, tr["T"])
    cc = CG.score(g.to_cc_matrix(), set(tr["T"]), tr["n"])
    out = {"dir_f1@expect": f["f1"], "dir_precision@expect": f["precision"], "dir_recall@expect": f["recall"],
           "S": co["S"], "c": co["c"], "q": co["q"], "a": co["a"],
           "adj_f1": cc["adj_f1"], "dir_f1@committed": cc["dir_f1"], "edges_predicted": f["predicted"]}
    if tr.get("targets") is not None:
        chk = dv.check(dv.claims(tr["n"], g.directed, U, tr["targets"]), tr["desc"])
        out["dv1_ok"] = sum(1 for *_, ok in chk if ok)
        out["dv1_committed"] = len(chk)
        out["dv1_pairs"] = dv.n_pairs(tr["n"], tr["targets"])
    return out


def score_record(rec, item, tier="T1"):
    """L0 of one run record ({} if the run has no graph). Variants are scored with the same reference."""
    if rec.graph is None:
        return {}
    tr = truth(item, rec.arm, tier)
    if tr is None:
        return {}
    if rec.notes.get("file_read"):           # the expectation rule seeds with the name of the file the system READ
        tr = dict(tr, seed_name=rec.notes["file_read"])   # (GIES reads the obs_int twin of the item's obs_only file)
    out = {"tier": tier, "word": TIER_WORD[tier], "metrics": score_graph(rec.graph, tr), "variants": {}}
    for k, g in rec.variants.items():
        out["variants"][k] = score_graph(g, tr)
    return out


# ---------------------------------------------------------------------------------------------------- aggregation
def mean(xs):
    xs = [x for x in xs if x is not None]
    return float(np.mean(xs)) if xs else None


def pooled_dv1(metric_dicts):
    ok = sum(m.get("dv1_ok", 0) for m in metric_dicts)
    com = sum(m.get("dv1_committed", 0) for m in metric_dicts)
    pairs = sum(m.get("dv1_pairs", 0) for m in metric_dicts)
    return {"precision": ok / com if com else None, "coverage": com / pairs if pairs else None, "committed": com,
            "correct": ok, "pairs": pairs}


def summarise_arm(records, scored):
    """One system x one arm. records: [RunRecord]; scored: {item: score_record(...)} for the ok ones.
    Rule R4: means over completed runs, and 'delivered' means where a failed run counts as an empty graph (score 0)."""
    from ..core.runs import FAILED, INFRA, NOT_RUN, OK
    st = {}
    for r in records:
        st[r.status] = st.get(r.status, 0) + 1
    ok = [r for r in records if r.status == OK]
    ms = [scored[r.item]["metrics"] for r in ok if r.item in scored]
    executed = [r for r in records if r.status in (OK, FAILED)]
    words = {scored[r.item]["word"] for r in ok if r.item in scored}
    if len(words) > 1:
        raise TierRefused("one arm mixes accuracy and agreement references")
    out = {"runs": len(records), "ok": len(ok), "statuses": st, "executed": len(executed),
           "infrastructure": sum(st.get(s, 0) for s in INFRA), "not_run": st.get(NOT_RUN, 0),
           "completion": len(ok) / len(executed) if executed else None, "word": words.pop() if words else None}
    for k in ("dir_f1@expect", "adj_f1", "dir_f1@committed", "S", "c", "q", "a"):
        out[k] = mean([m.get(k) for m in ms])
    dl = [scored[r.item]["metrics"]["dir_f1@expect"] if r.status == OK and r.item in scored else 0.0 for r in executed]
    out["dir_f1@expect_delivered"] = mean(dl)
    if any("dv1_pairs" in m for m in ms):
        out["dv1"] = pooled_dv1(ms)
    out["usd"] = float(sum((r.cost.get("usd") or 0) for r in records))
    srcs = {}
    for r in ok:
        for v in r.edge_source.values():
            srcs[v] = srcs.get(v, 0) + 1
    out["direction_sources"] = dict(sorted(srcs.items()))
    return out
