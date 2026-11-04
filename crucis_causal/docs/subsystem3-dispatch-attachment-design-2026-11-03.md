# S3 dispatch, native identity and attachment

Tickets: DLV-08, DLV-09; related DLV-10.
Date: 2026-11-03, America/Los_Angeles.
Status: DA01-DA12 are recommendations pending discussion. No S3 implementation,
exact API/schema freeze, production policy change, paid/native scientific execution,
protected-store access or actual remote attachment is performed in this design pass.

## 1. Continuation and scope

The user affirmed [input realization and staging](subsystem3-input-realization-staging-design-2026-11-03.md),
committed as f209d063a41bd6fcbca57a553d85cd4d0edcb4fb, and requested dispatch and
attachment: native invocation, job identity, lost acknowledgements and reconnecting
without duplicate launch. IS01-IS12 are direction-affirmed with exact details open;
that does not approve an implementation or freeze every proposal detail. New DA
recommendations remain proposals. Keep earlier dated proposal status as history.

Retain [execution identities](subsystem3-execution-identity-lifecycle-design-2026-11-03.md),
[knowledge/cutoff rules](subsystem3-minimum-account-knowledge-design-2026-11-03.md),
and [admission lifecycle](subsystem3-admission-lifecycle-design-2026-11-03.md).
Scientific trials, native attempts, commands, transmissions and observation
connections remain distinguishable. Permission, requested effects and observed
effects remain separate. Every example below is hypothetical. The source-linked
[methodology index](subsystem3-methodology-index-2026-11-03.json) distinguishes new
recommendations from narrower existing primitives, fixtures and historical receipts.

## 2. Prepare a description, then dispatch an admitted effect (DA01)

S2 supplies the applicable fixed run intent; S1 binds/represents the native request,
route and realized presentations. S3 links the exact effect command C1 to E1/R1/A1,
current admission, staging/input identity, configuration and target, actual owner
authority, resource/exposure commitments and required backend guarantees. Command
intent is durable before this coordinator permits forwarding. Late-bound transport
details must stay within the admitted content/recipient contract.

Preparation constructs a descriptor. A function entrypoint, process argument vector
or service request is not a launched job. Invocation uses an explicitly supplied
driver under current runtime authority; neither metadata nor a descriptor authorizes
arbitrary imports, shell execution, service access or implicit dependency installation.
S1 already separates prepare from invoke. This proposal adds durable coordination,
not a new unreviewed S1 route, port, grant type or wire field.

Record each attempted forwarding D separately from logical C. A pre-call marker
establishes intent to enter the driver, not actual native acceptance. Required
receiver fencing/current validity applies at the actual effect boundary; a local
check and journal transaction do not atomically include a remote launch.

## 3. Interpret operation results with boundary evidence (DA02)

| Evidence | Supported scoped claim | Does not establish |
|---|---|---|
| Controlled authorization rejection before the driver was entered | This invocation did not call its executor through the evidenced path | Absence of jobs from other transmissions/actors |
| Driver entered; exception/acknowledgement loss follows | Invocation outcome needs reconciliation; captured diagnostics/side effects remain evidence | No launch, zero cost or no disclosure |
| Native rejection with adequate admission semantics | The specified native request was rejected within that receipt's scope | No earlier upload, request billing or other commands |
| Native acceptance receipt | The identified operation/job was accepted within the receipt's meaning | Computation started, finished, correct or finally billed |
| Local driver returned a handle | A runtime reference was returned and associated as evidenced | Valid provider identity, actual native completion or durable reconnect support |
| Completion report and captured output | Those particular claims/bytes are available for assessment | Full request fulfillment, scientific correctness or settlement of every obligation |

S1 Op completed/partial/rejected describes a port operation. Keep that existing
meaning. supplied_connection currently returns rejected with execution_not_authorized
for failed pre-executor grant checks, and can also return rejected with
invocation_or_ack_failed after executor entry. S3 cannot collapse those into one
native-failure/no-effect verdict or change historical S1 labels to hide the gap.
Use structured boundary evidence and exact versioned driver semantics; arbitrary
exception text is not a reliable native-state classifier. If the necessary boundary
is unestablished, retain unknown and its admission/accounting consequences.

A malformed or wrong-attempt returned handle can be a post-effect driver failure.
Retain whatever underlying receipts/artifacts were actually captured and the missing
association evidence; failure to return a usable handle does not prove native abort
or authorize automatic retry.

### Example A: local function or process

An explicitly supplied function receives the bound input, writes an intermediate
artifact and raises before returning. Preserve the captured artifact and diagnostic;
the missing return does not negate the invocation or mutated state. If the observer
dies, a later recomputation is a later authorized occurrence, not recovery of the
original unobserved output. Purity/repeatability cannot be inferred from function.

