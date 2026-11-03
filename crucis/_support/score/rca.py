"""AC@k for root-cause analysis (D0.4; used by B5). Same definition as AB-12 (analysis/ab12_rca_probe.py):
a case is a hit at k when its true root cause is among the first k ranked candidates. With abstention, AC@k is
reported on the answered cases together with the answer rate (coverage); an abstained case is not a hit and not a miss.
"""


def ac_at_k(cases, k):
    """cases: [{"ranking": [candidates] or None (abstained), "root": true root cause}]."""
    answered = [c for c in cases if c.get("ranking") is not None]
    hits = sum(1 for c in answered if c["root"] in c["ranking"][:k])
    return {"k": k, "cases": len(cases), "answered": len(answered),
            "coverage": len(answered) / len(cases) if cases else None,
            "ac": hits / len(answered) if answered else None,
            "ac_all": hits / len(cases) if cases else None}
