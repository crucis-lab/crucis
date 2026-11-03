# Subsystem 1: exact port signatures and legacy compatibility (1 Nov 2026)

Tickets: DLV-08, DLV-09; neighbours DLV-10, ADV-01, DLV-06.
Status: proposed interface/compatibility specification; no Python modules, adapters or consumers changed.
Uses [SC-1 serialization](system-connections-serialization-2026-11-01.md) and
[interaction/recovery contracts](system-connections-interaction-recovery-2026-11-01.md).
Signatures below specify behavior and types, not executable classes or approved implementation locations.

## 1. Port model and operation results

An adapter implements only the ports it advertises. A recorded-only adapter needs description and import,
plus its native decoder binding where typed interpretation is claimed. It does not need fake invoke,
cancel, replay or interaction methods. Shared native formats can use reusable decoders; system-specific
encoding evidence stays in the native integration. No dispatch branches on system names in generic rules.

Op[T] is a tagged operation result:

- completed(value:T, diagnostics:Ref(gap)[])
- partial(value:T, diagnostics:Ref(gap)[])
- rejected(diagnostics:Ref(gap)[])

Rejected has nonempty diagnostics. These describe success/partial completion/refusal of an adapter/core
operation, never a universal native-run success flag. Partial can carry captured content after native,
parser or transport failure. Programmer/contract violations produce a component-attributed diagnostic and
retain recoverable evidence; unknown error attribution is not guessed as native fault.

All persistence uses core-assigned/persisted identities and explicit capture/store services. Read/prepare
operations cannot implicitly start paid or native work. Native imports/entry-point resolution with execution
or external effects are deferred to an explicitly granted invoke operation. Preparation is limited to
declared input materialization/formatting; describe/bind do not import native code to discover readiness.

## 2. Exact proposed adapter signatures

These are Python-style type declarations for design review; no function bodies or runtime code are supplied.

```text
describe() -> SupportDeclaration
bind(request: RequestRef, presented: PresentedBundle,
     route: RouteSpec, inventory: DependencyInventory,
     context: BindContext) -> Op[BoundConnection]
read(source: SourceSpec, context: ReadContext,
     sink: CaptureSink) -> Op[EvidenceDelta]
prepare(bound: BoundConnection, context: PrepareContext,
        sink: CaptureSink) -> Op[InvocationSpec]
invoke(spec: InvocationSpec, context: ExecutionContext,
       sink: CaptureSink) -> Op[NativeHandle]
observe(handle: NativeHandle, cursor: Cursor, limit: BatchLimit,
        context: ReadContext, sink: CaptureSink) -> Op[ObservationBatch]
decode(source: ArtifactView, request: DecodeRequest,
       context: DecodeContext) -> Op[InterpretationDelta]
deliver(response: ActionResponseRef, channel: ActionChannel,
        context: DeliveryContext, sink: CaptureSink) -> Op[DeliveryReceipt]
cancel(handle: NativeHandle, context: CancellationContext,
       sink: CaptureSink) -> Op[CancellationReceipt]
```

| Port | Side effects and result meaning |
|---|---|
| describe | Pure declaration of components/features/routes/conditions and evidence; no launch, network query or dependency installation |
| bind | Validate supplied request/presentation against declared route and supplied dependency inventory; no mutation of request or hidden native execution |
| read | Read only explicitly authorized source/access scope; may capture evidence through sink; no original native execution inferred from CPU ingestion |
| prepare | May materialize declared native inputs through sink; returns a route specification, not an executed job; no shell evaluation of arbitrary strings |
| invoke | Optional; only an explicit granted native route; records the new attempt's launch evidence and returned handle, including ambiguous acknowledgments |
| observe | One bounded observation batch; no unbounded polling/retry loop and no implicit restart; loss of contact remains scoped |
| decode | Read exact supplied snapshot/selector and explicit mappings; produce views/diagnostics; no original input enrichment or scientific repair |
| deliver | Optional; delivers a supplied authorized action response to its selected channel; does not choose an experiment or answer using hidden references |
| cancel | Optional; sends a granted cancellation and records receipt; receipt does not prove stop |

Adapters that only prepare commands return InvocationSpec to the execution owner. They do not claim invoke
support. An asynchronous native route can return a handle immediately and expose subsequent batches.
A synchronous route can return a completed handle plus final observations without inventing a session.
Callbacks can be captured during invoke through the declared ActionChannel; the native system chooses its
native action while the external policy owner decides permission and supplied response.

