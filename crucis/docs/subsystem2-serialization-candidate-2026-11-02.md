# Subsystem 2: bounded serialization candidate SC-2

Tickets: DLV-08, DLV-09; related DLV-10, DLV-06/07 and ADV-01.
Date: 2 Nov 2026, America/Los_Angeles.
Status: exact core wire-design candidate requested by Uzair, not accepted schema,
implemented codec/validator, preregistration or adopted public protocol. No build.
SC-2 is a local design label; it does not rename audit protocol v1/v1.1 or change
certificate versions, finding IDs, stored numbers, sealed rules or paper pointers.

Basis: [candidate families/profiles/lifecycle](subsystem2-family-profile-lifecycle-contract-2026-11-02.md),
[A-C examples](subsystem2-linked-experiment-examples-2026-11-02.md),
[D-H extensions](subsystem2-extension-composition-2026-11-02.md),
[S1 serialization](system-connections-serialization-2026-11-01.md),
and inspected `audit/connections/{schema,codec,model,evidence}.py`.
Companion: [exact interface/legacy candidate](subsystem2-interface-legacy-candidate-2026-11-02.md).

Follow-on candidate: [contract closure](subsystem2-contract-closure-2026-11-02.md)
and its [exact catalog](subsystem2-contract-catalog-2026-11-02.json) refine this
initial pass, including ParameterValue NativeIdentity, the evidence-kind union,
25 parameter schemas, 11 payload formats and qualified payload contexts. Use the
closure/catalog where they explicitly refine this historical candidate. See the
[final review candidate](subsystem2-final-design-review-2026-11-02.md); no freeze/build.

The A-H JSON registries remain logical review notation. Their readable aliases,
free-form accounts and fictional traces are not SC-2 instances. Transcription and
negative specimens under this candidate are a later design step, not a claim that
parsing those registries proves conformance.

## 1. Notation, format and package boundary

Initial format = {name: "s2.experiment_package", version: "0.1.0-proposal.1"}.
Known core record contracts have name equal to their record_type and that exact
version. Family/operation/parameter contracts select separately versioned meanings.
Readers support exact versions or an explicitly registered compatibility procedure;
there is no implicit semver widening, URI handler download or schema auto-fetch.

Review notation: T[] is an array, A|B is a tagged/structurally disjoint union,
K(T) is explicit knowledge, Ref(T) is typed identity, Index is integer text.
All catalog fields are required; objects are closed. Empty arrays state the known
empty value appropriate to that slot. Unknown enumeration uses IndexList extent,
unknown values use K, unknown association uses unresolved Ref. None is native null.

Package = {format: Contract, package_id: ID, roots: Ref[], records: Record[],
external_packages: ExternalPackage[], extensions: Extension[]}.

Roots are nonempty, unique internal S2 references. Local records are S2 core records
only; S1 records remain in explicitly referenced SC-1 packages. A package may be
a small definition or later receipt set and need not contain every kind below.
A frozen snapshot gets its own package ID. Mutable staging is not a publication;
appending observations must not silently change a published package identity.

Record = {id: ID, record_type: QName, contract: Contract, producer: Ref(component),
created_at: K(Time), payload: Payload, extensions: Extension[]}.

Unqualified core type names in this document mean s2.<name>. S1 types are explicitly
qualified. New S2 records identify their actual S2 author/recorder and known creation
instant; unknown historical times/identities belong in source claims/parameters.
The producer component can identify itself as the intrinsic bootstrap definition.
Its code identity must describe the actual S2 component, not borrow S1 Builder's
default connection-code manifest as though it identified new S2 implementation.

## 2. Shared primitives and typed references

Reuse the meanings of SC-1 Contract, QName, ID, Number, Index, Unit, Time, Source,
Scope, PayloadRef, Digest, BytePayload, Selector and NativeIdentity. S2 references
and metadata shapes below have their own validation/resolution ownership; reusing
notation does not make an S2 package valid under the closed SC-1 schema.

Reference-bearing supporting shapes use the S2 resolver explicitly:

