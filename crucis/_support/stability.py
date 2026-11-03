"""Run-to-run stability and the name-versus-data test (pass 4b).

  python stability.py --runs-dir RUNS --label p4b --out OUT [--mapping DATASETS/MAPPING.json]
                      [--repo PATH] [--stub] [--min-runs 3] [--python PY]

Reads every run under RUNS whose meta.json has the given label, groups runs into arms by dataset,
runs lineage.py on each (so every run must first pass lineage gates A-F), and reports per arm:
what was chosen, where runs stop asking the model the same thing, whether identical requests got
identical answers, how the LLM's per-pair decisions and the final edges vary, and accuracy by stage.
For the sachs-derived arms it then classifies every edge the LLM review set as following the column
labels, the data, both or neither.

Gates (exit code 1 if a blocking gate fails):
  T1  blocking  every included run: status COMPLETED, code identity OK, lineage gates A-F pass.
                Runs failing T1 are excluded and listed; the gate fails only if an arm is left empty.
  T2  blocking  each arm has at least --min-runs included runs (spread from fewer is not reported as spread).
  T3  blocking  every run in an arm read the same dataset bytes, and for derived arms those bytes are
                the ones recorded in MAPPING.json (needs the dataset_identity record; older runs: n/a).
  T4  blocking  the variable names seen by the pipeline equal the arm's column labels.
  T5  blocking  for derived arms, accuracy recomputed here from the stage matrices equals lineage.py's.
  T6  report    all runs of an arm were served by one model snapshot (a FALSE is reported, not fatal).

Predictions written down before any live data existed (thresholds fixed here, in code):
  P1  d03: of LLM-set final edges that are adjacent in exactly one reference, the share that follows
      the labels. SUPPORTED (names drive the review) if >= 0.8 with n >= 10; REFUTED if <= 0.5 with
      n >= 10; otherwise INCONCLUSIVE.
  P2  d02 has at most half as many LLM-set final edges per run as d01. SUPPORTED / REFUTED.
  P3  pooled over all distinct (data, algorithm output, bootstrap result) combinations, the share of the algorithm's non-directed edges (undirected,
      bidirected, circle marks) that are still adjacent after the bootstrap step. SUPPORTED (the step
      deletes them) if <= 0.25 with n >= 20 edges; REFUTED if >= 0.5 with n >= 20; else INCONCLUSIVE.
      (First written as "fewer than half of all adjacencies survive in every run"; the stub self-test
      showed that form mixes directed edges, which survive, with non-directed ones. Changed before
      any live repeat existed.)
  P4  (exploratory, no verdict) sachs versus d01: difference in mean final adjacency F1.
  P5  (exploratory, no verdict) share of arms in which the chosen algorithm was not unanimous.

Family-level predictions added for bundle 1 (several datasets, each with real / neutral / swapped
label arms on identical numbers), fixed before any bundle-1 run existed:
  N1  as P1 but pooled over families and counted by DISTINCT (family, edge), so a recurring edge
      counts once. Same thresholds as P1 (>= 0.8 supported, <= 0.5 refuted, n >= 10 distinct edges).
  N2  as P2 per family; SUPPORTED if it holds in every family whose real-name arm has any LLM-set
      edges (at least 2 such families), REFUTED if it holds in half of them or fewer.
  N4  the final graph has lower adjacency F1 than the algorithm's own output in at least 80% of
      runs (n >= 10 runs): SUPPORTED; in 50% or fewer: REFUTED.
  N5  (exploratory) directed-edge F1 and adjacency F1 of algorithm output and final graph by role.
P3 is unchanged and is pooled over everything analysed.
"""
import argparse
import hashlib
import itertools
import json
import os
import re
import statistics as st
import subprocess
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
from crucis._support import cc_graph as G  # noqa: E402

STAGES = ["S0 algorithm output", "S1 after bootstrap edits", "S2 after LLM review", "S3 after KCI pruning",
          "S4 final (after cycle step)"]
SHORT = ["S0", "S1", "S2", "S3", "S4"]
TS = re.compile(r"\d{8}_\d{6}")
T0 = time.time()
METRICS = ("adj_precision", "adj_recall", "adj_f1", "true_edges_correctly_directed", "true_edges_reversed", "shd_vs_true_cpdag",
           "dir_precision", "dir_recall", "dir_f1")
