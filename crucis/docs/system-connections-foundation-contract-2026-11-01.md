# Subsystem 1: minimum record, support matrix and common mechanisms (1 Nov 2026)

Tickets: DLV-08, DLV-09; neighbours DLV-10, ADV-01, DLV-06.
Status: design only. Accepted minimum distinction; concrete contract below is proposed for review.
Parent: [Consolidated outline](system-connections-contract-outline-2026-11-01.md).
Scope: subsystem 1 only. No implementation, execution/spend authorization or protocol adoption.
Current review status: [Final subsystem-1 review packet](system-connections-final-review-plan-2026-11-01.md).
SC-1 and its companion API/interaction specifications now resolve the detailed follow-on proposals; this
foundation remains the conceptual basis rather than the current exact wire-field source.

## 1. Decision now settled

Uzair agreed to evidence preservation as the minimum common foundation, with explicit additional obligations
for interpreting results. An unfamiliar or incomplete native response can have a valid preservation record
without being a valid interpreted result. Evaluation readiness and causal correctness remain separate.

Validity must name its target: envelope well-formedness, evidence binding, a particular semantic contract,
or an outcome assessment. There is no run-wide valid flag. An invalid native claim can be faithfully preserved.
Record conformance does not assert that every expected artifact was captured or that every native assertion
is true. Those are separately scoped claims with evidence.

The profile matrix and specific mechanisms below are recommendations made in this step, not decisions
retroactively attributed to Uzair. Public protocol/version names and current APIs are unchanged.

## 2. Concrete minimum logical record

Names in tables are proposed logical slots. Inline versus referenced encoding is permitted where the
referenced definition supplies the same meaning. No mandatory file per block or per observation is implied.

| Slot | Obligation | Absent historical information |
|---|---|---|
| Record identity | Stable observation/snapshot ID, kind and envelope contract version | The new import always has its own identity |
| Producer | Component/role, producer version and configuration identity or a scoped identity gap | Do not substitute a native version for an importer/parser version |
| Subjects | Typed references to established request, attempt, object or source artifact subjects | Explicit unresolved association; never a fabricated original request/attempt |
| Times | Current record creation/capture/import time, source event time/order where known and clock basis | Original time remains unresolved; import time remains distinct |
| Observation scope | Interface/artifacts/operation boundary examined and limits on completeness | Say what was examined; do not assume a complete original run |
| Statements/gaps | At least one typed, scoped source observation or explicit evidence gap, with basis | Capture/retrieval failure can be the observation; native outcome need not be known |
| Context bindings | Request, participant and information references sufficient for the claims made | Known values, references or explicit localized gaps |
| Object index | Members plus enumeration scope/extent | Empty enumeration, not examined and unresolved extent are different |
| Artifact index | Declarations/snapshots plus enumeration scope/extent | A reported but unretrieved artifact is not a captured snapshot |
| Conditional links | Applicable context/history relations required by the selected profile | Omit irrelevant families; required-but-unknown relations get gaps |
| Profile claims | Versioned profile/feature/guarantee scope and evidence references for claims made | Do not assert interpreted or executable support by default |

Producer gaps are permitted when importing old observation records. A new first-party producer must identify
itself and the relevant adapter/shared interpretation implementation; failure to do that is a conformance
diagnostic, not an excuse to reject preservation of the raw source. The source observation can be captured
inside a new conforming wrapper with explicit limits.

Outcome assessments are conditional. Preservation needs observations/gaps, not an invented completion
assessment. An interpreted object requires its typed interpretation/conformance result. A separate fulfillment
assessment requires a known request contract and the necessary response/scope evidence. Interpretation alone
does not require a known original request or prove that the request was fulfilled.

Every claim's evidence can be an artifact/source locator, a native declaration, a direct observer event, or
a versioned derivation from identified inputs. Do not create an infinite chain of files merely to support
the observer saying what it encountered. Identify observer, basis, scope and any unavailable corroboration.

### Knowledge values

Use one common knowledge wrapper for required slots needing uncertainty:

| State | Required meaning |
|---|---|
| known | A value/reference and source/basis. This means the value of the claim is recorded, not that the native claim is independently true. |
| unresolved | Reason code, affected scope and supporting observations/gaps; candidate values/references if useful |
| not_applicable | A scope and contract/rationale establishing non-applicability |

