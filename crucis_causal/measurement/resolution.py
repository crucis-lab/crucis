"""Capability-checked reads from exact caller-supplied measurement evidence."""

from collections.abc import Mapping
from dataclasses import dataclass
from hashlib import sha256
import json
from types import MappingProxyType

from crucis_causal.connections.validation import content_bytes
from crucis_causal.execution.api import ReadCapability
from crucis_causal.execution.codec import loads, parse_snapshot
from crucis_causal.execution.model import ExecutionError, canonical

from .codec import FORMAT, Limits, Snapshot, WireError, check_reference, inspect


@dataclass(frozen=True, slots=True)
class Issue:
    code: str
    scope: str = ""


class ResolutionError(ValueError):
    def __init__(self, code, scope=""):
        self.issue = Issue("s4." + code.removeprefix("s4."), scope)
        super().__init__(self.issue.code)


@dataclass(frozen=True, slots=True)
class ResolvedRecord:
    package_id: str
    package_digest: str
    record_id: str
    contract_bytes: bytes
    selected_bytes: bytes

    @property
    def contract(self):
        return json.loads(self.contract_bytes)

    @property
    def value(self):
        return json.loads(self.selected_bytes)


@dataclass(frozen=True, slots=True)
class ResolvedArtifact:
    package_id: str
    package_digest: str
    record_id: str
    source_bytes: bytes
    digest: str


@dataclass(frozen=True, slots=True)
class ResolvedView:
    snapshot: Snapshot
    _supplied: MappingProxyType
    _access: ReadCapability
    limits: Limits

    def reader(self):
        return Reader(self)

    def read(self, reference, anchor=None):
        return self.reader().read(reference, anchor)


def resolve(snapshot, supplied_views, read_capability, limits=Limits()):
    """Bind explicit read authority. Referenced sources are resolved on demand."""
    if not isinstance(snapshot, Snapshot):
        raise ResolutionError("verified_snapshot_required")
    if not isinstance(read_capability, ReadCapability) or not read_capability.permits(snapshot.snapshot_id):
        raise ResolutionError("read_denied")
    actual = inspect(snapshot.source_bytes, limits)
    if actual != snapshot:
        raise ResolutionError("snapshot_identity_mismatch")
    if not isinstance(supplied_views, Mapping):
        raise ResolutionError("supplied_mapping_required")
    if len(supplied_views) > limits.external_snapshots:
        raise ResolutionError("dependency_limit")
    supplied = dict(supplied_views)
    if any(not isinstance(pid, str) or type(data) is not bytes for pid, data in supplied.items()):
        raise ResolutionError("supplied_bytes_required")
    if actual.snapshot_id in supplied and supplied[actual.snapshot_id] != actual.source_bytes:
        raise ResolutionError("package_identity_conflict")
    return ResolvedView(actual, MappingProxyType(supplied), read_capability, limits)


@dataclass(slots=True)
class _Package:
    identity: str
    digest: str
    format: dict
    records: dict
    dependencies: dict


def _index(identity, digest, package):
    if package["format"]["name"] == FORMAT:
        dependencies = {item["key"]: item for item in package["dependencies"]}
    else:
        dependencies = {}
        for item in package.get("external_packages", ()):
            pin = item.get("expected_digest", {})
            value = pin.get("value", {})
            full_pin = (pin.get("state") == "known" and value.get("algorithm") == "sha256"
                        and value.get("scope", {}).get("kind") == "full_content")
            dependencies[item["package_id"]] = {
                "package_id": item["package_id"], "format": item.get("format"),
                "pin": {"digest": value.get("value"), "length": value.get("byte_length")}
                if full_pin else None,
            }
    return _Package(identity, digest, package["format"],
                    {record["id"]: record for record in package["records"]}, dependencies)


