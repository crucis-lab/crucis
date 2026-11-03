# W2 system connections: successful responses and the common record (1 Nov 2026)

Tickets: DLV-08, DLV-09; neighbours DLV-10, ADV-01, DLV-06.
Status: design discussion. Broader result preservation is accepted by Uzair; the organization below is proposed.
No schema, protocol, finding, certificate or runtime change is adopted or implemented.
Inputs: `system-connections-capability-map-2026-11-01.md` (A01-A18, C01-C28, H01-H04),
`system-connections-principles-2026-11-01.md`, and the current core/report code.

## 1. Decision accepted and boundaries still open

Uzair chose a broader common result record that preserves native outputs faithfully, rather than requiring a
single graph on every successful response. This is an architectural direction, not a claim that every result
family or evaluation procedure is already supported. No implementation go has been given. W2-5 through W2-9
remain pending; any change to the shared protocol or paper contract still goes to W5.

The design aims to accommodate every capability-map case by composition: a common record for the circumstances
and evidence, plus optional result/interaction contracts with explicit meanings. The next discussion can accept
or revise these contracts incrementally. The names below are illustrative; they are not frozen JSON fields.

## 2. What success should mean

A successful response means that the requested operation reached its declared completion condition and produced
a response of a declared kind, and that the connection can identify and preserve that response faithfully.
The response may be a graph, distribution, local answer, explicit abstention, model artifact, or permitted
interaction message. Success does not mean the causal answer is correct, certain, complete for every possible
question, applicable to every metric, or reproducible from inaccessible evidence.

Three scopes must be kept distinct:

- A successful job submission is not a completed remote discovery job.
- A successful interaction step is not necessarily a completed discovery session.
- A complete answer to a local question is not a complete graph over the entire input variable universe.

Preserving arbitrary bytes is useful evidence capture, but is not by itself proof that we understand their
semantics. A future unknown format can be archived with an explicit interpretation gap; it does not count as
fully supported semantic ingestion. Equally, a parse failure must not erase the native evidence or silently
become an empty graph.

### Separate the dimensions instead of overloading one status

| Dimension | Question | Examples of states/reasons to distinguish |
|---|---|---|
| Lifecycle | Where is the requested operation now? | Not started, active, waiting for an action/job, terminal, unknown. |
| Termination | Why did it stop? | Native completion, native failure, external cap, cancellation, host interruption, connection failure, unknown cause. |
| Response scope/completeness | What answer was delivered relative to the request? | Final response, usable partial response, explicit abstention, no response, unknown. Local coverage is described separately. |
| Evidence capture | What did we actually preserve? | Available captured artifacts, known missing artifacts, inaccessible artifacts, unobserved completeness. Completeness always has a declared observation scope. |
| Interpretation/validation | What can the connection establish about each object? | Unrecognized native format, parsed, contract-checked, faithfully mapped, declared lossy projection, failed interpretation. |
| Evaluation readiness | Which procedures can use it, with which prerequisites? | Per-procedure eligibility, missing prerequisites or unsupported semantics; maintained by the evaluator, not a single universal flag. |

These are conceptual distinctions, not proposed replacements for the current protocol status/verdict enums.
Provenance must distinguish system-reported completion from externally observed completion and uncertainty.
There should not be an unqualified all-purpose `success=true` that discards the component evidence.

### Validation must not repair scientific failures

Connection checks establish encoding, type/version, dimensions, references, coordinate mappings and declared
representation invariants. Scientific judgments remain downstream. If a system claiming to return a DAG emits
a directed cycle, retain both the native graph and that claim and record the inconsistency. Do not delete edges
to make it pass. A parseable, preserved answer can be a bad causal answer. If a structural/type inconsistency
prevents a normalized representation, retain a native object and diagnostics without asserting normalization.
Failure attribution is evidence-based: an adapter bug is not automatically a system crash, and an ambiguous
failure remains unknown. A hash establishes identity/integrity relative to observed bytes, not scientific truth
or proof that an inaccessible artifact was seen.