## 3. Exact support/result type fields

These are closed API value shapes. Refs/Contracts/Knowledge and persistent records use SC-1.

| Type | Fields |
|---|---|
| SupportDeclaration | adapter:Ref(component), claims:SupportClaim[], ports:Code[] |
| SupportClaim | operation:Contract, feature:Contract, route:Code, guarantee:preserve|interpret|prepare|invoke|observe|replay, conditions:Ref[], native_evidence:Ref[], connection_evidence:Ref[], validation_evidence:Ref[], limits:Ref(gap)[] |
| PresentedBundle | presentations:Ref(presentation)[], permitted_policy:Ref(policy) |
| RouteSpec | route_kind:recorded|direct|prepared_command|attached_job|recorded_response_replay, transport:Contract, operation:Contract, parameters:Ref[] |
| DependencyInventory | entries:DependencyEntry[], observation_scope:Scope, evidence:Ref[] |
| DependencyEntry | component:Ref(component), available:K(Boolean), version:K(String), evidence:Ref[] |
| BoundConnection | binding:Ref(binding), request:RequestRef, adapter:Ref(component), route:RouteSpec, permitted_presentations:Ref(presentation)[], readiness:ready|not_ready|unresolved, diagnostics:Ref(gap)[] |
| SourceSpec | sources:Ref(artifact_snapshot|artifact_declaration|location)[], expected_contracts:Contract[], import_occurrence:ID, prior_import:K(Ref(connection_observation)) |
| EvidenceDelta | records:Record[], artifacts:Ref(artifact_snapshot|artifact_declaration)[], subjects:Ref[], gaps:Ref(gap)[], source_occurrence:K(NativeIdentity) |
| InvocationSpec | binding:Ref(binding), route:RouteSpec, invocation:Invocation, inputs:Ref(presentation)[], outputs_expected:Contract[], initial_state:K(Ref(output)), authority_required:Ref(policy)[] |
| NativeHandle | attempt:Ref(attempt), native_identity:K(NativeIdentity), transport_handle:OpaqueRuntimeHandle, launch_evidence:Ref[], initial_observations:Ref(observation)[] |
| ObservationBatch | records:Record[], cursor:Cursor, exhausted:Boolean, scope:Scope, gaps:Ref(gap)[] |
| DecodeRequest | target_contract:Contract, selectors:Selector[], mappings:Ref(mapping)[], source_objects:Ref(output)[], requested_guarantee:preserve|interpret |
| InterpretationDelta | records:Record[], outputs:Ref(output)[], mappings_used:Ref(mapping)[], checks:Ref(check)[], gaps:Ref(gap)[] |
| DeliveryReceipt | response:Ref(action_response), transmissions:Ref(transmission)[], evidence:Ref[], acknowledgment:K(NativeIdentity) |
| CancellationReceipt | record:Ref(cancellation), evidence:Ref[], stop_established:K(Boolean) |

Invocation = {kind:function, entrypoint:Contract, arguments:Ref[]} |
{kind:process, executable:String, argv:String[], cwd:Ref(location), environment_policy:Ref(policy)} |
{kind:service, endpoint:Ref(endpoint), request:Ref}.
Container launch is a named process/transport contract with explicit image/configuration references.
No unstructured shell command is the universal invocation format. Runtime credentials/handles stay in
authorized runtime contexts; persistent descriptors identify access boundaries, not secret values.

Cursor = {stream:String, position:String, source_identity:K(NativeIdentity)}; opaque positions never imply
event order outside their stream. BatchLimit = {max_events:Index, max_bytes:Index, deadline:K(Time)} with
positive bounds. exhausted refers to the observation interface, not native scientific completion.

RequestRef abbreviates Ref(request); ArtifactView = {snapshot:Ref(artifact_snapshot), selectors:Selector[],
reader:Contract, scope:Scope}. CaptureSink writes only to caller-provided capture staging and returns stable
snapshot refs/digests; it cannot publish a complete package or choose identities for native occurrences.
Record-level ID allocation comes from the core IdentityService, supplied to sink/context services.

## 4. Contexts, ownership and core services

