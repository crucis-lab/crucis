# W2 system connections: Block 8, conditional relationships and limitations (1 Nov 2026)

Tickets: DLV-08, DLV-09; neighbours DLV-10, ADV-01, DLV-06.
Status: design discussion only. No implementation, public-contract adoption or result change is made.
Predecessor: `system-connections-artifact-evidence-design-2026-11-01.md`.

## 1. Accepted direction and scope

Uzair accepted Block 7's separation of artifact identity, location, observer/time-scoped availability and
integrity-check claims. Native occurrence/provenance, byte identity, interpretation and causal correctness
remain separate. Earlier accepted directions, including new attempt identity for checkpoint restarts, remain.

Block 8 is proposed here, not yet accepted merely by being written. It connects records to optional context
and limitations without turning unrelated details into mandatory fields for a simple operation. No
implementation go was given. W2-5 through W2-9 remain pending; shared contract changes still go through W5.

## 2. Purpose: typed cross-record context with one home for each detail

Block 8 answers which additional histories, state, accounting and limitations apply to this record and how
they are evidenced. It is an index of defined relationships, not an arbitrary notes field or a duplicate
copy of every earlier block.

- Identity/subject/configuration references remain owned by Blocks 1-3.
- Information presentation remains owned by Block 4.
- Outcome observations, gaps and assessments remain owned by Block 5.
- Object-to-object meaning and derivation remain owned by Block 6.
- Artifacts, locations and availability/integrity observations remain owned by Block 7.
- Block 8 links the relevant records into sessions, recovery/state histories, resource scopes and scoped
  limitations. Shared relation records can be referenced from several indexes rather than maintained as
  independent mutable copies.

The exact physical placement of records is still open. A simple stateless batch result may need few or no
conditional links. No session, transcript, checkpoint or limitation should be invented just to populate it.
Known non-applicability is distinct from unknown/not-recorded context.

## 3. Small common relationship descriptor

Illustrative requirements, not frozen field names:

| Part | What it establishes |
|---|---|
| Relationship identity/type/version | Which semantic relationship is being asserted, under which defined contract? |
| Source and target references | Which request, attempt, observation, object, artifact, session or accounting scope participates, and in what role? |
| Scope and direction | At which operation boundary, stage, variable/query/time domain or resource scope does it apply? |
| Evidence and basis | Is it a requested relation, native declaration, observed association, reconstruction or inference, with which supporting references? |
| Required parameters | Checkpoint restored, replay transcript, accounting scope, ordering link or procedure configuration needed to interpret this relation. |
| Time/order and status | Event/capture order when known; unresolved endpoints, disputed association or superseding evidence remain explicit. |

An ID/link is not proof that a relationship is true. Historical unresolved references can be retained with
diagnostics rather than fabricated matches. A documented extension can preserve a new relationship type,
but it cannot silently satisfy an existing type's semantics.

## 4. Conditional relationship families

| Family | Meaning and evidence to preserve | Misinterpretation to prevent |
|---|---|---|
| Session/hierarchy | Membership of scoped requests/steps/attempts in an identified workflow; parent/child roles and native boundaries. | A completed child submission is not completion of its parent discovery session. |
| Recovery | Retry-of versus continuation-from, reason and predecessor, with outcome evidence. | Retry success does not overwrite predecessor failure; checkpoint continuation is not an independent fresh trial. |
| State lineage | Checkpoint/state source, what was restored, producer and loading evidence; partial/unknown restoration and branches. | A checkpoint filename alone does not prove exact continuation, and forks are not one linear execution. |
| Planned replicates/groups | Experiment/trial membership, intended fresh-state/randomness policy and related request identities. | Same content does not merge trials; different IDs/seeds do not prove independence. |
| Events/interactions | Action/callback/tool/expert requests and responses, actors, correlation/order, allowed endpoints and actual deliveries. | Availability is not use; a missing response is not an invented abstention; an action response is not a final structure. |
| Replay/cache provenance | Source transcript/state/artifact, replay versus fresh-response events and matching/availability limits. | Reexecuted native code using recorded answers is not a fresh live model draw. |
| Resource accounting | Measurements/estimates linked to attempts/actions/sessions and explicit aggregation scopes. | Inclusive totals, parallel durations, retries and replay counters cannot be blindly added or equated. |
| Scoped limitations | References to particular gaps, unavailable capabilities/evidence or assumptions and the operations/claims they limit. | One missing trace does not automatically invalidate every object or evaluator. |

Detailed relationship families require their own contracts later. This index establishes common provenance,
addressing and boundary requirements so each adapter does not invent incompatible recovery/history policies.

## 5. Sessions and event ordering

A session may include several requests/attempts and state transitions. Internal system calls can be event
evidence without each becoming a top-level attempt. Explicitly scoped child operations can have their own
outcomes. Do not infer parent completion from a collection of completed children unless the parent's request
contract defines that condition.

For an interaction, distinguish who requested, permitted, selected and performed an action. Record which
response answers which request and what information it actually delivered. Use supported sequence/parent
relationships when clocks are uncertain. Preserve missing or ambiguous counterpart events; do not fabricate
an order or correlation based only on nearby timestamps.

Requests and responses can be linked to source artifacts rather than copied in full into the envelope.
Source observation and assessment logic remain in Block 5. The relationship record does not become a
universal workflow engine or an automatic authority to execute actions.

## 6. Recovery, continuation and branches

