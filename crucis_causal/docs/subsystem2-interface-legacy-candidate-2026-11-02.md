# Subsystem 2: exact interface, S1 handoff and legacy candidate

Tickets: DLV-08, DLV-09; related DLV-10, DLV-06/07 and ADV-01.
Date: 2 Nov 2026, America/Los_Angeles.
Status: proposed API/ownership and compatibility design requested by Uzair. No
functions/classes below are implemented by this document. No native/paid jobs,
S1 changes, CLI redirects, result migrations or public protocol adoption.
Companion: [SC-2 wire candidate](subsystem2-serialization-candidate-2026-11-02.md).
Follow-on [contract closure](subsystem2-contract-closure-2026-11-02.md) supplies
exact injected services and revises resolve_slots, bind_run, bind_evaluation,
link_evidence and context/reference typing. Those refinements supersede the initial
signatures below for the [final review candidate](subsystem2-final-design-review-2026-11-02.md).
Basis: [family/profile contract](subsystem2-family-profile-lifecycle-contract-2026-11-02.md)
and inspected `audit/connections/{api,ports,core,services,model,legacy}.py`,
`audit/core/{battery,runs,canon}.py`, `audit/collect.py` and controls source.

## 1. Ownership and effect boundaries

S2 owns scientific definitions, composition/readiness assessments, metadata
resolution/projection and analysis-population bindings. It does not invoke a native
system, schedule trials, select unauthorized actions, generate real sealed data,
authorize spend, compute new scientific metrics or assign finding verdicts.

S1 owns native connection/evidence contracts and existing ports. S3 will coordinate
authorized transformations/materialization, execution, state, recovery, action
delivery and grants. S4 computes the specified measurements/statistics; S5/S6 own
findings/reporting. Pure registered family readers may interpret supplied evidence
under explicit read access; selecting a reader never installs code from a record URI.

S2 is an opt-in layer. Existing `audit` routes/results and S1 packages remain valid
under their existing contracts. No adapter acquires an invoke/prepare/decode port
merely because an S2 task asks for one. Native capability and binding evidence stay
separate from scientific eligibility and authorization.

## 2. Proposed runtime values

These are closed conceptual runtime shapes; tuples are immutable API sequences,
not wire arrays. Ref in an S2 slot uses the SC-2 resolver; S1Ref explicitly means
an existing SC-1 reference in its supplied S1 record/package context.

| Value | Exact fields and meaning |
|---|---|
| PlanIssue | code:Code, path:String, message:String, evidence:tuple[Ref]; runtime parse/operation diagnostic, not a native failure |
| RecordDelta | records:tuple[S2Record], roots:tuple[Ref]; new staged S2 records only |
| PlanOp[T] | state:completed\|partial\|rejected, value:T\|None, additions:RecordDelta, diagnostics:tuple[PlanIssue] |
| ReaderLimits | max_manifest_bytes:Index, max_records:Index, max_packages:Index, max_external_bytes:Index, max_reference_depth:Index, max_parameter_depth:Index; all positive, no implicit unlimited value |
| PackageView | package:SC2Package, source_bytes:bytes, snapshot_digest:Digest, resolved_packages:tuple[ResolvedPackage]; view of exactly supplied/resolved snapshots |
| ResolvedPackage | package_id:ID, format:Contract, source_bytes:bytes, digest:Digest, records:tuple[S2Record\|S1Record]; one declared supported package format per snapshot, no mixed local catalog |
| ResolvedPlanRecord | record:S2Record\|S1Record, package_id:ID, availability:tuple[Ref], integrity:tuple[Ref]; cross-package resolution retains the actual namespace/format, with no implicit guarantee beyond evidence |
| PlanValidationReport | assessments:tuple[Ref(assessment)], requested:tuple[ProfileClaim], satisfied:tuple[ProfileClaim], withheld:tuple[ProfileClaim], issues:tuple[PlanIssue] |
| ResolutionDraft | receipt:Ref(resolution_receipt), selected:tuple[Ref], outstanding:tuple[Ref(requirement)] |
| RunBindingDraft | binding:Ref(run_binding), outstanding:tuple[Ref(requirement)], assessments:tuple[Ref(assessment)] |
| S1RequestProjection | request:S1Ref(request), attempt:S1Ref(attempt), presented:S1.PresentedBundle, route:S1.RouteSpec, s1_records:tuple[S1Record], provenance:tuple[Ref], assessments:tuple[Ref(assessment)] |
| ProjectionOccurrence | request_id:ID, attempt_id:ID; allocated once by the coordinator's supplied identity service, never inferred from content |
| EvaluationBindingDraft | binding:Ref(evaluation_binding), population:Ref(analysis_population_receipt), outstanding:tuple[Ref(requirement)] |
| CommitmentEvidence | subject:ContentBinding, event:Ref(lifecycle_event\|s1.event), assurance:Ref(parameter_set), exposure:tuple[Ref(exposure_receipt)] |
| AmendmentEvidence | event:Ref(lifecycle_event\|s1.event), affected:Scope, reason:Code, explanation:Ref(parameter_set\|s1.artifact_snapshot), prior_observed:IndexList(Ref) |
| LegacyImportSource | occurrence_id:ID, captured_sources:tuple[S1Ref], legacy_contract:Contract, source_identity:K(NativeIdentity); no implicit path lookup or arbitrary object deserialization |
| LegacyImportScope | kind:battery_manifest\|run_record\|audit_spec, bindings:Ref(parameter_set), interpretation_claims:tuple[Contract]; exact source-scoped selection/context and gaps |
| LegacyImportDelta | receipt:Ref(import_receipt), roots:tuple[Ref], s1_evidence:tuple[S1Ref], losses:tuple[PlanIssue] |
| LegacyProjectionPolicy | rule:Contract, selection:Ref(parameter_set), require_lossless:Boolean; an explicit legacy target and selection rather than a global downgrade |
| LegacyProjectionDelta | projections:tuple[S1.LegacyProjection], provenance:tuple[Ref], losses:tuple[PlanIssue]; no implicit new native record or scientific metric |