Adapters are constructed by
`make_connection(component: ComponentRef, services: AdapterServices) -> AdapterPorts`.
AdapterServices = {identities:IdentityService, records:RecordBuffer, registry:ContractRegistry}.
The core supplies stable component identities and declaration records before describe; adapters do not
invent a fresh component ID on each call. RecordBuffer holds staged metadata/diagnostics without implicit
filesystem publication. Every returned diagnostic reference must resolve in returned records or this buffer.

BindContext = {services:AdapterServices, observation_scope:Scope}.
ReadContext = {access:Ref(policy), resolver:Resolver, identities:IdentityService, records:RecordBuffer}.
PrepareContext = {write_scope:Ref(policy), identities:IdentityService}.
DecodeContext = {resolver:Resolver, mappings:MappingRegistry, identities:IdentityService}.
ExecutionContext = {grant:ExecutionGrant, attempt:AttemptRef, handle_registry:HandleRegistry, action_channel:ActionChannel|None}.
DeliveryContext = {grant:DeliveryGrant}; CancellationContext = {grant:CancellationGrant}.
AssessmentContext = {resolver:Resolver, services:AdapterServices}.
WriteContext = {write_scope:Ref(policy), resolver:Resolver, services:AdapterServices}.
ComponentRef, AttemptRef and AssessmentRef abbreviate their typed SC-1 references. The core creates the prospective attempt
identity under the bound request/grant; actual start still needs evidence. Shared services do not carry a
default execution grant. Services are supplied explicitly, not found through global state.

ObserverEvidence = {observer_only:Ref[], mappings:Ref(mapping)[]} is a core-side value, not part of
PresentedBundle passed to native binding/invocation. Decoder/evaluator access is separately scoped.
Reference selection enforces the declared presentation boundary; it is not proof that an unsandboxed native
program could not access information through an unobserved channel. Such access remains an explicit
observability limit. None is a runtime-only optional channel value and is never serialized as wire unknown.

ExecutionGrant = {request:RequestRef, attempt:AttemptRef, operations:Contract[], effects:Code[],
presentations:Ref(presentation)[], policies:Ref(policy)[], authority:Ref(authority_evidence),
runtime_capability:OpaqueRuntimeCapability}.
DeliveryGrant = {action:Ref(action_request), response:Ref(action_response), endpoint:Ref(endpoint),
effects:Code[], policies:Ref(policy)[], authority:Ref(authority_evidence), runtime_capability:OpaqueRuntimeCapability}.
CancellationGrant = {attempt:AttemptRef, policies:Ref(policy)[], authority:Ref(authority_evidence),
runtime_capability:OpaqueRuntimeCapability}. Their exact operation/effect must match the target.
Runtime capabilities/handles are caller-issued opaque
objects; parsing a native declaration cannot construct one. A legacy invocation still honors its existing
allow_spend/cap guards; a new descriptor is not a bypass. AdapterPorts is a collection of the optional
callables in section 2, with describe required; missing callables mean unsupported ports, not fake stubs.

These runtime service objects are not serialized by dumping arbitrary object attributes. A grant references
the exact request, operation, audience, resource/cumulative scope and permitted effects. It is supplied by
the execution/policy owner and checked at the boundary; boolean capability declarations do not create it.
Caller policy determines when execution is authorized. No current task grant exists to run these proposals.

Resolver reads declared locations under access policy, verifies exact snapshots when possible and returns
availability/integrity observations. It does not silently fetch external schemas or scan unrelated paths.
IdentityService persists occurrence IDs/associations and idempotent import keys; equality of bytes alone
does not identify runs. MappingRegistry resolves explicit versioned mappings; it does not infer aliases
from names/shape. HandleRegistry matches supported native identities and preserves duplicate-launch doubt.

Exact core entry-point declarations:

```text
resolve(reference: Ref, context: ReadContext) -> Op[ResolvedRecord]
validate(package: Package, profiles: Contract[], context: ReadContext) -> ValidationReport
assess(rule: Contract, subjects: Ref[], basis: Ref[], parameters: Ref[],
       context: AssessmentContext) -> Op[AssessmentRef]
publish(staged: Package, policy: PublicationPolicy,
        context: WriteContext) -> Op[PublishedPackage]
select_current(alias: SelectionAlias, selection: Ref(selection),
               expected_previous: K(Ref(selection)),
               context: WriteContext) -> Op[SelectionReceipt]
import_legacy(record: LegacyRunRecord, binding: LegacyBinding,
              source: SourceSpec, context: ReadContext,
              sink: CaptureSink) -> Op[EvidenceDelta]
project_legacy(package: Package, selection: LegacySelection,
               context: ReadContext) -> Op[LegacyProjection]
```

