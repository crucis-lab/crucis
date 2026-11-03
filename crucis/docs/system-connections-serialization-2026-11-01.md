# Subsystem 1: serialization candidate SC-1 (1 Nov 2026)

Tickets: DLV-08, DLV-09; neighbours DLV-10, ADV-01, DLV-06.
Status: complete proposed wire-contract decisions for review; not frozen, adopted or implemented.
Predecessor: [Composition review](system-connections-composition-review-2026-11-01.md).
SC-1 is a local design label. It does not rename protocol v1/v1.1 or alter certificate versions.

## 1. Notation and authority

This specification resolves the bounded serialization checklist. It gives exact tagged shapes and payload
field tables in review notation, not executable schema/validator code. The initial implementation bundle
will transcribe the approved specification into JSON Schema and semantic checks without inventing fields.
JSON Schema 2020-12 is the proposed structural-schema dialect [S1]. Cross-record identity, preservation,
graph-family and scientific claims remain separate from structural-schema assertions.

Notation: T[] is an array; A|B a tagged union; T? an optional property; Ref(type) a typed reference;
K(T) the knowledge union below; Contract a name/version pair. Every listed unmarked field is required.
All described objects are closed: extra keys are rejected under their known contract. Optional omission
makes no positive assertion. Extensibility uses the explicit extensions field, never arbitrary extra keys.
Type/member/predicate names starting s1. are reserved to this contract proposal; foreign names use their
own namespace. Inline versus referenced large payloads is explicitly specified, not guessed by shape.
String means a sequence of Unicode scalar values; reject unpaired surrogates in manifest strings and apply
no Unicode normalization. Native invalid text/bytes remain available through base64 or external snapshots.

The earlier 147-record JSON remains a readable logical specimen, not an instance of this newly selected
envelope. Its aliases, descriptive fields and hypothetical times require an explicit transcription into
SC-1 golden specimens in the schema bundle. Do not claim schema validation merely because that JSON parses.

## 2. Package, IDs, contracts and record envelope

Package = {format: Contract, package_id: ID, roots: Ref[], records: Record[],
external_packages: ExternalPackage[], extensions: Extension[]}.

Initial format name: s1.connection_package. Proposed exact version: 0.1.0-proposal.1, subject to adoption.
No implied semver compatibility or automatic version-range matching. A reader supports exact declared
contracts or an explicitly registered compatibility mapping. Package roots are nonempty.

ID is a lowercase UUID string matching
`^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$`.
Generate new production identities randomly and persist once. Stable source-association/import maps preserve
already assigned IDs. Hard-coded synthetic UUIDs are allowed in explicitly synthetic design/conformance
examples; lexical validity does not prove random sampling or execution independence. Native IDs and old
readable specimen aliases remain metadata, not substitutes for the ID.

Contract = {name: QName, version: NonemptyString}. QName matches
`^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$`. Contracts are immutable definitions in an explicit offline registry.
Selecting a reader may not fetch code/schema from a URI in an untrusted record. Unknown contracts are
preserved as opaque source content; claims requiring their interpretation are withheld.

Record = {id: ID, record_type: QName, contract: Contract, producer: Ref(component),
created_at: K(Time), payload: Payload, extensions: Extension[]}.

record_type chooses a payload category; contract chooses that category's exact meaning/version. Subtype tags
live in payload, not over the envelope. producer identifies the component producing this record; native
origin/producer claims belong in the payload. Thus a new importer always identifies itself without filling
an unknown original native producer. New publication requires a known creation instant; imported old records
can preserve unresolved original times in their payload under a newly created wrapper.

Record IDs are unique within the loaded package closure. A repeated ID in one package is rejected, even if
content matches. Importing the same identified record from two packages requires compatible contracts and
the same bound record snapshot; a collision with different content is an identity conflict. Representation
checks must name the comparison procedure; content equality alone never merges native occurrences.
Record array order is not an event order. Arrays with semantic ordering retain it under their own contract.

## 3. Primitive unions and exact encoding decisions

### References

Ref(T) is one of:

- {binding: internal, target: ID, target_type: T}
- {binding: external, package_id: ID, target: ID, target_type: T}
- {binding: unresolved, target_type: T, reason: Code, evidence: Ref[], source_labels: String[]}