The accepted rule gives a checkpoint restart a new attempt ID with an explicit continuation link. That link
references predecessor attempt, exact state/checkpoint evidence, observed loading/configuration and limits
on established continuity. A reliable observer reconnecting to the same still-running native job does not
create a fresh native attempt.

Separate attempts can branch from the same checkpoint. Their provenance shares an ancestor; their outputs
must not be treated as independent fresh runs solely because they have separate IDs. A new warm-started
trial can have a new request and a state-source relation without claiming continuation of the original task.

A continuation history should not create impossible self-predecessors or logical ancestry loops. Its order
must be supported by the relation/state evidence, not merely clock sorting. These constraints concern record
lineage; they impose no acyclicity requirement on a native causal graph.

Selection of a final result or a scientific counting/resampling unit remains an explicit experiment/evaluation
policy. Neither grouping a chain nor separating its attempts silently chooses the denominator.

## 7. Resource accounting without hidden aggregation

A resource quantity/observation should identify at least its kind/unit, value or unknown state, subject and
measurement scope, source/basis, event/time interval and any revised estimate. Examples of kinds to describe
when relevant include wall duration, compute usage, native requests, new provider calls, replayed responses,
money with its price/currency basis, samples, interventions and human inputs. Not every operation exposes them.

Distinguish observed, provider-reported and estimated quantities. Keep their evidence rather than silently
substituting a current price or a convenient zero. Actual enforcement belongs to execution; Block 2 states
the allowed policy; this block links observed consumption and its scope.

Aggregation needs a declared rule and member scope. A session total that already includes its attempts cannot
be added to those attempts again. Overlapping wall durations cannot automatically be summed into session
elapsed time. Query counts, new provider calls and replay/cache hits describe different things. Revisions to
estimates preserve earlier values as observations.

A per-attempt allowance differs from a cumulative request/recovery-chain/session allowance. Restarting cannot
silently reset a cumulative cap. A new budget request does not erase earlier consumed resources. Missing
usage remains unknown instead of defaulting to zero. No new resource policy or spend authorization is created
by this identity/accounting design.

## 8. Limitations should identify the affected claim

A limitation references its subject, reason, supporting observation/evidence, affected operation/object/view
and the consequence justified by that scope. Example: missing request/response history may prevent exact
replay while leaving a captured graph interpretable. Unknown model snapshot can limit native reproducibility
without proving the graph is wrong. A failed confidence interpretation can prevent calibration while a graph
metric remains eligible under its own prerequisites.

Reuse existing gap/diagnostic/availability records instead of generating inconsistent copies in each block.
Evaluator-specific consequences are derived under evaluator prerequisites, not an adapter-wide all-invalid
flag. If the consequence of missing evidence is not established, state that uncertainty too.
Limitations are not scientific findings or additions to their verdict enum.

## 9. Connected example

This is a hypothetical design case, not a new execution or resource measurement.

A hybrid workflow starts an attempt, makes an expert query, produces a graph snapshot and writes a checkpoint,
then is interrupted. A new attempt continues from that checkpoint and returns a final graph. Later, another
observer imports the artifacts, but part of the original query history is unavailable.

Block 8 links:

- Each attempt to the appropriate request/session, preserving the predecessor interruption and successor outcome.
- The successor to the predecessor/checkpoint and actual restoration evidence, with continuity limits.
- The expert response to its question and actual information presentation, preserving missing history.
- The graph/stage/interpretation references already defined in Block 6 and evidence artifacts in Block 7.
- Resource observations to their actual attempts/session and a stated aggregation rule, avoiding overlapping totals.
- The missing-history limitation to exact replay, rather than automatically declaring the final graph unusable.
- The later import observation to the same evidenced native occurrences, rather than another native attempt.

This should remain one coherent history with typed references, not duplicate versions of each earlier block.

## 10. Acceptance examples and tradeoff

| Case | Situation | Required behavior |
|---|---|---|
| R01 | Stateless batch request | No invented session, checkpoint or transcript. |
| R02 | Failed attempt followed by retry | Separate attempts and explicit recovery relation; failure survives. |
| R03 | Checkpoint restart | New attempt and state-backed continuation link. |
| R04 | Two branches from one checkpoint | Shared state ancestor, separate branches; no invented independence or linear history. |
| R05 | Remote reconnect | Native occurrence preserved when evidenced; new observations are not new runs. |
| R06 | Completed child action, waiting parent | Scope-specific completion; parent rule remains authoritative for its completion. |
| R07 | Missing expert response event | Gap/unknown correlation preserved, not fabricated response. |
| R08 | Recorded-response replay | New replay execution distinguished from original execution and fresh model responses. |
| R09 | Inclusive session/attempt resource totals | No double counting; explicit scope and rule. |
| R10 | Cumulative cap across continuation | Prior consumption retained; restart does not reset policy. |
| R11 | Missing trace but known graph | Scoped replay limitation; graph eligibility decided by its own prerequisites. |
| R12 | Shared object/derivation relations | One sourced relationship meaning, referenced without contradictory duplicate ownership. |

The richer index costs typed links and validation, but avoids forcing every workflow into one flat run.
The simpler alternative is arbitrary notes for retries/sessions/state, which is inexpensive to write and
expensive to interpret consistently. Reuse common relation patterns and omit irrelevant families for simple
systems; do not add a universal event/workflow framework just to support a batch result.

No tests or implementation were written or run. Only this new design document was created. Existing code,
protocol, results, certificates, paper/tracker/site files and green-gate state are unchanged. A separate
dated rebase summarizes the completed walkthrough, remaining work and boundary of final design review.
