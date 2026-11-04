# S3 execution identity and durable lifecycle

Tickets: DLV-08, DLV-09; related DLV-10.
Date: 2026-11-03, America/Los_Angeles.
Status: design discussion candidate. All new recommendations P01-P10 remain
proposals pending discussion. No S3 implementation, record/schema freeze, native
execution, paid campaign or protected-store access is authorized by this note.

## 1. Continuation and source precedence

The active framework repository is Crucis and its current Python namespace is
`crucis_causal`. The verified starting checkout for this milestone was clean main
at `05b9faefcbfbc108694e356db34903afcb646efa`, equal to the local origin/main ref.
This note continues the seven proposed responsibilities in
[the S3 opening](subsystem3-structure-design-2026-11-03.md). It does not repeat the
extraction or restart earlier subsystem plans.

Current root AGENTS.md, README.md and provenance/publication.json govern present
operations. Historical documents retain their original paths, source hashes,
acceptance records and dated pending states. S1 and S2 remain implemented within
their accepted scopes. The former research-layout exporter-pin warning is history,
not a newly diagnosed Crucis blocker. Technical documentation here is public;
private operational records belong outside this repository.

Existing constraints carried forward from the user's instructions and accepted
S1/S2 discussions:

- Preserve native meaning, unknowns and evidence; expand the generic core while
  keeping native mechanics in explicit drivers.
- Keep scientific eligibility, operational readiness, permission, requested effect
  and observed effect distinct.
- An observer reconnect to an established ongoing native episode does not create
  a new attempt. Checkpoint restart creates a new attempt and explicit continuation.
- Attempts, output particles and transport deliveries do not establish independent
  scientific repetitions. Stopping observation does not establish native stop.
- Preserve fixed S2 intent, information boundaries and the distinction between
  selected actions and delivered actions. Metadata does not establish isolation.
- S3 implementation and empirical execution await their own explicit authorization.

The seven opening responsibilities remain proposed boundaries. This note's new
execution-account, command and journal recommendations are not attributed to the
user as accepted choices. Companion source/status map:
[S3 methodology index](subsystem3-methodology-index-2026-11-03.json).

## 2. Start with the lost launch acknowledgement

The following is a hypothetical design example, not a native run:

1. S2 supplies fixed run binding B1. S1 has prospective request R1 and attempt A1.
2. S3 durably records command C1: submit this exact request to the selected native
   recipient, using the specified presentation and configuration bindings.
3. An authorized driver crosses the submission boundary. The provider might accept
   the job, but the acknowledgement does not reach durable local storage.
4. The coordinator process ends. A new coordinator later reads the same history.

The recovered journal establishes that submission was intended. It may also contain
evidence that the driver entered a call or forwarded bytes, depending on what was
captured. None of these observations alone establishes native acceptance, absence
of execution, termination, or final charges.

**Recommended recovery:** preserve C1/A1 and their unresolved effects. Use only an
authorized, supported reconciliation mechanism. Do not silently submit C2 as if
C1 had no effect. If reconciliation is unavailable, retain the uncertainty and
apply an explicitly declared recovery policy. An additional risk-bearing execution
can only be an explicit, authorized choice accounting for the unresolved earlier
effect; it cannot erase it or claim an extra independent scientific repetition.

| Available evidence | Claim it can support | Limit or next requirement |
|---|---|---|
| Durable local command intent only | The coordinator intended the specified effect | Zero, one or unintended duplicate native effects may remain possible |
| Driver evidence that a request was forwarded | That scoped forwarding event occurred | Does not establish provider acceptance or number of jobs |
| Authentic native receipt linked to the exact command/request and native namespace | The native service acknowledged the stated operation/job | Accepted/queued is not started/completed; receipt scope and contents govern |
| Supported lookup returns a matching native episode with sufficient binding evidence | Association to that episode and its reported status at the observed point | Do not associate by output similarity, filename or timestamp alone |
| Authoritative negative lookup with established coverage/consistency and no still-active sender | The specified submission is absent within the evidenced scope | An empty eventually-consistent listing, expired retention or a racing sender is insufficient |
| Verified native idempotency semantics with the original key, exact compatible content, applicable namespace and valid retention | Retransmission may safely seek the same effect/receipt within that guarantee | A key-shaped string, local request hash or expired guarantee establishes no native deduplication |
| Logs contradict each other or expose two native jobs | Preserve the conflicting/duplicate episode evidence | Do not choose a convenient job or force an expected one-to-one association |
| No supported reconciliation | Native effect remains unknown | Wait, close collection with gaps, or follow an explicit authorized risk policy; no fabricated failure/zero usage |

