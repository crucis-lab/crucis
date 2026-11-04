# S3 admission lifecycle under interruption and concurrency

Tickets: DLV-08, DLV-09; related DLV-10.
Date: 2026-11-03, America/Los_Angeles.
Status: AL01-AL12 are semantic recommendations pending discussion. No S3
implementation, API/schema freeze, production resource/exposure policy change,
native scientific execution, paid campaign or protected-store access.

## 1. Continuation and scope

The user affirmed the direction of [admission and ownership](subsystem3-admission-authority-resource-exposure-design-2026-11-03.md),
committed as 9fa73901567217fbcd60472d1214493b82072971, and requested interruption,
concurrency, partial reservations, lost acknowledgements, takeover and settlement.
AR01-AR10 are now direction-affirmed with exact details open; that affirmation
does not freeze a protocol or approve implementation. Earlier dated proposal
wording remains historical. New AL recommendations below remain proposals.

Retain the [minimum account and knowledge rules](subsystem3-minimum-account-knowledge-design-2026-11-03.md):
append evidence, version scoped assessments, distinguish native event boundaries
from knowledge cutoffs, and close collection without inventing native termination
or discharge of obligations. The [methodology index](subsystem3-methodology-index-2026-11-03.json)
maps these proposals to narrower existing primitives and their scoped tests.
Every example below is hypothetical, including quantities and owner policies.

## 2. One history, several independent questions (AL01)

Recommend separate views of the proposed command, each owner's reservation or
grant, coordinator ownership, native effects and settlement. A single state such
as prepared/running/finished would hide combinations that can actually occur.

| Question | Example of a justified conclusion | Independent uncertainty |
|---|---|---|
| What is proposed? | Exact launch command C1 for request R1/attempt A1 is recorded | No proof any owner or native service accepted it |
| What did an owner do? | Resource owner issued hold H1 | Exposure owner may be unavailable |
| What does the coordinator know? | H2 request sent; acknowledgement absent | H2 may exist despite no local receipt |
| Who may initiate new effects? | Receiver recognizes coordinator generation 8 | Work accepted under generation 7 may continue |
| What happened natively? | Job N1 is established running | Delivery, charges and child effects may remain unknown |
| What is settled? | Owner finalized one charge dimension | Other resources or disclosure obligations may remain pending |

Use words such as requested, held, denied, released, expired, unknown and disputed
as scoped meanings, not new frozen wire enums or one global finite-state machine.
A received grant is evidence within its actual semantics; it does not prove an
unobserved effect. An unknown result is a knowledge condition, not an owner's
business state. Empty local history is not proof that a remote hold never existed.

## 3. Logical operations, preparation and dispatch (AL02-AL04)

Retain E1, R1, A1 and native identities from earlier discussions. Distinguish the
logical effect command C1, owner-side reservation/renewal/release operations and
their individual transport transmissions. Reuse existing identities where their
meanings match; do not mandate extra UUIDs or record kinds for every local call.

An owner operation needs a stable correlation identity, exact owner namespace,
target/quantity/units/purpose and relevant policy/binding version. Retransmissions
can refer to the same operation only within the owner's evidenced deduplication
contract, including payload compatibility, retention and namespace. A content
digest alone does not establish that contract. A changed quantity or purpose is
an explicit amendment/new operation with relationships to prior obligations,
not reuse of the old key to silently mutate it. Reservation idempotency, native
launch idempotency and delivery idempotency are independent guarantees.

Recommended conceptual order, not an exact transaction algorithm:

1. Durably record intended command/owner operations before they can create effects.
   Reconstruct the full admitted history under the actual journal's durability and
   writer guarantees. Missing or corrupt journal evidence is a gap, not nonexecution.
2. Obtain required owner decisions and reservations. Capture each result separately,
   including partial preparation and uncertain acknowledgements. Preflight checks
   that have effects require their own applicable admission.
3. Establish a current admission decision tied to the exact command, evidence
   cutoff, prerequisites, grants, reservations and required guarantees. Preparation
   does not itself entitle dispatch; time-sensitive conditions can change.
4. At the actual effect receiver, enforce required validity, ownership and consumption
   conditions using the supported mechanism. Capture forwarding/acceptance evidence.
   A local dispatch marker cannot make a journal write and a remote effect atomic.
5. Reconcile native work, usage and exposure, retaining pending obligations until
   the relevant owners settle, release or explicitly accept responsibility.

No configured acquisition order produces a universal distributed transaction.
Where compatible owners actually provide atomic preparation/commit, use and state
that stronger guarantee. Otherwise preserve partial outcomes. Prefer a declared
acquisition order where feasible and bounded preparation/renewal rules to limit
deadlock, starvation and stranded holds; neither expiry nor a fairness policy
proves effects absent. Exact liveness, priorities and timing remain open. Do not
adapt scientific treatment or select successful units to hide admission delays.

