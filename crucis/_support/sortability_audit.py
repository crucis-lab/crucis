"""Sortability of CausalArena's public files: can the causal order be read off marginal variance or R2?

Varsortability (Reisach, Seiler, Weichwald, NeurIPS 2021) and R2-sortability (Reisach et al., NeurIPS 2023), both in the
path-weighted form of the CausalDisco reference code: over every directed path i ~> j of length 1..d-1 (counted with
multiplicity, A^k), the share where the statistic of the cause is smaller than that of the effect; ties count half.
0.5 = no order information; 1 = the statistic sorts the order perfectly. Edge-only versions (k = 1) are given too.
Values are computed on the observational rows exactly as released (the release stores standardised columns, so
varsortability is expected near 0.5 by construction; R2 is scale-invariant).

  python analysis/sortability_audit.py --root external/causalarena --out analysis/results/sortability
No model calls. Tickets: AUD-29, BEN-07
"""
import argparse, json, os, statistics as st, sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
from crucis._support import causalarena_io as CA  # noqa: E402


def r2_all(X):
    X = X - X.mean(0)
    out = np.zeros(X.shape[1])
    for j in range(X.shape[1]):
        y, Z = X[:, j], np.delete(X, j, axis=1)
        beta, *_ = np.linalg.lstsq(Z, y, rcond=None)
        resid = y - Z @ beta
        out[j] = 1 - resid.var() / y.var() if y.var() > 0 else 0.0
    return out


def sortability(stat, E, paths=True, tol=1e-6):
    """E[i, j] = 1 for i -> j. Path-weighted share of cause-before-effect orderings by `stat`."""
    d = E.shape[0]
    less = (stat[:, None] < stat[None, :] - tol).astype(float)
    tie = (np.abs(stat[:, None] - stat[None, :]) <= tol).astype(float)
    Ek = E.astype(float).copy()
    num = den = 0.0
    for _ in range(d - 1 if paths else 1):
        num += (Ek * less).sum() + 0.5 * (Ek * tie).sum()
        den += Ek.sum()
        Ek = Ek @ E
        if not Ek.any():
            break
    return num / den if den else float("nan")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(HERE.parent / "external" / "causalarena"))
    ap.add_argument("--families", nargs="+", default=["semantic", "formula"])
    ap.add_argument("--out", default=str(HERE / "results" / "sortability"))
    a = ap.parse_args()
    out = {"tickets": ["AUD-29", "BEN-07"], "definition": __doc__.split("\n\n")[1].strip(), "families": {}}
    for fam in a.families:
        folder = Path(a.root) / "scm" / fam / "data" / ("%s_obs_only" % fam)
        rows = []
        for f in sorted(os.listdir(folder)):
            s = CA.load(folder / f)
            X = s["values"][: s["n_obs"]]
            E = (np.asarray(s["g"]) != 0).astype(int)
            v, r2 = X.var(0), r2_all(X)
            rows.append({"file": f, "var_paths": sortability(v, E), "var_edges": sortability(v, E, paths=False),
                         "r2_paths": sortability(r2, E), "r2_edges": sortability(r2, E, paths=False),
                         "column_var_spread": float(v.max() - v.min())})
        summ = {k: {"mean": round(st.mean(r[k] for r in rows), 4), "min": round(min(r[k] for r in rows), 4),
                    "max": round(max(r[k] for r in rows), 4)} for k in ("var_paths", "var_edges", "r2_paths", "r2_edges")}
        summ["files"] = len(rows)
        summ["max_column_var_spread"] = round(max(r["column_var_spread"] for r in rows), 6)
        out["families"][fam] = {"summary": summ, "rows": rows}
        print(fam, json.dumps(summ))
    os.makedirs(a.out, exist_ok=True)
    json.dump(out, open(os.path.join(a.out, "sortability.json"), "w"), indent=1)
    json.dump({"producer": "analysis/sortability_audit.py", "score_bearing": False, "tickets": out["tickets"]},
              open(os.path.join(a.out, "CONTRACT.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
