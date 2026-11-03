"""Audit report: report.json (the full result), report.md (for people), certificate.json (+ .sha256).

Every number in report.md is read from report.json; nothing is typed in. A ranking across regimes is refused (rule R1):
the L0 table lists each arm with its regime, and controls appear only as findings.
"""
import json
from pathlib import Path

from ..protocol import regimes as R, tiers as T
from . import certificate as CERT


def fmt(x, nd=3):
    if x is None:
        return "-"
    if isinstance(x, float):
        return ("%." + str(nd) + "f") % x
    return str(x)


def eff_text(e):
    if not e:
        return "-"
    if "k" in e and "n" in e and e.get("point") is not None:
        return "%d of %d runs: %s [%s, %s]" % (e["k"], e["n"], fmt(e["point"]), fmt(e["lo"]), fmt(e["hi"]))
    if "ratio" in e or ("coverage" in e and "precision" in e):
        return _special(e)
    if e.get("point") is not None:
        s = fmt(e["point"])
        if e.get("lo") is not None:
            s += " [%s, %s]" % (fmt(e["lo"]), fmt(e["hi"]))
        if e.get("units") is not None:
            s += ", %s units" % e["units"]
        return s
    return _counts(e)


def _special(e):
    if "ratio" in e:
        return "USD/run %s vs round median %s: ratio %s" % (fmt(e.get("usd_per_run")), fmt(e.get("round_median")), fmt(e.get("ratio"), 2))
    if "coverage" in e and "precision" in e:
        return "coverage %s, precision %s (%s committed claims, %s arm)" % (fmt(e["coverage"]), fmt(e["precision"]), e.get("committed"), e.get("arm"))
    return "-"


def _counts(e):
    keys = [k for k in ("k", "n", "labels_only", "data_only", "right_to_wrong", "wrong_to_right", "unsourced", "committed") if k in e]
    return ", ".join("%s %s" % (k.replace("_", " "), fmt(e[k])) for k in keys) or "-"


def markdown(r):
    L = ["# Audit: %s" % r["audit"], "",
         "Protocol v%s (thresholds %s, sha256 %s...). Battery `%s` v%s (%s, %d items, %d scenario clusters; hash %s...)."
         % (r["protocol"]["version"], r["protocol"]["thresholds_version"], r["protocol"]["thresholds_sha256"][:12],
            r["battery"]["id"], r["battery"]["version"], r["battery"]["visibility"], r["battery"]["items"],
            r["battery"]["clusters"], r["battery"]["hash"][:12]), "",
         "System: `%s`; adapter %s v%s; takes %s; gives marks %s%s." % (
             r["system"]["id"], r["system"]["identity"]["adapter"], r["system"]["identity"]["adapter_version"],
             ", ".join(r["system"]["capabilities"]["takes"]), " ".join(r["system"]["capabilities"]["marks"]),
             "; per-edge source exposed" if r["system"]["capabilities"]["edge_source"] else ""), "",
         "## L0: what it gets right (per arm; compare a row only with rows of the same regime)", "",
         "| Arm | Regime | Runs | ok | Completion | Directed F1 (expectation rule, completed) | same, delivered | Adjacency F1 | DV-1 precision | DV-1 coverage | USD |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for arm, t in r["l0"].items():
        dv = t.get("dv1") or {}
        L.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            arm, r["regimes"][arm]["regime"], t["runs"], t["ok"], fmt(t["completion"]), fmt(t["dir_f1@expect"]),
            fmt(t["dir_f1@expect_delivered"]), fmt(t["adj_f1"]), fmt(dv.get("precision")), fmt(dv.get("coverage")), fmt(t["usd"], 2)))
    words = {t.get("word") for t in r["l0"].values()} - {None}
    L += ["", "References are %s (tier T1: %s), so these numbers are %s." % (
        "simulated graphs", T.TIERS["T1"], " / ".join(sorted(words)) or "accuracy"), ""]
    L += ["## Findings (closed list, protocol v1)", "",
          "| ID | Kind | Verdict | Effect [95% interval] | Label | Note |", "|---|---|---|---|---|---|"]
    for f in r["findings"]:
        note = f.get("reason") or (("stage %s" % f["stage"]) if f.get("stage") else "") or (
            ("measured on %s" % f["measured_on"]) if f.get("measured_on") not in (None, "final") else "")
        L.append("| %s | %s | **%s** | %s | %s | %s |" % (f["id"], f["kind"], f["verdict"], eff_text(f.get("effect")),
                                                         f["label"].split(" (")[0], note))
    if r.get("l2"):
        L += ["", "## L2: what each stage does (real names)", "", "| Stage | Adjacency F1 change [95%] | Right->wrong | Wrong->right |",
              "|---|---|---|---|"]
        for t in r["l2"]["transitions"].get("real") or next(iter(r["l2"]["transitions"].values())):
            L.append("| %s | %s | %s | %s |" % (t["stage"], eff_text(t["adj"]), t["flips"]["right_to_wrong"], t["flips"]["wrong_to_right"]))
    gaps = [f for f in r["findings"] if f["verdict"] in ("not_checkable", "not_run")]
    L += ["", "## Typed gaps (what this audit could not say, and why)", ""]
    L += ["- %s %s: %s, %s" % (f["id"], f["kind"], f["verdict"].replace("_", " "), f.get("reason") or "") for f in gaps]
    L += ["", "Exploratory labels: the kind's threshold was registered on 2026-10-30, after these runs; such a finding is "
              "confirmatory only for runs recorded after thresholds_v1.json was hashed.", "",
          "Runs: %d recorded runs (manifest sha256 %s...). Recompute everything: `%s`." % (
              len(r["runs"]), r["runs_manifest_sha256"][:12], r.get("rerun", "python -m crucis audit %s" % r["audit"]))]
    return "\n".join(L) + "\n"


def write(result, out_dir, rerun_command=None):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    rerun_command = rerun_command or "python -m crucis audit %s --out <dir>" % result["audit"]
    result = dict(result, rerun=rerun_command)
    for arm in result["l0"]:
        if result["regimes"][arm]["regime"] not in R.REGIMES:
            raise ValueError("unknown regime")
    (out / "report.json").write_text(json.dumps(result, indent=1, default=str, sort_keys=True), encoding="utf-8")
    (out / "report.md").write_text(markdown(result), encoding="utf-8")
    cert = CERT.make(result, rerun_command)
    CERT.write(cert, out / "certificate.json")
    return {"report": str(out / "report.json"), "markdown": str(out / "report.md"), "certificate": str(out / "certificate.json"),
            "certificate_sha256": cert["sha256"]}


def ranking(rows):
    """A table that ranks systems: refused when it mixes regimes (rule R1)."""
    R.check_comparable(rows)
    return sorted(rows, key=lambda r: -(r.get("score") or 0))
