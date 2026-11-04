# S3 admission, authority, resources and exposure ownership

Tickets: DLV-08, DLV-09; related DLV-10.
Date: 2026-11-03, America/Los_Angeles.
Status: semantic design recommendation. AR01-AR10 remain proposals for discussion.
No S3 implementation, production policy change, native scientific execution,
paid campaign, protected-store access or exact API/schema freeze.

## 1. Continuation and decision scope

Continue [the minimum account and knowledge design](subsystem3-minimum-account-knowledge-design-2026-11-03.md),
locally committed as 8c76c2e9be012b7bfbb9792dceedf423f123e23f. The user affirmed
that discussion and requested admission, authority, resources and exposure next.
Record the minimum-account, scoped-knowledge and independent-closure directions
as affirmed in discussion, with detailed contracts still open. The new AR choices
below are not silently attributed to the user as accepted.

The six account blocks and evidence/cutoff rules remain the foundation. An account
does not create permission. Unknown or disputed facts constrain actions whose
prerequisites require them; they do not invalidate unrelated evidence or force
every other activity to stop. Accepted S1/S2 meaning, native semantics and fixed
scientific intent remain binding. The [methodology index](subsystem3-methodology-index-2026-11-03.json)
distinguishes affirmed directions, new proposals, reused primitives and missing
implementation/evidence.

All examples and quantities below are hypothetical design reasoning. No price,
funding decision, actual read allowance or production experiment is introduced.

## 2. Admission belongs to an exact action (AR01, AR03)

Recommend deciding admission for a specific proposed action, not one global
can-run flag for an account. An action might stage bytes, probe an environment,
submit work, query status, deliver a response, restore a checkpoint, cancel,
disclose protected information or publish an allowed view. Each has different
effects, recipients, evidence requirements and resource/exposure consequences.

| Question | Required meaning |
|---|---|
| Scientifically eligible? | The action is compatible with the fixed S2 intent and its applicable prerequisites; this is not proof of causal correctness |
| Operationally ready? | The actual route, configuration, dependencies, inputs, state and required driver guarantees are evidenced within scope |
| Authorized? | The relevant real owners or valid delegates permit the exact operation, recipient, information and effects under applicable conditions |
| Resource-admissible? | Required resource capacity is reserved/available under authoritative accounting and the requested enforcement guarantee |
| Exposure-admissible? | Applicable disclosure/use policy and prior/pending exposure permit this recipient, purpose and operation |
| Safe against competing actors? | Command ownership and any required receiver-enforced fencing/reconciliation are established |
| Still valid at the effect boundary? | The bindings, authority, reservations and time-sensitive prerequisites remain applicable when the effect can occur |

For every required question, retain the supporting assessment/cutoff and actual
owner evidence. Unsupported or unassessed preconditions cannot become true through
a declaration. Unknown/disputed critical prerequisites normally hold the affected
action. Established prohibitions deny it; established missing dependencies make
it unavailable. Proved non-applicability removes only that requirement.

A policy can explicitly admit an action despite specified uncertainty, but it must
state the accepted risk and account for its possible effects. One owner cannot
accept another owner's risk or override S2's scientific conditions. Such admission
does not establish that the uncertain fact is true, create an independent trial,
or make a nonconforming result part of an intended conforming comparison.

### Example A: eligible task, unknown environment

S2's task/input binding is adequate, but the installed native dependency version
is unestablished. Hold native invocation. An authorized bounded environment probe
may establish readiness. If that probe imports executable code, contacts a service
or reads restricted data, it is itself an effect requiring appropriate admission.
Do not silently install a dependency or substitute another method. Preserve the
planned unit and its unavailable/held reason; no native-system failure follows.

## 3. Ownership and delegation (AR02)

Roles can be combined in one operator or local service for a simple deployment.
Their decision scopes must remain distinguishable. The generic core should not
require a particular cloud provider, central server or organizational structure.

