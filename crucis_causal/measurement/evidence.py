"""Bind observed journal work to explicit S4 calculation and result roles."""

from dataclasses import dataclass
from hashlib import sha256
import json
from types import MappingProxyType

from crucis_causal.execution.api import supplied_read

from .codec import VERSION, Snapshot, dumps, inspect
from .planning import plan
from .resolution import ResolutionError, resolve


def _contract(name):
    return {"name": name, "version": VERSION}


def _local(target, kind):
    return {"ref_kind": "local", "target_id": target, "expected_contract": _contract("s4." + kind)}


def _record(ident, kind, payload):
    name = "s4." + kind
    return {"id": ident, "kind": name, "contract": _contract(name), "payload": payload}


@dataclass(frozen=True, slots=True)
class RecordedMeasurement:
    snapshot: Snapshot
    view: object
    calculation: dict
    results: tuple[str, ...]


class _Dependencies:
    def __init__(self, original, journal):
        self._raw = {original.snapshot.snapshot_id: original.snapshot.source_bytes,
                     journal.package_id: journal.source_bytes}
        for pid, raw in original._supplied.items():
            if original._access.permits(pid):
                if pid in self._raw and self._raw[pid] != raw:
                    raise ResolutionError("recording_dependency_conflict")
                self._raw[pid] = raw
        self.entries = {}

    def reference(self, package_id, record_id, expected_contract, selector=None):
        raw = self._raw.get(package_id)
        if raw is None:
            raise ResolutionError("recording_dependency_unavailable")
        if package_id not in self.entries:
            key = "dep." + str(len(self.entries))
            self.entries[package_id] = {
                "key": key, "package_id": package_id, "format": json.loads(raw)["format"],
                "pin": {"algorithm": "sha256", "digest": sha256(raw).hexdigest(),
                        "length": str(len(raw)), "extent": {"extent_kind": "whole"}},
            }
        reference = {"ref_kind": "external", "dependency_key": self.entries[package_id]["key"],
                     "target_id": record_id, "expected_contract": expected_contract}
        if selector is not None:
            reference["selector"] = selector
        return reference

    def selected(self, record):
        return self.reference(record.package_id, record.record_id, record.contract)

    @property
    def supplied(self):
        return MappingProxyType(self._raw)


def _bind_outcome(value, reader, dependencies, anchor):
    if isinstance(value, list):
        return [_bind_outcome(item, reader, dependencies, anchor) for item in value]
    if not isinstance(value, dict):
        return value
    if value.get("ref_kind") in ("local", "external"):
        selected = reader.read(value, anchor)
        return dependencies.reference(selected.package_id, selected.record_id,
                                      selected.contract, value.get("selector"))
    if value.get("ref_kind") == "artifact":
        reader.read(value, anchor)
    return {key: _bind_outcome(item, reader, dependencies, anchor) for key, item in value.items()}


def materialize_recorded(plan_reference, original, registry, coordinator, invocation, basis, snapshot_id):
    """Create a new exact snapshot from actual committed work evidence."""
    prepared = plan(plan_reference, original, registry)
    if not prepared.outputs or prepared.basis_digest != basis:
        raise ResolutionError("recording_plan_basis_unestablished")
    recovery = coordinator.recover(invocation, basis)
    if recovery.state != "recorded":
        raise ResolutionError("recorded_work_unavailable")
    event = json.loads(recovery.event_bytes)
    pinned = event["plan_evidence"]["plan"]
    recorded_plan = prepared.plan_record
    if pinned != {"package_id": recorded_plan.package_id, "digest": recorded_plan.package_digest,
                  "record_id": recorded_plan.record_id}:
        raise ResolutionError("recorded_plan_pin_mismatch")
    journal = recovery.evidence_view
    dependencies = _Dependencies(original, journal)
    journal_record = next(row for row in journal.records if row["id"] == recovery.evidence_record_id)
    work = dependencies.reference(journal.package_id, journal_record["id"], journal_record["contract"])
    observer_id = journal_record["producer"]["target"]
    observer = next(row for row in journal.records if row["id"] == observer_id)
    observer_ref = dependencies.reference(journal.package_id, observer_id, observer["contract"])
    reader = original.reader()
    audience = dependencies.selected(reader.read(original.snapshot.package["audience"]))
    records = [
        _record("account", "account", {"observer": observer_ref, "sources": [_local("work", "source")]}),
        _record("work", "source", {"subject": recovery.occurrence_id, "attribution": observer_ref,
                                    "extent": "complete", "observations": [work], "basis": [work]}),
    ]
    procedure = reader.read(recorded_plan.value["payload"]["procedure"], recorded_plan.package_id)
    planned, observed, result_ids = [], [], []
    by_key = {item["key"]: item["outcome"] for item in event["emissions"]}
    if len(by_key) != len(event["emissions"]) or set(by_key) - {item.key for item in prepared.outputs}:
        raise ResolutionError("recorded_output_scope")
    for output in sorted(prepared.outputs, key=lambda item: item.key):
        binding, scope = dependencies.selected(output.binding), dependencies.selected(output.scope)
        position = {"key": output.key, "binding": binding, "output_role": output.output_role,
                    "subject_key": output.subject_key}
        planned.append({**position, "scope": scope})
        if output.key not in by_key:
            continue
        result_id = "val." + sha256(output.key.encode("utf-8")).hexdigest()
        result_ids.append(result_id)
        observed.append({**position, "result": _local(result_id, "result")})
        premises = []
        for i, assessment in enumerate(output.premises):
            premises.append({"key": f"assessment.{i:05}", "assessment": dependencies.selected(assessment)})
        records.append(_record(result_id, "result", {
            "binding": binding, "output_role": output.output_role, "subject_key": output.subject_key,
            "scope": scope, "origin": {"origin_kind": "computed", "calculation": _local("calc", "calculation"),
                                     "emission_key": output.key},
            "premises": premises,
            "outcome": _bind_outcome(by_key[output.key], reader, dependencies, output.binding.package_id),
        }))
    records.append(_record("calc", "calculation", {
        "invocation_id": "run." + sha256(invocation.encode("utf-8")).hexdigest(),
        "plan": dependencies.selected(recorded_plan), "procedure": dependencies.selected(procedure),
        "basis": [work], "work_state": event["state"],
        "extent": "complete" if event["state"] == "completed" else "partial" if observed else "known_empty",
        "planned": planned, "emissions": observed, "observations": [work],
    }))
    package = {
        "format": original.snapshot.package["format"], "account_id": original.snapshot.account_id,
        "snapshot_id": snapshot_id, "audience": audience,
        "frontier": [{"key": "recorded-work", "position": work}],
        "roots": [_local("account", "account")],
        "records": sorted(records, key=lambda record: record["id"]),
        "dependencies": sorted(dependencies.entries.values(), key=lambda row: row["key"]),
    }
    snap = inspect(dumps(package, original.limits), original.limits)
    supplied = dependencies.supplied
    access = supplied_read({snap.snapshot_id, *supplied})
    return RecordedMeasurement(snap, resolve(snap, supplied, access, original.limits),
                               _local("calc", "calculation"), tuple(result_ids))
