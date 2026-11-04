# S3 consolidated contract outline and complete worked cases

Tickets: DLV-08, DLV-09; related DLV-10.
Date: 2026-11-03, America/Los_Angeles.
Status: semantic consolidation candidate. CS01-CS12 are new recommended resolutions
pending review. No S3 implementation, wire/API freeze, production policy, native
scientific execution, paid campaign, protected-store access or remote publication.

## 1. Continuation and meaning of this pass

The user affirmed [publication/reconciliation](subsystem3-evidence-publication-reconciliation-design-2026-11-03.md),
committed as 3cf0cac76e6bb53815396ceb67525a484b35839a, and requested a consolidated
outline with complete local, remote, interactive and checkpoint examples to expose
and resolve gaps. EP01-EP12 are now direction-affirmed with exact details open,
not blanket approval of every detail or implementation. Preserve earlier dated
status and source hashes. New CS recommendations below remain proposals.

The [companion examples](subsystem3-contract-examples-2026-11-03.json) are illustrative
semantic traces, not SC-3 wire specimens, executed receipts, native scientific runs
or a validation suite for implementation. Their field names/IDs are documentary
vocabulary. Their claims are conditional on fictional capabilities explicitly stated
in each case. The [methodology index](subsystem3-methodology-index-2026-11-03.json)
retains rule -> existing primitive -> scoped test -> supported claim/limit boundaries.

This pass proposes semantic resolutions to the identified incompatibilities. Exact
encodings, owner/driver signatures and implementation evidence remain separate work;
an unresolved backend guarantee is represented as a scoped unavailable/unknown
capability, not silently supplied by the outline.

## 2. One contract, seven responsibilities and six account blocks (CS01)

S3 coordinates an explicitly commissioned preparation, execution or observation
purpose through admitted effects and durable evidence. S2 owns scientific intent,
eligible inputs/recovery/selection/timing/populations. S1 retains native connection,
presentation, artifact/output and scoped history meaning. Native systems/owners
provide actual effects, permission, metering and enforcement. S3 does not compute
new scientific scoring or invent source truth/permissions from metadata.

| Responsibility | Common contract obligation |
|---|---|
| Execution identity/history | Preserve commission, prospective/actual attempt relationships, effect commands, observations and knowledge history |
| Admission/environment/authority | Decide exact effects from applicable evidence, actual owner rights, reservations, validity and receiver guarantees |
| Input realization/staging | Realize admitted recipes, capture/check actual inputs, construct permitted presentations and retain partial disclosure/cleanup |
| Dispatch/attachment | Bind exact native effects and native identity; attach explicitly without hidden launch |
| Observation/interaction | Preserve capture progress, source scope/order/gaps, native occurrence associations and fixed permitted decision/delivery history |
| Recovery/stopping/accounting | Apply the declared evidence-dependent recovery rules; retain actual/possible resource/exposure and independent stop/settlement scopes |
| Publication/reconciliation | Freeze scoped views, preserve earlier cutoffs, project actual permitted content and reconcile commits/corrections/availability |

These responsibilities are not seven new implementation modules. The existing
six minimum account blocks remain the record outline:

1. **Identity and fixed target:** account/commission, purpose, recorder, original
   scientific or observational/preparation target and immutable version relationships.
2. **Activity and association index:** scoped requests, attempts, commands/transmissions,
   native episodes/candidates, runtime ownership and their evidenced relationships.
3. **Evidence index:** captured artifacts/observations or explicit declarations,
   availability/integrity/extent, interpretations, dependency and audience context.
4. **Scoped assessments:** exact questions/subjects, basis and cutoff, procedure,
   support/conflict/unknown/applicability and revision relationships.
5. **Disposition and pending obligations:** intended/admitted next operations,
   owner rights/reservations, resource/exposure/stop/cleanup/publication obligations.
6. **Collection periods and closure views:** source scope/frontiers, bounds and
   cutoffs, stopping reason, actual coverage, pending work and explicit follow-up.

Empty means empty only in its stated local/index scope. Known native absence,
non-applicability, unassessed, unknown and disputed retain their distinct meanings.
There is no one success flag combining native completion, response fulfillment,
scientific correctness, authority, evidence completeness and settlement.

