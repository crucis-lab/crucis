"""D0.5: the baseline table on the test splits (and dev, for reference), from the audit chapter's stored per-file rows.

  python -m score.baselines --out analysis/results/q2_b0/baselines.json

Rows per family and split: plain PC maxP and GES (BIC) on shuffled columns, GIES with the released targets (D+I,
shuffled), the empty graph ("nothing moves") and the true CPDAG (the identifiable ceiling), each with directed F1
(expectation rule), DV-1 precision and coverage, over the files each method finished. Every later kernel number is
paired with these per file. Baselines are not tuned, so reading them on the test splits is allowed (failure mode Q4).
No model calls. Tickets: BLD-02, EVL-03
"""
import argparse, json, statistics as st, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
from crucis._support.score import bench, dv, graph  # noqa: E402

ROWS = {"PC maxP (plain)": "pc_upstream_maxp_%s_obs_shuf", "GES (BIC)": {"semantic": "gesbic_semantic_obs_shuf", "formula": "gesbic_formula_obs_shuf"},
        "GIES with targets (D+I)": "gies_targets_%s_obsint_shuf"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "analysis" / "results" / "q2_b0" / "baselines.json"))
    a = ap.parse_args()
    out = {"tickets": ["BLD-02", "EVL-03"], "rule": "directed F1 expectation rule (per-file seed); DV-1 pooled over the files each row finished",
           "families": {}}
    for fam in bench.FAMILIES:
        for split in ("dev", "test"):
            rows = {}
            ref_files = None
            for label, name in ROWS.items():
                nm = name[fam] if isinstance(name, dict) else name % fam
                per = {f: r for f, r in bench.method_rows(nm).items() if not r.get("failed") and bench.split_of(fam, f) == split}
                f1, com, cor, pairs = [], 0, 0, 0
                for f, r in per.items():
                    I = bench.truth_info(fam, f)
                    D, U = bench.row_graph(r)
                    f1.append(graph.directed_f1(D, U, I["T"], graph.file_seed(f))["f1"])
                    c = dv.check(dv.claims(I["n"], D, U, I["targets"]), I["desc"])
                    com += len(c)
                    cor += sum(ok for *_, ok in c)
                    pairs += dv.n_pairs(I["n"], I["targets"])
                rows[label] = {"files": len(per), "f1": st.mean(f1) if f1 else None, "dv1_precision": cor / com if com else None,
                               "dv1_coverage": com / pairs if pairs else None}
                if label == "PC maxP (plain)":
                    ref_files = sorted(per)
            allf = [f.name for f in bench.files(fam, "obs_only", split)]
            for label, fn in (("empty graph", lambda I: (set(), set())), ("true CPDAG (ceiling)", lambda I: (I["cpdag_directed"], I["cpdag_undirected"]))):
                f1, com, cor, pairs = [], 0, 0, 0
                for f in allf:
                    I = bench.truth_info(fam, f)
                    D, U = fn(I)
                    f1.append(graph.directed_f1(D, U, I["T"], graph.file_seed(f))["f1"])
                    c = dv.check(dv.claims(I["n"], D, U, I["targets"]), I["desc"])
                    com += len(c)
                    cor += sum(ok for *_, ok in c)
                    pairs += dv.n_pairs(I["n"], I["targets"])
                rows[label] = {"files": len(allf), "f1": st.mean(f1), "dv1_precision": cor / com if com else None, "dv1_coverage": com / pairs}
            out["families"].setdefault(fam, {})[split] = rows
            print(fam, split)
            for k, v in rows.items():
                print("   %-26s files %3d  F1 %s  DV-1 %s at %s" % (k, v["files"], round(v["f1"], 4) if v["f1"] is not None else None,
                                                                     round(v["dv1_precision"], 4) if v["dv1_precision"] else None,
                                                                     round(v["dv1_coverage"], 4) if v["dv1_coverage"] else None))
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    json.dump(out, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
