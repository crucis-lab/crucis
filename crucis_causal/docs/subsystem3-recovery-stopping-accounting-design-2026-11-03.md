# S3 recovery, stopping and resource/exposure accounting

Tickets: DLV-08, DLV-09; related DLV-10.
Date: 2026-11-03, America/Los_Angeles.
Status: RC01-RC12 are recommendations pending discussion. No S3 implementation,
exact schema/API freeze, production recovery/budget/exposure policy, native
scientific execution, paid campaign or protected-store access is introduced.

## 1. Continuation and retained scope

The user affirmed [observation, collection and interaction](subsystem3-observation-collection-interaction-design-2026-11-03.md),
committed as 587f60ea561b6364293f597d40e9e2239f307377, and requested recovery,
stopping and accounting, with wait/retry/reconnect/restart/cancel/close examples.
OC01-OC12 are direction-affirmed with exact details open, not implementation
approval or blanket interface acceptance. RC01-RC12 below remain proposals.
Earlier dated proposal status and source hashes retain their historical meaning.

Consolidate rather than replace the [identity rules](subsystem3-execution-identity-lifecycle-design-2026-11-03.md),
[minimum account and closure](subsystem3-minimum-account-knowledge-design-2026-11-03.md),
[owner admission and settlement](subsystem3-admission-lifecycle-design-2026-11-03.md),
[input custody](subsystem3-input-realization-staging-design-2026-11-03.md),
and [dispatch/attachment](subsystem3-dispatch-attachment-design-2026-11-03.md).
S2 retains scientific intent, eligibility, selection, stopping/recovery conditions
and planned populations. S3 coordinates actual permitted effects and preserves
their evidence; it does not change scoring, thresholds, protocol or paper inputs.
All examples/quantities are hypothetical. The [methodology index](subsystem3-methodology-index-2026-11-03.json)
distinguishes recommendations from narrower existing code and scoped tests.

## 2. Choose an action from current evidence, not a universal error handler (RC01)

A failed local port call, lost contact, native failure, exhausted observer and
budget denial answer different questions. Recommend assessing exact subject/scope,
current native identity and knowledge cutoff, pending commands/effects, scientific
recovery eligibility, owner authority, capacity/exposure and actual backend guarantees
before choosing a recovery action. Missing recovery policy does not create a default
permission. Preserve disputed evidence and the rationale for held actions.

| Choice | When supported | Identity/effect consequence | What remains independent |
|---|---|---|---|
| Wait/reconcile | Evidence is incomplete and the declared bounds/authority permit the chosen follow-up | No new native invocation merely from waiting; queries/renewals are their own admitted operations | Existing work, charging, exposure and deadlines can continue |
| Retry a transmission | Same exact command under adequate native deduplication or evidenced no-effect/recovery conditions | Another forwarding of C1 can retain prospective/current A1 within the actual contract | Fresh runtime permission alone does not deduplicate or reset liabilities |
| Retry an ended native episode | New execution is allowed by the fixed recovery policy and current admission | New A2 with retry ancestry; R stays only if its meaning remains compatible | Prior outcomes/cost/exposure and the original scientific trial remain |
| Reconnect | Same N1 is established and attachment is supported/permitted | New observation connection, same A1/N1; reconstruct supported cursor history | No hidden launch, state reset or proof that pending delivery never happened |
| Restart from checkpoint | New native episode and restoration are eligible/admitted | New A2, normally N2, explicit continuation and actual load evidence | Exact state continuity, predecessor stop and settlement require their own evidence |
| Cancel/stop | Current authority and actual mechanism cover the intended target/effect | New control command and its actual receipt/stop evidence | Request, acknowledgement, native stop, descendant stop and final bills differ |
| Close collection | Declared observation boundary is reached or permitted closure is selected | Immutable cutoff/coverage/gaps and pending-obligation disposition | Native work and resource/exposure obligations do not automatically end |

Several choices can compose: request cancellation, collect bounded follow-up,
then close with stop unknown. A recovery decision records its exact trigger,
policy/version, evidence/cutoff, chosen operation and prerequisites, intended identity
relationships, actual receipts and pending obligations. These are semantic meanings,
not new enums, fixed retry counts or frozen record blocks.

