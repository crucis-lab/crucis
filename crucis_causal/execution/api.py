"""Closed S3 runtime values and exact port declarations (DLV-08/09).

Opaque authority is checked by its real issuer; these dataclasses are not a wire
format. No dataclass/object introspection is accepted by the manifest codec.
"""
from __future__ import annotations
import copy
import json
import re
from dataclasses import dataclass, field
from typing import Any, Generic, Literal, Protocol, TypeVar
from .model import ExecutionError

T = TypeVar('T')
_OPAQUE_KEY = object()

class _Opaque:
    __slots__ = ('_issuer', '__weakref__')
    def __init__(self, key, issuer):
        if key is not _OPAQUE_KEY:
            raise ExecutionError('s3.actual_issuer_required')
        self._issuer = issuer
    def __setattr__(self, name, value):
        if hasattr(self, name):
            raise TypeError('opaque runtime binding is immutable')
        object.__setattr__(self, name, value)
    def __copy__(self):
        raise TypeError('opaque runtime object cannot be copied')
    def __deepcopy__(self, memo):
        raise TypeError('opaque runtime object cannot be copied')
    def __reduce__(self):
        raise TypeError('opaque runtime object cannot be serialized')

class OpaqueControlCapability(_Opaque):
    __slots__ = ()

class OpaqueEpoch(_Opaque):
    __slots__ = ()

class OpaqueGrant(_Opaque):
    __slots__ = ()

class OpaqueHandle(_Opaque):
    __slots__ = ()

class OpaqueIssuePermit(_Opaque):
    __slots__ = ()

class SuppliedCallable(_Opaque):
    __slots__ = ('_function',)

@dataclass(frozen=True, slots=True)
class Limits:
    max_manifest_bytes: str = '16777216'
    max_depth: str = '64'
    max_records: str = '100000'
    max_collection_items: str = '100000'
    max_total_reference_nodes: str = '1000000'
    max_scalar_utf8_bytes: str = '1048576'
    max_external_packages: str = '10000'
    max_external_bytes: str = '67108864'
    max_reference_depth: str = '64'
    def __post_init__(self):
        for name in self.__slots__:
            if not isinstance(getattr(self, name), str) or re.fullmatch(r'[1-9][0-9]*', getattr(self, name)) is None:
                raise ExecutionError('s3.positive_explicit_limit_required', name)

class ReadCapability(_Opaque):
    __slots__ = ('_packages',)
    def __init__(self, key, issuer, packages):
        super().__init__(key, issuer)
        self._packages = frozenset(packages)
    @property
    def packages(self):
        return self._packages
    def permits(self, package_id):
        return self in _READ_ISSUED and package_id in self._packages

import weakref
_READ_ISSUED = weakref.WeakSet()
def supplied_read(packages):
    """Grant access only to explicitly supplied in-memory snapshots, never I/O."""
    cap = ReadCapability(_OPAQUE_KEY, _READ_ISSUED, packages)
    _READ_ISSUED.add(cap)
    return cap

@dataclass(frozen=True, slots=True)
class Issue:
    code: str
    scope: dict
    evidence: tuple[dict, ...]

@dataclass(frozen=True, slots=True)
class RecordDelta:
    records: tuple[S3Record, ...] = ()
    roots: tuple[dict, ...] = ()
    dependencies: tuple[PinnedView, ...] = ()
    native_additions: tuple[OwnedS1Delta, ...] = ()
    scientific_additions: tuple[OwnedS2Delta, ...] = ()

@dataclass(frozen=True, slots=True)
class EffectBoundary:
    command: dict
    boundary: Literal['not_crossed', 'may_have_crossed', 'crossed', 'not_applicable']
    acceptance: dict
    evidence: tuple[dict, ...]
    transmission: dict

@dataclass(frozen=True, slots=True)
class PreparedOperation:
    binding: dict
    source_view: PinnedView
    requirements: RequirementEvaluation
    driver: ExactDriverDescriptor
    dependencies: PinnedClosure
    command: dict