### Example A: partial preparation, then owner timeout

Resource owner B issues H1 for a maximum of 6 units. Exposure custodian X receives
reservation operation O2 for one hypothetical disclosure entitlement, but its reply
does not arrive. Native dispatch is held: H1 is established; O2's result is unknown.

The coordinator can perform an independently authorized lookup of O2. With a valid
owner deduplication contract it can retransmit O2, using the same bound operation,
to seek its result. Otherwise retransmission can allocate a second hold and is
not automatically safe. A lookup returning no match is inadequate if its coverage,
consistency, retention or still-active sender leaves a race.

If X authoritatively denies O2, the coordinator may request release of H1 under B's
protocol. If that release acknowledgement is also lost, release is unknown locally.
The coordinator must not manufacture available capacity from its release intent.
An authorized lookup can later establish release without launching native work.
Holding H1 indefinitely is not the only option: owner-supported expiry or explicit
handoff can manage it, within their actual semantics and remaining liabilities.

## 4. Abandonment and dispatch race at the receiver (AL05)

Before an unused entitlement can be released, establish what prevents a delayed
sender from consuming it afterward and what earlier effects may already exist.
An accepted invalidation/release can close a future admission window at a receiver
that enforces it; it need not undo an operation accepted before that boundary.
Separate invalidating future use, finalizing existing use and returning capacity.

### Example B: release races with a delayed launch

W1 holds permission to submit C1. W2 takes over and requests abandonment/release.
W1 then sends C1. If the effect receiver orders these operations and enforces the
same entitlement, there are two meaningful cases:

- Launch was admitted first: retain the resulting native work/liability. A later
  release cannot retroactively declare the entitlement unused.
- Invalidation was effective first: the receiver rejects the stale admission.
  Release follows only under the owner's rule covering remaining liability.

A coordinator-side lock alone cannot establish either ordering. If the native
endpoint ignores entitlement validity, local invalidation cannot promise no future
launch. Withhold a strict release/redispatch guarantee, or follow a separately
authorized weaker policy retaining possible effects. A fresh local preflight read
does not close a race between that read and actual acceptance.

## 5. Lost native acknowledgement and recovery (AL06)

### Example C: launch may exist, even after preparation was complete

All prerequisites for C1 were established, the driver entered submission, and the
native acknowledgement was lost. Preserve A1/C1 and all applicable reservations.
A consumed one-use capability proves its scoped consumption, not native acceptance.
An unconsumed locally recreated capability is not proof that no earlier sender acted.

An adequately bound native lookup can establish N1 and permit supported attachment
under current authority. A valid native idempotency contract may permit another
transmission for C1; account for any extra request effects/costs separately. Without
either guarantee, submission remains unknown. Do not create a fresh command solely
to escape the old uncertainty. Any explicitly authorized additional risk-bearing
execution preserves the possible old job, resource/exposure obligations and S2
recovery rules; it does not become an independent scientific repetition by naming.

Missing provider receipts are not native failures. Polling, reconciliation and
cancellation may themselves consume resources or expose information. Their own
admission and any required reserved control capacity remain applicable.

## 6. Coordinator takeover (AL07-AL08)

Recommend durable ownership for local journal mutation, coupled with actual
effect-receiver enforcement wherever exclusion of stale actors is required.
Generation numbers are useful only if the relevant receiver checks their authority
and ordering; a self-declared larger number has no inherent force.

### Example D: W1 pauses, W2 takes over, W1 wakes up

W1 operated under generation 7. An authoritative ownership mechanism gives W2
generation 8. W2 reconstructs E1's commands, owner holds, uncertain outcomes,
native associations and pending settlements. It obtains/reconciles current runtime
authority; serialized evidence does not recreate old capability secrets.

If all relevant effect receivers enforce the new generation, W1's later new effects
are rejected there. A journal compare-and-swap alone only protects journal writes.
Generation 8 also does not terminate a generation-7 job already accepted. W2 must
reconcile that job and its descendants rather than assume takeover erased them.
If only some receivers fence stale actors, state the exact protected scope and
retain possible effects through the others. Required strict exclusion may therefore
remain unavailable on a backend; no universal cloud/provider requirement is imposed.

W2 must distinguish attachment to established N1 (same A1) from checkpoint restart
(new A2 with explicit continuation). Neither takeover nor resuming collection is
itself a new scientific repetition. A pending response delivery retains its exact
native action/session binding; repeated text is not evidence of the same action.
Observation duplicates can be retained with occurrence links without inventing
duplicate native effects. Evidence from W1 is not discarded just because W1 is stale;
its source, scope and time are assessed under the same admission/knowledge rules.

