# W2 system connections: Blocks 1 and 2, identity and requests (1 Nov 2026)

Tickets: DLV-08, DLV-09; neighbours DLV-10, ADV-01, DLV-06.
Status: design only. No implementation or public contract change is made.
Prior discussion: `system-connections-outcome-cases-2026-11-01.md` and
`system-connections-result-record-design-2026-11-01.md`.

## 1. Accepted direction and remaining decisions

Uzair accepted the qualified outcome definitions discussed previously: execution completion, response delivery,
requested-response fulfillment, scoped evidence capture, faithful interpretation, and procedure-specific
evaluation eligibility. Native causal correctness remains separate, as do finality, fulfillment and abstention.
Exact field names and protocol enums were not adopted. Broader native-result preservation was already accepted.

This document proposes identities, request boundaries and worked cases for Blocks 1 and 2. The identity
granularity and relationship vocabulary below have not yet been accepted by Uzair. No implementation go was
given. W2-5 through W2-9 remain pending; shared protocol changes still go through W5.

## 2. Three primary identities, plus conditional relationships

| Identity | Meaning | What it must not be confused with |
|---|---|---|
| Request | A particular declared operation/question and its agreed scope, response and execution policy. | An algorithm name, reusable task template, dataset ID, or hash of a similar request. |
| Attempt | One bounded execution attempt to carry out that request, with its own launch/start/termination evidence and resolved execution conditions. | A whole collection of retries, every internal tool call, or an observer reconnecting to a still-running native job. |
| Observation record | A particular capture, import, interpretation or outcome observation about the request/attempt/artifacts. | The original native execution or its output bytes. |

These are conceptual identities, not mandatory independent files. Small cases can present them together.
Repeated observation/import never proves a fresh native execution occurred. Conversely, two executions that
return identical bytes are still distinct occurrences.

An attempt may be identified when planned/initiated and then never reach native start. Its ID does not itself
prove execution. A preflight rejection can leave a not-started attempt or a request-level rejection, depending
on the chosen orchestration boundary; neither is a native-system crash. The final scheduling convention remains
an execution-subsystem detail.

Conditional identities include a parent session, a native provider job/session identifier, checkpoint/state
objects, output objects and evidence artifacts. Include them when the system/operation needs them. A flat batch
operation should not need an invented session merely to fit the common record.

### One request, attempts and observations

Illustrative IDs below are labels in an example, not an ID-generation scheme:

    Request R
      Attempt A: starts, writes checkpoint, then is interrupted
        Observation record O: captures that interruption and checkpoint
      Attempt B: continues A from that checkpoint, then completes
        Observation record P: captures B's output
        Observation record Q: later imports the same output on another host

R identifies the original requested operation. A and B are different execution episodes connected by a
continuation relation. Q is a new import observation of B, not a third native attempt.

## 3. Request identity and specification equality

A request ID names an occurrence of an intended task, not a deduplication key computed solely from content.
Two separately requested trials can have identical task specifications and different request IDs. A content
fingerprint can establish equality of a precisely defined specification; it cannot establish that two events
are the same occurrence or that two executions are independent.

Proposed rule: use one request across recovery attempts intended to fulfill that same declared task. A planned
new replicate is a new request occurrence, linked to the same experiment/template or replicate group where
appropriate. Its specification may be identical. This distinguishes a repeated scientific trial from recovery
of an earlier request, without hiding either execution.

If randomness is bound to a specific seed in the request, changing it changes that specification. If the request
authorizes a defined seed/draw policy, attempts can resolve it under that policy; record the actual seed/state
and its source per attempt. Same request does not imply identical random draws. Distinct seeds do not by
themselves prove statistical independence. No new policy is retroactively imposed on the old recorded audits.

## 4. Attempt identity: retry, resume and reconnect

Proposed granularity: a new execution launch/episode across the audited operation boundary gets a new attempt
ID, even when it restores state. Internal worker processes, statistical tests and model/tool calls do not each
become another top-level attempt; they are internal evidence or explicitly scoped child operations.