@dataclass(frozen=True, slots=True)
class LiveAdmission:
    prepared: PreparedOperation
    owner_receipts: tuple[object, ...]
    live_grants: tuple[OpaqueGrant, ...]
    journal_head: JournalHead
    validity: ValidityContext
    admission_occurrence: str
    admission_plan: dict
    assessment: dict

@dataclass(frozen=True, slots=True)
class IssueToken:
    command: dict
    intent_commit: JournalCommit
    owner_epoch: OpaqueEpoch
    binding_digest: dict
    transmission: dict
    runtime_permit: OpaqueIssuePermit | None

@dataclass(frozen=True, slots=True)
class JournalHead:
    account: dict
    revision: str
    snapshot: PinnedView

@dataclass(frozen=True, slots=True)
class PinnedView:
    package_id: str
    format: dict
    digest: dict
    source_bytes: bytes
    read_scope: ReadCapability
    @property
    def package(self):
        return json.loads(self.source_bytes)
    @property
    def records(self):
        return tuple(self.package['records'])
    @property
    def snapshot_digest(self):
        return copy.deepcopy(self.digest)

@dataclass(frozen=True, slots=True)
class NativeBatch:
    source: SourceIdentity
    occurrence: str
    raw: tuple[CapturedBytes, ...]
    observations: RecordDelta
    next_cursor: dict
    coverage: dict
    source_ack: dict

@dataclass(frozen=True, slots=True)
class LookupResult:
    classification: Literal['positive', 'negative', 'unknown', 'disputed']
    matches: tuple[NativeDescriptor, ...]
    query_binding: dict
    coverage: QueryCoverage
    evidence: RecordDelta

@dataclass(frozen=True, slots=True)
class DecisionResult:
    actions: tuple[dict, ...]
    selected: dict
    input_frontier: dict
    rule: dict
    issues: tuple[Issue, ...]

@dataclass(frozen=True, slots=True)
class CoordinatorContext:
    read: PinnedReadContext
    journal: JournalPort
    storage: StoragePort
    owners: OwnerMap
    drivers: ExactDriverRegistry
    decisions: ExactDecisionRegistry
    control_capability: OpaqueControlCapability
    clock: ClockPort
    limits: Limits

@dataclass(frozen=True, slots=True)
class CommissionSpec:
    account_id: str
    purpose: Literal['prepare', 'execute', 'observe']
    target: ImmutableTargetDefinition
    audience: dict
    requirements: dict

@dataclass(frozen=True, slots=True)
class OperationRequest:
    operation: dict
    roles: tuple[object, ...]
    parameters: tuple[object, ...]
    request_occurrence: str

@dataclass(frozen=True, slots=True)
class ExactOperationRequest:
    command: dict
    binding: ResolvedOperationBinding
    inputs: PinnedInputs
    descriptor: ExactDriverDescriptor
    source_view: PinnedView

@dataclass(frozen=True, slots=True)
class ExactOwnerRequest:
    operation: dict
    owner: dict
    correlation: str
    binding: ResolvedOperationBinding
    parameters: tuple[object, ...]
    evidence: PinnedInputs
    request_occurrence: str
    admission_occurrence: str

@dataclass(frozen=True, slots=True)
class PinnedReadContext:
    views: tuple[PinnedView, ...]
    access: ReadCapability
    registry: SuppliedRegistryContext
    limits: Limits

@dataclass(frozen=True, slots=True)
class PinnedInputs:
    entries: tuple[BoundInput, ...]
    source_views: tuple[PinnedView, ...]

@dataclass(frozen=True, slots=True)
class BoundInput:
    role: str
    reference: dict
    record: ImmutableRecord
    source_package: str
    source_digest: dict

@dataclass(frozen=True, slots=True)
class ResolvedOperationBinding:
    record: dict
    context: object
    inputs: PinnedInputs

@dataclass(frozen=True, slots=True)
class ExactDriverDescriptor:
    component: dict
    operation: dict
    input_contract: dict
    output_contract: dict
    implementation: PinnedArtifactIdentity
    guarantees: tuple[SupportClaim, ...]
    method: SuppliedCallable

@dataclass(frozen=True, slots=True)
class PreparedNativeCall:
    binding: ResolvedOperationBinding
    descriptor: ExactDriverDescriptor
    invocation: DecodedInvocation
    inputs: PinnedInputs