Internal targets resolve to the declared record type. External packages have explicit descriptors
{package_id, locator: K(String), expected_digest: K(Digest), access: Code}. No implicit network fetch or
sibling-directory search. Unavailable external content is different from a broken internal reference.
An unresolved reference has no invented target ID. target_type can be an allowed type set at a typed slot;
the concrete reference carries one actual target type. Native labels are not passed through as resolved IDs.

### Knowledge, codes and literal values

K(T) = {state: known, value: T, basis: Ref[]} |
{state: unresolved, reasons: Code[], evidence: Ref[]} |
{state: not_applicable, rule: Contract, scope: Ref[]}.

Known means the claim value is recorded, not that a source assertion is independently true. Unresolved
reasons must be nonempty. Known basis can be empty only for intrinsic descriptor/authoring facts; native
claims and derived conclusions need their source/procedure evidence. Not-applicable requires an actual
contract rule. It is not an adapter-unsupported shortcut.

Code is a QName in a versioned code registry. Initial gap codes are s1.not_observed, s1.not_recorded,
s1.not_retrieved, s1.access_denied, s1.not_found_at_location, s1.incomplete_capture,
s1.unsupported_semantics, s1.interpretation_failed, s1.unresolved_identity, s1.conflicting_evidence,
s1.unavailable_dependency, s1.not_computed and s1.unknown_reason. Not-recorded is used only when established.
Namespaced extensions add reasons without changing existing meanings. Empty/zero/false, native abstention
and pending state are values under their respective contracts, not unknown reasons. Literal native null is
preserved in an artifact; it is not the manifest's unknown encoding.

### Numbers, positions and units

Number = {number_type: integer, text: IntegerText} |
{number_type: finite_decimal, text: DecimalText} |
{number_type: nonfinite, value: positive_infinity|negative_infinity|nan}.

IntegerText matches `^-?(0|[1-9][0-9]*)$`; DecimalText matches
`^-?(0|[1-9][0-9]*)(\.[0-9]+)?([eE][+-]?[0-9]+)?$` and has finite mathematical value.
Keep the lexical representation, including negative zero. No automatic rounding, float coercion or universal
normalization. Nonfinite values are legal only in payload contracts explicitly permitting them. Probability
conformance requires a finite value in [0,1]. Counts/indices require nonnegative integer meaning. Native
binary floating-point bit identity stays in captured bytes; a decimal view does not claim bit equivalence.
Index is a nonnegative IntegerText. Structural counts/offsets in this contract also use integer strings.
Booleans are ordinary JSON true/false. Do not treat booleans as numeric observations.

Unit = {name: String, convention: Contract}; units can be K(Unit). Dimensionless has its own declared unit.
Currency includes an explicit currency unit and separate price-basis reference. No implicit unit conversion.

### Time, order, bytes and selectors

Time = {time_type: utc_instant, value: String, precision: second|fractional_second,
clock: K(Ref(component)), uncertainty_seconds: K(Number)} |
{time_type: native_report, text: String, timezone: K(String), precision: K(String)}.

UTC instants must be valid calendar timestamps with explicit Z and optional fractional seconds. A native
partial date, unknown timezone or unreliable clock remains native_report. Do not synthesize a UTC instant.
The initial UTC codec uses seconds 00-59; unsupported leap-second reports stay native_report. second precision
has no fractional part, while fractional_second has at least one fractional digit.
Source event, capture, import and interpretation times are separate slots. Relative ordering uses typed
event/sequence relations, not chronological sorting of unreliable clocks.

BytePayload = {content_form: inline_utf8, text: String} |
{content_form: inline_base64, data: String} |
{content_form: external_snapshot, locations: Ref(location)[], digest: K(Digest)}.

inline_utf8 denotes exactly the UTF-8 encoding of the decoded JSON string, without newline normalization.
For arbitrary bytes/invalid UTF-8 use canonical padded base64; decode before checking byte lengths/digests.
An unretrieved artifact is a declaration with no BytePayload, not a fake external snapshot. Digest =
{algorithm: sha256, value: 64 lowercase hex characters, byte_length: Index, scope: ByteScope}.
ByteScope = {kind: full_content} | {kind: byte_range, start: Index, end_exclusive: Index}; range end >= start.
Digest basis is reported/expected/computed in the containing integrity observation, not inferred from shape.

