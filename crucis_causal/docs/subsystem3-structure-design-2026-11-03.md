# Subsystem 3: execution and collection

Tickets: DLV-08, DLV-09; related DLV-10.
Date: 2026-11-03, America/Los_Angeles.
Status: opening design proposal and read-only source inspection. No S3 contract
freeze, implementation authorization, native execution, API spend, protected-store
access or public protocol adoption. The alternatives/defaults below are proposals
for discussion, not newly attributed user decisions.

## 1. Responsibility and surrounding structure

S3 coordinates the operational realization of an S2 experiment through supported
S1 interfaces, and preserves evidence of what actually happened. It must connect
fixed scientific intent, actual prerequisites, owner authority, native side effects,
observation, interruption and immutable evidence publication.

| Owner | Existing or intended responsibility |
|---|---|
| S1 | Connection contracts, native ports, scoped runtime grants, artifacts/output objects, observations and history representation |
| S2 | Cases/trials/conditions, allowed information, source/materialization requirements, fixed selection/adaptive rules, run/request/evaluation bindings |
| S3 | Operational admission and coordination, input realization/staging, authorized dispatch/delivery, observation/collection, recovery and execution accounting |
| S4 | Referenced scientific measurement/statistical procedures; S3 may request a permitted computation without owning its mathematical meaning |
| S5/S6/S7 | Finding decisions, reporting/certification and auditor validation remain separate |
| Operator or external authority/service | Authorizes real effects and resource access; S3 must not turn a plan or an approving metadata assessment into that authority |

S3 can execute approved source-generation/transformation procedures and return
their actual outputs/evidence to S2's existing validators. It does not invent a
new transform meaning, alter a scientific condition or select a convenient output.
Actual data access, filesystem isolation and resource controls require the chosen
backend/owner mechanisms. A recorded policy alone does not enforce them.

## 2. What is already built

This pass inspected source only; it did not rerun tests or access any real sealed
store/read ledger. The prior S2 release receipt is
`../_w2_checks/2026-11-02_s2_build/S2-I/run3/gate.json`: 334 tests, zero failures or
errors, one existing optional native-PC dependency skip. Its compatibility checks
are historical evidence, not a completed S3 production execution engine.

| Source | Built capability | Boundary still needing S3 design |
|---|---|---|
| audit/connections/api.py and ports.py | Describe/bind/read/prepare/invoke/observe/decode/deliver/cancel interfaces; optional direct, prepared, attached and recorded routes | Coordinating real effects across these calls and interruptions; supplying actual drivers and prerequisites |
| audit/connections/services.py | Exact contract/route registry, scoped one-use in-memory RuntimeAuthority capabilities, HandleRegistry | Durable authority/admission ownership, restart reconciliation, resource reservations and cross-process job attachment |
| audit/connections/history.py | Attempt/recovery/event checks, accounting checks, exact ordered RecordedReplay | Durable coordinator recovery and explicit action choices after ambiguous effects; replay primitive is not universal full-system replay |
| tests/test_audit_connections_history.py and ports.py | Synthetic fixtures exercise grant refusal, duplicate launch uncertainty, reconnect, checkpoint restart, bounded observation, separate delivery/cancellation and no replay fallback | Evidence for those scoped primitives; no fresh multi-system production execution claim |
| audit/experiments/ | S2 plans, source/materialization/run bindings, exact request projection, immutable handoff and evidence links | Admitting and driving actual work; handling failures between publication and native acknowledgement |
| audit/core/adapter.py | Legacy recorded/replay/live modes and spend guards | Retain existing guards; mode labels alone do not provide every backend or authorize spending |
| audit/core/harness.py | Existing CausalArena presentation/permutation and graph/stage mapping helpers | Reusable execution cannot assume every input is one numeric table or every answer is a graph |
| audit/collect.py | Existing recorded item/arm collection; live/replay explicitly refused here | Generic durable collection and intended-versus-observed accounting; keep historical behavior unchanged |
| audit/core/sealed.py and audit/__main__.py | Existing external-store guard, commitment/check/read-eligibility helpers, aggregate filtering; sealed-check CLI | Production admission/exposure/release transactions and evidence of actual isolation; no sealed-read CLI is built here |

The RuntimeAuthority documentation explicitly limits its guarantee: it checks
supplied capability bindings and is not OS isolation against malicious Python
callers. HandleRegistry currently retains handles in memory. Its reconnect helper
does not by itself reconnect a new coordinator process to a remote job. Existing
read_allowed/record_read helpers are not a durable transactional reservation system
for concurrent, interrupted exposure. These are boundaries to design, not changes
made to those modules in this pass.

## 3. Guiding principles