Scope = {subjects:Ref[], qualifiers:Ref[]}.
Source = {basis:reported|observed|reconstructed|derived|intrinsic,
evidence:Ref[], procedure:K(Ref(component|s1.component)), inputs:Ref[]}.
PayloadRef = {artifact:Ref(s1.artifact_snapshot), selector:K(Selector)}.
NativeIdentity = {authority:String, namespace:String, native_id:String, source:Source}.

Time's clock reference can identify s2.component or external s1.component;
BytePayload external_snapshot.locations are Ref(s1.location)[]; Selector's
array_coordinate.axes is Ref(s1.schema). Those S1 targets are external or explicitly
unresolved under the rules below. Other SC-1 primitive tags/fields stay the same.
These are explicit namespace adaptations of the primitive meanings, not verbatim
use of SC-1 typedefs whose unqualified references resolve only inside SC-1.

- ID: lowercase UUIDv4 lexical form; allocate and persist occurrence identities
  independently of content hashes. Source IDs/paths remain scoped labels. Synthetic
  UUIDs are allowed only in labeled design/conformance specimens, not as evidence
  of native occurrences or independent sampling.
- QName: ASCII namespaced identifier under the SC-1 grammar. Unknown native text
  remains text/evidence, not a silently installed code or scientific contract.
- K(T): known with value/basis; unresolved with nonempty reasons/evidence; or
  not_applicable with rule/scope. Recorded native assertions are not independently
  proven by known status. Intrinsic definitions are distinguishable from observations.
- Numbers: tagged integer/finite-decimal/nonfinite text as SC-1. No binary float
  coercion or rounding. Counters/indices use nonnegative integer strings. Nonfinite
  values require an explicitly permitting semantic slot and never pass probability
  or cardinality checks by default. Booleans are not numeric observations.
- Time: actual UTC instants or preserved native reports with uncertainty/timezone
  limits. Event order requires explicit predecessor/sequence evidence, not ID order.

Ref(T) = {binding: internal, target: ID, target_type: QName} |
{binding: external, package_id: ID, target: ID, target_type: QName} |
{binding: unresolved, target_type: QName, reason: Code, evidence: Ref[], source_labels: String[]}.

Internal targets must be known local S2 types and resolve to exactly that record.
An S1 reference is external (or explicitly unresolved); S1 records are not inserted
into an S2 records array. Unresolved references have no invented target ID. Where
a slot allows a type set, the concrete reference declares one actual target type.

ExternalPackage = {package_id: ID, format: Contract, locator: K(String),
expected_digest: K(Digest), access: Code}.

This S2 descriptor includes format and is not copied verbatim into SC-1's smaller
ExternalPackage shape. It declares a source, not permission or proof of retrieval.
Resolution uses explicit caller-provided local packages/resolvers/access scope.
No network, sibling-directory search or native execution follows from a locator.
Restricted/unavailable descriptors can remain preserved; a required unresolved
dependency withholds the affected interpretation/readiness claim.

Different packages may contain the same identified record only when the exact
record contents agree under the named comparison rule. Different content for one
record ID is an identity conflict, never latest-wins. Duplicate record IDs within
one package are rejected even when equal. Different IDs with equal contents do
not merge native occurrences, cases, samples or membership slots.

IndexList(T) = {members: T[], extent: complete_for_scope|partial_for_scope|
not_examined|unresolved, scope: Scope, gaps: Ref(diagnostic|s1.gap)[]}.
Not-examined lists assert no members. Partial/unresolved lists may retain established
members. Completeness extends only to their explicit scope.

Extension = {contract: Contract, affects: Ref[], critical_for: Code[], payload: BytePayload}.
Unknown extensions are retained; affected guarantees remain withheld where critical
meaning is unsupported. Unknown core kinds or incompatible envelope versions are
not accepted as known records. Preserve the original bytes through an S1 snapshot
and S2 import/diagnostic account instead of silently dropping or guessing fields.

## 3. Parameterization without an unrestricted metadata bag

ParameterBinding = {key: String, role: Code, value: K(ParameterValue)}.
ParameterValue = String|Boolean|Number|Unit|Time|Contract|Digest|Ref|Ref[]|PayloadRef.