Selector = {selector_type: json_pointer, pointer: String} |
{selector_type: byte_range, start: Index, end_exclusive: Index} |
{selector_type: member_key, key: String, member_contract: Contract} |
{selector_type: array_coordinate, axes: Ref(schema), coordinates: Index[]} |
{selector_type: archive_member, name: String, member_digest: K(Digest)}.
Every selector is bound by its containing payload reference to an immutable artifact snapshot. JSON pointer
uses the empty string for the root and ~0/~1 escapes; '/' denotes an empty-string property, not the root.
Do not silently import the legacy pointer helper's broader root shortcut into this contract.

## 4. Shared payload building blocks

Scope = {subjects: Ref[], qualifiers: Ref[]}. Role-qualified scientific scope such as node/query domain lives
in its one typed payload slot; Scope references it rather than copying mutable coverage facts.
Source = {basis: reported|observed|reconstructed|derived|intrinsic,
evidence: Ref[], procedure: K(Ref(component)), inputs: Ref[]}.
PayloadRef = {artifact: Ref(artifact_snapshot), selector: K(Selector)}.
IndexList(T) = {members: T[], extent: complete_for_scope|partial_for_scope|not_examined|unresolved,
scope: Scope, gaps: Ref(gap)[]}.
Not-examined lists have no asserted members; partial/unknown lists can retain established members.
Completeness never extends beyond the referenced scope.

Extension = {contract: Contract, affects: Ref[], critical_for: Code[], payload: BytePayload}.
Unknown extensions are retained. An unknown critical extension withholds the affected guarantee; it does
not erase unrelated evidence. Unknown contract requirements/criticality are conservatively unresolved for
the affected scope. A consumer cannot strip unknown fields/extensions and claim a lossless round trip.

## 5. Exact initial payload field catalog

The table specifies payload properties; envelope fields are not repeated. ? means optional. All other fields
are required, including empty arrays where genuinely applicable. These shapes govern selected core types;
family-specific scientific invariants remain in the domain/output specifications and must be checked by
their named procedures. Unrecognized subtypes use extensions/opaque evidence, not arbitrary extra fields.