Separate representation from the native system's assertions about it: a directed graph can be retained along
with a native assertion that it is acyclic and an observed contradiction. A claimed probability outside its
valid range can likewise be retained with a diagnostic, never clamped into a valid value. These observations
must not be converted into successful validation of the asserted model/quantity. Operation completion and
faithful capture remain separate from conformance to that scientific assertion.

## 3. Record organization: common envelope plus linked objects

The common record is a manifest of linked evidence, not one enormous nested graph object. Small systems use
a small subset; rich systems attach typed objects and transcripts. Large data, models and native outputs can
remain in separately identified artifacts. One logical record need not place all content in one physical file.

Conceptual organization:

    Record for a requested operation / attempt
      identity and contract versions
      task, scope and request references
      system / adapter / configuration references
      lifecycle, termination and response observations
      output-object index
      evidence-artifact index
      links to session, state, resources and events when applicable
      links to interpretations and derived views

    Separate downstream evaluation records
      procedure, prerequisites and input object references
      projection/selection rule where needed
      computed measurements and later finding/report/certificate references

The envelope provides common addressing and accounting. Each output type defines its own payload semantics.
An extension with an unknown payload can still be preserved and identified, but consumers must not silently
interpret it as a known type. A new semantic contract requires a type/version definition and conformance checks.

## 4. The minimal common envelope

Required here means that the common record must answer the question or explicitly record why it cannot.
It does not require inventing missing historical information. Exact field names, encoding and enums remain open.

| Block | Minimum question it answers | Detailed content may be referenced |
|---|---|---|
| Record identity and version | Which record/attempt is this, under which envelope contract? | Stable record ID, schema version, producer identity, observation/import time and relation to any source record. |
| Requested operation and task | What was requested, for which scope? | Task type, item/arm/query IDs, target variables, requested coverage, completion contract, and parent session if any. |
| Subject and connection identity | Which system/configuration and which adapter produced/interpreted it? | Native version/checkpoint, resolved configuration, adapter and shared converter identities; declared versus observed values. |
| Presented-information manifest | What was permitted/supplied to this operation? | Dataset/schema references, names/context/knowledge, interventions and tools/callbacks; actual interactions linked as events. Supplied does not prove consumed. |
| Outcome observations | What happened and how do we know? | Lifecycle/termination/response facets, source of each observation, partial evidence and diagnostic references. |
| Output index | What objects were returned or captured? | Stable object IDs, roles, semantic types/versions, declared scope and evidence references. An empty index needs a reason. |
| Artifact and availability index | Where is the evidence and what is known about it? | Artifact identity, location/access status, format, digest algorithm/value if available, origin and source locator; computed versus externally reported digests. |
| Conditional links and limitations | Which additional records apply, and what cannot be established? | Session/attempt lineage, state, events, resources, interpretation results and missing-information reasons. |

The request record is separate from evaluator-only references. Battery truth, hidden targets and scoring
references must not be passed to the system merely because the auditor can link them. An explicitly authorized
oracle control remains identifiable in the request. Historical mode can link a reconstructed request manifest,
with reconstruction provenance and uncertainty rather than pretending it was observed at runtime.

The final record and output/artifact references should form an integrity structure that avoids self-referential
hash cycles. Native evidence and derived views are distinct. Packaging, content-addressing details, signing,
and certificate integration belong to later design work rather than being silently specified here.

## 5. Each output object has a small common descriptor

The envelope can hold multiple output objects rather than one optional slot for every future algorithm.
Every object descriptor should identify:

1. Its stable ID, semantic type, type version and role (for example primary answer, intermediate state,
   checkpoint, diagnostic, or requested action).
2. The task/query and declared variable/claim coverage to which it responds, including its coordinate domain.
3. Its native evidence artifact(s) and precise locator, where available. A file pointer, array key or transcript
   event reference is evidence addressing; IDs should not depend on a list's current position.
4. Origin: native output, observed event, adapter reconstruction, or auditor derivation. These origins can
   refer to each other but must not be relabeled as equivalent evidence.
