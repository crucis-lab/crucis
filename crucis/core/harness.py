"""What the harness owns (protocol v1, section 2.1, point 6): the view a system is shown, and the mapping back.

The AB-05 rule: the columns are ALWAYS shuffled before a system sees them, with
    perm = numpy.random.default_rng(shuffle_seed + crc32(file name)).permutation(d)     (harness/probe_io.shuffle_perm)
so shown position k is original column perm[k]. The system sees names and data in shown order, never the true order, the
reference graph, or metadata beyond the context text. Its graph comes back over shown positions and is mapped to original
columns here, once, for every system.
"""
import zlib
from dataclasses import replace

import numpy as np

from .adapter import Presented
from .paths import ROOT, import_paths

import_paths()
from crucis._support import probe_io as PIO  # noqa: E402

SHUFFLE_SEED = 20261010          # the AB-05 / AB-06 / BND-06 seed


def perm_for(file_name, d, shuffle_seed=SHUFFLE_SEED):
    return PIO.shuffle_perm(file_name, d, shuffle_seed)


def present(item, arm="real", shuffle_seed=SHUFFLE_SEED, names_map=None, context=None, file_label=None, shuffle=True):
    """Presented view of a CausalArena item (npz) and the perm that maps it back."""
    s = PIO.load(str(ROOT / item.file("obs_only")))
    X = s["values"][: s["n_obs"]] if s["n_int"] else s["values"]
    d = X.shape[1]
    perm = perm_for(item.item_id, d, shuffle_seed) if shuffle else list(range(d))
    names0 = list(s["node_ids"])
    if names_map is not None:
        names0 = [str(names_map.get(n, n)) for n in names0]
    if len(set(names0)) != d:
        raise ValueError("variable names are not unique after the names map")
    names = [names0[perm[k]] for k in range(d)]
    ctx = PIO.domain_context(s["meta"]) if context is None else context
    return Presented(data=X[:, perm], names=names, context=ctx, file_label=file_label or "item_%08x" % zlib.crc32(item.item_id.encode()),
                     seed=PIO.score_seed(item.item_id)), perm


def map_back(rec, perm):
    """RunRecord over shown positions -> over original columns (graph, variants, per-arrow sources, stages)."""
    f = lambda e: (int(perm[e[0]]), int(perm[e[1]]))  # noqa: E731
    return replace(rec, graph=rec.graph.mapped(perm) if rec.graph is not None else None,
                   variants={k: g.mapped(perm) for k, g in rec.variants.items()},
                   edge_source={f(e): v for e, v in rec.edge_source.items()},
                   stages=[(n, g.mapped(perm)) for n, g in rec.stages] if rec.stages else rec.stages)


def inverse(perm):
    inv = np.empty(len(perm), dtype=int)
    inv[np.asarray(perm)] = np.arange(len(perm))
    return [int(x) for x in inv]
