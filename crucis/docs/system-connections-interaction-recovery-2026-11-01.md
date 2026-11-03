# Subsystem 1: interaction, recovery, replay and resource contracts (1 Nov 2026)

Tickets: DLV-08, DLV-09; neighbours DLV-10, ADV-01, DLV-06.
Status: precise proposed contracts for review; no executor, workflow engine or runtime implementation.
Uses [SC-1 serialization](system-connections-serialization-2026-11-01.md) types and closed-field notation.
These payload contracts have independent versions; they do not alter the base envelope or protocol verdicts.

## 1. Responsibility boundary

Subsystem 1 describes and observes a native connection, including state and exchanges. It neither selects
scientific experiments nor sets retry/spend policies. A supplied policy/authority can be represented and
checked at the connection boundary. Recording an action or requested allowance does not authorize it.
Scheduling, scientific denominators and analysis choices remain external consumers of these records.

The actor making an assertion, the observer recording it, the native audited component and the actor
performing an action are separate references. Unknown identities stay unresolved. Callback/test/expert
implementations have version/configuration identity like other components.

## 2. Exact additional record payloads

All use the SC-1 envelope, knowledge, reference, scope, source, number and time definitions. Tables list
closed payload fields, not code. Required uncertain fields can use the specified unresolved form.

| record_type | Payload fields |
|---|---|
| s1.session | request:Ref(request), native_identity:K(NativeIdentity), parent:K(Ref(session)), membership:IndexList(Ref), completion_rule:Contract, source:Source |
| s1.event | subject:Ref, actor:Ref(component), event_contract:Contract, content:Ref, native_time:K(Time), local_sequence:K(Sequence), predecessors:Ref(event)[], correlation:K(String), source:Source |
| s1.endpoint | owner:Ref(component), operation:Contract, request_contract:Contract, response_contract:Contract, input_domains:Ref(domain)[], allowed_information:Ref(policy), transport:Contract, source:Source |
| s1.authority_evidence | actor:Ref(component), policy:Ref(policy), operation:Contract, subjects:Ref[], permitted_effects:Code[], decision:permitted|denied|unresolved, validity:Scope, source:Source |
| s1.action_request | session:Ref(session), attempt:Ref(attempt), requester:Ref(component), endpoint:Ref(endpoint), arguments:Ref[], question:K(Ref(proposition)), authority:Ref(authority_evidence), native_action_identity:K(NativeIdentity), source:Source |
| s1.action_response | request:Ref(action_request), responder:Ref(component), content:Ref[], response_state:returned|abstained|rejected|failed|unresolved, delivery:Ref(presentation)[], source:Source |
| s1.transmission | message:Ref(action_request|action_response), sender:Ref(component), recipient:Ref(component), transport:Contract, native_receipt:K(NativeIdentity), outcome:submitted|acknowledged|rejected|contact_lost|unresolved, source:Source |
| s1.recovery | successor:Ref(attempt), predecessor:Ref(attempt), recovery_kind:retry|checkpoint_continuation|warm_start|branch, request_relation:same_request|new_request, state:K(Ref(output)), load:K(Ref(state_load)), reason:K(Code), policy:Ref(policy), source:Source |
| s1.state_load | attempt:Ref(attempt), snapshot:Ref(output), requested_components:Code[], observed_components:StateComponent[], configuration_before:Ref(configuration)[], configuration_after:Ref(configuration)[], continuity:exact_within_scope|partial|unresolved|contradicted, scope:Scope, source:Source |
| s1.replay | request:Ref(request), attempt:Ref(attempt), source_attempt:Ref(attempt), transcript:Ref(artifact_snapshot), match_rule:Contract, match_parameters:Ref[], consumed:ReplayMatch[], unmatched:Ref(action_request)[], exhaustion:stop|return_unresolved, fresh_fallback:forbidden, source:Source |
| s1.accounting | scope:Scope, quantities:Ref(output)[], members:Ref[], aggregation:Contract, coverage:disjoint_members|inclusive_total|overlapping|unresolved, revised:Ref(accounting)[], source:Source |
| s1.cancellation | subject:Ref(attempt|session|action_request), requester:Ref(component), policy:Ref(policy), requested:Ref(event), acknowledgment:K(Ref(event)), observed_stop:K(Ref(event)), source:Source |

Sequence = {stream:String, position:Index, producer:Ref(component)}. Positions are comparable only within
their declared stream/producer contract. StateComponent = {component:Code, identity:K(String),
availability:K(Ref(artifact_snapshot)), loaded:K(Boolean), evidence:Ref[]}.
ReplayMatch = {action:Ref(action_request), source_event:Ref(event), response:Ref(action_response),
match_scope:Scope, occurrence_key:String, checks:Ref(check)[]}.

Root session parent uses not_applicable under the explicit s1.no_parent rule rather than a fake session.
Membership is a scoped immutable enumeration, with later membership observations/relations appended instead
of overwriting the session snapshot. A session/action association absent from historical evidence remains
unresolved rather than requiring a fabricated hierarchy. Non-propositional actions can mark question
not_applicable under their endpoint contract; missing question evidence is a separate unresolved state.

## 3. Correlation, messages and partial order

An action occurrence, transmission and native execution are different identities. A transport retry can
resend the same action; it does not establish a new native action or exactly-once delivery. Preserve each
transmission outcome and reliable receipt/deduplication evidence. If two possible native actions cannot
be distinguished, retain ambiguity instead of merging them or counting two established operations.

Responses reference the question/action they answer, the responder and actual delivered content. Multiple
responses to an action are allowed when the endpoint contract permits streams/revisions. Contradictory
responses remain separate sourced statements. A transport acknowledgment is not proof of application-level
use or completion. A missing response is an observation gap, not an abstention.

