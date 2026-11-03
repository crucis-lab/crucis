"""Run a causal discovery method on CausalArena released sample files and store graph + scores per file (BND-04, BND-06).

No LLM. Resumable jobkit script: finished files are skipped; the final output is identical however the work was chunked.
Methods (all from the repo's vendored causal-learn 0.1.3.8 unless stated):
  pc    stable PC, Fisher-z, alpha 0.05 (CausalArena's published configuration; the calibration row)
  ges   GES with the Gaussian BIC score (local_score_BIC); on observational data this is what GIES reduces to (slow:
        minutes to hours on dense 25-variable files; superseded for BND-04 by gesbic)
  gesbic GES from the `ges` package 1.1.0 (Gamella; pip install ges==1.1.0), Gaussian l0-penalised likelihood with
        lambda = log(n)/2, phases forward/backward/turning, on z-scored columns: the score and phases of the published GIES
        row (TabCausal baselines/paper_algorithms/run_gies.py: pcalg GIES via cdt, score "int", lambda_gies = log(n)/2,
        no intervention targets on observational files). Same algorithm and score, different implementation (Python, not R).
  fci   FCI, Fisher-z, alpha 0.05; output is a PAG
  lingam DirectLiNGAM (causal-learn, random_state 0), edges where |B| >= 0.5 (TabCausal run_lingam.py: FIXED_THRESHOLD 0.5)
  notears linear NOTEARS (analysis/notears_linear.py; lambda1 0.1, l2 loss, max_iter 100, h_tol 1e-8), edges where |W| >= 0.5
        (TabCausal run_notears.py + the release threshold)
Every row stores the committed arrows and every undecided pair with its endpoint marks, so any orientation rule can be
re-applied without rerunning. Scores are given under the published rule ("random": undecided pairs oriented with the per-file
seed crc32(file name)), "drop", "both", and "lower" (earlier column -> later column: the "liberal" rule in the
authors' baseline code, run_pc.py / run_gies.py; on released column order this reads the answer, see BEN-07/EXT-01).
For a PAG, a committed arrow is tail -> arrowhead only; o->, o-o and <-> pairs are undecided (rule stated in the contract).
Columns may be shuffled with --shuffle-seed (BEN-07): the method sees a permuted file; the graph is mapped back before scoring.
Files are read with causalarena_load.load_any (= causalarena_io.load for semantic/formula; the 2-D synthetic layout otherwise).
--file-list restricts the run to the file names listed in a text file (one per line; every listed file must exist), e.g.
plans/synth_sample_100.txt for the 100-file synthetic sample (BND-06).
Environment shim (BND-06, 2026-10-11): ges 1.1.0 uses np.Inf, removed in NumPy 2; on NumPy >= 2 np.Inf is set to np.inf
(the same float) before ges runs. Without it every gesbic file fails with AttributeError and is scored as an empty graph.

  python analysis/causalarena_methods.py --method ges --family semantic --regime obs_only --out analysis/results/methods/ges_semantic_obs.json [--files-every 1] [--budget-s 150]
"""
import argparse, glob, json, os, sys, time, zlib
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
from crucis._support import causalarena_io as CA  # noqa: E402
from crucis._support.causalarena_load import load_any  # noqa: E402
from crucis._support import jobkit  # noqa: E402
from crucis._support import score_record as SR  # noqa: E402

REPO = Path(os.environ.get("CC_REPO", HERE.parent.parent / "Causal-Copilot"))


def marks_to_graph(A):
    """causal-learn endpoint matrix -> (committed arrows, undecided pairs with marks). A[i, j] is the mark at i on the i-j edge:
    -1 tail, 1 arrowhead, 2 circle."""
    d = A.shape[0]
    directed, undecided = set(), {}
    for i in range(d):
        for j in range(i + 1, d):
            mi, mj = int(A[i, j]), int(A[j, i])
            if mi == 0 and mj == 0:
                continue
            if mi == -1 and mj == 1:
                directed.add((i, j))
            elif mi == 1 and mj == -1:
                directed.add((j, i))
            else:
                undecided[(i, j)] = (mi, mj)
    return directed, undecided


