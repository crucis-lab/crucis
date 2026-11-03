"""Batteries (protocol v1, section 1.6): manifests, hashes and the development batteries the existing audits used.

A battery hash is the sha256 of the manifest's canonical JSON, file hashes included, so a changed byte anywhere changes it.
Every run record and certificate carries the hash of the battery it was scored on.
"""
import glob
import json
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import numpy as np

from .canon import sha256_file, sha256_obj
from .paths import ROOT, import_paths, rel, research_path

import_paths()

VISIBILITY = ("development", "sealed")


@dataclass(frozen=True)
class Item:
    item_id: str
    cluster: str                 # resampling unit for intervals (the scenario)
    family: str
    files: tuple                 # ((role, repo-relative path), ...)
    reference: tuple             # ((arm or "*", kind, repo-relative path, tier), ...)
    n: int
    arms: tuple
    meta: tuple = ()             # ((key, value), ...)

    def file(self, role):
        return dict(self.files)[role]

    def ref(self, arm, tier="T1"):
        for a, kind, path, t in self.reference:
            if a in (arm, "*") and t == tier:
                return kind, path
        return None

    def m(self, key, default=None):
        return dict(self.meta).get(key, default)

    def manifest(self, hash_files=True):
        files = {r: {"path": p, "sha256": sha256_file(ROOT / p) if hash_files else None} for r, p in self.files}
        refs = [{"arm": a, "kind": k, "path": p, "tier": t, "sha256": sha256_file(ROOT / p) if hash_files else None}
                for a, k, p, t in self.reference]
        return {"item_id": self.item_id, "cluster": self.cluster, "family": self.family, "files": files,
                "reference": refs, "n": self.n, "arms": list(self.arms), "meta": dict(self.meta)}


@dataclass
class Battery:
    battery_id: str
    version: str
    visibility: str
    items: list
    generator: dict = None
    about: str = ""
    _hash: str = field(default=None, repr=False)

    def __post_init__(self):
        if self.visibility not in VISIBILITY:
            raise ValueError(self.visibility)
        ids = [i.item_id for i in self.items]
        if len(set(ids)) != len(ids):
            raise ValueError("duplicate item ids in battery %s" % self.battery_id)

    def manifest(self, hash_files=True):
        return {"battery_id": self.battery_id, "version": self.version, "visibility": self.visibility, "about": self.about,
                "generator": self.generator, "items": [i.manifest(hash_files) for i in self.items]}

    def hash(self):
        if self._hash is None:
            self._hash = sha256_obj(self.manifest(True))
        return self._hash

    def item(self, item_id):
        for i in self.items:
            if i.item_id == item_id:
                return i
        raise KeyError(item_id)

    def clusters(self):
        return sorted({i.cluster for i in self.items})


# ----------------------------------------------------------------------------------------------- development batteries
CA = "external/causalarena/scm/%s/data/%s_%s"


def _ab06_plans():
    return sorted(p for p in glob.glob(str(ROOT / "plans" / "ab06" / "*__*__*.json")))


@lru_cache(maxsize=None)
def ca_ab06():
    """The 10 CausalArena semantic scenarios (rep000) of the AB-06 grid, as planned in plans/ab06/."""
    seen = {}
    for p in _ab06_plans():
        pl = json.loads(Path(p).read_text(encoding="utf-8"))
        f = research_path(pl["run"]["scenario"])
        seen.setdefault(pl["scenario_id"], f)
    items = []
    for sid, f in sorted(seen.items()):
        obs = rel(f)
        intf = obs.replace("semantic_obs_only/", "semantic_obs_int/").replace("_obs_only__", "_obs_int__")
        files = (("obs_only", obs),) + ((("obs_int", intf),) if (ROOT / intf).exists() else ())
        n = len(np.load(ROOT / obs, allow_pickle=False)["node_ids"])
        items.append(Item(Path(obs).name, sid, "semantic", files, (("*", "npz:g", obs, "T1"),), n,
                          ("real", "neutral", "swapped")))
    return Battery("ca-ab06", "1", "development", items,
                   about="AB-06 grid: 10 CausalArena semantic scenarios, rep000, obs_only (+ obs_int for released targets)")


@lru_cache(maxsize=None)
def ca_family(family):
    """Every public CausalArena obs_only file of a family (AB-01 / AB-04 scope); the kernel split is item metadata."""
    from crucis_causal._support.score import bench
    items = []
    for f in bench.files(family, "obs_only"):
        obs = rel(f)
        intf = obs.replace("_obs_only/", "_obs_int/").replace("_obs_only__", "_obs_int__")
        files = (("obs_only", obs),) + ((("obs_int", intf),) if (ROOT / intf).exists() else ())
        n = len(np.load(f, allow_pickle=False)["node_ids"])
        items.append(Item(f.name, bench.scenario_of(f.name), family, files, (("*", "npz:g", obs, "T1"),), n,
                          ("released", "shuffled"), (("split", bench.split_of(family, f.name)),)))
    return Battery("ca-%s" % family, "1", "development", items,
                   about="all public CausalArena %s obs_only files; arms: columns as released, columns shuffled" % family)


@lru_cache(maxsize=None)
def q1s2():
    """The Q1 suite: 10 scenarios x real / neutral / swapped names as CSVs with opaque paths (datasets/suite_q1s2)."""
    base = ROOT / "datasets" / "suite_q1s2"
    mp = json.loads((base / "MAPPING.json").read_text(encoding="utf-8"))
    fams = {}
    for arm, spec in mp["arms"].items():
        fams.setdefault(spec["family"], []).append((arm, spec))
    items = []
    for fam, arms in sorted(fams.items()):
        files, refs, roles, meta = [], [], [], {}
        for arm, spec in sorted(arms):
            role = spec["role"]
            roles.append(role)
            files.append((role, rel(research_path(spec["dataset_arg"]))))
            refs.append((role, "npy:cc", rel(base / spec["reference_by_data"]), "T1"))
            if role == "swapped":
                refs.append((role, "npy:cc", rel(base / spec["reference_by_label"]), "T4"))
            meta["arm_code:%s" % role] = arm
            meta["labels:%s" % role] = tuple(spec["column_labels"])
        n = len(arms[0][1]["column_labels"])
        items.append(Item(fam, arms[0][1]["scenario_id"], "s2", tuple(files), tuple(refs), n, tuple(sorted(roles)),
                          tuple(sorted(meta.items()))))
    return Battery("q1s2", "1", "development", items,
                   about="datasets/suite_q1s2 (frozen 10 Oct): 10 CausalArena semantic scenarios x real/neutral/swapped "
                         "names, byte-identical numbers, shuffled columns, opaque paths; T1 by data, T4 label-implied")


BUILDERS = {"ca-ab06": ca_ab06, "ca-semantic": lambda: ca_family("semantic"), "ca-formula": lambda: ca_family("formula"),
            "q1s2": q1s2}


def get(battery_id):
    return BUILDERS[battery_id]()