A process descriptor contains executable, argv, working-directory and environment
policy bindings. A process handle can evidence an actual process when supplied with
adequate host/incarnation and launch provenance. A bare PID or process name is not
a durable execution identity. Where a local route has no independently meaningful
native-issued identity, retain an evidenced local invocation and unknown/not-applicable
native identity as justified; do not rename C1's generated UUID as a provider receipt.

## 4. Establish native identity and assess request conformance separately (DA03-DA04)

Recommend enough identity evidence to distinguish issuer, actual service/host and
namespace, relevant tenant/region/generation/incarnation scope, and the native ID.
Only applicable dimensions are needed; no universal cloud layout is imposed. A
native identity is not a credential or a reusable connection object. Protect secret
locators/capabilities and restrict identity evidence to its permitted audience.

Bind the receipt to the actual operation/command/request/attempt through adequate
provider/owner provenance: for example an evidenced submission correlation, exact
request or supported job metadata. No universal requirement for provider-side input
hash echo is imposed. State what is established and what remains unchecked. Name,
output shape, similar content, a timestamp or a bare user-supplied job number is
insufficient on its own. A request digest establishes content identity, not native
acceptance, deduplication or source authenticity.

Keep whose native job this is separate from whether it received/conformed to the
intended inputs/configuration. An independently bound receipt may establish N1 as
the job caused by C1 while later evidence shows the wrong dataset was used. Retain
N1 and the actual deviation; do not erase the association or claim conformance.
Conversely, plausible matching output cannot establish a launch association.

Existing S1 NativeIdentity has authority/namespace/native_id/source. Exact treatment
of additional incarnation scope needs later interface review, potentially through
existing scoped evidence/contracts where faithful. Do not add fields to its closed
wire representation in this milestone or pretend a bare ID covers recycled jobs.

### Example B: asynchronous receipt

C1 receives an adequate receipt for job 42 in its established provider/account/
namespace/incarnation scope. Capture and assess that receipt: acceptance is supported.
Queued remains distinct from running or completed. A new coordinator can later seek
that exact job under current authority. Job 42 in a different account or reused
generation is not established to be N1 just because the visible integer matches.

An authenticated callback may arrive before invoke returns. Preserve it as an
observation with its actual capture boundary. Bind it when adequate correlation
evidence exists; otherwise keep an unresolved candidate. Neither an early callback
nor its later arrival order creates a second attempt or rewrites the earlier cutoff.

## 5. Lost acknowledgement: reconcile before assuming a replacement (DA05-DA06)

### Example C: provider may have accepted C1

The provider accepts C1, but acknowledgement is lost before durable capture. E1
retains C1/A1 and pending commitments. Recovery uses the following evidence-dependent
choices; it does not issue an unrecorded fresh launch as a convenience fallback.

| Available mechanism | Permitted direction, subject to its own admission |
|---|---|
| Adequately bound native receipt/lookup establishes N1 | Associate and attach to that native episode |
| Valid native idempotency contract for C1 | Another transmission may seek the same effect/receipt within exact key, payload, namespace and retention semantics |
| Adequate negative reconciliation excluding prior acceptance and racing senders | Follow the declared recovery policy for the actually established absence |
| Inadequate/empty/eventually incomplete lookup | Retain unknown; it is not a negative receipt |
| No safe reconciliation or idempotency | Wait, close collection with obligations, or follow an explicit authorized risk policy retaining the possible old work |

Retransmitting C1 is distinct from commissioning a new native attempt. A new runtime
capability may be needed under S1's one-use authority, but that permission alone
does not make retransmission idempotent. It still needs valid native guarantees,
capacity for request effects, current exposure permission and S2 recovery eligibility.
After a guarantee's retention window expires, a repeated key cannot be presumed
safe. Changed payloads are explicit new/amended operations, not secret key reuse.

Driver/SDK/internal retry behavior must be covered by the supported guarantee or
recorded as a limit. Do not silently change a native method's retry treatment to
make a profile appear enforceable. One deduplicated provider job can still have
multiple transmissions, charges, child tasks or internal executions; native job
identity is not a universal independent-computation counter.

## 6. Attachment is its own admitted operation (DA07-DA08)

### Example D: coordinator restart, same established job

W1 ends after N1's receipt was durably recorded. W2 reconstructs E1, the association
evidence, native scope, staged-input/authority relationships, pending effects and
the declared observation position. It obtains current ownership, applicable runtime
authority and an explicit driver capable of obtaining a new connection to N1.
The old socket/object/token is not deserialized back into authority.