## 3. Bounded waiting and distinct stopping clocks (RC02)

### Example A: no acknowledgement, no adequate job lookup

C1 may have launched. An authorized bounded reconciliation query can seek evidence;
waiting without a new native launch preserves C1/A1 and their commitments. Waiting
is not proof of inactivity or zero incremental cost. Polls, subscriptions, reservation
renewals and stored evidence can have their own costs/disclosures. Backoff, maximum
follow-up, observation deadlines and necessary control capacity need declared rules;
this design selects no universal retry count, interval or emergency bypass.

Keep scientific treatment limits (for example an eligible native action budget),
scientific stopping criteria, observation/watchdog bounds, owner authority/resource
validity and native deadlines distinct. Record whose clock/order establishes each
boundary and why stopping was triggered. Coordinator restart does not reset elapsed
treatment time or replenish a budget. Pausing an observer need not pause native work.

A predeclared convergence/quality-based stop can be legitimate when its actual
measurement/input authority and procedure are supported. S3 cannot invent a reference-
score stopping rule after seeing results or repair missing measurements with evaluator
feedback. Later measurement providers retain their own scope. An operational outage
or storage cap is not automatically native algorithm failure or successful scientific
completion. Actual deviations remain available to S2's declared analysis policy.

Hard total bounds require native/backend enforcement covering relevant effects.
A local timer, inability to poll, cancellation request or expired coordinator lease
does not cap ongoing remote work by itself. If required control capacity/authority
cannot be established before launch, the corresponding strict operating profile is
unavailable. If it is lost after launch, retain the resulting risk/obligation; no
new permission or claimed stop is manufactured.

## 4. Transmission retry, ended-attempt retry and reconnect (RC03-RC04)

### Example B: lost launch acknowledgement versus failed native job

For an uncertain C1, a retransmission using the original adequately bound key may
seek the same effect within a valid native idempotency contract. Keep each transport
occurrence and actual request costs. A hash, new local capability, expired key or
convenient empty listing cannot establish that guarantee. Evidence proving no effect
through the relevant paths can instead support the declared recovery choice, with
current admission; do not assume every failed call reached or failed to reach native.

If A1 is established ended and another eligible native execution is commissioned,
allocate A2 and explicit retry ancestry. Preserve the original intended trial,
inputs/recipe/randomization relationships, failures and total accounting. A new
attempt is not a new scientific repetition and is not permission to redraw until
a favorable answer appears. Changed scientific meaning needs its actual new request/
binding or amendment; compatible retry alone does not change the fixed target.

### Example C: connection lost while N1 remains running

If N1 is adequately identified and attachment is supported, reconcile current
authority/ownership and reconnect to N1/A1. Restore only the evidenced observation
position under the source contract, preserving replay/gaps and pending decisions.
Do not call invoke merely because an observation handle disappeared. If N1 completed,
capture available evidence without restarting. Reprocessing retained bytes with a
new decoder is a derived evidence operation, not a new native attempt.

Native internal worker retries or workflow children retain their actual native
hierarchy and limitations. They are not automatically additional S2 repetitions or
proof of one elementary computation per provider job. The DA association/cardinality
questions remain explicit full-review obligations rather than a forced universal map.

## 5. Checkpoint restart and continuity (RC05)

### Example D: optimizer restored, RNG and interaction history unknown

A1 produced an available checkpoint. An admitted restart creates A2/N2 and records
the checkpoint identity/extent, compatible implementation/configuration, requested
components, actual observed load results and continuation to A1. A successful file
hash or load intention does not prove actual restoration of every state component.

If optimizer state is established loaded but RNG, fitted preprocessing, cache or
session/action history is unknown, preserve partial continuity. An exact-within-scope
claim requires adequate evidence for every component in its named scope; it does
not establish complete hidden-state equality or statistical independence. If required
continuity is unestablished, hold that recovery/claim or use only the explicitly
eligible weaker mode. A warm start for a changed task has its related new request.