### Preparation dependency resolution

An account can start from prospective S2 intent/recipe/source requirements before
the final run binding and native request exist. Realization is an admitted S3
effect; it must not be hidden inside S1's pure descriptor preparation. Return actual
realization evidence to S2, then establish its final eligible binding/S1 handoff.
Admitted staging can precede that handoff when content/recipient/effects are already
bound. A later binding cannot authorize an earlier disclosure retroactively.

Do not fabricate a ready binding, prospective scientific trial or original native
attempt for a materialization-only or external-observation commission.

## 3. Identity/cardinality resolution (CS02-CS03)

| Concept | Recommended common rule |
|---|---|
| Account E | One explicit commission/purpose; may reference zero or multiple actual attempts and related immutable bindings within that purpose |
| Scientific trial T / binding B / request R | Reuse actual S2/S1 identities when meaning matches; no attempt/transport/observer count implies independent T |
| Attempt A | One prospective/evidenced execution episode in its declared history; checkpoint relaunch/ended-episode retry has a successor, reconnect does not |
| Native episode inventory | Retains every evidenced/candidate native episode and actual hierarchy, even without a unique canonical attempt association |
| Primary A-to-N association | Establish only when unique and adequately supported; zero/unknown/disputed remains explicit; duplicate episodes cannot overwrite the primary guard |
| Command C / transmission D | Exact logical effect has zero/multiple forwarding occurrences; changed effect/binding needs an explicit new related command, not hidden mutation |
| Runtime connection | Opaque connection scoped to native target, role/subscription and ownership/context epoch; not durable native identity |
| Publication | Exact immutable snapshot/operation relationships, separate from mutable current selection and native/scientific occurrences |

**Duplicate resolution:** store native episode evidence/associations independently
of the single guarded active-handle slot. If C1 caused N1 and N2 unexpectedly,
retain both, their possible/established cause, costs and exposure. Where the primary
association is ambiguous, withhold it and automatic effects requiring it; authorized
observation of each target can still be admitted. An independently established
original association can remain supported while extra native work is recorded;
it does not establish single execution. Count actual evidenced native episodes
separately from prospective attempt records, without inventing extra planned trials,
forcing both into one S1 handle or labeling them declared workflow children.

**Shared/external observation resolution:** additional observers reference an already
established canonical attempt/episode where appropriate rather than minting a second
attempt for the same native work. A native episode with unknown original request/
attempt can remain an explicit external-observation target with origin unknown.
Use an S1 route only when its actual reference/handle requirements are met. A new
S3 observation driver/profile must support no-established-origin-attempt scope where
needed; until supplied, that route is unavailable. Never invent A to satisfy an API.
Shared native work across scientific units requires S2's explicit compatible shared-
work/dependence binding; identity reuse does not establish independent repetitions.

**Handle replacement resolution:** reconstruct current connections in an explicit
new runtime context/ownership epoch from durable association evidence, current
authority and a supported attachment driver. Keep S1's current registry invariants
inside each context; do not patch entries or deserialize old capabilities. A fresh
registry/context does not fence an old worker. Required exclusion still needs actual
receiver enforcement and reconciliation of already accepted work. Multiple observer
connections are allowed only under the source's read/consumer ownership semantics.

**Incarnation resolution:** native identity includes the relevant generation/host/
issuer/namespace scope under an exact descriptor contract. Existing S1 NativeIdentity
is closed; any faithful compatibility encoding or accompanying S3 association needs
an explicit reviewed mapping. Unknown critical incarnation prevents strong lookup/
control claims, not preservation of captured evidence.

## 4. Common effect and owner contract (CS04)

Every effect, including source generation, reservation/reconciliation, upload,
invocation, attachment, polling, delivery, cancellation and publication, binds:

- Its exact commission/subject, operation/content/recipient and parent dependencies.
- Applicable scientific conditions, operational prerequisites and evidence cutoff.
- Actual owner authority, resource/exposure commitments and runtime capability use.
- Current ownership/validity and required versus evidenced receiver guarantees.
- Logical operation/transmission identities, captured receipts and unresolved effects.

