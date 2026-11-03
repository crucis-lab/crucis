"""Load any released CausalArena sample file (BND-06): semantic and formula through causalarena_io.load (unchanged), synthetic
through the layout below. causalarena_io.py is the C1-gated scorer module and is deliberately not edited.

Synthetic layout (verified on all 100 public files in scm/synthetic/data/synthetic_obs_only, 2026-10-11):
  x         (n, d) float32   standardised values (column means |.| < 1e-3, stds within 1e-3 of 1); no intervened-cell channel
  raw_x     (n, d) float32   unstandardised values (not used)
  g         (d, d)           g[i, j] == 1 means node_ids[i] -> node_ids[j] (row = cause; equals metadata "edges" in all 100 files)
  mask      (n, d)           all zero in the obs-only files
  metadata_json             scenario id under scenario_spec.scenario_id, graph family under graph_family; no domain_id
Returned dict has the keys causalarena_io.load returns; meta carries scenario_id and domain_id (= graph family for synthetic).
"""
import json

import numpy as np

from crucis._support import causalarena_io as CA


def load_any(path):
    with np.load(path, allow_pickle=False) as z:
        ndim = z["x"].ndim
    if ndim == 3:
        return CA.load(path)
    z = np.load(path, allow_pickle=False)
    x = z["x"].astype(float)
    meta = json.loads(str(z["metadata_json"]))
    spec = meta.get("scenario_spec", {})
    n_obs = int(z["n"]) if "n" in z.files else x.shape[0]
    return {"values": x, "intervened": np.zeros(x.shape, dtype=bool), "g": (z["g"] != 0).astype(int),
            "node_ids": [str(s) for s in z["node_ids"]], "n_obs": n_obs, "n_int": 0,
            "meta": {"scenario_id": spec.get("scenario_id"), "domain_id": meta.get("graph_family"),
                     "replicate": meta.get("replicate"), "layout": "synthetic (n, d)"}}