@dataclass(frozen=True, slots=True)
class DriverDeclaration:
    component: dict
    methods: tuple[ExactDriverDescriptor, ...]
    dependencies: tuple[SupportClaim, ...]

@dataclass(frozen=True, slots=True)
class DecisionDeclaration:
    component: dict
    procedure: dict
    input_contract: dict
    output_contract: dict
    information_requirements: dict
    fallback_rule: dict
    implementation: PinnedArtifactIdentity

@dataclass(frozen=True, slots=True)
class RecoveryGoal:
    kind: Literal['wait', 'reconcile', 'reconnect', 'retransmit', 'restart', 'stop', 'close']
    scope: dict
    policy: dict

@dataclass(frozen=True, slots=True)
class RecoveryPlan:
    goal: RecoveryGoal
    operations: tuple[OperationRequest, ...]
    held_requirements: tuple[Issue, ...]
    obligations: tuple[dict, ...]

@dataclass(frozen=True, slots=True)
class RequirementEvaluation:
    requirements: dict
    established: tuple[ClaimRequest, ...]
    withheld: tuple[ClaimRequest, ...]
    issues: tuple[Issue, ...]
    frontier: dict

@dataclass(frozen=True, slots=True)
class InformationRequirements:
    actions: PinnedActionSet
    sources: tuple[RequirementSpec, ...]
    policy: PinnedPolicy
    context: object

@dataclass(frozen=True, slots=True)
class OwnerReceiptAndOptionalLiveGrant:
    receipt: dict
    revision: str
    grant: OpaqueGrant | None
    effects: tuple[EffectBoundary, ...]

@dataclass(frozen=True, slots=True)
class OwnerSnapshot:
    owner: dict
    revision: dict
    availability: RequirementEvaluation
    evidence: RecordDelta

@dataclass(frozen=True, slots=True)
class ValidityReceipt:
    binding_digest: dict
    owner: dict
    decision: Literal['permitted', 'denied', 'unresolved']
    evidence: RecordDelta

@dataclass(frozen=True, slots=True)
class JournalCommit:
    receipt: dict
    head: JournalHead
    binding_digest: dict
    durability: dict

@dataclass(frozen=True, slots=True)
class CaptureCommit:
    commit: JournalCommit
    source: SourceIdentity
    occurrence: str
    artifacts: tuple[dict, ...]
    durable_cursor: dict

@dataclass(frozen=True, slots=True)
class IssueReceipt:
    command: dict
    token: IssueToken
    result: DriverEvidence
    effects: tuple[EffectBoundary, ...]
    transmission: dict
    admission_occurrence: str

@dataclass(frozen=True, slots=True)
class DriverEvidence:
    binding: dict
    records: RecordDelta
    subjects: dict
    receipts: dict
    assessments: dict
    live_handles: tuple[OpaqueHandle, ...]

@dataclass(frozen=True, slots=True)
class NativeStart:
    attempt: dict
    native_subject: dict
    connection: OpaqueHandle | None
    evidence: DriverEvidence

@dataclass(frozen=True, slots=True)
class NativeConnection:
    subject: dict
    attempt: dict
    role: str
    owner_epoch: str
    handle: OpaqueHandle
    evidence: DriverEvidence

@dataclass(frozen=True, slots=True)
class SourceIdentity:
    subject: dict
    protocol: dict
    filter_digest: dict
    generation: dict
    consumer: dict
    identity_rule: dict

@dataclass(frozen=True, slots=True)
class QueryCoverage:
    scope: dict
    paths: tuple[dict, ...]
    interval: dict
    retention: dict
    complete: dict
    evidence: RecordDelta
    no_late_acceptance: dict

@dataclass(frozen=True, slots=True)
class PublicationReceipt:
    receipt: dict
    package_id: str
    digest: dict
    commit_state: Literal['committed', 'unconfirmed', 'failed', 'disputed']

@dataclass(frozen=True, slots=True)
class CommitLookup:
    state: Literal['committed', 'not_committed', 'unknown', 'disputed']
    package_id: str
    digest: dict
    evidence: RecordDelta