A request digest establishes a content relation. An occurrence ID identifies our
command. A provider idempotency guarantee establishes a native behavior within
its own scope. These facts cannot substitute for one another. Even reconciliation
queries may consume resources or reveal information; they need applicable access
and authority rather than an assumption that all queries are harmless.

## 3. Proposed identity model (P01-P03)

Concepts below need distinguishable identity where applicable. They are not a
requirement to create eleven new UUIDs or new wire record kinds for every call.
Reuse S1/S2 identities when meanings match. Ordinary calls should not need
distributed-job fields; absence/unknown must be explicit where the distinction
matters. Exact cardinalities and serialization remain open.

| Concept | Meaning | Reuse or renewal rule proposed |
|---|---|---|
| Scientific trial T (S2) | An intended scientific unit under a plan | Reconnect/retry does not create a new T; a new planned repetition needs its own scientific identity |
| Run binding B (S2) | Exact relation among plan, trial, resolved inputs, condition and subject | Retain the fixed binding; changed bound meaning needs an explicit revised/new binding |
| Execution account E (proposed S3) | Operational history for a particular commissioned realization or observation task | Survives coordinator restarts and can group related attempts; a separately commissioned occurrence stays distinct even with equal content |
| Native request R (S1) | The exact requested native operation and its scope/policies | Reuse only under compatible intent; changed request meaning requires a related new R |
| Attempt A (S1) | A prospective or evidenced native execution episode in its declared history | Reconnect can retain A; a retry after an ended episode or checkpoint restart uses a new A and relation |
| Native episode N | The provider/process/session's evidenced execution identity | May be unknown; scope by issuer/namespace and relevant generation, not a bare reusable PID or job number |
| Effect command C (proposed role) | A logical request to cause a particular effect: submit, deliver, restore, cancel, etc. | Durable identity before an effect; compatible safe retransmission may retain C |
| Dispatch occurrence D | A particular attempted forwarding of C | Distinguish repeated forwarding attempts and their receipts; allocating D does not prove bytes were sent |
| Observation occurrence O | An observer's acquisition of a native claim, event, artifact or gap | New observation remains distinguishable; repeated observation is not necessarily a new native action or charge |
| Coordinator incarnation W | One running owner/worker incarnation | A new W after a crash does not automatically create new E, R, A or T |
| Publication P | An immutable evidence package snapshot | Changed package content gets a fresh publication identity; unchanged copied records retain identity/content |

E is an operational grouping, not an additional sample-size unit or native job.
The normal prospective route links it to B. Historical observation and source
materialization work may need other explicit target roles without inventing a
scientific trial or original launch. Parent/child coordination does not establish
independent trials or parent completion from child completion.

One intended A normally targets one native episode, but uncertain or defective
dispatch can produce unexpected duplicate native jobs. Retain both observations
and the association uncertainty. Existing HandleRegistry's guarded associations
must not be weakened or bypassed to force a clean history. The precise S1/S3
representation of extra unplanned episodes remains to be designed.

## 4. Durable history and knowledge (P04-P06)

Recommend a durable event/receipt history with a derived coordinator view. The
coordinator view answers what it should do next. Observations answer what is
evidenced. Persisting a new control state cannot turn an unknown effect into a
known fact. Suggested independent questions include:

- Is the scientific target eligible, and are operational prerequisites established?
- Was the effect authorized/reserved, requested, forwarded or acknowledged?
- Which native episode, progress and termination claims are evidenced?
- Which inputs were delivered, accessed or reported used, and to whom?
- Which outputs/artifact bytes were produced, captured, verified or interpreted?
- Which resources were reserved, reported consumed, incurred or still unknown?
- Did the observer stop collecting, and are further actions permitted?

These are conceptual facets, not settled field names or a frozen set of states.
Conflicting observations retain their sources and scope; a later assessment may
revise a conclusion without deleting its earlier evidence. Wall-clock order alone
does not prove causal order. Record predecessors/native stream sequence/observed
relationships where available; do not invent a total order across independent
workers, sites or clocks.

Recommended effect boundary:

1. Resolve/pin intent and applicable supplied evidence. Persist the command and
   its exact binding before permitting its dispatch. If durable intent cannot be
   established, do not knowingly initiate the effect through this coordinator.
2. Establish current admission and authority. The detailed reservation/grant
   ordering is an upcoming design topic; neither a journal entry nor a serialized
   permission record creates a runtime capability.
3. Record each dispatch attempt and the actual driver/native evidence obtainable.
   A pre-call marker proves only that marker was written.
