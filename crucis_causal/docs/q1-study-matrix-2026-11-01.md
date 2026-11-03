# Proposed Q1 empirical study: systems, experiments and evidence

Tickets: DLV-08, DLV-09, DLV-10; related DLV-06/07/11 and ADV-01.
Date: 1 Nov 2026, America/Los_Angeles.
Status: planning scenario for Uzair's review. No selected-case manifest,
preregistration, subsystem-2 implementation, funding award or paid-run approval.

## 1. Purpose and boundaries

Q1 evaluates the generic auditor as software, as a measurement procedure, and
through its findings on real causal-discovery systems. These are three separate
evidence obligations. Subsystem 1's engineering tests establish selected connection
behavior; they do not establish detector sensitivity or complete this empirical
study. Scientific success includes trustworthy clear and inconclusive findings,
not a required number of accusations against systems.

The [program contract](project/program-v3-excerpts.md), section 2, identifies five
LLM systems plus classical methods. The current eight-adapter panel is the starting
empirical scope below. The broader [capability map](system-connections-capability-map-2026-11-01.md)
guides architecture and extension selection; these eight do not empirically cover
every temporal, latent-variable, local-query, interactive or other mapped family.
Broader paper claims require appropriately selected additional native evidence.

The 6 Nov checkpoint retains its existing W1 sources. This proposed campaign is
for the 4 Dec final and must not block the checkpoint. It is not a promise that
every prerequisite will be ready by that date. Q2 system construction and its
funding are separate. Shared protocol/contract changes remain proposals to W5.

## 2. Panel and native execution readiness

| System/configuration | Primary empirical object | Existing footing and prerequisite before fresh execution |
|---|---|---|
| Causal-Copilot original baseline | Native pipeline graph and surviving stages | Recorded results and traces exist. Freeze the original source/environment/configuration and verify trace collection does not alter behavior. Modified versions are separate optional comparisons. |
| MATMCD CC-Agent mode | Native PC-to-LLM-constraints-to-PC pipeline | Existing harness calls native CC-Agent code. Live-web DA-Agent is omitted. Label the tested mode explicitly; full MATMCD including retrieval requires a separately supported and costed extension. |
| Vashishtha/Causal Order | Native causal ordering, including native cleanup | Existing wrapper uses native ordering code, then adds its own PC combination. Preserve the order as primary; any harness-derived graph is a separately labeled object/analysis. |
| PyWhy-LLM | Native pairwise knowledge suggestions | Selected recordings exist. Verify native client features, parsing, retry behavior, request scope and output meaning in the frozen environment. |
| causaliq | Native graph/probability outputs | Selected recordings exist. Preserve distinct existence and orientation meanings; verify native configuration and confidence extraction. |
| PC | Native statistical output under its assumptions | CPU execution route exists, conditional on dependencies. causal-learn is absent on the current S1 test host; S1's skipped test is not native readiness evidence. |
| GES | Native score-based output under its assumptions | CPU route exists, conditional on dependency/environment verification. Preserve equivalence-class/output semantics. |
| GIES | Native interventional output | Current support includes recorded imports; a fresh native execution route remains a prerequisite. Require correct intervention targets and compatible interventional samples. |

Sources: inspected `harness/agents/`, `audit/systems/`, `audit/run.py`, and
scope correction (archived research planning record), sections 3-5.
This is a readiness inventory, not new native execution evidence. Native sanity
checks use a suitable author example or equivalent documented input in the native
environment. Freeze versions, dependency identity, actual model/backend, arguments
and request/response evidence before accepting a row. Environment fidelity and a
compatible shared benchmark are complementary requirements.

## 3. Cases, repetitions and comparisons

The recommended costing scenario uses **20 public development cases**, provisionally
10 semantic and 10 formula cases from the existing CausalArena family pools. These
are two strata within one benchmark suite, not two independent benchmark suites.
The lean scenario uses 10 cases, provisionally five from each stratum. Availability,
eligibility, variable counts and the exact selection procedure remain to be checked
and frozen through subsystem 2; neither list is selected here. Do not extrapolate
this price to arbitrary larger graphs. Record all prior exposure; public or
previously examined cases must not be described as pristine held-out confirmation.

Use the same eligible case identities and fixed dataset replicate for compatible
comparisons. Preserve each system's actual information profile: data, names,
context, knowledge, interventions and metadata. Shared cases do not permit a single
ranking across different regimes, tasks or output semantics. Native orders, DAGs,
equivalence classes and pairwise claims need suitable declared measures; do not
invent a graph merely to make a table uniform. Exact synthetic truth supports
accuracy; contested real-world references support agreement.

Three independent native LLM draws per case/condition are proposed in the
recommended scenario; two in the lean scenario. A failed attempt followed by a
retry remains the same planned draw, with both attempts retained. Independent
draws require fresh eligible stochastic executions, not replayed responses. They
are nested within scenarios: 20 cases times three draws is not 60 independent
datasets. Deterministic classical methods do not receive artificial LLM repeats.
These repetition counts are affordability choices, not a completed power analysis.