| Situation | Identity rule proposed | Relationship/evidence |
|---|---|---|
| Fresh retry after failure | Same request; new attempt. | retry-of relation; restart/reset policy, reason and resolved conditions. |
| Restart from a checkpoint after the earlier episode ended | Same request when scope/policy are unchanged; new attempt. | continues-from relation, checkpoint artifact and restored-state evidence. |
| Pause/unpause inside the same continuing native execution | Same request and attempt, when continuity is evidenced. | State/lifecycle events showing the same native episode continues. |
| Client disconnect/reconnect while a remote job continues | Same request and native attempt when matched by reliable evidence. | New observation/access record; scoped native job identity. |
| Two branches launched from one checkpoint | New attempts with explicit branch/state lineage; distinct requests if they are new trials/questions. | forked-from-state links; they are not independent fresh starts merely because IDs differ. |
| Another planned trial | New request occurrence and attempt. | replicate-group or replicate-of-request link, plus intended seed/reset policy. |
| Replay that reexecutes the system with recorded answers | New replay request and attempt. | source execution/transcript links and replay mode; not an independent live model draw. |
| Reading/parsing old outputs only | Observation/import/interpretation record; no new native attempt. | Source-run/artifact links, parser identity and import time. |

An import can involve CPU work without being a new causal-discovery execution. A response replay can execute
native code without being a fresh stochastic model run. Preserve those distinctions in later accounting.

The strongest alternative is to keep one logical attempt ID across checkpoint restarts and introduce a
separate execution-segment ID for each episode. That is also defensible if every interruption/segment is
preserved. It gives users a continuous logical-run identity, but adds another mandatory distinction whenever
a restart occurs. The recommendation here uses new attempt IDs with explicit continuation links, so a segment
type is not required for the basic restart case. A continuation-chain view can supply the logical-run grouping.
Whichever design is chosen, evaluation must name its unit; ID granularity cannot choose denominators implicitly.

### What qualifies as continuation

Checkpoint existence alone is insufficient. A continuation relationship should identify:

- The predecessor attempt and the exact checkpoint/snapshot restored, with artifact availability and identity.
- The native code/configuration used before and after, and any observed changes.
- The state that the restore actually carries: model/optimizer state, RNG state, caches, data cursor, action
  history or other state relevant to this system. Unknown parts remain unknown.
- The unchanged request and its allowed continuation policy, and the new episode's resource allowance.

Record a provider's claimed continuation separately from verified/observed state continuity. Partial or
unverifiable restoration must not be advertised as exact resumption. Do not erase the claim; retain it with
its evidence and limitations. If evidence cannot distinguish a resume from a fresh restart, state that
uncertainty rather than inventing a confident relationship.

Warming a new run with a previous fitted model is an initial-condition choice for a new task/trial, not
automatically continuation of the previous attempt. Two concurrent branches from the same state must not
be collapsed into a single linear continuation history.

### Lost acknowledgments and transport retries

Retrying a network submission may or may not launch another native execution. Record the actual transport
events, provider identifiers and any supported duplicate-suppression evidence. Do not infer one native attempt
per HTTP call or silently merge two possible jobs. If native occurrence identity is unresolved, preserve that
uncertainty and the source events. The connection layer cannot manufacture an exactly-once execution guarantee.

## 5. Observation-record identity, versions and time

Proposed rule: persisted observation records are immutable evidence snapshots. A later observation or corrected
interpretation gets a new record identity and a typed relationship to earlier records; it does not overwrite
the evidence available at the earlier time. A read-only verification need not publish another record merely
because it reads an artifact. Deliberately persisted repeated imports can reuse the same artifact reference
while keeping distinct ingestion observations where useful.

Block 1 needs at least:

- The observation record ID and envelope/schema version.
- Its kind and producer: execution observer, artifact importer, interpreter or other declared component, with
  relevant producer/version identity linked to Block 3.
- The subject request/attempt/source references when known, and explicit unresolved identity otherwise.
- Creation/observation/import time, source event time when known, and origin/evidence for reported timestamps.
- Relationships to a preceding snapshot, interpretation, source record or correction when applicable.

Keep the envelope version, request/response contract version, native system version and interpretation version
separate. Updating a schema does not mean the native system reran or changed version. A migrated representation
must retain its source and transformation lineage.

Original execution time, original capture time, later import time and later interpretation time are different.
An unknown original time is not filled with today's date. Preserve source timezone/precision or uncertainty.
Do not infer causal order solely by sorting unreliable wall clocks; explicit sequence/parent/checkpoint links
provide other ordering evidence.

Paths, timestamps and native labels are useful evidence but insufficient universal identity schemes. Scope
native IDs by source/service/namespace and relevant occurrence evidence. A content digest identifies bytes or
a defined canonical specification; it does not identify a unique execution. The exact ID format and hash
canonicalization policy remain implementation-design choices.

