# Subsystem 2: parameter, service and composition closure candidate

Tickets: DLV-08, DLV-09; related DLV-10, DLV-06/07 and ADV-01.
Date: 2 Nov 2026, America/Los_Angeles.
Status: design closure requested by Uzair; proposed contract, not implementation,
user acceptance of every detail, public adoption or permission to build.

This note and its [catalog](subsystem2-contract-catalog-2026-11-02.json) refine the
[wire candidate](subsystem2-serialization-candidate-2026-11-02.md) and
[interface candidate](subsystem2-interface-legacy-candidate-2026-11-02.md).
The catalog is a declarative design artifact, not an installed schema or registry.
The [specimen manifest](subsystem2-specimens-2026-11-02/manifest.json) identifies
synthetic wire packages, negative mutations, source mappings and API scenarios.
Earlier A-H logical registries remain unchanged historical review sources.

## 1. Incompatibilities exposed and proposed resolutions

| ID | Incompatibility or underspecified boundary | Resolution and prevented failure |
|---|---|---|
| Z01 | Unqualified S1 refs cross S2 snapshots without their original context | Persisted cross-subsystem evidence always uses S2 external refs with package ID. Native runtime-local refs carry an explicit S1 view. Prevents resolving the right record in the wrong snapshot |
| Z02 | Parameter unions allow keys but do not define their meanings | Closed, exact-version parameter schemas in the catalog define every key/role/type, allowed knowledge states, scalar enums and semantic checks. Prevents arbitrary metadata acquiring scientific meaning |
| Z03 | Strings/lists/matrices do not fit every scalar parameter slot | Scalars use existing ParameterValue alternatives; structured data use typed PayloadRef formats or typed S1 objects. Prevents embedding unrestricted JSON or coercing a list to a string |
| Z04 | A reader has no explicit active package | PlanReadContext has active_package:ID or None for initial parsing. Resolution receives an anchor. Entering another view is explicit. Prevents internal-ref ambiguity |
| Z05 | Registries can accidentally imply downloaded handlers or native support | Exact offline registrations bind input/output contracts, implementation identity and callable kind. Names do not install code. Prevents automatic or falsely supported interpretation |
| Z06 | Failed operations might leave staged evidence | Writer transactions expose begin/add/get/commit/discard; rejected operations commit no additions. Partial useful results are explicit. Prevents orphan records being mistaken for completed work |
| Z07 | bind_run has no direct input for materialization or its applicability | Add materialization and assessments arguments; all must agree with selected resolution and frozen plan. Prevents required checks disappearing through an indirect reference |
| Z08 | Evaluation binding can lose output selection and interpretation parameters | Add inputs, alignments, interpretations and parameters arguments matching its payload. Prevents implicit last/best outputs, default mappings and hidden reference choices |
| Z09 | Evidence index omits direct S1 observations/assessments/action requests | Broaden only to the named S1 evidence kinds in the catalog. Preserve their role and attribution; do not turn observer assessments into native facts |
| Z10 | A local graph record can look complete because links are absent | Scope, pair universe, omission and explicit abstention remain mandatory semantic inputs. Missing bytes/partial coverage are never a negative answer |
| Z11 | Plan/trial and collection/member cycles look like computation cycles | Opaque identities permit structural cycles. Procedure predecessors and event dependencies have separate typed DAG checks. Prevents rejecting valid records or permitting future-outcome dependence |
| Z12 | Immutable S1 publication cannot follow a growing Builder package ID | Fresh publication ID per changed snapshot, unchanged copied record identities, verified ref closure. Prevents prior pins changing meaning; implementation belongs to the bridge bundle |
| Z13 | A reader could hash a normalized copy and claim original byte integrity | Received-byte digest and canonical publication digest are separate observations. Only actual canonical published bytes use that canonical digest. Prevents false byte verification |
| Z14 | Cached hash / legacy n / replicates / score key imply richer science | Source-scoped interpretations, fresh capture separate from reported hash, explicit repetition selection and loss rejection. Prevents false sampling, independence and overwritten trials |
| Z15 | Unknown alignment/targets or unavailable party can look empty | Explicit unresolved values and scoped withheld profiles. No uniform mapping probability, zero mask, central raw table or full-site claim |
| Z16 | Assessment state and chronology lack a common explicit schema | assessment payload parameters require assessment_context; claimed/observed time, cutoff, boundary, revision/conflict inputs and claim limits stay distinct. No latest-wins assessment |
| Z17 | Fixed plan may name a later domain without inventing its identity | Requirement slots refer to future properties. Materialization/resolution later binds actual S1 domain and mapping. Known future observation IDs/values cannot be dependencies of a prospective definition |
| Z18 | A passing fictional package can be confused with a real admission | Specimen provenance is intrinsic synthetic authorship; real authority/native start/capture stay unknown. Semantic examples and future test expectations never issue runtime grants |
| Z19 | Refs inside an artifact payload lack the plan's local reference context | Typed scientific payload refs are fully qualified by their own supplied package views. A ref to its containing verified package uses that view, without a self-digest descriptor. No implicit S2-local reinterpretation |
| Z20 | A definition's package digest might include future trace accounts even without a direct record link | Definition, prior evidence and later trace bytes are separated into snapshots; check package dependency closure as well as record links. Prevents hidden future values entering a purported earlier fixed snapshot |
| Z21 | An adaptive receipt names a branch rule but omits the actual chosen target/value | Add exact action parameters: target, value, operation, selected/delivered/observed state and source inputs. The C specimen encodes Y=1 as selected, not executed |
| Z22 | A retrospective evaluation acquires an artificial scientific trial/run binding | B has no native trial slots or run binding. Its evaluation binds the recovered occurrence and original-history gaps directly. Prevents historical evaluation from implying a new or original native execution |
| Z23 | resolve_slots receives a bare predicate but the selection rule belongs to its slot | Accept explicit case_slot/selection_rule refs, or requirements carrying the exact resolution parameter schema. Missing rules withhold resolution; no reverse-search/default rule. Prevents ambiguity between validity predicates and selection procedures |
| Z24 | Scientific task operation and native invocation operation may use different contracts | Projection registration keys both exact operation contracts, response contract and route kind. The task retains scientific intent; RouteSpec and S1 request use the native operation. A versioned translation proves the correspondence or withholds projection. Prevents name coincidence, registry collision or silent scientific simplification |