1. **Faithful evidence before convenience.** Preserve uncertain launch, termination,
   capture, use and accounting facts as uncertain. A coordinator exception, timeout,
   or missing acknowledgement is not proof of native failure or absence of effects.
2. **Generic core with explicit specialized drivers.** The core owns identity,
   lifecycle, admission orchestration, evidence and recovery rules. Drivers provide
   native submit/attach/poll/interaction/cancel semantics and truthful limits. No
   system-name branches in common scientific policy. New shared capabilities can
   move into the core as their semantics become established.
3. **Separate scientific eligibility, operational readiness and authority.** A
   supported task can lack an installed dependency. An available backend can lack
   permission. A grant can expire or be consumed without proving a native effect.
4. **S2 intent stays fixed and versioned.** Realize only declared procedures and
   allowed later-bound choices. Operational difficulty does not authorize changed
   data, references, response meaning, retries or analysis selection.
5. **Durability surrounds side effects.** Record durable intent before requesting
   an effect; preserve receipts/observations afterward. Local storage and a remote
   service generally have no shared transaction. Exactly-once execution cannot be
   promised without appropriate native/backend support and reconciliation evidence.
6. **Control state and observed facts stay distinct.** A scheduler can stop waiting
   while a native job still runs. An observation stream can end without establishing
   native termination. An accepted cancellation request does not establish stop.
7. **Resources and exposure survive interruption.** Reservations, permissions,
   delivery/exposure, observed usage, provider-reported charges and unknown remaining
   liability are separate. Restart does not reset budgets or erase prior exposure.
8. **Attempts are not scientific replications.** Reconnect, replay, transport retry,
   checkpoint continuation, new attempt and new scientific trial require separate
   identities/relationships. Equal bytes do not merge occurrences.
9. **Information boundaries need operational evidence.** Stage only permitted
   payloads/endpoints. Record actual delivery/access/use separately. Required OS or
   service isolation must be supplied and evidenced, or its claim stays unavailable.
10. **Every mode and observation loop has explicit limits.** Bound events, bytes,
    time and applicable resources. No live fallback after replay mismatch, no hidden
    repair/retry, and no hard monetary-cap claim based only on a post-hoc estimate.

## 4. Proposed internal responsibilities

These seven areas are design responsibilities, not frozen modules, serialization
blocks or implementation bundles. The journal is a cross-cutting foundation.

| Area | What it needs to coordinate | Evidence or boundary |
|---|---|---|
| Execution identity and durable journal | Link S2 trial/run to S1 requests/attempts, submitted commands, native episodes and observer occurrences; preserve causal event order | Intent, acknowledgement and independently observed effect are different facts |
| Admission, environment and authority | Exact supported route, actual dependency/configuration evidence, permitted effects, resource reservations and owner-issued capabilities | Eligibility/readiness/permission/reservation/actual consumption remain distinct |
| Input realization and information staging | Execute declared trusted providers/transforms when allowed; capture actual inputs, outputs, randomization and state evidence; stage permitted native inputs | Return actual materialization evidence to S2; keep evaluator-only references/maps private to their intended audience |
| Dispatch and attachment | Direct call, process/job submission, external preparation, native attachment or historical/replay route | A prepared command is not a launch; attachment does not fabricate an original submission |
| Observation, collection and interaction | Bounded observation, artifact capture, native action requests, authorized responses, actual transmissions and partial progress | S2 supplies decision rules; S4 supplies any required measurement; S3 records and effects the permitted interaction |
| Recovery, stopping and accounting | Reconciliation after uncertain effects, reconnect, checkpoint restart, allowed retries, cancellation, resource/exposure history | Never turn unknown submission into automatic duplicate work or cancellation acknowledgement into confirmed stop |
| Evidence publication and reconciliation | Publish immutable partial/final S1 observations and S2 links; account for planned work that did not start or could not be observed | Native termination, output availability, capture integrity, interpretation and scientific correctness remain separate |

Scheduling spans these areas. It must respect the declared dependencies, pairing,
state/reset restrictions and resource limits. Performance optimization must not
silently create a new scientific condition. A single linear state enum may be
useful for local control, but cannot replace all independent evidence facets.

## 5. Execution patterns the design must cover or explicitly withhold

- One synchronous in-process call returning a value or raising after partial work.
- A subprocess, container, GPU batch or multi-stage native pipeline.
- Remote submit/poll/callback jobs where the coordinator and native lifetimes differ.
- A pre-existing external job that can be observed but must not be relaunched.
- Stateful or interactive sessions, expert/oracle queries and experimental actions.
- Multi-party/distributed work, child tasks and shared resources without invented
  global ordering, independent child counts or shared state.
- Source generation, fitted preprocessing and learned domains whose realized
  evidence becomes available after the definition is fixed.