This is one common semantic pattern with typed operation-specific inputs, not one
untyped execute-anything API. Owners provide scoped request/decision/reserve/reconcile/
settle meanings where applicable; the coordinator cannot mint rights. Each owner
operation has stable correlation, exact binding, validity/retention and positive/
negative/unknown result semantics. Native idempotency is separate from owner hold,
publication or response idempotency. A hash or new runtime grant supplies none.

Partial preparation is explicit. Dispatch waits for all applicable prerequisites;
independent preparation may proceed under its own admission. There is no universal
all-or-none transaction over owners/native effects. Hold/release/consume arbitration,
revocation/fencing and finality must operate at actual enforcing boundaries where
the requested guarantee requires them. Required unknown guarantees hold affected
actions; weaker risk profiles need actual owner permission and S2 eligibility.

Unknown protocols may be preserved descriptively but cannot execute merely through
a declared capability. Exact operation defaults, acquisition liveness and signatures
remain later contract work; no fixed retry count, exposure allowance or paid action
is selected by these examples.

## 5. Capture, event and action consistency (CS05-CS07)

**Capture resolution:** a durable capture checkpoint binds the permitted evidence
and source scope/extent to its next recoverable position in one actual journal commit.
Referenced external evidence must have the storage/availability guarantees required
by that capture claim before progress is asserted. Cross-store orphaned artifacts
can exist after interruption; source ack remains its own evidenced operation.
Interpretation progress is separate, so malformed captured bytes do not cause a
false complete interpretation or endless replay solely to satisfy a parser.

**Cursor/event resolution:** positions retain source/partition/filter/generation/
protocol and boundary/retention semantics. Native occurrence identity is separate
from observer occurrence and wire-record identity. Associate replayed native events
only on adequate evidence; preserve actual capture order and native partial order.
Sparse offsets are not missing records without the needed coverage contract.

**Conflicting wire identities:** if an incoming record reuses a global record ID
with different content, reject its integration into the valid record namespace.
When permitted, capture the offending source package as raw evidence under a new
artifact identity with diagnostics; do not merge contradictory definitions or lose
the source merely because it cannot be ingested as valid structured evidence.
Native semantic disputes instead use distinct observations/assessments with their
actual source/scope. These two conflict classes have different remedies.

**Decision resolution:** each supported native action has an evidenced occurrence,
permitted decision procedure/input frontier, immutable selected-response history
and separately admitted delivery command. No text-based action deduplication or
automatic re-selection after possible transmission. If S2 explicitly permits a
pre-delivery decision update, create a new decision/command and establish old command
invalidation/nonexecution at the required boundary; do not overwrite the old choice.

Incoming callback acknowledgement and answer delivery stay logically distinct. A
native endpoint can combine them in one physical response only under an explicitly
supported combined-effect contract with the corresponding exact admission/evidence.
Logical roles do not require extra physical round trips or UUIDs when one real
operation faithfully supplies several facts. Abstention remains an explicit response,
not an invented interpretation of silence. Unsupported decision/provider/fallback
contracts hold the dependent action rather than leak evaluator information.

## 6. Recovery, accounting and outcome consistency (CS08-CS09)

Wait/reconcile, transport resend, new native attempt, reconnect, checkpoint restart,
cancel and close collection retain RC meanings. A checkpoint successor has actual
load evidence and continuity only for established components. Required full continuity
or serial execution remains withheld when RNG/state or predecessor stop is unknown.
An explicitly eligible partial continuation preserves those limits and every attempt.

Resource/exposure history survives account/worker/connection/attempt changes within
its actual owner scope. Keep reservations, usage, charges, unknown remaining liability,
credits, release and settlement distinct. Report revisions/inclusive membership are
interpreted by explicit rules; never add every cumulative report or assume zero from
missing data. Native durations, interval unions and peaks need their appropriate
procedures. Existing S1 accounting_total remains its narrow disjoint nonnegative
quantity checker; new S3 owner-ledger meanings do not silently expand it.

Scientific treatment budgets and control overhead remain explicit. Native stop,
descendant stop, observer close, cleanup, budget release and exposure settlement
are independent assessments. A primary output can survive native failure; S2's
fixed role/selection/inclusion policy chooses usability, not latest/best convenience.

