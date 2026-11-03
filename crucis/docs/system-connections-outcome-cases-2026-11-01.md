# W2 system connections: outcome definitions, cases and common blocks (1 Nov 2026)

Tickets: DLV-08, DLV-09; neighbours DLV-10, ADV-01, DLV-06.
Status: design discussion only. Adds worked definitions to `system-connections-result-record-design-2026-11-01.md`.
No implementation, protocol enum, public schema, result migration or finding-rule change is made.

## 1. Accepted direction and what is still proposed

Uzair accepted separating what happened in execution, what response was delivered, what evidence was preserved,
what the connection can interpret, and which evaluations apply. Broader native-result preservation was already
accepted. This document works through the requested cases before detailing the eight common blocks.
The exact vocabulary, required fields and predicates below remain design proposals for discussion; acceptance
of the distinctions is not adoption of every enum or an implementation go. Shared contract changes still go
to W5. The historical W2-5 through W2-9 decisions remain pending.

## 2. Definitions anchored to the requested operation

The unit of outcome must be explicit: job submission, one inference request, one update, one interaction step,
or the whole discovery session. A parent operation can still be active while a child operation has completed.

Before execution, the request contract should establish the operation, intended response kind, required
deliverables and scope, permitted abstention, and how completion is recognized. It also states the role of any
resource limit. These are experimental/interface requirements, not thresholds for declaring scientific findings.
For historical records, recover only what the evidence supports and mark the rest unknown. Never retrofit a
completion rule merely to make an observed outcome look successful.

Use qualified terms:

- **Execution completed:** evidence supports reaching the operation's declared normal completion boundary.
  A process exit, service claim or terminal event is recorded with its source. A zero exit code alone does not
  establish that every requested deliverable was produced or that the result is scientifically valid.
- **Response delivered:** an answer object/artifact/message was actually received or is evidenced. This can
  coexist with later failure. Distinguish native final versus intermediate designation from coverage/completeness.
- **Requested response fulfilled:** the response covers the deliverables/scope required by the request contract.
  This is fulfillment of an interface/task request, not proof of causal correctness. Partial fulfillment and
  unknown fulfillment are explicit possibilities.
- **Capture succeeded for a declared scope:** the specified observable evidence was preserved. This cannot
  claim unseen internals were recorded, and a reference to unavailable bytes is not possession of those bytes.
- **Faithful interpretation succeeded for an object/view:** the connection has preserved the observed meaning,
  variable identities and native assertions under a known interpretation contract, with limitations exposed.
  Correctly recording an invalid native assertion does not validate that assertion.
- **Evaluation eligible for a particular procedure:** that procedure's input semantics and prerequisites are
  satisfied. This is determined downstream. Eligibility neither guarantees a good score nor applies to every
  other procedure.

A convenient display may summarize these observations, but there is no authoritative unqualified success bit.
If the word successful is used, name the operation and the kind of success: execution, response fulfillment,
capture, interpretation or evaluation. A system-quality judgment must not be inferred from these summaries.

### Separate dimensions within the response

Final/intermediate describes where a response sits in the native workflow. Full/partial describes fulfillment
relative to the request. Asserted/abstained/unresolved/no-edge describes decisions over particular claims.
These are not one mutually exclusive list. A final response can fulfill a request by explicitly abstaining;
another final response can contain assertions for some pairs and abstentions for others. A complete local
answer can leave the rest of the global graph unqueried.

Unknown is epistemic, not another kind of system behavior. An absent old log may mean we do not know the
termination reason; it does not establish that the system failed or abstained. Likewise, a disconnected client
does not establish that its remote job stopped. Distinguish last observed state from current state inferred
from new evidence, and retain the observation time.

### Sources and contradictions

Outcome observations need a scope, time/order where available, source/actor and evidence reference. Keep native
claims, runner observations, adapter diagnostics and later deductions distinguishable. If a service reports
completion but a required artifact is missing, preserve both facts. Do not silently choose a favorable source.
A derived summary can report the conflict or unknown fulfillment. Later evidence adds a traceable update rather
than rewriting history.