Each parameter_set selects one exact schema Contract. That schema defines allowed
roles, key/cardinality/type rules, scientific meaning and conditional requirements.
Keys are unique within the set; roles can repeat only under their declared rules.
Order is retained unless an explicit derived view reorders it. Larger matrices,
tables, maps and native payloads use typed S1 objects/payload references or referenced
parameter sets, not arbitrary extra manifest properties. Original literal null and
unrecognized native objects remain captured bytes under their actual source format.

Known schema examples below specify required meanings; exact registered role
names/reader implementations must be transcribed and checked against the A-H
candidate specimens before final freeze. Unknown schemas remain preservable but
do not satisfy profile requirements requiring their interpretation.

| Parameter schema family | Required bounded meaning |
|---|---|
| Population/selection | Source-pool snapshot, scope/selectors, inclusion/exclusion, grouping/strata and enumeration limits |
| Access/interface | Evidence mode, source/interface version, operations, permitted arguments/responses, party ownership and scope |
| Task target/response | Domain/proposition/coordinate scope, deliverable groups, cardinality, admissibility and abstention rules |
| Coverage/reference | Relationship/event meaning, closed/open extent, positive/negative/unknown scope, applicability and legacy tier association |
| Temporal/grouped | Trajectory/subject/time domains, units/frames/windows/lags, boundary eligibility, epoch/stationarity and overlap |
| Relational/distributed | Perspective/schema/path/cardinality, entity/party identity, joins, counts, allowed remote/statistic meaning and aggregation assumptions |
| Learned/alignment | Encoder/model/native domain, source target, calibration procedure/evidence, ambiguity, losses and outcome-selection limits |
| Collection/quantity | Member/weight/parameter associations, event/conditioning, native inference meaning, normalization and derived view selection |
| Intervention/measurement | Environment/source sample identity, target/value uncertainty and disclosure, baseline/active/proxy target and validity requirements |
| Randomization/transform | Role/generator/parameters, explicit coupling, realized maps/selections, fitted inputs and preservation/loss checks |
| Comparison/analysis | Target, direction, matching cardinality, units/weights/dependence, missingness, utility/selection and uncertainty/multiplicity/stopping |
| Commitment/release | Fixed/later binding rules, assurance/exposure, actors/authority/recipients, admission/disclosure/consumption and amendments |
| Native handoff | Exact recipient/route/support/configuration and S1 operation/deliverable/policy/completion projection |
| Legacy interpretation | Source battery/item/arm/status/coordinate contract, actual snapshot pins, original-ID/timing gaps and loss/projection rules |

Thus the core catalog below is exact in shape, while a scientific family claim
still requires its exact supported parameter schema and evidence. A schema name
alone is not scientific support; the remaining transcription boundary is explicit.

## 4. Supporting shapes and constraints

ScopedKey = {namespace: String, key: String}.
Cardinality = {minimum: Index, maximum: {kind: finite, value: Index}|{kind: unbounded}}.
Deliverable = {role: Code, contract: Contract, scope: Scope, cardinality: Cardinality,
required: Boolean, abstention: allowed|forbidden, parameters: Ref(parameter_set)[]}.
ResolutionEntry = {role: Code, requirement: Ref, selected: IndexList(Ref),
rule: Contract, basis: Ref[]}.
PopulationEntry = {key: String, unit: Ref, members: Endpoint[],
disposition: included|excluded|unmatched|unresolved|not_applicable,
reasons: Code[], basis: Ref[], weight: K(Number)}.
Endpoint = {role: Code, target: Ref}.
ContentBinding = {package_id: ID, digest: Digest, selected_records: ID[]}.
ProfileClaim = {profile: Contract, families: Contract[], scope: Scope,
evidence: Ref[], limits: Ref(diagnostic)[]}.
Tier = T1|T2|T3|T4 (existing meanings only).

Population disposition concerns one named analysis selection, not native lifecycle.
Members retain their comparison-role multiplicities and source observations; an
included unit can still have missing/abstained facets under an appropriate rule.
Cardinality is checked against the declared role, not inferred from an array length.
ContentBinding pins a complete earlier package byte snapshot and identifies the
records relevant to its claim; selected_records does not change digest scope.