def _pointer(value, pointer):
    for token in pointer.split("/")[1:]:
        key = token.replace("~1", "/").replace("~0", "~")
        if isinstance(value, dict) and key in value:
            value = value[key]
        elif (isinstance(value, list) and key.isascii() and key.isdecimal()
              and len(key) <= 8 and str(int(key)) == key and int(key) < len(value)):
            value = value[int(key)]
        else:
            raise ResolutionError("selector_target")
    return value


def _select(record, selector):
    if selector is None:
        return record
    payload = record["payload"]
    kind = selector["selector_kind"]
    if kind == "member":
        record_kind = record.get("kind", record.get("record_type"))
        field = {"s4.ledger": "entries", "s4.population": "slots",
                 "s4.request": "goals"}.get(record_kind)
        items = payload[field] if field else ()
        if record_kind == "s4.result" and payload["outcome"]["tag"] == "defined":
            value = payload["outcome"]["value"]
            if value.get("value_kind") == "keyed":
                items = value["entries"]
        matches = [row for row in items if row["key"] == selector["key"]]
    elif kind == "output" and record.get("kind") == "s4.calculation":
        matches = [row for row in payload["emissions"]
                   if row["binding"]["ref_kind"] == "local"
                   and row["binding"]["target_id"] == selector["binding_id"]
                   and row["output_role"] == selector["role"]
                   and row["subject_key"] == selector["subject_key"]]
    else:
        raise ResolutionError("selector_target")
    if len(matches) != 1:
        raise ResolutionError("selector_target")
    return matches[0]