def run(method, X):
    if method == "pc":
        from causallearn.search.ConstraintBased.PC import pc
        return pc(X, alpha=0.05, indep_test="fisherz", stable=True, show_progress=False).G.graph
    if method == "ges":
        from causallearn.search.ScoreBased.GES import ges
        return ges(X, score_func="local_score_BIC")["G"].graph
    if method == "gesbic":
        import ges as ges_pkg
        if not hasattr(np, "Inf"):                     # NumPy >= 2 removed the alias; ges 1.1.0 main.py still uses it
            np.Inf = np.inf
        Z = (X - X.mean(0)) / X.std(0)
        C, _ = ges_pkg.fit_bic(Z)                      # C[i, j] = 1 and C[j, i] = 0: i -> j; both 1: undirected
        d = C.shape[0]
        M = np.zeros((d, d), dtype=int)                # causal-learn marks: M[i, j] = mark at i on the i-j edge
        for i in range(d):
            for j in range(d):
                if C[i, j] and not C[j, i]:
                    M[i, j], M[j, i] = -1, 1
                elif C[i, j] and C[j, i]:
                    M[i, j] = M[j, i] = -1
        return M
    if method in ("lingam", "notears"):
        if method == "lingam":
            from causallearn.search.FCMBased.lingam import DirectLiNGAM
            m = DirectLiNGAM(random_state=0)
            m.fit(X)
            W = np.asarray(m.adjacency_matrix_).T              # W[i, j]: i -> j
        else:
            from crucis._support.notears_linear import notears_linear
            W = notears_linear(X, lambda1=0.1, max_iter=100, h_tol=1e-8, w_threshold=0.0)
        B = (np.abs(W) >= 0.5).astype(int)
        np.fill_diagonal(B, 0)
        d = B.shape[0]
        M = np.zeros((d, d), dtype=int)                        # causal-learn marks; both directions -> (1, 1), undecided
        for i in range(d):
            for j in range(d):
                if B[i, j]:
                    M[j, i] = 1
                    if not B[j, i]:
                        M[i, j] = -1
        return M
    if method == "fci":
        from causallearn.search.ConstraintBased.FCI import fci
        G, _ = fci(X, independence_test_method="fisherz", alpha=0.05, show_progress=False, verbose=False)
        return G.graph
    raise ValueError(method)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--method", required=True, choices=("pc", "ges", "gesbic", "fci", "lingam", "notears"))
    ap.add_argument("--family", default="semantic")
    ap.add_argument("--regime", default="obs_only")
    ap.add_argument("--root", default=str(HERE.parent / "external" / "causalarena"))
    ap.add_argument("--out", required=True)
    ap.add_argument("--files-every", type=int, default=1, help="use every k-th file (sorted); 1 = all")
    ap.add_argument("--shuffle-seed", type=int, default=None)
    ap.add_argument("--file-list", default=None, help="text file of file names (one per line) to run; all must exist")
    ap.add_argument("--shard", default="0/1", help="k/n: this process takes files k, k+n, k+2n, ... (outputs are merged afterwards)")
    ap.add_argument("--budget-s", type=float, default=0)
    ap.add_argument("--file-timeout-s", type=int, default=0,
                    help="per-file wall-clock limit; a file over it is a failed file scored as an empty graph (the authors' runners use 300 s)")
    a = ap.parse_args()
    splits = json.load(open(HERE.parent / "plans" / "splits.json", encoding="utf-8"))["families"].get(a.family, {})
    files = sorted(glob.glob(os.path.join(a.root, "scm", a.family, "data", "%s_%s" % (a.family, a.regime), "*.npz")))[::a.files_every]
    if a.file_list:
        want = [ln.strip() for ln in open(a.file_list, encoding="utf-8") if ln.strip()]
        have = {os.path.basename(f): f for f in files}
        missing = [w for w in want if w not in have]
        if missing:
            raise SystemExit("--file-list names %d files not found, e.g. %s" % (len(missing), missing[:3]))
        files = sorted(have[w] for w in set(want))
    k, n = (int(x) for x in a.shard.split("/"))
    files = files[k::n]
    parts = jobkit.Parts(a.out)
    budget = jobkit.Budget(a.budget_s)
    for f in files:
        key = os.path.basename(f)
        if parts.has(key):
            continue
        if not budget.ok(60):
            break
        s = load_any(f)
        X, d = s["values"], len(s["node_ids"])
        if a.regime == "obs_int":
            X = X[: s["n_obs"]] if False else X               # obs+int: all rows, interventions not used by these methods
        perm = list(range(d))
        if a.shuffle_seed is not None:
            perm = list(np.random.default_rng(a.shuffle_seed + zlib.crc32(key.encode())).permutation(d))
            X = X[:, perm]
        t0 = time.time()
        import contextlib, io
        failed = None
        import signal

        def _alarm(signum, frame):
            raise TimeoutError("file exceeded --file-timeout-s %d" % a.file_timeout_s)
        try:
            if a.file_timeout_s:
                signal.signal(signal.SIGALRM, _alarm)
                signal.alarm(a.file_timeout_s)
            try:
                with contextlib.redirect_stdout(io.StringIO()):          # causal-learn prints edges in some versions
                    A = run(a.method, X)
            finally:
                signal.alarm(0)
        except ImportError:
            raise                                                  # environment problems are not data
        except Exception as e:  # noqa: BLE001
            # A method failing on a file is data: e.g. an exactly collinear (deterministic) variable makes a Gaussian score or
            # the Fisher-z correlation matrix singular. The authors' runners score a failed method as an empty graph
            # (TabCausal run_pc.py / run_gies.py: except -> zeros); we do the same and flag the row.
            A, failed = np.zeros((d, d), dtype=int), "%s: %s" % (type(e).__name__, e)
        secs = time.time() - t0
        directed, undecided = marks_to_graph(A)
        back = lambda i: int(perm[i])                       # column i of the permuted file is original variable perm[i]
        directed = {(back(i), back(j)) for i, j in directed}
        undecided = {tuple(sorted((back(i), back(j)))): (m if back(i) < back(j) else m[::-1]) for (i, j), m in undecided.items()}
        truth = CA.true_edges(s["g"])
        und = {frozenset(p) for p in undecided}
        scen = s["meta"]["scenario_id"]
        slug = next((sl for sl in splits.get("dev", []) + splits.get("test", []) if sl in key), None)
        split = "dev" if slug in splits.get("dev", []) else ("test" if slug in splits.get("test", []) else "all-public (measurement, no tuning)")
        scores = {rule: CA.directed_scores(directed, und, truth, d, rule, seed=zlib.crc32(key.encode())) for rule in ("random", "drop", "both")}
        # "lower" orients by the column order the method saw (released order unless shuffled): score in that index space
        pos = {int(v): k for k, v in enumerate(perm)}
        P = lambda e: (pos[e[0]], pos[e[1]])
        scores["lower"] = CA.directed_scores({P(e) for e in directed}, {frozenset(pos[i] for i in p) for p in und},
                                             {P(e) for e in truth}, d, "lower")
        r = SR.row(ticket="BEN-11", family=a.family, scenario=scen, file=key, method=a.method, regime="D",
                   columns_shuffled=a.shuffle_seed is not None, names="not applicable", supplier="causalarena", split=split,
                   metrics={"directed_f1": scores["random"]["f1"], "directed_precision": scores["random"]["precision"],
                            "directed_recall": scores["random"]["recall"], "shd": scores["random"]["shd"], "seconds": round(secs, 2)},
                   domain=s["meta"]["domain_id"], d=d, failed=failed, true_edges=len(truth), shuffle_seed=a.shuffle_seed,
                   directed_edges=sorted([list(e) for e in directed]),
                   undecided_pairs=sorted([[i, j, m[0], m[1]] for (i, j), m in undecided.items()]), scores=scores)
        parts.add(key, r)
    header = {"shard": a.shard, "method": a.method, "family": a.family, "regime": a.regime, "files": len(files), "files_every": a.files_every,
              "shuffle_seed": a.shuffle_seed, "file_timeout_s": a.file_timeout_s, "file_list": a.file_list, "env": jobkit.environment(), "causal_learn": "vendored 0.1.3.8 (Causal-Copilot a31aa7c)"}
    jobkit.finish(parts, header, len(files))


if __name__ == "__main__":
    main()
