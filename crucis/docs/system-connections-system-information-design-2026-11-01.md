# W2 system connections: Blocks 3 and 4, system identity and presented information (1 Nov 2026)

Tickets: DLV-08, DLV-09; neighbours DLV-10, ADV-01, DLV-06.
Status: design only. No implementation, schema adoption or historical result reinterpretation is made.
Predecessor: `system-connections-identity-request-design-2026-11-01.md`; capability coverage:
`system-connections-capability-map-2026-11-01.md`.

## 1. Decision accepted and current boundary

Uzair accepted a new attempt identity for a checkpoint restart, with an explicit continuation link. This
preserves the previous execution episode and identifies the restarted episode without claiming they are
independent trials. Reliable evidence still determines what state was actually restored. No implementation
go was given; the checkpoint decision does not adopt every proposed field or relationship name.

The qualified outcome distinctions and broader native-result preservation remain accepted directions.
The design below develops Blocks 3 and 4; its detailed organization remains proposed for discussion. W2-5
through W2-9 remain pending. Shared protocol and paper-contract changes still require W5 adoption.

## 2. The two questions and their relationship to earlier blocks

- Block 1 identifies the request, attempt and observation occurrences.
- Block 2 binds what operation/configuration/information was intended and how its response will be understood.
- **Block 3 establishes the native system/configuration that was requested and what the execution evidence
  identifies, separately from the machinery that observed and interpreted it.**
- **Block 4 establishes what information was permitted, presented and observed as accessed at the native boundary.**

The request points to intended bindings; the attempt points to observed bindings. A mismatch remains visible.
Do not rewrite a request after execution to match the configuration or input that happened to be used.
If a deliberate prospective change is made, it creates a new related request under the earlier design.

These are reusable semantic roles. No system-name-dependent field is needed to express the distinctions.

## 3. Block 3: distinguish the subject, its execution context and its interpreters

One algorithm label or wrapper-file hash cannot answer all of the identity questions. The proposed profile
has several roles, referenced only where applicable:

| Role | What should be identified | Why the distinction matters |
|---|---|---|
| Native audited system | Code/package/build, constituent algorithms/components, relevant dependencies and resolved scientific configuration. | Different settings or algorithmic wrappers can define different procedures even under the same name. |
| Models and native state | Checkpoints, provider/model identity and observed served version where available; relevant caches, reset and RNG/state references. | Code identity alone does not identify a learned or resumed system. |
| Native invocation/execution context | Entry point, resolved arguments, execution mode, container/runtime and relevant backend/environment evidence. | A registry pin or image label does not prove what a particular invocation used. |
| Observation and interpretation | Adapter, launcher/observer, parser, coordinate mapper and shared semantic code, each in its actual role. | A later interpretation change must not be mistaken for a new native execution or a different original model. |

The execution context and state details may be linked from Block 8. This block establishes their identity
roles rather than duplicating complete logs or resource accounting. Native internal stages do not become
separate top-level systems simply because they are visible; their component roles can be described.

### Requested, declared and observed are evidence positions

For a material identity claim, retain the value/reference, what it refers to, source/evidence, time/scope and
how it is known. Examples: requested in the plan; resolved by the launcher; reported by the native service;
observed in a manifest; inferred during historical reconstruction; unknown. A reported identifier is not
promoted to independently verified identity merely by placing it in a structured field.

If a requested version and an observed version differ, preserve both and the mismatch. A preflight check may
prevent an unintended launch under the execution policy, but discovering a mismatch afterward cannot create
retroactive authorization or silently revise the request. Do not substitute the requested version for a missing
observed one. Unknown identity narrows a reproducibility/comparability claim; it does not erase usable output.

An expected identity profile can be reused across requests; per-attempt observations refer to it and record
actual evidence or differences. A single combined fingerprint should not conceal which component changed.
Version/fingerprint canonicalization is still an implementation-design question.

### Configuration and defaults

Preserve explicit settings and resolved defaults that determine behavior, with the code/version under which
they were resolved. Native preprocessing, variable selection, statistical tests/scores, thresholds used by the
native system, model/prompt configuration, stopping rules, and initial-state policy can all be material.
The requirement is an inspectable relevant configuration, not a promise to observe every internal choice or
collect every installed package. A dependency/environment manifest can be referenced where available.