PlanOp is deliberately not an alias for S1.Op: S1.Op diagnostics must be s1.gap
references. PlanIssue can describe an input parse error before a valid S2 record
exists; a persisted issue uses s2.diagnostic with its actual source/context. S1
rejections remain sourced S1 evidence and can be linked, never cast into native
failures. Rejected has no value and nonempty diagnostics. Partial retains a useful
value with scoped unestablished work. Completed means the metadata operation ran;
report.satisfied/withheld and named assessments determine profile claims, not
that operation state. Assessing a false predicate can complete successfully.

No grant, native handle, resolver callable or runtime capability is serialized by
attribute inspection. Descriptive wire references are not those runtime objects.
PlanOp.additions describe staging only; no API below publishes or starts work.
Rejected operations return an empty RecordDelta and do not commit partial staging.
Partial operations retain their useful value and explicit outstanding work. The
bytes-only encode_package entry point raises a typed encoding/structural error
on rejection; it never returns partially encoded publication bytes.

## 3. Injected contexts

PlanReadContext = {limits:ReaderLimits, resolver:PlanResolver, registry:FamilyRegistry,
access:ReadAccess}.
DraftContext = {read:PlanReadContext, identities:IdentityService,
records:S2RecordWriter, author:Ref(component), clock:ClockService}.
PlanAssessmentContext = {read:PlanReadContext, draft:DraftContext,
procedures:AssessmentRegistry}.
S1ProjectionContext = {draft:DraftContext, s1_records:S1RecordWriter,
s1_identities:IdentityService, s1_registry:S1.ContractRegistry,
s1_recorder:S1Ref(component), compiler:S1Ref(component)}.
LegacyContext = {draft:DraftContext, s1_read:S1.ReadContext,
s1_capture:S1.CaptureSink, s1_services:S1.AdapterServices}.

The injected writer/identity services have explicit staging/occurrence scopes.
Current S1 IdentityService.allocate can supply UUID identities under its existing
contract; S1 Builder/RecordBuffer remain SC-1 writers and are not used as an S2
package builder. A new S2 writer needs its own producer/catalog/format identity.
S1 bridge records identify the actual recorder and compiler/procedure with correct
implementation provenance. They do not label S1's default code manifest as S2 code.

PlanResolver only consumes explicitly supplied packages or access-approved snapshot
sources and supported exact-format readers. ReadAccess constrains those effects;
a wire policy reference does not grant filesystem, network or protected-store access.
Reader limits and authority are caller-supplied, never loaded as executable settings
from an untrusted native record. No context above includes ExecutionGrant,
DeliveryGrant, CancellationGrant or permission to dispatch an action.

## 4. Exact proposed core signatures

Function names/signatures are candidate interfaces, not current Python exports.
Every returned reference must resolve in supplied snapshots or returned staged
records, or use an explicit unresolved form. Single-valued resolution and unknown
critical families cannot become ready through an implicit fallback.

