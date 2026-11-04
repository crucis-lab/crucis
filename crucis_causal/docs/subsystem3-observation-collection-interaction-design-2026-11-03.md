# S3 observation, collection and interaction

Tickets: DLV-08, DLV-09; related DLV-10.
Date: 2026-11-03, America/Los_Angeles.
Status: OC01-OC12 are recommendations pending discussion. No S3 implementation,
exact schema/API freeze, production policy change, native scientific execution,
paid campaign, protected-store access or actual response delivery.

## 1. Continuation and scope

The user affirmed [dispatch and attachment](subsystem3-dispatch-attachment-design-2026-11-03.md),
committed as f9e32c3940de734a5b0ecb468813986088afea40, and requested observation,
collection and interaction: resumed cursors, duplicate/out-of-order events, gaps,
partial outputs and authorized responses. DA01-DA12 are direction-affirmed with
exact details open; this does not freeze every proposal or authorize implementation.
OC01-OC12 below remain recommendations. Preserve earlier dated status as history.

Retain [knowledge/cutoff and closure rules](subsystem3-minimum-account-knowledge-design-2026-11-03.md),
[admission and concurrent effects](subsystem3-admission-lifecycle-design-2026-11-03.md),
and [capture/staging boundaries](subsystem3-input-realization-staging-design-2026-11-03.md).
S1 supplies scoped ports/representations; S2 supplies scientific intent, selection,
information and recovery rules. S3 coordinates their admitted operational realization;
it does not invent a metric, answer policy, reference feedback or analysis population.
All examples are hypothetical. The [methodology index](subsystem3-methodology-index-2026-11-03.json)
links proposals to narrower existing source, fixtures and scoped tests.

## 2. A cursor belongs to a source contract (OC01)

Recommend binding an observation position to the established native episode,
source/producer, stream/partition and relevant generation, filter/subscription scope,
cursor/protocol version and direction/boundary semantics. Positions can be opaque;
only the source contract can establish comparison, inclusive/exclusive meaning,
expiry, retention and completeness. A string named position is not universally
an integer offset or a complete-history certificate.

Separate native source position from local observation occurrence/order and the
collection period. Reattaching to N1 need not create a new native stream or attempt.
Changing filter, source generation or subscription can invalidate cursor continuity.
Record the new scope and its relationship; do not silently apply the old cursor
to a replacement source. Use per-stream positions/coverage when needed, rather
than max(offset) across unrelated producers. Polling snapshots do not acquire a
native event history merely because each poll has a local timestamp.

## 3. Preserve capture before advancing recoverable progress (OC02)

Distinguish fetched/returned position, durable capture position, interpretation/
decision readiness and source acknowledgement. A backend may combine some boundaries
under a real guarantee; do not assume they form one end-to-end transaction.

### Example A: batch 101-104 arrives, coordinator crashes

The established source contract resumes strictly after its numeric position. E1
has durable capture through 100. It returns events 101-104 and next position 104.
Persist the permitted captured evidence, source scope/extent and progress association
under the journal's actual guarantees before treating 104 as recoverable capture.

If interruption occurs before that commit, recovery resumes from established 100
within the source's supported replay contract. Repeated deliveries are expected;
they do not create new native events. If bytes were captured but interpretation
failed, retain them and the parser gap; interpretation need not block durable raw
capture progress forever. Its own readiness/coverage remains incomplete.

If a source requires acknowledgement to discard messages, acknowledge only under
the applicable capture/retention policy and supported semantics. A lost acknowledgement
can cause redelivery or uncertain source retention. It does not invalidate the
earlier durable capture. Destructive reads or nonreplayable sources can lose evidence
between source consumption and local persistence; represent that actual limit.

Required evidence may be a permitted scoped representation rather than unrestricted
raw retention. An explicitly allowed lossy capture can advance with declared gaps;
it cannot claim lossless/full-content capture. Never mark progress complete merely
because a remote cursor advanced, especially if the captured evidence is unavailable.
No exact journal/acknowledgement algorithm or new wire cursor fields are frozen here.

## 4. Duplicate captures versus native occurrences (OC03)

### Example B: event E101 arrives through a callback and a replayed page

Capture both observations with their actual source/transport/cutoff context. Adequate
native identity evidence can associate them to one underlying native event. Do not
charge/count a second native action or create another scientific repetition merely
because it was observed twice. Actual transport/resource costs can still differ.

Equal text or bytes is insufficient: two native events can legitimately carry the
same content. Conversely, the same immutable native event identity with incompatible
content is conflicting evidence until scoped/versioned semantics or a correction
resolves it. Preserve distinct immutable captures; do not overwrite one S1 record
ID with changed content. Transport envelope changes need interpretation under the
named contract rather than automatic payload conflict or content-based deduplication.

