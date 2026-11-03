# W2 system connections: Block 5, outcome observations and later updates (1 Nov 2026)

Tickets: DLV-08, DLV-09; neighbours DLV-10, ADV-01, DLV-06.
Status: design discussion only. No runtime, schema, protocol, finding or stored-result change is made.
Predecessor: `system-connections-system-information-design-2026-11-01.md`; outcome definitions:
`system-connections-outcome-cases-2026-11-01.md`.

## 1. Direction accepted by Uzair

Uzair accepted the Blocks 3 and 4 boundaries: distinguish the native system/configuration and execution
evidence from observation/interpretation machinery; distinguish intended/permitted/presented information,
observed access and claims/inferences about use. Intended bindings and observed bindings remain separate.
The checkpoint-restart identity decision and qualified outcome definitions remain accepted directions.

This document develops Block 5. Exact fields, enums, source-resolution policies and implementation remain
proposals. No implementation go was given. W2-5 through W2-9 remain pending; shared protocol/contract changes
still go through W5.

## 2. Representation: observations, gaps/diagnostics and assessments

Block 5 should preserve the evidence behind an outcome while providing a usable current interpretation.
Three roles keep those responsibilities explicit:

1. **Source observations:** scoped statements about what an actor reported or what an observer encountered.
   For example, a service reported completion, an observer recorded a process exit, or retrieval of a named
   artifact returned not-found at a particular location/time. A report of completion is not identical to an
   independently established conclusion that the task was fulfilled.
2. **Gaps and diagnostics:** explicit limits or detected inconsistencies in our evidence/interpretation,
   such as a missing historical log, unresolved attempt association or parser failure. They do not pretend
   that the native system itself reported those unknowns.
3. **Outcome assessments:** derived, versioned summaries for the relevant facets, based on identified
   observations, request contracts and reconciliation rules. They may include unknown or unresolved conflict.

Raw logs/artifacts belong in Block 7 and event/session history can be linked through Block 8. Block 5 retains
material outcome observations and references, not a requirement to copy every log line into a new event system.
A simple synchronous operation can have a small observation list and assessment.

An assessment is not the protocol's scientific finding/verdict. Execution completion, response delivery,
fulfillment, capture and interpretation remain distinct facets. Evaluation readiness and causal quality are
maintained downstream, with explicit input/assessment references when relevant.

## 3. What an observation must express

Illustrative components below are semantic requirements, not frozen JSON keys:

| Component | Question answered |
|---|---|
| Identity and subject | Which observation, request, attempt, operation, object or artifact does this concern? |
| Proposition and value | Exactly what was reported/observed? A typed proposition avoids conflating process termination, native completion and delivery. |
| Scope | Which task boundary, stage, object, location, time interval, participant or observation interface does the statement cover? |
| Source and basis | Who said/saw it, through which observer/parser version, and is this a native report, observed event, reconstruction or inference? |
| Evidence references | Which immutable artifact snapshot, source locator or event supports the statement, and what is its availability? |
| Time/order | When did the underlying event reportedly occur, and when was the evidence captured/imported/interpreted? Unknown times and limited precision remain explicit. |
| Relationships | Does it add evidence, describe a transition, dispute, correct, retract, clarify or resolve an earlier statement? What is the scope and evidence for that relationship? |

Request/attempt/object identity and producer references reuse earlier blocks. Unknown original identity must
remain representable; do not invent a known attempt merely to complete a field. Predicate/type versions define
meaning, rather than arbitrary adapter strings being treated as interchangeable status facts.

Example observation: 'The provider reported normal completion for this native job in this response.'
That statement is narrower than 'the requested graph was delivered, parsed and fulfilled the request.'
Another observation can establish that a final graph was captured, and another can establish its interpreted
coverage. The assessment combines only the conclusions the request contract and evidence justify.

## 4. Conflicting evidence: establish that the propositions actually disagree

Before calling evidence contradictory, compare subject identity, proposition, operation boundary, time/order,
object identity and source semantics. Some apparent conflicts are normal transitions or complementary facts.

| Pair of observations | Interpretation |
|---|---|
| Native service reports completion; collector cannot retrieve the required artifact. | Can coexist. Completion is reported; delivery/capture/fulfillment are not thereby established. A not-found response is scoped to the retrieval location/time. |
| Job observed running, then later observed finished. | A state transition when event order and identity support it, not a contradiction. |
| Final graph was emitted, then the process errored before the requested operation completed. | Delivered output and failed termination can coexist; response role and operation scope matter. |
| Child submission operation completed; parent discovery job is pending. | Different operation boundaries, not inconsistent outcomes. |
| Two sources give incompatible exit codes for the same established final process-exit event. | A genuine conflict candidate; preserve both observations and unresolved exit assessment unless further evidence resolves it. |
| A parser first maps a native terminal message to success, then corrected parser logic maps it differently. | A correction to interpretation if justified; retain native evidence and the original interpretation record. |
| A file path yielded different bytes on two retrievals. | Could be a changed path target or different version. Do not assume one immutable content object changed or that either earlier observation was false. |

