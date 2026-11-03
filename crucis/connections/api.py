"""Closed runtime port values from the accepted S1 API (DLV-08, DLV-09).

Runtime objects are intentionally separate from the SC-1 wire codec. Dataclasses
have slots; opaque grants/handles are never serialized by walking __dict__.
"""
from dataclasses import dataclass, field
from typing import Any, Callable, Generic, TypeVar

from .codec import WireError

T = TypeVar('T')
Ref = dict
Contract = dict
Knowledge = dict


@dataclass(frozen=True, slots=True)
class Op(Generic[T]):
    state: str
    value: T | None = None
    diagnostics: tuple = ()
    def __post_init__(self):
        if self.state not in ('completed','partial','rejected'): raise WireError('invalid operation state')
        if self.state == 'rejected' and (not self.diagnostics or self.value is not None):
            raise WireError('rejection requires diagnostics and no value')
        if any(x.get('target_type') != 's1.gap' for x in self.diagnostics): raise WireError('diagnostic must reference a gap')


@dataclass(frozen=True, slots=True)
class SupportClaim:
    operation: Contract; feature: Contract; route: str; guarantee: str
    conditions: tuple = (); native_evidence: tuple = (); connection_evidence: tuple = (); validation_evidence: tuple = (); limits: tuple = ()

@dataclass(frozen=True, slots=True)
class SupportDeclaration:
    adapter: Ref; claims: tuple; ports: tuple

@dataclass(frozen=True, slots=True)
class PresentedBundle:
    presentations: tuple; permitted_policy: Ref

@dataclass(frozen=True, slots=True)
class RouteSpec:
    route_kind: str; transport: Contract; operation: Contract; parameters: tuple = ()
    def __post_init__(self):
        if self.route_kind not in ('recorded','direct','prepared_command','attached_job','recorded_response_replay'):
            raise WireError('unknown route kind')

@dataclass(frozen=True, slots=True)
class DependencyEntry:
    component: Ref; available: Knowledge; version: Knowledge; evidence: tuple = ()

@dataclass(frozen=True, slots=True)
class DependencyInventory:
    entries: tuple; observation_scope: dict; evidence: tuple = ()

@dataclass(frozen=True, slots=True)
class BoundConnection:
    binding: Ref; request: Ref; adapter: Ref; route: RouteSpec; permitted_presentations: tuple; readiness: str; diagnostics: tuple = ()

@dataclass(frozen=True, slots=True)
class SourceSpec:
    sources: tuple; expected_contracts: tuple; import_occurrence: str; prior_import: Knowledge

@dataclass(frozen=True, slots=True)
class EvidenceDelta:
    records: tuple; artifacts: tuple; subjects: tuple; gaps: tuple; source_occurrence: Knowledge

@dataclass(frozen=True, slots=True)
class InvocationSpec:
    binding: Ref; route: RouteSpec; invocation: dict; inputs: tuple; outputs_expected: tuple; initial_state: Knowledge; authority_required: tuple

@dataclass(frozen=True, slots=True)
class NativeHandle:
    attempt: Ref; native_identity: Knowledge; transport_handle: Any; launch_evidence: tuple; initial_observations: tuple

@dataclass(frozen=True, slots=True)
class Cursor:
    stream: str; position: str; source_identity: Knowledge

@dataclass(frozen=True, slots=True)
class BatchLimit:
    max_events: str; max_bytes: str; deadline: Knowledge
    def __post_init__(self):
        for value in (self.max_events, self.max_bytes):
            if not isinstance(value,str) or not value.isascii() or not value.isdigit() or int(value) <= 0 or str(int(value)) != value:
                raise WireError('batch bounds must be positive SC-1 indices')

@dataclass(frozen=True, slots=True)
class ObservationBatch:
    records: tuple; cursor: Cursor; exhausted: bool; scope: dict; gaps: tuple

@dataclass(frozen=True, slots=True)
class ArtifactView:
    snapshot: Ref; selectors: tuple; reader: Contract; scope: dict

@dataclass(frozen=True, slots=True)
class DecodeRequest:
    target_contract: Contract; selectors: tuple; mappings: tuple; source_objects: tuple; requested_guarantee: str

@dataclass(frozen=True, slots=True)
class InterpretationDelta:
    records: tuple; outputs: tuple; mappings_used: tuple; checks: tuple; gaps: tuple