@dataclass(frozen=True, slots=True)
class PointerReceipt:
    namespace: str
    name: str
    previous_revision: str
    current_revision: str
    selection: PinnedSelection
    evidence: RecordDelta

@dataclass(frozen=True, slots=True)
class PackageDraft:
    package_id: str
    format: dict
    bytes: bytes
    digest: dict
    audience: AudienceClosure
    withheld: tuple[Issue, ...]

@dataclass(frozen=True, slots=True)
class PinnedArtifactIdentity:
    reference: dict
    content_digest: dict
    selector: dict
    source_view: PinnedView

@dataclass(frozen=True, slots=True)
class PinnedSelection:
    reference: dict
    source_view: PinnedView
    commit_receipt: PublicationReceipt

@dataclass(frozen=True, slots=True)
class AudienceClosure:
    audience: dict
    allowed_records: tuple[dict, ...]
    allowed_dependencies: tuple[PinnedView, ...]
    policy: dict
    checks: tuple[dict, ...]

@dataclass(frozen=True, slots=True)
class AccessScope:
    owner: dict
    recipients: tuple[dict, ...]
    rights: tuple[dict, ...]
    subject: PinnedArtifactIdentity

@dataclass(frozen=True, slots=True)
class CopyRetentionScope:
    owner: dict
    copies: tuple[dict, ...]
    retention_rule: dict
    subject: PinnedArtifactIdentity

@dataclass(frozen=True, slots=True)
class CapturedBytes:
    occurrence: str
    source: SourceIdentity
    bytes: bytes
    extent: dict
    metadata: RecordDelta

@dataclass(frozen=True, slots=True)
class ClaimRequest:
    contract: dict
    scope: dict
    parameters: PinnedInputs

@dataclass(frozen=True, slots=True)
class OwnerBindingReceipts:
    receipts: tuple[dict, ...]
    binding_digest: dict
    validity: ValidityContext

@dataclass(frozen=True, slots=True)
class ValidityContext:
    owner_epochs: tuple[OwnerEpochBinding, ...]
    deadline: dict
    requirements: tuple[dict, ...]
    evidence: RecordDelta

@dataclass(frozen=True, slots=True)
class OwnerEpochBinding:
    owner: dict
    epoch: str
    binding_digest: dict
    validity: PinnedInputs

@dataclass(frozen=True, slots=True)
class TimeInterval:
    start: dict
    end: dict
    clock: dict
    comparison: dict

@dataclass(frozen=True, slots=True)
class ClockReading:
    value: dict
    source: dict
    evidence: RecordDelta

@dataclass(frozen=True, slots=True)
class TransactionLookup:
    state: Literal['committed', 'not_committed', 'unknown', 'disputed']
    transaction: str
    binding_digest: dict
    commit: dict
    records: RecordDelta

@dataclass(frozen=True, slots=True)
class OwnedS1Delta:
    context: PinnedWorkingS1Context
    value: object
    scope: dict

@dataclass(frozen=True, slots=True)
class OwnedS2Delta:
    context: object
    value: object
    scope: dict

@dataclass(frozen=True, slots=True)
class CommitDelta:
    records: tuple[S3Record, ...] = ()
    roots: tuple[dict, ...] = ()
    dependencies: tuple[PinnedView, ...] = ()

@dataclass(frozen=True, slots=True)
class PinnedClosure:
    views: tuple[PinnedView, ...]
    record_bindings: tuple[BoundInput, ...]

@dataclass(frozen=True, slots=True)
class CallResult(Generic[T]):
    state: str
    value: T | None = None
    records: RecordDelta = field(default_factory=RecordDelta)
    issues: tuple[Issue, ...] = ()
    effects: tuple[EffectBoundary, ...] = ()
    def __post_init__(self):
        if self.state not in ('completed', 'partial', 'rejected'):
            raise ExecutionError('s3.invalid_return_state')
        if self.state == 'rejected' and (not self.issues or isinstance(self.value, LiveAdmission)):
            raise ExecutionError('s3.rejection_requires_issues_and_no_executable_admission')
        if self.state == 'partial' and (self.value is None or not self.issues):
            raise ExecutionError('s3.partial_requires_value_and_issues')
        if any(not isinstance(i, Issue) for i in self.issues):
            raise ExecutionError('s3.typed_issue_required')

