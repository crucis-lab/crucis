"""L1 metamorphic controls (protocol v1): transformed copies of an item. Every transform is pure and seeded, and keeps what
it must keep (tested): name arms leave the data bytes unchanged; a column order is a bijection; a reference moves with its
columns; a subsample is a subset of rows.

Controls and the finding kinds they feed
  names        real / neutral / swapped                              K04 name_reliance, K05 wrong_knowledge_harm
  columns      released / shuffled (seed 20261010)                   K06 layout_reliance
  path         plain (the file's own name) / opaque (crc code)       K06 layout_reliance
  sample size  first-n rows or a seeded subsample                    K08 robustness_drop
  noise        seeded Gaussian, sd relative to each column's sd      K08
  knowledge    none / oracle order / wrong order (a share reversed)  K09 knowledge_ignored, K07 (knowledge off)
The AB-06 name arms are RECORDED (plans/ab06/names/<scenario>__<arm>.json, made by plans/make_ab06_plans.py from the A3
labels); new items get generated arms (neutral_names, derangement) with the same rules.
"""
import json
import zlib

import numpy as np

from ..core.paths import ROOT

NAMES_DIR = ROOT / "plans" / "ab06" / "names"
SHUFFLE_SEED = 20261010


def _rng(*parts):
    return np.random.default_rng([zlib.crc32(str(p).encode()) for p in parts])


# ------------------------------------------------------------------------------------------------------------- names
def recorded_names_map(scenario_id, arm):
    """{original name: shown name} for an AB-06 arm; None for real names."""
    if arm == "real":
        return None
    p = NAMES_DIR / ("%s__%s.json" % (scenario_id, arm))
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def neutral_names(names, seed):
    """V01..Vd numbered by a seeded random position, so the numbering carries no order."""
    order = _rng("neutral", seed).permutation(len(names))
    w = max(2, len(str(len(names))))
    return {n: "V%0*d" % (w, int(order[k]) + 1) for k, n in enumerate(names)}


def derangement(names, seed):
    """Swapped arm: every variable shows another variable's real name (no fixed point)."""
    rng = _rng("swapped", seed)
    d = len(names)
    while True:
        s = rng.permutation(d)
        if d < 2 or not np.any(s == np.arange(d)):
            return {names[k]: names[int(s[k])] for k in range(d)}


# ------------------------------------------------------------------------------------------------- layout and path
def column_order(file_name, d, arm, seed=SHUFFLE_SEED):
    """released: the file's order; shuffled: the AB-05 permutation (shown k = original perm[k])."""
    if arm == "released":
        return list(range(d))
    from crucis_causal._support import probe_io as PIO
    return PIO.shuffle_perm(file_name, d, seed)


def path_label(file_name, arm):
    """plain: the file's own name (which may name the scenario); opaque: a code that says nothing."""
    if arm == "plain":
        return file_name.rsplit(".", 1)[0]
    return "q%08x" % zlib.crc32(file_name.encode())


def move_reference(T, perm):
    """Reference edges over original columns -> over shown positions."""
    inv = {int(o): k for k, o in enumerate(perm)}
    return {(inv[c], inv[e]) for c, e in T}


# ------------------------------------------------------------------------------------------------------ robustness
def subsample(X, n_rows, seed, mode="random"):
    if n_rows >= X.shape[0]:
        return X
    if mode == "head":
        return X[:n_rows]
    idx = np.sort(_rng("rows", seed).choice(X.shape[0], n_rows, replace=False))
    return X[idx]


def add_noise(X, rel_sd, seed):
    sd = X.std(0, keepdims=True)
    return X + rel_sd * sd * _rng("noise", seed).standard_normal(X.shape)


# ------------------------------------------------------------------------------------------------------- knowledge
def oracle_order(T, d):
    """A topological order of the true graph (oracle supplier): required-before relations only, no edges given."""
    parents = {v: {c for c, e in T if e == v} for v in range(d)}
    order, done = [], set()
    while len(order) < d:
        ready = sorted(v for v in range(d) if v not in done and parents[v] <= done)
        if not ready:
            raise ValueError("reference graph has a cycle")
        order += ready
        done |= set(ready)
    return order


def wrong_supplier(T, share, seed):
    """Knowledge that reverses a seeded share of the true edges (the planted wrong supplier)."""
    E = sorted(T)
    k = int(round(share * len(E)))
    pick = set(map(int, _rng("wrong", seed).choice(len(E), k, replace=False))) if k else set()
    return {(e, c) if i in pick else (c, e) for i, (c, e) in enumerate(E)}


def data_body_sha256(csv_path):
    """sha256 of a CSV's rows without its header: name arms of one item must agree (the numbers are byte-identical)."""
    import hashlib
    lines = open(csv_path, encoding="utf-8").read().splitlines()
    return hashlib.sha256("\n".join(lines[1:]).encode("utf-8")).hexdigest()