An omitted optional family makes no assertion about it. A profile can make that family conditionally required.
Do not use bare null as the universal encoding for all three states. A literal null emitted by a native
system is native content and can be preserved as a known literal under the relevant payload contract.

Initial gap reasons: not_observed, not_recorded (only when established), not_retrieved, access_denied,
not_found_at_location, incomplete_capture, unsupported_semantics, interpretation_failed,
unresolved_identity, conflicting_evidence, unavailable_dependency, and unknown_reason. Gaps may coexist;
they are not protocol finding verdicts. Pending/running/stopped, false, zero, abstention and no-edge are
ordinary propositions with their own meanings, not gap reasons.

Indexes describe the enumerated source domain and one of: enumeration_complete_for_scope,
enumeration_partial_for_scope, not_examined, or extent_unresolved. Completeness is always scoped. A complete
enumeration of a response file does not establish complete capture of a native session.

## 3. Support matrix: proposed subsystem-1 contract target

The matrix chooses broad common mechanisms and bounded semantic families. It does not promise a new adapter
for every mapped system, a generic remote-job executor, or evaluation procedures for every family. Each
adapter/path claims only the cells it can meet and validate. Profile labels here are design handles, not
adopted public enums. All selected cells require the minimum record.

Guarantee columns are separate: preserve native evidence; interpret defined meaning; connect to execution;
evaluate scientifically. A cell may have preservation while interpretation/execution are unavailable.

| Profile/family | Proposed core contract target | Recorded/import path | Native/replay path | Limits on the claim |
|---|---|---|---|---|
| E: evidence foundation | IDs, source observations, gaps, declarations/snapshots, provenance and explicit index extent | Required for every import | Required for every captured invocation/observation | No automatic semantic understanding or complete-capture claim |
| D: domains and mappings | Stable variable IDs; ordered axes; roles, units/categories; explicit namespaces and coordinate mappings | Interpret declared schemas and supported mapping contracts | Bind intended and observed schemas without changing native meaning | Relational, learned or temporal identity needs its selected domain extension; no shape-based alignment |
| I: input presentation | Typed content/endpoint descriptors; allowed/intended/delivered/access/use distinctions and transformation lineage | Preserve reconstructed versus observed presentation | Describe exact native-boundary payloads when observable | No universal reader for every data format and no unobserved-use claim |
| G: structural graphs | Explicit family/endpoint semantics, directed cycles versus acyclicity claims, scope, adjacency/absence and associated weights | Interpret selected endpoint/edge-list encodings with versioned mappings | Same semantic contract for actually captured native outputs | No automatic DAG completion, graph repair or flattening of time/latent structure |
| C: scoped claims, sets and orders | Typed proposition/query domain, coverage, abstention; membership versus unreported; partial versus total order | Interpret explicitly defined claim/set/order types | Same meaning for returned local answers | No inferred global negatives or invented edge probabilities |
| Q: quantities and uncertainty | Subject/proposition binding, statistic kind, units, conditioning, source and sampling basis | Interpret typed quantities linked to exact claims/objects | Same contract for native diagnostics/uncertainty/resource measurements | Coefficients, p-values, probabilities, frequencies and weights remain distinct |
| L: collections and associations | Stable member keys, ordered/unordered semantics, multiplicity, weights, pairing and shared domains | Preserve and interpret typed graph/claim/quantity collections | Same meaning for captured sample/ensemble outputs | No deduplication that loses multiplicity; no independence/joint-law inference |
| M: model, representation and state references | Typed role/dependency/domain associations and evidence binding | Preserve artifacts and known associations | Describe actual state load/save evidence if exposed | No blanket interpretation of model internals, learned-factor alignment or exact restoration |
| H: history and contextual relations | Retry, continuation, branch, replicate group, stage, session, action/response, replay and scoped limitations | Represent evidenced history and explicit gaps | Represent observed events and externally managed operations | This is a connection/history contract, not a workflow/experiment engine |
| U: resource accounting | Typed quantities, measurement basis, coverage, membership and explicit aggregation | Preserve reported/observed/estimated amounts separately | Associate consumption and cumulative-scope evidence | Unknown is not zero; inclusive or overlapping scopes cannot be added blindly |

