"""The certificate (protocol v1, section 1.7) and its verification.

certificate.json = {"body": {...}, "sha256": sha256(canonical body)}; the body holds the protocol identity, the system
identity and capabilities, the battery identity and hash, the regimes, the run manifest (every raw file with its sha256)
and its hash, EVERY number of the report keyed by its JSON pointer in report.json with the function that derived it, the
findings with verdicts and labels, the environment, and the rerun command.

verify(cert) recomputes the audit from the raw files and checks: the body hash; every raw file's sha256 against the
manifest; every number (counts exact; floats within 1e-9 on the same host, 0.001 across hosts); every verdict.
"""
import json
from pathlib import Path

from ..core.canon import canon, sha256_bytes, sha256_file, sha256_obj
from ..core.evidence import pointer
from ..core.paths import ROOT

DERIVATION = {"l0": "crucis_causal.metrics.l0.summarise_arm (via crucis_causal.collect.l0_table)",
              "l1/names": "crucis_causal.controls.l1.name_effects", "l1/layout": "crucis_causal.controls.l1.layout_effect",
              "l1/data_only": "crucis_causal.controls.l1.data_only_effect", "l2": "crucis_causal.findings.stage_effects",
              "findings": "crucis_causal.findings.evaluate"}
SAME_HOST_TOL, CROSS_HOST_TOL = 1e-9, 0.001


def numbers(result):
    """{json pointer: number} over the report sections that hold results (l0, l1, l2, findings)."""
    out = {}

    def walk(x, path):
        if isinstance(x, bool) or x is None or isinstance(x, str):
            return
        if isinstance(x, (int, float)):
            out[pointer(*path)] = x
        elif isinstance(x, dict):
            for k, v in x.items():
                walk(v, path + [k])
        elif isinstance(x, (list, tuple)):
            for i, v in enumerate(x):
                walk(v, path + [i])
    for sec in ("l0", "l1", "l2"):
        walk(result.get(sec), [sec])
    for i, f in enumerate(result["findings"]):
        walk(f.get("effect"), ["findings", i, "effect"])
    return out


def derivation_of(ptr):
    for pre in ("l1/names", "l1/layout", "l1/data_only", "l0", "l2", "findings"):
        if ptr.startswith("/" + pre):
            return DERIVATION[pre]
    return None


def make(result, rerun_command):
    nums = numbers(result)
    body = {"certificate_format": "audit-certificate/1", "audit": result["audit"], "spec": result["spec"],
            "protocol": result["protocol"],
            "system": result["system"], "battery": result["battery"], "regimes": result["regimes"],
            "runs": result["runs"], "runs_manifest_sha256": result["runs_manifest_sha256"],
            "numbers": {p: {"value": v, "derivation": derivation_of(p)} for p, v in sorted(nums.items())},
            "findings": [{"id": f["id"], "kind": f["kind"], "verdict": f["verdict"], "label": f["label"],
                          "point": (f.get("effect") or {}).get("point"), "lo": (f.get("effect") or {}).get("lo"),
                          "hi": (f.get("effect") or {}).get("hi"), "reason": f.get("reason")} for f in result["findings"]],
            "environment": result["environment"], "rerun": rerun_command,
            "evidence_rule": "every number is recomputed from the files in runs[] by `rerun`; numbers are keyed by their "
                             "JSON pointer in report.json"}
    return {"body": body, "sha256": sha256_bytes(canon(body))}


def write(cert, path):
    Path(path).write_text(json.dumps(cert, indent=1, sort_keys=True, default=str), encoding="utf-8")
    Path(str(path) + ".sha256").write_text(cert["sha256"] + "\n", encoding="utf-8")


def verify(cert, recompute):
    """cert: the certificate dict; recompute(name, spec) -> a fresh audit result from the raw files, with the spec the
    certificate stores (the round context of K03 included)."""
    body = cert["body"]
    out = {"hash_ok": sha256_bytes(canon(body)) == cert["sha256"], "files_changed": [], "number_mismatches": [],
           "verdict_changes": []}
    for r in body["runs"]:
        for role, f in (r.get("files") or {}).items():
            p = ROOT / f["path"]
            if not p.exists() or sha256_file(p) != f["sha256"]:
                out["files_changed"].append(f["path"])
    fresh = recompute(body["audit"], body["spec"])
    same_host = fresh["environment"] == body["environment"]
    tol = SAME_HOST_TOL if same_host else CROSS_HOST_TOL
    now = numbers(fresh)
    for p, rec in body["numbers"].items():
        v = now.get(p)
        exact = isinstance(rec["value"], int)
        bad = v is None or (abs(v - rec["value"]) > (0 if exact else tol))
        if bad:
            out["number_mismatches"].append({"pointer": p, "certified": rec["value"], "recomputed": v})
    extra = sorted(set(now) - set(body["numbers"]))
    for a, b in zip(body["findings"], fresh["findings"]):
        if a["verdict"] != b["verdict"]:
            out["verdict_changes"].append({"id": a["id"], "certified": a["verdict"], "recomputed": b["verdict"]})
    out.update({"numbers_compared": len(body["numbers"]), "numbers_not_in_certificate": extra, "tolerance": tol,
                "same_host": same_host})
    out["pass"] = (out["hash_ok"] and not out["files_changed"] and not out["number_mismatches"] and not out["verdict_changes"]
                   and not extra)
    return out