S1's local producer/stream sequence uniqueness and record identity invariants remain
binding. Repeated observer captures should not fabricate duplicate local sequence
slots for the same event. Exact canonical-event/capture association representation
remains open; use adequate scoped identity evidence rather than guessed event IDs.
An event identity can remain disputed while its captured bytes remain verified.

## 5. Partial order, delayed evidence and gaps (OC04-OC05)

### Example C: completion arrives before an older running report

N1's source establishes running at native sequence 17 and completed at 18. Capture
18 first, then 17. Retain the native ordering and both capture times/cutoffs; the
late older report adds history without rolling current native state back. An
unknown order cannot be replaced with assumed wall-clock or arrival ordering.
Across independent streams retain established predecessors/causal relationships
and unresolved order. A total sort by timestamp is not a causal history.

Same-subject/same-boundary incompatible claims remain disputed under EA rules.
The existing outcome_observations helper groups supplied facets but does not
implement this temporal adjudication; do not run it over mixed-time evidence and
claim this proposed interpretation is already supplied.

For an unfiltered source whose contract establishes contiguous event positions,
capturing 101 and 104 can establish a gap at 102-103. A filtered/sparse stream may
legitimately jump; numeric difference alone does not establish missing events.
Record why a gap is known or why coverage is merely unknown: disconnect, retention
expiry, bounded truncation, inaccessible source, failed decoding or uncertain scope.
An empty page, no callback or expired cursor does not prove that no event occurred.

If 102 arrives later, revise current coverage for that part; 103 can remain missing.
Keep the earlier cutoff view with its original gap. Source watermarks/finality
claims support only the coverage their actual contract establishes. Time passing
does not by itself certify a complete history. A new known terminal status can
coexist with missing intermediate events and unresolved artifact/cost questions.

## 6. Bounded observation and actual observer effects (OC06)

Admit polling/subscription/reads under their actual authority, resource and information
effects. Define applicable batch/event/byte/time/storage bounds, backpressure and
capture policy. A rejected over-limit batch can follow actual reads or partial sink
writes; preserve available evidence and gaps rather than infer no effects.

Backpressure, blocking a callback, altered polling or stopping consumption can change
native timing/behavior. Preserve the declared treatment and actual deviations; do
not assume instrumentation is scientifically neutral or silently change timeouts
to obtain a favorable result. Required bounds need actual enforcement mechanisms.

S1 currently checks returned record count and serialized record bytes for nonrejected
batches. BatchLimit also carries deadline, but those wrappers do not enforce a
general driver runtime/deadline, source identity, cursor validity, durable capture
or total sink/storage resource bound. Those remain S3/driver design obligations.

An empty or exhausted ObservationBatch establishes only the supplied scope/contract.
It is not universal native completion or a final closure of every stream. A source
with no new records now can produce more later. Native termination, observer stopping
and resource/exposure settlement keep their independently evidenced meanings.

## 7. Capture extent, output identity and interpretation (OC07-OC08)

### Example D: incomplete bytes and a complete intermediate answer

A native output stream ends with an incomplete JSON prefix. Capture the actual
bytes/fragments, framing/source identity, extent and gaps. A valid snapshot digest
proves those captured bytes, not that a complete graph exists. Do not add guessed
closing syntax, fill absent edges with zeros or manufacture an empty answer.

Separately, N1 may have produced a complete intermediate graph G1 before a later
stage failed. Keep G1's actual stage/role/domain/coverage alongside failure evidence.
S2's fixed selection policy determines whether it is an eligible answer; do not
promote it silently to final output or select whichever stage scores best. A local
answer can be fully captured while covering only part of the requested domain;
unreported relationships are not established absences.

Snapshots at a reused mutable path get their own captured identities. A source
declaring an artifact does not prove its current availability, and a hash of bytes
read during a concurrent write does not establish a coherent native-produced file.
Use actual snapshot/version/framing guarantees appropriate to the source. Assemble
chunks only with adequate identity/order/extent evidence under a declared procedure;
never join unrelated generations to make a plausible output.

Parsing and semantic checks are versioned derived operations over retained evidence.
Unsupported decoding or an observer bug is a scoped observer/interpretation gap.
If adequate native-format evidence establishes malformed output, record that exact
conformance failure without broadening it into unsupported algorithmic failure.
A later decoder can add a new interpretation without rerunning the native system
or overwriting earlier bytes/assessments. Retention and audiences stay within IS rules.

## 8. Correlate actions and freeze the decision basis (OC09)

### Example E: a native session requests an answer

Observe native action Q1 with its session/attempt, requester, endpoint/operation,
arguments/question and actual native action identity/provenance. S1/S2 can represent
nontextual requests as well as questions. Validate the supported action contract and
applicable information policy; a native request is not itself authority to execute it.