Selected design scope is a recommendation: E plus the shared D/I foundation and defined G/C/Q/L/M/H/U
contracts. All adapters are not required to implement all families. Semantic subtypes and converters must be
listed explicitly; a family name alone cannot claim every conceivable graph, input, model or relation.
Detailed payload schema review must enumerate those subtypes before this matrix becomes implementation-ready.

Advanced systems can therefore connect at the evidence level immediately once an appropriate importer exists,
and gain stronger typed support as domain/semantic converters are validated. Such an evidence-only connection
must be labeled as such. Restricted data stay with their authorized holder; descriptors can preserve a gap
without fetching/copying the material.

### Acquisition routes and readiness

For each adapter, declare one or more routes: read existing artifacts; directly invoke a supplied binding;
prepare a command/job specification for an external runner; attach to/observe an existing job; or reexecute
using recorded external responses. Function/process/container/service is a transport condition, not proof
that the route is implemented. A prepared command is not direct invocation readiness.

Readiness is an assessment at a time/environment for a particular request/profile. It identifies prerequisites,
supported operation, dependencies, schemas, artifacts, route, required authorization and unresolved conditions.
Advertised, assessed-ready and exercised-with-evidence are separate. A ready route does not prove execution
occurred. Replay requires explicit response-matching/coverage policy and no unannounced fallback to fresh calls.
These distinctions supplement, not silently rename, current live/replay/recorded modes.

### Composition rules

- G/C/Q/L/M interpretation depends on identified domains where their semantics require them. Missing original
  request identity does not alone prevent interpreting a well-described native object.
- A quantity attaches to its specific proposition/member/domain. A probability matrix's shape cannot supply
  missing existence/orientation/conditioning semantics.
- Temporal, relational and learned-variable outputs combine a selected domain extension with the result
  family. An opaque identifier can preserve identity without supplying unsupported scientific meaning.
- L specifies collection/member contracts and associations. Q weights need their own declared meaning.
- H interaction records identify participant/action/response semantics and I presentation bindings. Missing
  correlation is a gap; timestamps alone cannot manufacture a matching response.
- H continuation links require attempt/state evidence; M checkpoint references do not establish exact restore.
- U aggregates only under defined membership/coverage rules. Recovery must retain prior cumulative use.
- Unknown required extensions prevent the corresponding semantic/readiness claim, while E preservation
  remains possible. Each composed profile must declare requirements and reject incompatible combinations.

### Support claim record

Each support claim identifies component/version, native subject/configuration scope, path/mode, operation,
feature/type versions, guarantee kind, conditions/dependencies, limits, and supporting evidence. Evidence can
be documentation, native declaration, inspected implementation, observed artifact or executed conformance
check, distinguished by basis. Check evidence records procedure/version, fixture/native source, environment,
result, date and exact scope. Synthetic conformance evidence is not a real-system integration claim.

Evaluation availability is a separate consumer contract reference if known. The connection does not manufacture
an evaluator or declare scientific non-applicability just because its adapter lacks an extraction path.

## 4. Identity, reference and evidence-resolution rules

Proposed default for new IDs: opaque random UUIDs in an explicit namespace, with entity kind in the typed
reference. IDs are assigned/persisted once. No timestamps, paths or content equality determine occurrence
identity. Native IDs remain source-scoped metadata/associations. Exact public string syntax is not frozen.

Requests and persisted snapshots are immutable. Attempt identity names an occurrence; lifecycle changes are
new observations about it. A checkpoint restart is a new attempt with a continuation relation; observer
reconnect can retain the native attempt when identity is established. Request changes create a related new
request. A new intended replicate gets its own request/attempt, without asserting independence.

References identify namespace, entity kind, ID and required snapshot/version where the target has versions.
Define three resolution cases:

1. Internal target: must resolve in the record/package closure, with matching type and bound identity.
2. Declared external target: source authority/package, expected identity and access/availability limits are
   explicit. Offline inspection must not pretend it fetched that target.
3. Unresolved association: preserves source labels/candidates and reason without inventing a resolved ID.