| Role | Owns or attests | Cannot establish by that role alone |
|---|---|---|
| Scientific policy owner | Fixed task/condition, permitted information and declared recovery/selection constraints | Runtime permission, installed dependencies or actual compliance |
| Execution authority/host owner | Permission to invoke/attach/restore/cancel specified native operations and effects | Additional disclosure rights or scientific eligibility |
| Resource owner | Capacity, reservations, metering scope and settlement/release decisions | Permission to spend it on an otherwise forbidden action |
| Information/exposure custodian | Admission at the actual disclosure boundary; recipient/purpose/history policy and its consumption/settlement rules | Actual native use merely from a permission record, or automatic replenishment after a crash |
| Coordinator | Assemble supplied evidence, request scoped decisions, persist commands/receipts and follow declared policy | Mint rights from S2 metadata, self-reset budgets or hide unresolved effects |
| Native driver/backend | Execute permitted mechanics and report native identity, acknowledgements, usage and supported guarantees | Change scientific policy or silently broaden effect/resource/data scope |

Delegation must have an evidenced issuer, scope and validity, including relevant
recipient, operation and conditions. A resource allocator can delegate a sub-budget
within its authority, not private-data rights it never held. Applicable permissions
compose by satisfying all relevant owner constraints. Resolve policy applicability
and delegation rather than treating any arbitrary JSON denial or permit as authority.

S1's runtime capabilities are intentionally distinct from serialized authority
evidence. Persist references to authorization and validity evidence, not credentials
or runtime capability secrets. A new coordinator must obtain/reconcile current
authority as required; an old one-use capability cannot be serialized back to life.

### Example B: public reference, prohibited information channel

A reference graph is publicly obtainable, and the operator has capacity for a
native job. The declared names-only condition still does not permit supplying that
graph as native input. Hold/deny that delivery for the conforming trial. An explicit
oracle-control condition can permit its own scoped channel when the fixed plan
and applicable owners allow it. Public availability is not scientific permission,
and an input-channel rule is not proof the model never encountered public facts.

## 4. Resource reservations and guarantees (AR04, AR09)

Keep capacity, reservations, actual usage, reported charges, estimates and unknown
liabilities separate. Track typed dimensions: monetary budget and its billing scope,
requests, native actions/jobs, CPU/GPU time, memory, slots, storage and any other
declared resource. No exchange between dimensions is inferred. One deduplicated
job can still involve multiple billed requests or other consumed resources.

Recommend durable owner reservations for capacity that must not be oversubscribed.
Every reservation binds its purpose/command and accounting scope, quantities/units,
applicable validity and possible prior liabilities. Parent envelopes and child
allocations need explicit inclusion relationships; do not subtract or sum the same
capacity twice. This reuses S1's disjoint/inclusive/overlap distinctions without
claiming its accounting checker is already a reservation manager.

| Guarantee requested | Admission consequence |
|---|---|
| Hard bound over all relevant effects | Require an adequately evidenced bound and an enforcing native/backend boundary or equivalent mechanism covering those effects |
| Estimate/advisory threshold | Allowed only if the plan and owners explicitly accept that weaker guarantee; record its limitations |
| Required bound unknown or hidden work can exceed it | Withhold the hard-bound admission/claim; do not relabel an estimate as enforcement |
| No applicable monetary billing dimension | Establish non-applicability for that scope; other compute/time/storage/data conditions can still apply |

A local timer or cancellation request cannot generally cap remote billing without
the necessary native guarantees. Native retry behavior, child calls and permitted
side channels must fall within the claimed enforcement scope. S1's grant checks
are not OS isolation against arbitrary malicious Python code. Required isolation
or mediation must be evidenced; otherwise restrict the support claim or withhold
admission where that guarantee is a prerequisite.

### Example C: a lost job does not restore capacity

Suppose a fictional budget contains 10 job-resource units. Command C1 reserves an
enforced maximum of 6. Its launch acknowledgement is lost. The owner still has a
6-unit pending commitment, leaving 4 unreserved units under that accounting rule.
Actual consumption is unknown; the ledger must not claim that 6 were actually used.

A second independent 6-unit commitment cannot fit the unchanged budget. Verified
native idempotent retransmission might seek the same job/receipt within C1's valid
guarantee, but any extra request cost needs its own capacity and authority. A new
permission token does not erase the prior reservation or prove no first job exists.
An expanded budget would still not, by itself, authorize a scientifically invalid
retry or override exposure restrictions.

