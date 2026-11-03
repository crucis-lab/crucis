# Subsystem 1: consolidated connection contract outline (1 Nov 2026)

Tickets: DLV-08, DLV-09; neighbours DLV-10, ADV-01, DLV-06.
Status: current working design, not an adopted protocol/schema or implementation specification.
Scope: subsystem 1, system connections, only. No implementation go has been given.

Current final-review entry point: [Subsystem-1 review packet and proposed bundle plan](system-connections-final-review-plan-2026-11-01.md).
The bounded serialization, detailed interaction/recovery, exact API and legacy mapping proposals are now
written. They are ready for review, not accepted/frozen or implemented. SC-1 governs proposed wire shapes;
the earlier 147-record JSON remains a logical composition specimen rather than an SC-1 schema instance.

## 1. Review target and authority

Uzair clarified that the upcoming final design review concerns subsystem 1 only. Complete its design before
planning its implementation bundles, each with validation gates and acceptance criteria. Other subsystems
are not being redesigned in this sequence. Describe adjacent interfaces only as needed to bound this one.

Uzair accepted Block 8's boundary alongside the earlier block boundaries, and then agreed to evidence
preservation as the minimum foundation with additional obligations for interpretation. The foundation's
broad direction was subsequently reviewed as sound, with precise domain/mapping and output subtypes requested.
Exact fields,
types, profiles, identity mechanics and implementation details are still proposals. This outline consolidates
the discussion; it does not turn unreviewed proposals into accepted decisions.

For this redesign discussion, use this document as the current outline and decision/gap index. Earlier dated
walkthroughs remain supporting examples. Where early sketches conflict with the distinctions here, the
consolidated distinctions take precedence for the proposal. Existing executable contracts, PROTOCOL.md,
STATE/kickoff constraints, ownership and historical evidence remain unchanged. Shared changes require W5
adoption. The document has no authority to migrate data, change certificate/paper pointers or permit spend.

## 2. Purpose and guiding rules

The connection contract describes what a system was asked, which native execution is evidenced, what it
received, what happened, what it returned, and how those statements are supported. It must accommodate
different result meanings without requiring every response to be a graph.

Accepted architectural directions:

- Faithful evidence and meaning take priority over adapter size or convenient uniformity.
- Put reusable, system-independent contracts/checks in the core. Native translation remains in adapters
  where it cannot yet be expressed through a faithful common mechanism.
- Preserve native evidence, standardized interpretations and derived views as distinct related things.
- Keep requested, declared, observed, reconstructed and inferred statements distinguishable.
- Preserve unknowns, partial results, failures, disagreements and later corrections without invented defaults.
- Separate execution, delivery, fulfillment, capture, interpretation and procedure-specific evaluation.
- Support claims identify features, modes, conditions and validation evidence; archiving bytes is not full
  semantic support, and semantic support is not scientific evaluation.

No adapter line-count target or universal all-good success flag is an acceptance criterion.

## 3. Logical structure: a small manifest with referenced records

