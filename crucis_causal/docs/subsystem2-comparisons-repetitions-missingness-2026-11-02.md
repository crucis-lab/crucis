# Subsystem 2: comparisons, repetitions and missingness

Tickets: DLV-08, DLV-09; related DLV-10, DLV-06/07 and ADV-01.
Date: 2 Nov 2026, America/Los_Angeles.
Status: design proposal. Uzair authorized proceeding from transformations and
randomization to comparison/repetition/missingness contracts, with no implementation.
Specific policies, estimators, profiles and wire contracts below remain proposals.

Sources: [transformations/randomization](subsystem2-transformations-randomization-design-2026-11-02.md),
[conditions/information](subsystem2-conditions-information-design-2026-11-02.md),
[reference/response semantics](subsystem2-reference-response-semantics-2026-11-02.md),
[S2 structure](subsystem2-structure-design-2026-11-01.md),
`audit/controls/{effects,l1}.py`, `audit/core/{runs,battery}.py`, `audit/collect.py`
and `audit/connections/schema.py`. Examples are hypothetical, not measured findings
or executed experiments. No stored number, score implementation or certificate changes.

## 1. Define the target before choosing available observations

A comparison specifies the scientific quantity/question, target population,
conditions/subjects, response/reference scopes, unit, weighting and treatment of
events such as noncompletion. It then binds a measurement/analysis contract.
The observed analysis set is subsequent evidence; it cannot silently redefine
the original question. A contrast is not fully specified by two condition labels.

Examples of different legitimate questions:

- Mean difference in a specified output-quality measure over a declared matched
  dataset population, with an explicit policy for unavailable values.
- Conditional quality among cases with usable outputs in both conditions.
- Probability of fulfillment/completion under one attempt or a bounded recovery
  policy, with infrastructure and native outcomes separately described.
- Task utility under a fixed rule covering definite answers, abstention, failure,
  cost or deadline limits as appropriate.
- Quality or cost of a declared set-valued/interactive policy, under its action,
  source-state and reference conditions.

No one question is a universal default for every native family. In particular,
correctness can be undefined when no relevant output exists. That does not justify
silently substituting zero graph F1, inventing an empty graph or dropping the case.
A defined task loss/utility may assign a consequence to failure/abstention, but its
meaning and values are explicit and its result is not relabeled native graph accuracy.

## 2. Proposed comparison obligations

| ID | Responsibility | Failure prevented |
|---|---|---|
| C01 | Identity/version, author, temporal/commitment basis and amendment history | Retroactive primary-analysis selection presented as prospective |
| C02 | Scientific target/contrast, direction, units, permitted label and metric/rule versions | Reversing a difference or confusing accuracy, agreement, completion and utility |
| C03 | Intended population and selection rule, cases/source releases and condition/system/configuration bindings | Replacing the planned population with returned/successful outputs |
| C04 | Task/output/reference applicability, information regime, domain/alignment and native/derived roles | Comparing different meanings or using a surviving stage as an undeclared final output |
| C05 | Trial/repetition/draw/attempt identities and planned multiplicities | Counting retries, samples or bootstrap draws as new scientific cases |
| C06 | Matching keys, requirements, cardinalities and permitted coupling; explicit unmatched cases | Pairing by row order, similar labels or equal repeat indices |
| C07 | Nesting/overlap/dependence relationships, analysis units and weighting/aggregation order | Pseudoreplication or changing from case-average to edge-pooled performance silently |
| C08 | Eligibility/readiness rules and timing/basis, distinct from observed output/score availability | Calling hard cases inapplicable after seeing failure or poor performance |
| C09 | Outcome/coverage populations and scoped reasons for gaps/nonconformance | A single success flag concealing abstention, missing truth, capture loss or policy violations |
| C10 | Missingness/abstention/recovery handling and any identification/utility/sensitivity assumptions | Unjustified imputation or full-population claims from selected complete pairs |
| C11 | Uncertainty, multiplicity, sensitivity and stopping-rule references with applicable support limits | Treating correlated outputs as independent or selecting significant findings after the fact |
| C12 | Evidence/resolution/selection receipts and actual included/excluded/unmatched identities | An aggregate that cannot be traced to exact outputs, denominators and decisions |

These are logical obligations, not frozen JSON fields or twelve mandatory files.
Use S1 evidence/domain/request/attempt identities rather than duplicating native
history. S2 declares the intended analysis; S3 later enforces authorized execution
and recovery; S4 computes measurements/statistics; S5 applies finding rules.

## 3. Population accounting is metric- and scope-specific

Retain identities, counts and relationships for the applicable scopes below:

| Scope | What it identifies |
|---|---|
| Intended case/trial population | Every selected case and planned scientific condition/repetition slot |
| Scientifically eligible | Cases for which the declared task/comparison assumptions and scope apply, including unresolved eligibility where not established |
| Operationally ready | Supported bindings, dependencies, resources and input/reference prerequisites at their required boundaries |
| Attempted / native started | Created execution attempts and evidence of actual native start; the ID alone does not prove start |
| Delivered / policy-conforming | Actual-input bindings and assessed condition fidelity, with unknown/nonconforming scopes retained |
| Fulfilled / partial / abstained | Scoped request assessments and native decisions under the actual response contract |
| Captured / interpretable | Available output/evidence at a defined scope and supported semantic interpretation |
| Reference-covered / scoreable | The particular output/proposition/metric scope has an applicable reference and valid measurement |
| Matchable / analysis-included | Actual members satisfying a particular matching and analysis rule, including exclusions and reasons |

These are not necessarily one nested funnel or mutually exclusive bins. A failed
pipeline may have an interpretable intermediate graph; a fulfilled response may
abstain on some propositions; a complete graph may lack a reference. Conditions
can be conformance-unknown while a descriptive output comparison remains meaningful
at a narrower declared scope. Always identify numerator, denominator and unit.

A case can be excluded from a particular analysis without disappearing from its
original population. Distinguish intended, eligible and selected populations when
stating the scope of generalization. Exposure history, selection and reference
coverage can limit conclusions even if every native run completed.

## 4. Matching and repetitions

Match using explicit case/source-realization, task/target, condition, output-role,
reference/view and nuisance-transform bindings. Allow declared differences; do not
require equal realized inputs in an equal-budget adaptive-policy comparison.
Every required equality/correspondence has its meaning and evidence. Similar file
names, equal shapes, historical arm labels and returned list positions are insufficient.

One-to-one pairs, repeated measurements within a case, many-to-one baselines,
multiple alternatives and hierarchical groups require different cardinality and
selection contracts. Reusing one baseline across several contrasts is allowed
when declared; it creates dependent contrasts and does not create extra baseline runs.

For the prior illustrative 10-scenario x 1-dataset x 3-condition x 3-native-repeat
layout, there are 90 planned trials. Repetition summaries may be defined per
case/condition before comparing conditions, or a justified hierarchical procedure
may model the nested outputs. The target distinguishes conditional native variance
from data-realization and source-population variance. No concrete estimator or
interval is adopted by this note.

If native repetitions are independent across arms, comparisons can still be paired
at the shared case/dataset level. Matching repetition index 1 to index 1 does not
prove shared native randomness. If valid coupling exists, record it and preserve
its structure in the chosen analysis. A failed repetition leaves its slot visible;
do not compact surviving runs and invent new pairs by position.

Native graph particles, bootstrap members or multiple outputs within one request
retain their collection/provenance meaning. They are not automatically separately
randomized scientific trials. Source scenarios, sites, subjects and overlapping
time windows can impose multiple dependence structures. A flat count of graphs
is not an independent sample size.

## 5. Concrete unavailable-score example

Assume four equally weighted matched cases and one scalar score in [0,1] per arm
per case. For this example only, each score is well-defined because suitable
outputs/references exist, but two scores are unavailable due to capture gaps.
This assumption is needed for the later bounds; it is not a general claim about
scores for native failures or absent outputs.

| Case | Real-name score | Neutral-name score |
|---|---:|---:|
| A | 0.90 | 0.80 |
| B | 0.80 | 0.70 |
| C | unavailable | 0.95 |
| D | 0.20 | unavailable |

Each arm has three available scores out of four. Only two of four cases have both.
On the complete pairs A/B, the mean real-minus-neutral difference is +0.10.
Separate available-case arm averages are 1.90/3 and 2.45/3; their difference is
-11/60, approximately -0.1833. The opposite signs arise from different populations.
Neither calculation by itself establishes the full four-case contrast.

For the explicitly defined bounded full-population quantity, denote the missing
scores x and y. Its contrast is (-0.55 + x - y)/4. With only 0 <= x,y <= 1,
the range is [-0.3875, 0.1125], which does not establish the contrast's sign.
These are elementary illustrative bounds, not an adopted missing-data estimator,
confidence interval, stored audit number or new experimental result.

Report the conditional complete-pair result with its population and coverage if
useful. The separately observed arm averages answer another descriptive question.
To infer a broader target needs justified assumptions, an appropriate design or
honest sensitivity/partial-identification limits. Equal per-arm coverage rates
alone do not solve the matching/selection issue.

## 6. Different gaps need different treatment