Separate the native scientific procedure from operational wrapping and later interpretation. If an adapter adds
graph repair, filtering, a different test or data imputation, that transformation is part of the effective
procedure and must be identified. It is not an invisible convenience. Transport serialization, system-native
preprocessing and evaluator projections should have distinct provenance roles even when implemented in one
existing codebase. The design does not authorize adding any of those transformations.

### Prompt and state boundaries

A prompt template and its generation logic belong to configuration identity. The rendered prompt actually
supplied belongs to presented information. A template reference alone cannot establish which variable names,
examples or context were sent. Conversely, the same template can be reused across different input arms.

A checkpoint identity belongs to the state/system profile; the fact that a particular attempt loaded it is
an observed binding. For a checkpoint restart, compare predecessor and successor code/configuration/state
observations and preserve unknown or altered RNG/optimizer/cache state. A new attempt does not by itself
prove exact continuation. Parser changes after the run belong only to the interpretation profile unless they
actually affected native execution at that time.

## 4. Block 4: describe the actual presented view and access history

The native system should receive only the view authorized for the experiment, while the auditor can retain
mapping and evaluation evidence separately. Block 4 describes the intended presentation and observed delivery;
it is not a copy of every artifact the auditor possesses.

| Information state | Meaning | What it does not establish |
|---|---|---|
| Intended | The request calls for this information/view. | That it was actually delivered. |
| Permitted or made available | The policy/interface allowed access to a specified resource. Actual availability can be separately observed. | That access happened, or that all potential access was monitored. |
| Presented/delivered | Evidence identifies the payload passed at a native interface boundary. | That the system accepted it or used it in its reasoning/computation. |
| Observed access | Evidence shows a file/read/callback/tool response or other access within the stated observation scope. | That this information caused a particular output. |
| Claimed or inferred use | Native declaration or auditor inference about use/influence. | A direct observation of causal dependence unless the evidence actually supports it. |

These are distinct observations, not necessarily a linear sequence that every system must expose. A black box
may expose delivery but no internal reads. A failed file read may show attempted access without delivery of
the file content. Preserve the evidence's actual meaning and observation scope.

### What a presented-information descriptor needs

| Part | Meaning |
|---|---|
| Information kind and semantics | Samples, sufficient statistics, names/context, graph/constraint, intervention metadata, image sequence, model/representation, callback or other declared type. |
| Artifact or endpoint identity | The delivered artifact/content reference, format/schema/version, or callable/service identity; actual known availability. |
| Variable and sampling schema | Stable variables, shown positions/names, types/units/categories, temporal/group/environment/partition identities and missingness semantics where relevant. |
| Presentation lineage | Source view and explicit transformations, including column/name mapping, selection, encoding, numerical conversion, prompt rendering or file materialization. |
| Delivery/access binding | Which attempt, native component, stage or interaction received/accessed it, when/order where known, and the evidence. |
| Origin and authorization | Provider/source, whether supplied knowledge or data, permitted information channel, and distinction from evaluator-only material. |
| Availability and limits | What was captured, declared, reconstructed, unobserved, inaccessible or unknown. |

The same structured mechanisms can describe a matrix, file, message, statistical callback or dynamic experiment
response. Payload-specific contracts still define their meaning. An arbitrary object with a data label is not
equivalent to a faithfully described dataset.

### Presented data are a view, not just a dataset label

Record the chain from source evidence through declared transformations to the actual native input. Relevant
details can include selected rows/columns, row order, masks, categorical encodings, numerical precision,
standardization, column permutation, label substitution, file path/header and rendered context.
The experiment defines authorized changes; adapters should not silently apply additional ones.

Byte identity and semantic/value identity are distinct. A CSV and an in-memory array can represent the intended
same values while having different byte encodings; a conversion can also change precision or missingness.
Record its rule/version and level of verification. Do not assert identical bytes or lossless conversion without
supporting evidence. Artifact IDs/hashes identify representations; variable/schema mappings connect their meaning.

For a name-swapped arm, retain the actual shown names and their mapping to stable variable identities, together
with the numerical view. For temporal data, ordinary independent-row shuffling cannot be assumed valid. Priors,
intervention masks, confidence keys and outputs referring to variables must follow the same mapping policy.
The native system sees its authorized shown view; evaluator mappings must not become extra system-facing input.