| record_type | Payload fields |
|---|---|
| s1.component | name:String, role:Code, version:K(String), implementation:K(PayloadRef), configuration:K(Ref(configuration)), source:Source |
| s1.configuration | component:Ref(component), explicit_settings:Ref(artifact_snapshot), resolved_defaults:K(Ref(artifact_snapshot)), scope:Scope, source:Source |
| s1.request | operation:Contract, task_scope:Scope, deliverables:Deliverable[], completion:Contract, completion_parameters:Ref[], presentation_policy:Ref(policy), resource_policy:K(Ref(policy)), recovery_policy:K(Ref(policy)), route:Code, source:Source |
| s1.attempt | request:Ref(request), native_identity:K(NativeIdentity), initial_state:K(Ref(output)), binding:K(Ref(binding)), source:Source |
| s1.connection_observation | subjects:Ref[], request:Ref(request), native_subject:Ref(component), information:IndexList(Ref(presentation)), observations:Ref(observation)[], gaps:Ref(gap)[], outputs:IndexList(Ref(output)), artifacts:IndexList(Ref(artifact_snapshot|artifact_declaration)), context:Ref[], checks:Ref(check)[] |
| s1.observation | subject:Ref, proposition:Ref(proposition), value:ObservationValue, scope:Scope, source_time:K(Time), capture_time:K(Time), source:Source, event:K(Ref(event)) |
| s1.gap | subjects:Ref[], reasons:Code[], scope:Scope, source:Source |
| s1.assessment | subjects:Ref[], rule:Contract, parameters:Ref[], basis:Ref[], conclusions:Conclusion[], cutoff:Ref[], revises:Ref(assessment)[] |
| s1.variable | namespace:Ref(component|domain|schema|output), meaning:K(String), roles:K(Code[]), value_space:K(ValueSpace), source:Source, derivation:Ref[] |
| s1.domain | domain_kind:finite|relative_temporal|absolute_temporal|component|grouped|learned|native_extension, members:DomainMember[], coordinate_contract:K(Contract), extent:Code, source:Source |
| s1.schema | payload:PayloadRef, axes:Axis[], labels:Label[], encoding:Contract, domain:Ref(domain), source:Source |
| s1.mapping | mapping_kind:permutation|partial_correspondence|value_conversion|feature_construction|semantic_alignment|native_decode, from:Ref(domain|schema), to:Ref(domain|schema), entries:MappingEntry[], procedure:Ref(component), purpose:Code, coverage:Scope, properties:Ref(proposition)[], checks:Ref(check)[], source:Source |
| s1.proposition | predicate:Contract, arguments:Argument[], conditioning:Ref(proposition)[], scope:Scope |
| s1.output | output_type:graph|claims|set|order|ranking|quantity|collection|model_reference|message|diagnostic|abstention|native_report, native_producer:Ref(component), subjects:Ref[], role:K(Code), designation:K(Code), body:OutputBody, source:Source, relations:Ref(relation)[], checks:Ref(check)[] |
| s1.artifact_snapshot | content:BytePayload, format:K(Contract), capture_scope:ByteScope, source_span:K(ByteScope), native_capture_extent:Code, locations:Ref(location)[], digest_claims:Ref(observation)[], source:Source |
| s1.artifact_declaration | native_identity:K(NativeIdentity), reported_format:K(Contract), locations:Ref(location)[], claims:Ref(observation)[], source:Source |
| s1.location | locator:String, access_contract:Contract, expected_snapshot:Ref(artifact_snapshot), retrievals:Ref(observation)[], automatic_access:false |
| s1.check | procedure:Ref(component), contract_checked:Contract, subjects:Ref[], inputs:Ref[], scope:Scope, result:pass|fail|unknown|not_checked, diagnostics:Ref(gap)[], source:Source |
| s1.relation | relation_contract:Contract, endpoints:Endpoint[], parameters:Ref[], scope:Scope, source:Source |
| s1.selection | purpose:Code, selected:Ref[], rule:Contract, basis:Ref[], source:Source |
| s1.binding | request:Ref(request), adapter:Ref(component), route:Code, presented:Ref(presentation)[], resolved_configuration:Ref(configuration)[], prerequisites:Ref(check)[], state:ready|not_ready|unresolved, gaps:Ref(gap)[] |
| s1.presentation | information_contract:Contract, payload:K(PayloadRef), endpoint:K(Ref(endpoint)), domain:K(Ref(domain)), schema:K(Ref(schema)), recipient:Ref(component), state:intended|permitted|delivered|access_observed|use_claimed, attempt:Ref(attempt), source:Source |
| s1.policy | policy_contract:Contract, parameters:Ref[], scope:Scope, authority:K(Ref(component)), source:Source |
| s1.import_receipt | import_occurrence:ID, sources:Ref(artifact_snapshot|artifact_declaration)[], reader:Ref(component), configuration:K(Ref(configuration)), operation_policy:Contract, result_roots:Ref[], native_occurrence:K(NativeIdentity), source:Source |

Ref slots accept their unresolved form where the referent is not established; this does not satisfy an
operation that requires it resolved. A generic source reference can preserve original unknown request/run
associations without fabricating request or attempt records. At least one observation/gap is required in
a connection_observation. No interpretation result is required for evidence preservation.

Artifact capture_scope and digest scope address stored snapshot bytes. source_span addresses their known
position in the original native stream/file; unknown origin offsets use unresolved, not an invented prefix.
A full_content hash of a captured prefix covers all stored prefix bytes and does not claim the native
response was complete. native_capture_extent expresses that separate interface-level limitation.

Supporting value shapes:

