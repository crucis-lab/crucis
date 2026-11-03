"""Protocol v1: the closed list of finding kinds (section 1.5 of crucis/PROTOCOL.md). Thresholds live in thresholds_v1.json
and are hashed into every report; this file holds what each kind means. A finding whose kind is not in KINDS is refused.

registered: the date its threshold was fixed. "2026-10-14" kinds were hashed before the AB-06 grid ran
(plans/ab06_prereg.json); "2026-10-30" kinds were set after the existing results were known, so on those results they are
exploratory, and confirmatory only for systems or rounds run after thresholds_v1.json was hashed.
"""
import json
from pathlib import Path

from ..core.canon import sha256_obj

VERSION = "1.0"
HERE = Path(__file__).resolve().parent
VERDICTS = ("fires", "clear", "inconclusive", "not_checkable", "not_run")

KINDS = [
    {"id": "K01", "kind": "crash", "level": "L0", "control": "none",
     "statistic": "failed runs / executed runs (infrastructure statuses excluded), Wilson 95% interval",
     "registered": "2026-10-30"},
    {"id": "K02", "kind": "no_better_than_null", "level": "L0", "control": "system vs the empty graph on the same files",
     "statistic": "paired difference in DV-1 precision (system - empty graph), scenario-cluster bootstrap", "registered": "2026-10-30"},
    {"id": "K03", "kind": "cost_outlier", "level": "L0", "control": "systems of one round, same battery and regime",
     "statistic": "USD per executed run / median USD per executed run of the round's LLM systems", "registered": "2026-10-30"},
    {"id": "K04", "kind": "name_reliance", "level": "L1", "control": "names real vs swapped, same data",
     "statistic": "paired mean F1(real) - F1(swapped) by scenario (P9's statistic)", "registered": "2026-10-14"},
    {"id": "K05", "kind": "wrong_knowledge_harm", "level": "L1", "control": "names neutral vs swapped",
     "statistic": "paired mean F1(neutral) - F1(swapped) by scenario", "registered": "2026-10-30"},
    {"id": "K06", "kind": "layout_reliance", "level": "L1", "control": "columns released vs shuffled; path plain vs opaque",
     "statistic": "paired mean difference (released - shuffled) of the metric by scenario cluster", "registered": "2026-10-30"},
    {"id": "K07", "kind": "knowledge_degrades_data", "level": "L1",
     "control": "final graph vs the system's own data-only variant (black box: the knowledge-off arm)",
     "statistic": "pooled DV-1 precision final - data-only, real names (P10's statistic); rows: B5 classes I5/I3",
     "registered": "2026-10-14"},
    {"id": "K08", "kind": "robustness_drop", "level": "L1", "control": "sample size / noise / mechanism family transform",
     "statistic": "paired mean F1(base) - F1(transformed)", "registered": "2026-10-30"},
    {"id": "K09", "kind": "knowledge_ignored", "level": "L1", "control": "oracle supplier vs none",
     "statistic": "paired mean F1(oracle) - F1(none)", "registered": "2026-10-30"},
    {"id": "K10", "kind": "stage_deletes_supported_links", "level": "L2", "control": "a stage's output vs its input",
     "statistic": "paired mean adjacency F1 (stage out - stage in) over runs, per stage", "registered": "2026-10-30"},
    {"id": "K11", "kind": "stage_follows_names", "level": "L2",
     "control": "swapped names: pairs a stage set, against the T1 reference (data) and the T4 reference (labels)",
     "statistic": "distinct (family, edge) adjacent only in the label reference vs only in the data reference",
     "registered": "2026-10-30"},
    {"id": "K12", "kind": "stage_flips_data_direction", "level": "L2",
     "control": "a stage's input vs output on true adjacencies the input had committed",
     "statistic": "right-to-wrong minus wrong-to-right direction flips, sign test", "registered": "2026-10-30"},
    {"id": "K13", "kind": "unsourced_claims", "level": "L3-lite", "control": "none",
     "statistic": "committed arrows with no exposed source / committed arrows (B5 class G4)", "registered": "2026-10-30"},
    {"id": "K14", "kind": "overconfident", "level": "calibration", "control": "stated confidence vs realised precision",
     "statistic": "expected calibration error (10 equal-width bins) and mean confidence - precision", "registered": "2026-10-30"},
    {"id": "K15", "kind": "never_abstains", "level": "L0", "control": "none",
     "statistic": "DV-1 coverage and DV-1 precision, pooled", "registered": "2026-10-30"},
]
BY_ID = {k["id"]: k for k in KINDS}
BY_KIND = {k["kind"]: k for k in KINDS}


def thresholds():
    return json.loads((HERE / "thresholds_v1.json").read_text(encoding="utf-8"))


def protocol_identity():
    th = thresholds()
    return {"version": VERSION, "kinds_sha256": sha256_obj(KINDS), "thresholds_sha256": sha256_obj(th),
            "thresholds_version": th["version"]}


def label(kind_id, runs_date=None):
    """confirmatory if the kind's threshold was registered before the runs it judges; exploratory otherwise.
    runs_date: 'YYYY-MM-DD' (the runs started that day) or '<=YYYY-MM-DD' (they were all recorded by that day)."""
    reg = BY_ID[kind_id]["registered"]
    if not runs_date:
        return "unknown"
    if runs_date.startswith("<="):
        return "exploratory (threshold set after the data)" if runs_date[2:] <= reg else "unknown"
    return "confirmatory" if runs_date >= reg else "exploratory (threshold set after the data)"