5. Available interpretations and their validation status, including explicitly unknown or unsupported semantics.
6. Relationships to other objects: members/samples, weights, fitted parameters, variable schema, encoder,
   stage input/output, source statements, uncertainty annotations, or derived-from links as appropriate.

Availability is per object and field. Missing, unsupported, unrecorded, inaccessible, unknown, explicitly empty,
zero and false are different states. Use structured reasons where absence changes interpretation; do not
give every missing field an invented default. There is no need to wrap ordinary unambiguous values in an
unlimited hierarchy of status objects.

## 6. Optional semantic contracts

These families describe how to retain meaning across the capability space. They are proposed design units,
not a promise to implement all families in the first increment.

| Contract family | What must be preserved | Typical result or attachment |
|---|---|---|
| Variable/schema registry | Stable IDs versus display names/positions; data types; observed/context/latent roles; temporal/relational/group identity; mapping versions. | A graph can reference observed columns or learned factors without pretending they are the same universe. |
| Dataset/information descriptor | Raw samples versus statistics/oracle access, sampling organization, partition/environment membership and supplied knowledge semantics. | Typed references used by the request and interpretation; evaluator-only truth remains separate. |
| Graph | Graph family, endpoint meanings, direct/ancestral/temporal relation semantics, weights and their units, coverage, native conventions and conflicting marks. | Directed/partial/latent-variable/cyclic/temporal graph objects with declared invariants. |
| Collections and distributions | Member IDs, joint graph/parameter association, sampling basis, probability/weight meaning, normalization if applicable and sample provenance. | Posterior particles, bootstrap replicates or weighted candidate structures without conflating them. |
| Claims, local sets, orders and constraints | Proposition and queried domain; direct versus ancestral meaning; local/full coverage; order versus causal edge; no-edge/undecided/abstained/unasked distinctions. | Pairwise responses, parent/blanket sets, partial orders, constraints or ranked candidates with their stated interpretation. |
| Quantities and uncertainty | Proposition/conditioning, numeric kind and unit, p-value/probability/frequency/coefficient/score/interval semantics, native versus derived origin, decision rule. | An edge probability, directional test result, confidence interval or coefficient attached to the relevant object/claim. |
| Models and learned representations | Artifact/checkpoint identity, declared input/output schema, learned variables, encoder/mechanism relationships and state availability. | Learned factors plus an encoder, parameters/mechanisms accompanying structure, or a native model artifact. |
| Events, actions and sessions | Ordered requests/responses, who selected/permitted/performed each action, state transitions, pauses, completion contracts and evidence boundaries. | Active experiment loop, expert/model callback, distributed round, asynchronous job or online update. |
| Execution observations and resources | Native/connection/host termination evidence, attempt and session boundaries, unit/scope of costs, partial results and observed/estimated/unavailable accounting. | Time, calls, samples, interventions and other resources without assuming every measure exists. |
| Provenance, interpretations and derivations | Parent object IDs, exact transformation/implementation/configuration, evidence origin, semantic loss and verification state. | Mapping a native graph, reconstructing a stage or deriving a point graph from samples. |

For an opaque future result, retain its native type/format declaration, artifact and scope when available.
Storage support can then precede a new semantic contract, while interpretation/evaluation stay explicitly
unsupported. This is an extension path, not a substitute for specifying the family's meaning.

A model artifact or remote handle may be recorded without being runnable later. A handle's presence is not
permission or proof of reproducibility. Any supported invocation/sampling interface is a separately declared
capability with its own requirements. Artifact inspection must not implicitly execute native serialized code.

## 7. Native output, interpretation and evaluation are separate layers

1. **Native evidence:** the exact available response/artifact plus the observed circumstances of its production.
2. **Interpretation:** a type-aware translation into a standardized representation, linked to its source,
   coordinate mapping, parser/contract version and any limitations. Representation validation is explicit.
3. **Derived view:** an additional operation such as selecting a graph, thresholding, marginalizing particles,
   reconstructing a stage or aligning learned variables. Preserve parameters, implementation identity, inputs,
   output and known semantic loss. A native algorithm's own thresholding is identified as native configuration.