| Situation | Required account and scientific consequence |
|---|---|
| Task genuinely inapplicable to a case | Apply an evidenced task/assumption rule; retain original selection and report scientific eligibility |
| Native method supports the task but adapter route/dependency is missing | Integration/readiness gap, not proof that the scientific task or native system is unsupported |
| Budget tier not released or provider quota unavailable | Planned-not-executed/resource evidence; do not label it a native crash or quietly drop it |
| Native exception or timeout | Preserve observed source, stage and resource policy; cause classification can remain uncertain. A study deadline and infrastructure interruption are not automatically intrinsic system faults |
| Failure with a surviving stage output | Score only under the declared stage/task/reference binding; final fulfillment can remain unmet or unresolved |
| Explicit allowed abstention | Preserve its scope; it may fulfill the response rule while reducing definite-answer coverage |
| Unreported local propositions | No fabricated negatives; retrieval/coverage/utility consequences follow their declared rule |
| Missing/truncated output or unsupported decoder | Capture/interpretation gap, not invented abstention, empty graph or proof of native nonproduction |
| Missing/partial/contested reference | Metric-specific scoreability/label limit; not zero quality. Partial labels judge only their established scope |
| Wrong input or unauthorized reference access | Preserve intended and actual conditions, nonconformance evidence and affected applicability; do not relabel after outcomes |
| Conflicting or unidentified records | Preserve candidates and uncertainty; do not pick the record yielding the best score |

Several reasons can apply to one trial. Record source and confidence/basis of
attribution; do not assert missing-at-random merely because a label says host error.
Infrastructure/capture failures can correlate with graph size, runtime, condition
or source difficulty and thus affect observed populations.

## 7. Missingness policy and permitted claims

The contract must choose the intended question and bind suitable handling. Useful
options include:

- A conditional answered/scoreable/complete-pair analysis, explicitly limited to
  that observed set, accompanied by intended-population coverage and reasons.
- Separate quality, fulfillment, abstention, conformance, cost and evidence-availability
  measures; do not imply that one scalar captures all of them.
- A defined all-trial task utility/loss that assigns meaningful consequences to
  noncompletion/abstention under a fixed policy. Never describe assigned values as
  observed graph scores or silently synthesize graphs to obtain them.
- Bounds/sensitivity for a well-defined partially observed target, with its boundedness,
  assumptions and identification limits. Undefined no-output quality needs a target
  definition before such arithmetic applies.
- Model-based adjustment/imputation only under an explicitly justified, versioned
  analysis with its data/missingness assumptions and diagnostics. No automatic
  inverse weighting or imputation is proposed as a universal core default.

The generic core should represent these scoped rules and check that required
inputs/semantics exist. It should not select a favorable statistical policy from
the outcomes. Computation belongs to its declared measurement procedure. A historic
analysis can be reconstructed or extended under an honest retrospective label;
newly written rules do not retroactively preregister it.

## 8. Retry, restart and recovery policies

Scientific trial identity stays distinct from S1 request/attempt identities.
External retries and checkpoint restarts create the appropriate new attempts and
continuation links under the declared trial/recovery policy. Actual loaded state,
request relation and information history determine what can be claimed about the
continuation. Native internal retries/sampling retain their native event scope.

Two meaningful operational questions illustrate the choice:

- First-attempt behavior: later recovery can be reported separately; the original
  failure does not disappear because another attempt produced a graph.
- Bounded recovery-episode behavior: define allowed attempts, retryable events,
  total resource/deadline rules, state policy and output-selection rule. Report
  recovered fulfillment together with initial failures and attempt history.

An output-selection rule could select the first response satisfying the declared
response contract within the cap. That policy measures the configured recovery
process, not an untouched single attempt. Contract fulfillment is not evaluation
correctness: evaluator reference scores cannot secretly determine which output
is selected. A best-of-n or oracle-selected output is a different declared method
or diagnostic, with the additional selection information explicitly identified.

Known costs of failed, interrupted and retried work remain relevant. Resource
aggregation needs scope/membership checks for cumulative/overlapping accounting;
do not blindly sum inclusive receipts. Created attempt count, actual native starts,
scientific trial count and observed billable work remain distinct.

## 9. Weighting, uncertainty and multiple comparisons

Bind the weighting target: equal cases, source-balanced cases, a specified source
distribution, edge/claim-weighted aggregates or another justified population.
Mean case F1 and a pooled edge-level ratio are different quantities. If one arm
loses repetitions, an available-output mean has a different selection/precision
account from the planned equal-repeat mean. Do not silently compensate with more
retries, new cases or weights selected from favorable outputs.

Uncertainty must reflect the actual independent/randomization units and retained
matching/coupling. A procedure meant to preserve case pairing must retain both
arms' association when resampling/modeling their common units. More native repeats
can inform conditional variability without replacing source diversity. Bootstrap
draw count is computational, not new observed evidence. Few clusters and unresolved
overlap/independence limit generalization even if a numeric interval can be computed.

Reference uncertainty and selective annotation can limit a conclusion beyond a
sampling interval. An interval for observed metric variation is not automatically
an interval for truth correctness, domain alignment or missing-data assumptions.