## 5. Exact initial core payload catalog

All rows include source:Source explicitly. Ref without a type abbreviation means
a slot whose target kinds are restricted by the selected exact semantic contract;
it is not permission to join arbitrary objects. Scope/assumption/parameter/gap
checks remain necessary after structural parsing. Unqualified names are s2 names.

| record_type | Required payload fields |
|---|---|
| s2.component | name:String, role:Code, version:K(String), implementation:K(PayloadRef), configuration:K(Ref(parameter_set)), source:Source |
| s2.parameter_set | schema:Contract, bindings:ParameterBinding[], source:Source |
| s2.requirement | predicate:Contract, subjects:Ref[], parameters:Ref(parameter_set)[], scope:Scope, source:Source |
| s2.relation | relation_contract:Contract, endpoints:Endpoint[], parameters:Ref(parameter_set)[], scope:Scope, source:Source |
| s2.source_definition | source_kind:Contract, domain:K(Ref(s1.domain)), evidence:IndexList(Ref(s1.artifact_snapshot\|s1.artifact_declaration)), access:K(Ref(parameter_set)), population:Ref(parameter_set), assumptions:Ref(requirement)[], lineage:Ref(relation)[], source:Source |
| s2.case_revision | case_key:ScopedKey, prior:K(Ref(case_revision)), origin_time:K(Time), aliases:NativeIdentity[], scope:Scope, domains:IndexList(Ref(s1.domain)), evidence:IndexList(Ref(s1.artifact_snapshot\|s1.artifact_declaration)), definitions:Ref(source_definition)[], relations:Ref(relation)[], exposure:IndexList(Ref(exposure_receipt)), limitations:Ref(diagnostic)[], source:Source |
| s2.case_slot | requirement:Ref(requirement), sources:Ref(source_definition)[], domain_requirements:Ref(requirement)[], resolution_rule:Contract, parameters:Ref(parameter_set)[], scope:Scope, source:Source |
| s2.selection_rule | rule:Contract, population:Ref(parameter_set), inputs:Ref[], parameters:Ref(parameter_set)[], randomization:K(Ref(randomization_spec)), stopping:K(Ref(requirement)), source:Source |
| s2.collection_release | collection_key:ScopedKey, previous:K(Ref(collection_release)), membership:IndexList(Ref(membership)), selection:K(Ref(selection_rule)), ordering:ordered\|unordered, multiplicity:unique_case_revisions\|explicit_slots, scope:Scope, exposure:IndexList(Ref(exposure_receipt)), source:Source |
| s2.membership | collection:Ref(collection_release), case:Ref(case_revision), selection_slot:K(Ref(case_slot)), role:Code, basis:Ref[], source:Source |
| s2.coverage_spec | domain:K(Ref(s1.domain)), predicate:Contract, parameters:Ref(parameter_set)[], extent:complete_for_scope\|partial_for_scope\|not_examined\|unresolved, omission:Contract, scope:Scope, source:Source |
| s2.response_contract | deliverables:Deliverable[], coverage:Ref(coverage_spec), fulfillment_rule:Contract, parameters:Ref(parameter_set)[], source:Source |
| s2.task_definition | operation:Contract, scope:Scope, response:Ref(response_contract), completion:Contract, completion_parameters:Ref(parameter_set)[], assumptions:Ref(requirement)[], source:Source |
| s2.task_binding | definition:Ref(task_definition), cases:Ref(case_slot\|case_revision\|resolution_receipt)[], domains:Ref(s1.domain\|s1.mapping)[], targets:Ref(parameter_set)[], scope:Scope, source:Source |
| s2.reference_definition | reference_kind:Contract, assertions:K(Ref(s1.output\|s1.artifact_snapshot\|s1.artifact_declaration)), domain:K(Ref(s1.domain)), applicability:Ref(requirement)[], coverage:Ref(coverage_spec), tier:K(Tier), parameters:Ref(parameter_set)[], source:Source |
| s2.channel_binding | information:Contract, recipient:K(Ref(component\|s1.component)), domain:K(Ref(s1.domain)), payload_requirement:K(Ref(requirement)), disposition:permitted\|required\|forbidden\|unresolved, parameters:Ref(parameter_set)[], scope:Scope, source:Source |
| s2.information_policy | channels:IndexList(Ref(channel_binding)), state_policy:K(Ref(parameter_set)), constraints:Ref(requirement)[], scope:Scope, source:Source |
| s2.condition | condition_key:ScopedKey, applies_to:Scope, varies:Ref(requirement)[], preserves:Ref(requirement)[], information:Ref(information_policy), transforms:Ref(transform_spec)[], parameters:Ref(parameter_set)[], source:Source |
| s2.randomization_spec | role:Code, procedure:Contract, parameters:Ref(parameter_set)[], coupling:K(Ref(relation\|parameter_set)), source:Source |
| s2.transform_spec | operation:Contract, inputs:Ref(requirement)[], parameters:Ref(parameter_set)[], preserves:Ref(requirement)[], produces:Ref(requirement)[], randomness:Ref(randomization_spec)[], predecessors:Ref(transform_spec)[], reference_rule:Contract, source:Source |
| s2.comparison | tasks:Ref(task_binding)[], conditions:Ref(condition)[], target:Ref(parameter_set), measures:Contract[], analysis_rule:Contract, population_rule:Contract, matching:Ref(parameter_set), dependence:Ref(parameter_set), missingness:Ref(parameter_set), uncertainty:Ref(parameter_set), parameters:Ref(parameter_set)[], source:Source |
| s2.subject_binding | native_subject:K(Ref(s1.component)), configuration:K(Ref(s1.configuration)), support:K(Ref(parameter_set\|s1.artifact_snapshot\|s1.output)), requirements:Ref(requirement)[], parameters:Ref(parameter_set)[], scope:Scope, source:Source |
| s2.trial_slot | origin_plan:Ref(plan_snapshot), case_requirement:Ref(case_slot\|case_revision\|resolution_receipt), task:Ref(task_binding), condition:Ref(condition), subject:Ref(subject_binding), repeat_key:ScopedKey, randomness:Ref(randomization_spec)[], source:Source |
| s2.plan_snapshot | purpose:Contract, definitions:Ref[], collections:Ref(case_slot\|selection_rule\|collection_release)[], tasks:Ref(task_binding)[], conditions:Ref(condition)[], subjects:Ref(subject_binding)[], comparisons:Ref(comparison)[], trials:IndexList(Ref(trial_slot)), resolution_requirements:Ref(requirement)[], commitment_requirements:Ref(requirement)[], prior_evidence:IndexList(Ref), limitations:Ref(diagnostic)[], source:Source |
| s2.resolution_receipt | entries:ResolutionEntry[], candidates:IndexList(Ref), scope:Scope, source:Source |
| s2.materialization_receipt | transform:Ref(transform_spec), sources:Ref[], outputs:Ref(case_revision\|s1.artifact_snapshot\|s1.domain\|s1.mapping\|s1.output)[], randomness:Ref(resolution_receipt)[], checks:Ref(assessment\|s1.check)[], gaps:Ref(diagnostic)[], scope:Scope, source:Source |
| s2.run_binding | plan:Ref(plan_snapshot), trial:Ref(trial_slot), resolutions:Ref(resolution_receipt)[], materialization:IndexList(Ref(materialization_receipt)), subject:Ref(subject_binding), assessments:Ref(assessment)[], source:Source |
| s2.request_binding_receipt | run:Ref(run_binding), request:Ref(s1.request), attempt:Ref(s1.attempt), projection:Ref(parameter_set), checks:Ref(assessment\|s1.check)[], source:Source |
| s2.evidence_link | subjects:Ref[], native_evidence:IndexList(Ref(s1.connection_observation\|s1.output\|s1.artifact_snapshot\|s1.artifact_declaration\|s1.event\|s1.check\|s1.gap\|s1.action_response\|s1.import_receipt)), source:Source |
| s2.analysis_population_receipt | comparison:Ref(comparison), intended:IndexList(Ref(trial_slot\|membership\|case_revision\|evidence_link)), entries:PopulationEntry[], rule:Contract, parameters:Ref(parameter_set)[], source:Source |
| s2.evaluation_binding | plan:Ref(plan_snapshot), comparison:Ref(comparison), inputs:Ref(evidence_link\|s1.output\|s1.connection_observation)[], references:Ref(reference_definition)[], alignments:Ref(s1.mapping\|materialization_receipt\|resolution_receipt)[], interpretations:Ref(assessment\|s1.check)[], population:Ref(analysis_population_receipt), parameters:Ref(parameter_set)[], source:Source |
| s2.assessment | claim:Contract, subjects:Ref[], inputs:Ref[], procedure:Ref(component\|s1.component), scope:Scope, result:pass\|fail\|unknown\|not_checked, diagnostics:Ref(diagnostic)[], parameters:Ref(parameter_set)[], source:Source |
| s2.lifecycle_event | event_contract:Contract, subjects:Ref[], parameters:Ref(parameter_set)[], predecessors:Ref(lifecycle_event\|s1.event)[], claimed_time:K(Time), observed_time:K(Time), source:Source |
| s2.commitment_receipt | plan:Ref(plan_snapshot), content:ContentBinding, event:Ref(lifecycle_event\|s1.event), assurance:Ref(parameter_set), exposure:IndexList(Ref(exposure_receipt)), source:Source |
| s2.amendment | previous:Ref(plan_snapshot), revised:Ref(plan_snapshot), affected:Scope, reason:Code, explanation:Ref(parameter_set\|s1.artifact_snapshot), event:Ref(lifecycle_event\|s1.event), prior_observed:IndexList(Ref), source:Source |
| s2.decision_receipt | policy:Ref(selection_rule\|requirement\|parameter_set), information:IndexList(Ref), chosen:IndexList(Ref), rule:Contract, event:Ref(lifecycle_event\|s1.event), parameters:Ref(parameter_set)[], source:Source |
| s2.exposure_receipt | subjects:Ref[], recipients:IndexList(Ref(component\|s1.component)), information:IndexList(Ref), event:Ref(lifecycle_event\|s1.event), policy:Ref(information_policy\|s1.policy), scope:Scope, assessment:K(Ref(assessment)), source:Source |
| s2.support_declaration | profiles:ProfileClaim[], subject:Scope, source:Source |
| s2.import_receipt | import_occurrence:ID, sources:Ref(s1.artifact_snapshot\|s1.artifact_declaration\|s1.import_receipt)[], reader:Ref(component\|s1.component), configuration:K(Ref(parameter_set)), original_identity:K(NativeIdentity), interpretations:Ref[], gaps:Ref(diagnostic)[], source:Source |
| s2.diagnostic | subjects:Ref[], reasons:Code[], scope:Scope, source:Source |

