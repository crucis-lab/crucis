# Subsystem 2: conditions and information policy

Tickets: DLV-08, DLV-09; related DLV-10, DLV-06/07 and ADV-01.
Date: 2 Nov 2026, America/Los_Angeles.
Status: proposed design. Uzair accepted proceeding from reference/response semantics
to conditions and information policy. No particular detailed policy, serializer,
implementation, paid run or public protocol change is approved by this note.

Predecessors: [reference/response semantics](subsystem2-reference-response-semantics-2026-11-02.md),
[task/reference design](subsystem2-task-reference-design-2026-11-02.md),
[case obligations](subsystem2-case-membership-minimum-2026-11-02.md).
Inspected footing: `audit/protocol/regimes.py`, `audit/core/harness.py`,
`audit/controls/transforms.py`, `audit/connections/{schema,history}.py`,
and the [S1 system/information design](system-connections-system-information-design-2026-11-01.md).
All experiments and evidence situations below are illustrative. No native run,
scientific effect, information isolation or new validation result is established.

## 1. Responsibility and ownership

A condition defines the scientific treatment: what changes, what remains fixed,
which information/actions are permitted and which question the contrast can answer.
A concrete per-system binding describes how that common condition maps to supported
native inputs, modes and channels. Subsequent observations record what happened.
These roles need not be separate files and must not duplicate S1 request records.

S2 defines intent, prerequisites and scientific comparability. S1 supplies domains,
presentations, action/response and sourced observation records. S3 will implement
authorized materialization/execution/enforcement. S4 measures the declared contrast;
S5 evaluates findings. Recording a policy is not proof of its enforcement or a
permission to execute. Adapter declarations do not establish native behavior.

Generic core rules should describe typed channels, subjects, information scopes,
derivations, permissions and evidence. Native bindings supply faithful translation.
They must not silently disable native behavior or decide scientific independence,
reference access or causal attribution based on a system name.

## 2. Proposed minimum condition obligations

| ID | Obligation | Purpose |
|---|---|---|
| I01 | Stable identity/exact version, authoring/commitment timing, parent/contrast links and known gaps | Preserve intended treatment and amendments rather than rewriting it after results |
| I02 | Scientific purpose, applicable cases/tasks and the factor levels being varied | Distinguish names, layout, knowledge, data availability, backend and state manipulations |
| I03 | Declared fixed properties and equality/invariant meanings with checkable procedure references | Prevent a names condition from quietly changing samples, task, order or reference alignment |
| I04 | Typed input/channel inventory with recipients, content/source scopes, boundary/transport and applicable disclosure policy | Account for prompts, metadata, callbacks and state as well as the nominal data file |
| I05 | Allowed, denied, required or unresolved information/actions within explicit scope, including evaluator-only material | Prevent an unspecified channel from silently inheriting access to answers or hidden metadata |
| I06 | Exact presentation/transform recipes, domain mappings and selected native-mode bindings | Bind scientific intent to actual supported representations without inventing native capabilities |
| I07 | State/reset/cache/history policy and randomization/resource rule references | Prevent earlier conditions or retries from invisibly changing available information |
| I08 | Prerequisites and enforcement/observation requirements, with explicit support limits | Distinguish policy intent, declared support and demonstrated isolation |
| I09 | Delivery/access/use evidence requirements and its expected capture/interpretation scope | Avoid equating file existence, delivery or a changed answer with observed causal use |
| I10 | Planned handling of unavailable, contradictory, nonconforming or unverified conditions and analysis-population links | Preserve denominators and prevent result-driven relabeling/exclusion |

Exact vocabulary is not frozen. Channel/action families may have scoped extensions;
unsupported semantics withhold the affected readiness claim. Optional unrelated
families require no invented null records. Required unknowns have scoped gaps.

## 3. Information channels are broader than file arguments

| Channel family | Examples and necessary boundaries |
|---|---|
| Empirical observations/statistics | Raw values, masks, images, trajectories, correlation matrices, sample counts and CI answers; bind role/domain and actual availability |
| Experiment/environment information | Intervention targets and assignments, context/group labels, time coordinates and action outcomes; hidden/unknown targets are not implicitly revealed |
| Identifiers and layout | Names, variable IDs, ordering, paths, filenames, table/schema labels, object keys and source/scenario identifiers; a stable internal ID may itself contain a denied semantic clue |
| Natural-language/task context | Instructions, descriptions, units, examples and error/help messages; task-defining meaning cannot be removed without acknowledging a changed task |
| Knowledge/restrictions | Expert claims, known orders, prohibited edges, mechanistic assumptions and supplied priors; bind proposition type, source, uncertainty and coverage |
| Retrieval and external interaction | Web/document search, databases, human/LLM experts, simulators, CI services and distributed messages; distinguish permission, service source/version and actual responses |
| Persistent/pretrained state | Model/checkpoint identity, fitted preprocessing, memory, sessions, caches and prior messages; record known training/exposure limits without claiming to erase learned knowledge |
| Feedback and evaluation material | Reference graphs, evaluator mappings, correctness feedback, metric/finding reports and earlier-condition outcomes; evaluator-side by default unless an explicit condition permits a bounded channel |