4. Capture receipts and observations durably; publish immutable partial snapshots
   and S2 links as appropriate. Native action and evidence publication do not
   constitute one universal transaction.
5. After interruption, reconcile all pending effects before decisions that rely
   on their absence. Recover the operational view from retained evidence and
   approved recovery rules, with any unresolved liabilities still present.

| Interruption boundary | What can be concluded on recovery |
|---|---|
| Before durable command commit, with evidence that no dispatch path crossed | No effect was initiated through that evidenced path; do not generalize to other actors |
| After durable commit, before/around forwarding, without distinguishing evidence | Intent exists; whether an effect occurred may remain unknown |
| After provider acceptance, before local receipt capture | Native acceptance may be recoverable; loss of local receipt does not negate it |
| After native completion, before artifact capture | Completion and output availability can differ; original output bytes may remain unavailable |
| After artifact capture, before journal/package publication | Recover captured bytes/identity only if their durable storage is evidenced; reconstruct observer records honestly |
| After publication, before coordinator acknowledgement | Verify/reuse the exact publication rather than changing its identity/content or counting a second native result |

A journal's local transaction protects the records inside that transaction. It
does not make a Python function, provider, filesystem, experimental action and
remote accounting ledger all commit atomically. Backend-specific stronger
guarantees can be supported with evidence instead of a universal exactly-once claim.

## 5. Four worked lifecycle paths

### A. Local call

T1/B1 -> E1 -> R1/A1 -> C1 asks an explicitly supplied function driver to run.
Where there is no native-issued identity, N remains unavailable or scoped to an
evidenced local invocation. The coordinator must not invent a provider identity.

A successful captured return supplies output evidence for A1; its scientific
correctness is still a later question. A raised exception may coexist with files,
partial outputs, mutated state or incurred usage. Capture those facts separately.
If the process ends between the call and durable result capture, a local route
can have the same uncertain-effect problem as a remote route.

A declared pure, repeatable computation may permit a new authorized attempt.
Purity, controlled random state and repeatability are prerequisites, not properties
inferred from the word function. Regenerated bytes are a later occurrence; they
do not retrospectively prove which bytes the interrupted attempt produced.

Existing primitives: supplied_connection, InvocationSpec, CaptureSink, NativeHandle,
S2 request projection, S1 scoped outcomes. Missing: durable call boundary,
recoverable storage ownership and evidence-based local interruption semantics.

### B. Asynchronous remote job

E1/R1/A1/C1 submits work; a supported receipt binds native episode N1. Later polls
and callbacks create observations about N1. A worker restart W1 -> W2 can attach
to N1 without resubmission or A2, once the binding is established and authority
permits observation. A reported queued status does not establish computation start.

For the lost acknowledgement case, use the evidence matrix above. Safe native
idempotent retransmission can be another dispatch of C1, within its exact native
guarantee. That still requires current applicable authority; the old in-memory
one-use capability cannot simply be consumed again or serialized back to life.
Without safe reconciliation, keep the possible first job and its liabilities.

Attaching to pre-existing external work is a distinct supported mode. S3 records
its present observation/attachment role and any evidenced original history. It
does not fabricate an earlier Crucis submission or scientific trial for it.

Existing primitives: prepared/supplied/attached ports, scoped grants, handle/native
identity bindings, bounded observe and immutable packages. Missing: native driver
guarantees, durable attachment/reconciliation and worker-ownership protocols.

### C. Interactive session

An attempt/session can contain multiple native action requests and responses.
Separate each action request, selected response, delivery command and transmission
evidence. Two questions with identical text can still be different native actions.
Two received copies of one evidenced native action can be repeated observations.
Content equality alone decides neither case.

Suppose S2 selects answer V for action Q1. S3 records an authorized delivery command
C2, sends it, then loses contact. The answer is selected, but actual receipt/access
may be unknown. Do not automatically resend it, reset an exposure allowance or
continue as though the system never saw it. Use endpoint-specific acknowledgement,
lookup or idempotency evidence, if supported. Subsequent work must honor whatever
exposure is established or unresolved under the declared policy.

S2 supplies the permitted decision rule; S3 effects its authorized choice and
records actual interaction. Neither an evaluator-only score nor private reference
becomes permissible feedback through convenience. An observation batch ending
does not establish that the session ended or a native action was answered.

Existing primitives: action requests/responses, sessions, transmissions, ActionChannel,
DeliveryGrant, S2 decision/exposure records. Missing: durable incoming-event
correlation, delivery recovery and exposure-reservation behavior under uncertainty.