4. **Evaluation:** a later record identifies the task-compatible procedure, required reference/evidence,
   projection if any, computed metrics and why other evaluations are unavailable. Findings/reports/certificates
   consume these records under the adopted protocol.

The native layer is retained when interpretations improve. New interpretations do not overwrite old ones;
they are versioned derivations from the same observed source. A native artifact is not guaranteed to contain
every internal state: capture completeness is always relative to a declared observable interface.
An evaluation reusing old evidence retains its original data/run chronology; new extraction does not make
the old observations prospective or confirmatory.

This separation permits the core to grow without needing a special algorithm branch in every scorer.
Evaluators declare required semantic inputs. An unrelated new adapter producing an already supported type
can use that evaluator after conformance; a new semantic type cannot be coerced into it automatically.

## 8. Attempt, result, session, variant and aggregate are different units

- A request defines the operation and scope; a session may issue many requests over time.
- An attempt is one invocation/import observation tied to that request, with its own identity and outcome.
  Importing historical evidence must retain the original run identity where known and distinguish the new
  ingestion identity/time. It is not a newly executed causal-discovery run.
- A response/result bundle belongs to a request/attempt and can contain several objects, including no usable
  primary answer with an explicit reason. Partial objects can survive an interrupted or failed attempt.
- A retry, resumed continuation and independent replicate have different relationships. Record them explicitly;
  choosing the latest or best answer is an experiment/aggregation policy, not adapter behavior.
- A native pipeline stage/variant links to its parent run. An independently rerun knowledge-off condition is
  a different attempt/experimental arm, even when it is described as a variant for comparison.
- An aggregate over attempts, a round or a version comparison is derived evidence with a selection/combination
  rule and member references. It is not the native result of one system invocation.

For streaming/stateful systems, distinguish snapshots and revisions rather than repeatedly overwriting one
result ID. Parentage/state references allow a reader to understand updates without requiring the common
record to duplicate an entire history. Live observation may have an event sequence plus immutable snapshots;
terminal record packaging and append/immutability policy are implementation choices still to be designed.

## 9. Walkthroughs across the mapped space

These are conceptual examples applying the researched map, not new executions or measured results.

| Case | What the common record preserves | What success means | Evaluation boundary |
|---|---|---|---|
| C01 static PC/GES | Request, graph/schema, native artifact, configuration, completion and resources. | Native operation completes and its graph is faithfully interpreted. | Wrong arrows remain a successful captured response; accuracy is measured later. |
| C02/C04/C07/C11 intervention, configuration and context cases | Presented targets/context/knowledge, actual configuration, cache identity where applicable and graph output. | The declared native operation and graph response are preserved with those conditions. | Different information or assumptions are not silently treated as an identical experimental regime. |
| C03 FCI / C12-C14 temporal graphs | Graph family/endpoints, variable roles/lags, any dataset/context identities. | Requested structure is delivered and interpreted under the right graph semantics. | No automatic conversion of a partial endpoint to a definite arrow or temporal edge to an ordinary self-loop. |
| C05-C06 sufficient statistics / CI callback | Typed request evidence or query transcript; sample-size meaning and test identity. | The defined operation completes using the supplied statistical interface. | Raw-row controls may be unavailable; no fabricated samples. |
| C08-C10 multi-group / weighted / intervention methods | Group/mask identities, knowledge semantics, coefficient/weight meanings and native thresholds. | The expected typed object(s) are delivered and interpretable. | Evaluator-only intervention targets stay hidden when not supplied by the request. |
| C15 DiBS-style posterior | Graph/parameter members and joint associations; native evidence; sampling/configuration metadata. | A collection conforming to the declared response contract is captured. | No mandatory point graph; marginal or point summaries are separately derived views. |
| C16 directional tests | Two named directional test quantities attached to the queried variables. | The requested tests return validly encoded, interpretable responses. | P-values are not edge probabilities; a later direction-decision recipe requires its own definition. |
| C17 local discovery | Target, candidate universe, returned set/claims and coverage semantics. | A final answer to the local query is preserved. | Unqueried pairs are not false negatives; completeness is relative to the request. |
| C18-C19 pretrained / learned representation | Checkpoint/configuration; encoder, graph and learned-variable identities; native artifacts. | Requested inference/training response completes with interpretable model/representation references. | Evaluator alignment is a recorded derivation; no reference-derived relabeling supplied to the system. |
| C20 relational discovery | Relational schema/perspective and native structure references. | The declared relational result is preserved under a known semantic contract. | A flat graph projection is not silently substituted; unavailable relational metrics remain unavailable. |
| C21 active discovery | Session, typed actions/responses, allowed endpoint, sampling/state history and stopping evidence. | Each step has its own completion; the session completes only under its task contract. | A cap can terminate the session while leaving a usable partial graph; recording that graph does not erase the cap. |
| C22 expert loop / C23 federated / C24 online | Callback/round/update events, actors/partitions, state references, result objects and evidence access. | Completion is evaluated at the declared step/session/update boundary. | Missing centralized data or incomplete transcripts limit verification claims, not native existence of results. |
| C25-C28 current LLM/hybrid systems | Supplied names/context/data, final objects, native sources, observed/reconstructed stages and actual execution route. | The particular recorded or executed operation is faithfully represented. | Missing probability extraction or stage artifacts is explicit; command preparation is not execution. |
| Future unrecognized format | Artifact plus observed producer/operation/outcome, declared native type and interpretation gap. | Capture can succeed; native completion may be reported/observed. Semantic integration is not established. | No applicable evaluator is invented. |