This inventory is extensible. A flat data/names flag cannot establish all these
boundaries. A scoped public descriptor can reference restricted evidence without
publishing its contents. No real sealed material, credentials or secret state is
read or copied during design.

An information policy is about the actual scientific question. Predictive structure
in legitimately supplied numerical data is not automatically leakage. A benchmark
layout shortcut may be allowed input whose influence is being audited. Unauthorized
reference access is a different event. Preserve these distinctions in findings.

## 4. Intended information versus established observations

Record the following separately where applicable:

1. Permitted: the condition authorizes the scoped information/action.
2. Intended/offered: the binding specifies what should be supplied or made available.
3. Reachable/available: evidence establishes access capability at a boundary/time.
4. Delivered: evidence establishes transmission/presentation of particular content.
5. Accessed: evidence establishes a read/query or another scoped access event.
6. Used/influential: a supported source observation or analysis establishes the
   particular use/influence claim, with its own scope and assumptions.

These are not a universal sequence: a reachable public source may never be queried;
a response may be delivered without evidence that a downstream step read it.
Record source declarations, direct observations, reconstructions and derived
assessments with their separate bases. Missing logs do not establish non-use.

A controlled change in supplied information can support its declared output-effect
contrast when the design/analysis assumptions hold. It does not alone identify
which native component read it or establish a mediation/provenance percentage.
A null output contrast likewise does not prove that information was ignored.
Such stronger claims need appropriate later designs/evidence, not a renamed field.

## 5. Names: define the exact intervention

Illustrative source case: fixed samples over rainfall R, sprinkler S and wetness W.
The names-only input boundary is distinct from whether an audited system accepts
these numerical samples. Two useful designs ask different questions:

- Labels-only: change specified variable-label fields while retaining the declared
  numerical values, rows/masks, ordering, context, task, native version/model,
  reference bindings and other channels. The contrast concerns those label fields
  in that retained information environment.
- Broader semantic masking: neutralize specified labels plus selected descriptive
  context/metadata/path identifiers. This is a multi-channel intervention; report
  the actual package and any task changes rather than calling it a pure label effect.

| Condition | Changed input | Meaning and required checks |
|---|---|---|
| Real labels | R/S/W receive their intended semantic names | Freeze the actual source names/context and map to canonical identities |
| Neutral labels | R/S/W receive declared generic labels | Verify the target fields changed; retained descriptions may still provide semantic knowledge |
| Swapped labels | Each variable receives another declared variable's label | Keep values and canonical variable identity fixed; preserve the mapping evaluator-side and verify it is not delivered through a denied side channel |

Changes in token length, familiarity, syntax or native parsing can accompany label
changes. State the actual intervention and its limits; do not claim isolation of
abstract semantic knowledge without a design supporting that narrower mechanism.
Keep column permutation as a separate controlled factor unless a joint condition
explicitly varies it. Changed units/descriptions or task targets require declared
additional changes. Reference alignment is checked after mapping to the canonical
domain, not silently redefined to agree with the misleading labels.

If descriptions still say "R measures rainfall", neutral names do not establish
absence of domain context. A labels-only comparison can still be valid for its
bounded question. A broader masking study must account for such fields and explain
whether its target task remains meaningfully the same. Pretrained knowledge,
recognizable values and prior public exposure are separate limitations; renaming
does not prove an information-free system.

A names-only native method receives only its supported information under the
declared binding. Do not pretend raw data were consumed or infer data reliance
from removing numeric inputs it never accepted. Its masked condition may be useful
as a knowledge-reduced diagnostic with the corresponding scope, not as a data-only
performance result. Unsupported bindings remain explicit eligibility gaps.

## 6. Knowledge controls: none, oracle and wrong supplier

Bind the knowledge object type and scientific role: direct-edge assertions, allowed
orientations, a partial order, a chosen topological sequence or a probabilistic
prior are not interchangeable. Specify candidate/domain coverage, uncertainty,
source generation and how the native interface interprets it.