## 6. Semantic closure and lifecycle constraints

All local references resolve; unresolved associations use their explicit variant.
An external declaration can remain unavailable, with profile requirements withheld.
Exact source bytes/identity, then reference target/type/contract, then family meaning
and claim prerequisites are separate checks. Structural validity never establishes
native completion, causal truth, source independence or actual authorization.

Legitimate record cycles, such as collection/member and origin-plan/trial, do not
define hashes recursively. Recipe predecessors, temporal precedence and selected
generation dependencies obey their own acyclicity/validity rules. Foreign package
dependency cycles or self-content bindings cannot satisfy strong snapshot closure;
preserve the declarations with a scoped diagnostic instead of pretending to verify
unconstructible content pins.

Plan definitions can depend on explicitly prior evidence. Their prospective claim
scope cannot depend on future outcomes/resolution values. Later receipts point
back to fixed requirements. A trial's origin_plan remains historical when a new
effective run binding uses an amended plan; compatibility/carry-forward must be
explicitly evidenced, not inferred from the same trial label.

Resolution rules determine whether zero, one or several selections are valid for
each role. A single-valued required role needs one explicit selected binding; no
best/latest fallback. Multiple candidates remain preserved. Analysis-population
entries retain all missing/unmatched/excluded units and relevant facets under
their declared scope. Different completed-output populations are not equated.