Before a required nonoverlapping restart, establish predecessor stop to the required
scope. If A1 may still run, A2 can introduce overlap/duplicate risk and additional
resource/exposure. Proceed only under the actual scientific recovery policy and
owner admission accounting for that possibility. Accepting financial risk cannot
override a condition forbidding concurrent work. A failed/partial restore after
A2 starts remains an actual attempt with its costs and effects, not an erased setup.

## 6. Cancellation, escalation and stop scope (RC06-RC07)

### Example E: cancellation acknowledged, job still running

An authorized cancellation targets the established native episode and relevant
scope. Its receipt acknowledges the request; a later observation still reports
running. Preserve both. Follow only the declared bounded observation/escalation
policy, with current authority and capacity for each operation.

Graceful stop, forced process termination, provider cancellation, child-task cleanup,
endpoint revocation and staging cleanup can have different rights/effects. Do not
silently escalate to a stronger operation because a soft cancellation did not stop
work. Execution authority may be revoked while a separate recovery/termination
permission remains; assess the actual current scopes. Revalidate incarnation identity
before acting on a reusable PID/job number, and honor actual receiver fencing.

An evidenced parent stop does not establish that all children, callbacks, remote
calls, staged access or metering ended. Declare which components must be stopped
for the requested guarantee and assess their actual evidence. If enumeration or
termination is incomplete, retain the limit and possible ongoing work. A remote
stop receipt can leave final billing unknown. Natural completion can race with
cancellation; later-arriving output remains evidence with its source/cutoff and
selection limits, not automatic proof that the cancellation failed or succeeded.

Collection may close at its declared boundary with pending stop/resource/exposure
questions. Preserve gaps, responsibility/handoff and the permitted follow-up. If no
owner accepts an obligation, retain it as unresolved/unassigned rather than claim
discharge. Do not silently keep active polling inside a closed period or answer an
unresolved native question merely to make shutdown appear complete.

## 7. Typed accounting with explicit aggregation and uncertainty (RC08)

Keep capacity, reservation, actual usage, reported/established charges, estimates,
remaining liability, release and settlement separate under owner scope. Each
quantity needs resource kind/units, membership/time/recipient scope, evidence basis,
measurement/aggregation procedure, coverage and revision/finality meaning. Partial
evidence can support a lower bound without establishing an exact total or zero.

| Resource/account | Appropriate meaning, subject to actual scope |
|---|---|
| Repeated cost reports | Revisions/cumulative totals are not additive disjoint charges; establish coverage and select a consistent current assessment |
| Native actions/jobs and transport requests | Count distinct evidenced units under their contracts; one idempotent job can involve several requests |
| Elapsed time | Overlapping intervals need a named interval/clock procedure; adding durations can overcount |
| Compute time | Add only established compatible disjoint usage under the chosen procedure; it is not automatically elapsed time |
| Peak memory/concurrency/slots | Individual peaks are not an observed shared peak; define temporal/aggregation scope or an explicit bound |
| Storage/retained objects | Current size, peak size and byte-time differ; continuing retention may remain billable after native stop |
| Exposure | Recipient/information/history policy, confirmed/possible disclosure, policy debit and settlement remain distinct from monetary units |

Do not convert resources, currencies or inclusive parent/child counters implicitly.
Versioned billing corrections/refunds need owner evidence and a named accounting
rule; do not mutate original reports or feed negative usage into S1's nonnegative
disjoint-sum helper. A legitimate scoped credit remains distinguishable from gross
charges, usage and unsupported negative corrections invented to erase real effects.
Revised/overlapping totals need their own reviewed interpretation, not wider tolerance.

S1 accounting_total currently supports explicitly selected unrevised disjoint,
nonnegative compatible quantities and rejects inclusive overlap and s1.duration sums.
It does not implement this generic metering/settlement ledger. Preserve that boundary.

## 8. Budgets survive attempts; preserve control overhead (RC09)

### Example F: failed attempt plus restart within 20 native-job units

This hypothetical single dimension covers the included native job charges under
enforced envelopes. A1 reserves 8. An interim owner report establishes 3 charged,
leaving at most 5 pending. A1 is then established stopped to the restart-required
scope, but its final bill is unknown. A2 is eligible and reserves 6.