ValidationReport = {checks:Ref(check)[], gaps:Ref(gap)[], claims_satisfied:Contract[],
claims_withheld:Contract[]}. It is not an all-valid scientific verdict.
SelectionAlias = {namespace:ID, name:String}; SelectionReceipt = {alias:SelectionAlias,
previous:K(Ref(selection)), selected:Ref(selection), generation:Index}.
Alias updates use compare-and-swap against expected_previous and the caller's write scope; conflict returns
a diagnostic instead of overwriting another selection. Immutable selection records/bases remain unchanged.
PublicationPolicy = {allowed_profiles:Contract[], required_checks:Contract[], backend:Contract,
destination:Ref(location)}. PublishedPackage = {package_id:ID, location:Ref(location), manifest_digest:Digest,
published_records:Ref[]}. ResolvedRecord = {record:Record, availability:Ref(observation)[],
integrity:Ref(check)[]}. Published manifests pin exact snapshots; current pointers remain separate records.

## 5. Legacy baseline and mapping: legacy to new

Read-only source inspection for this proposal: audit/core/{adapter,runs,graph,harness,evidence}.py,
audit/{collect.py,metrics/l0.py,controls/l1.py,report/certificate.py,rerun/existing.py},
audit/systems/{_methods,_probe,causal_copilot}.py and audit/trace/stages.py.

LegacyBinding = {system:Ref(component), item:String, arm:String, domain:Ref(domain),
coordinate_basis:shown|original|unresolved, mapping:K(Ref(mapping)), source_identity:K(NativeIdentity),
legacy_contract:Contract}. Unknown original request/attempt is allowed; never fabricate one solely to
attach an old (system,item,arm) tuple.

| Existing field/behavior | New representation | Compatibility restriction |
|---|---|---|
| system,item,arm | Subject/battery/condition associations under LegacyBinding | Tuple is not universal execution identity; repeated runs can share it |
| status | Sourced legacy-status claim and scoped outcome evidence | Do not promote wrapper status to independently established native termination |
| graph.n and integer positions | Finite domain and explicit original/shown schema binding | Need known coordinate basis; never map twice |
| directed/undirected/bidirected/partial | Typed legacy-graph representation with exact mark semantics and raw source where available | A legacy undecided conversion may already have lost native endpoint properties |
| graph.raw | Captured encoding/view linked to its original convention | It is not proof every original native artifact survives |
| variants and stages | Related output objects with stage/variant role and observed/reconstructed provenance | Not additional independent attempts; external ablation reruns need distinct occurrence evidence |
| edge_source | Native/legacy label observations tied to mapped propositions | Reported source labels are not measured causal attribution |
| confidence | Q descriptors only where proposition/conditioning/coordinates are established; otherwise native report/gap | Nonempty data or a capability flag alone does not establish semantics |
| cost | Q resource observations with units, source and coverage | Missing values stay unresolved; do not reinterpret all usd as billed actual dollars |
| failure | Diagnostic/source error with phase and attribution basis | Heuristics remain attributed legacy classifications, not independent proof |
| files | Artifact/location/digest claims and exact selectors | Digest claims are reported until actually checked; lost files do not prove no execution |
| notes | Known fields get explicit contracts; remainder preserved as legacy source artifact/extension | Never discard unknown notes while claiming a lossless bridge |
| notes.replicates | Occurrence/grouping evidence with original selection/order retained | Historical label does not prove independent scientific replicates or checkpoint continuity |

Legacy statuses specifically:

- ok proves the legacy wrapper accepted a graph because RunRecord enforces that condition. It does not alone
  prove native normal termination, requested-scope fulfillment, complete capture or causal correctness.
- failed preserves the wrapper's failure attribution; stronger native attribution needs source evidence.
- aborted_cap, aborted_quota, interrupted and host_error preserve their distinct legacy classifications
  and evidence. They are not reclassified as native crashes. A resumable comment does not prove a checkpoint.
- not_run preserves that classification. Some importers return it when a source summary/state is missing;
  missing local evidence does not prove the original system never ran. Keep this distinction in the new view.

## 6. New to legacy: partial and explicit

