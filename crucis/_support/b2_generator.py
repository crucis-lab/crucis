"""B2 name-reliance benchmark generator (AB-08): names suggest G_N, data follow G_D, disagreeing on a fraction rho of edges.

Design and every parameter: analysis/reports/ab08_benchmark_card.md (section 2). In short, for each CausalArena semantic
scenario S (rep000; names N and true graph G_N) and each rho, round(rho |E|) edges of G_N are broken (reversed where that
keeps the graph acyclic, otherwise rewired to a pair adjacent in neither graph), giving G_D; n rows are sampled from G_D
with standardised (iSCM-style) linear-Gaussian or nonlinear additive-noise mechanisms; columns are standardised and
shuffled; the file stores G_D as `g`, G_N as `g_names` and a per-edge agreement matrix.

  python analysis/b2_generator.py --root external/causalarena --out external/b2_namereliance
  python analysis/b2_generator.py --out external/b2_namereliance --check
Deterministic: a rerun with the same arguments writes byte-identical files (fixed zip timestamps, seeded RNGs).
No model calls. Tickets: AUD-39, STR-02, EVL-02
"""
import argparse, hashlib, io, json, os, sys, zipfile, zlib
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
VERSION = "b2-gen/1.0"
TRACKS = ("linear", "nonlinear")
TRACK_ID = {"linear": 1, "nonlinear": 2}
RHOS = (0.0, 0.25, 0.5, 0.75, 1.0)
R_RANGE = (0.5, 0.9)        # share of a node's variance explained by its parents
W_RANGE = (0.5, 2.0)        # |relative weight|
N_ROWS = 1000
R2_BAND = 0.05              # accept a mechanism draw when both R2-sortabilities are within this of 0.5
MAX_ATTEMPTS = 100


def _ensure_imports(root=None):
    """causalarena_io / sortability_audit live in the checkout's analysis/ folder (the kit mirrors it)."""
    pass  # Standalone package: no external source-path injection.
    try:
        from crucis._support import causalarena_io  # noqa: F401
    except ImportError:
        if root is None:
            raise
        pass  # Standalone package: no external source-path injection.
    from crucis._support import causalarena_io as CA
    from crucis._support import sortability_audit as SA
    return CA, SA


def script_sha256():
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def rho_tag(rho):
    return "rho%03d" % int(round(rho * 100))


# ---------------------------------------------------------------- graph surgery

def reaches(A, u, v):
    """True if there is a directed path u ~> v in adjacency A (A[i, j] = 1: i -> j)."""
    if u == v:
        return True
    seen, stack = {u}, [u]
    while stack:
        x = stack.pop()
        for y in np.flatnonzero(A[x]):
            y = int(y)
            if y == v:
                return True
            if y not in seen:
                seen.add(y)
                stack.append(y)
    return False


def is_acyclic(A):
    A = np.asarray(A) != 0
    indeg = A.sum(0).astype(int)
    q = [i for i in range(A.shape[0]) if indeg[i] == 0]
    seen = 0
    while q:
        x = q.pop()
        seen += 1
        for y in np.flatnonzero(A[x]):
            indeg[y] -= 1
            if indeg[y] == 0:
                q.append(int(y))
    return seen == A.shape[0]


def edge_order(GN, seed, slug):
    edges = [tuple(int(t) for t in e) for e in np.argwhere(GN != 0)]
    perm = np.random.default_rng([seed, zlib.crc32(slug.encode()), 7]).permutation(len(edges))
    return [edges[i] for i in perm]