## 4. Counted experimental matrix

Counts are planned pipeline executions, not individual LLM calls, successful
outputs or additional independent datasets. One execution can make many calls.
Rows share their baseline executions; never charge or count the baseline twice.

| Row | Question and design | Recommended hosted-LLM executions | Lean hosted-LLM executions |
|---|---|---:|---:|
| E1 names | Five LLM systems x cases x real/neutral/swapped names x independent draws | 5 x 20 x 3 x 3 = 900 | 5 x 10 x 3 x 2 = 300 |
| E2 presentation order | One additional order per case at real names; E1 supplies baseline. Reorder the actual native variable/list representation and invert the recorded mapping. | 5 x 20 x 1 x 3 = 300 | 5 x 10 x 1 x 2 = 100 |
| E3 sample availability | Causal-Copilot and MATMCD data-using modes only; two additional smaller sample budgets at real names and baseline order | 2 x 20 x 2 x 3 = 240 | 0 |
| Total scored paid scenario | E1 + E2 + E3 | **1,440** | **400** |

For E3, two nested random subsets, provisionally 50% and 25% of the available rows,
change sample availability, not names or mechanism. This assumes an eligible iid
dataset and sufficient sample sizes; interventions require stratified preservation
of target metadata. Final subset rules and seeds remain design work. Do not apply
this control to names-only native ordering/suggestion systems. Measurement noise,
mechanism changes and the Vashishtha-derived hybrid are separate extensions with
their own reference and interpretation review.

The classical companion scenario is PC/GES/GIES x cases x four conditions:
baseline, reordered variables, and the two sample budgets. This gives **240 CPU
executions** for 20 cases or **120** for 10, conditional on every cell being
eligible. No hosted LLM charge is assigned to these rows. These counts do not
include setup, tests or auditor validation and are not CPU/GPU-hour estimates.
GIES uses a correctly matched observational/interventional task; do not silently
substitute observational inputs. Ineligible cells remain listed with reasons.

Rename conditions must specify every modified/exposed channel. A neutral column
label does not prove absence of semantic information in context, paths, prompts
or other metadata. Presentation-order controls preserve variable identity, values,
references and intervention alignment. Label any extra task change separately.

Stage, confidence, abstention and cost observations are collected from these same
executions wherever natively available. They add no paid execution by default;
extra intervention runs would need their own row. Missing native signals remain
missing. Observing a trace must not silently turn a black-box system into an
altered algorithm. Stage association alone does not establish a causal explanation.

## 5. Other required work and bounded extensions

| Work | Role and resource | Scope boundary |
|---|---|---|
| Recorded evidence reuse | Recompute existing raw evidence and certificates; no fresh LLM calls | Fourteen legacy audit configurations are not fourteen systems. Reuse only after exact request/configuration/task/provenance checks; historical ca-ab06 and q1s2 share zero scenarios. Cost scenarios above conservatively assume fresh executions throughout. |
| Native setup and pricing pilot | Separate development work; proposed cap $100 inside the funding ceiling | Up to three representative sizes/cases per LLM system x two relevant conditions = up to 30 executions, plus required setup within that cap. Include the expensive eligible size/branch. A native sanity execution may serve this purpose without duplicate billing. Pilot rows are not automatically promoted to the scored cohort. |
| Auditor validation | Known-positive/null fixtures, suitable fault strengths and repeated sampling, primarily CPU | Plan evidence per finding procedure across K01-K15; the earlier eight fault families do not automatically cover all fifteen kinds. Measure false alarms, sensitivity, inconclusive behavior and limits. S1's engineering tests do not substitute for this work. Exact counts and statistical design remain open. |
| Benchmark appendix | Existing CausalArena layout and CausalBench metric investigations; CPU/recomputation where possible | DLV-11/W1 ownership and existing source contracts remain unchanged. The new system matrix does not replace these obligations. |
| Additional native capability families | Select contrasting temporal/local/latent-variable/other families needed for intended claims | Integration, task/reference choice, tests and compute estimates are prerequisites. No named family is claimed implemented or empirically validated by this plan. Costs are unpriced extensions. |
| Full MATMCD retrieval; knowledge controls | Separate native mode and eligible none/oracle/wrong-supplier experiments | Cost retrieval services and calls; preserve native vs derived modes and define reference meaning. Omitted from the present ceiling. |
| Model/backend comparison | Separately identified model configuration, potentially institution-hosted | Check feature compatibility, actual served model identity and inference settings. Model substitution changes the experiment. Omitted from counts unless it replaces a proposed row before preregistration. |
| Causal-Copilot version comparisons | Separate declared Q1 evaluation question, reusing exact eligible baselines | Q2 implementation is excluded. Additional versions/calls are not hidden inside E1-E3. |
| Sealed confirmation | Owner-controlled release after eligible design and integration freeze | Do not access real seeds here, call exposed development cases sealed, or assume eight systems fit the existing read allowance. Eligibility, authorization and any policy adoption must be resolved first. No fresh sealed-call allowance is priced here. |