- NativeIdentity = {authority:String, namespace:String, native_id:String, source:Source}.
- Deliverable = {role:Code, contract:Contract, scope:Scope, required:Boolean, abstention:allowed|forbidden}.
- Conclusion = {facet:Code, value:K(ObservationValue), supporting:Ref[], disputed:Ref[]}.
- ObservationValue = Boolean|String|Number|Ref|Ref[]; structured statements use typed referenced records.
- Argument = {role:Code, value:Member|Ref|Number|String|Boolean}; roles unique unless predicate permits repeats.
- Member = {domain:Ref(domain), key:String}; keys unique within their bound immutable domain.
- DomainMember = {key:String, variable:Ref(variable), coordinates:Coordinate[]}.
- Coordinate = {dimension:Contract, value:String|Number|Ref, reference:K(Ref)}; dimensions unique per member.
- Axis = {name:Code, axis_kind:variable|sample|component|time|native, length:Index,
coordinates:AxisCoordinate[], index_base:zero|one}; coordinate count matches length.
- AxisCoordinate = {key:String, member:K(Member), value:K(String|Number|Ref)}; keys identify axis occurrences.
  Variable axes require established Member bindings for interpreted variable semantics. Sample/row axes
  can bind sample/time identities without pretending those are causal variables. Repeated samples can
  have distinct occurrence keys and the same source-sample reference.
- Label = {member:Member, text:String, audience:Code}; duplicate text does not merge members.
- MappingEntry = {from:Member[], to:Member[], source:Source}; a permutation requires singleton pairs and bijection.
- ValueSpace = {space_type:boolean|categorical|ordered_categorical|integer|real|tensor|native_extension,
contract:Contract, units:K(Unit), levels:Ref[], axes:Ref(domain)[], missing:Contract}.
- Endpoint = {role:Code, target:Ref}; endpoint role semantics belong to relation_contract.

Ref(component) etc. abbreviates the s1.component record type. Attempt initial_state requires an output
whose model_reference body has checkpoint/state role when that field is applicable. Initial interpreted
domains are explicitly enumerable; symbolic/native domain expressions are extension content until a
supported reader exists. Within a graph domain, different member keys cannot be used to disguise the same
established variable-plus-coordinate identity as distinct nodes; use representation aliases instead.

## 6. OutputBody tagged union

| output_type | Exact body fields |
|---|---|
| graph | family:Contract, domain:Ref(domain), coverage:PairDomain, omission:Omission, links:Link[], native_assertions:Ref(proposition)[], quantities:Ref(output)[] |
| claims | propositions:Ref(proposition)[], decisions:Decision[], coverage:Scope, omission:Code |
| set | predicate:Contract, targets:Member[], candidates:Ref(domain), members:Member[], decisions:Decision[], coverage:Scope, omission:Code |
| order | predicate:Contract, domain:Ref(domain), representation:sequence|relation_pairs|cover_pairs, sequence:Member[], pairs:MemberPair[], coverage:Scope, omission:Code |
| ranking | predicate:Contract, domain:Ref(domain), groups:Member[][], direction:earlier_higher|earlier_lower, unranked:Member[], excluded:Member[], quantities:Ref(output)[] |
| quantity | quantity_kind:Code, subject:Ref, value:K(Number)|Tensor|Interval, units:K(Unit), conditioning:Ref(proposition)[], basis:K(Ref), procedure:Ref(component), associated_rule:K(Contract) |
| collection | collection_kind:sequence|set|multiset|sample_bank|weighted_support|finite_measure, member_contracts:Contract[], members:CollectionMember[], extent:Scope, ordering:native_sequence|explicit_order|unordered, generation:K(Ref), weights:Ref(output)[] |
| model_reference | model_role:Code, artifacts:PayloadRef[], input_domains:Ref(domain)[], output_domains:Ref(domain)[], dependencies:Ref[], associated:Ref[], reader:K(Contract), state_coverage:IndexList(Ref) |
| message | message_kind:action_request|action_response|native_message, content:Ref, correlation:Ref, operation:Contract, participants:Endpoint[] |
| diagnostic | code:Code, phase:Code, subjects:Ref[], attribution:K(Ref(component)), details:Ref(artifact_snapshot)[], source_error:K(String) |
| abstention | query:Ref(proposition|request), reason:K(Code), scope:Scope |
| native_report | type_claim:K(Contract), payload:PayloadRef, interpretation_gap:Ref(gap)[] |