def rejected(code, scope=None, *, records=None, effects=()):
    return CallResult('rejected', records=records or RecordDelta(), issues=(Issue(code, scope or {'subjects': [], 'qualifiers': []}, ()),), effects=tuple(effects))

@dataclass(frozen=True, slots=True)
class RuntimeContext:
    read: PinnedReadContext
    control: Any
    owner_epochs: tuple = ()
    transport: Any = None
    secret_bindings: Any = None
    fault: Any = None

OperationBinding = ResolvedOperationBinding
AccountView = PinnedView
JournalReadContext = RuntimeContext
JournalWriteContext = RuntimeContext
CaptureWriteContext = RuntimeContext
LiveDriverContext = RuntimeContext
StorageContext = RuntimeContext
OwnerControlContext = RuntimeContext
PureDriverContext = PinnedReadContext
PureDecisionContext = PinnedReadContext
ClockReadContext = RuntimeContext
NativeDescriptor = dict
BoundaryKind = dict
RealizationEvidence = DriverEvidence
StagingEvidence = DriverEvidence
SourceAck = DriverEvidence
InformationEvidence = DriverEvidence
ComputationEvidence = DriverEvidence
DeliveryEvidence = DriverEvidence
DeliveryLookup = DriverEvidence
StopEvidence = DriverEvidence
StateLoadEvidence = DriverEvidence
ImportEvidence = DriverEvidence
InterpretationEvidence = DriverEvidence
AvailabilityEvidence = DriverEvidence
RevocationEvidence = DriverEvidence
DeletionEvidence = DriverEvidence

# Wire aliases retain schema ownership; no reader widens S1/S2 to S3.
S3Record = dict
ImmutableRecord = dict
ImmutableTargetDefinition = dict
SupportClaim = dict
OwnerReceipt = dict
DecodedInvocation = dict
PinnedActionSet = tuple[BoundInput, ...]
PinnedPolicy = BoundInput
RequirementSpec = ClaimRequest
OpaqueGrantSet = tuple[OpaqueGrant, ...]
OwnerMap = dict[str, 'OwnerPort']
from crucis_causal.experiments.api import ProjectionOccurrence as S1ProjectionOccurrence
from crucis_causal.experiments.api import S1ProjectionContext as PinnedProjectionContext
@dataclass(frozen=True, slots=True)
class PinnedWorkingS1Context:
    buffer: object
    source_views: tuple[PinnedView, ...]
    mappings: tuple
    request: dict
    attempt: dict
    limits: Limits = field(default_factory=Limits)

@dataclass(frozen=True, slots=True)
class S1Projection:
    projection: object
    request_view: PinnedView
    handoff: dict
    scientific_view: PinnedView
    bridge: dict
    dependencies: tuple[PinnedView, ...]
    claim_scope: str = 'Exact metadata handoff; no launch, admission or causal correctness'

class ExactDriverRegistry(Protocol):
    def lookup(self, selected: dict) -> ExactDriverDescriptor: ...

class ExactDecisionRegistry(Protocol):
    def lookup(self, selected: dict) -> tuple[DecisionDeclaration, 'DecisionPort']: ...

class PayloadDecoderPort(Protocol):
    def decode(self, selected: dict, value: object) -> object: ...

class SuppliedRegistryContext(Protocol):
    drivers: ExactDriverRegistry
    decisions: ExactDecisionRegistry
    payloads: PayloadDecoderPort

class CaptureSink(Protocol):
    def capture(self, data: bytes) -> dict: ...