class Reader:
    """Per-operation budget and private cache. Each lookup rechecks authority."""

    def __init__(self, view):
        self._view = view
        self._loaded = {}
        self._bytes = 0
        self._visits = 0
        root = inspect(view.snapshot.source_bytes, view.limits)
        if root != view.snapshot:
            raise ResolutionError("snapshot_identity_mismatch")
        self._permit(root.snapshot_id)
        self._charge_bytes(len(root.source_bytes))
        self._loaded[root.snapshot_id] = _index(root.snapshot_id, root.digest, root.package)

    def _permit(self, package_id):
        if not self._view._access.permits(package_id):
            raise ResolutionError("read_denied")

    def _charge_bytes(self, count):
        self._bytes += count
        if self._bytes > self._view.limits.closure_bytes:
            raise ResolutionError("closure_byte_limit")

    def _visit(self):
        self._visits += 1
        if self._visits > self._view.limits.reference_visits:
            raise ResolutionError("reference_visit_limit")

    def _dependency(self, owner, key):
        descriptor = owner.dependencies.get(key)
        if descriptor is None or descriptor["pin"] is None:
            raise ResolutionError("dependency_unpinned")
        identity, pin = descriptor["package_id"], descriptor["pin"]
        self._permit(identity)
        raw = self._view._supplied.get(identity)
        if raw is None:
            raise ResolutionError("dependency_unavailable")
        loaded = self._loaded.get(identity)
        if str(len(raw)) != pin["length"]:
            raise ResolutionError("integrity_mismatch")
        if loaded is None:
            if len(self._loaded) - 1 >= self._view.limits.external_snapshots:
                raise ResolutionError("dependency_limit")
            self._charge_bytes(len(raw))
        actual_digest = loaded.digest if loaded else sha256(raw).hexdigest()
        if actual_digest != pin["digest"]:
            raise ResolutionError("integrity_mismatch")
        if loaded is None:
            try:
                fmt = descriptor["format"]
                if fmt is not None and fmt["name"] == FORMAT:
                    snapshot = inspect(raw, self._view.limits)
                    actual_id, package = snapshot.snapshot_id, snapshot.package
                else:
                    view = parse_snapshot(raw, self._view.limits.execution_limits(),
                                          access=self._view._access)
                    actual_id, package = view.package_id, view.package
            except (ExecutionError, WireError) as exc:
                raise ResolutionError("dependency_wire_invalid") from exc
            if actual_id != identity:
                raise ResolutionError("package_identity_mismatch")
            loaded = _index(actual_id, actual_digest, package)
            self._loaded[identity] = loaded
        if descriptor["format"] is not None and loaded.format != descriptor["format"]:
            raise ResolutionError("package_format_mismatch")
        return loaded

    def _record(self, ref, owner):
        self._visit()
        self._permit(owner.identity)
        target = owner if ref["ref_kind"] == "local" else self._dependency(owner, ref["dependency_key"])
        found = target.records.get(ref["target_id"])
        if found is None:
            raise ResolutionError("reference_target")
        kind = found.get("kind", found.get("record_type"))
        expected = ref["expected_contract"]
        if expected["name"] != kind or found.get("contract") != expected:
            raise ResolutionError("reference_contract")
        return target, found

    def read(self, ref, anchor=None):
        try:
            check_reference(ref, self._view.limits)
        except WireError as exc:
            raise ResolutionError("invalid_reference") from exc
        owner = self._loaded.get(anchor or self._view.snapshot.snapshot_id)
        if owner is None:
            raise ResolutionError("reference_anchor_required")
        if ref["ref_kind"] != "artifact":
            package, record = self._record(ref, owner)
            value = _select(record, ref.get("selector"))
            return ResolvedRecord(package.identity, package.digest, record["id"],
                                  canonical(record["contract"]), canonical(value))
        self._visit()
        artifact_ref = ref["artifact_record"]
        if (artifact_ref["expected_contract"]["name"] != "s1.artifact_snapshot"
                or "selector" in artifact_ref):
            raise ResolutionError("artifact_target_contract")
        package, record = self._record(artifact_ref, owner)
        return self._artifact(package, record, ref)

    def _artifact(self, package, record, ref):
        try:
            raw = content_bytes(record["payload"]["content"])
        except (ValueError, OSError, KeyError) as exc:
            raise ResolutionError("artifact_unavailable") from exc
        self._charge_bytes(len(raw))
        pin, selector = ref["content_pin"], ref.get("selector")
        extent = pin["extent"]
        first, end = int(extent.get("start", 0)), int(extent.get("end_exclusive", len(raw)))
        if not 0 <= first <= end <= len(raw):
            raise ResolutionError("artifact_extent")
        selected = raw[first:end]
        if str(len(selected)) != pin["length"] or sha256(selected).hexdigest() != pin["digest"]:
            raise ResolutionError("artifact_integrity_mismatch")
        if selector is not None:
            kind = selector["selector_kind"]
            if kind == "byte_range":
                a, b = int(selector["start"]), int(selector["end_exclusive"])
                if not first <= a <= b <= end:
                    raise ResolutionError("artifact_extent")
                selected = raw[a:b]
            elif kind == "json_pointer":
                try:
                    # Artifact JSON uses the same bounded strict token rules as S4.
                    document = loads(selected, self._view.limits.execution_limits())
                    selected = canonical(_pointer(document, selector["pointer"]))
                except ExecutionError as exc:
                    raise ResolutionError("artifact_document_invalid") from exc
            else:
                raise ResolutionError("selector_target")
        return ResolvedArtifact(package.identity, package.digest, record["id"],
                                selected, sha256(selected).hexdigest())

    def closure(self):
        """Verify every declared pin for a complete audience/dependency claim."""
        active, heights = set(), {}

        def visit(package, depth):
            if depth > self._view.limits.dependency_depth:
                raise ResolutionError("dependency_depth_limit")
            if package.identity in active:
                raise ResolutionError("dependency_cycle")
            height = heights.get(package.identity)
            if height is not None:
                if depth + height > self._view.limits.dependency_depth:
                    raise ResolutionError("dependency_depth_limit")
                return height
            active.add(package.identity)
            height = 0
            for key in package.dependencies:
                self._visit()
                height = max(height, 1 + visit(self._dependency(package, key), depth + 1))
            active.remove(package.identity)
            heights[package.identity] = height
            return height

        visit(self._loaded[self._view.snapshot.snapshot_id], 0)
        return frozenset(heights)