- Recorded imports and exact response replay, with explicit exhaustion/mismatch
  behavior and no inference that replay reproduces a whole native environment.
- Long-running streams for which bounded collection ends without native completion.

Describing this space does not commit to implementing every backend immediately.
The support matrix must distinguish representable lifecycle, supplied driver,
actual environment/authority, recovery semantics, evidence and exercised tests.

## 6. Important choices and tradeoffs to discuss

| Choice | Proposed starting position | Strongest alternative | Cost and prevented failure |
|---|---|---|---|
| Coordination model | Durable events/receipts plus explicit control state, connected by occurrence identities | One mutable run/status row | More storage and reconciliation work; avoids overwritten history and success inferred from a final status |
| Uncertain submission | Preserve pending/unknown effect; reconcile using native identity/idempotency/query evidence before any retry | Automatically retry failed or unacknowledged submissions | Less automatic progress when evidence is unavailable; prevents duplicate jobs, charges, actions and exposure |
| Core versus drivers | Shared lifecycle/policy/evidence engine; small drivers for native effects and evidence | Complete workflow implemented separately in each adapter | More up-front common contracts; prevents inconsistent retries, accounting and scientific bookkeeping across systems |
| Admission | Distinct task eligibility, backend readiness, resource availability and runtime authority checks | A single runnable/ready Boolean | More explicit prerequisites; prevents a metadata pass or installed executable being treated as permission |
| Input isolation | Scoped staging plus backend-specific evidence for the isolation required by the experiment | Treat a private folder or policy label as sufficient | Environment setup and sometimes unsupported admission; prevents claiming blindness from unenforced metadata |
| Scheduling | Optimize within declared dependence, reset, ordering and resource constraints; record actual deviations | Maximize concurrency and reuse by default | Lower throughput for some designs; prevents state contamination and operational changes silently altering a comparison |
| Modes and replay | Distinct recorded/prepared/attached/direct/replay guarantees; unsupported combinations remain unavailable | One execution wrapper that falls back until something works | More explicit support gaps; prevents hidden native/API work and false reproduction claims |
| Resource/exposure limits | Durable reservations plus effect/usage evidence; unknown liabilities remain visible | Rebuild a counter from final successful reports | Integration with real authorities/providers; prevents crash/retry reset and understated cost/exposure |

No choice in this table is a new user decision or a build authorization.

## 7. Concrete failure case anchoring the next deep dive

A coordinator records that it intends to submit an LLM-backed job. The provider
accepts the job, but the acknowledgement is lost and the coordinator crashes before
recording the provider job ID. On restart:

- The intended request and attempt identities should still exist.
- We know submission was requested; we do not yet know the native effect's extent.
- Automatic resubmission could create a second billable job and additional exposure.
- A real idempotency key or supported native lookup can provide reconciliation
  evidence; hashing the request alone cannot establish that guarantee.
- If reconciliation is impossible, retain the uncertainty and apply the declared
  recovery policy. Do not silently label the first attempt unstarted or failed.
- Any new attempt must have its own identity and relationship. It is not an extra
  independent scientific repetition.

The same issue appears in process launch, human responses, intervention delivery,
checkpoint restoration and protected-data exposure. It motivates designing identity,
effect boundaries and durable history before selecting a scheduler or job backend.

## 8. Design sequence and evidence plan

Start with execution occurrences and durable lifecycle across four concrete paths:
local call, asynchronous remote job, interactive session and interrupted/resumed
work. Map the relevant execution capabilities and distinguish request/trial/attempt/
native episode/command/observation before selecting exact states or serialization.
Then examine admission/authority/resources, input realization/isolation, dispatch/
observation/interaction, recovery/accounting and publication in turn. Reconcile
complete cross-component examples before final signatures, review and bundle DAG.

Prospective acceptance cases should include a lost submission acknowledgement,
duplicate command delivery, coordinator crash, reconnect versus restart, unknown
restored RNG/state, partial outputs after failure, cancellation without confirmed
stop, replay exhaustion, changed inputs under reused identities, concurrent
resource/exposure admission and unauthorized private-input delivery. These are
future S3 acceptance obligations, not newly executed or passed tests.

A future methodology index should cite each accepted rule, implementation,
scope-specific test and real recorded/native evidence separately. Existing S1/S2
release evidence remains its own baseline. No W1 paper, tracker/site, B5/shared
scientific code, sealed storage, protocol/certificate contract or result pointer
is changed by this design note.

## Where we're going

Discuss this structure and its principles first. Next, work through execution
identity and durable lifecycle with the four concrete paths, then choose bounded
support profiles. Keep all S3 implementation and empirical execution behind their
later explicit approvals.