| Function | Signature and bounded behavior |
|---|---|
| read_package | read_package(data:bytes, context:PlanReadContext) -> PlanOp[PackageView]; strict parse supplied bytes, no implicit external retrieval |
| encode_package | encode_package(view:PackageView) -> bytes; SC-2 canonical encoding after required structural checks, no publication or scientific reinterpretation |
| resolve | resolve(reference:Ref, context:PlanReadContext) -> PlanOp[ResolvedPlanRecord]; exact local/external identity/type/byte checks within supplied access and limits |
| assess | assess(roots:tuple[Ref], claims:tuple[ProfileClaim], context:PlanAssessmentContext) -> PlanOp[PlanValidationReport]; only installed named procedures, no new metric/statistical/native evaluation |
| resolve_slots | resolve_slots(requirements:tuple[Ref], candidates:tuple[Ref], context:DraftContext) -> PlanOp[ResolutionDraft]; use the requirements' fixed rules, not a caller-selected best/latest rule |
| record_materialization | record_materialization(spec:Ref(transform_spec), evidence:tuple[Ref], realized:Ref(parameter_set), context:PlanAssessmentContext) -> PlanOp[RecordDelta]; validate/bind supplied realization evidence, do not execute a transformation or generate data |
| bind_run | bind_run(plan:Ref(plan_snapshot), trial:Ref(trial_slot), resolution:Ref(resolution_receipt), context:PlanAssessmentContext) -> PlanOp[RunBindingDraft]; derive exact task/condition/subject from fixed intent and permitted resolutions |
| project_request | project_request(binding:Ref(run_binding), occurrence:ProjectionOccurrence, recipient:S1Ref(component), route:S1.RouteSpec, context:S1ProjectionContext) -> PlanOp[S1RequestProjection]; stage metadata using exact supported projection rules, no bind/invoke/grant |
| record_handoff | record_handoff(binding:Ref(run_binding), occurrence:ProjectionOccurrence, s1_snapshot:ResolvedPackage, context:DraftContext) -> PlanOp[RecordDelta]; qualify request/attempt against a verified immutable SC-1 snapshot and emit the S2 request-binding receipt |
| link_evidence | link_evidence(subjects:tuple[Ref], s1_evidence:tuple[S1Ref], context:DraftContext) -> PlanOp[RecordDelta]; sourced associations, with original unknown identity preserved rather than fake requests/attempts |
| record_population | record_population(comparison:Ref(comparison), evidence:tuple[Ref], context:PlanAssessmentContext) -> PlanOp[RecordDelta]; apply declared selection/cardinality/weighting rules and retain missing/unmatched identities, without computing metric values |
| bind_evaluation | bind_evaluation(plan:Ref(plan_snapshot), comparison:Ref(comparison), population:Ref(analysis_population_receipt), references:tuple[Ref(reference_definition)], context:PlanAssessmentContext) -> PlanOp[EvaluationBindingDraft]; validate the bound reference-selection rule, never choose the highest-scoring reference |
| record_commitment | record_commitment(plan:Ref(plan_snapshot), evidence:CommitmentEvidence, context:DraftContext) -> PlanOp[RecordDelta]; account for supplied chronology/content evidence, do not create external assurance or publish/register a plan |
| record_amendment | record_amendment(previous:Ref(plan_snapshot), revised:Ref(plan_snapshot), evidence:AmendmentEvidence, context:DraftContext) -> PlanOp[RecordDelta]; preserve old/new content and exposure, do not authorize revised work |
| import_legacy | import_legacy(source:LegacyImportSource, scope:LegacyImportScope, context:LegacyContext) -> PlanOp[LegacyImportDelta]; use exact installed source readers/S1 legacy capture, retain reconstruction gaps |
| project_legacy | project_legacy(bindings:tuple[Ref], policy:LegacyProjectionPolicy, context:LegacyContext) -> PlanOp[LegacyProjectionDelta]; explicit source-backed echo or a supported declared lossy projection, never silent repeat collapse |

ID allocation is idempotent only for a declared occurrence and unchanged bound
inputs. Reusing a supplied occurrence/record ID with different content is rejected;
equal bytes under a new occurrence do not merge it. Existing requests are reused
only with their exact stored identity/content and compatible intent. New attempts
can refer to the same request under declared recovery; changed intent requires a
new request and explicit relationship. Never refresh created_at on an old record.