Assemble only the information permitted for this decision under the declared S2
rule and actual evidence cutoff. Establish required interpretation/ordering/coverage
before a decision that depends on it. A later event cannot enter an earlier decision
view through retrospective reconstruction. Native effect/response time and observer
arrival time remain different; S2's actual timing rule governs analysis inclusion.

Record the selected response/action, procedure/version, actual input basis and
remaining gaps before permitting its delivery. Selection is not delivery. Existing
S2 record_decision checks a particular supplied threshold-action contract; it is
not a generic decision engine for every callback. Required new decision procedures
remain explicit supplied/registered capabilities, not arbitrary invented defaults.
Any generation/oracle/service call that itself has effects needs separate admission
and actual evidence; no hidden paid model or evaluator-reference fallback is implied.

If prerequisite evidence is missing, hold the dependent action or use only an
explicitly permitted fallback under the fixed plan. Abstention can be a meaningful
selected response with its own delivery and resource/exposure effects. Transport
failure, silence and native timeout do not automatically establish abstention.

## 9. Deliver under current authority and native action validity (OC10-OC11)

Bind delivery to the exact Q1, session/attempt, response content, recipient/endpoint,
applicable owner authority, resource/exposure reservation, command and supported
validity/idempotency rules. Execution permission is not delivery permission. A
selected answer does not grant itself transmission rights. A closed/superseded
question or expired response window requires its actual native semantics; a local
flag alone cannot enforce remote validity or establish native expiry.

Observed unauthorized/nonconforming delivery remains evidence with its intended
condition and actual deviation. A preventive check cannot erase an effect already
observed through another actor or an earlier uncertain transmission.

### Example F: Q1 repeats, then its delivery acknowledgement is lost

Polling and a callback both report established action Q1. A coordinated durable
decision claim can prevent redundant selection locally, subject to actual ownership.
Two native actions Q1 and Q2 with identical text remain distinct. If native action
identity/correlation is insufficient, retain that uncertainty rather than deduplicate
by text. Any stronger single-response guarantee needs the actual receiver protocol.

After choosing V1 for Q1, one admitted delivery command sends it and loses its
acknowledgement. Preserve selection, each transmission, receipt uncertainty and
possible exposure. Do not reselect using newly available information or resend
with a fresh key simply because the old reply is unknown. Reconciliation or valid
receiver idempotency can justify supported continuation with current authority.
An extra one-use in-memory grant cannot deduplicate effects across coordinators.

If another coordinator takes over, receiver fencing/validity and the established
pending command govern new effects. A journal claim or locally unique decision
record does not prove one native delivery. A native transport acknowledgement,
receipt of answer, access/use and policy settlement remain different questions.
Acknowledging receipt of the incoming callback is also distinct from answering Q1.

## 10. Collection closure and handoff (OC12)

A period may close at its declared bound with a capture cutoff, source positions,
coverage/interpretation gaps, pending actions/transmissions, partial objects and
resource/exposure/control obligations. Do not silently answer pending questions
to make shutdown convenient. Any timeout response, cancellation or other recovery
effect needs the declared policy and its own admission.

Late evidence appends current assessments. Active follow-up opens its explicit
collection boundary under EA rules, retaining the native attempt when applicable.
Preserve the original knowledge view and S2 selection/missingness/analysis population.
A well-formed partial collection is not proof of a complete scientific response,
and missing observations are not zero scores or evidence of absent native output.

Minimum logical receipt links: native source/episode and collection scope; request/
cursor protocol/filter and established coverage; fetched versus durable/acknowledged
positions; captured observations/artifacts with extent and time/order basis; native
event associations/conflicts; interpretation versions/gaps; decision input cutoff,
selected response and actual delivery history; owner authority and pending obligations.
These are conditional meanings using shared references, not twelve new mandatory
wire blocks or one total-order event log for every system.

The core should coordinate common capture/knowledge/identity/decision-history rules.
Drivers supply truthful polling, streaming, callback, artifact or multi-party source
mechanisms. S2 supplies scientific policy; authorized decision providers supply their
actual procedures; later measurement/finding subsystems retain their scope. A
representable cursor or response does not establish durable replay or enforcement.

## 11. Choices, alternatives and remaining contracts