## 3. Concrete cases and edge cases

These are hypothetical design cases, not new experiment results.

| Case | Observed facts | Faithful classification and preservation |
|---|---|---|
| O01 normal graph answer | The operation reaches its completion boundary and returns the requested graph. | Execution completed, graph response delivered, requested coverage fulfilled if confirmed, capture/interpretation recorded separately; causal accuracy is still unjudged. |
| O02 wrong arrows | Same operational facts as O01, but later comparison finds errors. | The execution/response record remains what happened. The errors belong to evaluation, not a retroactive crash status. |
| O03 empty native graph | The system deliberately returns a graph with no edges under a full-graph task. | A real delivered answer. Its emptiness is preserved; graph quality is assessed later. This differs from a missing graph replaced with an empty default. |
| O04 explicit abstention | The native response says it cannot answer, or abstains on some queried claims. | Record abstention at its actual scope. A final abstention fulfills the request if the agreed contract permits it; a mandatory answer remains unfulfilled otherwise. Preserve abstention either way. |
| O05 unresolved structure | A system returns a valid partial/equivalence representation with unresolved directions. | It can be a final, complete response of that declared type. Do not automatically call every unresolved direction a voluntary abstention or force an orientation. |
| O06 local question | Asked for a target's local neighborhood; system returns that neighborhood. | Assess fulfillment against the local question. Other pairs are outside the query, not missing global predictions or asserted no-edges. |
| O07 posterior or tests | The native response is graph samples or directional test quantities. | These can fulfill their declared response contracts without producing a point graph. Point selection or direction decisions are separate derived procedures. |
| O08 external cap with snapshot | The runner enforces an external limit before native completion; a checkpoint/graph snapshot exists. | Termination by cap and lack of native completion remain explicit. Preserve snapshot as intermediate/partial with its own role and scope. Later scoring must state its selection policy. |
| O09 bounded operation completed | The request itself asks for a bounded run returning its current answer, and that native boundary is reached. | Completion can be normal under this contract. Preserve the stopping policy; do not equate it with O08 merely because both involved a limit. |
| O10 system error after output | A graph was delivered; the system subsequently raises an error before the requested operation finishes. | Keep both the delivered graph and the failed termination. Do not discard the graph or let its existence erase the failure. Whether it was final is a separate observation. |
| O11 parser failure | Native bytes exist, but the adapter cannot read them. | Capture may have succeeded; interpretation failed or is unsupported. System execution may be completed or unknown. Cause attribution depends on evidence about the native format and adapter. No invented empty graph. |
| O12 unknown native format | A future system emits a documented native artifact that has no registered interpreter yet. | Store native type/format declaration, artifact and known scope. Archival capture can succeed; semantic support and evaluation remain unavailable. |
| O13 violated native assertion | A claimed DAG contains a cycle, or a claimed probability lies outside its valid range. | Retain native values and the assertion; record the contradiction/validation diagnostic. Never remove edges or clamp a number to make the assertion pass. A faithful capture is not valid scientific output. |
| O14 conflicting completion evidence | A service says done, but one requested artifact is unavailable or missing. | Keep its reported completion, observed artifact availability and unresolved/partial fulfillment separately. Do not invent the missing artifact or presume the provider's failure mechanism. |
| O15 async or lost contact | Submission returns a job ID, or the client loses contact after observing a running job. | Submission can be completed while discovery is pending/unknown. Record the last observed state and time. Lost contact alone does not establish remote failure, cancellation or completion. |
| O16 adaptive step | An active system returns a request for another permitted experiment. | The action-selection step may be complete; the discovery session remains active/waiting. The request, authorization and experimental response become distinct linked events. |
| O17 successful retry | An earlier attempt fails and a later attempt completes. | Preserve both attempts and their relationship. A selection rule belongs to experiment/aggregation design; do not overwrite the failure or double-count resumed work. |
| O18 incomplete historical evidence | A final graph is available but a trace, native version or original completion evidence is absent. | Interpret the graph where justified and record unknown/missing facts. Do not invent a new original run, native termination evidence or complete trace. Verification claims narrow accordingly. |
| O19 mixed object availability | Graph is delivered and interpretable, while optional confidence metadata is absent or its parsing fails. | Graph interpretation can succeed while confidence interpretation is unavailable/failed. Track required versus optional deliverables; do not call the whole native system a crash based solely on optional extraction. |