Bind primary contrasts, secondary/exploratory analyses and the relevant family of
conditions, metrics, stages, versions and findings. Any multiple-comparison or
sensitivity procedure has an explicit contract. Stopping/funding releases and
adaptive decisions retain timing and rule; inspecting an effect until it looks
significant does not acquire fixed-sample confirmation status. Exact formulas,
power/precision targets and multiplicity choices remain for joint S2/S4 design.

Zero matched units means the requested paired statistic is unestablished, not an
observed zero effect. No detected effect is not evidence of practical equivalence
without the requisite target, margin and precision. Claim labels and thresholds
remain under their adopted owner contracts.

## 10. Existing implementation footing and compatibility

- `audit/controls/effects.py::paired` intersects available keys, groups differences
  by the supplied cluster function and delegates to the shared cluster bootstrap.
  Empty intersections return missing values and zero units, not a zero effect.
- `audit/controls/l1.py::by_cluster` averages selected scored outputs by scenario,
  requiring OK for the final source; `layout_effect` uses OK rows in both arms.
  These are specific historical analysis populations, not universal defaults.
- `audit/collect.py` reads recorded item/arm combinations, skips arms not listed
  on an item, and keys scored records by (item, arm). It preserves supported
  variants from some failed records. That key space is not a generic per-trial
  repetition identity; new repeated-trial support must not overwrite/collapse it.
- `audit/core/runs.py` defines one record per (system, item, arm), with typed native,
  infrastructure and not-run statuses. Its notes-based `replicates` include earlier
  attempts such as repeats after host errors, and `all_runs` exposes them for
  existing counts. The field name does not establish independent scientific draws.
- S1 request/attempt, recovery and replay structures already preserve relevant
  occurrence/continuation evidence. They do not choose a new statistical population,
  output-selection policy or scientific repeat count.

This is read-only source inspection. Preserve all historical calculations, status
meanings, thresholds, certificate/paper pointers and 0.001 compatibility gates.
New generic comparison/coverage behavior remains proposed; changes to protocol
or measurement contracts require owner adoption, not a silent reinterpretation.

## 11. Alternatives and future acceptance examples

| Proposed direction | Strong alternative | Cost and prevented failure |
|---|---|---|
| Explicit comparison target and population | One mean over all available scores | More contract/population metadata; prevents confusing conditional and full-population claims |
| Scoped outcome/availability dimensions | One mutually exclusive success/missing flag | More accounting; preserves partial outputs, abstention and reference-specific limits |
| Trial/draw/attempt/nesting identities | Treat each run record as independent | More links and analysis constraints; prevents pseudoreplication and collapsed repetitions |
| Metric-specific declared missingness policy | Always drop gaps or assign zero | Additional statistical/utility design; prevents fabricated correctness or hidden survivor selection |
| Explicit recovery selection and total resource scope | Report the final successful retry only | More history/cost evidence; prevents erased failures and undisclosed best-of-n methods |

| ID | Future acceptance example |
|---|---|
| V01 | The four-case example reports both available-arm and complete-pair populations; neither is mislabeled the full-population contrast |
| V02 | Empty matches yield no established paired effect, not zero |
| V03 | One failed native repetition keeps its planned slot and does not reindex surviving outputs into new pairs |
| V04 | A failed final pipeline with a surviving stage yields scoped stage evidence, not invented final completion |
| V05 | Explicit abstention, empty prediction, unreported answer and capture loss retain distinct native/evaluation meanings |
| V06 | Missing adapter support and missing truth are distinguished from native method failure and scientific inapplicability |
| V07 | An intended-condition violation retains its original arm, actual input and applicability/accounting consequence |
| V08 | Bounded recovery preserves first failures, attempt histories, selection policy and non-overlapping resource totals |
| V09 | Reused baselines, native collections and data/subject overlap retain dependence rather than adding independent samples |
| V10 | Case-balanced versus edge-pooled weighting and unavailable-repeat handling identify their actual target |
| V11 | Bounds/imputation/utility require a defined target and declared assumptions; missing graph quality is never silently synthesized |
| V12 | Joint uncertainty/multiplicity/stopping rules and retrospective amendments retain their supported claim labels |

These are proposed design acceptance obligations, not tests run or coverage cells
closed. Open details: exact comparison families, identity cardinalities, readiness/
eligibility vocabularies, concrete weighting/missingness/recovery/statistical rules,
population receipts, historical projections, serialization and API bindings.

## Where we're going

Review the target/population and missing-arm examples. Next consolidate eligibility
and operational/scientific readiness with plan commitment and controlled release:
when each binding becomes fixed, who can amend/release it, how adaptive policies
and actual decisions are logged, and how development/sealed exposure is represented.
Then exercise complete cross-linked experiment definitions, resolve remaining
contract/compatibility gaps and conduct subsystem 2's final design review before
implementation bundle planning or any build authorization.