The recommended matrix covers names, variable order and selected sample-size
robustness. It does not claim exhaustive layout/path, knowledge-supplier, noise,
mechanism, backend, version or adversarial coverage. Reports need a per-system,
per-finding applicability/evidence table rather than a blanket "all audited" label.

## 6. Analysis and acceptance requirements before a run plan

1. Freeze system/mode/environment/model identity, case manifest, input profile,
   transformations, seeds, repetitions, resource caps and analysis populations.
   Hash relevant content again at materialization; a cached manifest hash alone
   cannot establish that mutable source files still agree.
2. Register the target contrast, output/reference semantics, effects, intervals,
   thresholds, multiplicity policy and any exploratory labels. Infer at scenario
   level with within-scenario draws accounted for. Do not silently pool regimes,
   case strata or native/derived objects. Approve power/precision limits explicitly.
3. Preserve intended, eligible, attempted, completed, output-usable and scoreable
   denominators. Report failures, partial results, abstention, missing cost and
   unsupported cases. Paired successful-only results, if useful, accompany their
   coverage rather than replacing the declared population.
4. Pilot resource use per system, size, condition and actual backend. Reforecast
   before any main campaign. Select lean/recommended/revised scope explicitly;
   do not change model, drop hard cases or rerun only favorable outputs to fit a cap.
5. Require native-fidelity checks, S1 record validity, applicable later-subsystem
   tests, raw evidence retention and per-report certificate verification. Existing
   stored numbers must retain the 0.001 compatibility gate. New measurements need
   their own recomputation/evidence checks, not agreement with old result values.

## 7. Funding scenarios and tradeoffs

The budget ledger (archived research planning record) derives each system's historical
proxy from its own known USD records in the cost inventory (archived research planning record).
These are reported estimates, not invoices or current quotes. Vashishtha and
PyWhy-LLM each have only ten cost-bearing records, covering five real and five
swapped cases, with no neutral cost observations. Some metadata mix models;
Causal-Copilot used a different cohort. Missing costs are not zero. Transferring
these means to new arms, sizes and models is **unvalidated sensitivity arithmetic**.

| Scenario | Historical-rate projection | 25% planning allowance | Separate pilot cap | Rounded proposed ceiling |
|---|---:|---:|---:|---:|
| Lean, 400 paid executions | $239.38 | $59.85 | $100 | **$400** |
| Recommended, 1,440 paid executions | $806.10 | $201.52 | $100 | **$1,200** |

The allowance is a budgeting choice, not a confidence bound. Recommended math is
$806.096364 x 1.25 + $100 = $1,107.620455, rounded up to a $1,200 proposed cap.
Lean math is $239.383101333... x 1.25 + $100 = $399.228876666..., rounded to $400.
At twice the historical rates the corresponding totals would be about **$2,115.24**
and **$698.46**. This is a sensitivity example, not an asserted upper bound.
No fixed ceiling guarantees completion until model/size-aware pilots validate it.
Additional attempts, provider billing differences and changed inference conditions
must be included in that forecast; no automatic additional retries are authorized.

The recommended scope offers more scenario diversity, an extra draw and targeted
numeric robustness. The lean scope preserves all eight panel members and the main
name/order comparisons but supports weaker precision/generalization and omits
paid numeric controls. It is a useful reduced study, not automatic completion of
the program's full golden scope. Smaller awards can fund a capped multi-system
pilot and existing-evidence work, followed by an explicitly revised claim set.

Institutional compute and API dollars are separate. NRP's
[managed-model access](https://nrp.ai/documentation/userdocs/ai/llm-managed/api-access/)
requires eligible access; its [model service](https://nrp.ai/documentation/userdocs/ai/llm-managed/)
is a potential distinct backend, subject to compatibility and actual-model
recording. Do not use fallback model routing in a frozen comparison. Expanse
[compute allocations](https://hpc-training.sdsc.edu/hpc-training-docs/expanse-101/expanse-101/accounts-and-charging/)
do not by themselves pay commercial API bills. Course access, capacity and CPU/GPU
hour estimates are unresolved; no unlimited/free resource assumption is used.

## Where we're going

Review the proposed matrix and provisional funding tiers with Uzair. A replacement
professor draft requests up to $1,200 for Q1 in stages, starting with a $100
multi-system pricing pilot, and offers the $400 lean scope if funding is limited.
Nothing is sent or spent. Then return to subsystem 2's case identity and collection
membership design, using this study to test its requirements without prematurely
freezing manifests, statistical choices or later-subsystem implementation.
