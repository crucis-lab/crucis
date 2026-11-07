
"""Read explicitly supplied, pinned evidence for S5."""

from collections.abc import Mapping
from dataclasses import dataclass
from hashlib import sha256
from types import MappingProxyType, SimpleNamespace

from crucis_causal.execution.api import ReadCapability
from crucis_causal.measurement import codec as measurement
from crucis_causal.measurement.resolution import Reader as PinnedReader, ResolvedArtifact, ResolvedRecord
from crucis_causal.measurement.resolution import ResolutionError as PredecessorError

from .codec import FORMAT, Limits, Snapshot, WireError, check_reference, inspect


class ResolutionError(ValueError):
    def __init__(self, code, scope=""):
        self.code = "s5." + code.removeprefix("s5.").removeprefix("s4.")
        self.scope = scope
        super().__init__(self.code)


@dataclass(frozen=True, slots=True)
class ResolvedView:
    snapshot: Snapshot
    supplied: MappingProxyType
    access: ReadCapability
    limits: Limits

    def reader(self):
        return Reader(self)

    def read(self, ref, anchor=None):
        return self.reader().read(ref, anchor)


def resolve(snapshot, supplied_views, read_capability, limits=Limits()):
    if not isinstance(snapshot, Snapshot):
        raise ResolutionError("verified_snapshot_required")
    if not isinstance(read_capability, ReadCapability) or not read_capability.permits(snapshot.snapshot_id):
        raise ResolutionError("read_denied")
    actual = inspect(snapshot.source_bytes, limits)
    if actual != snapshot:
        raise ResolutionError("snapshot_identity_mismatch")
    if not isinstance(supplied_views, Mapping) or len(supplied_views) > limits.wire.external_snapshots:
        raise ResolutionError("invalid_supplied_mapping")
    supplied = dict(supplied_views)
    if any(not isinstance(key, str) or type(value) is not bytes for key, value in supplied.items()):
        raise ResolutionError("supplied_bytes_required")
    if actual.snapshot_id in supplied and supplied[actual.snapshot_id] != actual.source_bytes:
        raise ResolutionError("package_identity_conflict")
    return ResolvedView(actual, MappingProxyType(supplied), read_capability, limits)


class Reader(PinnedReader):
    _formats = frozenset({FORMAT, measurement.FORMAT})
    _wire_errors = (WireError, measurement.WireError)

    def __init__(self, view):
        self._finding_limits = view.limits
        try:
            super().__init__(SimpleNamespace(snapshot=view.snapshot, limits=view.limits.wire,
                                             _supplied=view.supplied, _access=view.access))
        except PredecessorError as exc:
            raise ResolutionError(exc.issue.code, exc.issue.scope) from exc

    def _inspect_snapshot(self, raw, limits):
        return inspect(raw, self._finding_limits)

    def _decode_snapshot(self, raw, name):
        return (inspect(raw, self._finding_limits) if name == FORMAT
                else measurement.inspect(raw, self._finding_limits.wire))

    def _check_reference(self, ref, limits):
        # The referring format is checked in read; the shared reader checks
        # common reference structure for both accepted dialects.
        measurement.check_reference(ref, limits)

    def read(self, ref, anchor=None):
        try:
            owner = self._loaded.get(anchor or self._view.snapshot.snapshot_id)
            if owner is not None and owner.format["name"] == FORMAT:
                check_reference(ref, self._finding_limits)
            return super().read(ref, anchor)
        except (PredecessorError, WireError) as exc:
            code = exc.issue.code if isinstance(exc, PredecessorError) else exc.code
            raise ResolutionError(code) from exc

    def verified_closure(self):
        try:
            return super().verified_closure()
        except PredecessorError as exc:
            raise ResolutionError(exc.issue.code) from exc


def whole(reader, ref, contract, anchor=None):
    value = reader.read(ref, anchor)
    if ("selector" in ref or not isinstance(value, ResolvedRecord)
            or value.contract["name"] != contract):
        raise ResolutionError("role_contract")
    return value


def identity(value):
    return value.package_id, value.package_digest, value.record_id


def pin(value):
    return (*identity(value), value.digest if isinstance(value, ResolvedArtifact)
            else sha256(value.selected_bytes).hexdigest())
