"""Occurrence identity and explicit record constructors; DLV-08, DLV-09."""
import copy
import contextlib
import datetime
import uuid
import hashlib
import json
from pathlib import Path
from decimal import Decimal, InvalidOperation
from .codec import WireError

VERSION = "0.1.0-proposal.1"


def contract(name, version=VERSION):
    return {"name": name if "." in name else "s1." + name, "version": version}


def reference(target, target_type, binding="internal", **extra):
    return {"binding": binding, "target": target,
            "target_type": target_type if "." in target_type else "s1." + target_type, **extra}


def unresolved(reason="s1.not_observed", evidence=()):
    return {"state": "unresolved", "reasons": [reason], "evidence": list(evidence)}


def unknown_ref(target_type, reason="s1.unresolved_identity", evidence=(), labels=()):
    return {"binding": "unresolved", "target_type": target_type if "." in target_type else "s1." + target_type,
            "reason": reason, "evidence": list(evidence), "source_labels": list(labels)}


def known(value, basis=()):
    return {"state": "known", "value": copy.deepcopy(value), "basis": list(basis)}


def not_applicable(rule="s1.not_applicable", scope=()):
    return {"state": "not_applicable", "rule": contract(rule), "scope": list(scope)}


def number(value):
    """Preserve a supplied decimal lexeme, including negative zero. Never use float for validation."""
    if isinstance(value, bool):
        raise TypeError("boolean is not a numeric observation")
    text = str(value)
    try:val = Decimal(text)
    except InvalidOperation as exc:raise WireError('numeric field is not a supported numeric value; retain its native source') from exc
    if not val.is_finite():
        tag = "nan" if val.is_nan() else "negative_infinity" if val.is_signed() else "positive_infinity"
        return {"number_type": "nonfinite", "value": tag}
    import re
    if re.fullmatch(r'-?(0|[1-9][0-9]*)(\.[0-9]+)?([eE][+-]?[0-9]+)?',text) is None:
        raise WireError('numeric lexeme is outside the SC-1 decimal contract; retain its native source')
    return {"number_type": "integer" if isinstance(value, int) else "finite_decimal", "text": text}


def scope(*subjects):
    return {"subjects": list(subjects), "qualifiers": []}


def source(basis="intrinsic", evidence=(), procedure=None, inputs=()):
    return {"basis": basis, "evidence": list(evidence), "procedure": known(procedure) if procedure else unresolved(),
            "inputs": list(inputs)}


def index(members=(), extent="complete_for_scope", subjects=(), gaps=()):
    return {"members": list(members), "extent": extent, "scope": scope(*subjects), "gaps": list(gaps)}


class Builder:
    """Staged records; all access returns copies so callers cannot mutate an established snapshot."""

    def __init__(self, name="connection observer", component_id=None, package_id=None):
        self.package_id = package_id or str(uuid.uuid4())
        self.component_id = component_id or str(uuid.uuid4())
        self._records = {}
        self.producer = reference(self.component_id, "component")
        implementation_id=str(uuid.uuid4())
        implementation_ref=reference(implementation_id,"artifact_snapshot")
        self.add("component", {"name": name, "role": "s1.observer", "version": known(VERSION),
                              "implementation": known({"artifact":implementation_ref,"selector":known({"selector_type":"json_pointer","pointer":""})}), "configuration": unresolved(),
                              "source": source()}, record_id=self.component_id)
        directory=Path(__file__).resolve().parent
        files=sorted(directory.rglob("*.py"))+sorted(directory.glob("*.schema.json"))+[directory/"requirements.txt"]
        identity={p.relative_to(directory).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files if p.is_file()}
        self.add("artifact_snapshot",{"content":{"content_form":"inline_utf8","text":json.dumps(identity,sort_keys=True)},
                 "format":known(contract("code_identity_manifest")),"capture_scope":{"kind":"full_content"},
                 "source_span":unresolved(),"native_capture_extent":"s1.full_for_interface","locations":[],
                 "digest_claims":[],"source":source("intrinsic")},record_id=implementation_id)

    def add(self, kind, payload, record_id=None, producer=None):
        kind = kind if "." in kind else "s1." + kind
        rid = record_id or str(uuid.uuid4())
        if rid in self._records:
            raise ValueError("record identity already exists: " + rid)
        now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")
        record = {"id": rid, "record_type": kind, "contract": contract(kind), "producer": producer or self.producer,
                  "created_at": known({"time_type": "utc_instant", "value": now, "precision": "fractional_second",
                                       "clock": known(self.producer), "uncertainty_seconds": unresolved("s1.not_computed")}),
                  "payload": copy.deepcopy(payload), "extensions": []}
        self._records[rid] = record
        return reference(rid, kind)

    def get(self, ref):
        return copy.deepcopy(self._records[ref["target"]])

    @contextlib.contextmanager
    def transaction(self):
        previous=set(self._records)
        try:yield self
        except Exception:
            for rid in set(self._records)-previous:del self._records[rid]
            raise

    def package(self, roots, external_packages=(), extensions=()):
        return copy.deepcopy({"format": contract("connection_package"), "package_id": self.package_id,
                              "roots": list(roots), "records": list(self._records.values()),
                              "external_packages": list(external_packages), "extensions": list(extensions)})

    def output(self, output_type, body, subjects=(), role="s1.native_answer", evidence=(),
               native_producer=None, designation=None, relations=(), checks=()):
        return self.add("output", {"output_type": output_type,
                                  "native_producer": native_producer or unknown_ref("component"),
                                  "subjects": list(subjects), "role": known(role), "designation": designation or unresolved(),
                                  "body": body, "source": source("reconstructed", evidence, self.producer),
                                  "relations": list(relations), "checks": list(checks)})
