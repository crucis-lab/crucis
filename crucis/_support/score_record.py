"""The score contract (EVL-01, EVL-02, EVL-03): what every reported score must state.

Every directory under analysis/results/ carries a CONTRACT.json. Score rows written by new code also carry the per-row fields
below (use `row(...)`), and `check_scores.py` rejects any results directory or row that does not state them.

Regime (EVL-01): what information the method was given.
  D       data only (observational rows)
  D+I     data plus interventional rows with their targets
  D+K     data plus knowledge: variable names, declared tiers, an LLM reading names, or oracle order from the true graph
  D+I+K   both
Controls (EVL-02): columns_shuffled (true/false/"per-row"), names ("real", "neutral", "swapped", "synthetic", "per-row"),
  supplier (who produced the data: "causalarena", "repo", "uci", "causal_chambers", "ours"), knowledge_source when K is present.
Metrics (EVL-03): every metric name used must be defined in metric_defs (with the SHD variant and the orientation rule for
  undecided pairs where they apply).
"""
import json

REGIMES = {"D", "D+I", "D+K", "D+I+K"}
NAMES = {"real", "neutral", "swapped", "synthetic", "per-row", "not applicable", "decoupled (rho dial)"}  # last: AB-08 benchmark (2026-10-13)
SPLITS = {"dev", "test", "all-public (measurement, no tuning)", "per-row", "not applicable"}
STANDARD_METRICS = {
    "directed_f1": "F1 over directed edges; undecided pairs turned into predictions by the stated orientation rule",
    "directed_precision": "precision over directed edges, same rule",
    "directed_recall": "recall over directed edges, same rule",
    "adjacency_f1": "F1 over unordered adjacencies (edge type ignored)",
    "skeleton_precision": "precision over unordered adjacencies",
    "skeleton_recall": "recall over unordered adjacencies",
    "direction_accuracy": "share of committed directions (true adjacencies only) that match the truth",
    "shd": "structural Hamming distance; the variant must be named in shd_variant",
    "coverage": "share of true edges for which a claim (adjacency or direction) was made",
    "calibration_error": "expected calibration error of stated confidences, 10 equal-width bins",
    "interventional_error": "mean absolute error of predicted interventional means",
    "cost_usd": "API cost of the run", "seconds": "wall time",
}
REQUIRED_CONTRACT = ("tickets", "producer", "score_bearing")
REQUIRED_IF_SCORES = ("regime", "controls", "split", "metric_defs")


def check_contract(c):
    """Return a list of problems with one CONTRACT.json. A directory mixing regimes declares them per file under "per_file";
    each entry is checked as a contract of its own, with the directory-level fields as defaults."""
    if c.get("per_file"):
        base = {k: v for k, v in c.items() if k != "per_file"}
        out = []
        for f, spec in c["per_file"].items():
            merged = dict(base, **spec)
            merged["controls"] = dict(base.get("controls", {}), **spec.get("controls", {}))
            out += ["%s: %s" % (f, x) for x in check_contract(merged)]
        return out
    p = [k for k in REQUIRED_CONTRACT if k not in c]
    if c.get("score_bearing"):
        p += [k for k in REQUIRED_IF_SCORES if k not in c]
        if "regime" in c and c["regime"] not in REGIMES | {"per-row"}:
            p.append("regime %r not one of %s" % (c["regime"], sorted(REGIMES)))
        ctl = c.get("controls", {})
        for k in ("columns_shuffled", "names", "supplier"):
            if k not in ctl:
                p.append("controls.%s missing" % k)
        if ctl.get("names") not in NAMES and "names" in ctl:
            p.append("controls.names %r not one of %s" % (ctl.get("names"), sorted(NAMES)))
        if "+K" in str(c.get("regime")) and not ctl.get("knowledge_source"):
            p.append("regime includes K but controls.knowledge_source is missing")
        if c.get("split") not in SPLITS and "split" in c:
            p.append("split %r not one of %s" % (c.get("split"), sorted(SPLITS)))
        md = c.get("metric_defs", {})
        if not md:
            p.append("metric_defs empty")
        if any("shd" in k.lower() for k in md) and not c.get("shd_variant"):
            p.append("an SHD metric is reported but shd_variant is not named")
        if any("directed" in k.lower() for k in md) and not c.get("orientation_rule"):
            p.append("a directed metric is reported but orientation_rule is not named")
    return p


def row(*, ticket, family, scenario, method, regime, columns_shuffled, names, supplier, split, metrics, knowledge_source=None,
        file=None, replicate=None, env=None, **extra):
    """One score row for new result files. Raises ValueError if it does not satisfy the contract."""
    r = {"contract": "v1", "ticket": ticket, "family": family, "scenario": scenario, "file": file, "replicate": replicate,
         "method": method, "regime": regime, "controls": {"columns_shuffled": columns_shuffled, "names": names, "supplier": supplier,
                                                          "knowledge_source": knowledge_source},
         "split": split, "metrics": metrics, "env": env}
    r.update(extra)
    problems = check_row(r)
    if problems:
        raise ValueError("; ".join(problems))
    return r


def check_row(r, metric_defs=None):
    p = []
    if r.get("regime") not in REGIMES:
        p.append("row regime %r" % r.get("regime"))
    if "+K" in str(r.get("regime")) and not (r.get("controls") or {}).get("knowledge_source"):
        p.append("row regime has K but no knowledge_source")
    if (r.get("controls") or {}).get("names") not in NAMES:
        p.append("row names %r" % (r.get("controls") or {}).get("names"))
    if r.get("split") not in SPLITS:
        p.append("row split %r" % r.get("split"))
    unknown = [m for m in (r.get("metrics") or {}) if m not in STANDARD_METRICS and not (metric_defs and m in metric_defs)]
    if unknown:
        p.append("undefined metrics %s" % unknown)
    return p