| ID | Proposed direction | Strongest alternative | Cost / failure prevented | Reuse / still open |
|---|---|---|---|---|
| OC01 | Cursor bound to exact source/protocol/scope | One global numeric last-seen position | More source contracts; prevents cross-generation/filter skips and false ordering | S1 Cursor/native identities; cursor semantics/profiles open |
| OC02 | Separate fetch, durable capture, interpretation and source ack | Advance on fetch, or require perfect interpretation before any progress | Persistence/replay work; prevents crash loss and malformed-event loops | S1 snapshots/AL durable history; capture/ack transaction protocol unbuilt |
| OC03 | Preserve captures and associate evidenced native occurrences | Deduplicate by content or count every arrival | Identity/association records; prevents merged real actions and duplicate effects/counts | S1 events/identity invariants; canonical-event association open |
| OC04 | Native partial order and versioned knowledge cutoffs | Last-arrival/timestamp wins | More temporal reasoning; prevents rollback, false disputes and hindsight | S1 history/EA assessments; temporal interpreter unbuilt |
| OC05 | Scoped gap/coverage evidence and later repair | Empty batch/offset jump/timeout implies absence or completeness | Reconciliation/withheld claims; prevents fabricated negatives and hidden omissions | S1 gap/index and S2 timing; continuity/watermark contracts open |
| OC06 | Actual bounded observation/backpressure with scoped exhaustion | Treat batch limits as total runtime control and exhausted as final | Instrumentation/support costs; prevents overstated enforcement and native completion | S1 batch count/byte checks; runtime/sink/time guarantees open |
| OC07 | Captured extent and explicit partial/intermediate object roles | Repair partial bytes or promote surviving output to final | More provenance; prevents fake graphs, absent-edge claims and selected-success bias | S1 artifact/output index and S2 selection; incremental capture protocol open |
| OC08 | Versioned decoding over retained evidence, observer/native attribution separate | Parse failure means native failure or rerun native to repair | Retention/decoder versions; prevents lost evidence and fabricated native errors | S1 decoder/snapshots; durable interpretation progress open |
| OC09 | Exact action correlation and fixed permitted decision basis | Recompute convenient answers using newest/all evaluator information | More policy/provider bindings; prevents hindsight and feedback leakage | S2 decision/exposure records; generic provider contracts unbuilt |
| OC10 | Current exact delivery authority, action validity and separate abstention | Execution grant or selected content authorizes sending | Extra checks/reservations; prevents wrong-recipient, stale or unauthorized effects | S1 DeliveryGrant/ActionChannel; durable delivery protocol open |
| OC11 | Coordinated decision ownership plus actual receiver guarantees | Local one-use token/text dedup means exactly one native reply | Backend support/uncertainty; prevents concurrent/resumed duplicate exposure | AL fencing/idempotency and S1 transmissions; receiver integration unbuilt |
| OC12 | Bounded closure with gaps/pending obligations and faithful S2 handoff | Wait forever or mark collection end as complete success | Follow-up accounting; prevents invented completion, dropped units and allowance reset | EA closure/S2 handoff; full S3 support/interface reconciliation open |

## 12. Prospective validation and actual evidence boundary

Future acceptance cases must interrupt before/after capture-progress commit and
source ack; replay the same events; expire opaque cursors; change filters/generations;
include nonreplayable reads, snapshot-only polling and multiple independent streams.
Test same native event across transports, equal content with different events,
conflicting immutable-event content and duplicate local sequence invariants.

Include native order versus arrival order, sparse versus contiguous offsets, partial
gap repair, late evidence after closure, malformed/oversized batches and actual
backpressure effects. Capture incomplete bytes, coherent intermediate outputs,
changing files, missing artifacts and later decoder corrections without native rerun.
Check missing action identity, repeated Q1 versus new same-text Q2, incomplete
decision basis, forbidden evaluator feedback, unsupported decision procedure,
authorized abstention versus silence, expired action, concurrent response attempts,
lost delivery acknowledgement and callback receipt versus answer acknowledgement.

These are planned obligations, not newly executed S3 tests. Existing S1 tests check
bounded returned batches, immutable evidence, scoped event ordering, exact response
authority and particular replay occurrences. S2 tests check supplied decision and
exposure evidence, including no delivery inferred from selection and evaluator
feedback limits. Neither provides the proposed durable cursor, complete temporal
interpreter, generic policy engine or distributed exactly-once response guarantee.
The offline fixture remains a deterministic local protocol, not native scientific
or remote-provider evidence. No source/test hash is rebaselined.

Mandatory staged-tree gates check offline package/public-source compatibility only.
No historical numerical campaign/certificate, scoring, paper contract or production
resource/exposure policy changes in this milestone.

## Where we're going

Review capture/acknowledgement progress, event identity/order/gaps and the action/
decision/delivery examples together. Then consolidate recovery, stopping and actual
resource/exposure accounting across these boundaries, followed by immutable evidence
publication/reconciliation. Resolve outstanding cursor/association/handle/decision
contracts during full S3 review before exact interfaces, profiles or build bundles;
implementation still requires explicit authorization.