## 7. Expiry, renewal and revocation (AL09)

Keep expiry of a permission, an unused hold, a coordinator lease and native work
separate. An unused reservation can expire safely for a particular owner protocol
when that protocol establishes prevention of future use and treatment of any
already accepted liability. Local elapsed time or a dead observer does not supply
those guarantees. Record whose clock/order establishes expiry; uncertain timing
cannot be filled with a presumed native timestamp.

Renewal is an explicit versioned owner operation, not local extension of a grant.
A lost renewal acknowledgement can leave validity unknown. New effects requiring
that validity wait for reconciliation or an expressly accepted weaker guarantee;
ongoing native work may continue. A stricter deadline cannot be enforced by changing
metadata after the native service has accepted work. Required immediate revocation
needs a receiver mechanism whose documented scope actually provides it.

An owner-signed denial and later grant may be legitimate progression when ordered
within the same scope. Conflicting same-boundary receipts remain disputed; neither
latest arrival nor the coordinator's preferred outcome resolves them. Keep historical
permission assessments and later corrections, including discoveries that weaken
the evidence of authority originally relied upon.

## 8. Settlement without double accounting (AL10-AL11)

Settlement is an owner decision for a defined scope, supported by the applicable
usage/charge/exposure evidence and policy. An accepted settlement operation also
needs enough evidence to establish its result; lost replies remain uncertain.
Keep partial, final, transferred and disputed obligations distinguishable. A release
intent, cancellation receipt, native stop, collection close and final bill answer
different questions. One can settle while another remains unresolved.

### Example E: six reserved, four ultimately charged

The example's single resource dimension has a 10-unit total; the enforced 6-unit
job envelope includes all charges in this stated scope. With 6 pending and no usage
established, 4 are free. Later an adequately scoped interim report establishes
4 charged while the maximum remaining liability is 2. Represent 4 charged + 2
pending + 4 free, not 4 charged + another full 6 pending. Parent/child and inclusive
reports need explicit membership; absent that relation, withhold a fabricated total.

When the owner establishes a final total of 4 and release of the remaining 2,
the resulting allocation is 4 charged + 0 pending + 6 free. A final bill alone is
insufficient if unclosed child calls or other charges lie outside its coverage.
Different resources/units, taxes or extra requests cannot be silently folded into
this illustration. Uncertain remaining bounds withhold exact available-capacity
claims; a hard maximum is not inferred from an estimate.

### Example F: uncertain disclosure is conservatively consumed

Delivery may have occurred. The custodian's explicitly applicable policy counts the
allowance as consumed while physical delivery remains unknown. Record policy
consumption and unresolved delivery separately. This settles that policy allowance
if the owner says so; it does not prove access/use or eliminate every follow-up
obligation. No new production sealed-read rule is selected by this example.

Responsibility can instead be transferred under an explicit accepting owner's
protocol. Keep the original liability and the acceptance/scope of transfer linked;
handoff is not global discharge or proof no effects occurred. If nobody accepts,
record an unassigned/unresolved obligation rather than an imaginary responsible party.

Later evidence can contradict a supposed final settlement, reveal extra work or
weaken an enforcement premise. Append that evidence, mark the relevant current
assessment disputed/revised, and re-evaluate future affected admissions under owner
policy. Do not rewrite the old cutoff, hide a real charge, invent a negative balance
correction to erase it, or change historical scientific inclusion/scoring.

## 9. Reconciliation evidence and minimum receipt meaning (AL12)

A useful receipt must identify its actual issuer/authority and namespace, logical
operation and exact binding, resource/exposure scope and quantities where relevant,
the decision/conditions, established native identities, version/order/time semantics,
and evidence of applicability/finality. Capture source authenticity and coverage
within the actual supported protocol, not by declaring JSON authoritative. Keep
runtime secrets outside serialized/public records. No exact schema/signature is frozen.

Reconciliation must answer a precise question: whether reservation O2 exists,
whether C1 was accepted, whether H1 can still be consumed, which work is stopped,
or which liability is final. One generic status response cannot answer all of them.
An authoritative negative needs appropriate coverage/consistency, retention and
evidence excluding still-authorized racing senders; an empty listing is insufficient.
Preserve conflicting receipts and update assessments without erasing the earlier
knowledge view. If reconciliation is unavailable, retain the scoped unknown and
its policy consequences. Bounded collection may close with those obligations.

## 10. Choices, alternatives and costs

