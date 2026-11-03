"""One audit: a system on a battery, every level the system's capabilities allow (protocol v1).

  result = audit(spec)          spec: {system, adapter_kw, battery, arms, extra, runs_date}
The result holds the system and battery identities, the protocol identity, the run manifest (every raw file with its
sha256), L0 per arm, the L1 effects, the L2 stage effects, and the typed findings. report/ renders it and certifies it.
AUDITS names the standard audits the rerun (B5) performs; `python -m crucis_causal audit NAME` runs one.
"""
import platform
import sys

import numpy as np

from . import collect as C, findings as F
from .controls import l1
from .core import adapter as A, battery as B
from .core.canon import sha256_obj
from .protocol import kinds as K, regimes as R

NAME_ARMS = ("real", "neutral", "swapped")
LAYOUT_ARMS = ("released", "shuffled")
CC_STAGES = {"stage_names": ["S0", "S1", "S2", "S3", "S4"], "name_source": "S3", "name_metric": "dir_f1@committed"}

AUDITS = {
    "matmcd": {"system": "matmcd", "battery": "ca-ab06", "arms": NAME_ARMS, "runs_date": "2026-10-14"},
    "vashishtha": {"system": "vashishtha", "battery": "ca-ab06", "arms": NAME_ARMS, "runs_date": "2026-10-14"},
    "pywhyllm": {"system": "pywhyllm", "battery": "ca-ab06", "arms": NAME_ARMS, "runs_date": "2026-10-14"},
    "causaliq": {"system": "causaliq", "battery": "ca-ab06", "arms": NAME_ARMS, "runs_date": "2026-10-14"},
    "causal_copilot@bnd08": {"system": "causal_copilot", "adapter_kw": {"source": "bnd08"}, "battery": "q1s2", "arms": NAME_ARMS,
                             "extra": CC_STAGES, "runs_date": "2026-10-11"},
    "causal_copilot@ab06cc": {"system": "causal_copilot", "adapter_kw": {"source": "ab06cc"}, "battery": "q1s2",
                              "arms": NAME_ARMS, "extra": CC_STAGES, "runs_date": "2026-10-13"},
    "causal_copilot@main": {"system": "causal_copilot", "adapter_kw": {"source": "main"}, "battery": "q1s2", "arms": NAME_ARMS,
                            "extra": CC_STAGES, "runs_date": "2026-10-21"},
    "causal_copilot@bld06": {"system": "causal_copilot", "adapter_kw": {"source": "bld06"}, "battery": "q1s2", "arms": NAME_ARMS,
                             "extra": {"name_metric": "dir_f1@committed"}, "runs_date": "2026-10-21"},
}
for _s in ("pc", "ges", "gies"):
    for _f in ("semantic", "formula"):
        AUDITS["%s@%s" % (_s, _f)] = {"system": _s, "battery": "ca-%s" % _f, "arms": LAYOUT_ARMS, "runs_date": "<=2026-10-29"}

ARM_OFFER = {"real": {"data", "names", "context"}, "neutral": {"data", "context"}, "swapped": {"data", "names", "context"},
             "released": {"data", "interventions"}, "shuffled": {"data", "interventions"}}
K_SOURCE = {"real": "names_real", "swapped": "names_swapped"}


def environment():
    flags = ""
    try:
        flags = " ".join(sorted({f for line in open("/proc/cpuinfo") if line.startswith("flags") for f in line.split()[2:]}
                                & {"avx2", "avx512f", "fma"}))
    except OSError:
        pass
    return {"python": sys.version.split()[0], "numpy": np.__version__, "platform": platform.platform(), "machine": platform.machine(),
            "cpu_flags": flags}


def audit(spec, name=None, cache=None):
    kw = spec.get("adapter_kw", {})
    if cache is not None:
        ad, b, recs, sc = cache.get(spec["system"], spec["battery"], spec["arms"], **kw)
    else:
        ad, b = A.get(spec["system"], **kw), B.get(spec["battery"])
        recs = C.collect(ad, b, spec["arms"])
        sc = C.score_all(recs, b)
    arms = tuple(a for a in spec["arms"] if any(r.arm == a for r in recs))
    system_id = getattr(ad, "system_id", ad.name)
    ctx = dict(adapter=ad, battery=b, records=recs, scored=sc, arms=arms, runs_date=spec.get("runs_date"),
               system_id=system_id, round=spec.get("round"), **spec.get("extra", {}))
    extra = spec.get("extra", {})
    l1_out = {}
    if {"real", "swapped"} <= set(arms):
        ne = l1.name_effects(recs, sc, b, extra.get("name_metric", "dir_f1@expect"), extra.get("name_source", "final"))
        l1_out["names"] = {k: _slim(v) for k, v in ne.items()}
    if set(LAYOUT_ARMS) <= set(arms):
        l1_out["layout"] = {m: _slim(l1.layout_effect(recs, sc, b, m)) for m in ("dir_f1@expect", "S", "a")}
    var = ad.capabilities.variants.get("data_only")
    if var and "real" in arms:
        l1_out["data_only"] = _slim(l1.data_only_effect(recs, sc, b, var))
    stages = extra.get("stage_names") or ([var, "final"] if var else None)
    l2 = None
    if stages:
        l2 = {"stages": stages, "transitions": {a: [{"stage": t["stage"], "adj": _slim(t["adj"]), "flips": t["flips"]}
                                                    for t in F.stage_effects([r for r in recs if r.arm == a], sc, b, stages)]
                                                for a in arms}}
    table = C.l0_table(recs, sc, arms)
    regimes = {a: {"regime": R.regime(ad.capabilities.takes, ARM_OFFER.get(a, {"data"})),
                   "k_source": K_SOURCE.get(a, "none") if "names" in ad.capabilities.takes else "none"} for a in arms}
    manifest = []
    from .core.runs import all_runs
    for r in all_runs(recs):
        manifest.append({"item": r.item, "arm": r.arm, "status": r.status, "files": r.files, "cost": r.cost,
                         "graph_sha256": sha256_obj(r.graph.canonical()) if r.graph is not None else None,
                         "run_id": r.notes.get("run_id")})
    return {"audit": name or system_id, "spec": _jsonable_spec(spec), "protocol": K.protocol_identity(),
            "system": {"id": system_id, "identity": ad.identity(), "capabilities": ad.capabilities.to_json()},
            "battery": {"id": b.battery_id, "version": b.version, "visibility": b.visibility, "hash": b.hash(),
                        "items": len(b.items), "clusters": len(b.clusters()), "about": b.about},
            "regimes": regimes, "runs": manifest, "runs_manifest_sha256": sha256_obj(manifest),
            "l0": table, "l1": l1_out, "l2": l2, "findings": F.evaluate(ctx), "environment": environment()}


def _slim(e):
    return {k: v for k, v in e.items() if k != "per_unit"} if isinstance(e, dict) else e


def _jsonable_spec(spec):
    return {k: (list(v) if isinstance(v, tuple) else v) for k, v in spec.items()}


def spec_from_json(d):
    """The spec a certificate stores -> the spec audit() takes (tuples back), round context included."""
    out = dict(d)
    out["arms"] = tuple(d["arms"])
    return out