| Owner-evidenced stage | Charged | A1 pending | A2 pending | Free |
|---|---:|---:|---:|---:|
| A1 interim charge within its 8-unit envelope | 3 | 5 | 0 | 12 |
| A1 stopped; A2 admitted; A1 bill unresolved | 3 | 5 | 6 | 6 |
| A1 finalized at 5 and remainder released | 5 | 0 | 6 | 9 |
| A2 finalized at 4 and remainder released | 9 | 0 | 0 | 11 |

Each row accounts for the same 20-unit total. Final native cost is 9 even if only
A2 supplies the selected answer. An A1 stop does not release its unresolved 5 by
itself. Interim/final reports revise the covered liability; they do not add another
full A1 envelope on top of its included charges. This arithmetic is a design example,
not a stored billing result or execution receipt.

Observation, requests, retention and control costs require their own actual scopes;
the table does not imply they are free or covered by these illustrative job units.
When bounded recovery requires polling/cancellation headroom, reserve it explicitly
under the operating profile. Do not quietly reduce a declared native treatment
budget to fund control overhead, and do not assume an exhausted budget authorizes
emergency paid work. Actual overruns or unsupported bounds remain reported facts.

## 9. Exposure across reconnect, restart and changed state (RC10)

### Example G: V1 may have reached Q1 before interruption

A1's selected answer V1 has uncertain delivery. Reconnect retains Q1's exact action,
pending transmission and possible exposure. Restart A2 does not reset its history
scope or create a fresh entitlement. If the actual restored state contains prior
information, retain that evidence and its limits. A new process/session label cannot
establish a previously unexposed scientific condition or erase provider/pretrained state.

The custodian's actual policy may retain a hold, consume the allowance conservatively
or accept a scoped settlement. Record that decision separately from physical delivery,
access and use. Duplication/replay and per-action versus per-information units follow
the applicable owner rule; identical bytes do not establish a free read or response.
No new production allowance count, reset rule, sealed seed access or consumption
policy is selected here. One owner cannot waive another's information constraints.

## 10. Later evidence, settlement and scientific handoff (RC11-RC12)

Reconcile each resource/exposure/stop question against actual owner/native evidence.
Late billing or stop evidence can revise current assessments while preserving what
was known at each earlier decision/closure cutoff. Settlement/release replies can
also be lost or disputed. Current availability/finality cannot be inferred from
intent, timeout, native completion, collection closure or an expired local lease.

An accepted responsibility transfer records who accepted which remaining obligation
under what policy; it does not establish that no effects occurred or globally discharge
the liability. If supposed finality is contradicted, retain new evidence, reassess
affected future admission and record a revision/dispute. Do not hide the charge,
relabel a condition or rewrite the old receipt/knowledge view.

Preserve the scientific trial and fixed S2 intent, every actual attempt/continuation,
selected and unselected outputs with their roles, nonconformance/missingness reasons,
and all actual/pending accounting. Retry count, reconnect count, cost count and
scientific repetition count remain distinct. Supported output inclusion/selection
and analysis cutoffs follow S2; S3 neither chooses the best surviving result nor
turns an operational failure into a zero score or removes the intended unit.

The common core should evaluate these policy/evidence/identity relationships;
explicit drivers/owners supply actual restoration, cancellation, measurement,
settlement and receiver guarantees. State unsupported strict profiles honestly.
Exact interfaces and defaults remain full-review work, not universal action-on-error
rules installed by this milestone.

## 11. Choices, alternatives and open work