A missing internal target is a package conformance error, not an ordinary unresolved association. Evidence
can still be preserved under a diagnostic wrapper. Content deduplication may share snapshots/storage;
distinct native occurrences and produced views retain their own provenance identities.

Payload locators use a versioned selector contract: JSON pointer/member key, array index/axis mapping, byte
range, or archive member, bound to the exact container snapshot. Member position is usable only under an
immutable ordered-container contract. Do not use current file/list position as a permanent identity by itself.

### Locations, portability and integrity

Package-relative paths resolve against a declared package root and stay within it. External locations use
explicit descriptors; a resolver does not silently search sibling repos or fetch remote data. Copies/moves
add location observations, not new runs or silently revised content pins. No current result move or port map
is authorized by this design.

Exact-byte snapshot identity uses a declared digest algorithm and scope, with SHA-256 proposed as the initial
algorithm. New checks hash bytes actually read; path/size/mtime caching alone cannot substantiate a fresh
integrity assertion. Distinguish expected, externally reported and locally computed digest values. A partial
capture identifies its span/coverage, never the digest of an imaginary complete artifact.

Hash exact stored bytes without newline/encoding/float normalization. A semantic/specification fingerprint
is optional and must name a separate versioned canonicalization procedure, included fields and unknown-value
rules. Initial design does not require request equality hashing; this avoids making a new cross-language
canonicalizer a prerequisite for correct occurrence identity. Legacy canonical hashes remain unchanged.

## 5. Version, configuration and extension behavior

The envelope, request, payload family, domain, relation and assessment procedure have independent versions.
Native software/model versions and adapter/shared converter code identities have separate roles. A parser
update creates a new interpretation with source/procedure lineage, not a new native attempt.

Configuration records preserve explicit values, evidenced resolved defaults and unresolved settings, with
the component/version that resolved them. Distinguish native scientific procedure, operational wrapping,
presentation transformation and later interpretation. Prompt template identity differs from delivered prompt
content. Fingerprints supplement inspectable configuration; they do not conceal which component changed.

Proposed encoding baseline for manifests is UTF-8 JSON, with a published versioned schema after review. Reject
duplicate keys and nonstandard numeric tokens in new manifests. Preserve native source bytes even if their
encoding violates that baseline. Numeric payload contracts retain type/precision and explicitly represent
nonfinite or missing values where relevant; never silently round, clamp or map them all to null. Large native
arrays/models can remain in their original identified artifacts with declared reader contracts.

Compatibility rules:

- Same declared contract version has stable meaning. Changes to interpretation, required fields or meanings
  need a new version and a declared migration/compatibility rule; do not guess compatibility from a number.
- Unknown extension content is preserved with its source/type/version. Its criticality and affected scope
  are declared. If its requirements cannot be understood, withhold the corresponding interpretation or
  readiness guarantee. An unsupported extension does not erase unrelated evidence.
- A consumer must preserve unrecognized content when republishing with a preservation claim, or retain the
  original snapshot and identify its output as a partial/derived view. Reading only known fields is not a
  lossless round trip.
- Unknown envelope versions can be captured as opaque source evidence in a supported wrapper. They cannot
  be declared envelope-conformant without a supported reader.
- No automatic lossy downgrade to the old graph-only contract. Compatibility projection must name its
  selection/mapping procedure, prerequisites and explicit limits.

## 6. Persistence, later updates and duplicate imports

Persist immutable observations and payload snapshots. An in-progress staging area is not a committed record.
Publication checks internal references, declared required members, snapshot integrity and claimed profile
conformance, then exposes a complete manifest as the commit point. This is complete publication of that
manifest, not proof of complete native evidence capture. An unsupported atomic-commit storage backend cannot
claim the publication guarantee until its equivalent protocol is specified and validated.

Partial capture can be deliberately published as partial with gaps. Interrupted writes are not silently
published as complete; surviving bytes can later be recovered into a new explicitly partial observation.
If payloads change during capture, retain the observed snapshot/instability evidence and withhold any
unsupported consistency claim. An invalid native response need not pass its claimed scientific contract
before evidence publication; only the corresponding validated-view claim is withheld.