Event order comes from supported local sequences, native predecessor links or established correlations.
Concurrent events need not have a total order. Check predecessor identity, prohibit self-predecessors and
cycles in asserted event precedence, and leave unreliable-clock comparisons unresolved. Do not impose this
order constraint on the native causal graph. Message payloads and model prompts use identified artifacts;
retaining a transcript does not imply every unobserved internal action was captured.

Native action requests do not grant themselves authority. The connection records intended/requested,
policy-permitted and actually performed/delivered states separately. A forbidden request can be preserved
while execution is refused. A system-facing delivery contains only the explicitly selected presentation
bundle; evaluator artifacts available to the observer are not automatically forwarded.

## 4. Completion, waiting and cancellation

Session, child action, submission and remote job each have their own completion rule and outcome scope.
Completed children do not imply completed parent discovery. Contact loss is not an established stop, and
an accepted job submission is not a delivered final graph. Parent completion may be inferred only under
its explicitly bound request rule and sufficient evidence.

Cancellation has request, acknowledgment and observed-stop evidence. An acknowledgment alone does not
prove the native process stopped; output can still arrive afterward. Preserve cancellation and later
outputs without rewriting their event order. The execution owner decides whether/when to request it.

## 5. Recovery and state invariants

- Retry after an ended episode creates a new attempt; the unchanged task may retain the same request.
- Checkpoint restart creates a new attempt and a checkpoint_continuation relation. Exact state load must
  be evidenced within its declared component scope, not inferred from a filename or provider label.
- Observer reconnect to the same established still-running job creates observations, not a new attempt.
- A new task/trial warmed from prior state uses a new request and warm_start relation, not automatically
  continuation of the old scientific task.
- Branches share predecessor/state ancestry but have distinct attempts. No independence claim follows.
- Ordinary pause/unpause within one evidenced native episode can retain the same attempt.
- New request parameters/policy scope create an explicitly related new request; do not overwrite old intent.

Recovery references cannot be self-predecessors or create ancestry cycles. The shared checkpoint must be
the actual declared/restored snapshot. Configuration, native code/model identities and RNG/cache/cursor/
optimizer/history evidence remain separate. exact_within_scope means the listed state components were
established, not that all hidden state in the world was restored. Unknown components limit stronger claims.

The restoration record can contradict a requested continuation: preserve both intended and observed state.
Changing scientific configuration or omitting relevant state cannot be hidden under a continuous-run label.
Unknown native occurrence identity cannot be resolved solely from folder names or equal output bytes.

## 6. Replay and accounting

Replay creates its own request/attempt and references original execution/transcript evidence. Initial
matching rule: exact specified request content and context bindings, with ordered occurrence identity where
the transcript distinguishes repeated requests. If a source route normalizes fields, its precise versioned
normalization procedure and excluded fields must be declared and checked. No undocumented fuzzy match.

The same response cannot be consumed as two distinct recorded occurrences unless a declared cache/reuse
policy permits that relation. Exhaustion/unmatched requests stop or yield unresolved response under the
bound rule; never silently fall back to fresh provider calls. A new native replay execution is not a new
model draw. Exact replay of the full system can remain unsupported even when graph artifacts are readable.

Accounting quantities identify actual units, measurement basis, time/event scope and aggregation membership.
Inclusive session totals cannot be added to their child totals. Overlapping wall durations cannot be summed
as elapsed time. Native queries, transmissions, fresh provider calls, cached/replayed responses and human
inputs are different quantities. Provider-reported amounts and estimates retain their sources and revision
history; missing values are unresolved.

Cumulative allowances remain bound to their request/session/recovery scope. Restart does not reset consumed
resources. A new policy does not erase prior use. State-load/cap records describe enforcement evidence; the
connection contract does not itself invent a scheduler, currency price or new spending permission.

## 7. Complete interaction/recovery walkthrough

Hypothetical request R permits one expert operation and checkpoint recovery within a cumulative cap.
Attempt A1 in session S sends action Q through endpoint E. Transmission T1 loses contact; T2 resends Q
with the same supported native idempotency key. A receipt establishes one native action occurrence.
Response P references Q; delivery D records the actual information exposed to A1. Absent receipt evidence,
native action multiplicity would remain unresolved.

A1 writes checkpoint C and is interrupted. A2 receives a new attempt ID with recovery link (A2,A1,C), a
state-load record, resolved configuration and remaining cumulative allowance reference. Its RNG component
is unknown, so continuity is partial even if optimizer restoration is observed. It returns graph G2.
A later observer reconnects to the same evidenced A2 native job and imports G2; it creates neither A3 nor
a new independent result. Missing expert-history bytes limit exact replay without automatically rejecting G2.

Expected acceptance cases: duplicate transport with proven/unproven idempotency; streamed conflicting replies;
concurrent actions with partial order; child completion with waiting parent; cancellation without stop;
checkpoint branch/partial restore; reconnect after lost contact; replay exhaustion; cumulative budget across
restart; inclusive totals and unknown usage. These are design cases, not executed tests.

## 8. Review status

This specification fills the detailed optional-behavior contract gap for the selected scope. New native
endpoint families, distributed coordination or richer state semantics require versioned extensions and
conformance checks. It does not promise universal orchestration. Public adoption remains W5-coordinated;
implementation remains subject to Uzair's go.

## Where we're going

Review these contracts with the exact API and legacy mapping, then decide the subsystem-1 design freeze.
Executable interaction/recovery checks belong to the gated implementation plan.