| ID | Proposed direction | Strongest alternative | Cost / failure prevented | Reuse / still open |
|---|---|---|---|---|
| RC01 | Evidence-dependent recovery with exact trigger/policy/cutoff | Retry every rejected/failed operation | More decisions/holds; prevents unknown effects becoming duplicate work | EA/DA evidence facets; recovery decision protocol open |
| RC02 | Bounded waiting and distinct scientific/observer/owner/native clocks | One global timeout resets/stops everything | Timing/control evidence; prevents false stop, free waiting and altered treatment | OC bounds/AR headroom; clock/stopping profiles open |
| RC03 | Transmission retry distinct from ended-episode retry | One retry counter or fresh attempt for every transport resend | Explicit identity history; prevents deduplication mistakes and false repetitions | S1 transmission/recovery; actual retry planner unbuilt |
| RC04 | Reconnect established ongoing work or reprocess captured evidence | Relaunch when observation fails | Driver/retention support; prevents hidden replacements and recomputation passed off as original | S1 handles/decoder and DA attachment; durable protocols unbuilt |
| RC05 | New restart attempt with scoped observed restoration and overlap eligibility | Treat checkpoint hash/load success as exact continuation | State evidence/possible unsupported recovery; prevents lost RNG/history and concurrent duplicate work | S1 state_load/recovery; restoration drivers/association details open |
| RC06 | Separately admitted cancellation and explicit escalation | Stop flag or soft ack authorizes stronger termination | Backend/owner integration; prevents wrong-target effects and false termination | S1 CancellationGrant/native_stop; escalation protocol unbuilt |
| RC07 | Separate observer, native/descendant and obligation closure | Mark account finished when one component exits | Pending obligations; prevents orphaned work and premature release | EA closure/AL settlement; full stop-scope profiles open |
| RC08 | Typed scoped metering and explicit revisions/aggregation | Sum every reported number/cumulative total | Accounting contracts; prevents overlap, mixed units and fake exact totals | S1 accounting_total; generic ledger/aggregation unbuilt |
| RC09 | Cumulative budgets across attempts with explicit control overhead | Reset budget on retry or report only selected-attempt cost | Lower apparent headroom; prevents hidden failed-work costs and stranded recovery | AR reservations/S1 disjoint costs; owner budget integration open |
| RC10 | Persistent actual/possible exposure and owner-specific settlement | New session/attempt means fresh allowance | Custodian/state evidence; prevents repeated disclosure and false fresh-state claims | S2 exposure/IS custody; actual owner enforcement unbuilt |
| RC11 | Versioned owner-evidenced settlement and accepted handoff | Release on stop/timeout/closure or overwrite bill | Longer holds/reconciliation; prevents overstated capacity and hindsight | AL owner operations/EA cutoffs; finality/transfer rules open |
| RC12 | Faithful S2 intent/population/output handoff and truthful support | Keep last/best success and flatten attempts into repetitions | More provenance; prevents selected-success bias and changed denominators | S2 bindings/evaluation; complete S3 reconciliation/interfaces open |

## 12. Prospective validation and actual evidence boundary

Future cases should exercise each choice with positive controls, missing/denied
prerequisites and disputed outcomes: bounded wait while native charges continue;
safe resend versus ended-episode retry; reconnection without invoke; decoder-only
reprocessing; partial/failed checkpoint restoration; predecessor stop unknown under
serial versus explicitly permitted overlap; cancellation ack without stop; child
work after parent exit; unauthorized escalation; deadline and control-capacity loss.

Check inclusive/cumulative charge revisions, all-attempt versus selected-attempt
cost, disjoint versus overlapping time/peak metrics, unknown usage, legitimate credits,
20-unit example arithmetic, exposure carryover across restart, uncertain delivery,
late final bills, lost settlement replies, accepted/unaccepted handoff and closure
with pending obligations. Preserve fixed trial membership, actual attempts, state
limits and S2 selection/cutoff rules in every case.

These are planned S3 obligations, not newly executed acceptance tests. Existing
S1 tests cover checkpoint successor/partial RNG evidence, cancellation-versus-stop,
disjoint costs across attempts, duplicate-receipt limits and local fixture behavior.
S2 tests retain exposure, amendments, intended missing units and scoped selection.
They do not implement operational recovery, actual resource/exposure owners,
distributed stop or the proposed generic accounting. Source/test hashes are unchanged.
This milestone's staged-tree gates check offline compatibility/public-source limits;
any arithmetic check validates the hypothetical example only, not real metering.
No historical numeric campaign/certificate, scientific scoring or paper contract changes.

## Where we're going

Review the evidence-dependent action table, restart/stop examples and cumulative
resource/exposure account. Then design immutable evidence publication and
reconciliation: how partial and final operational views become verifiable packages
without exposing restricted material or rewriting prior cutoffs. Resolve remaining
association, cursor, handle, owner, decision and accounting contracts during full
S3 review before exact interfaces, support profiles and build bundles; implementation
still requires explicit authorization.