Before attachment, establish that the target still denotes the intended episode
within the receiver's guarantees. Attachment may open a subscription or consume
resources, so its actual effects need admission. Opening another native inference
job/session is outside an observation-only attachment guarantee. Unsupported
attachment remains unsupported; no hidden invoke/create/reset fallback is allowed.

If N1 is running, observe it within the supported scope using the same A1. If N1
has completed, collect available evidence without restarting it. If N1 is missing
or inaccessible, preserve the gap and reconcile; not found/permission denied is not
automatic authority to submit again. If a checkpoint is explicitly relaunched,
create successor A2 with continuation evidence; an observation reconnect is not A2.

Existing HandleRegistry stores established associations in memory and reconnect
returns the same registered runtime handle. It rejects a different transport handle
occupying an attempt and an established native episode assigned to another attempt.
Do not weaken those checks to force new sockets into a clean history. Durable
association reconstruction and controlled runtime-handle replacement/ownership
require a new reviewed S3/driver protocol; existing attached_connection only
observes a caller-established handle. It does not itself implement network lookup,
fresh authorization, remote attachment or duplicate-launch prevention.

## 7. Stateful sessions and externally launched work (DA09-DA10)

### Example E: reconnecting an interactive session

A session N1 paused after question Q1 and an uncertain response transmission.
Attachment must establish the same native session/action scope and recover the
available transcript/action/receipt evidence. Identical question text does not
establish the same action. A copied transcript in a newly created conversation
does not prove continuity of hidden state, pending actions, caches or exposure.

If the actual operation creates a new session or reloads a checkpoint, preserve
its new episode/attempt/continuation relationship and scope of state restoration.
Selected responses and uncertain delivery retain S2/AL exposure rules. Do not resend
an answer or reset an allowance simply because the transport connection changed.
Actual observation cursor continuity/duplication/gaps gets its own next design pass.

An operator may instead commission observation of a pre-existing external job N75.
Record the current attachment purpose, authority and actual original-history evidence.
Do not fabricate an earlier Crucis launch, prospective commitment or independent
scientific repetition. Later import can link adequately evidenced history under
S2's applicable profile/timing rules; retrospective discovery does not become an
original prospective execution receipt. External attachment cannot silently fill
a planned conforming trial merely because an output looks suitable.

## 8. Composite work and unexpected duplicates (DA11)

### Example F: native workflow versus accidental second launch

A declared workflow has a parent job and child jobs for its native stages. Retain
the actual hierarchy, correlation, input roles, accepted/missing members and accounting
coverage. One root handle can represent a native workflow where that is truthful;
do not turn each child into an independent scientific repetition or infer parent
completion from one child. Partial batch acceptance preserves each actual member's
scope rather than inventing success/failure for the complete batch.

Now suppose evidence shows that uncertain C1 actually caused two unintended jobs
N1 and N2. Preserve both and their association to the uncertain/duplicate dispatch
history. Stop automatic further launch where its prerequisites are no longer met;
any cancellation or observation needs its own authority. Do not choose the better
result, merge equal bytes into one execution, or assign an invented planned repeat.
Apply the fixed S2 selection/nonconformance policy to any analysis handoff.

The exact representation of extra unplanned native episodes remains open from the
first S3 identity note. Recommend explicit duplicate/candidate association evidence
outside the guarded single active-handle mapping until a reviewed representation
can retain it faithfully. Do not misrepresent accidental duplicates as declared
children, overwrite N1 with N2, or weaken S1 registry invariants. Durable association
cardinalities and controlled active-handle selection must be resolved before freezing
interfaces/build bundles; this milestone does not claim that gap is implemented.

## 9. Receipt and support meaning (DA12)

Minimum logical evidence links: exact intended command/request/attempt/route and
presentations; applicable admission/owner/capability references without secrets;
each dispatch occurrence and established driver boundary; source receipt/diagnostic
with native identity/operation scope and authenticity basis; input/configuration
conformance limits; identity associations/revisions; current attachment/worker
ownership and supported native guarantees; outstanding resource/exposure/stop
questions and relevant cutoffs. Reuse existing records and conditional fields;
this is not a mandatory twelve-block schema or extra IDs for every function call.

Support declarations should distinguish pure preparation, invocation, supplied-handle
observation, durable native reconciliation/attachment, idempotent retransmission,
state restoration and their guarantees/limits. A driver can support launch without
supporting safe post-crash reconnect. The generic core applies common policy and
identity/knowledge rules; explicit drivers supply mechanisms and evidence. No
universal provider API or system-name shortcut is assumed, and no capability is
claimed merely because the schema can describe it.