PairDomain = {pairing:ordered|unordered, domain:Ref(domain), include_same_node:Boolean,
pairs:MemberPair[], extent:all_in_domain|listed_only}. For all_in_domain pairs must be empty; listed_only
uses explicit pairs. Ordered/unordered endpoint semantics remain distinct, with duplicates checked under
the declared pairing rule. Same-node pairs require include_same_node and a permitting relation contract.
MemberPair = {left:Member, right:Member}.
Omission = {within_coverage:asserted_absence|unreported|explicit_only|unresolved,
outside_coverage:no_assertion}; no silent completeness inferred from the request.
Link = {key:String, left:Member, right:Member, relation:Contract, endpoint_marks:Code[],
properties:Ref(proposition)[], quantities:Ref(output)[]}.
Marks are empty for a pure relation contract, or have exactly two entries bound left/right. A single
bidirected relation, reciprocal arrows and contradictory assertions are not interchangeable encodings.

Decision = {proposition:Ref(proposition), decision:assert|deny|abstain|native_unresolved,
reason:K(Code), source:Source}. Auditor uncertainty uses gaps/K, not invented native_unresolved.
CollectionMember = {key:String, object:Ref(output), multiplicity:Index, associated:Endpoint[]}; multiplicity
must be positive. Ordered member keys and repeated content retain native associations. No implicit deduplication.
Tensor = {value_type:tensor, payload:PayloadRef, axes:Ref(schema), entry_contract:Contract,
missing:Contract}. Interval = {value_type:interval, lower:K(Number), upper:K(Number),
lower_inclusive:Boolean, upper_inclusive:Boolean, construction:Contract, level:K(Number), target:Ref}.
Finite measures require a named normalization check, support/remaining-mass scope and probability semantics;
an incomplete sample bank cannot be relabeled as a complete exact target distribution.

Initial predicates: s1.direct_relation, s1.adjacent, s1.ancestor, s1.conditional_independence,
s1.member_of, s1.precedes and s1.native_property. Exact arguments and conditioning are versioned with each
predicate; unknown predicates cannot satisfy a known predicate's prerequisites. Resource, probability,
coefficient, p-value, count and score kind codes keep the meanings specified in the output subtype draft.

### Initial code and predicate bindings

Initial role codes: s1.native_answer, s1.intermediate, s1.support, s1.checkpoint, s1.diagnostic,
s1.action, s1.standardized_interpretation, s1.derived_view. Unknown role uses K unresolved rather than a
guessed role. Variable-role codes: s1.observed_measurement, s1.learned_representation, s1.latent,
s1.context_indicator, s1.intervention_indicator, s1.auxiliary; multiple roles can apply with evidence.
Capture extent codes: s1.full_for_interface, s1.partial_for_interface, s1.extent_unresolved. Full for one
interface never means every original native artifact was captured.

Initial route codes: s1.recorded_import, s1.direct_invoke, s1.prepared_command, s1.attached_job,
s1.recorded_response_replay. Legacy mode strings remain separately preserved source claims.
Mark codes: s1.tail, s1.arrowhead, s1.circle; foreign marks require a defined extension, not coercion.
Quantity codes: s1.probability, s1.p_value, s1.coefficient, s1.frequency, s1.weight, s1.count,
s1.duration, s1.currency_amount, s1.statistic, s1.score. Unknown quantity kinds retain native_report
until their contract is supported; they do not acquire calibration semantics.

| Predicate | Required arguments | Meaning/constraint |
|---|---|---|
| s1.direct_relation | cause:Member, effect:Member | Source's declared direct structural relation under the bound family; not mere statistical association |
| s1.adjacent | left:Member, right:Member | Unordered adjacency within the bound graph family/domain |
| s1.ancestor | ancestor:Member, descendant:Member | Proper directed reachability over distinct members; source conventions differing on reflexivity need explicit translation/extension |
| s1.conditional_independence | left:Ref(domain), right:Ref(domain), given:Ref(domain) | Conditional-independence proposition over explicitly enumerated variable sets and the bound population/context; test result/decision requires its own procedure |
| s1.member_of | member:Member, set:Ref(output) | Membership in the referenced typed set, with its candidate scope and predicate |
| s1.precedes | before:Member, after:Member, order:Ref(output) | Strict precedence in that defined order; causal versus score meaning belongs to the order contract |
| s1.native_property | subject:Ref, property:String, value:String|Number|Boolean | property is a namespaced QName; a source property assertion cannot silently substitute for a known causal predicate |