Identity assignment and reference handling should be reusable core/coordinator responsibilities. Adapters
provide native identifiers, invocation boundaries, state references and evidence; they should not each invent
their own unrelated request/attempt naming or deduplication policy. Historical importers preserve source IDs
and record supported associations rather than inferring occurrence identity from a folder name alone.

## 6. Historical imports and uncertain original identity

### Import with an established native run

An old run identifier and reliable manifest identify the original request/attempt. A new import record links
to them and the observed artifacts, records its import/interpretation versions, and leaves the original run's
date and outcomes unchanged. Reimporting the same evidence does not add another run to completion denominators.
A better parser produces a new interpretation linked to the same native evidence.

### Import with an unknown original run

An artifact's presence alone may not identify the original execution or even establish how it was produced.
Assign a local source/artifact handle if needed; leave the original request/attempt identity unresolved.
Do not fabricate a historical execution simply to satisfy a required foreign key. The import itself still
has an identifiable observation record and evidence provenance. Native declarations, externally reported
digests and observed bytes remain distinguishable.

Identical outputs are not enough to merge unknown native occurrences. Later evidence may establish that two
imports concern the same original run, or disprove an earlier association. Add a sourced identity-resolution
or correction record; keep the earlier observation and its uncertainty. Selection/deduplication in an analysis
must state how it handles unresolved identity rather than inventing an execution count.

### Reconstructing the historical request

Identify the origin of each reconstructed fact: original plan, runtime metadata, native output, later inference
or unknown. An archived plan may express intent without proving the runtime used exactly that configuration.
Preserve that discrepancy. Improved reconstruction changes our evidence/description of the historical request;
it does not retrospectively issue a new native request or prove a pre-run contract existed.

Observation records can supply partial, versioned descriptions of the same established historical identity.
New knowledge is an evidence update. Deliberately changing a prospective request is a different event (section 8).

## 7. Block 2: the minimum request contract

The contract establishes what outcome words mean. Common defaults can be supplied by a referenced versioned
contract/template; the resolved request binds them to this occurrence. The examples here are hypothetical.

| Part | Required question | Example |
|---|---|---|
| Operation and boundary | What operation is being asked to finish? | Discover a structure; submit a job; update a model; choose an action; import an artifact. These have different boundaries. |
| Task and scope | Which variable universe, target, item/arm/query and relation meanings are in scope? | Full structure over the supplied schema versus a local neighborhood around a named target. |
| Bound subject and inputs | Which system/configuration and prepared information are requested? | References to Block 3's system/configuration and Block 4's input/schema manifest; evaluator-only truth is separate. |
| Response contract | Which types, coverage and deliverables are required/optional? | Final partial-direction graph required; confidence optional; query-specific abstention permitted. |
| Completion rule | What evidence establishes the declared completion boundary? | Native terminal response plus required artifacts; or completion of a bounded update. Exit code alone need not establish fulfillment. |
| Execution and state policy | Which mode, initial-state/reset/continuation and randomness policy is intended? | Fresh run versus permitted checkpoint continuation versus recorded-response replay. Actual resolved conditions are recorded per attempt. |
| Resources and interactions | Which resources/actions are allowed, at which scope, with what stopping semantics? | Cumulative request allowance versus per-attempt limit; external cap versus requested bounded operation; available action endpoints. |
| Origin and contract version | Who issued the request, when, and how is this description evidenced? | Prospective frozen request versus reconstructed historical intent with explicitly unknown parts. |

Block 2 references the native subject/configuration and presented input records rather than duplicating all
their contents. It specifies the requested binding; later evidence records what actually ran and was supplied.
Differences remain visible rather than rewriting the request to match execution.

## 8. Prospective request immutability and allowed variation

Before a new operation starts, freeze its intended scientific scope, input/configuration bindings, response
contract, mode/state/randomness policy and resource rules. A semantic change creates a new request ID linked
to the earlier request with the change and reason. Optional display labels can be added as metadata observations
without pretending the task itself changed. Exact representation of annotations remains open.

| Change after an attempt | Same request or new request? |
|---|---|
| Fresh retry allowed by the existing recovery policy, unchanged task and inputs | Same request, new attempt; all prior evidence and resource charges remain. |
| Restoring a checkpoint generated by this task under its existing continuation policy | Same request, new attempt when native execution restarts; restored-state evidence is required. |
| Different data, names arm, algorithm configuration, required output family or fixed seed | New request, linked to the earlier one if related. |
| New random draw under the request's predeclared draw policy | Same request may be valid for recovery; record the draw and why it occurred. A separately planned replicate is still a new request occurrence. |
| Enlarged cumulative budget beyond the frozen allowance | New amended request/policy binding; preserve prior stopping and cumulative resource history. |
| Another action/data update permitted by an adaptive/online session contract | A linked child operation/event under the existing parent policy; does not silently redefine the parent task. |
| Better parser or additional observation of the same native artifact | New interpretation/observation record; no new native execution or retrospective task change. |