A commitment's ContentBinding pins a different, already frozen subject package;
the receipt cannot be inserted into the very package whose bytes its digest claims.
Private reference and exposure facts can stay external/restricted. Their descriptor
and public projection cannot replace the authorized evaluator's actual checks.

## 7. Strict encoding and canonical publication

Input JSON is strict UTF-8: reject duplicate properties before overwriting, invalid
Unicode scalar strings, nonstandard NaN/Infinity tokens, malformed tags and extra
known-object keys. Do not silently normalize Unicode or native literal text.
No semantic numeric field uses untagged JSON numbers. Native scientific arrays,
binary floats and original encodings remain S1 evidence with their actual contracts.

Proposed s2.canonical_json/1 publication bytes:

1. Normalize only package-set order: records by ID, external_packages by package ID,
   roots by (target_type, target). Reject duplicates first. No other array reordering.
2. Sort object property names by Unicode scalar-value order; preserve strings and
   tagged number lexical text. No scientific equality normalization.
3. Emit UTF-8 without BOM or insignificant whitespace/trailing newline. Use the
   JSON escapes for quotation mark, backslash and control characters; controls not
   represented by a short JSON escape use lowercase four-digit hex escapes. Other
   Unicode scalar values remain literal UTF-8. Solidus is not escaped.