## 5. S1 field mapping and native boundary

The compiler stages only existing SC-1 record kinds and field shapes. Its recipient,
route, presentation and completion semantics must be supported by installed exact
S1 registry contracts; unknown operations are gaps, not auto-installed handlers.

| S2 meaning | Exact S1 destination / obligation |
|---|---|
| Task operation | s1.request.operation equals RouteSpec.operation; existing route registration required |
| Concrete target/domain | s1.request.task_scope using S1 scopes/domains/propositions; no S2 records inserted as local S1 subjects |
| Required native outputs | s1.request.deliverables roles/contracts/scopes/required/abstention under supported response projection |
| Cardinality, alternatives and scientific parameters | Named supported S1 completion rule/parameters, with exact parameter snapshots/propositions; no lossy flattening to a simple required flag |
| Completion | s1.request.completion and completion_parameters; response fulfillment remains separate from scientific correctness |
| Permitted native information | s1.request.presentation_policy plus PresentedBundle.permitted_policy and scoped s1.presentation records |
| Resource/recovery intent | s1.request.resource_policy / recovery_policy references; no runtime authority created |
| Source payload or endpoint | s1.presentation payload/endpoint/domain/schema and recipient, with prospective attempt association |
| Route | s1.request.route and RouteSpec.route_kind/transport/operation/parameters matched to actual support |
| Prospective occurrence | s1.request and s1.attempt IDs supplied once; initial-state intent does not prove native start or loaded-state restoration |
| Observer provenance | S1 recorder/compiler component identities and permitted provenance/parameter snapshots, not whole private S2 plans as native inputs |
| S2 association | A later s2.request_binding_receipt externally pins the exact S1 request/attempt package; S1 wire schema remains unchanged |

Where a response/task parameter cannot be represented by a supported S1 rule,
withhold the affected runnable projection. Retain the S2 definition and diagnostic;
do not silently simplify native outputs, add arbitrary S1 fields or create a fake
successful fulfillment assessment. A names-only/local/temporal/learned route must
keep the actual native scope and supported interpretation.

The existing S1 adapter call surface remains:

| Port | Existing arguments; coordinator responsibility |
|---|---|
| describe | describe(); obtain actual SupportDeclaration, not scientific validity |
| bind | bind(request, presented, route, inventory, context); checks route/policy/dependency metadata, not execution authority |
| read | read(source, context, sink); supplied recorded snapshot reads within explicit scope |
| prepare | prepare(bound, context, sink); only for an actual supported port |
| invoke | invoke(spec, context, sink); only S3/operator with actual ExecutionContext/grant |
| observe | observe(handle, cursor, limit, context, sink); bounded observation, no invented native completion |
| decode | decode(source, request, context); supported native artifact interpretation, not automatic scientific scoring |
| deliver | deliver(response, channel, context, sink); actual DeliveryContext/grant, no evaluator-generated unauthorized answer |
| cancel | cancel(handle, context, sink); actual CancellationContext/grant, cancellation request is not proof of stop |

S2 projection does not call those effectful ports. Creating prospective request,
attempt or presentation records is metadata only and does not establish launch,
delivery, access, use or actual native independence. S3 retains the existing S1
authority/effect checks and the user's actual authorization scope.

## 6. Snapshot publication without a digest cycle

Separate chronological snapshot roles:

1. P: frozen S2 definitions/commitment target; M: later S2 source/input resolutions
   referring to P and actual source evidence.
2. R: prospective SC-1 request/attempt/presentation metadata. Its observer provenance
   can identify already fixed P/M and exact projection parameters, never a future
   handoff receipt that will pin R itself. Only permitted presentations reach native.
3. H: new S2 request-binding receipt pins R. Native dispatch remains S3's decision.
4. O: later immutable S1 observations/output snapshot, preserving identical earlier
   record identities where copied. It never rewrites R's published bytes/ID.
5. E: later S2 evidence/population/evaluation bindings pin the actual O and P/M/H.

S1 Builder.package currently exposes a mutable staging builder's package identity.
The integration must not publish R, append records, then republish different bytes
under the same identity. The publication boundary needs a fresh snapshot identity
and exact copied record contents/reference closure for each distinct frozen set.
A wrapper can stage an independent immutable snapshot without changing the S1
wire schema; reference-qualified/self-package dependencies must be checked, not
blindly relabeled. Implementing/testing that boundary remains a later bundle gate.