def break_graph(GN, rho, seed, slug):
    """Return G_D, edge_agreement, info. The first k edges of a rho-independent order are broken in turn (nested in rho)."""
    GN = (np.asarray(GN) != 0).astype(np.int8)
    d, m = GN.shape[0], int(GN.sum())
    k = int(np.floor(rho * m + 0.5))
    order = edge_order(GN, seed, slug)
    G = GN.copy()
    adjN = (GN + GN.T) > 0
    kinds = {"reversed": 0, "rewired_effect": 0, "rewired_cause": 0, "rewired_any": 0}
    for t, (a, b) in enumerate(order[:k]):
        rng = np.random.default_rng([seed, zlib.crc32(slug.encode()), 11, t])
        G[a, b] = 0
        if not reaches(G, a, b):                       # b -> a closes no cycle
            G[b, a] = 1
            kinds["reversed"] += 1
            continue
        adj = adjN | ((G + G.T) > 0)
        free = lambda u, v: u != v and not adj[u, v] and not reaches(G, v, u)  # noqa: E731
        cand, kind = [(c, b) for c in range(d) if c not in (a, b) and free(c, b)], "rewired_effect"
        if not cand:
            cand, kind = [(a, c) for c in range(d) if c not in (a, b) and free(a, c)], "rewired_cause"
        if not cand:
            cand, kind = [(u, v) for u in range(d) for v in range(d) if (u, v) != (a, b) and free(u, v)], "rewired_any"
        if not cand:
            raise RuntimeError("%s: no rewire target for edge %d" % (slug, t))
        u, v = cand[int(rng.integers(len(cand)))]
        G[u, v] = 1
        kinds[kind] += 1
    assert int(G.sum()) == m and is_acyclic(G), slug
    agree = np.zeros((d, d), dtype=np.int8)
    for i, j in np.argwhere(G != 0):
        agree[i, j] = 1 if GN[i, j] else (-1 if GN[j, i] else -2)
    acc = float((agree == 1).sum()) / m
    assert abs(acc - (1 - rho)) <= 0.5 / m + 1e-12, (slug, rho, acc)
    return G, agree, {"m": m, "k": k, "name_direction_accuracy": acc, **kinds}


# ---------------------------------------------------------------- sampling

def topo_order(G):
    G = np.asarray(G) != 0
    indeg = G.sum(0).astype(int)
    q = sorted(i for i in range(G.shape[0]) if indeg[i] == 0)
    out = []
    while q:
        x = q.pop(0)
        out.append(x)
        for y in np.flatnonzero(G[x]):
            indeg[y] -= 1
            if indeg[y] == 0:
                q.append(int(y))
        q.sort()
    return out


def noises(track, seed, slug, rep, d, n=N_ROWS):
    """Per-variable noise vectors (standardised), keyed by variable identity only: identical at every rho and attempt."""
    base = [seed, zlib.crc32(slug.encode()), TRACK_ID[track], rep]
    out = []
    for j in range(d):
        nr = np.random.default_rng(base + [1, j])
        e = nr.uniform(-1, 1, n) if (track == "nonlinear" and nr.random() < 0.5) else nr.standard_normal(n)
        out.append((e - e.mean()) / e.std())
    return out


def uniforms(key, k):
    """k deterministic U[0, 1) draws from a key (blake2b of its text): cheap per-node / per-edge streams."""
    h = hashlib.blake2b(("|".join(str(v) for v in key)).encode(), digest_size=8 * k).digest()
    return np.frombuffer(h, dtype="<u8") / 2.0 ** 64


def sample(G, track, seed, slug, rep, attempt=0, noise=None, order=None):
    """Sample N_ROWS rows from DAG G in the source (G_N) indexing. The mechanism draws (r_j per node; weight, sign and h
    per edge) are keyed by (attempt, variable identity), so at attempt 0 an unbroken edge's weight is the same at every
    rho. Returns (X, mean r_j over non-root nodes)."""
    d = G.shape[0]
    noise = noise if noise is not None else noises(track, seed, slug, rep, d)
    base = [seed, zlib.crc32(slug.encode()), TRACK_ID[track], rep, attempt]
    rs = []
    X = np.zeros((d, N_ROWS))                     # row j = variable j (contiguous)
    for j in (order if order is not None else topo_order(G)):
        pa = np.flatnonzero(G[:, j])
        if len(pa) == 0:
            X[j] = noise[j]
            continue
        r = R_RANGE[0] + (R_RANGE[1] - R_RANGE[0]) * uniforms(base + [3, j], 1)[0]
        rs.append(r)
        s = np.zeros(N_ROWS)
        for i in pa:
            u = uniforms(base + [2, int(i), j], 3)
            w = (W_RANGE[0] + (W_RANGE[1] - W_RANGE[0]) * u[0]) * (1 if u[1] < 0.5 else -1)
            h = X[i] if track == "linear" else (np.tanh(X[i]) if u[2] < 0.5 else X[i] * X[i] - 1)
            s += w * h
        s -= s.mean()
        sd = np.sqrt(s @ s / N_ROWS)
        X[j] = (np.sqrt(r) / sd * s if sd > 0 else 0.0) + np.sqrt(1 - r) * noise[j]
    X = X.T
    X = (X - X.mean(0)) / X.std(0)
    return X, float(np.mean(rs)) if rs else 0.0