LegacySelection = {source_records:Ref[], graph:Ref(output), outcome_basis:Ref(assessment),
coordinate_mapping:Ref(mapping), variants:Endpoint[], stages:Ref(output)[],
legacy_labels:LegacyBinding, projection_rule:Contract}.
LegacyProjection = {record:LegacyRunRecord, provenance:Ref[], lost_guarantees:Code[],
limits:Ref(gap)[], contract:Contract}.

Projection is defined only when a selected graph, statuses, domain and required legacy fields are supported
under an explicit rule. No arbitrary latest/best-scoring object is selected. A distribution/local response/
abstention/model artifact without an explicitly authorized graph derivation cannot become legacy ok.
Unknown outcome cannot be forced into failed or not_run to satisfy the enum. Return rejected with preserved
evidence instead. A graph projection with lost endpoint/coverage meaning is identified as lossy and cannot
satisfy a faithful-native-view claim.

Status mapping for new prospective data requires evidence that satisfies the selected legacy rule. Multiple
simultaneous facets can make projection undefined. In particular, delivered output followed by failure must
not be silently converted to ok just because a graph exists. Legacy echo mode for existing reruns returns
the preserved original legacy fields; it does not pretend the new distinctions existed historically.

## 7. Exact consumer constraints and discovered compatibility seams

- audit/core/harness.map_back maps graphs, variants, edge sources and stages, but does not map confidence.
  The new generic mapping must cover every claimed typed field. Do not retrofit historical confidence
  coordinates or alter shared scoring silently; quarantine unsupported legacy associations as gaps.
- audit/core/harness.present currently requires unique shown names. The new domain contract permits duplicate
  display labels, but a route through that old helper must retain its narrower prerequisite and reject
  unsupported duplicates. New support elsewhere does not change the old helper's capability.
- audit/collect.collect runs recorded mode only. A class advertising live/replay or returning a command
  does not establish that this collector executes it. _probe.command prepares a run-sheet specification.
- audit/collect.score_all can score variants of failed runs; preserve those objects and the old branch.
- audit/metrics/l0 applies its own random-orientation/committed/DV-1 rules and tier labels. New marked graphs
  are not automatically eligible; do not copy/replace those algorithms in the connection core.
- notes.file_read affects the legacy scoring seed (e.g. intervention twin paths). Preserve the exact value
  and mapping; normalizing filenames can change historical numbers.
- CausalCopilot.recorded selects the last stored run and keeps earlier ones as replicates. all_runs includes
  those earlier records. New identity rules do not change that historical denominator/selection by default.
- audit/trace/stages computes last-changed-stage attribution. A reconstructed stage/source is retained as
  that derivation, not promoted to native proof of which information caused an edge.
- audit/core/evidence.pointer_get accepts both empty pointer and '/' as root. SC-1 uses standard JSON-pointer
  meaning; the legacy helper remains untouched and any bridge declares its legacy selector contract.
- Existing certificate bodies, pointers, file hashes, exact counts, numeric tolerances and verdicts stay
  on their legacy path until an adopted migration. New connection records do not silently add a certificate
  field or change the certified number set.
- RunRecord.summary omits confidence, edge sources, notes/stages/replicates and full variant payloads;
  Graph.canonical omits raw. Neither is a lossless bridge source. Capture all original fields with an
  explicit legacy codec and retain raw source artifacts; never substitute default=str serialization.

Recommended first integration is additive: legacy reruns remain the authority for existing public reports;
new packages can reference/import that evidence. Bidirectional echo/projection tests demonstrate supported
cases, while intentional nonrepresentable cases must reject honestly. Compatibility is a named partial
mapping, not a universal round-trip claim.

## 8. Acceptance cases and status

Required future checks: recorded-only adapter without invoke; prepared command without readiness claim;
missing dependency; duplicate labels on a restricted legacy route; shown-to-original mapping exactly once;
confidence coordinate mismatch; invalid native DAG; parser failure preserving raw data; failed run with
stage objects; retry/import identities; partial transport acknowledgment; replay without fresh fallback;
unsupported distribution-to-legacy conversion; exact legacy-status/replicate/file_read preservation.

No code or tests were written. The signatures, closed result shapes, concrete bridge and consumer seams are
now available for final design review. Any chosen public API/certificate/protocol change remains a proposal
to W5 until adopted. Implementation and native/API execution require separate authorization.

## Where we're going

Review the complete subsystem-1 package and resolve any targeted changes. Then use its bundle plan to build
and validate incrementally, preserving legacy parity and every existing certificate contract.