### Context, pretrained state and other channels

Neutral labels close a particular names channel. They do not establish that descriptive context, examples,
retrieved information, expert answers or learned priors are absent. Record each observable channel separately.
Pretrained/checkpoint identity belongs to Block 3; known training-data information can be linked, while unknown
pretraining content is not fabricated. Do not claim to observe a model's internal knowledge merely from weights
or a model name.

This richer information record can support later regime summaries. It does not revise the existing protocol's
K/none/D labels or retrospectively relabel historical findings. That change, if proposed, requires W5 review.

### Tools, files and adaptive information

A callback or tool descriptor states the operation and permitted source, including whether an expert/oracle
is deliberately part of the experiment. Actual questions and answers become linked events. An active system's
information boundary grows over its permitted interaction history; preserve that order rather than flattening
the final accumulated data into an apparently initial batch.

If the system can access a directory or endpoint beyond the explicitly passed payload, record the known
availability and the observation boundary. The absence of a read log is not evidence that no other resource
was available or used. This is information-accounting for faithful evaluation, not a claim that our record
enforces isolation by itself.

Intervention targets or reference truth retained only for scoring are evaluator-only evidence. They cannot
be passed to the system merely because they share a battery manifest. An authorized oracle control is a
distinct, explicit system-facing channel. Unknown-target interventions stay unknown in the delivered view.

## 5. Concrete cases

The cases below are hypothetical design exercises, not new executions or experimental findings.

| Case | Situation | Block 3 preserves | Block 4 preserves |
|---|---|---|---|
| P01 | A classical method runs on a numeric matrix. | Native code/test configuration, relevant resolved defaults/dependencies, invocation and interpreter identities. Irrelevant LLM fields need not exist. | Exact presented matrix/schema and any selection/permutation/conversion lineage. Delivery alone does not prove every column influenced the answer. |
| P02 | Identical numerical values are presented with swapped variable names. | Same native system/configuration if it actually stayed the same. | Different presented labels/header/prompt and mapping; evidence that the numeric view stayed fixed at the declared comparison level. Different arms remain distinct requests. |
| P03 | Labels are neutral, but a descriptive domain paragraph remains. | Prompt-template/provider/checkpoint configuration. | Both neutral labels and the actual remaining paragraph; no blanket claim that all knowledge was removed. |
| P04 | The plan pins one build but runtime evidence identifies another. | Intended and observed profiles, sources and mismatch. The original request remains unchanged. | What was actually delivered under that attempt; intended versus observed input differences if any. |
| P05 | A hosted model has an alias in the request and only a reported served identifier in the response. | Requested alias and reported value as separate claims; exact snapshot unknown if not evidenced. | Actual supplied prompt/messages and returned-call evidence within capture scope. This case asserts no behavior of a specific provider. |
| P06 | A shared graph parser is upgraded after a native run. | New interpretation identity, same native occurrence/profile to the extent evidenced. No claim the system reran. | Original input view remains historical; any newly reconstructed description is labeled as such. |
| P07 | A new attempt restores a checkpoint but RNG/cache restoration is unclear. | New attempt's actual code/configuration and loaded-state evidence; continuity limitation. | Information carried by restored state and any new payloads where observable; do not pretend a fresh information state. |
| P08 | A historical plan survives but the actual command/environment does not. | Planned identity distinguished from unknown actual identity; reconstruction evidence. | Intended input distinguished from a proven delivered payload; output existence does not prove every planned field was supplied. |
| P09 | A temporal/interventional input is permuted or re-encoded. | Transformation/adapter implementation identities and native test/settings. | Stable variable, lag/environment identities, actual values/masks and consistent intervention/constraint mappings. |
| P10 | An expert callback supplies a direction during a run. | Expert/provider identity and callback policy where available. | Exact question/context/answer, scope and order; native versus supplied provenance, not an inferred hidden use claim. |
| P11 | An active system requests another experiment with hidden targets. | Action-selection procedure/state and endpoint identities. | Requested action, returned samples and exactly the target information exposed; scoring truth remains outside the payload. |
| P12 | The wrapper applies an unplanned preprocessing operation. | The effective wrapper/procedure change and its identity; intended profile remains preserved. | Actual transformed view and lineage. Do not present the run as if the unmodified requested data were delivered. |
| P13 | An input file was passed and opened, but internal use is opaque. | System/invocation and observation instrumentation identities. | Separate evidence of presentation and read access; influence on a particular edge remains unestablished. |
| P14 | Data remain distributed across participants. | Coordinator/participant components and configuration/state identities to the extent observable. | Partition/schema and exchanged-message/update evidence; no invented centralized raw dataset or unrestricted verification claim. |