P1_HI, P1_LO, P1_N = 0.8, 0.5, 10
P3_HI, P3_LO, P3_N = 0.25, 0.5, 20          # share surviving: <= P3_HI supported, >= P3_LO refuted
N2_MIN_FAMILIES = 2                         # N2 needs at least this many families where the real-name arm has LLM-set edges
N4_HI, N4_LO, N4_N = 0.8, 0.5, 10           # share of runs with final adjacency F1 below the algorithm's: >= HI supported, <= LO refuted


def norm_hash(obj):
    s = json.dumps(obj, sort_keys=True, default=str)
    return hashlib.sha256(TS.sub("<TS>", s).encode("utf-8")).hexdigest()


def ms(xs, nd=2):
    xs = [x for x in xs if x is not None]
    if not xs:
        return "n/a"
    if len(xs) == 1:
        return ("%." + str(nd) + "f (1 run)") % xs[0]
    return ("%." + str(nd) + "f ± %." + str(nd) + "f") % (st.mean(xs), st.stdev(xs))


def jaccard(a, b):
    return 1.0 if not a and not b else len(a & b) / float(len(a | b))


def mean_pairwise(sets):
    ps = [jaccard(a, b) for a, b in itertools.combinations(sets, 2)]
    return st.mean(ps) if ps else None


def load_calls(run_dir):
    out = []
    f = run_dir / "llm_calls.jsonl"
    if not f.exists():
        return out
    for line in open(f, encoding="utf-8"):
        d = json.loads(line)
        if d.get("level") != "client":
            continue
        api = d.get("api") or []
        api = api if isinstance(api, list) else [api]
        last = (api[-1].get("response") if api and isinstance(api[-1], dict) else None) or {}
        out.append({"seq": d["seq"], "stage": d.get("stage"),
                    "req": norm_hash([d.get("args"), d.get("response_format")]),
                    "res": norm_hash(d.get("result")),
                    "model": last.get("model"), "fingerprint": last.get("system_fingerprint"),
                    "sdk_calls": len(api)})
    return out


def arm_of(meta, mapping):
    ds = str(meta.get("dataset", "")).replace("\\", "/")
    if mapping:
        for arm, spec in mapping["arms"].items():
            tail = spec["dataset_arg"].split(":", 1)[1]
            if ds.endswith("/" + tail) or ds == tail:
                return arm, spec
    return Path(ds).name.replace(".csv", ""), None


ROLE_ORDER = {"real_named_path": 0, "real": 1, "neutral": 2, "swapped": 3}
V1_ROLES = {"sachs": ("sachs", "real_named_path"), "d01": ("sachs", "real"), "d02": ("sachs", "neutral"), "d03": ("sachs", "swapped")}


def family_role(arm, spec):
    """(family, role) of an arm. Format-2 mappings state them; the pass-4b mapping is translated."""
    if spec is None:
        return arm, "ground_truth"
    if "family" in spec:
        return spec["family"], spec["role"]
    return V1_ROLES.get(arm, (arm, "real"))


def typed_edges(M, names):
    p = len(names)
    out = set()
    for a, b in G.pairs(p):
        t = G.pair_type(M, a, b)
        if t != "none" and G.is_adjacent(M, a, b):
            out.add(G.named(t, names[a], names[b]))
    return out


def adjacency(M):
    p = M.shape[0]
    return {(a, b) for a, b in G.pairs(p) if G.is_adjacent(M, a, b)}