def r2_fast(X):
    """R2 of each column regressed on all others (with intercept), 1 - 1/(var_j * inv(cov)_jj): the same quantity as
    sortability_audit.r2_all (checked in the tests), from one d x d inverse instead of d least-squares fits."""
    C = np.cov(X, rowvar=False, bias=True)
    return 1 - 1 / (np.diag(C) * np.diag(np.linalg.inv(C)))


def sample_matched(SA, G, track, seed, slug, rep):
    """R2-sortability matching: draw mechanisms (attempt 0, 1, ...) until the R2-sortability against G, path-weighted and
    edge-only, is within R2_BAND of 0.5 (distance = the larger of the two); after MAX_ATTEMPTS keep the closest draw. Without this the linear track's
    R2-sortability falls with rho (pilot on 8 dev scenarios: 0.46 at rho 0 to 0.32 at rho 1), because reversing edges
    turns many-parent sinks into many-child roots, whose R2 given all other columns is high."""
    best = None
    E = (np.asarray(G) != 0).astype(int)
    noise, order = noises(track, seed, slug, rep, E.shape[0]), topo_order(E)
    for att in range(MAX_ATTEMPTS):
        X, rbar = sample(E, track, seed, slug, rep, attempt=att, noise=noise, order=order)
        r2 = r2_fast(X)
        s = SA.sortability(r2, E)
        dist = max(abs(s - 0.5), abs(SA.sortability(r2, E, paths=False) - 0.5))
        if best is None or dist < best[4]:
            best = (X, rbar, s, att, dist)
        if dist <= R2_BAND:
            break
    return best[:4]


# ---------------------------------------------------------------- deterministic npz

def write_npz(path, arrays):
    """np.savez_compressed with fixed zip metadata, so identical arrays give identical bytes."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name in sorted(arrays):
            b = io.BytesIO()
            np.lib.format.write_array(b, np.asanyarray(arrays[name]), allow_pickle=False)
            zi = zipfile.ZipInfo(name + ".npy", date_time=(1980, 1, 1, 0, 0, 0))
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = 0o600 << 16
            zf.writestr(zi, b.getvalue())
    data = buf.getvalue()
    tmp = str(path) + ".tmp"
    with open(tmp, "wb") as f:
        f.write(data)
    os.replace(tmp, path)
    return hashlib.sha256(data).hexdigest()


def read_json(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def write_json(obj, p):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1, sort_keys=True)


def sha256_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


# ---------------------------------------------------------------- one file

def make_file(SA, src, slug, split, rho, track, rep, seed, gen_sha):
    """Build one released file's arrays from a loaded source scenario. Returns (arrays, meta)."""
    GN = (np.asarray(src["g"]) != 0).astype(np.int8)
    names = list(src["node_ids"])
    d = len(names)
    GD, agree, info = break_graph(GN, rho, seed, slug)
    X, rbar, r2s, att = sample_matched(SA, GD, track, seed, slug, rep)
    perm_seed = int(np.random.default_rng([seed, zlib.crc32(slug.encode()), TRACK_ID[track], rep,
                                           int(round(rho * 100)), 3]).integers(2 ** 31))
    perm = np.random.default_rng(perm_seed).permutation(d)           # column c of the file = source variable perm[c]
    P = lambda M: np.asarray(M)[np.ix_(perm, perm)]                   # noqa: E731
    Xs = X[:, perm].astype(np.float32)
    x = np.zeros((N_ROWS, d, 2), dtype=np.float32)
    x[:, :, 0] = Xs
    meta = {"generator": "analysis/b2_generator.py", "generator_version": VERSION, "generator_sha256": gen_sha,
            "benchmark": "b2_namereliance", "source_family": "semantic", "source_file": src["_file"],
            "source_scenario_id": src["meta"].get("scenario_id"), "slug": slug, "domain_id": src["meta"].get("domain_id"),
            "scenario_id": "b2_%s_%s_%s" % (track, rho_tag(rho), slug), "rho": rho, "track": track, "replicate": rep,
            "split": split, "n_obs": N_ROWS, "n_int": 0, "d": d, "edges": info["m"], "broken": info["k"],
            "break_kinds": {k: info[k] for k in ("reversed", "rewired_effect", "rewired_cause", "rewired_any")},
            "name_direction_accuracy": info["name_direction_accuracy"],
            "r2_matching": {"band": R2_BAND, "attempt": att, "r2_paths_at_generation": r2s, "mean_explained_share": rbar},
            "seeds": {"master": seed, "graph": [seed, "crc32(slug)", "edge position"],
                      "noise": [seed, "crc32(slug)", TRACK_ID[track], rep, 1, "variable"],
                      "mechanism": "blake2b of [%d, crc32(slug), %d, %d, %d, 3, node | 2, parent, child]" % (seed, TRACK_ID[track], rep, att), "column_permutation": perm_seed},
            "column_permutation": [int(v) for v in perm],
            "mechanism": {"linear": "X_j = sqrt(r_j) s_j/sd(s_j) + sqrt(1-r_j) e_j, s_j = sum w_ij X_i, Gaussian e",
                          "nonlinear": "same, s_j = sum w_ij h_ij(X_i), h in {tanh, x^2-1}, e Gaussian or uniform"}[track],
            "weights": "sign x U%s" % (list(W_RANGE),), "explained_share": "U%s per node" % (list(R_RANGE),),
            "encoding": {"g": "G_D, g[i,j]=1: node_ids[i] -> node_ids[j]", "g_names": "G_N (the source scenario's graph), same indexing",
                         "edge_agreement": "on G_D edges: 1 names agree, -1 reversed (G_N has j->i), -2 rewired (no G_N edge on the pair); 0 no G_D edge"},
            "node_ids": [names[i] for i in perm]}
    arrays = {"x": x, "g": P(GD).astype(np.float32), "g_names": P(GN).astype(np.float32), "edge_agreement": P(agree).astype(np.int8),
              "mask": np.ones((N_ROWS, d), dtype=np.float32), "f": np.array([d], dtype=np.int64),
              "n_obs": np.array([N_ROWS], dtype=np.int64), "n_int": np.array([0], dtype=np.int64),
              "node_ids": np.array([names[i] for i in perm]), "metadata_json": np.array(json.dumps(meta, sort_keys=True))}
    return arrays, meta