Each resolution costs explicit context, evidence or validation. The common simpler
alternative is a mutable plan plus implicit defaults. Its smaller initial API
would hide the exact scientific distinctions under review. These choices remain
proposals and must survive implementation tests; documentation alone cannot prove
all possible combinations correct.

## 2. Exact parameter rules

Each parameter_set has one exact schema contract. Each schema's fields in the
catalog are closed. All listed keys occur once, with the exact role
`s2.param.<key>`; no extra key/role or duplicate key is accepted. Every field uses
K(value). Unknown stays unresolved; not_applicable needs its named rule and scope.
Structural preservation permits these knowledge variants. A profile's semantic
requirements decide which fields must be known/applicable at that boundary.

Numbers remain tagged Number values; counts are integer Number text with an
explicit nonnegative or positive constraint, never a Boolean or binary float.
Ref arrays preserve order and multiplicity. QName enums are represented as exact
strings in parameter values, with their allowed set stated by the schema.
There is no implicit family, unit, domain, metric, target or selection algorithm.

ParameterValue additionally permits NativeIdentity as a closed supporting value,
so the exact legacy identity field need not be stringified or hidden in a blob.
No arbitrary object alternative is added. These refinements precede any implemented
or adopted format.

The catalog includes the 14 original parameter families and explicit supporting
schemas for alignment, distributed access, quantity, measurement, selection,
resolution, state, response groups, assessment context and concrete actions (25
schemas total). Profiles require the
applicable schemas, not every schema for every experiment. A declared schema can
be preserved without a reader; it then withholds affected interpretation/binding.

Structured payload contracts are closed lists of typed entries: code/string lists,
coordinate vectors, temporal windows, adjacency pairs, label maps, weighted members,
environment targets, relational paths, adaptive action rules and native reports.
The catalog gives exact fields and type expressions. A captured logical review
account is explicitly `s2.design_source_account`, evidence for the design discussion,
not a typed scientific input or a substitute for these fields.

## 3. Exact injected-service protocols

Runtime only; opaque callables and access capabilities never enter wire records.
All methods below raise a typed ServiceError(code,path,evidence) on contract failure.
Installed procedures return PlanOp/PlanIssue; arbitrary foreign exceptions become
observer diagnostics with source attribution, never a native failure by default.