| Condition | Meaning | Necessary boundary |
|---|---|---|
| No added supplier | Withhold the declared external knowledge channel | Does not erase names, model priors, context or previously loaded memory |
| Oracle supplier | Supply reference-derived information under an explicitly permitted condition | Record exact disclosure content and derivation, preserve unused evaluator material, and label the changed information regime |
| Wrong supplier | Supply a defined corrupted knowledge object with justified error labels | Specify corruption procedure/strength, validity constraints and whether inconsistency is intentional |

A true topological sequence is one valid arrangement, not a list of unique direct
causal edges or proof of ancestry between every ordered pair. Its arbitrary choices
and generation/tie-breaking procedure can matter; preserve the actual disclosed
object and derivation. If the task requires only necessary precedence constraints,
a complete chosen sequence supplies additional ordering choices and must be labeled.

Corrupting knowledge can produce an inconsistent/cyclic constraint set. Distinguish
plausible-but-wrong compatible knowledge from deliberately conflicting knowledge.
A native rejection can answer the conflict-robustness question without establishing
the same effect as a valid mistaken prior. Do not silently repair the supplied object,
replace a native interface or call uncertain real-world consensus objectively wrong
without a supporting reference basis.

All variants use matched, declared presentation recipes and native setup where
the intended contrast requires them. If prompts, budgets or models change too,
record the joint change. Withholding a native retrieval stage or supplier changes
the evaluated mode when that stage is part of the original system. The original
full-mode baseline and a restricted-mode control must remain separately identified.

## 7. Interactive actions, resources and feedback

A static condition can enumerate supplied inputs. An interactive condition defines
an allowed information/action policy: endpoint/proposition semantics, permitted
arguments, recipient, response contract, authority boundaries, resource/stopping
rules and episode/state constraints. Actual queries/actions/responses are later
S1/S3 evidence. A declaration does not authorize calls or spend.

Two policies may obtain different evidence under the same allowed action budget.
Record the declared comparison estimand: fixed-transcript behavior, equal-budget
adaptive performance, a native-mode study or another explicitly defined question.
Equal budgets are not identical realized inputs. Fixed transcript replay and a
fresh interactive episode remain distinct, and a changed request does not inherit
a previous response's validity merely because its cost would be lower.

Evaluator references and scores remain outside the native information boundary
unless a declared oracle/feedback condition permits particular content. Feedback
after each action, across arms or during development changes the available state
and possibly later selection. Bind permitted feedback/adaptation before drawing
confirmatory claims; preserve original exposure, including failed attempts.

## 8. State, reset and cross-condition contamination

Specify the actual scope of session/memory/cache/checkpoint/preprocessing state.
Options may include independently initialized attempts, a pinned shared initial
state or deliberate continuation. They answer different questions. A chosen reset
policy needs evidence of the components actually reset; a fresh request ID or
new process does not prove all relevant external/provider state was cleared.

Serving caches, native result caches, fitted transformations and conversation
memory can affect the experiment differently. Describe content, isolation/keying,
reuse policy and known gaps as relevant. Do not claim every cache is harmful or
that disabling an available cache is scientifically neutral. A private evaluator
mapping or oracle response must not be carried into an ostensibly unexposed arm.

Bind randomness by role. The same seed does not prove identical remote model draws;
matched randomization and independent scientific repeats are distinct design choices.
Ordering/counterbalancing and carryover controls need their later detailed design.
When isolation is unestablished, preserve that limit instead of asserting that
every arm started with identical knowledge or that contamination certainly occurred.

## 9. Readiness, violations and analysis populations

Before a prospective run, establish each required binding and the level of
enforcement/observation the scientific claim needs. Where permitted information
cannot be faithfully supplied, withheld or observed, report the scoped readiness
gap or explicitly amend the question/mode before proceeding. Do not silently drop
native stages, permit an extra source or fabricate an execution failure.

If actual delivery/access contradicts the policy, retain the original intended
condition and the observed evidence. Do not relabel the arm after seeing results
to make it compliant. Mark the affected comparison/applicability limitation and
apply the declared missingness/nonconformance policy. Descriptive measurements
that remain meaningful may be reported at their honest scope, with the intended
population, completion and conformance accounting preserved.

An unobserved channel is not automatically compliant or violated. A policy with no
enforcement evidence is not a proven isolated environment. Any amended interpretation
keeps its timing, rationale and source. Metric-specific exclusions need their
predeclared or honestly retrospective analysis policy; no favorable-only filtering.