def leakage_checks(SA, arrays):
    Xs = arrays["x"][:, :, 0].astype(float)
    E = (arrays["g"] != 0).astype(int)
    EN = (arrays["g_names"] != 0).astype(int)
    v, r2 = Xs.var(0), SA.r2_all(Xs)
    iu = np.triu_indices(E.shape[0], 1)
    return {"var_paths": SA.sortability(v, E), "var_edges": SA.sortability(v, E, paths=False),
            "r2_paths": SA.sortability(r2, E), "r2_edges": SA.sortability(r2, E, paths=False),
            "r2_paths_vs_names": SA.sortability(r2, EN),
            "lower_col_share": float(E[iu].sum()) / E.sum(),
            "name_agreement": float((arrays["edge_agreement"] == 1).sum()) / E.sum()}


def sources(root, splits_path):
    CA, _ = _ensure_imports(root)
    folder = Path(root) / "scm" / "semantic" / "data" / "semantic_obs_only"
    sp = read_json(splits_path)["families"]["semantic"]
    out = []
    for f in sorted(folder.glob("*__rep000.npz")):
        s = CA.load(f)
        s["_file"] = f.name
        slug = s["meta"]["scenario_id"]
        split = "dev" if slug in sp["dev"] else ("test" if slug in sp["test"] else None)
        if split is None:
            raise SystemExit("scenario %s is in neither split" % slug)
        out.append((slug, split, s))
    return out


def generate(root, out, rhos, tracks, reps, seed, splits_path, slugs=None, quiet=False):
    CA, SA = _ensure_imports(root)
    gen_sha = script_sha256()
    out = Path(out)
    files, checks = {}, []
    for slug, split, src in sources(root, splits_path):
        if slugs and slug not in slugs:
            continue
        for track in tracks:
            for rho in rhos:
                sub = out / track / rho_tag(rho)
                sub.mkdir(parents=True, exist_ok=True)
                for rep in range(reps):
                    arrays, meta = make_file(SA, src, slug, split, rho, track, rep, seed, gen_sha)
                    name = "b2_%s_%s_%s__rep%03d.npz" % (track, rho_tag(rho), slug, rep)
                    rel = "%s/%s/%s" % (track, rho_tag(rho), name)
                    files[rel] = write_npz(sub / name, arrays)
                    c = leakage_checks(SA, arrays)
                    checks.append({"file": rel, "slug": slug, "split": split, "track": track, "rho": rho, "rep": rep,
                                   "d": meta["d"], "edges": meta["edges"], "broken": meta["broken"], **meta["break_kinds"],
                                   "attempt": meta["r2_matching"]["attempt"], "mean_explained_share": meta["r2_matching"]["mean_explained_share"], **c})
        if not quiet:
            print("done", slug, flush=True)
    manifest = {"benchmark": "b2_namereliance", "generator": "analysis/b2_generator.py", "generator_version": VERSION,
                "generator_sha256": gen_sha, "params": {"rhos": list(rhos), "tracks": list(tracks), "reps": reps, "seed": seed,
                                                       "n": N_ROWS, "weights": list(W_RANGE), "explained_share": list(R_RANGE),
                                                       "r2_band": R2_BAND, "max_attempts": MAX_ATTEMPTS,
                                                       "slugs": sorted(slugs) if slugs else "all"},
                "files": dict(sorted(files.items()))}
    write_json(manifest, out / "MANIFEST.json")
    write_json({"rows": checks}, out / "leakage_checks.json")
    return manifest, checks