The eight blocks are responsibilities, not eight mandatory files, classes or large nested objects.
One small record can contain the ordinary case; larger payloads and histories can be referenced.

    Connection/semantic contract definitions and support declaration
                              |
    Request occurrence ------+------ Intended task, scope, permitted policy
           |
    Attempt occurrence(s) ----------- Native execution evidence, if established
           |
    Observation/import/interpretation snapshots
           |-- 1 Identity/version/producer
           |-- 2 Request/task reference or explicit uncertainty
           |-- 3 Native subject and connection/interpretation identities
           |-- 4 Information manifest
           |-- 5 Sourced outcomes, gaps and optional versioned assessments
           |-- 6 Output-object index
           |-- 7 Artifact/evidence index
           `-- 8 Applicable context/relationship references

A historical import can identify artifacts while leaving the original request/attempt unresolved. No dummy
execution is created. An attempt ID can exist before native start; the ID alone does not prove it started.
One attempt can have several later observations and interpretations. Equal bytes do not merge occurrences.

The supporting vocabulary includes requests, attempts, observations, assessments, schemas/domains, objects,
artifacts, relations and conditional session/event/accounting records. These are logical distinctions;
their physical packaging and identifier syntax remain design work.

## 4. The eight blocks and single ownership of details

| Block | Owns | Minimum responsibility | Conditional detail |
|---|---|---|---|
| 1. Identity and version | Observation/snapshot identity, producer, contract versions and subject references | Identify this persisted record and what it describes; retain unresolved original identity | Correction/import lineage, native job namespaces, ordering/time evidence |
| 2. Request and task | Intended operation, scope, response/completion contract and allowed policy | Bind interpretation of fulfillment to an identified request, or state what historical intent is unknown | Required/co-primary deliverables, allowed abstention, targets, limits, recovery policy |
| 3. System and connection | Native subject/configuration and observer/parser/adapter identities in their separate roles | Identify known participants and provenance of identity claims; expose unknowns | Dependencies, checkpoints, model snapshots, native preprocessing and conversion configurations |
| 4. Information boundary | Allowed/intended/presented information and evidence about access/use | Describe established presentation within an explicit scope; preserve gaps | Data partitions, names/context, interventions, knowledge, callbacks, delivered interaction responses |
| 5. Outcome evidence | Typed observations, gaps/diagnostics and derived assessments | Preserve what is established and uncertain without a global success shortcut | Lifecycle transitions, conflicting sources, versioned reconciliation, interpretation diagnostics |
| 6. Output objects | Semantic descriptors, roles, domains and object derivation/association meaning | Index evidenced or reported objects; explain an empty/unknown index | Graphs, claims, quantities, collections, models, intermediate objects and alternate views |
| 7. Evidence artifacts | Declarations/snapshots, locations, availability and integrity observations | Bind claims to known evidence or record the limit; distinguish reported from captured | Multipart objects, selectors, digests, restricted access, changed locations and partial streams |
| 8. Context relationships | Sessions, recovery/state history, interactions, grouping, replay, resource scopes and limitations | Link applicable context without inventing it for simple cases | Branches, correlated actions, cumulative consumption, shared ancestors and scoped replay limits |

References reuse a fact/relation in its owning contract. Object derivation is defined with Block 6 semantics;
Block 8 can expose the relevant context without independently maintaining a second mutable derivation story.
Artifact availability belongs to Block 7; an outcome assessment may reference it through Block 5.

## 5. Minimum record: accepted distinction and proposed semantic requirements

The distinction between a minimum preservation record and additional interpretation obligations is accepted.
This section proposes its detailed obligations, not final JSON keys or a mandatory eight-section serialization.
Required information can be inline or referenced under a defined contract. The focused
[foundation contract](system-connections-foundation-contract-2026-11-01.md) develops these obligations,
the proposed support matrix and concrete common mechanisms; use it for the next detailed review.

### 5.1 What every persisted connection observation must establish

1. Its own stable identity, record kind and envelope contract version.
2. Its actual producing/capturing component and relevant version/configuration identity. Unknown native
   identity is allowed; the current observer must not masquerade as the native producer.
3. Its subject: known request/attempt/object/source references, or a scoped unresolved association with reason.
4. Observation/import creation time and source event time/order where known, with their distinct meanings.
   An unknown original timestamp is not replaced by import time.
5. At least one scoped observation or explicit evidence gap. An artifact-only import can report capture;
   it need not fabricate native completion. Each statement identifies source/basis and evidence or its limit.
6. Output and artifact indexes with defined extent. Empty, unexamined and unknown are different. A capture
   containing no graph is not a graph with zero edges or proof that no graph was ever produced.
7. Resolution of the other block responsibilities through content/references or explicit applicable gaps.
   Unrelated optional families need no manufactured records or repeated null fields.

An assessment is optional in this smallest preservation record. When emitted, it names its procedure/version,
input observations and assessed scope. A fulfillment assessment also needs the applicable request contract.
An interpreted object requires its typed interpretation/conformance result; that does not inherently require
knowing the original request. A raw import needs no invented outcome conclusions to be accepted as evidence.

### 5.2 Additional obligations for a new prospective request

Before the connection claims it can fulfill a request, the binding must establish operation boundary, task
and target scope, required response family/deliverables, completion/abstention rules, intended native subject,
requested mode, information-access policy and applicable resource/recovery policy. Shared definitions can
supply these details. Record resolved conditions separately from intended ones.

Required prerequisites are checked against the selected support profile and actual connection conditions.
Failure to establish a prerequisite is reported at that boundary; it does not become a fabricated native crash.
This defines connection readiness, not a scheduler, retry strategy or permission to execute.

Historical imports are not forced to satisfy prospective knowledge requirements. Missing intent is preserved
and limits later fulfillment/comparability claims. Evidence preservation can still succeed.

### 5.3 Additional obligations when indexing an object or artifact

An object needs an identity, evidenced/reported origin, type claim or explicit unknown, role/scope, payload
reference or availability gap, and applicable schema/domain and provenance references. Interpretation claims
name a semantic contract and mapping procedure. Required missing outputs are gaps, not invented objects.

An artifact needs a declaration/snapshot distinction, representation and provenance information as known,
plus located/retrieved/captured evidence at its actual scope. Computed/reported digests are separate claims.
No digest is invented for missing bytes. An in-memory native response may be captured inline or serialized;
record that capture procedure rather than pretending it originally existed as a native file/byte encoding.

### 5.4 Ordinary case and sparse historical case

Illustrative logical content; names below are not schema keys:

| Part | Ordinary graph response | Historical artifact with unresolved original execution |
|---|---|---|
| Record | O1, connection observation, contract/observer version, capture time | O2, import observation, contract/importer version, import time |
| Subject | Request R1 and attempt A1, backed by invocation evidence | Original request/attempt unresolved; source artifact association known |
| Request | Declared variable scope and graph response/completion contract | Original requested scope/completion unknown |
| Participants | Known native/configuration and adapter/capture identities | Known importer; native version unknown unless source evidence supplies it |
| Information | References to presented inputs and presentation evidence | Original presentation unknown; do not infer it from the output |
| Outcome | Separately sourced termination and graph-delivery observations | Import/capture observed; original completion/fulfillment unknown |
| Objects | Native graph G1; optionally a separately identified common view V1 | Native/reported object descriptor if justified; interpretation optional |
| Artifacts | Captured response snapshot E1 and graph locator | Snapshot E2, capture location/scope and computed identity if available |
| Context | None needed for a stateless case | Source/import relation as justified; no invented session or attempt |

These examples demonstrate minimum meaning, not exhaustive final record encodings or implemented support.

## 6. Shared rules for knowledge, references and history

### Knowledge and omission

Proposed rule: at a required semantic slot, distinguish an established value, an unresolved value with a
reason/evidence reference, and known non-applicability with its scope. Temporal states such as pending are
actual outcome propositions, not synonyms for unknown. Native abstention, measured zero, false, empty
structure and unavailable evidence are also distinct.

Optional-family omission means no statement is supplied for that family; it must not silently imply zero,
unsupported, unavailable, no events, successful completion or complete capture. Prospective requests/profiles
specify which conditional families must be present. Exact encoding and reason vocabulary remain to be defined.

### References and identity

Locally defined IDs must be unique within the chosen resolution scope and references must identify type and
namespace sufficiently to avoid accidental aliasing. Ordinary internal references must resolve. Historical
unresolved external associations require explicit unresolved-reference records; arbitrary broken references
must not pass as successful resolution. Exact scopes, generation, resolver/package rules and external access
behavior remain open.

Occurrence identity, content fingerprints, locators and semantic equality are different. A request fingerprint
does not merge trials; a native job ID needs a source namespace; a mutable path does not bind fixed bytes.
Payload selectors bind to a particular snapshot and defined selector contract.

### Updates, conflicts and assessments

Persisted evidence snapshots retain identity. Later observations, interpretations and corrections link to their
sources instead of silently overwriting history. Current convenience views can change their selected basis;
published/derived outputs pin their exact basis and procedure.

Compare subject, proposition, scope and event boundary before declaring conflict. Do not resolve disagreement
by generic latest-wins or majority vote. A scoped, versioned rule can assess evidence and retain disputed or
excluded inputs. Storage transactions, partial writes, idempotent import and publication mechanics still need
their own concrete connection-side contract before implementation planning.

### Types, extensions and preservation

Envelope, request, payload, relation and procedure versions are separate from native software versions. A
documented unknown extension can be preserved with its source and unresolved interpretation; it cannot
satisfy a known semantic contract merely by having a similar shape/name. Define compatibility, unknown-field
handling and preservation requirements before freezing serialization. Never silently discard raw fields and
claim exact preservation. Native bytes remain the reference for exact-byte claims; common representations
need separate semantic-preservation claims.

## 7. Support profiles: proposed organization, not selected implementation scope

A profile is a versioned set of obligations for a specific connection path. It is not a ranking of system
quality or one all-purpose capability boolean. Compose three dimensions instead of requiring a profile for
every possible combination. Composition still needs checks for incompatible/dependent features.

### 7.1 Acquisition path: how evidence can reach us

| Candidate path | Claim permitted | Important condition |
|---|---|---|
| Recorded/import | Read and preserve historical evidence; interpret only supported types | Original execution/input/outcome facts remain evidence-dependent |
| Native execution | Connect to an actual invocation through a declared function/process/service route | Exact mode, environment, authorization and supported operation must be established |
| Recorded-response replay | Reexecute with identified recorded external responses | New execution is distinct from original execution and fresh external responses; matching limits explicit |

These are conceptual profile paths, not replacements for existing live/replay/recorded API enums. A prepared
command is a prepared route, not evidence of execution capability. Transport (function, process, container,
service) is another declared condition. Free native execution and paid external calls must not be conflated.

### 7.2 Semantic families: what meaning the core can establish

All profiles use the minimum evidence contract. Candidate optional families are:

| Family | Meaning that needs a precise contract | Failure to prevent |
|---|---|---|
| Variable/domain schemas | Identity, roles, scope, coordinates and mappings, including conditional temporal/latent/group/relational domains | Equal shape or position mistaken for equal variable meaning |
| Graph/structural outputs | Graph family, endpoints, weights if present, scope and absence semantics | Unresolved marks silently oriented, coefficients treated as probabilities |
| Local/individual claims and order/set outputs | Proposition, query/coverage, relation meaning, abstention and unreported domains | A local answer expanded to global negative claims |
| Quantities and uncertainty | Proposition/subject, units, statistic kind, conditioning, sampling basis and missingness | P-values, bootstrap frequencies and posterior probabilities conflated |
| Collections and associated objects | Members, multiplicity, weights, joint/member identities and parameter associations | Graph draws collapsed into one graph or paired with the wrong parameters |
| Models/representations/state artifacts | Artifact roles, variable/model domain, dependencies and evidenced associations | Archiving an encoder/checkpoint advertised as understanding its internals |
| Relations and context | Endpoint roles, basis, provenance and family-specific parameters | Unsupported continuation, ordering, authority or resource aggregation inferred |

These are contract work areas, not seven promised finished implementations. Finer temporal, relational,
model-internal or action semantics require explicit extensions and their own checks where selected. A generic
artifact reference preserves a model without claiming typed interpretation of its inaccessible internals.

### 7.3 Optional behavior/observation families

Static batch, asynchronous job observation, staged outputs, stateful continuation/branching, interactions,
replay/cache tracing and resource accounting add conditional obligations. They are not mutually exclusive.
Partial observability is supported honestly; it must not be advertised as a complete transcript.

For each claimed feature/path, a support declaration should identify:

1. Exact native subject/configuration and feature contract/version.
2. Native support evidence versus adapter access in this mode.
3. Representation/interpretation guarantee, conditions and known limitations.
4. Required dependencies, artifacts, schemas and observation interfaces.
5. Applicable conformance evidence and checked versions, with absent evidence explicit.
6. Downstream evaluation interface availability as a separate referenced claim, if known.

One successful recorded import cannot certify native execution or replay. An interpreted PAG cannot certify
all temporal PAG variants. Native-supported, accessible, preserved, interpreted and checked are distinct claims.
Evaluation methods remain consumers of these contracts; this discussion does not design new metrics.

### 7.4 Recommended decision structure for selecting scope

Proposed baseline: every selected path satisfies the common evidence contract and can preserve an unknown
native artifact without promoting it to a known type. Add specific typed families and behavior obligations
explicitly. Unknown semantics produce a visible interpretation limit, never a guessed graph.

Select scope in a matrix: feature/family, acquisition path, conditions, preservation guarantee, interpretation
guarantee, conformance evidence required, first-increment versus later status. The capability map supplies
design probes, not an automatic commitment to integrate every mapped system. Actual first-increment cells
are still to be chosen with Uzair; no narrow graph-only scope or universal typed support is assumed.

## 8. Core/adapter responsibility outline

| Responsibility | Generic core | Native adapter |
|---|---|---|
| Describing a path | Profile/type/relation definitions and checks | Native features, route/prerequisites and supported version evidence |
| Request binding | Common task/schema/reference/readiness rules | Native accepted parameters and translation constraints |
| Capturing evidence | Common snapshot/provenance/gap mechanisms | Native identifiers, artifact/event extraction and source locators |
| Semantic interpretation | Reusable domain/graph/quantity/collection contracts and validators | Documented native encoding and system-specific extraction |
| Outcomes and history | Common sourced propositions, relation and assessment contracts | Native declarations/events and evidence about their meaning |
| Limits | Preserve unknown/unsupported/conflicting evidence with scope | Identify unsupported native cases; never fabricate missing capabilities |

This is an ownership outline, not an executable plugin API. Method signatures, publication boundaries,
readiness failure behavior, dependency discovery and compatibility shims remain to be specified. Core checks
do not silently repair a system's scientifically invalid output. A cyclic native directed structure and its
contradicted DAG claim can both be preserved while a validated-DAG view is withheld.

## 9. Decision and gap register before final subsystem-1 review

Use this register rather than starting another parallel narrative for each small clarification. Update the
current document as decisions land; add focused examples/specifications only where they materially help.

| ID | Design item | Current status / necessary next result |
|---|---|---|
| S1-01 | Scope and eight ownership boundaries | Accepted architectural direction; subsystem 1 only, Block 8 included |
| S1-02 | Minimum semantic record | Preservation/interpretation distinction accepted; detailed obligations and conditional presence rules proposed in the foundation contract |
| S1-03 | Support profiles and first-increment scope | Concrete proposed initial core/adapter scope and limits in the final review packet; user acceptance pending |
| S1-04 | Identifiers, references and packages | SC-1 fixes UUID syntax, reference variants, byte/selector bindings and reader/publication rules as a proposal |
| S1-05 | Exact common schemas and knowledge states | SC-1 closes the bounded encoding checklist with exact tagged shapes and field tables; structural schema transcription is implementation work |
| S1-06 | Semantic payload contracts | Domain/output meanings and SC-1 body unions specified; selected limits and check scopes ready for review |
| S1-07 | Optional behavior contracts | Detailed interaction/recovery/replay/cancellation/accounting fields, invariants and walkthrough now proposed |
| S1-08 | Adapter/core producer-consumer interface | Exact optional port/core signatures, result/context types, injected services and side-effect boundaries now proposed |
| S1-09 | Persistence and evolution | SC-1 plus API specifies publication, receipts/idempotency, current-selection compare-and-swap and partial data behavior |
| S1-10 | Whole-record composition and conformance | Nine logical scenarios, proposed fixes and small exact-envelope SC-1 specimen inspected mechanically; runtime/schema/semantic validation remains unexecuted |
| S1-11 | Existing-package compatibility | Bidirectional partial mapping and concrete consumer restrictions specified from source; legacy defaults/certificates remain unchanged |
| S1-12 | Final review and implementation planning | Final-review packet and provisional S1-A..G bundle gates prepared; acceptance, final plan confirmation and implementation go remain with Uzair |

The sequence is minimum record, scope/profile choice, dependent concrete contracts and interfaces, whole-record
examples/conformance and compatibility, then final design review and bundle planning. Resolve dependencies
iteratively; do not freeze field spelling before meaning or reopen accepted principles without a concrete issue.

## 10. Review obligations and future validation evidence

These are design obligations, not executed tests or a completed bundle plan:

- An ordinary stateless case stays small; historical capture works with unresolved original intent/identity.
- Retry, checkpoint restart, reconnect, new trial, replay and import have distinct evidenced meanings.
- No unobserved input use, native completion, empty graph, zero cost, independent trial or exact restoration
  is invented to fill a field.
- Native output meaning, domains, collection multiplicity and related-object associations survive selected
  conversions; a lossy transformation is separately identified and cannot satisfy a faithful-view contract.
- Conflicting evidence, corrections and changing availability remain inspectable; downstream users can pin
  exact objects, interpretations, evidence snapshots and assessment rules.
- Profiles reject unmet prerequisites honestly, preserve unknown extensions as specified and do not claim
  modes or semantic families merely because a command or opaque field exists.
- Selected core mechanisms are exercised with structurally different systems/examples, not system-name
  branches. The capability-map probes are design inputs, not evidence of implemented coverage.
- Existing stored-number comparisons must remain within 0.001 and certificates must verify for any later
  bundle touching those paths. Preserve existing public consumers until an explicit adopted migration.
- Each later subsystem-1 bundle has its required tests, an applicable system audit end to end and parity/
  certificate evidence. Exact bundle contents come after the contract gaps above are resolved.

## 11. Supporting documents and current evidence status

This outline consolidates:

- [Principles](system-connections-principles-2026-11-01.md)
- [Capability map](system-connections-capability-map-2026-11-01.md)
- [Early broad record sketch](system-connections-result-record-design-2026-11-01.md)
- [Outcome definitions and cases](system-connections-outcome-cases-2026-11-01.md)
- [Blocks 1-2](system-connections-identity-request-design-2026-11-01.md)
- [Blocks 3-4](system-connections-system-information-design-2026-11-01.md)
- [Block 5](system-connections-outcome-observations-design-2026-11-01.md)
- [Block 6](system-connections-output-index-design-2026-11-01.md)
- [Block 7](system-connections-artifact-evidence-design-2026-11-01.md)
- [Block 8](system-connections-relationships-design-2026-11-01.md)
- [Previous rebase](w2-design-rebase-2026-11-01.md)
- [Minimum, support matrix and common mechanisms](system-connections-foundation-contract-2026-11-01.md)
- [Variable domains, coordinates and mappings](system-connections-domains-mappings-2026-11-01.md)
- [Output subtypes, fields and invariants](system-connections-output-subtypes-2026-11-01.md)
- [Complete-record composition review and proposed gap resolutions](system-connections-composition-review-2026-11-01.md)
- [Complete logical design specimen records](system-connections-composition-records-2026-11-01.json)
- [SC-1 serialization candidate](system-connections-serialization-2026-11-01.md)
- [SC-1 synthetic wire example](system-connections-sc1-example-2026-11-01.json)
- [Detailed interaction and recovery](system-connections-interaction-recovery-2026-11-01.md)
- [Exact API and legacy compatibility](system-connections-api-legacy-2026-11-01.md)
- [Final review and proposed bundle gates](system-connections-final-review-plan-2026-11-01.md)

Consistency resolutions: historical import is an observation, not a new native attempt; checkpoint restart
has a new attempt with explicit continuation; finality/fulfillment/abstention are independent; native origin
and derivation are independent; reported artifacts are not automatically captured; byte integrity,
semantic preservation and scientific correctness are separate. There is no blanket repair or newest-wins rule.

This design document and its focused foundation, domain/mapping, output-subtype and composition companions record the
design discussion. No implementation/tests, existing protocol, result folders,
certificates, paper/tracker/site, protected B5 modules, shared analysis/score/harness logic or git state changed.
No runtime tests were rerun. The dated runtime baseline and wider pending W2 obligations remain in the rebase;
they are not solved by consolidating subsystem 1. C1-C5 are not this subsystem's new bundle plan.

## Where we're going

Review the complete SC-1/semantic/interaction/API/legacy candidate and request targeted revisions. After
design acceptance, confirm the provisional S1-A..G plan and separately authorize the intended implementation
scope. Build one bundle at a time against its acceptance/validation gates. No implementation or redesign
of other subsystems is authorized by this document.