Explicit abstention can be a final, well-formed response if the declared task contract permits it. An empty
graph is likewise a substantive response if the system actually returned it, rather than an adapter's fallback.
Absence of all output after a crash is a different outcome. Neither correctness nor abstention quality is
decided by calling the connection successful.

## 10. Crosswalk to all 18 capability axes

| Map axis | Where its information belongs in this design |
|---|---|
| A01 task/scope | Request/task contract and every output's declared coverage. |
| A02 variable identity | Shared schema/identity registry plus mapping/encoder references. |
| A03 evidence form | Typed presented-information descriptors and source artifacts. |
| A04 sampling organization | Dataset/schema/group/partition descriptors and state/window references. |
| A05 interventions/contexts | Supplied-information descriptors, typed action/events, evaluator-only reference separation. |
| A06 knowledge/channels | Request payload/provider/constraint semantics and actual interaction transcript. |
| A07 assumptions | System/configuration declarations and result-family contracts, with assertion origin and unknowns. |
| A08 computational access | Versioned endpoint/callback descriptors and request/response evidence. |
| A09 interaction | Optional sessions, actions, event ordering and step completion contracts. |
| A10 lifecycle/state | Attempt/session relationships, checkpoints, reset/update/cache/seed policy and observed state references. |
| A11 result families | Output index plus independently typed graph/collection/claim/model/etc. objects. |
| A12 semantic meaning | Result-family definitions, graph/claim semantics, coverage and versioned interpretations. |
| A13 uncertainty/abstention | Quantity/proposition contracts and response/coverage observations. |
| A14 provenance | Native/observed/reconstructed/derived origins and source-event/artifact links. |
| A15 execution/transport | Connection/mode/transport description, invocation or import evidence and readiness. |
| A16 resources/failures | Outcome observations, diagnostic evidence, per-attempt/session resource accounting and partial outputs. |
| A17 identity | Native/adapter/shared implementation/configuration/environment identities, with declared/observed distinctions. |
| A18 evidence/access | Artifact availability and observation scope; interpretation and verification limits. |

The same organization accommodates the four combination probes without inventing a new top-level format:
H01 combines temporal schemas, graph collections and remote job evidence; H02 combines sessions, intervention
visibility and resource termination; H03 combines stateful sessions, several information channels and expert
events; H04 combines distributed schemas, learned representations and restricted artifact access.
This is an architectural fit argument, not a claim that those semantic contracts have been implemented or validated.