## 7. Publication, audience and assurance consistency (CS10-CS11)

A frozen S3 view pins its admitted operational frontier and applicable exact S1/S2
snapshots/dependencies; it does not retype their scientific/native meanings. This
is a logical dependency manifest, not a newly frozen SC-3 wire schema. Partial
components/unknowns stay explicit; a complete root claim needs actual required
component commit/availability evidence. Publication receipt/hash reports bind the
exact frozen subject externally, avoiding self-hash cycles and post-commit mutation.

Actual audience projection precedes serialization/dissemination to that audience.
Preserve unchanged safe records/context; altered/redacted records are new derived
identities. Close over permitted dependencies/metadata, not merely selected roots.
If the original basis/lineage cannot be disclosed, retain its connection to the
public statement in an authorized private projection receipt; do not export that
private dependency chain as a public reference closure. A derived audience summary
declares its limited extent rather than masquerading as a complete six-block account.
Public claims can be weaker than authorized private verification. Raw retention,
source authenticity, byte integrity, cutoff coverage and scientific eligibility
remain distinct. Later unavailability/corrections get new observations/packages,
not repinned historical hashes or backdated decisions.

Current pointers are optional. Immutable publication and reproducible analysis can
use exact pinned identities without any mutable alias. For history-sensitive S3
pointer advancement, require an actually enforced expected revision/generation
or equivalent mechanism. Existing selected-value CAS remains a narrower compatibility
capability; do not use its output generation to claim an expected-generation check.
Lost commit/alias acknowledgements reconcile exact operations and state rather than
rerun native work. Compatible branches merge through explicit assessments/membership,
while record conflicts and semantic disputes retain the distinct handling above.

## 8. Support is a composition of scoped capabilities (CS12)

Recommend a common capability vocabulary across drivers/owners/backends, with exact
operation, subject/effect scope, prerequisite, guarantee, evidence and limitation.
Convenient named profiles can compose these; no system-name shortcuts or universal
all-live/all-complete tier. Distinguish representable contract, supplied driver,
available dependency/authority, passed scoped tests and actual native evidence.

| Axis | Meaning needed when applicable | Honest fallback |
|---|---|---|
| Input | Static/generated/fitted/dynamic/multi-party identity and permitted realization | Preserve declaration/gap; no silent replacement input |
| Effect | Explicit launch/attach/observe/deliver/restore/cancel operations | Unsupported operation held; pure description remains available |
| Recovery | Source replay, native lookup/idempotency, receiver ownership and stop scope | Bounded partial account with pending effects |
| Information | Actual presentation/custody/recipient/retention and exposure rule | Scoped trusted-interface/advisory claim; strict isolation withheld |
| Resources | Actual owner capacity/metering/bounds/finality and compatible aggregation | Unknown/advisory only where allowed; no fabricated hard cap |
| Evidence | Durable capture/progress, exact package/dependency integrity and audience projection | Explicit weaker scope or unavailable stronger publication |
| Selection | S2-compatible action/output rule and exact admitted input cutoff | Held/partial nonconformance, not a guessed scientific answer |

Simple local work need not implement every distributed capability. The four cases
exercise selected lifecycles only; they are not universal integration evidence.
Streaming/federated/generated/native-hidden-state variants retain explicit additional
obligations rather than being forced into the batch/local examples.

## 9. Complete local path: L (proposed trace, not a run)

L starts with one intended trial and prospective source/recipe target. The admitted
realization takes a synthetic three-column table, presents [C,A,B] with neutral names,
and records the value/mapping check. Only after materialization does it establish
B/R/A and pure invocation preparation. An explicit trusted local function boundary
is admitted; no provider job ID or OS-wide blindness guarantee is fabricated.

One invocation returns a complete native ordering. Preserve its raw bytes, derive
the canonical ordering using the evaluator-only map and assess requested response
fulfillment separately from causal correctness. Native/job-resource scope settles
at 0.7 of a fictional 1-unit allowance; control/storage dimensions remain their
explicit scope. Close collection and publish a private exact view plus an admitted
public summary that excludes the evaluator map. Public verification is limited to
its actual allowed evidence/attestation basis.