Corrections add observations/interpretations and typed correction/supersession links with scope, rationale
and evidence. Retain the earlier basis. A convenience current-view pointer can change under a documented
selection procedure, but derived/published assessments pin exact snapshot and procedure identities. Multiple
incomparable corrections can remain unresolved; no blanket newest-wins rule.

For an idempotent import operation, persist its operation key scoped to importer, explicit source identity,
parser/configuration and caller-designated import occurrence. Repeating that same operation returns the
persisted result after checking its bound inputs. Changed inputs under the same key cause a conflict,
not silent overwrite. A deliberate fresh inspection/import uses a new occurrence key and may capture new
availability evidence. Source content equality alone never merges native executions or independently
requested observations. A correction/parser change produces a related new interpretation.

## 7. Adapter/core interface behavior, without implementation signatures

| Operation | Native adapter supplies | Core guarantees/checks | Result and failure boundary |
|---|---|---|---|
| Describe | Native subject, supported feature/path conditions, component identities and native semantics evidence | Validate declaration shape/version and dependencies; keep claims distinct from demonstrated support | Support descriptor with scoped evidence/gaps |
| Bind | Native parameter/input translation and required dependencies | Check request/profile/schema/authorization prerequisites; preserve intended versus resolved settings | Bound request or readiness diagnostics; no native crash inference |
| Acquire/import | Readable source handles, native identities/events/artifacts and observation scope | Assign/reuse correct observation identities; capture snapshots/gaps and provenance | Evidence record even when semantic interpretation is unsupported |
| Prepare execution route | Entry point/argument/job description and promised observation interface | Validate typed binding and route readiness; distinguish prepared versus invocable | Invocation descriptor, not proof of execution |
| Observe invocation/job | Native start/job/event/termination evidence and delivered content where exposed | Associate attempts/observations without manufacturing exactly-once execution; retain ambiguity | Outcome observations and evidence, including loss of contact |
| Interpret | Versioned native decoder, encoding conventions and source mapping | Validate selected domain/payload/reference contracts; retain native claims and diagnostics | Typed view or scoped interpretation failure/limit |
| Publish | Required extracted descriptors and source references | Check manifest closure, evidence bindings and profile claims; retain source on failure | Published snapshot or publication diagnostic/recoverable staging evidence |

These are separable capabilities, not seven mandatory adapter methods. Shared helpers should implement
repeated native formats/transports only under reusable contracts, without system-name branches. Adapter
operations must not silently launch work, fetch restricted data or spend while merely describing/binding/importing.
Caller-authorized external invocation remains an explicit boundary. Subsystem 1 does not choose scheduling,
retry budgets, scientific denominators or experiment actions.

Diagnostics identify phase, component, affected subject, source error, attribution basis and uncertainty.
Native error, adapter decoder error, host/transport interruption, cap, unsupported contract and invalid native
claim remain distinct. If attribution is unknown, say so. Exceptions must not be universally converted to
native-system failure; captured partial outputs survive a later error.

## 8. Current-package compatibility evidence and proposed boundary

Inspected sources, not newly executed checks:

- `audit/core/runs.py`: RunRecord requires a graph for status ok; files/cost/variants/stages are narrower
  existing slots. Preserve this API for existing consumers until a reviewed compatibility path is adopted.
- `audit/core/adapter.py`: Capabilities mixes modes/features/cost class; describe requested route and actual
  readiness separately in the new contract. Keep existing mode strings/guards until explicit adoption.
- `audit/systems/_methods.py`: stored imports and direct run method exist; generic marks_graph collapses
  several endpoint cases to undecided. Do not advertise general lossless endpoint/PAG conversion from it.
- `audit/systems/_probe.py`: recorded graph import exists; command prepares a runner specification and is
  explicitly not executed by that method. Confidence capability is not proof of extraction: recorded()
  does not populate the confidence slot.
- `audit/systems/causal_copilot.py`: recorded sources/stages/replicates exist. Their legacy selection and
  denominator behavior must not be changed by re-labeling them as new requests/attempts.

Recommended boundary: keep legacy reruns/certificates on their existing path during initial connection-core
work. A legacy-to-new wrapper preserves legacy claims and their limitations. New-to-legacy projection is
available only when the old contract is actually satisfied; unsupported broad records do not become ok with
an invented graph. Exact mapping tables and consumer checks remain required before migration planning.
No B5 module or shared analysis/score/harness change is authorized or needed for this design document.