Later partial billing is not necessarily final settlement. Release unused capacity
only under adequate owner evidence/policy about remaining liability, not merely
because the current cost report is below the reserved bound.

## 5. Exposure belongs at the custodian's boundary (AR05)

Keep the allowed information, permission, reservation/hold, requested delivery,
actual delivery/access/use, policy consumption decision and release separate.
One service may own both resource and exposure ledgers; their meanings stay distinct.

The applicable custodian must define what consumes an allowance and the identity
scope over which history applies: for example the experiment/battery, system/version
lineage, recipient, session, purpose, data/channel or operation. These are policy
dimensions, not new production defaults. S3 must not infer that a new account,
attempt, coordinator, session label or editable version string resets history.

For a limited disclosure, recommend an authoritative reservation/check at the point
where protected bytes or an information-bearing response can leave custody. A
post-report log alone cannot establish that concurrent earlier disclosure was
properly admitted. Any driver or cache that bypasses the custodian limits the
enforcement/blindness claim; no metadata label closes that gap.

When delivery might have happened, retain a pending hold or record the owner's
explicit consumption decision. A conservative policy debit is an accounting
decision under uncertainty, not proof of actual delivery/use. Release/rotation/
replenishment require the relevant owner's rule and evidence. There is no new
sealed-read count, reset rule or authorization selected in this design pass.

### Example D: two coordinators see one remaining disclosure allowance

Two workers each read a view saying one allowance remains. Independent local checks
cannot both justify disclosure. An authoritative atomic reservation or equivalent
custodian mechanism must decide the competing requests before release. One can
receive an entitlement; the other is held or refused within that policy scope.

If acknowledgement of a reservation is lost, the reservation itself may be unknown.
Reconcile the same reservation operation with the owner rather than create a new
one and ignore the first. If a worker dies after possible disclosure, mere timeout
or lease expiry does not prove the allowance is unused. Expiry can release only
what the owner's protocol establishes is safe to release. Pending exposure survives
coordinator restart and collection closure.

Current sealed helpers retain their historical policy/tests. This proposal does
not use real seeds/read ledgers or replace those helpers with a claimed production
transactional service. If a required single-admission guarantee is unavailable,
the strict protected-execution profile remains unavailable.

### Example E: selected answer, uncertain delivery

S2 selects response V for action Q1. Its exact recipient and permitted information
are bound. S3 still needs applicable delivery authority and resource/exposure
entitlement; an execution grant does not supply them automatically. A denied or
unknown recipient/disclosure prerequisite holds that delivery. Any abstention or
alternate response must itself be supported, permitted and conform to the plan.

If transmission then becomes uncertain, retain its possible exposure. Do not
automatically resend V, authorize another read or count it as definitely unseen.
A later matched receipt can establish delivery; actual access/use and policy
settlement remain their own questions. Repeated answer bytes do not establish a
free duplicate operation under a policy whose unit is an action or disclosure.

## 6. Multi-owner admission and durable effect boundaries (AR06-AR08)

Recommend these conceptual steps, without freezing an exact transaction protocol:

1. Persist the proposed effect command and its exact target, intent and requested
   guarantees. Prerequisite checks that themselves have effects need applicable
   authority; do not access protected data merely to discover whether access is allowed.
2. Evaluate the relevant evidence/cutoff and applicable owner policies/delegations.
   Obtain required scoped reservations and authorizations through supported protocols.
3. Retain every acquired, rejected, expired or uncertain hold/grant decision. If one
   owner is unavailable after another reserved capacity, record partial preparation.
   Do not dispatch until all applicable conditions for that action are satisfied.
4. Establish current command ownership and required receiver-enforced fencing.
   Recheck time-sensitive bindings/permissions at the effect boundary under the
   actual owner/backend guarantee. Bind the grant to the exact action and conditions.
5. Capture consumption, forwarding and acknowledgement evidence independently.
   Capability consumption does not prove native acceptance or actual billing.