4. Compute SHA-256 over those exact frozen bytes, outside the subject manifest.
   Digest includes byte length and full-content scope. A record comparison uses
   the same object encoding without package-array sorting and never includes a
   new self-digest field. Equal encoding never merges occurrences.

Input may contain ordinary insignificant whitespace, but published S2 snapshots
use the above named encoding so their canonical fingerprint is their stored byte
digest. A pretty review copy is a different artifact and cannot replace that pin.
SC-1 packages retain their actual existing bytes/codec/digest conventions; do not
re-encode S1 with this algorithm and pretend its historical byte digest is unchanged.

This is a specified local encoding, not a claim to implement another JSON
canonicalization standard. Unknown/unsupported formats are preserved as bytes,
not normalized into an invented equivalence. No codec is implemented by this note.

## 8. Resolver and operation bounds

A reader receives explicit positive limits for manifest bytes, record count,
external-package count/bytes, reference traversal and interpreted parameter depth.
There is no implicit unbounded mode or silent truncation. Limit failure produces
a scoped parse/resolution diagnostic, not a native system failure or zero score.
Large evidence remains externally referenced under explicit access rules.

Loading parses supplied bytes only. Resolving uses caller-provided snapshot sources
and known offline readers; no arbitrary import, network lookup or seed-store access.
It checks actual byte digest/length/scope where required, package identity/format,
target kind and record collision. A valid locator or reported hash does not alone
establish retrieval/integrity. Grants, runtime capabilities and handles are never
serialized by traversing their attributes or placed into parameter payloads.

## 9. Review choices, costs and remaining transcription

The strongest simpler alternative is reusing the SC-1 package unchanged or placing
the scientific plan into a generic metadata blob. The first would violate its closed
record catalog; the second would lose accountable selection, repetition and readiness
meaning. A separate package reusing precise primitives costs a resolver/handoff and
explicit snapshots, while preserving subsystem ownership and native boundaries.

Forty kinds are a responsibility catalog, not mandatory per-run boilerplate. Simple
plans reference shared definitions; historical imports use only their actual accounts.
Typed parameter schemas keep core fields bounded while family readers expand, with
unknown semantics explicitly limiting claims rather than silently succeeding.

Before final freeze: transcribe exact parameter-role schemas and A-H wire specimens;
check every core/supporting type, reference/cardinality and invalid case; settle the
interface projection/publication invariants in the companion; and retain genuinely
unsupported scientific procedures as scoped prerequisites. None of the example
registries has been passed through a nonexistent SC-2 runtime validator.

## Where we're going

Review these wire choices together with the exact interface and legacy contract.
Recompose the linked examples under the candidate, including unsupported/private/
late-bound cases, and close remaining role-schema and cross-reference issues before
final subsystem-2 review and bundle planning. Implementation still requires its own go.