## 11. Current-code relationship and future migration constraints

`audit/core/runs.py` currently requires a graph for status ok and has optional variants, confidence, sources,
cost, stages, files and notes. The proposal broadens the conceptual model rather than editing those fields now.
`audit/core/graph.py` remains an existing graph representation, not a universal result superclass.
`audit/core/evidence.py` and `audit/report/certificate.py` remain the existing evidence/certificate paths.

Later compatibility could expose a graph view from a known graph-type object to the existing scorers; it must
not select a graph from a distribution or invent one from a pairwise test result without an explicit recipe.
Whether this is a compatibility layer or a versioned replacement is an open implementation-design choice.
The new record is not itself a report, certificate, round or version-comparison aggregate. Their formats and
stable paper pointers are separate shared contracts. Do not rename folders, regenerate stored outputs,
rewrite historical labels or alter the 1,298-number gate as a side effect of this discussion.

## 12. Tradeoffs and unresolved design details

| Choice | Recommended direction | Cost or strongest alternative |
|---|---|---|
| Minimal envelope plus linked typed objects | Generic composition and progressive capability growth. | More references and validation than one flat graph record; a flat record becomes brittle as the map expands. |
| Faceted outcomes | Keep execution, response, capture, interpretation and evaluation separate. | More vocabulary; a single status is easier to display but hides scientifically material distinctions. A derived display summary can remain convenient. |
| Native evidence plus standardized views | Retain provenance and allow improved interpretation. | Storage/indexing cost; standardized-only storage loses evidence about translation or projection. Large artifacts should be references, not forced inline payloads. |
| Explicit extensions | Unknown types can be preserved but cannot silently satisfy a known semantic contract. | Requires type/version ownership and conformance; arbitrary untyped dictionaries shift ambiguity to every evaluator. |
| Event/session support | Optional records for interactive/stateful workflows. | Complexity; simple batch results should not require fabricating a detailed event log. |
| Rich identity/availability | Explicitly record what can be established and unknown reasons. | Metadata burden; require meaningful evidence rather than filling every possible field for every system. |

Details to settle in later design discussions: precise success predicates at each operation boundary; the
minimal mandatory envelope fields; object identifiers and version/extension rules; exact graph and uncertainty
contracts; coverage/absence semantics; state/attempt accounting; artifact and event packaging; compatibility
with existing RunRecord and downstream certificates. No enum or data class is frozen by the illustrative names.

## 13. Acceptance obligations before implementation

- Every C01-C28 and H01-H04 case has a faithful conceptual encoding or a named unsupported interpretation;
  unsupported semantics cannot masquerade as supported evaluation.
- A well-formed wrong answer, an explicit abstention, an empty native graph, a local answer, a partial result,
  an unrecognized artifact, an adapter failure and a system failure remain distinguishable.
- No zero-valued/default graph or confidence is invented to satisfy the envelope.
- Stable IDs, schema/version references and provenance edges resolve. Mapping touches every indexed field;
  learned, relational and temporal identities are not forced into an unqualified column index.
- Every derived view identifies its inputs, procedure/configuration and semantic loss; native evidence survives.
- Request permissions/presentation stay separate from evaluator truth. Supplied and actually observed access
  are distinguishable; unavailable evidence remains unavailable.
- Direct execution, recorded import, replay, pending remote jobs and session steps have distinct completion
  claims. Submission is not job completion; ingestion time is not original run time.
- Partial outputs and retry/resume/replicate relationships survive termination and cannot silently change
  cost, completion or selection denominators.
- A common mechanism can serve structurally different systems under the same semantic contract, with adapter
  specifics limited to native invocation/translation. These requirements will become checks only after design approval.

Only this new design document was written in this turn. Existing code, tests, protocol, results and shared
paper/tracker/site files remain unchanged. The next discussion should start with the success/outcome distinctions
and the minimal envelope before freezing any optional family or implementation plan.