## 10. Current code footing and exact limits

- `audit/protocol/regimes.py` computes offered-channel categories using adapter
  declarations and name-arm conventions. It preserves within-(regime, k_source)
  ranking rules and paired across-arm controls. Neutral names conventionally close
  its K-name channel; this is not an audit of every semantic/context/state channel.
- `audit/core/harness.py::present` constructs context from source metadata when
  no explicit context is supplied, independently of the names map. Existing neutral
  naming does not itself establish removal of that context. This is a scope limit,
  not evidence that all historical controls were invalid or that a native model
  used any particular context.
- `audit/controls/transforms.py` contains name maps, ordering/path, sample/noise
  and knowledge helpers. Each has specific assumptions. `data_body_sha256` excludes
  the header and hashes decoded row text joined with LF; it is not a hash of exact
  original whole-file bytes. Future invariant claims must name the equality level
  actually checked, including relevant parsed values/rows/masks and mappings.
- `oracle_order` returns a topological sequence. `wrong_supplier` returns an edge
  set with selected reversals; that is not automatically the same typed knowledge
  object as an order, nor does its construction establish consistency. Native
  bindings and the intended question must identify the actual supplier semantics.
- S1 has policy/presentation, endpoint/authority, action-response and scoped state
  evidence structures. History checks do not implement scientific scheduling,
  resets, access isolation, retry policy or task budgets.

These were inspected, not modified or run here. Keep existing protocol categories,
historical metrics/certificates and compatibility behavior unchanged. A richer
channel/information assessment is a proposed additional contract, not retrospective
permission to change labels, tiers, denominators or finding verdicts. Adoption of
public regime/protocol changes remains W5's responsibility.

## 11. Tradeoffs and future acceptance examples

| Proposed direction | Strong alternative | Cost and failure prevented |
|---|---|---|
| Typed, scoped channel inventory and per-native bindings | A few universal input flags | More explicit metadata/checks; prevents missing context, retrieval and state channels or pretending all methods consume the same inputs |
| Distinguish labels-only and joint masking questions | One default neutral-name condition | Additional condition design and potentially runs; prevents overstating removal of domain information |
| Separate intended/available/delivered/accessed/used claims | Infer knowledge use from supplied files or output changes | More scoped observations/analysis; prevents unsupported provenance and non-use claims |
| Preserve native full mode and name restricted controls explicitly | Disable expensive/unsupported stages silently | More integration/resources or visible gaps; prevents evaluating a different method under the original name |
| Explicit state/feedback and nonconformance history | Assume fresh requests are isolated | More lifecycle evidence and possible analysis limits; prevents hidden carryover and favorable relabeling |

Future design acceptance examples must include:

| ID | Example and required behavior |
|---|---|
| P01 | Neutral header with semantic context: preserve the labels-only interpretation; withhold a no-context/no-knowledge claim |
| P02 | Swapped names with evaluator inverse map: establish intended mapping and visibility policy without redefining truth |
| P03 | Names-only method with unavailable data binding: show eligibility/claim limits, not fabricated numeric consumption |
| P04 | Oracle order: distinguish one chosen valid sequence from direct-edge/ancestry knowledge and retain disclosure provenance |
| P05 | Corrupted constraints forming a cycle: retain invalidity/rejection and distinguish the intended conflict question |
| P06 | Retained oracle text in a later arm's memory: preserve nonconformance/carryover evidence and intended membership |
| P07 | Equal action budgets with different queries: evaluate the declared policy question without asserting equal samples |
| P08 | Unobserved external access: report the observation/isolation gap rather than infer use or non-use |
| P09 | Partial reset or normalized-body hash: scope the demonstrated invariant, withhold stronger equality/isolation claims |
| P10 | Native retrieval disabled for one arm: identify the changed native mode and avoid full-method attribution |

These are proposed future validation obligations, not executed tests or closed
coverage cells. Instrumentation itself needs its own fidelity/overhead assessment
where relevant. Open details include exact channel/action contracts, enforcement
profiles, native bindings, materialization invariants, randomization/carryover,
nonconformance analysis and historical projection. Resolve these jointly before
serialization and implementation planning.

## Where we're going

Review the labels-only, knowledge-supplier and interactive/state examples. Next
design transformations and randomization: typed source-to-derived procedures,
invariant/equality levels, domain/reference applicability, randomization roles and
materialization receipts. Then develop comparisons, repeats and missingness so
the resulting contrasts retain their intended populations and scientific meaning.
No runtime, shared scientific logic, stored result, tracker or public paper contract
has been changed by this note.