Resource scope must be explicit. A per-attempt limit, a cumulative recovery-chain limit and a session limit
are different policies. Continuing or retrying must not silently reset a cumulative limit. A budget extension
may authorize more work only when separately permitted; an identity design never authorizes spend.
No historical count/status rule is changed by choosing a conceptual identity granularity here.

## 9. Worked identity cases

| Case | Situation | Proposed identity behavior |
|---|---|---|
| I01 | Ordinary fresh operation | One request, one attempt, observed records linked to each; separate object/artifact IDs as needed. |
| I02 | Failure followed by a fresh retry | Same request, new attempt, retry-of relation; failure retained. |
| I03 | Interrupted episode followed by checkpoint restart | Same unchanged request, new attempt, continues-from relation and exact state evidence. |
| I04 | In-process pause/unpause | Same native attempt when continuity is established; new lifecycle observations. |
| I05 | Reconnect to the same running remote job | Same native attempt; new transport/observation evidence, not a newly discovered graph run. |
| I06 | Restart with partial or unverified state | Preserve claimed continuation and its uncertainty; do not assert exact continuity from the checkpoint filename alone. |
| I07 | Two branches from one checkpoint | Separate attempts with common state lineage; new requests where they are distinct trials/questions. |
| I08 | Another intended replicate with the same specification | New request occurrence and attempt; same-specification evidence and replicate grouping do not imply event identity or independence. |
| I09 | Same run imported on another host | New import observation; known original request/attempt reused, no added native run. |
| I10 | Same native bytes interpreted by a better parser | New interpretation/derivation record and parser identity; same evidence/native occurrence. |
| I11 | An old graph file with unknown origin | Identifiable imported source/artifact; original request/attempt unresolved. |
| I12 | Two identical graph files from unknown sources | Preserve both provenance claims; identical bytes alone do not establish one execution. |
| I13 | An archived plan disagrees with runtime evidence | Keep planned request and observed binding separately, with sources; no silent correction of either. |
| I14 | Larger budget or changed configuration after a cap | New related request for the changed policy/configuration; preserve original cap and cost history. |
| I15 | Submission resent after its acknowledgment was lost | Preserve transport and provider evidence; native duplicate/execution identity can be unknown. |
| I16 | Recorded model-response replay | New replay request/attempt linked to the source transcript; no claim of a new live model sample. |

The unit of completion, resource aggregation and uncertainty resampling is a later explicit analysis policy.
Different IDs are not a license to count resumed segments as independent trials. A continuation chain's total
and its per-episode costs need stated accounting scopes. A failed episode followed by completion of a related
task must not erase either event. These rules preserve evidence for several defensible analyses without
silently selecting one in the adapter.

## 10. Current package comparison and acceptance obligations

The inspected current RunRecord identifies system/item/arm and stores some run IDs and replicates in notes.
Causal-Copilot's reader selects the latest stored run as its record and retains earlier ones as replicates;
the existing protocol counts them under its established rules. The proposal supplies more explicit future
identity/relationship semantics; it does not reinterpret those historical records or change their gates.
`audit/systems/_probe.py` and `audit/systems/causal_copilot.py` remain untouched.

Before implementation, acceptance examples should demonstrate:

- Retries, checkpoint restarts, observer reconnects, replicas, replay and imports remain distinguishable.
- Identical specification/content does not merge occurrences; distinct observation IDs do not inflate native
  execution counts. Unresolved original identity can be represented without a fake run.
- Requests bind outcome scope and completion rules before prospective execution; recovery does not change
  those rules, configuration or cumulative allowances silently.
- Historical request reconstruction and later identity resolution retain their evidence and chronology.
- Continuation relationships identify actual restored state and uncertainty; branches are not forced into a
  linear chain. Lost acknowledgments do not acquire an invented exactly-once guarantee.
- Every interpretation records its producer/version and source while preserving native occurrence identity.
- Record, request/response contract, system and interpretation versions remain separate.

No tests or code were written or run. The next design discussion should settle the proposed identity
granularity and the request's immutable versus per-attempt-resolved information before moving to Blocks 3 and 4.