Reconciliation should not use automatic majority vote, blanket latest-wins or native-provider-always-wins.
Several logs may copy the same source; duplication is not independent confirmation. A source can be authoritative
about one narrow fact without establishing another: a collector can establish bytes it saw, while a provider
may only report an inaccessible internal state. A human judgment also needs a source, rationale and scope.

A genuine unresolved conflict can produce an unknown assessment with a structured conflict reason and
references to both sides. It is not a new native behavior or an automatic crash/inconclusive scientific finding.
Where a defensible procedure can prefer evidence for a particular proposition, record the versioned rule,
selected evidence, excluded/disputed evidence and rationale. Never silently discard the disagreeing source.

Do not force a global outcome from one disputed facet. A well-identified graph may still be evaluated when
its prerequisites hold even if completion or cost is unresolved. Conversely, a graph's presence does not make
every execution/capture claim established. Analysis policies must explicitly handle contested prerequisites;
the connection must not choose the most favorable denominator by silently dropping disputed attempts.

## 5. Unknowns need reasons, not invented values

Unknown describes the auditor's knowledge about a proposition. It is distinct from a native system's own
abstention, the explicit absence of an edge, an empty graph, a measured zero, false, or scientific inconclusiveness.

Useful gap reasons include:

- The relevant event was not observed within the available observation interface.
- The required evidence was not recorded, where an omission is actually established.
- Evidence is known/reported but currently inaccessible or unavailable to this observer.
- The operation has not yet reached an evidenced terminal boundary, or current state is unknown after contact loss.
- The artifact format is not interpreted, or interpretation failed.
- Original request/attempt/object identity cannot be resolved.
- Relevant observations conflict or the cause cannot be determined.

These are conceptual availability/knowledge reasons, not additions to the protocol verdict set. Some can
coexist. Avoid claiming 'not recorded' when we only know 'not found here'. An unknown reason can itself be
unknown. A not-applicable field is appropriate only when the relevant concept truly does not apply to the
declared operation; it is not a shortcut for missing implementation or evidence.

Unknowns should be localized: a graph's variable mapping may be known while the original model snapshot is
unknown. No fake defaults are introduced to make a complete-looking record, and no demand for irrelevant
metadata should prevent recording the parts that are supported.

## 6. Later evidence and immutable history

Persisted observations and assessments are evidence snapshots. Later information adds new records/relations.
It can change the best current assessment without overwriting what was observed or concluded earlier.
Not every update corrects a mistake: genuinely new events, delayed evidence and parser corrections have
different meanings.

| Update kind | What changes | What stays preserved |
|---|---|---|
| New observation | Evidence grows. | Earlier evidence and the assessment available at that time. |
| Native state transition | The operation evolves, if identity/order establish it. | The earlier state at its observed scope/time. |
| Delayed artifact availability | More evidence can now be retrieved/interpreted. | Earlier unavailability observation; no invented original delivery time. |
| Parser/interpretation correction | A prior derived statement is corrected under identified logic/evidence. | Original bytes, old interpretation, correction producer/reason and new interpretation. |
| Native source correction/retraction | The source amends or withdraws its own claim, where provenance establishes that. | That the old claim was issued; a retraction does not prove the replacement claim by itself. |
| Clarified scope or identity | Some apparent conflicts become distinct events/objects or are properly associated. | Earlier associations and their uncertainty; the evidence for the clarification. |
| New reconciliation rule | A new assessment interprets identified evidence under a new rule. | Earlier rule/version and its conclusions; no silent change to past analyses. |

The mere existence of a newer observation does not supersede an older one. Correction/retraction/clarification
relationships must identify what assertion they affect and their evidential authority. One observer does not
erase another source's report by publishing a later record. If a supposed correction is disputed, preserve
that dispute as well.

Store event/source time separately from capture/import/interpretation time. A log imported today may describe
an old event. Where clocks disagree or original times are unknown, retain sequence/parent references and time
limitations instead of manufacturing an exact timeline.

## 7. How to keep the current outcome useful

An outcome assessment should identify:

- Its request/attempt/operation and relevant output subjects.
- The facet conclusions it can establish and explicit unknown/conflict reasons where it cannot.
- The observations/artifacts/gaps considered, including relevant conflicting inputs and dependency links.
- The request/response completion contract and reconciliation/interpretation rule versions used.
- Its producer, creation time, included evidence set and any earlier assessment it revises.
- Whether it reconstructs a historical event using later evidence or represents knowledge available at an
  earlier cutoff. Those two views are different.

Evidence IDs or a manifest establish the input set more precisely than an observation cutoff timestamp alone.
A convenient current-summary pointer can reference the latest selected assessment under a declared policy;
that pointer is not the original source of truth and can expose unresolved branches or conflicts. The actual
assessment remains versioned and reproducible from its identified inputs and rules where evidence is available.
Do not build a generic reasoning engine for all conceivable propositions: use scoped, typed rules for the
outcome facets, and preserve unsupported cases as explicit limitations.

