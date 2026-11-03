"""Effect sizes with intervals for findings (protocol v1, section 1.5). The interval rule is one implementation for every
kind: the scenario-cluster bootstrap of score/paired.py (B = 2000, seed 20261014, percentile 95%)."""
import math

from ..core.paths import import_paths

import_paths()
from crucis._support.score import paired as SP  # noqa: E402


def paired(a_by_unit, b_by_unit, cluster_of=lambda u: u, B=2000, seed=20261014):
    """Mean of a - b over units present in both, interval clustered by cluster_of(unit). None when nothing is paired."""
    common = sorted(set(a_by_unit) & set(b_by_unit))
    if not common:
        return {"point": None, "lo": None, "hi": None, "units": 0, "clusters": 0, "per_unit": {}}
    by = {}
    for u in common:
        by.setdefault(cluster_of(u), []).append(a_by_unit[u] - b_by_unit[u])
    out = SP.cluster_bootstrap(by, B=B, seed=seed)
    return {"point": out["point"], "lo": out["lo"], "hi": out["hi"], "units": len(common), "clusters": out["clusters"],
            "B": B, "seed": seed, "per_unit": {str(u): a_by_unit[u] - b_by_unit[u] for u in common}}


def pooled_ratio_diff(a_by_unit, b_by_unit, cluster_of=lambda u: u, B=2000, seed=20261014):
    """Pooled ratio difference: sum(num_a)/sum(den_a) - sum(num_b)/sum(den_b) over common units, values (num, den),
    interval by resampling clusters (used for DV-1 precision, which pools claims, as P10 did)."""
    import numpy as np
    common = sorted(set(a_by_unit) & set(b_by_unit))
    if not common:
        return {"point": None, "lo": None, "hi": None, "units": 0, "clusters": 0}
    groups = {}
    for u in common:
        groups.setdefault(cluster_of(u), []).append((a_by_unit[u], b_by_unit[u]))
    keys = sorted(groups)

    def stat(gs):
        na = sum(a[0] for g in gs for a, _ in g)
        da = sum(a[1] for g in gs for a, _ in g)
        nb = sum(b[0] for g in gs for _, b in g)
        db = sum(b[1] for g in gs for _, b in g)
        return (na / da if da else float("nan")) - (nb / db if db else float("nan"))
    gs = [groups[k] for k in keys]
    point = stat(gs)
    rng = np.random.default_rng(seed)
    draws = [stat([gs[i] for i in rng.integers(0, len(gs), len(gs))]) for _ in range(B)]
    lo, hi = np.nanpercentile(draws, [2.5, 97.5])
    return {"point": point, "lo": float(lo), "hi": float(hi), "units": len(common), "clusters": len(keys), "B": B, "seed": seed}


def wilson(k, n, z=1.959963984540054):
    if n == 0:
        return {"point": None, "lo": None, "hi": None, "k": k, "n": n}
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return {"point": p, "lo": max(0.0, c - h), "hi": min(1.0, c + h), "k": k, "n": n}


def binom_cdf(k, n, p=0.5):
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(0, k + 1))


def binom_q05(n, p=0.5):
    """Largest k with P(X <= k) <= 0.05 under Binomial(n, p): a data-only count at or below it is improbable by chance."""
    k = -1
    while binom_cdf(k + 1, n, p) <= 0.05:
        k += 1
    return k


def sign_test(pos, neg):
    """One-sided sign test p-value for pos > neg."""
    n = pos + neg
    return 1.0 - binom_cdf(pos - 1, n) if n else None


def binom_q95(n, p=0.5):
    """Smallest k with P(X <= k) >= 0.95 (the BND-08 M3 bound, analysis/s2_analysis.binom_q95, restated)."""
    acc = 0.0
    for k in range(n + 1):
        acc += math.comb(n, k) * p ** k * (1 - p) ** (n - k)
        if acc >= 0.95:
            return k
    return n