@dataclass(frozen=True, slots=True)
class DeliveryReceipt:
    response: Ref; transmissions: tuple; evidence: tuple; acknowledgment: Knowledge

@dataclass(frozen=True, slots=True)
class CancellationReceipt:
    record: Ref; evidence: tuple; stop_established: Knowledge

@dataclass(frozen=True, slots=True)
class AdapterServices:
    identities: Any; records: Any; registry: Any

@dataclass(frozen=True, slots=True)
class BindContext:
    services: AdapterServices; observation_scope: dict

@dataclass(frozen=True, slots=True)
class ReadContext:
    access: Ref; resolver: Any; identities: Any; records: Any

@dataclass(frozen=True, slots=True)
class PrepareContext:
    write_scope: Ref; identities: Any

@dataclass(frozen=True, slots=True)
class DecodeContext:
    resolver: Any; mappings: Any; identities: Any

@dataclass(frozen=True, slots=True)
class ExecutionGrant:
    request: Ref; attempt: Ref; operations: tuple; effects: tuple; presentations: tuple; policies: tuple; authority: Ref; runtime_capability: Any

@dataclass(frozen=True, slots=True)
class DeliveryGrant:
    action: Ref; response: Ref; endpoint: Ref; effects: tuple; policies: tuple; authority: Ref; runtime_capability: Any

@dataclass(frozen=True, slots=True)
class CancellationGrant:
    attempt: Ref; policies: tuple; authority: Ref; runtime_capability: Any

@dataclass(frozen=True, slots=True)
class ExecutionContext:
    grant: ExecutionGrant; attempt: Ref; handle_registry: Any; action_channel: Any = None

@dataclass(frozen=True, slots=True)
class DeliveryContext:
    grant: DeliveryGrant

@dataclass(frozen=True, slots=True)
class CancellationContext:
    grant: CancellationGrant

@dataclass(frozen=True, slots=True)
class AssessmentContext:
    resolver: Any; services: AdapterServices

@dataclass(frozen=True, slots=True)
class WriteContext:
    write_scope: Ref; resolver: Any; services: AdapterServices

@dataclass(frozen=True, slots=True)
class ObserverEvidence:
    observer_only: tuple; mappings: tuple

@dataclass(frozen=True, slots=True)
class SelectionAlias:
    namespace: str; name: str

@dataclass(frozen=True, slots=True)
class SelectionReceipt:
    alias: SelectionAlias; previous: Knowledge; selected: Ref; generation: str

@dataclass(frozen=True, slots=True)
class PublicationPolicy:
    allowed_profiles: tuple; required_checks: tuple; backend: Contract; destination: Ref

@dataclass(frozen=True, slots=True)
class PublishedPackage:
    package_id: str; location: Ref; manifest_digest: dict; published_records: tuple

@dataclass(frozen=True, slots=True)
class ResolvedRecord:
    record: dict; availability: tuple; integrity: tuple

@dataclass(frozen=True, slots=True)
class ValidationReport:
    checks: tuple; gaps: tuple; claims_satisfied: tuple; claims_withheld: tuple

@dataclass(frozen=True, slots=True)
class LegacyBinding:
    system: Ref; item: str; arm: str; domain: Ref; coordinate_basis: str; mapping: Knowledge; source_identity: Knowledge; legacy_contract: Contract

@dataclass(frozen=True, slots=True)
class LegacySelection:
    source_records: tuple; graph: Ref; outcome_basis: Ref; coordinate_mapping: Ref; variants: tuple; stages: tuple; legacy_labels: LegacyBinding; projection_rule: Contract

@dataclass(frozen=True, slots=True)
class LegacyProjection:
    record: Any; provenance: tuple; lost_guarantees: tuple; limits: tuple; contract: Contract

@dataclass(frozen=True, slots=True)
class AdapterPorts:
    describe: Callable
    bind: Callable | None = None
    read: Callable | None = None
    prepare: Callable | None = None
    invoke: Callable | None = None
    observe: Callable | None = None
    decode: Callable | None = None
    deliver: Callable | None = None
    cancel: Callable | None = None
    def supported(self):
        return tuple(name for name in self.__dataclass_fields__ if getattr(self,name) is not None)
    def verify_declaration(self):
        declaration=self.describe()
        if set(declaration.ports) != set(self.supported()): raise WireError('advertised ports differ from actual callables')
        return declaration
