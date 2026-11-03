"""Paired differences with a scenario-cluster bootstrap (D0.4).

CausalArena releases 5 replicate files per scenario; files of one scenario are not independent. The interval resamples
scenarios with replacement (all files of a drawn scenario come along), B = 2000, percentile 95% interval, fixed seed.
The landmark rule: a requirement is met when the lower end of this interval clears its threshold.
"""
import numpy as np


def cluster_bootstrap(values_by_cluster, B=2000, seed=20261014, stat=None):
    """values_by_cluster: {cluster: [values]} -> mean over all values and its 95% percentile interval.
    stat(list_of_lists) -> float may replace the pooled mean (e.g., pooled precision from (hits, total) pairs)."""
    keys = sorted(values_by_cluster)
    groups = [values_by_cluster[k] for k in keys]
    f = stat or (lambda gs: float(np.mean([v for g in gs for v in g])))
    point = f(groups)
    rng = np.random.default_rng(seed)
    draws = []
    for _ in range(B):
        idx = rng.integers(0, len(groups), len(groups))
        draws.append(f([groups[i] for i in idx]))
    lo, hi = np.percentile(draws, [2.5, 97.5])
    return {"point": point, "lo": float(lo), "hi": float(hi), "clusters": len(groups), "B": B, "seed": seed}


def paired_diff(a_by_file, b_by_file, cluster_of, B=2000, seed=20261014):
    """Mean of a - b over files present in both, clustered by scenario."""
    common = sorted(set(a_by_file) & set(b_by_file))
    by = {}
    for f in common:
        by.setdefault(cluster_of(f), []).append(a_by_file[f] - b_by_file[f])
    out = cluster_bootstrap(by, B=B, seed=seed)
    out["files"] = len(common)
    return out


def pooled_ratio(num_den_by_cluster, B=2000, seed=20261014):
    """Pooled ratio sum(num)/sum(den) with a cluster bootstrap: values are (num, den) tuples."""
    def stat(gs):
        n = sum(x for g in gs for x, _ in g)
        d = sum(y for g in gs for _, y in g)
        return n / d if d else float("nan")
    return cluster_bootstrap(num_den_by_cluster, B=B, seed=seed, stat=stat)