### D. Interrupted/resumed work

Use the observed native history to choose among these cases:

| Situation | Identity consequence | Required evidence/limit |
|---|---|---|
| Coordinator restarts; same native episode continues | New W, new observations; retain E/R/A/N | Establish native association and current observation authority |
| Native pauses/unpauses within the same evidenced episode | Can retain A/N | Do not infer unchanged hidden state merely from a pause label |
| Checkpoint restart launches a successor episode | New A2 and normally N2; explicit A2 -> A1 continuation | Pin actual checkpoint, requested/observed restored components and any unknown state |
| An ended episode is retried under compatible intent | New A2, explicit retry relation; R may remain compatible | Declared retry policy/current authority; prior costs and outcomes survive |
| A new task uses prior state as a warm start | Related new request and explicit warm-start history | Compatible new scientific binding; no inferred independence |
| S2 commissions another scientific repetition | Distinct scientific occurrence and operational links | Equal payloads/output bytes do not merge the repetition or establish independence |

If model parameters load but RNG, optimizer, cache or interaction history do not
have adequate evidence, preserve that partial restoration. Exact continuation
stays unestablished. If the predecessor may still be running, a successor can be
a concurrent branch or duplicate-risk action; do not silently declare the first
one stopped. Resource/exposure accounts continue over the relevant scope.

Existing primitives: S1 recovery/state_load/event/accounting checks, scoped state
objects, S2 amendment and repetition contracts. Missing: operational recovery
admission, actual restoration drivers and reconciliation after interrupted restore.

## 6. Ownership, deduplication and publication (P07-P10)

One coordinator should own permission to issue a given command at a time, through
a backend-appropriate durable claim. Exact locking/lease choices are deferred.
Expiry of a local lease does not stop an old worker or its already submitted job.
A generation/fencing token only prevents stale effects when the relevant effect
receiver actually enforces it. Protecting journal writes alone is insufficient.

Separate duplicate handling by identity and purpose:

- Re-reading an immutable snapshot can reuse that exact snapshot identity.
- Re-observing a proven native event retains observer provenance without treating
  it as another scientific trial or charge.
- Same native request text without matching event identity is not a duplicate proof.
- Duplicate forwarding has its own uncertainty; native deduplication requires its
  actual scoped guarantee.
- An unexpected second native episode remains evidence even if the intended model
  expected one. Do not discard it to make the history satisfy a desired shape.

Immutable S1 observations and S2 links remain publication boundaries. Changed
package sets use fresh publication IDs; copied records keep exact contents. A
new observer can import recovered evidence with its own creation time and source,
without claiming to have witnessed an earlier event. Closing the collection with
gaps is distinct from native termination and discharging resource liabilities.
Unstarted or unobserved planned units remain visible to S2 population accounting.

## 7. Important choices: recommendation, alternative and remaining work

All rows are proposals. The existing primitives are reusable mechanisms, not proof
that the proposed durable S3 behavior is implemented.

| ID / choice | Proposed direction | Strongest alternative | Cost / failure prevented | Reuse / still to design |
|---|---|---|---|---|
| P01 Operational grouping | Stable execution account distinct from trial/request/attempt/worker | Use attempts plus an external scheduler's job grouping | Extra concept/links; prevents coordinator restart or regrouping changing scientific identity | S2 B, S1 A/history; settle minimum E meaning and cardinalities |
| P02 Commands versus forwarding | Stable logical effect command with distinct dispatch evidence | One command ID per low-level call | More correlation; prevents retransmissions being counted as independent effects or silently merged | S1 events/actions; define effect/correlation boundaries |
| P03 Native association | Evidence-bound, scoped native identity; preserve missing/conflicting associations | Derive identity from request digest/output/location | Native metadata requirements; prevents mistaken attachment, PID reuse and hidden duplicate jobs | NativeIdentity/HandleRegistry; cross-process and unexpected-episode representation |
| P04 Durable history | Events/receipts plus derived control view | Transactional mutable workflow state plus audit log | Storage/replay/migration cost; prevents lost evidence or status rewriting knowledge | Immutable stores/events; journal transaction and reconciliation contracts |
| P05 Submission uncertainty | Reconcile before a potentially new effect; keep unknown when evidence is unavailable | At-least-once automatic retry, with backend deduplication where available | Can sacrifice progress; prevents duplicate job/charge/exposure claims without verified deduplication | Runtime grants and driver receipts; scoped native guarantees and admissible risk policies |
| P06 Outcome facets | Separate requested/accepted/running/terminated/captured/interpreted/collection/accounting facts | One terminal success/failure enum plus details | More explicit assessments; prevents timeout, capture or observer failure becoming a false native outcome | S1 scoped outcomes; S3 knowledge/revision rules and minimum summary |
| P07 Worker ownership | Durable single-command ownership and receiver-appropriate fencing where required | One coordinator process and local lock only | Backend coordination cost; prevents takeover races and stale-worker effects | One-use runtime authority; leases, loss of ownership and receiver enforcement |
| P08 Interaction identity | Native action identity and scoped acknowledgement/delivery history | Match questions and answers by content/order | Driver correlation cost; prevents hidden repeated actions, duplicate exposure and misbound responses | S1 actions/transmissions, S2 decisions; inbox/outbox and unknown-delivery recovery |
| P09 Recovery | Reconnect same episode; restart new attempt with explicit continuity limits | Treat every recovery as one resumable job ID | More attempt/state evidence; prevents restart masquerading as exact continuation or replication | S1 recovery/state_load/accounting; admission and restoration evidence |
| P10 Publication/accounting | Immutable scoped snapshots and retained pending liabilities | Publish only a final successful result and final cost | More partial artifacts; prevents lost partial evidence, denominator shrinkage and cost/exposure reset | S1 stores/S2 links/populations; durable partial publication, closure and release rules |

