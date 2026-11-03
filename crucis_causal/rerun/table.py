"""The comparison table of the rerun: every stored audit number next to the number the package recomputes from raw
outputs, with its source pointer and the absolute difference. Gate: every difference <= 0.001 (counts: exact)."""
from ..core.evidence import stored

TOL = 0.001


class Table:
    def __init__(self):
        self.rows = []

    def add(self, bundle, audit, system, arm, metric, recomputed, path, ptr, exact=False, note=""):
        try:
            s, src = stored(path, ptr)
        except (KeyError, IndexError, TypeError) as e:
            s, src = None, {"file": path, "pointer": ptr, "error": "missing: %s" % e}
        if isinstance(s, list):                       # stored lists of names are compared as sorted, comma-joined text
            s = ",".join(sorted(map(str, s)))
        if isinstance(recomputed, (list, tuple, set)):
            recomputed = ",".join(sorted(map(str, recomputed)))
        if isinstance(s, bool) or isinstance(recomputed, bool) or isinstance(s, str) or isinstance(recomputed, str):
            ok = s == recomputed
            diff = 0.0 if ok else None
        elif s is None or recomputed is None:
            ok = s is None and recomputed is None
            diff = 0.0 if ok else None
        else:
            diff = abs(float(recomputed) - float(s))
            ok = diff == 0 if exact else diff <= TOL
        self.rows.append({"bundle": bundle, "audit": audit, "system": system, "arm": arm, "metric": metric,
                          "stored": s, "recomputed": recomputed, "abs_diff": diff, "exact": exact, "pass": ok,
                          "source": src, "note": note})
        return ok

    def add_derived(self, bundle, audit, system, arm, metric, recomputed, sources, fn, note=""):
        """A stored number derived from several stored numbers (e.g. released mean - shuffled mean)."""
        vals, srcs = [], []
        for path, ptr in sources:
            v, src = stored(path, ptr)
            vals.append(v)
            srcs.append(src)
        s = fn(*vals)
        diff = abs(float(recomputed) - float(s)) if (s is not None and recomputed is not None) else None
        ok = diff is not None and diff <= TOL
        self.rows.append({"bundle": bundle, "audit": audit, "system": system, "arm": arm, "metric": metric, "stored": s,
                          "recomputed": recomputed, "abs_diff": diff, "exact": False, "pass": ok,
                          "source": {"derived_from": srcs}, "note": note})
        return ok

    def summary(self, bundle=None):
        rs = [r for r in self.rows if bundle is None or r["bundle"] == bundle]
        diffs = [r["abs_diff"] for r in rs if isinstance(r["abs_diff"], float)]
        return {"compared": len(rs), "passed": sum(r["pass"] for r in rs), "failed": [r for r in rs if not r["pass"]],
                "max_abs_diff": max(diffs) if diffs else None, "pass": all(r["pass"] for r in rs) and bool(rs),
                "tolerance": TOL}
