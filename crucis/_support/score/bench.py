"""Benchmark access for the Q2 build: CausalArena files, splits, truth, released intervention targets (D0.4/D0.5).

Splits come from plans/splits.json (fixed 2026-10-09 by scenario hash, before any tuning). A file belongs to a split
when its name contains one of the split's scenario slugs. Released intervention targets follow AB-04 exactly
(analysis/decision_value.targets_and_shifts: a variable is a target when at least 5 rows intervene on it alone).
"""
import json, re, sys
from functools import lru_cache
from pathlib import Path

import numpy as np

from crucis.core.paths import ROOT
from crucis._support import causalarena_io as CA  # noqa: E402
from crucis._support.causalarena_load import load_any  # noqa: E402

from . import graph  # noqa: E402

CA_ROOT = ROOT / "external" / "causalarena"
FAMILIES = ("semantic", "formula")


def splits():
    return json.load(open(ROOT / "plans" / "splits.json", encoding="utf-8"))["families"]


def split_of(family, file_name):
    sp = splits()[family]
    for which in ("dev", "test"):
        if any(slug in file_name for slug in sp[which]):
            return which
    return None


def scenario_of(file_name):
    return re.sub(r"__rep\d+\.npz$", "", file_name.replace("_obs_int__", "_obs_only__"))


def files(family, regime="obs_only", split=None, root=CA_ROOT):
    fs = sorted((Path(root) / "scm" / family / "data" / ("%s_%s" % (family, regime))).glob("*.npz"))
    if split:
        fs = [f for f in fs if split_of(family, f.name) == split]
    return fs


def load(path):
    return load_any(path)


@lru_cache(maxsize=4096)
def truth_info(family, file_name, root=str(CA_ROOT)):
    """Truth and released targets for one observational file name (an obs_int name is mapped to its obs twin)."""
    f = file_name.replace("_obs_int__", "_obs_only__")
    base = Path(root) / "scm" / family / "data"
    s = load_any(base / ("%s_obs_only" % family) / f)
    T = CA.true_edges(s["g"])
    n = len(s["node_ids"])
    intfile = base / ("%s_obs_int" % family) / f.replace("_obs_only__", "_obs_int__")
    targets = sorted(released_targets(str(intfile))) if intfile.exists() else list(range(n))
    cd, cu = graph.cpdag(T, n)
    return {"n": n, "T": frozenset(T), "desc": graph.reach(n, T), "targets": targets, "released_targets": intfile.exists(),
            "cpdag_directed": frozenset(cd), "cpdag_undirected": frozenset(cu), "names": tuple(s["node_ids"])}


@lru_cache(maxsize=4096)
def released_targets(int_path, min_rows=5):
    s = CA.load(int_path)
    I = s["intervened"]
    return tuple(t for t in range(I.shape[1]) if int(np.sum(I[:, t] & (I.sum(1) == 1))) >= min_rows)


def method_rows(name):
    """Per-file rows of an audit-chapter method run (analysis/results/methods/<name>.json); failed rows kept, flagged."""
    d = json.load(open(ROOT / "analysis" / "results" / "methods" / (name + ".json"), encoding="utf-8"))
    return {r["file"]: r for r in d["rows"]}


def row_graph(r):
    return {tuple(e) for e in r["directed_edges"]}, {tuple(u[:2]) for u in r["undecided_pairs"]}