Failure attribution is not guessed from one error word. A timeout can be an external runner cap, a native
exception or an ambiguous historical message. Record actor/layer, the observed symptom and any supported cause.
The same principle applies to resource exhaustion, output corruption and interrupted connections. A later
finding may use these observations under an adopted classification policy; the connection preserves evidence.

## 4. How these definitions populate the eight common blocks

The blocks are conceptual responsibilities, not frozen field names or eight mandatory nested dictionaries.
Details can be referenced; unknown historical facts carry a reason instead of a fabricated value.

### Block 1. Record identity and version

Purpose: distinguish an original operation/attempt, its observation/import, and later interpretations.
Needs: a stable record ID, envelope version, producing component/version and creation/observation time;
links to the original request/attempt/source record where known. Original execution time, capture time and
later import time are distinct. A new import does not pretend the system ran again. File paths or list
positions are locators, not durable object identities. Identifier generation and packaging are still open.

Example O17: the failed attempt and retry have different identities. Example O18: a new import record points
to the old run if known; unknown original time/version stays unknown.

### Block 2. Requested operation and task

Purpose: make completion, fulfillment and coverage interpretable.
Needs: the operation type and boundary, task, item/arm/query, target/candidate variable universe, intended
response family, required versus optional deliverables, permitted abstention, native completion evidence,
applicable limits and parent session. A reference to a versioned request contract may supply common details.
Experiment design chooses the question and resource policy; the adapter does not silently redefine it.

O06 is complete for a local question; O08 and O09 differ because their agreed completion rules differ.
O19 requires knowing whether confidence was an optional extra or part of the promised response.

### Block 3. System and connection identity

Purpose: establish whose behavior and whose interpretation are represented.
Needs: system/version/checkpoint and resolved configuration, native preprocessing and relevant dependencies;
adapter, parser and shared translation versions; observed versus pinned/declared versus unknown identity.
State/cache/checkpoint references may be necessary to identify a stateful operation. The native system's
configuration and the auditor's interpretation configuration are separate even when both influence a final view.

O11 may result from an outdated parser, not the native system. O13 preserves the native assertion and the
identity of the checker that diagnosed it. Future shared converter changes need identity coverage beyond
the thin adapter file's hash.

### Block 4. Presented information

Purpose: preserve the actual experimental information boundary.
Needs: typed input and variable-schema references; relevant data partitions/time/context; names/descriptions,
knowledge/constraints, intervention metadata, tools/oracles and endpoints offered; supplied versus allowed
versus actually observed access. Runtime requests/responses link to events rather than being guessed from
a static capability declaration. Passing data does not prove that an algorithm used it internally.

Evaluator-only references/hidden targets stay separate from system-facing payloads. A historical reconstructed
manifest is labeled as reconstructed. O16 records exactly which experiment information was returned; later
evaluation cannot quietly use its own truth to enrich that response.

### Block 5. Outcome observations

Purpose: record O01-O19 without collapsing their distinctions.
Needs: operation lifecycle and termination evidence; response designation and requested-scope fulfillment;
relevant claim-level decisions; capture and interpretation observations/references; missing/conflicting
evidence and diagnostics. Each material statement has a source, scope and time/order where available.
Evaluation readiness and scientific judgments remain downstream or explicitly linked, rather than native facts.

O10 can have a delivered graph and an execution failure. O14 can have reported completion and unknown
fulfillment. O19 can have successful graph interpretation and failed optional confidence extraction.

### Block 6. Output index