def directed(M):
    """(cause, effect) pairs for cells with code 1 whose mirror cell is empty."""
    return {(int(j), int(i)) for i, j in np.argwhere(M == 1) if M[j, i] == 0}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs-dir", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--mapping", default=None)
    ap.add_argument("--repo", default=os.environ.get("CC_REPO", os.path.expanduser("~/cc")))
    ap.add_argument("--stub", action="store_true", help="analyse STUB runs (tool self-test) instead of live runs")
    ap.add_argument("--min-runs", type=int, default=3)
    ap.add_argument("--python", default=sys.executable)
    ap.add_argument("--reuse-lineage", action="store_true", help="do not recompute lineage for runs that already have it under OUT")
    ap.add_argument("--lineage-budget-s", type=float, default=0, help="stop (exit 3) once this many seconds were spent; rerun to continue")
    a = ap.parse_args()
    out = Path(a.out)
    (out / "lineage").mkdir(parents=True, exist_ok=True)
    mapping = json.load(open(a.mapping, encoding="utf-8")) if a.mapping else None
    mdir = Path(a.mapping).parent if a.mapping else None

    arms = defaultdict(list)
    excluded = []
    for d in sorted(Path(a.runs_dir).iterdir()):
        mp = d / "meta.json"
        if not mp.exists():
            continue
        meta = json.load(open(mp, encoding="utf-8"))
        if meta.get("label") != a.label or bool(meta.get("stub_llm")) != a.stub:
            continue
        arm, spec = arm_of(meta, mapping)
        try:
            summ = json.load(open(d / "summary.json", encoding="utf-8"))
        except Exception:
            summ = {"status": "NO SUMMARY", "must_show": {}}
        why = []
        if summ.get("status") != "COMPLETED":
            why.append("status %s" % summ.get("status"))
        if summ.get("must_show", {}).get("1_code_identity") != "OK":
            why.append("code identity %s" % summ.get("must_show", {}).get("1_code_identity"))
        lin = None
        if not why:
            ldir = out / "lineage" / d.name
            cmd = [a.python, str(HERE / "lineage.py"), str(d), "--repo", a.repo, "--out", str(ldir)]
            if spec is not None:
                cmd += ["--reference", str(mdir / spec["reference_by_data"])]
            if a.reuse_lineage and (ldir / "lineage.json").exists():
                r = subprocess.CompletedProcess(cmd, 0, "", "")          # a run record never changes once written
            elif a.lineage_budget_s and time.time() - T0 > a.lineage_budget_s:
                print("lineage budget reached; rerun with --reuse-lineage to continue")
                sys.exit(3)
            else:
                r = subprocess.run(cmd, capture_output=True, text=True)
            if not (ldir / "lineage.json").exists():
                why.append("lineage.py produced no output: %s" % (r.stderr.strip().splitlines() or ["?"])[-1][:200])
            else:
                lin = json.load(open(ldir / "lineage.json", encoding="utf-8"))
                if not lin.get("all_gates_pass"):
                    why.append("lineage gates failed: %s" % [k for k, v in lin["gates"].items() if not v])
        if why:
            excluded.append({"run": d.name, "arm": arm, "why": why})
            continue
        arms[arm].append({"dir": d, "id": d.name, "meta": meta, "summary": summ, "lin": lin, "spec": spec,
                          "calls": load_calls(d)})

    gates = {}
    L = ["# Stability and name-versus-data report", "",
         "Label `%s`%s. Runs directory `%s`. %d runs included in %d arms; %d excluded." % (
             a.label, " (STUB LLM: tool self-test, answers carry no meaning)" if a.stub else "", a.runs_dir,
             sum(len(v) for v in arms.values()), len(arms), len(excluded)), ""]
    res = {"label": a.label, "stub": a.stub, "arms": {}, "excluded": excluded}
    if excluded:
        L += ["## Excluded runs", "", "| Run | Arm | Reason |", "|---|---|---|"]
        L += ["| %s | %s | %s |" % (e["run"], e["arm"], "; ".join(e["why"])) for e in excluded]
        L.append("")
    all_arms_named = set(arms) | {e["arm"] for e in excluded}
    gates["T1_no_arm_left_empty"] = all(len(arms.get(k, [])) > 0 for k in all_arms_named)
    gates["T2_min_runs_per_arm"] = bool(arms) and all(len(v) >= a.min_runs for v in arms.values())
    t3, t4, t5, t6 = [], [], [], []

    fr = {arm: family_role(arm, runs_[0]["spec"]) for arm, runs_ in arms.items()}
    order = sorted(arms, key=lambda k: (fr[k][1] == "ground_truth", fr[k][0], ROLE_ORDER.get(fr[k][1], 9), k))
    for arm in order:
        runs = arms[arm]
        spec = runs[0]["spec"]
        names = runs[0]["lin"]["variables"]
        p = len(names)
        n = len(runs)
        A = {"n_runs": n, "runs": [r["id"] for r in runs]}
        L += ["## Arm `%s` (%d runs)" % (arm, n), ""]
        if spec is not None:
            L += ["Family `%s`, role `%s`. Column labels: %s. File path names the dataset: %s." % (
                fr[arm][0], fr[arm][1], ", ".join(spec["column_labels"]),
                "yes" if spec.get("path_says_sachs", spec.get("path_says_name", False)) else "no"), ""]
        A["family"], A["role"] = fr[arm]

        # T3 dataset bytes
        idents = [json.dumps((r["meta"].get("dataset_identity") or {}).get("files"), sort_keys=True) for r in runs]
        have = all((r["meta"].get("dataset_identity") or {}).get("files") for r in runs)
        if not have:
            A["T3"] = "n/a (runs recorded before dataset_identity existed)"
        else:
            same = len(set(idents)) == 1
            ok = same
            if spec is not None:
                shas = {v["sha256"] for v in runs[0]["meta"]["dataset_identity"]["files"].values()}
                ok = same and shas == {spec["sha256"]}
            A["T3"] = bool(ok)
            t3.append(ok)
        # T4 variable names
        ok4 = all(r["lin"]["variables"] == names for r in runs) and (spec is None or names == spec["column_labels"])
        A["T4"] = bool(ok4)
        t4.append(ok4)
        # T6 model snapshot
        models = Counter(m for r in runs for m in r["summary"]["must_show"].get("3_llm_calls", {}).get("served_models", []))
        A["served_models"] = dict(models)
        t6.append(len(models) <= 1)

        # choices
        algo = Counter(r["lin"]["algorithm"] for r in runs)
        hp = Counter(json.dumps(r["lin"]["hyperparameters_used"], sort_keys=True) for r in runs)
        dropped = Counter(json.dumps(r["lin"]["hyperparameters_proposed_by_llm_but_not_used"]) for r in runs)
        A.update({"algorithm": dict(algo), "hyperparameters": dict(hp), "hyperparameters_proposed_not_used": dict(dropped)})
        L += ["**Choices.** Algorithm: %s. Hyperparameters passed to it: %s. Proposed by the LLM but not passed: %s. Served model: %s." % (
            ", ".join("%s ×%d" % kv for kv in algo.most_common()), "; ".join("%s ×%d" % kv for kv in hp.most_common()),
            "; ".join("%s ×%d" % kv for kv in dropped.most_common()), ", ".join("%s" % k for k in models) or "n/a"), ""]

        # request / response agreement
        groups = defaultdict(lambda: defaultdict(set))       # stage -> req -> {(run, res)}
        for i, r in enumerate(runs):
            for c in r["calls"]:
                groups[c["stage"]][c["req"]].add((i, c["res"]))
        rows, tot_shared, tot_same = [], 0, 0
        for stage in sorted(groups):
            shared = [v for v in groups[stage].values() if len({i for i, _ in v}) >= 2]
            same = [v for v in shared if len({h for _, h in v}) == 1]
            in_all = [v for v in groups[stage].values() if len({i for i, _ in v}) == n]
            rows.append((stage, len(groups[stage]), len(shared), len(same), len(in_all)))
            tot_shared += len(shared)
            tot_same += len(same)
        firsts = Counter()
        for x, y in itertools.combinations(range(n), 2):
            cx, cy = runs[x]["calls"], runs[y]["calls"]
            k = next((i for i in range(min(len(cx), len(cy))) if cx[i]["req"] != cy[i]["req"]), None)
            firsts[cx[k]["stage"] if k is not None else ("never (%d calls)" % min(len(cx), len(cy)))] += 1
        A["identical_request_groups"] = {"asked_in_2plus_runs": tot_shared, "of_which_identical_answer": tot_same}
        A["first_stage_where_requests_differ"] = dict(firsts)
        L += ["**Same question, same answer?** A request is \"the same\" when the full prompt and settings are identical after masking timestamps.", "",
              "| Stage | Distinct requests | Asked in 2+ runs | of which answered identically | Asked in every run |", "|---|---|---|---|---|"]
        L += ["| %s | %d | %d | %d | %d |" % r for r in rows]
        L += ["", "First stage at which two runs stop sending identical requests (one count per pair of runs): %s." % (
            ", ".join("%s ×%d" % kv for kv in firsts.most_common()) or "n/a (one run)"), ""]

        # is the bootstrap the same in every run? (Python's random is seeded as a side effect of an import)
        import pickle
        rng = set()
        for r in runs:
            try:
                stt = pickle.load(open(r["dir"] / "rng_initial_states.pkl", "rb"))
                rng.add(hashlib.sha256(repr(stt.get("python_random")).encode()).hexdigest()[:12])
            except Exception:
                rng.add("unreadable")
        bgroups = defaultdict(set)
        for r in runs:
            key = "%s %s" % (r["lin"]["algorithm"], json.dumps(r["lin"]["hyperparameters_used"], sort_keys=True))
            bgroups[key].add(norm_hash([row["bootstrap_frequency"] for row in r["lin"]["pairs"]]))
        A["python_random_initial_states"] = sorted(rng)
        A["bootstrap_tables_per_choice"] = {k: len(v) for k, v in bgroups.items()}
        L += ["**Randomness.** Distinct initial states of Python's random-number generator across runs: %d. Distinct bootstrap frequency tables among runs that used the same algorithm and hyperparameters: %s." % (
            len(rng), "; ".join("%s: %d" % (k, len(v)) for k, v in bgroups.items())), ""]

        # stage matrices
        mats = [[np.array(r["lin"]["matrices"][s]) for s in STAGES] for r in runs]
        s0_same = len({m[0].tobytes() for m in mats})
        A["distinct_algorithm_outputs"] = s0_same
        L += ["**Graph by stage.** %d distinct algorithm outputs (S0) across %d runs." % (s0_same, n), "",
              "| Stage | Adjacent pairs | Agreement between runs on adjacent pairs (mean pairwise Jaccard) | Agreement on typed edges |", "|---|---|---|---|"]
        A["by_stage"] = {}
        for k, s in enumerate(STAGES):
            adjs = [adjacency(m[k]) for m in mats]
            typed = [typed_edges(m[k], names) for m in mats]
            ja, jt = mean_pairwise(adjs), mean_pairwise(typed)
            A["by_stage"][SHORT[k]] = {"adjacent_pairs": [len(x) for x in adjs], "jaccard_adjacency": ja, "jaccard_typed": jt}
            L.append("| %s | %s | %s | %s |" % (s, ms([len(x) for x in adjs], 1), "n/a" if ja is None else "%.2f" % ja, "n/a" if jt is None else "%.2f" % jt))
        L.append("")

        # LLM per-pair decisions
        dec = defaultdict(dict)
        for i, r in enumerate(runs):
            for row in r["lin"]["pairs"]:
                key = tuple(row["pair"])
                ans = []
                for x in row.get("llm_answers", []):
                    left, right = [t.strip() for t in x["asked_as"].strip("()").split(",", 1)]
                    ans.append("%s->%s" % (left, right) if x["letter"] == "A" else "%s->%s" % (right, left) if x["letter"] == "B" else x["letter"])
                dec[key][i] = "|".join(sorted(ans)) if ans else "(not asked)"
        unanimous = sum(1 for v in dec.values() if len(set(v.get(i, "(not asked)") for i in range(n))) == 1)
        modal = [Counter(v.get(i, "(not asked)") for i in range(n)).most_common(1)[0][1] / float(n) for v in dec.values()]
        edge_or_not = lambda s: "edge" if "->" in s else "no edge"
        unanimous_eo = sum(1 for v in dec.values() if len(set(edge_or_not(v.get(i, "")) for i in range(n))) == 1)
        letters = Counter(k for r in runs for k, c in r["lin"]["counts"]["llm_letters"].items() for _ in range(c))
        A["llm_decisions"] = {"pairs": len(dec), "unanimous": unanimous, "unanimous_edge_vs_no_edge": unanimous_eo,
                              "mean_modal_share": st.mean(modal) if modal else None, "letters": dict(letters)}
        L += ["**LLM review decisions.** %d pairs. Same decision in every run: %d. Same edge/no-edge call in every run: %d. Mean share of runs agreeing with the commonest decision for a pair: %s. Letters over all runs: %s." % (
            len(dec), unanimous, unanimous_eo, "n/a" if not modal else "%.2f" % st.mean(modal), ", ".join("%s %d" % kv for kv in sorted(letters.items()))), ""]

        # final edges
        fin = Counter()
        setby = Counter()
        llm_set_per_run, noadj_per_run, absent_per_run = [], [], []
        for r in runs:
            fe = r["lin"]["final_edges"]
            for e in fe:
                fin[e["edge"]] += 1
                setby[e["set_by"]] += 1
            llm_set_per_run.append(sum(1 for e in fe if e["set_by"] == "llm"))
            noadj_per_run.append(sum(1 for e in fe if not e["adjacent_in_algorithm_output"]))
            absent_per_run.append(r["lin"]["counts"]["llm_added_where_bootstrap_no_edge_frequency_ge_0.9"])
        A["final_edges"] = {"frequency": dict(fin), "set_by": dict(setby), "llm_set_per_run": llm_set_per_run,
                            "no_adjacency_in_algorithm_output_per_run": noadj_per_run,
                            "llm_added_against_bootstrap_absence_per_run": absent_per_run}
        L += ["**Final edges.** %d distinct edges appear in at least one run; %d appear in every run. Set by: %s. Per run: LLM-set edges %s; final edges between pairs the algorithm did not connect %s; LLM additions where at least 90%% of resamples had no edge %s." % (
            len(fin), sum(1 for v in fin.values() if v == n), ", ".join("%s %d" % kv for kv in setby.most_common()) or "none",
            ms(llm_set_per_run, 1), ms(noadj_per_run, 1), ms(absent_per_run, 1)), ""]
        if fin:
            L += ["| Final edge | Runs (of %d) |" % n, "|---|---|"] + ["| %s | %d |" % kv for kv in fin.most_common()] + [""]

        # accuracy by stage
        refs = {}
        if spec is not None:
            refs["by data"] = np.load(mdir / spec["reference_by_data"])
            if spec.get("reference_by_label") and spec["reference_by_label"] != spec["reference_by_data"]:
                refs["by label"] = np.load(mdir / spec["reference_by_label"])
        A["accuracy"] = {}
        if refs:
            for rname, R in refs.items():
                E = G.truth_edges(R)
                sc = [[G.score(m[k], E, p) for k in range(5)] for m in mats]
                if rname == "by data":
                    ok5 = all(abs((sc[i][k]["adj_f1"] or 0) - (runs[i]["lin"]["scores_by_stage"][STAGES[k]]["adj_f1"] or 0)) < 1e-12 and
                              sc[i][k]["shd_vs_true_cpdag"] == runs[i]["lin"]["scores_by_stage"][STAGES[k]]["shd_vs_true_cpdag"]
                              for i in range(n) for k in range(5))
                    A["T5"] = bool(ok5)
                    t5.append(ok5)
                A["accuracy"][rname] = {SHORT[k]: {m_: [s[k][m_] for s in sc] for m_ in METRICS} for k in range(5)}
        elif runs[0]["lin"].get("scores_by_stage"):
            A["accuracy"]["ground truth"] = {SHORT[k]: {m_: [r["lin"]["scores_by_stage"][STAGES[k]].get(m_) for r in runs] for m_ in METRICS} for k in range(5)}
        for rname, tab in A["accuracy"].items():
            L += ["**Accuracy by stage, scored %s** (mean ± sample s.d. over runs)." % ("against the " + rname if rname == "ground truth" else "against the reference graph read " + rname), "",
                  "| Stage | adj precision | adj recall | adj F1 | reference edges directed correctly | reversed | SHD vs CPDAG | directed-edge precision | recall | F1 |", "|---|---|---|---|---|---|---|---|---|---|"]
            for k in range(5):
                t = tab[SHORT[k]]
                L.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
                    STAGES[k], ms(t["adj_precision"]), ms(t["adj_recall"]), ms(t["adj_f1"]),
                    ms(t["true_edges_correctly_directed"], 1), ms(t["true_edges_reversed"], 1), ms(t["shd_vs_true_cpdag"], 1),
                    ms(t["dir_precision"]), ms(t["dir_recall"]), ms([0.0 if v is None else v for v in t["dir_f1"]])))
            L.append("")

        # name versus data (needs both references)
        if "by label" in refs:
            Rd, Rl = refs["by data"], refs["by label"]
            ad, al = {frozenset(x) for x in adjacency(Rd)}, {frozenset(x) for x in adjacency(Rl)}
            dd, dl = G.truth_edges(Rd), G.truth_edges(Rl)
            cls = Counter()
            dir_ok = Counter()
            distinct = defaultdict(set)
            for i, r in enumerate(runs):
                S1, S2, S4 = mats[i][1], mats[i][2], mats[i][4]
                for (c, e) in directed(S4):
                    if G.pair_type(S1, min(c, e), max(c, e)) == G.pair_type(S4, min(c, e), max(c, e)):
                        continue                                # not set by the LLM step or later
                    if G.pair_type(S2, min(c, e), max(c, e)) != G.pair_type(S4, min(c, e), max(c, e)):
                        continue                                # changed after the LLM step
                    k = frozenset((c, e))
                    kind = "both" if (k in ad and k in al) else "labels only" if k in al else "data only" if k in ad else "neither"
                    cls[kind] += 1
                    distinct[kind].add("%s->%s" % (names[c], names[e]))
                    if kind == "labels only":
                        dir_ok["labels: direction as in reference" if (c, e) in dl else "labels: reversed"] += 1
                    if kind == "data only":
                        dir_ok["data: direction as in reference" if (c, e) in dd else "data: reversed"] += 1
            A["name_vs_data"] = {"llm_set_final_edges": dict(cls), "direction": dict(dir_ok),
                                 "distinct_edges": {k: sorted(v) for k, v in distinct.items()}}
            L += ["**Do the LLM-set edges follow the labels or the data?** Every directed final edge that the LLM review set, over all runs, classified by which reference graph has that pair adjacent.", "",
                  "| Follows | Edges |", "|---|---|"] + ["| %s | %d |" % (k, cls.get(k, 0)) for k in ("labels only", "data only", "both", "neither")] + [
                  "", "Direction among those: %s." % (", ".join("%s %d" % kv for kv in sorted(dir_ok.items())) or "n/a"),
                  "Distinct edges: %s." % ("; ".join("%s: %s" % (k, ", ".join(sorted(v))) for k, v in sorted(distinct.items())) or "none"), ""]
        res["arms"][arm] = A

    gates["T3_same_dataset_bytes"] = all(t3) if t3 else "n/a"
    gates["T4_variable_names_match_arm"] = all(t4) if t4 else "n/a"
    gates["T5_scores_recomputed_equal_lineage"] = all(t5) if t5 else "n/a"
    gates["T6_one_model_snapshot_per_arm (report only)"] = all(t6) if t6 else "n/a"

    # predictions
    P = {}
    X = res["arms"]
    if "d03" in X and "name_vs_data" in X["d03"]:
        c = X["d03"]["name_vs_data"]["llm_set_final_edges"]
        lab, dat = c.get("labels only", 0), c.get("data only", 0)
        nn = lab + dat
        share = lab / float(nn) if nn else None
        P["P1"] = {"labels_only": lab, "data_only": dat, "share_following_labels": share,
                   "verdict": "INCONCLUSIVE" if nn < P1_N or share is None or P1_LO < share < P1_HI else "SUPPORTED" if share >= P1_HI else "REFUTED"}
    if "d01" in X and "d02" in X:
        m1, m2 = st.mean(X["d01"]["final_edges"]["llm_set_per_run"]), st.mean(X["d02"]["final_edges"]["llm_set_per_run"])
        P["P2"] = {"d01_mean_llm_set_edges": m1, "d02_mean_llm_set_edges": m2,
                   "verdict": "INCONCLUSIVE (d01 has none)" if m1 == 0 else "SUPPORTED" if m2 <= 0.5 * m1 else "REFUTED"}
    nd = [0, 0]
    dr = [0, 0]
    seen = set()
    for arm, runs in arms.items():
        for r in runs:
            S0, S1 = np.array(r["lin"]["matrices"][STAGES[0]]), np.array(r["lin"]["matrices"][STAGES[1]])
            key = (fr[arm][0], S0.tobytes(), S1.tobytes())
            if key in seen:                     # identical output and identical bootstrap result: one observation, not several
                continue
            seen.add(key)
            for (x, y) in adjacency(S0):
                tgt = dr if G.pair_type(S0, x, y) in ("a->b", "b->a") else nd
                tgt[0] += 1
                tgt[1] += int(G.is_adjacent(S1, x, y))
    if nd[0] or dr[0]:
        share = nd[1] / float(nd[0]) if nd[0] else None
        P["P3"] = {"distinct_outputs_counted": len(seen), "nondirected_edges_in_algorithm_output": nd[0], "of_which_still_adjacent_after_bootstrap_step": nd[1],
                   "share": share, "directed_edges": dr[0], "directed_still_adjacent": dr[1],
                   "verdict": "INCONCLUSIVE" if share is None or nd[0] < P3_N or P3_HI < share < P3_LO else "SUPPORTED" if share <= P3_HI else "REFUTED"}
    if "sachs" in X and "d01" in X and "by data" in X["sachs"]["accuracy"]:
        f = lambda k: st.mean(v or 0.0 for v in X[k]["accuracy"]["by data"]["S4"]["adj_f1"])
        P["P4"] = {"sachs_mean_final_adj_f1": f("sachs"), "d01_mean_final_adj_f1": f("d01"), "difference": f("sachs") - f("d01"), "verdict": "exploratory"}
    if X:
        P["P5"] = {"arms": len(X), "arms_with_more_than_one_algorithm": sum(1 for v in X.values() if len(v["algorithm"]) > 1), "verdict": "exploratory"}
    # ---- family-level predictions (bundle 1): thresholds are the constants at the top of this file
    fams = defaultdict(dict)
    for arm in X:
        fams[fr[arm][0]][fr[arm][1]] = arm
    lab_set, dat_set, nei_set = set(), set(), set()
    for fam, rl in fams.items():
        sw = rl.get("swapped")
        if sw and "name_vs_data" in X[sw]:
            de = X[sw]["name_vs_data"].get("distinct_edges", {})
            lab_set |= {(fam, e) for e in de.get("labels only", [])}
            dat_set |= {(fam, e) for e in de.get("data only", [])}
            nei_set |= {(fam, e) for e in de.get("neither", [])}
    if any("swapped" in rl for rl in fams.values()):
        nn = len(lab_set) + len(dat_set)
        share = len(lab_set) / float(nn) if nn else None
        P["N1"] = {"what": "swapped arms, distinct (family, edge): LLM-set final edges adjacent in exactly one reference",
                   "labels_only": len(lab_set), "data_only": len(dat_set), "neither": len(nei_set), "share_following_labels": share,
                   "verdict": "INCONCLUSIVE" if nn < P1_N or share is None or P1_LO < share < P1_HI else "SUPPORTED" if share >= P1_HI else "REFUTED"}
    n2 = {}
    for fam, rl in sorted(fams.items()):
        if "real" in rl and "neutral" in rl:
            m1 = st.mean(X[rl["real"]]["final_edges"]["llm_set_per_run"])
            m2 = st.mean(X[rl["neutral"]]["final_edges"]["llm_set_per_run"])
            n2[fam] = {"real": m1, "neutral": m2, "holds": (None if m1 == 0 else bool(m2 <= 0.5 * m1))}
    if n2:
        testable = [v for v in n2.values() if v["holds"] is not None]
        held = sum(1 for v in testable if v["holds"])
        P["N2"] = {"what": "mean LLM-set final edges per run, neutral names at most half of real names, per family",
                   "families": n2, "testable_families": len(testable), "held_in": held,
                   "verdict": "INCONCLUSIVE" if len(testable) < N2_MIN_FAMILIES else "SUPPORTED" if held == len(testable)
                   else "REFUTED" if held <= len(testable) / 2.0 else "INCONCLUSIVE"}
    below = total = 0
    by_role = defaultdict(lambda: {"S0": [], "S4": [], "S0_adj": [], "S4_adj": []})
    for arm, A_ in X.items():
        acc = A_["accuracy"].get("by data") or A_["accuracy"].get("ground truth")
        if not acc:
            continue
        for v0, v4 in zip(acc["S0"]["adj_f1"], acc["S4"]["adj_f1"]):
            total += 1
            below += int((v4 or 0.0) < (v0 or 0.0) - 1e-12)
        role = fr[arm][1]
        by_role[role]["S0"] += [v or 0.0 for v in acc["S0"]["dir_f1"]]
        by_role[role]["S4"] += [v or 0.0 for v in acc["S4"]["dir_f1"]]
        by_role[role]["S0_adj"] += [v or 0.0 for v in acc["S0"]["adj_f1"]]
        by_role[role]["S4_adj"] += [v or 0.0 for v in acc["S4"]["adj_f1"]]
    if total:
        share = below / float(total)
        P["N4"] = {"what": "runs whose final graph has lower adjacency F1 than the algorithm's own output",
                   "runs": total, "below": below, "share": share,
                   "verdict": "INCONCLUSIVE" if total < N4_N or N4_LO < share < N4_HI else "SUPPORTED" if share >= N4_HI else "REFUTED"}
        P["N5"] = {"what": "exploratory: mean F1 by role over all runs, scored against the data-side reference or ground truth",
                   "by_role": {r: {"runs": len(v["S4"]), "directed_edge_f1_algorithm_output": st.mean(v["S0"]), "directed_edge_f1_final": st.mean(v["S4"]),
                                   "adjacency_f1_algorithm_output": st.mean(v["S0_adj"]), "adjacency_f1_final": st.mean(v["S4_adj"])}
                               for r, v in sorted(by_role.items(), key=lambda kv: ROLE_ORDER.get(kv[0], 9))},
                   "verdict": "exploratory"}
    res["families"] = {f: dict(rl) for f, rl in fams.items()}
    res["predictions"], res["gates"] = P, gates

    L += ["## Predictions fixed before the data", ""]
    for k in sorted(P):
        L.append("- **%s**: %s" % (k, json.dumps(P[k], default=float)))
    L += ["", "## Gates", ""] + ["- %s: **%s**" % (k, "PASS" if v is True else "FAIL" if v is False else v) for k, v in gates.items()] + [""]
    if a.stub:
        L += ["This is a STUB self-test: the numbers above show that the tool runs and its checks behave as expected. They say nothing about Causal-Copilot's behaviour with a real model.", ""]
    (out / "stability.md").write_text("\n".join(L), encoding="utf-8")
    (out / "stability.json").write_text(json.dumps(res, indent=1, default=float), encoding="utf-8")
    print("\n".join(L))
    blocking = [k for k, v in gates.items() if v is False and "report only" not in k]
    sys.exit(1 if blocking else 0)


if __name__ == "__main__":
    main()