Argument roles must be exact and unique except where the predicate explicitly admits a collection argument.
The predicate table's role labels abbreviate namespaced wire codes, e.g. cause is s1.cause and subject is
s1.subject. Initial component roles include s1.native, s1.observer, s1.importer, s1.decoder, s1.mapper,
s1.checker and s1.policy_owner. The first-party producer's actual role is established independently of any
unknown original native component identity.
All variable-set domains and member references must be compatible; distinct namespaces are not joined by
label. Unsupported truth/assumption/test semantics withhold the affected interpretation check, not evidence.
Code registries are exact-version artifacts accompanying the approved schema; unknown foreign codes are
preserved but cannot satisfy known-code prerequisites. There is no implicit miscellaneous-code success path.

## 7. Reader, publication and evolution behavior

Reader order: parse losslessly with duplicate-key rejection; select supported envelope contract; validate
closed field shapes; index IDs; resolve/type-check references; check domains/selectors; apply requested
subtype invariants; record check scopes and withhold unsupported claims. Cyclic associations are legal;
derivation/continuation ancestry is constrained separately. No scientific metric is chosen by this process.
Invalid native source bytes are captured in a valid wrapper, never parsed into a guessed graph.

Exact-byte hashes cover stored bytes only. No new canonical JSON hash is required. Lexical/key-order changes
can change package digests without changing occurrence identity. A semantic comparison or derived encoding
names its procedure and retains original snapshots. Array sorting is never a generic normalization step.

Publish staged content only after manifest/reference closure and claimed checks are established. Publish
partial evidence explicitly as partial. A package with an unavailable external snapshot can be valid under
that declared limitation; a missing required internal target is not valid closure. Atomic local publication
uses a single final manifest commit point; other storage backends require an equivalent documented guarantee.
No storage move or existing result/certificate rewrite is authorized by this candidate.

Any changed required field, predicate meaning, omission/default rule, coordinate meaning or guarantee needs
a new exact contract version and mapping. Optional foreign extensions can be added without redefining the
base. Unknown envelope versions can be preserved as opaque content under a known wrapper. Historical public
consumers remain on their adopted contracts until an explicit migration.

## 8. Freeze boundary and remaining checks

This completes the earlier six-item encoding checklist as a proposal. The base envelope, references,
knowledge/numeric/time/byte unions and selected payload shapes have explicit decisions. Optional interaction
and recovery payloads use independently versioned contracts in their companion specification. Exact API
signatures do not change the wire shape by hiding native fields in arbitrary dictionaries.

Before adoption: Uzair reviews this candidate and its scope; W5 adopts any shared/public contract changes.
Before implementation release: approved shapes are transcribed to structural schema, golden positive and
negative specimens are validated, cross-record checks run and legacy parity/certificates pass. Runtime checks
are release gates, not a claim that design approval requires implementation first.

No runtime/schema code or tests were written. This is the design source for that transcription, not proof
that a JSON Schema alone can enforce every stated invariant.

Import receipts bind an explicitly designated import occurrence to immutable sources, reader/configuration
and result roots. Repeating that operation returns the same receipt after validating its bound inputs;
changed inputs under the occurrence key conflict. Deliberate reinspection uses a new occurrence/receipt.
Receipt identity never claims a fresh native execution. Source-code/registry changes must be reflected in
the reader/configuration identity rather than silently reusing a stale idempotent result.

## Sources

[S1] [JSON Schema 2020-12 core](https://json-schema.org/draft/2020-12/json-schema-core) and
[object property/closure behavior](https://json-schema.org/understanding-json-schema/reference/object),
consulted 1 Nov 2026. These support the proposed structural-schema tooling choice; SC-1 itself is our proposal.

## Where we're going

Review SC-1 together with the interaction/recovery and API/legacy specifications, then decide the subsystem-1
design freeze. Schema transcription and executable validators belong to the authorized implementation
bundles, not this design pass.