Purpose: enumerate the objects actually returned/captured and their roles.
Needs: stable object IDs, native type declaration and interpretation/type version where known; primary,
intermediate, checkpoint, diagnostic or action role; scope/coordinate-domain references; source artifact and
locator; relationships to collections/parameters/uncertainty/stages; native versus reconstructed/derived origin.
An empty index has an explicit reason. An unreadable artifact can still appear in the evidence index with
an interpretation gap; it is not silently promoted to a parsed graph.

O07 indexes graph samples or test quantities as native objects. O08 identifies its snapshot as intermediate.
O03 contains an explicitly empty graph object, which differs from an index containing no graph object.

### Block 7. Evidence and artifact availability

Purpose: make preservation and verification claims inspectable.
Needs: artifact identity, format and location/access state; origin and source locator; content digest and
algorithm when computed, or a clearly labeled externally supplied digest; capture scope; known missing or
inaccessible evidence. A path or remote handle is not proof of byte availability. Availability can differ by
reader/environment and should be an observation, not a timeless claim that the file exists everywhere.

O11 retains native bytes and parser diagnostics. O12 retains an uninterpreted artifact. O14 records the absent
artifact without a fake digest. O18 can support a graph-only verification claim while trace verification is
unavailable. A content hash establishes integrity relative to bytes, not the truth of causal assertions.

### Block 8. Conditional relationships and limitations

Purpose: connect a record to the additional context that applies without burdening every simple system.
Needs when applicable: session/parent/child identities; retry, resume and independent-replicate relationships;
state/checkpoint/cache/seed/reset references; event transcript; scoped resource accounting; native-to-standard
interpretation and derived-view provenance; unavailable capabilities and their reasons.

This is an index of named relationships, not an untyped notes dump. Each rich capability has a defined contract.
O15 links submission to its eventual job observations; O16 links interaction steps to a session; O17 keeps
attempts separate. Resource amounts state their units and accounting scope so inclusive session totals and
per-attempt amounts cannot be inadvertently summed twice.

## 5. One connected illustrative walkthrough

An auditor asks a system for a full structure over a declared variable set. The request permits unresolved
directions and requires a final graph, with an optional confidence artifact. The system emits an intermediate
graph, later reports normal completion and emits a final partial-direction graph. The graph parser succeeds;
the optional confidence parser fails.

- Block 1 identifies the attempt, observations and interpreted objects.
- Block 2 establishes that partial directions are a permitted final result and confidence is optional.
- Block 3 identifies the native system/configuration and the graph/confidence interpreters.
- Block 4 links the data and knowledge actually supplied, with evaluator truth outside that boundary.
- Block 5 preserves normal reported/observed completion, final graph delivery, and the confidence interpretation
  error; these facts do not turn into either an unqualified all-good flag or a native-system crash.
- Block 6 lists the intermediate and final graph with distinct roles, plus native confidence evidence where present.
- Block 7 retains raw artifacts and the diagnostic with actual availability/integrity observations.
- Block 8 links events, state/resources and interpretation provenance as applicable.

Graph evaluation can proceed when its prerequisites are met, under a stated selection of the final graph.
Calibration remains unavailable until confidence can be interpreted. This demonstrates why a single run-wide
success flag would discard relevant facts.

## 6. Design acceptance obligations and next increment

The record design must encode O01-O19 without inventing observations, repairing outputs, discarding failures,
changing requested scope after the fact, or confusing missing information with native abstention/no-edge.
It must preserve disagreements between observations and uncertainty about cause, completion or provenance.
The eight blocks must answer their questions through values, references or explicit limitations; a simple
case must not need to manufacture a session transcript or fill unrelated optional contracts.

No tests are created or executed for this document. These cases will become conformance/acceptance examples
only after the design is agreed and implementation is authorized. The existing RunRecord, protocol statuses,
certificates, stored outputs, paper pointers and shared scorer behavior remain unchanged.

The next detailed design step is to settle the operation/request boundary and minimum requirements for Blocks
1 and 2, since every later outcome depends on which operation and scope the record describes. Other blocks
can then be specified incrementally using the same cases. Writing this document does not freeze exact schemas.