## 9. Composition probes for the concrete rules

These are design acceptance scenarios, not executed tests or newly collected system results.

| Probe | Required representation/behavior |
|---|---|
| P01: unfamiliar historical file | E record with real import identity/snapshot, original request unresolved, interpretation gap; no new native attempt |
| P02: understood graph, unknown original request | G view with established domain/type and source; original fulfillment unresolved, interpretation can still pass |
| P03: final graph plus failed optional confidence parser | Separate graph and quantity interpretations/diagnostics; no relabeling as native crash or automatic graph rejection |
| P04: native DAG claim with a cycle | Preserve native directed structure and contradicted assertion; do not issue a validated-DAG view or repair edges |
| P05: weighted graph samples with paired parameters | L membership/multiplicity/pairing, Q weight meaning and shared domains; no accidental deduplication or averaging |
| P06: local answer plus abstention | C query scope and claim-level decisions; unasked/unreported pairs remain unasserted |
| P07: restart and later reconnect | New checkpoint-restored attempt with H/M links; later observation of that continuing job does not create another attempt |
| P08: temporal partial graph, unknown converter | Preserve native artifact and temporal identity evidence; withhold unsupported interpretation instead of flattening to a static graph |
| P09: command prepared, dependency unavailable | Route described; readiness diagnostic; no assertion that native execution occurred |
| P10: repeated import operation | Same key and bound inputs returns persisted result; different content under that key is a conflict; deliberate reinspection is a new observation |
| P11: missing internal reference versus unavailable external file | Internal closure error versus declared external-availability gap, with different conformance consequences |
| P12: changed file at same path/mtime | Recheck actual bytes; preserve new snapshot/mismatch, never silently refresh the old expected digest |
| P13: crash during publication | No complete committed manifest from partial staging; recover partial evidence under new scoped observation |
| P14: unknown required extension | Preserve source; withhold the affected guarantee and emit a scoped diagnostic, leaving unrelated known views usable |
| P15: session and attempt resource totals | U scope/membership prevents double counting; missing usage stays unknown and restart retains cumulative consumption |
| P16: hidden intervention targets | I records the delivered view; evaluator-only targets do not appear in a system-facing binding |

## 10. Remaining work and decision status

Accepted: minimum preservation versus additional interpretation obligations. Matrix/mechanism choices above
are proposed defaults for review. They fill foundation gaps with concrete rules, but are not approval of exact
schema spelling, every semantic subtype, every acquisition route or an implementation increment.

Next dependent specification work:

1. Review the proposed [domain/mapping fields and invariants](system-connections-domains-mappings-2026-11-01.md)
   and [output subtype fields and invariants](system-connections-output-subtypes-2026-11-01.md).
   Finalize domain/input/result/relation subtype limits, including temporal/relational/learned-domain depth
   and action semantics rather than hiding them in dictionaries.
2. Review the [complete-record composition findings](system-connections-composition-review-2026-11-01.md)
   and [logical specimen records](system-connections-composition-records-2026-11-01.json). Ordinary/import/
   collection/temporal/learned/conflict/correction/partial/local cases now have closed reference examples;
   detailed continuation/interaction examples and final wire-schema forms remain subsequent work.
3. Finish exact producer-consumer operation signatures, package/reader constraints and compatibility mapping
   for current RunRecord/Presented/Graph/Capabilities consumers. Review schema/version labels for adoption.
4. Reconcile all outline gap-register entries, then final subsystem-1 design review. Only after that, plan
   implementation bundles with dependencies, acceptance cases, end-to-end/parity/certificate gates and clear
   unsupported-path behavior. Implementation still needs an explicit go.

No implementation, test, live/replay execution, API spend, result migration, certificate/protocol edit,
paper/tracker/site/shared logic edit, port map or git write occurred. Existing runtime evidence remains dated
as recorded in the rebase. These probes and source inspections are design evidence, not runtime validation.

## Where we're going

Review this proposed matrix and its concrete foundation rules. Then specify selected semantic payloads and
complete records to close the remaining subsystem-1 gaps, before final design review and bundle planning.