def summarise(checks):
    import statistics as st
    keys = ("var_paths", "r2_paths", "r2_edges", "r2_paths_vs_names", "lower_col_share", "name_agreement",
            "attempt", "mean_explained_share")
    out = {}
    for track in sorted({c["track"] for c in checks}):
        out[track] = {}
        for rho in sorted({c["rho"] for c in checks}):
            rows = [c for c in checks if c["track"] == track and c["rho"] == rho]
            out[track][rho_tag(rho)] = {"files": len(rows), **{k: {"mean": round(st.mean(r[k] for r in rows), 4),
                                                                  "sd": round(st.pstdev(r[k] for r in rows), 4),
                                                                  "min": round(min(r[k] for r in rows), 4),
                                                                  "max": round(max(r[k] for r in rows), 4)} for k in keys},
                                         "reversed_share_of_broken": round(sum(r["reversed"] for r in rows) / max(1, sum(r["broken"] for r in rows)), 4)}
    return out


def check(out):
    out = Path(out)
    man = read_json(out / "MANIFEST.json")
    bad = [rel for rel, h in man["files"].items() if not (out / rel).exists() or sha256_file(out / rel) != h]
    listed = set(man["files"])
    extra = sorted(str(p.relative_to(out)) for p in out.glob("*/*/*.npz") if str(p.relative_to(out)) not in listed)
    same_gen = man["generator_sha256"] == script_sha256()
    print(json.dumps({"files": len(listed), "hash_mismatch_or_missing": bad[:20], "n_bad": len(bad), "unlisted": extra[:20],
                      "generator_sha256_matches": same_gen}, indent=1))
    return not bad and not extra


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(HERE.parent / "external" / "causalarena"), help="CausalArena root (holds scm/)")
    ap.add_argument("--out", default=str(HERE.parent / "external" / "b2_namereliance"))
    ap.add_argument("--splits", default=None, help="default: <root>/../../plans/splits.json")
    ap.add_argument("--rhos", type=float, nargs="+", default=list(RHOS))
    ap.add_argument("--tracks", nargs="+", default=list(TRACKS), choices=TRACKS)
    ap.add_argument("--reps", type=int, default=5)
    ap.add_argument("--seed", type=int, default=20261012)
    ap.add_argument("--slugs", nargs="*", default=None, help="restrict to these source scenarios (tests, pilots)")
    ap.add_argument("--summary-out", default=None, help="also write the sortability-by-rho summary JSON here")
    ap.add_argument("--check", action="store_true", help="verify MANIFEST.json against the files under --out")
    a = ap.parse_args()
    if a.check:
        sys.exit(0 if check(a.out) else 1)
    splits = a.splits or str(Path(a.root).resolve().parents[1] / "plans" / "splits.json")
    man, checks = generate(a.root, a.out, a.rhos, a.tracks, a.reps, a.seed, splits, slugs=a.slugs)
    summ = summarise(checks)
    total = sum((Path(a.out) / r).stat().st_size for r in man["files"])
    print(json.dumps({"files": len(man["files"]), "bytes": total, "summary": summ}, indent=1))
    if a.summary_out:
        os.makedirs(os.path.dirname(a.summary_out) or ".", exist_ok=True)
        write_json({"producer": "analysis/b2_generator.py", "generator_sha256": man["generator_sha256"], "files": len(man["files"]),
                    "bytes": total, "by_track_rho": summ}, a.summary_out)


if __name__ == "__main__":
    main()