Publication/evaluation should cite a particular assessment and evidence selection rather than an unpinned
current pointer. Later evidence can motivate a new evaluation/report version without silently changing the
old one. A failed attempt is not overwritten by a successful retry, and an interrupted attempt is not turned
into a completed attempt by its checkpoint successor. The accepted new-attempt/continuation rule applies.

## 8. Connected walkthrough with later evidence

This is a hypothetical scenario, not an experimental result. Labels E and V below are illustrative identities.

1. E-a: a service reports that a discovery attempt completed.
2. E-b: the collector cannot retrieve the required final artifact at the checked location.
3. V-a: assessment records reported completion, unavailable artifact at the observation boundary, and
   unverified delivery/fulfillment. Native completion is not independently upgraded from the report alone.
4. E-c: later, a final artifact is obtained with evidence associating it to the same attempt. It is interpretable
   as the requested output kind, and its coverage is checked against the request.
5. V-b: a new assessment can establish the newly supported artifact/response facts and fulfillment if the
   contract's evidence requirements are met. Other unresolved facets remain unresolved. E-b stays true for its
   earlier retrieval scope; the artifact's original creation/delivery time is not invented.
6. E-d: a later interpreter correction establishes that a previously assumed full-scope output actually covered
   only a local query. The correction links to the native evidence and earlier interpretation.
7. V-c: a new assessment revises fulfillment for the original full-scope request while preserving the service's
   completion report and the artifact. V-b remains the earlier published interpretation, now explicitly corrected.

No native execution happened again in steps 4-7 merely because evidence or interpretation improved.
If a new attempt actually runs, it receives its own identity and observations rather than being folded into
this history. This walkthrough illustrates the separation of native events, our knowledge and our conclusions.

## 9. Edge-case checks for the design

The following cases are hypothetical acceptance examples, not tests written or executed.

| Case | Evidence situation | Required behavior |
|---|---|---|
| B01 | Reported completion plus unavailable artifact | Separate propositions; no automatic success or crash. |
| B02 | Running then finished with established order | Preserve state transition rather than flag contradiction. |
| B03 | Same exit event has incompatible reported exit codes | Preserve true conflict and evidence; no arbitrary winner. |
| B04 | Native graph was emitted before a later error | Retain delivered object and failed termination at their proper scopes. |
| B05 | Only final graph survives a historical run | Record known graph interpretation and unknown native termination/version evidence. |
| B06 | Client loses contact with a remote job | Preserve last observed state and current uncertainty; no invented remote stop. |
| B07 | Artifact appears after an earlier not-found response | New availability observation; no erasure of earlier retrieval result or fabricated original delivery time. |
| B08 | Parser bug is corrected | New interpretation and assessment; native bytes and earlier derived error remain traceable. |
| B09 | Provider retracts an earlier status claim | Retain issued claim and sourced retraction; replacement claims require their own evidence. |
| B10 | Identical copied logs appear several times | No false independent corroboration or majority-vote resolution. |
| B11 | Retry or checkpoint successor completes | New attempt's evidence cannot overwrite predecessor failure/interruption. |
| B12 | Optional confidence extraction fails, graph interpretation succeeds | Localize the gap; compatible graph evaluation may remain possible. |
| B13 | A missing field is mistaken for native abstention or zero | Keep absence/unknown reasons; do not invent a native decision or measurement. |
| B14 | New evidence disambiguates two apparent native-run identities | Add identity-resolution evidence and rederive affected assessments; preserve old association history. |
| B15 | Same artifact path yields different contents later | Identify observed content versions and scope; do not silently replace bytes underlying an earlier conclusion. |
| B16 | New reconciliation rules yield a different summary | New versioned assessment; published/pinned earlier reports do not mutate. |

## 10. Costs, boundaries and current implementation

The current `audit/core/runs.py` supplies one status plus failure/notes metadata, and the current certificate
compares reproduced numeric/verdict results. This design does not replace those interfaces, reinterpret their
historical statuses or change stored certificate verification behavior. Block 5 outcome assessments are distinct
from scientific findings. Any later shared-contract migration must be proposed to W5 with compatibility checks.

The recommendation costs more references and explicit evidence handling than a mutable single status. Its
benefit is that conflict, missing evidence and later corrections remain understandable. The strongest simpler
alternative is one status plus a diagnostic note; that is adequate only for narrow cases and makes reproducible
reconciliation depend on prose. To keep the richer design practical, share typed observation/reconciliation
mechanisms in the core, allow small records for simple cases, and reference raw logs rather than duplicating them.

Adapters expose available native facts and locators; they should not independently decide all cross-source
conflicts, assign invented certainty scores, or rewrite history. Core rules can summarize recognized facets,
while unsupported interpretations remain explicit. Capture completeness, trust assumptions and evidence scope
must remain inspectable even when a UI presents a concise outcome.

No implementation or tests were created or run. Only this new design record was written. Existing code,
protocol, results, certificates, paper/tracker/site files and the green gate are unchanged. The next discussion
can settle observations/gaps/assessments as Block 5's boundary before developing Block 6's output-object index.