Exposed gap/resolution: preparation cannot require an already-final B; S1 prepare
stays pure; lack of external N is not failure; a public root does not filter the map.

## 10. Complete remote path: R (proposed trace, not a run)

R has one trial, A1/C1 and a 6-unit commitment in a 10-unit native-job envelope.
W1 submits once, loses acknowledgement and closes a first view with acceptance
unknown and the commitment pending. W2 obtains actual ownership/fencing, looks up
the same command and establishes scoped N42 with acceptance predating that cutoff.
P2 adds that evidence without rewriting P1 or creating A2.

W2's new observation connection is reconstructed in its new runtime context. An
event-18 callback arrives before a source-window poll returns events 17 and 18;
associate the duplicate 18, retain native running17 -> completed18 order, and commit
the poll's capture progress only with durable evidence. Capture the graph response,
retain causal correctness as unassessed, finalize native charges at 4/release 2,
and publish a new view. The example counts two explicitly scoped control requests;
no observation reconnect is a second invocation.

Exposed gap/resolution: durable association is not the old socket; replay/callback
dedup is not content merging; P1's earlier unknown stays valid. If lookup/idempotency
or receiver fencing required by the profile is absent, hold the affected new effects
and retain uncertainty. Two discovered jobs use the independent episode inventory,
not a registry overwrite or invented second planned repetition.

## 11. Complete interactive path: I (proposed trace, not a run)

I has one native session/attempt. Its declared condition explicitly permits an
oracle-response channel with a custodian-defined action allowance; this is not
default evaluator feedback. A callback and poll identify the same Q1. Capture both,
make one selection V1 from its permitted source/frontier, reserve/authorize its
delivery and send once. Acknowledgement is lost. The replacement coordinator keeps
that selected answer and possible exposure, then reconciles a matched Q1 receipt.
It does not reselect from newer information or send again merely because it can
obtain a fresh local grant.

A later Q2 has identical text but a distinct established native action identity.
The required source information is unavailable in this branch and no fallback is
permitted, so the dependent answer is held. At the declared deadline, close with
Q2 pending, an actual captured partial local answer and native termination unresolved.
Q2's required source context differs from Q1 despite identical question text;
the earlier response cannot silently stand in for the unavailable current source.
One policy allowance is consumed for Q1; that is not proof of use. Publish the
bounded partial account without an invented final response or zero score.

Exposed gap/resolution: complete account does not require complete native execution;
same-text Q2 is not Q1; silence is not abstention. A condition explicitly permitting
abstention would need a new selected/admitted response. An endpoint combining callback
ack and answer needs its real combined-effect contract, not an extra universal ACK.

## 12. Complete checkpoint path: K (proposed trace, not a run)

K starts A1, captures a complete intermediate output and available checkpoint, then
establishes A1 stopped to its nonoverlapping-restart scope while billing remains
pending. Its declared recovery policy permits partial continuation. A2/N2 loads
the evidenced model/optimizer state; RNG/history continuity remains unknown. Record
the explicit successor/load and scoped limits rather than exact full restoration.

A2 produces the first eligible final response under the fixed S2 rule. Preserve
unselected intermediate output and both attempts. In the 20-unit illustration,
A1's final 5 plus A2's final 4 gives 9 native-job units, leaving 11 after settlement.
Pending A1 charges were retained while A2 ran. A late final bill creates a new
assessment/package; it does not rewrite earlier unknown costs. The checkpoint's
restricted audience remains separate from any permitted public result view.

Exposed gap/resolution: stopped is not settled; checkpoint identity is not complete
restoration; a permitted partial restart is not an exact-continuation claim. If full
RNG continuity or predecessor stop is required but unestablished, hold that restart/
claim. A2 is not a second scientific repetition and its 4 units are not the total
cost of obtaining the selected answer.

## 13. Resolution ledger, alternatives and remaining precision