class CoordinatorPort(Protocol):
    def open(self, commission: CommissionSpec, context: CoordinatorContext) -> CallResult[AccountView]: ...
    def plan(self, view: PinnedView, request: OperationRequest, context: PinnedReadContext) -> CallResult[PreparedOperation]: ...
    def compile(self, run: dict, occurrence: S1ProjectionOccurrence, context: PinnedProjectionContext) -> CallResult[S1Projection]: ...
    def admit(self, prepared: PreparedOperation, expected_head: JournalHead, context: CoordinatorContext, admission_occurrence: str) -> CallResult[LiveAdmission]: ...
    def issue(self, admission: LiveAdmission, context: CoordinatorContext, transmission_occurrence: str) -> CallResult[IssueReceipt]: ...
    def recover(self, view: PinnedView, goal: RecoveryGoal, context: PinnedReadContext) -> CallResult[RecoveryPlan]: ...
    def freeze(self, view: PinnedView, audience: dict, claims: tuple[ClaimRequest, ...], context: PinnedReadContext) -> CallResult[PackageDraft]: ...

class OwnerPort(Protocol):
    def inspect(self, binding: OperationBinding, context: OwnerControlContext) -> CallResult[OwnerSnapshot]: ...
    def reserve(self, request: ExactOwnerRequest, context: OwnerControlContext) -> CallResult[OwnerReceiptAndOptionalLiveGrant]: ...
    def reconcile(self, request: ExactOwnerRequest, context: OwnerControlContext) -> CallResult[OwnerReceiptAndOptionalLiveGrant]: ...
    def renew(self, request: ExactOwnerRequest, context: OwnerControlContext) -> CallResult[OwnerReceiptAndOptionalLiveGrant]: ...
    def settle(self, request: ExactOwnerRequest, context: OwnerControlContext) -> CallResult[OwnerReceiptAndOptionalLiveGrant]: ...
    def release(self, request: ExactOwnerRequest, context: OwnerControlContext) -> CallResult[OwnerReceiptAndOptionalLiveGrant]: ...
    def authorize(self, request: ExactOwnerRequest, context: OwnerControlContext) -> CallResult[OwnerReceiptAndOptionalLiveGrant]: ...
    def check(self, grant: OpaqueGrant, binding: OperationBinding, boundary: BoundaryKind, context: OwnerControlContext) -> CallResult[ValidityReceipt]: ...

class DriverPort(Protocol):
    def describe(self, context: SuppliedRegistryContext) -> DriverDeclaration: ...
    def prepare(self, binding: OperationBinding, inputs: PinnedInputs, context: PureDriverContext) -> CallResult[PreparedNativeCall]: ...
    def realize(self, request: ExactOperationRequest, context: LiveDriverContext, grants: OpaqueGrantSet, issue_token: IssueToken, sink: CaptureSink) -> CallResult[RealizationEvidence]: ...
    def stage(self, request: ExactOperationRequest, context: LiveDriverContext, grants: OpaqueGrantSet, issue_token: IssueToken, sink: CaptureSink) -> CallResult[StagingEvidence]: ...
    def invoke(self, request: ExactOperationRequest, context: LiveDriverContext, grants: OpaqueGrantSet, issue_token: IssueToken, sink: CaptureSink) -> CallResult[NativeStart]: ...
    def lookup(self, request: ExactOperationRequest, context: LiveDriverContext, grants: OpaqueGrantSet, issue_token: IssueToken, sink: CaptureSink) -> CallResult[LookupResult]: ...
    def attach(self, request: ExactOperationRequest, context: LiveDriverContext, grants: OpaqueGrantSet, issue_token: IssueToken, sink: CaptureSink) -> CallResult[NativeConnection]: ...
    def observe(self, request: ExactOperationRequest, context: LiveDriverContext, grants: OpaqueGrantSet, issue_token: IssueToken, sink: CaptureSink) -> CallResult[NativeBatch]: ...
    def ack(self, request: ExactOperationRequest, context: LiveDriverContext, grants: OpaqueGrantSet, issue_token: IssueToken, sink: CaptureSink) -> CallResult[SourceAck]: ...
    def acquire(self, request: ExactOperationRequest, context: LiveDriverContext, grants: OpaqueGrantSet, issue_token: IssueToken, sink: CaptureSink) -> CallResult[InformationEvidence]: ...
    def compute(self, request: ExactOperationRequest, context: LiveDriverContext, grants: OpaqueGrantSet, issue_token: IssueToken, sink: CaptureSink) -> CallResult[ComputationEvidence]: ...
    def deliver(self, request: ExactOperationRequest, context: LiveDriverContext, grants: OpaqueGrantSet, issue_token: IssueToken, sink: CaptureSink) -> CallResult[DeliveryEvidence]: ...
    def lookup_delivery(self, request: ExactOperationRequest, context: LiveDriverContext, grants: OpaqueGrantSet, issue_token: IssueToken, sink: CaptureSink) -> CallResult[DeliveryLookup]: ...
    def stop(self, request: ExactOperationRequest, context: LiveDriverContext, grants: OpaqueGrantSet, issue_token: IssueToken, sink: CaptureSink) -> CallResult[StopEvidence]: ...
    def restore(self, request: ExactOperationRequest, context: LiveDriverContext, grants: OpaqueGrantSet, issue_token: IssueToken, sink: CaptureSink) -> CallResult[StateLoadEvidence]: ...
    def read(self, request: ExactOperationRequest, context: LiveDriverContext, grants: OpaqueGrantSet, issue_token: IssueToken, sink: CaptureSink) -> CallResult[ImportEvidence]: ...
    def decode(self, request: ExactOperationRequest, context: PureDriverContext) -> CallResult[InterpretationEvidence]: ...