6. Reconcile observations/usage/exposure against the owner scope. Release, revoke,
   compensate or hand off only as that authority's protocol permits; preserve
   uncertain or irreversible effects and their obligations.

There is no universal atomic transaction over independent owners and native effects.
Use stronger prepare/commit guarantees where actually supplied. Otherwise retain
partial/unknown outcomes and withhold effects that require stronger guarantees.
A local rollback cannot undo disclosure, remote submission or consumed capacity.

Leases are not permission to ignore pending effects. A stale worker can still act
after a local lease expires unless the relevant effect receiver enforces ownership
or revocation. Protecting journal writes alone does not fence native operations.
Cached decisions can be reused only within their evidenced scope/validity and
declared freshness rule; no mandatory central round trip is imposed on every local
action. Required immediate revocation needs an appropriate enforcement mechanism.

Minimum admission-receipt meaning: exact action/account/request/attempt binding;
target/recipient/inputs/configuration; governing policies and actual owner evidence;
knowledge/evidence cutoff and unresolved prerequisites; separate decision and its
conditions; resource/exposure reservations and pending liabilities; ownership and
validity; required versus established enforcement guarantees. Runtime secrets stay
outside serialized/public records. Admission is not observation that the effect occurred.

### Example F: revocation, cancellation and closing collection

Execution was permitted when C1 launched. Its authority is later revoked for new
execution effects. Preserve the original time-scoped permission and actual launch
evidence. Evaluate later polling, responses, restoration or cancellation against
their own current permissions. A policy may separately permit termination/recovery;
revoked execution authority neither creates nor necessarily removes that permission.

A cancellation acknowledgement does not prove stop, and stopping collection does
not discharge the native job's liability. Hold or settle the relevant resources/
exposure through owner evidence. Never turn revocation into a claim that earlier
authorized execution did not happen or that the native process has already stopped.

## 7. Bounded recovery and heterogeneous work (AR09-AR10)

When a bounded operating profile requires future status checks or cancellation,
plan the needed control capacity/authority rather than consume all available
resources on launch and assume recovery is free. This is a conditional planning
recommendation, not a new default cap or proof that cancellation can stop every job.
Keep native treatment budgets and coordinator control overhead explicit; do not
silently reduce the declared native allowance to fund recovery.

Multi-party work may satisfy admission for party A while party B remains unknown.
Independent preparation or a child action may proceed only if its own fixed-plan
prerequisites and owners allow it. Do not substitute A-only execution for a question
requiring both parties or report complete global evidence. Retain held/missing
units and actual deviations. Resource envelopes and exposure policies can have
different parent/child scopes; native parallelism does not establish independence.

The core should interpret common policy/identity/knowledge/ledger protocols.
Drivers provide native mechanisms and truthful capabilities; owners supply actual
permissions and accounting/disclosure rules. Representable policy does not imply
every backend can enforce it. Strict versus advisory profiles make those limits
visible without system-name shortcuts or hidden live/replay fallback.

## 8. Choices, tradeoffs, reused primitives and open work

