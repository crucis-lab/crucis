"""Calibration and risk-coverage (D0.4; used by B4).

ECE: claims binned by stated probability into `bins` equal-width bins on [0, 1]; ECE = sum over bins of
(bin share) x |mean stated probability - realised hit rate|. Bins with no claims contribute nothing.
Risk-coverage: claims sorted by confidence (descending, ties together); precision of the most confident share at each
coverage step.
Claimed vs realised: for a selective view that keeps claims whose stated probability is >= p*, the claimed precision is
the mean stated probability of the kept claims and the realised precision is their hit rate (B4.2: realised >= claimed
- 0.03).
"""


def reliability(probs, hits, bins=10):
    rows = []
    for b in range(bins):
        lo, hi = b / bins, (b + 1) / bins
        idx = [i for i, p in enumerate(probs) if (lo <= p < hi) or (b == bins - 1 and p == 1.0)]
        if idx:
            rows.append({"bin": [lo, hi], "n": len(idx), "stated": sum(probs[i] for i in idx) / len(idx),
                         "realised": sum(hits[i] for i in idx) / len(idx)})
    return rows


def ece(probs, hits, bins=10):
    n = len(probs)
    if not n:
        return None
    return sum(r["n"] / n * abs(r["stated"] - r["realised"]) for r in reliability(probs, hits, bins))


def risk_coverage(conf, hits, steps=10):
    order = sorted(range(len(conf)), key=lambda i: -conf[i])
    n = len(order)
    out = []
    for k in range(1, steps + 1):
        m = max(1, int(round(k / steps * n)))
        cut = conf[order[m - 1]]
        kept = [i for i in order if conf[i] >= cut]
        out.append({"coverage_target": k / steps, "coverage": len(kept) / n, "precision": sum(hits[i] for i in kept) / len(kept)})
    return out


def claimed_vs_realised(probs, hits, p_star):
    kept = [i for i, p in enumerate(probs) if p >= p_star]
    if not kept:
        return {"p_star": p_star, "kept": 0, "claimed": None, "realised": None}
    return {"p_star": p_star, "kept": len(kept), "share": len(kept) / len(probs),
            "claimed": sum(probs[i] for i in kept) / len(kept), "realised": sum(hits[i] for i in kept) / len(kept)}