| ID | Proposed direction | Strongest alternative | Cost / failure prevented | Reuse / still open |
|---|---|---|---|---|
| AL01 | Separate owner state, coordinator knowledge, effects and settlement | One orchestration state with an auxiliary log | More explicit views; prevents unknown acknowledgements becoming failed reservations | EA assessments; exact predicates/cardinalities open |
| AL02 | Stable scoped owner operations, separate transmissions and explicit amendments | Fresh IDs on retries, or one global dedup key | Contract/reconciliation work; prevents duplicate holds and false cross-service idempotency | S1 transmission/history; owner correlation contracts unbuilt |
| AL03 | Persist intent and partial outcomes without claiming atomic remote dispatch | Treat a local transaction/outbox as end-to-end exactly-once proof | Explicit uncertainty; prevents forgotten effects at crash boundaries | Existing identity/evidence records; durable journal protocol open |
| AL04 | Conditional multi-owner preparation with bounded declared acquisition policy | Distributed prepare/commit where every required participant supports it | Stranded holds/liveness work; avoids false rollback while allowing real stronger guarantees | AR ownership; acquisition/fairness mechanisms unbuilt |
| AL05 | Order abandonment versus consumption at the actual enforcing boundary | Release on local timeout or journal cancellation | Backend support; prevents a stale sender using already-returned capacity | S1 exact grants; release/consume arbitration open |
| AL06 | Reconcile lost native acknowledgements within actual native guarantees | Automatically launch again and choose one result | Delayed progress; prevents duplicated jobs, exposure and selected-success bias | S1 native_action_count; general native recovery unbuilt |
| AL07 | Authoritative takeover plus scoped receiver fencing | Coordinator lease/journal lock alone | Receiver integration; prevents stale-actor effects beyond protected journal writes | S1 in-memory authority; durable takeover protocol unbuilt |
| AL08 | Reconstruct liabilities and preserve attempt/continuation identities on takeover | Start a clean account/attempt for every new coordinator | More history; prevents budget reset and false independent repetitions | S1 recovery/reconnect and S2 bindings; recovery planner unbuilt |
| AL09 | Distinct versioned expiry/renewal/revocation semantics | One TTL clears all ownership, holds and native work | Owner/time semantics; prevents reuse after uncertain renewal or unsafe expiry release | EA event ordering; time/revocation protocols open |
| AL10 | Scoped owner settlement with explicit inclusive membership and remaining liability | Release on current cost or observed native stop | Longer holds; prevents double accounting and premature capacity reuse | S1 accounting_total; metering/settlement integration unbuilt |
| AL11 | Separate policy debit, physical exposure and accepted obligation transfer | Treat debit/handoff as proof delivery happened or all obligations ended | More facets; prevents false exposure claims and abandoned liabilities | S2 exposure_information; owner consumption/transfer protocols open |
| AL12 | Exact reconciliation questions with scoped positive/negative/conflict evidence | Latest status wins or empty lookup means absence | Coverage evidence; prevents convenient but unsupported recovery | EA knowledge and S1 evidence; receipt/interpreter contracts open |

## 11. Prospective validation and actual evidence boundary

Future S3 acceptance cases should interrupt before and after each owner request,
receipt persistence, dispatch admission, native acceptance, release and settlement.
Include lost reserve/renew/release replies, same-operation retransmission within
and outside retention, changed payload/key misuse, partial multi-owner acquisition,
concurrent consume/release and takeover with stale actor effects. Include both
receiver-fenced positive controls and explicitly unsupported receivers.

Check interim/final inclusive costs, unknown child effects, disclosure debit with
unknown delivery, accepted/rejected responsibility transfer, conflicting/out-of-order
receipts and late evidence after closure. Assertions must distinguish native effects,
owner ledger decisions, local knowledge and permitted follow-up. These are planned
cases, not newly executed tests or evidence of live distributed/native guarantees.

S1 history already checks narrowly supported duplicate receipts, continuation,
cancellation-versus-stop and disjoint accounting; RuntimeAuthority and HandleRegistry
remain in-memory. S2 retains exposure gaps and fixed intent without executing the
new owner protocol. No existing source/test identity is rebaselined for this note.
The required staged-tree package gate checks compatibility/public-source boundaries;
it does not establish the proposed lifecycle. Scientific data-backed campaigns,
historical numbers/certificates and the paper contract are outside this milestone.

## Where we're going

Review the independent lifecycle questions and examples, including exactly which
owner/backend evidence justifies each transition. Then carry the resulting limits
into input realization and information staging. Receipt schemas, driver/core APIs,
support profiles, full S3 review and build bundles follow later design reconciliation;
implementation still requires explicit authorization.