| ID | Recommended resolution | Strongest alternative | Cost / failure prevented | Remaining precision |
|---|---|---|---|---|
| CS01 | Six account blocks, target roles and pre-final preparation dependency | One fixed run record requiring B/R/A at creation | Conditional references; prevents dummy readiness and historical launch fabrication | Exact minimum field/cardinality encoding |
| CS02 | Independent native inventory/associations, guarded unique primary, unknown-origin observation | One-to-one E/T/A/N model or relax S1 guards | Association records; prevents hidden duplicates and false independent samples | Typed episode/relationship serialization and S1 projection |
| CS03 | Durable association plus explicit new runtime ownership context | Serialize/replace old handles in place | Controlled reconstruction; prevents stale effects and identity overwrite | Attachment/replacement signatures and scope enforcement |
| CS04 | One typed effect/admission/owner semantic pattern with real guarantees | Broad coordinator root credential and generic execute | Owner integration/holds; prevents self-grants and false idempotency/atomicity | Exact owner operations, validity/finality and liveness contracts |
| CS05 | Capture-evidence/progress commit, interpretation and source ack separate | Advance on fetch or require flawless parse first | Durable storage/replay; prevents loss and poison-event loops | Journal/artifact commit protocol and ack profiles |
| CS06 | Separate native occurrence/capture/wire identity and scope/order | Hash dedup, latest wins or merge same-ID changed content | Explicit evidence; prevents merged real actions, false gaps and corrupted namespaces | Cursor/event association and raw-conflict capture shapes |
| CS07 | Frozen permitted decision basis; explicit supersession/combined effects | Recompute after uncertainty or mandate separate ACK everywhere | Versioned decisions/backend support; prevents response races and changed treatment | Decision/provider/delivery/receiver signatures |
| CS08 | Explicit successor/load/stop/outcome facets and S2 fixed selection | One success/retry/reset state | More scoped outcomes; prevents false restoration and favorable output selection | Recovery policy and supported stop/component vocabulary |
| CS09 | Typed owner ledgers, report revisions and cumulative exposure/attempt cost | Sum all numbers or reset on new attempt | Metering/settlement work; prevents double counting, zero-unknown and allowance reset | Aggregation/revision/credit contracts and owner API |
| CS10 | Exact dependency view, external receipt pins and actual audience projection | Serialize roots/all evidence and redact display | Projection/storage; prevents leak and self-hash/byte-identity mistakes | Snapshot/projection/assurance envelope and permitted provenance |
| CS11 | Optional current pointer, strong revision precondition where required | Treat value CAS/latest as full history assurance | Backend support or no pointer; prevents missed-update overclaims and analysis drift | Alias generation/operation protocol and cross-store commit scope |
| CS12 | Composed capability/claim matrix with explicit unsupported scope | One universal native-ready tier or system-name profiles | More declared conditions; prevents representation becoming integration proof | Exact named profiles, support evidence and acceptance matrix |

These resolve the semantic choices as recommendations, not accepted wire contracts
or claims that the mechanisms are built. Backend-specific absence of a required
guarantee has a defined consequence: hold the dependent action/claim, retain evidence
and gaps, and permit only independently admitted effects. No universal guarantee is
invented to make the four examples complete.

## 14. Documentary validation and implementation evidence boundary

Check the companion's local reference closure, six-block coverage, history references,
one planned scientific trial per case, expected native invocation/attempt counts,
local synthetic permutation/order consistency, remote replay identity, interactive
pending Q2/no second transmission, checkpoint continuation/partial state and ledger
arithmetic. These checks inspect authored documentary examples only; they do not
execute a native system, materializer, owner, durable coordinator or SC-3 codec.

Existing source/test hashes remain unchanged. Scoped S1/S2 primitives and offline
fixtures are foundations, not four implemented S3 paths. Mandatory staged-tree gates
check existing package compatibility and public-source constraints. No historical
scientific rerun/certificate, threshold, scoring, production policy or paper change.
The separate research/reviewer tooling remains outside this contract and repository.

## Where we're going

Review this common outline, the four complete semantic traces and CS resolutions.
Next specify the precise minimum/conditional record and capability matrix, then
bounded serialization, journal/owner/driver interaction and recovery signatures,
S1/S2 compatibility mappings and failure cases. Run another complete-record review
before final S3 design acceptance and bundle planning. No S3 implementation is
authorized by this consolidation.