class DecisionPort(Protocol):
    def describe(self, context: SuppliedRegistryContext) -> DecisionDeclaration: ...
    def requirements(self, actions: PinnedActionSet, policy: PinnedPolicy, context: PinnedReadContext) -> CallResult[InformationRequirements]: ...
    def select(self, actions: PinnedActionSet, policy: PinnedPolicy, inputs: PinnedInputs, frontier: dict, context: PureDecisionContext) -> CallResult[DecisionResult]: ...

class JournalPort(Protocol):
    def head(self, account: dict, context: JournalReadContext) -> CallResult[JournalHead]: ...
    def append(self, account: dict, expected_revision: str, transaction: str, delta: CommitDelta, context: JournalWriteContext) -> CallResult[JournalCommit]: ...
    def prepare_issue(self, command: dict, expected_head: JournalHead, grant_bindings: OwnerBindingReceipts, context: JournalWriteContext, transmission: dict) -> CallResult[IssueToken]: ...
    def commit_capture(self, source: SourceIdentity, expected_revision: str, batch_occurrence: str, bytes: tuple[CapturedBytes, ...], delta: CommitDelta, next_cursor: dict, context: CaptureWriteContext) -> CallResult[CaptureCommit]: ...
    def snapshot(self, account: dict, revision: str, context: JournalReadContext) -> CallResult[PinnedView]: ...
    def lookup_transaction(self, account: dict, transaction: str, expected_binding: dict, context: JournalReadContext) -> CallResult[TransactionLookup]: ...

class StoragePort(Protocol):
    def publish(self, publication_id: str, bytes: bytes, expected_id: str, expected_digest: dict, audience: AudienceClosure, grants: OpaqueGrantSet, issue_token: IssueToken, context: StorageContext) -> CallResult[PublicationReceipt]: ...
    def lookup_commit(self, publication_id: str, package_id: str, expected_digest: dict, grants: OpaqueGrantSet, issue_token: IssueToken, context: StorageContext) -> CallResult[CommitLookup]: ...
    def cas_pointer(self, namespace: str, name: str, expected_revision: str, committed_selection: PinnedSelection, grants: OpaqueGrantSet, issue_token: IssueToken, context: StorageContext) -> CallResult[PointerReceipt]: ...
    def locate(self, subject: PinnedArtifactIdentity, locator: str, expected_digest: dict, grants: OpaqueGrantSet, issue_token: IssueToken, context: StorageContext) -> CallResult[AvailabilityEvidence]: ...
    def revoke(self, subject: PinnedArtifactIdentity, scope: AccessScope, grants: OpaqueGrantSet, issue_token: IssueToken, context: StorageContext) -> CallResult[RevocationEvidence]: ...
    def delete(self, subject: PinnedArtifactIdentity, scope: CopyRetentionScope, grants: OpaqueGrantSet, issue_token: IssueToken, context: StorageContext) -> CallResult[DeletionEvidence]: ...

class ClockPort(Protocol):
    def now(self, context: ClockReadContext) -> CallResult[ClockReading]: ...