## 10. Choices, alternatives and open contracts

| ID | Recommended direction | Strongest alternative | Cost / failure prevented | Reuse / still open |
|---|---|---|---|---|
| DA01 | Durable exact command plus admitted explicit driver dispatch | Treat prepared descriptor as authorization/launch | More boundary records; prevents implicit effects and unbound inputs | S1 prepare/invoke and IS bindings; durable dispatch contract open |
| DA02 | Interpret port status with actual boundary/native evidence | Map completed/rejected directly to native success/no launch | Phase evidence; prevents acknowledgement failure becoming a false negative | Existing Op/gap semantics; structured driver boundary receipts open |
| DA03 | Evidenced issuer/namespace/incarnation identity | Trust a bare PID/job number or output similarity | Native provenance integration; prevents attachment to recycled/wrong jobs | S1 NativeIdentity; additional scoped identity contracts open |
| DA04 | Separate job association and request conformance | Require perfect input match before retaining association | Extra assessments; prevents hiding the actual wrong-input job or inventing matches | EA facts/S1 binding; association/conformance checks open |
| DA05 | Reconcile lost acknowledgements with scoped positive/negative evidence | Resubmit immediately on error/not found | Delay and lookup capacity; prevents duplicate launch and false absence | AL pending effects/S1 history; native lookup semantics unbuilt |
| DA06 | Actual native idempotency, separate transmissions and retry scope | Use request hash or new grant as deduplication proof | Guarantee/retention tracking; prevents repeated job charges/exposure | S1 native_action_count and one-use grants; general retransmission driver open |
| DA07 | Admitted attachment with no implicit create/invoke fallback | SDK attach-or-create convenience path | Unsupported profiles visible; prevents observing a replacement as original work | attached_connection; actual remote attachment unbuilt |
| DA08 | Durable association reconstruction, fresh runtime ownership/authority | Serialize handles or replace guarded registry entries | Driver/recovery protocol; prevents stale credentials and identity overwrite | HandleRegistry invariants; controlled replacement/cardinalities open |
| DA09 | Evidence of same session/action state or explicit new continuation | Treat copied transcript/repeated text as reconnect | State evidence; prevents exposure reset and fabricated continuity | S1 sessions/recovery; native session reconciliation open |
| DA10 | Preserve external-observation origin and timing | Backfill a prospective launch/trial from useful external output | Separate provenance/profile; prevents hindsight and manufactured repetitions | S2 historical/timing bindings; external-job admission open |
| DA11 | Distinguish native children and accidental duplicate episodes | Force one job per attempt or select one convenient result | Association records; prevents hidden work, selection bias and pseudoreplication | S1 guarded handles/accounting; duplicate representation still open |
| DA12 | Truthful scoped dispatch/attachment support and receipt requirements | One universal runnable/reconnectable flag | More support dimensions; prevents schema claims becoming native guarantees | S1 optional ports/support claims; exact interfaces/profiles open |

## 11. Prospective validation and actual evidence boundary

Future S3 cases must include pure descriptor without launch; unauthorized invocation
with zero executor calls; executor failure after an effect; native acceptance before
durable receipt; malformed/wrong-attempt handle after an effect; early callback
before invoke return; recycled/wrong-namespace IDs;
adequately associated job with wrong input; unknown local native identity; lost
acknowledgement with supported and unsupported idempotency/retention; incomplete
negative lookup and racing sender; hidden driver retry; actual durable reconnect
without launch; denied/inaccessible/completed attachment; stateful session fork;
external work without invented commitment; workflow children/partial acceptance;
two accidental jobs retained without registry overwrite or favorable selection.

These are planned acceptance obligations, not new executed S3 tests. Existing port
tests check exact in-memory grants, pure descriptors and handle reuse. The offline
s1_native_fixture and its test demonstrate a deterministic local process protocol,
duplicate-key receipts, observation, checkpoint/callback and cancellation distinctions.
They do not establish any provider guarantee or a durable post-crash network reconnect.
Existing source hashes stay unchanged. Mandatory staged-tree package gates validate
compatibility/public-source constraints, not the proposed native mechanisms.
No historical data-backed campaign/certificate, scoring or paper contract is changed.

## Where we're going

Review native boundary evidence, identity, reconciliation and explicit attachment
examples, including the still-open duplicate association/handle-replacement contract.
Then detail observation, collection and interaction: cursor scope, out-of-order and
duplicate events, gaps, capture, and admitted action/response delivery. Recovery,
publication, full S3 reconciliation, exact interfaces and build bundles remain
later design work; implementation still requires explicit authorization.