| ID | Recommended direction | Strongest alternative | Cost / failure prevented | Reuse / still to design |
|---|---|---|---|---|
| AR01 Action-scoped admission | Check all applicable scientific, readiness, authority, resource and exposure conditions for the exact action | One account-wide runnable flag | More explicit decisions; prevents a launch permit authorizing unrelated effects | S2 bindings/S1 bind; action prerequisite contracts remain open |
| AR02 Ownership/delegation | Explicit real-owner scopes, composable delegates and runtime capabilities | Coordinator owns one broad root credential/policy | More integrations; prevents self-grant and cross-owner overrides | S1 grant types/RuntimeAuthority; durable issuer/delegation contracts unbuilt |
| AR03 Knowledge-dependent permission | Bind decision to evidenced prerequisites, validity and accepted uncertainty | Reuse a prior ready/allowed result without freshness checks | Rechecks/holds; prevents stale readiness or unknown effects being treated as absence | EA cutoff/revision rules; precise validity/freshness predicates open |
| AR04 Resource accounting | Typed owner reservations distinct from actual usage/charges | Final-report cost counters or estimated cost ceilings | Persistent accounting; prevents oversubscription and unknown cost becoming zero | S1 accounting scopes; reservation/metering enforcement unbuilt |
| AR05 Exposure custody | Admission/reservation at actual disclosure boundary, with persistent policy history | Check a local flag and log the read after results exist | Custodian coordination; prevents concurrent double disclosure and crash reset | S2 exposure/legacy sealed helpers; production owner protocol remains open |
| AR06 Multi-owner preparation | Explicit partial/unknown holds, with conditional dispatch and real protocol guarantees | Assume local transaction gives all-or-none cross-service effects | Reconciliation/compensation; prevents forgotten holds and false atomicity | Immutable history; exact prepare/commit/reconcile order deferred |
| AR07 Ownership/revocation | Scope grants and fencing at the effect receiver, honoring actual validity | Local locks, leases and journal flags alone | Backend support/limited profiles; prevents stale-worker effects after takeover/revocation | S1 one-use capabilities; durable ownership/revocation integration unbuilt |
| AR08 Settlement | Retain unknown liabilities until authorized settlement/release/handoff | Release on timeout, expiry, callback error or collection close | Longer holds; prevents duplicate spending/exposure and understated obligations | EA closure and S1 accounting; owner release conditions open |
| AR09 Enforcement profiles | State exactly which hard/advisory guarantees a backend supports | Treat every configured cap or private-path label as enforced | Visible unsupported scope; prevents overstated cost/isolation/privacy guarantees | Existing support registries; detailed S3 profile matrix open |
| AR10 Recovery headroom | Reserve appropriate control capacity when required by the operating profile | Spend all capacity on primary work and rely on emergency bypass | Reduced initial throughput; prevents stranded unobservable work or invented permission | Bounded observe/cancel ports; sizing and priority policy deferred |

Existing source is deliberately narrower than these proposals. S1 bind consumes a
supplied dependency inventory and returns scoped readiness. Its capability checks
enforce their supplied in-memory bindings, not a durable distributed budget or
disclosure service. Observe bounds batches; it does not establish the new resource
admission policy. S2 exposure_information retains reported/observed information and
gaps independently of grant/consumption policy. core.sealed's existing checks/log
helpers and tests do not prove transactional production admission under concurrency.
Legacy RunRecord cost/status meanings and existing spend guards remain unchanged.

## 9. Prospective acceptance obligations

Future S3 cases need positive controls and precise missing/denied prerequisites:

- Adequate scientific binding with missing environment, permission or enforcement.
- Grant bound to wrong command/attempt/recipient/payload/effects or expired/revoked
  validity; copied permission metadata cannot create runtime capability.
- Two concurrent workers contesting one resource or disclosure reservation.
- Lost reservation acknowledgement and partial acquisition across different owners.
- Lost native launch/delivery acknowledgement retaining capacity and possible exposure.
- Native idempotency covering one job but not eliminating extra request costs.
- Hard-bound request on a backend supplying only estimates or incomplete mediation.
- Lease expiry/takeover with a stale worker, and revocation without confirmed native stop.
- Partial billing/inclusive totals and parent/child envelopes without double accounting.
- Collection close or new account/version label without allowance or liability reset.
- A permitted scientific oracle control and a prohibited reference leak in another arm.
- One unavailable party without automatic scientific substitution, and bounded recovery
  requiring reserved control capacity rather than emergency authority invented later.

These are hypothetical obligations, not executed S3 acceptance tests. Source hashes,
scoped existing tests and claim limits are in the methodology index. This milestone's
mandatory staged-tree gate checks package compatibility and publication constraints;
it does not establish these new admission/enforcement guarantees. No historical
scientific numbers, thresholds, certificates or checkpoint inputs are changed.

## Where we're going

Discuss the owner roles, action-specific conditions and examples first. Then work
through exact interrupted/concurrent admission and reservation lifecycles, including
grant validity, partial acquisition and safe settlement, before input realization
and staging. Choose detailed interfaces, profiles and implementation bundles only
after the complete S3 design is reconciled and reviewed.