S1 runtime-local refs stay in their actual record context; persisted S2 links are
qualified against the published S1 package snapshot. If durable prospective R/H
is required by an execution policy, missing publication/pins block that admission
claim. If only an incomplete old observation exists, preserve its gap instead of
inventing a prior dispatch receipt. Internal copied record equality and package
byte identity are different checks; no recursive self-digest is required.

## 7. Legacy import mapping

Imports preserve original encoded objects/manifests and supplied raw evidence
through S1 snapshots; interpretation is an additional record. Use existing safe,
named S1 legacy readers/capture APIs, never arbitrary pickle/class loading or
silent current defaults to reconstruct unknown original intent.

| Legacy source | S2 meaning and required limit |
|---|---|
| Battery id/version | Source-scoped collection identity/reconstruction; not global case identity or a scientific commitment |
| Battery.items | Capture actual manifest/membership/order at the import occurrence; later source mutation is another snapshot |
| Battery.hash() | Preserve as reported/cached legacy hash with basis. Fresh capture byte/hash observations are separate; neither overwrites historical pins |
| Battery.generator/visibility | Source declarations with exact public metadata only; sealed label is no permission/blindness proof or seed-store lookup |
| Item.item_id | Alias scoped by source battery/version/manifest; no filename-only cross-battery deduplication |
| Item.cluster | Historical analysis-group declaration, not proof of source independence or the only future dependence structure |
| Item.family | Source family/stratum label, not a complete semantic contract or common cohort |
| Item.n | Variable count in the inspected builders; never silently observation/sample count |
| Item.files | Role/locator/reported hash plus actual snapshots when explicitly accessible. Missing files remain declarations/gaps; no fabricated digest |
| Item.reference | Separate reference definition with source kind/arm/tier/applicability. T4 remains diagnostic-only inside its declared control |
| Item.arms/meta | Declared/reconstructed condition and label/context metadata. Listed arms are not evidence of native execution or complete planned populations |
| collect's skipped/unlisted arms | Preserve the observed legacy selection behavior; do not reinterpret it as proven scientific inapplicability or invent unexecuted original trials |
| RunRecord(system,item,arm) | Source-scoped labels and observed/reported record content. A fresh S2 scientific trial is created only when original plan/occurrence evidence supports that association |
| status=ok | Legacy graph-returned meaning; not proof of all deliverables, normal termination, complete capture or scientific correctness |
| failed / infrastructure / not_run | Preserve exact legacy status and reported attribution separately from evidence. Do not change historical crash/score rules or infer absent native production from missing local source |
| graph / variants / stages | Distinct S1 objects/roles and coordinates. Surviving stage can be useful after failure; native variant is not a new independent experiment |
| notes.replicates | Earlier recorded occurrences/attempts under the legacy contract, including retries; not automatic independent scientific repetitions |
| confidence / edge_source | Preserve native report and known scope/coordinates. Source labels do not establish causal contribution; existing unresolved semantics remain explicit |
| cost | Reported estimates/amounts and source scope, not invoices/current quotes or zero for missing. Failed/retry and cumulative/overlap accounting remains explicit |
| scored[(item,arm)] | Existing key space is not a per-repetition identity. New trials cannot be stuffed into it with silent overwrite |
| audit specs/metrics/certificates | Pin their exact source/version and call unchanged legacy measurement logic for compatibility; do not duplicate or reinterpret it inside S2 |

Original request/attempt, chronological commitment, sampling rule and native identity
may remain unresolved. S1 import_record already avoids fabricating a native request
or attempt. Its current legacy snapshot is an encoded RunRecord value; echo of that
value is not automatically byte reproduction of every original native file. Keep
captured original files and their actual availability/integrity claims separately.

Reusing an import occurrence with identical inputs is idempotent through explicit
persistent identity maps. Changing inputs under that occurrence is a conflict;
a new capture occurrence with equal bytes remains distinct. Shared scientific case
associations require their own evidence and never follow from equality alone.

## 8. Back projection and compatibility gates

Two projection questions remain distinct:

- Source-backed echo: existing S1 echo restores its exact encoded legacy value at
  that contract's scope, with unknown original facts still unknown.
- Declared compatibility view: a caller selects supported S2/evidence bindings and
  an explicit projection rule, using S1 LegacySelection/LegacyProjection for the
  actual representable native objects and outcomes. Lost guarantees are reported.

