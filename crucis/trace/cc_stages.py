"""Causal-Copilot's stages from a recorded run (runs/<id>/artifacts/*.pkl, written by harness/cc_trace.py).

  S0  the algorithm's graph, as handed to refinement     quality_judge kwargs full_graph
  S1  after the bootstrap edits                           analysis/lineage.step_bootstrap(S0, bootstrap_recommend)
  S2  after the LLM review                                the graph handed to KCI (kci_pruning args[1]); also rebuilt with
                                                          lineage.step_llm(S1, llm_evaluation_new) and checked equal
  S3  after KCI pruning                                   lineage.step_kci(S2, kci_pruning); checked against check_cycle's
                                                          input when the run reached the cycle step
  S4  after the cycle step (completed runs)               check_cycle's return value
The step functions are analysis/lineage.py's independent re-statements of postprocess/judge.py, called, not copied.

Unpickling: artifacts may hold causal-learn objects (BackgroundKnowledge in quality_judge's arguments). A restricted
unpickler loads NumPy arrays and builtins only and replaces any other class with an inert stub, so the stage graphs load
without the Causal-Copilot environment and no pickled code runs.
"""
import glob
import io
import json
import os
import pickle
from pathlib import Path

import numpy as np

from ..core.graph import Graph
from ..core.paths import ROOT, import_paths

import_paths()
from crucis._support import lineage as LIN  # noqa: E402
from crucis._support import partial_stages as PS  # noqa: E402

NEED = ("quality_judge", "bootstrap_recommend", "llm_evaluation_new", "kci_pruning")
SAFE_BUILTINS = {"set", "frozenset", "list", "dict", "tuple", "complex", "slice", "range", "bytearray", "bytes", "int",
                 "float", "str", "bool", "object"}
SAFE_NUMPY = {"_reconstruct", "ndarray", "dtype", "scalar", "_frombuffer"}


class _Stub:
    def __init__(self, *a, **k):
        pass

    def __setstate__(self, state):
        self.__dict__["_state"] = state


class SafeUnpickler(pickle.Unpickler):
    """Allows only named data constructors: listed builtins, NumPy's array/dtype/scalar reconstructors and dtype classes,
    OrderedDict/defaultdict, copyreg._reconstructor and _codecs.encode. Anything else becomes an inert stub class."""
    def find_class(self, module, name):
        ok = ((module == "builtins" and name in SAFE_BUILTINS)
              or (module.split(".")[0] == "numpy" and (name in SAFE_NUMPY or module == "numpy.dtypes"
                                                      or (module == "numpy" and name.endswith(tuple("0123456789_"))))
                  and not name.startswith("load"))
              or (module == "collections" and name in ("OrderedDict", "defaultdict"))
              or (module == "copyreg" and name == "_reconstructor") or (module == "_codecs" and name == "encode"))
        if ok:
            return super().find_class(module, name)
        return type(name, (_Stub,), {"__module__": "stub." + module})


def safe_load(path):
    with open(path, "rb") as fh:
        return SafeUnpickler(io.BytesIO(fh.read())).load()


def load_artifacts(run_dir, names=NEED + ("check_cycle",)):
    arts = {}
    for f in sorted(glob.glob(os.path.join(str(run_dir), "artifacts", "*.pkl"))):
        if not any(f.endswith("_%s.pkl" % n) for n in names):
            continue
        a = safe_load(f)
        arts.setdefault(a["name"], []).append(a)
    return arts


def stages(run_id):
    """-> {"stages": [(name, Graph)], "matrices": {...}, "gates": {...}, "reached": "S4"|"S3"|"no refinement graph"}"""
    run_dir = ROOT / "runs" / run_id
    arts = load_artifacts(run_dir)
    if not all(k in arts for k in NEED) or arts["kci_pruning"][0].get("ret") is None:
        return {"stages": [], "matrices": {}, "gates": {}, "reached": "no refinement graph"}
    S0 = np.asarray(arts["quality_judge"][0]["args_before"]["kwargs"]["full_graph"]).copy()
    S1, _, _ = LIN.step_bootstrap(S0, arts["bootstrap_recommend"][0]["ret"])
    direct, forbid = arts["llm_evaluation_new"][0]["ret"]
    S2 = LIN.step_llm(S1, direct, forbid)
    S2_rec = np.asarray(arts["kci_pruning"][0]["args_before"]["args"][1])
    S3 = LIN.step_kci(S2_rec, arts["kci_pruning"][0]["ret"])
    gates = {"S2_rebuilt_equals_recorded": bool(np.array_equal(S2, S2_rec))}
    mats = {"S0": S0, "S1": S1, "S2": S2_rec, "S3": S3}
    if "check_cycle" in arts:
        gates["S3_rebuilt_equals_cycle_input"] = bool(np.array_equal(S3, np.asarray(arts["check_cycle"][0]["args_before"]["args"][2])))
        ret = arts["check_cycle"][0].get("ret")
        if ret is not None:
            mats["S4"] = np.asarray(ret)
    out = [(k, Graph.from_cc_matrix(M)) for k, M in mats.items()]
    return {"stages": out, "matrices": mats, "gates": gates, "reached": "S4" if "S4" in mats else "S3",
            "cycle_in_S3_pipeline_test": bool(PS.cycle_as_pipeline(S3)),
            "cycle_in_S3_committed_only": bool(PS.cycle_committed(S3)), "llm_set_cells": int(len(direct))}


def run_meta(run_id):
    p = ROOT / "runs" / run_id / "meta.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def crashed_in_cycle_step(meta):
    f = meta.get("failure")
    return bool(f) and "LLM_remove_cycles" in json.dumps(f)