No universal scheduler, database, retry count, lease duration, native idempotency
window or new SC-3 record type is selected in this pass. Four examples exercise
design reasoning only; they are not executed S3 acceptance cases.

## 8. Prospective acceptance obligations and source map

Future tests need positive controls and scoped failure evidence for:

1. Lost acknowledgement, with supported positive lookup, authoritative negative
   lookup, native idempotency, expired guarantees and no reconciliation.
2. Crash immediately before/after each durable boundary, with no side effect
   inferred just from a pre-call marker.
3. Reuse of command/occurrence identity with changed payload, recipient, policies,
   input snapshot or effective native key.
4. Duplicate observations versus duplicate commands and multiple native episodes.
5. Worker takeover while an old worker or provider job may still act.
6. Local exception/return followed by lost capture and retained partial artifacts.
7. Interactive selected-but-unknown-delivered response, repeated question content
   under distinct native action IDs and duplicate callback receipts.
8. Same-episode reconnect, checkpoint restart, partial RNG/state restoration and
   predecessor possibly still running.
9. Observer deadline, native stop and cancellation acknowledgement remaining
   distinguishable; no restart resetting cumulative exposure/resources.
10. Recovered/published evidence retaining original bytes and source time limits,
    with every planned scientific unit retained in its appropriate disposition.

Current reusable sources, under the qualified namespace:

- `crucis_causal/connections/api.py`: InvocationSpec, NativeHandle, Cursor,
  ObservationBatch, grant/context and publication values.
- `crucis_causal/connections/services.py`: RuntimeAuthority, HandleRegistry and
  exact execution/delivery/cancellation bindings; these services are in memory.
- `crucis_causal/connections/ports.py`: supplied/prepared/attached routes,
  bounded observation, separate delivery/cancellation authority and diagnostics.
- `crucis_causal/connections/history.py`: check_history, replay and accounting;
  representation/semantic checks do not implement a durable S3 coordinator.
- `crucis_causal/experiments/handoff.py`: project_request, record_handoff and
  link_evidence; no native launch or runtime permission follows from projection.
- `crucis_causal/experiments/lifecycle.py`: commitment/amendment/decision/exposure
  metadata with source and scope; does not perform native delivery or reserve reads.
- Existing `tests/test_audit_connections_history.py`,
  `tests/test_audit_connections_ports.py` and
  `tests/test_audit_experiments_handoff.py`: scoped primitive evidence.
  Exact test methods are indexed in the companion JSON. No S3 test is added here.

The S1 140-test and S2 334-test historical release scopes remain distinct from the
later standalone 335-test/26-skip package receipt. The qualified recorded rerun's
1,298 comparisons and 14 stored plus 14 recomputed certificate checks are prior
compatibility evidence. This design milestone must pass the current staged-tree
gate, which checks package conformance; that does not implement or validate S3
native lifecycle guarantees. No expensive data-backed rerun is needed for prose.

## Where we're going

Discuss P01-P06 and the four paths first. Then settle the minimum execution account
and what each durable lifecycle observation can establish, including contradictory
and later evidence. Detailed concurrency, authority/resource admission and exposure
reservation follow in their own design passes. Preserve the seven responsibility
boundaries, reconcile complete examples, and only later freeze serialization,
signatures, supported modes and implementation bundles.