| Service | Closed callable surface and rules |
|---|---|
| IdentityService | allocate()->ID; import_once(occurrence:ID,bound_digest:Digest,create:Callable[[],T])->T. Explicit persistent store for idempotence; changed bound inputs reject |
| ClockService | now()->Time. Actual recorder time only; cannot supply original native chronology |
| PlanResolver | lookup(package_id:ID,access:ReadAccess,limits:ReaderLimits)->ResolvedPackage or None; record(reference:Ref,anchor:ID,access:ReadAccess,limits:ReaderLimits)->ResolvedPlanRecord. Explicitly supplied offline sources; no implicit fetch/search |
| ReadAccess | permits(package_id:ID,purpose:Contract)->Boolean. Caller capability; false denies retrieval. A true answer is access to supplied metadata, not native execution authority |
| S2RecordWriter | begin(author:Ref,clock:ClockService)->Transaction; transaction.add(kind:QName,payload:Payload,record_id:ID)->Ref; get(ref:Ref)->S2Record; ingest(records:tuple[S2Record])->None; snapshot()->RecordDelta; commit()->RecordDelta; discard()->None. All refs use declared overlay/anchor; conflicts reject; no publication |
| FamilyRegistry | lookup(contract:Contract)->FamilyReader or None; register(reader:FamilyReader)->None. Exact unique pair only, explicit owner setup; incompatible duplicate registration rejects |
| AssessmentRegistry | lookup(contract:Contract)->AssessmentProcedure or None; register(procedure:AssessmentProcedure)->None. No fallback truth/metric procedure |
| ProjectionRegistry | lookup(scientific_operation:Contract,native_operation:Contract,response:Contract,route_kind:String)->ProjectionProcedure or None; register(procedure:ProjectionProcedure)->None. Both operation identities exact; scientific translation separate from existing S1 route registration |
| LegacyRegistry | lookup(source:Contract,target:Contract)->LegacyProcedure or None; register(procedure:LegacyProcedure)->None. Explicit source/version selection; no unsafe object deserialization |
| S1RecordWriter | Existing S1 RecordBuffer.add/get/ingest/snapshot contract; valid S1 kinds only. Compiler passes actual producer/procedure provenance through a correctly configured builder |

FamilyReader = {contract:Contract, implementation:Ref(component),
input_contract:Contract, output_contract:Contract,
read:Callable[[Ref,PlanAssessmentContext],PlanOp[InterpretedValue]]}.
InterpretedValue = {contract:Contract, subjects:tuple[Ref], parameters:tuple[Ref(parameter_set)],
evidence:tuple[Ref], limits:tuple[PlanIssue]}.
It carries interpreted facts under named semantics, never an opaque arbitrary dict.

AssessmentProcedure = {contract:Contract, implementation:Ref(component),
assess:Callable[[tuple[Ref],tuple[Ref],tuple[Ref(parameter_set)],PlanAssessmentContext],
PlanOp[tuple[Ref(assessment)]]]}.
Its three tuples are subjects, supplied evidence and parameters. It cannot execute
the native system, fit an encoder, query a private store or compute new S4 metrics.

ProjectionProcedure = {scientific_operation:Contract,native_operation:Contract,response:Contract,route_kind:String,
implementation:Ref(component),
project:Callable[[Ref(run_binding),ProjectionOccurrence,S1Ref(component),S1.RouteSpec,
S1ProjectionContext],PlanOp[S1RequestProjection]]}.
Only the generic entry point calls it after exact registry and scope checks.
It reads scientific_operation from the bound S2 task and native_operation from
RouteSpec.operation. s1.request.operation must equal that native operation, not
necessarily the scientific operation's identifier. native_handoff.operation records
the native contract; its run/task links retain the scientific contract. Different
native targets can therefore register separate faithful translations for one task.

LegacyProcedure = {source_contract:Contract,target_contract:Contract,
implementation:Ref(component),
import_value:Callable[[LegacyImportSource,LegacyImportScope,LegacyContext],PlanOp[LegacyImportDelta]],
project_value:Callable[[tuple[Ref],LegacyProjectionPolicy,LegacyContext],PlanOp[LegacyProjectionDelta]]}.
Unsupported direction returns a typed rejection, not a guessed conversion.

Context refinements (other fields retain the interface candidate definitions):