## 6. One connected continuation example

A request binds a hybrid discovery procedure and a prepared input view. An attempt receives a data file,
shown variable names and a rendered domain prompt, then is interrupted after writing a checkpoint. Uzair's
accepted rule gives the checkpoint restart a new attempt with a continuation link.

For the original attempt, Block 3 records the procedure/model/template configuration and observed execution
identity; Block 4 records the exact supplied file/schema/prompt and known accesses.
For the successor attempt, Block 3 records what actually executed and which state was loaded. Block 4 links
the preserved information history and any payload newly supplied after restart. The predecessor's checkpoint
state is not silently treated as empty memory. Missing state evidence remains a limitation.

If the successor unexpectedly uses a different procedure or receives altered data, preserve that mismatch
against the original request. Do not silently call it exact continuation of an unchanged experiment or issue
a retrospective replacement request. If the change was deliberately planned beforehand, it is a new related
request under the Block 2 design, with any warm-start/state lineage explicitly retained.

## 7. Minimum versus conditional detail

For Block 3, every record should identify the audited subject and interpreting producer as far as evidence
permits, distinguish intended/declared/observed/unknown identity, and link relevant configuration/state.
It need not populate irrelevant model, image or GPU fields for every system. Unknown historical details remain
unknown rather than being replaced with the current installed environment.

For Block 4, every operation should identify its intended and observed information boundary, the semantic type
and identity of presented inputs where known, and presentation/mapping provenance. Rich types, callback history,
partition schemas or state-carried information are conditional on the operation. A statement of unobserved
access is honest where internal visibility is absent; it does not automatically prevent output evaluation.

Shared core mechanisms can assign references, carry source/availability annotations, preserve transformations
and compare intended versus observed bindings. Adapters supply native conventions, invocation evidence and
available metadata. They should not each invent incompatible provenance, variable-mapping or identity policies.

## 8. Tradeoffs and acceptance obligations

| Choice | Recommended direction | Cost / failure avoided |
|---|---|---|
| One label versus role-separated identity | Distinguish subject, execution context/state and interpreters. | More references; avoids attributing a parser change to the native system or claiming one label fixes all versions. |
| Planned identity versus evidence-backed actual identity | Retain both and any mismatch. | Some unknowns remain; avoids false reproducibility based on a registry pin alone. |
| Input category versus actual presented view | Typed input/artifact/schema references with presentation lineage. | More metadata; avoids hiding changes to names, precision, masks, context or preprocessing. |
| Supplied versus used | Preserve delivery/access/claim/inference distinctions. | Internal use may remain unknown; avoids unjustified claims about information dependence. |
| Exhaustive environment dump versus relevant explicit profile | Relevant resolved configuration and available manifests, with limits. | Relevance needs a stated policy; avoids both arbitrary metadata collection and overclaiming complete identity. |

Before implementation, acceptance examples should establish that P01-P14 retain these distinctions, especially:

- Requested and observed configurations/inputs can disagree without overwriting either.
- Native execution identity survives later parser improvements; shared converter identity remains traceable.
- Defaults, checkpoints and conditional components are sourced or explicitly unknown rather than invented.
- Stable variable identities survive all corresponding name, position, mask and output mappings.
- Different information types and provider channels retain their meaning; a path/endpoint or digest alone
  does not claim delivery of known bytes or internal computational use.
- Dynamic and state-carried information are linked to the right attempt/session history and observation scope.
- Evaluator-only truth stays outside the native presentation except for an explicitly authorized oracle condition.
- A simple case remains simple; missing historical metadata narrows claims instead of fabricating failure or completeness.

No tests or implementation were created or executed. Existing protocol labels, identity hashes, result files,
certificates, paper pointers and shared code remain unchanged. The next discussion should settle the proposed
Block 3/4 boundaries before moving to Block 5's outcome-observation representation.