One legacy (system,item,arm) key cannot hold arbitrary repeated trials, local sets,
learned domains, temporal graphs, posterior collections or alternative references.
Require an explicit justified one-record selection/partition for a narrow supported
view, or reject the projection. Never pick the last/best successful repeat, collapse
particles, coerce a partial object to DAG, synthesize failure graphs or discard
unmatched outputs just to satisfy that key shape. require_lossless rejects any
projection needing such loss; a declared lossy view never claims full equivalence.

Preserve the old route as the default until owner-adopted changes. Future S2 bundles
must show unchanged stored-number comparison keys/counts within 0.001 and all
existing certificates verifying, plus appropriate new scoped acceptance cases.
S1's existing release evidence remains its own source; no tests were rerun here.
No migration, port_map, W1 number registry, exporter pin or B5/shared code is changed.

## 9. Choices, alternatives and costs

All choices below are proposals in this pass, not newly attributed user decisions.

| Choice | Strongest alternative | Cost and failure prevented |
|---|---|---|
| Separate SC-2 scientific package with explicit S1 links | Extend SC-1 with all experiment records | Costs a second catalog/resolver and handoff. Preserves the closed existing S1 contract and separates experimental intent from native evidence |
| Immutable package snapshots; record identities can persist unchanged | One growing published package retaining its ID | Costs additional snapshots/pins and publication checks. Prevents a prior commitment or handoff silently identifying different bytes |
| Fixed rules resolve later-bound slots; later receipts record actual values | Materialize every value before freezing any plan | Costs requirement/receipt links and scoped readiness. Supports adaptive/generated cases without fabricating early knowledge or choosing later outcomes opportunistically |
| Pure S2 entry points; effects and runtime authority stay with S1/S3 | One plan object both describes and runs the experiment | Costs coordinator orchestration. Prevents metadata conformance or imported policy text being treated as execution/spend authority |
| Source-scoped legacy interpretation with explicit unknowns | Populate new scientific fields from legacy labels/defaults | Costs gaps and narrower historical claims. Prevents false sample counts, independence, chronology, original trial populations and native completion |
| Named selection/loss accounting or rejected legacy projection | Automatically choose one latest/best result per legacy key | Costs caller-specified views and some unsupported conversions. Prevents overwritten repetitions, cherry-picking and scientific meanings silently lost in a narrow record |

Evidence for the compatibility choices is the inspected source behavior in
sections 5-8, not a newly executed experiment. Exact callable protocols for injected
family/projection/assessment registries and record writers still need the final
API specimen pass alongside parameter-role schemas. The entry-point signatures
above settle inputs/outputs and ownership, not the existence of those services.

## 10. Review gates before implementation

| ID | Required candidate acceptance case |
|---|---|
| B01 | Strict SC-2 payload/reference and semantic profile checks preserve unknown/critical extension limits |
| B02 | Each supported task projects only existing S1 fields, policies, recipients and permitted payloads |
| B03 | Unsupported operation/completion/cardinality or source family withholds runnable projection without native calls |
| B04 | S2 producer and S1 recorder/compiler identities accurately bind their actual implementations |
| B05 | Prospective IDs do not imply native start; retries preserve request intent and distinct attempt identities |
| B06 | P/M/R/H/O/E snapshot chain has no self-digest/future-outcome dependency or reused changed publication ID |
| B07 | Source-backed legacy echo retains reported statuses, stages, costs and unresolved original history |
| B08 | Item n, cluster, arms and replicates receive the exact scoped legacy mapping, not scientific defaults |
| B09 | Rich/repeated evidence cannot silently collapse into the legacy item/arm score key |
| B10 | Negative/partial/private/late-bound A-H cases remain traceable under the candidate and lossless/lossy profiles |
| B11 | Native side-effect ports and runtime grants remain S3/S1 responsibilities, never created by S2 metadata conformance |
| B12 | Historical result/certificate parity and owner-controlled adoption remain separate from new design validation |

These are future design/implementation must-show requirements, not passed runtime
tests. Before freeze, transcribe exact parameter-role schemas and A-H wire/API
specimens; close cross-reference/cardinality and snapshot-publication details;
verify exact native contract support and legacy loss boundaries; then perform final
subsystem-2 review and bundle planning. No implementation go has been given.

## Where we're going

Review SC-2 and these signatures/mappings together. The next bounded pass should
transcribe the role schemas and examples, resolve any exposed type/phase/projection
gaps, and freeze only what that review establishes. Keep scientific procedure and
owner-policy gaps explicit; do not fill them with convenient serializer behavior.