- PlanReadContext adds active_package:ID or None. read_package consumes supplied
  bytes without requiring an existing anchor; resolve requires an explicit anchor.
  `context.for_view(view:PackageView)->PlanReadContext` returns a new view context,
  does not mutate the old resolver or retrieve anything.
- DraftContext writer overlay is explicit and visible to its read context during
  a transaction. Reads never silently combine another transaction's records.
- PlanAssessmentContext.read must be draft.read; incompatible views reject.
- S1ProjectionContext adds s1_view:ResolvedPackage, projections:ProjectionRegistry.
  Internal S1 refs resolve only in that view or its explicit staged S1 overlay.
- LegacyContext adds legacy:LegacyRegistry. captured_sources are S2 external refs
  to verified S1 snapshots/declarations, not ambiguous S1-local refs.

Revised signatures (16 entry-point names retained):

```
resolve_slots(requirements:tuple[Ref(case_slot|selection_rule|requirement)],
              candidates:tuple[Ref], context:DraftContext) -> PlanOp[ResolutionDraft]

bind_run(plan:Ref(plan_snapshot), trial:Ref(trial_slot),
         resolution:Ref(resolution_receipt),
         materialization:tuple[Ref(materialization_receipt)],
         assessments:tuple[Ref(assessment)],
         context:PlanAssessmentContext) -> PlanOp[RunBindingDraft]

bind_evaluation(plan:Ref(plan_snapshot), comparison:Ref(comparison),
                population:Ref(analysis_population_receipt),
                references:tuple[Ref(reference_definition)],
                inputs:tuple[Ref(evidence_link|s1.output|s1.connection_observation)],
                alignments:tuple[Ref(s1.mapping|materialization_receipt|resolution_receipt)],
                interpretations:tuple[Ref(assessment|s1.check)],
                parameters:tuple[Ref(parameter_set)],
                context:PlanAssessmentContext) -> PlanOp[EvaluationBindingDraft]

link_evidence(subjects:tuple[Ref], s1_evidence:tuple[Ref],
              context:DraftContext) -> PlanOp[RecordDelta]
```

link_evidence's second tuple permits only the catalog's S1 evidence kinds, with
external package qualification. It does not permit local S1 refs in an S2 view.
Native recipient refs in project_request remain S1-local to its explicit s1_view.
Every PlanOp rejected result has no value, no committed additions and diagnostics;
partial has a useful value and diagnostics for outstanding work. Completed means
the operation ran, not that its assessed predicate passed. encode_package raises
ServiceError on invalid input and never emits partial publication bytes.

## 4. Profile and compatibility obligations

The catalog names exact proposed profiles: s2.preserve, s2.interpret,
s2.bind_inputs_sources, s2.bind_evaluation, s2.commit_release_account.
All use version 0.1.0-proposal.1. Installed-reader support and actual evidence are
separate requirements; synthetic wire packages do not satisfy real native claims.

Family checks include scope/omission and valid alternatives; variable/domain and
coordinate mapping; task-target/reference applicability; information recipient and
actual delivery; transform loss/equality and randomization coupling; repetition and
dependence; and chronology/exposure. Known false evidence yields fail, insufficient
evidence yields unknown, absent procedure yields not_checked plus a diagnostic.
Conflicting assessments remain explicit and require a named reconciliation rule;
one pass never implicitly supersedes another failure.

Concrete scoring, statistical inference, scientific identifiability and owner
authority rules remain external procedure/owner prerequisites. Keeping them
unestablished is the resolved behavior, not permission to invent them. Registered
S2 checks assess bindings and stated invariants; S4 owns scientific measurement.

## 5. Composition and next review

The specimen manifest maps every source logical record to a wire responsibility
and retains which facts are merely preserved design-source accounts. Dedicated
typed fields encode the selected scientific meanings. It also identifies negative
mutations and API expectations for rejection, partial preservation or withheld
profiles. These are expected outcomes for future tests, not tests already passed
by an unbuilt S2 library.

The [final review](subsystem2-final-design-review-2026-11-02.md) inventories bounded
closure, limitations and decisions. The [implementation DAG](subsystem2-implementation-dag-2026-11-02.json)
orders future bundles; it grants no implementation or paid execution authority.

## Where we're going

Use the explicit schemas, service protocols, specimens and counterexamples as the
review baseline. Review acceptance belongs to Uzair; public protocol adoption to
W5. Only an explicit subsequent implementation go activates the bundle plan.
