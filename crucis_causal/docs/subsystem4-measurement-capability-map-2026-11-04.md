# Subsystem 4: measurement capability space

Tickets: DLV-08, DLV-09; related DLV-10.
Date: 2026-11-04, America/Los_Angeles.
Status: design map for discussion, before support-profile selection. No S4
implementation, exact schema, evaluator adoption, inference default, paid/native
campaign, paper change or public protocol change is authorized by this document.

## 1. Continuation, acceptance and evidence status

The [opening proposal](subsystem4-structure-design-2026-11-04.md) introduced seven
responsibilities. Uzair endorsed continuing from that structure, then endorsed the
measurement-question identity/applicability walkthrough as the basis for this pass.
This is conceptual acceptance for continued design, not a frozen encoding, support
matrix or mathematical procedure. The present request is to map the full measurement
space, including output/reference combinations, prerequisites and withheld claims,
before choosing profiles. Specific map decomposition and recommendations below are
proposals; they are not silently attributed to the user as accepted details.

The preceding walkthrough distinguished a scientific question, its exact evidence
binding, and each calculation occurrence. Applicability assessments relate those
accounts rather than replacing them with one ready flag. A metric name, a matching
array shape or a content hash does not establish scientific semantic equivalence.
Changed scientific conventions require an explicitly revised question; later source
evidence requires a new binding/assessment; an implementation correction under an
unchanged mathematical definition requires a new calculation with provenance.
Exact template/instance identity rules remain to be specified.

This map is a design synthesis from inspected local contracts and the two primary
scientific sources linked below. It is broad coverage of the currently identified
space, not proof that every future causal system has been anticipated. Rows are
design inventory, not implemented evaluators, native integrations, tests or trials.
No procedure is qualified merely because its possible role appears here.

## 2. Compose independent dimensions

A capability is a combination of:

- Question/quantity and intended interpretation.
- Native output semantics, including uncertainty, omission and associations.
- Reference role, scope and evidential strength.
- Domain identity, alignment and allowed derived views.
- Unit/population, experimental design and selection/stopping history.
- Available evidence, cutoff, access and execution authority.
- Exact evaluator semantics/implementation and mathematical applicability.
- Result form and the stronger claims that remain withheld.

No cross-product is automatically supported. Separate support for temporal outputs
and probability outputs does not establish temporal-probability evaluation. New
combinations need checks at their shared boundaries. A new semantic family needs a
named versioned contract and qualified procedure; an opaque extension name does
not gain scientific interpretation by passing a common envelope validator.

The core should reuse question/binding identity, source pins, domain mappings,
coverage/missingness accounting, population contributions, aggregation, applicability
evidence and result publication. Semantic evaluators supply reusable mathematical
meaning. Native adapters supply native mechanics and evidenced decoding. S3 remains
the owner of effectful execution, access/authority and recovery. S4 does not create
a second runner, permission system, finding-threshold engine or generic reviewer.

## 3. Reference-role map

References can combine roles. Completeness, disagreement, uncertainty, provenance,
access and revisions are modifiers, not a simple ladder in which every later row
is universally stronger. Every claim remains scoped to its target and basis.

| ID | Reference role | What it can support with the right procedure | What it does not establish by itself |
|---|---|---|---|
| R01 | No external target; an object's own declarations | Internal consistency, family conformance, specified invariants and observed response scope | Scientific correctness, calibration, external validity or faithful reasoning |
| R02 | Another selected output, system, stage or condition | Agreement, change, stability, disagreement and matched descriptive contrasts | Either system's accuracy or causal attribution of the difference |
| R03 | Exact scoped generating/reference object | Error/recovery at compatible predicates, coordinates and scope | Truth outside scope, all identifiable properties or all downstream tasks |
| R04 | Partial assertions and necessary constraints | Judgments on supported propositions, constraint violations and justified bounds | Unlisted negatives or full correctness merely from satisfying necessary constraints |
| R05 | Complete admissibility rule, equivalence class or identified answer set | Membership, compatibility, set relationships and justified specificity/coverage measures | A unique answer, equal probabilities for members or full recovery from one compatible member |
| R06 | Numerical target, uncertainty set or reference distribution | Compatible point/set/distribution comparisons with reference uncertainty retained | Exact truth from a noisy estimate, or a realized label from an ungrounded probability |
| R07 | Observational samples, sufficient statistics or test service | Predictive/statistical checks under a defined sampling and access contract; causal quantities only with an applicable identification basis | Causal structure or effects from fit/association alone |
| R08 | Interventional/experimental outcomes | Scoped intervention-response or identified effect assessment under the actual design | Every edge, every environment, transportability or individual counterfactual truth |
| R09 | Specified generative/mechanism model, simulator or oracle | Model-relative structural, functional, intervention or counterfactual targets within its declared operation contract | Correctness of that model for the world or truth for unprovided operations |
| R10 | Task, operational, exposure, resource or utility contract | Deliverable fulfillment, operational conformance, scoped accounting and defined utility | Causal correctness, actual native termination from collection closure, or usage from access alone |

Two scientific boundaries inform this decomposition. Causal and counterfactual
assessment requires explicit targets and assumptions beyond associations alone;
see [Pearl (2009)](https://web.cs.ucla.edu/~kaoru/SS-2009-57-Sup.pdf), especially
sections 2 and 3. Probabilistic assessment distinguishes scores on realized outcomes
from calibration across forecasts and outcomes; see
[Gneiting and Raftery (2007)](https://sites.stat.washington.edu/raftery/Research/PDF/Gneiting2007jasa.pdf),
introduction and sections 2-6. These sources motivate boundaries, not this map's
engineering taxonomy or a selected implementation. No new formula is adopted here.

Restricted evidence may occupy any reference role. An attestation is evidence of a
scoped assertion/procedure, not an interchangeable copy of unavailable raw truth.
Conflicting reference assertions retain their evidence and applicable scope. Do not
average labels, prefer the newest file or choose the best score to resolve conflict.

## 4. Output/reference combinations

The rows describe potential measurement contracts, not chosen support profiles.
Common identity, selection, evidence and unit requirements apply to every row.

| ID | Native output / measurement target | Relevant reference roles and possible questions | Additional prerequisites | Claims withheld without them |
|---|---|---|---|---|
| M01 | Point graph or structural relation | R02-R05/R09: adjacency, orientation, ancestry, family conformance, agreement or recovery | Exact graph/predicate semantics, endpoint meanings, omission/coverage, aligned domains and target-specific reference view | Direct edges from ancestry; causal claims from associations; global accuracy from partial labels; arbitrary completion of uncertain endpoints |
| M02 | Equivalence-class or set-valued structural answer | R03-R05/R09: membership, asserted/possible relations, set coverage, specificity or bounds | Evidenced class/set meaning, complete admissibility where needed, logical consequence procedure and selection policy | Full correctness because one member matches; uniform member probabilities; guessed canonical representative |
| M03 | Local sets and proposition decisions | R03-R05/R10: membership quality, answer coverage, abstention and fulfillment | Exact query predicate/target, candidate universe, exhaustive versus open answer, native decisions and reference coverage | Global negatives, unknown reference labels as false, abstention from capture loss |
| M04 | Orders, rankings, tiers and tied groups | R03-R06/R10: precedence constraints, admissible sequence, ranking relevance/utility or completeness | Sequence versus relation/ranking semantics, closure rule, tie/incomparability meaning, relevance target, candidate and top-k/tie policy | Causation from sequence position; one arbitrary reference order; equality from unspecified placement; penalties for unranked items by default |
| M05 | Coefficients, effects, parameters and numeric tensors | R03/R06/R08/R09: numerical error, set membership or functional contrast | Same quantity, coordinates, units/scale, population/context, conditioning and parameterization; explicit conversion/identification basis | Probability from weight/coefficient; total effect from direct coefficient; parameter comparability from matching shapes |
| M06 | Event probabilities or predictive distributions | R03/R06-R09: realized-outcome contributions, distribution comparison, calibration or decision-derived performance | Exact event/sample space, conditioning, valid mass/normalization, observed labels or appropriate reference distribution; population/design for calibration | Edge probability from an unspecified confidence; joint graph assessment from edge marginals; calibration from one outcome; unknown label as 0 or 0.5 |
| M07 | Test statistics and p-values | R07/R09 or designed null/alternative references: rejection behavior, null calibration, power or declared decision performance | Hypothesis/test/statistic semantics, null generation, sampling design and selection/multiplicity rules | Posterior edge probability, scientific absence from non-rejection, or calibration from numeric range alone |
| M08 | Confidence/credible/prediction intervals and uncertainty sets | R03/R05/R06-R09: target inclusion, width, set relationships, procedure coverage or appropriate predictive scores | Interval/set target, construction/level meaning, units and repeated-design/outcome basis for coverage claims | Frequentist coverage from one interval, causal validity from narrow width, interchangeability of confidence/credible/prediction meanings |
| M09 | Collections, samples, ensembles and weighted graph/parameter members | R03-R09: member-level quantities, empirical summaries, event mass, joint assessment and sampling diagnostics | Member identity/multiplicity, associated parameters, weight/generation meaning, complete or residual support and justified derived views | Independent scientific repetitions from draws; exact posterior from an empirical bank; silent normalization; best-member selection as native quality |
| M10 | Fitted mechanisms, executable models and learned functions | R06-R09: predictive loss, distribution checks, functional fidelity or authorized intervention queries | Actual callable/reader support, domains, state/version, evaluation-data separation, query/operation meaning and scoped target | Causal validity from observational prediction; executable behavior from an artifact reference; unobserved mechanisms from a graph alone |
| M11 | Intervention effects, policies and counterfactual answers | R03/R05/R06/R08/R09: target error, identified bounds, response or utility | Exact intervention and target quantity, population, horizon/environment, identification assumptions and suitable reference operation/design | Individual counterfactual truth from one factual outcome; all interventions from one experiment; proxy intervention equivalence or transport by default |
| M12 | Learned/latent representation plus associated structure | R03-R09: explicitly aligned structural/functional quality, invariant quantities or alignment ranges | Evidenced variable/coordinate relation, allowed equivalences, calibration/training separation and declared ambiguity treatment | Matching factors by index/name; source-variable accuracy without alignment; outcome-optimized alignment presented as independent validation |
| M13 | Explanations, citations, free text and native reports | R02-R05/R10: extracted-claim assessment, source support, declared rubric or human assessment | Supported interpretation/rubric, exact source passages, assessor identity/limits and any reliability/design requirements | Causal reasoning faithfulness from plausible text; evidence that a cited source influenced execution; semantic correctness from text similarity alone |
| M14 | Interaction/action histories and adaptive policies | R02/R08-R10: response utility, constraint fulfillment, learning/quality trajectories, resource frontiers or regret under a defined oracle | Action/opportunity identity, delivered versus selected/accepted effects, histories, comparable initial conditions, utility/oracle and stopping/design evidence | Counterfactual performance of unchosen actions without a basis; identical final data by assumption; actual information use from availability |
| M15 | Operational outcomes, costs and exposure | R02/R10 plus S3 observations: delivery, time/resource totals, compliance or quality/resource tradeoffs | Defined accounting boundary, units/price/hardware basis, overlap/revisions, missingness, actual effects and relevant quality quantity | Unknown cost as zero; sum of overlapping facets/totals; stopping observation as native termination; a universal scalar resource budget |
| M16 | Partial, malformed, failed, abstained or unavailable responses | R01/R04/R10 plus observed evidence: delivered scope, conformance, conditional quantities and declared task loss | Distinguish native commitment, fulfillment, operational effects, capture/parse failure and missing evidence; preserve intended population | Empty graph from malformed output; abstention from absence; complete-result quality from a partial artifact; universal zero quality |
| M17 | Opaque native object or new extension | R01/R02/R10 only where an independently understood property is actually observable; richer roles after qualified interpretation | Named exact reader and semantic/evaluator contracts for stronger content claims | Scientific content interpretation, compatibility with unrelated families or runnable behavior from a type label |

Rows overlap deliberately: a weighted collection can contain temporal latent graphs
and parameter intervals; a local response can include probability, ranking and
abstention. Combine obligations rather than let a preferred label erase the others.
M17's observable metadata does not establish semantic output equality: equal bytes
and semantically equal objects remain different notions.

## 5. Modifiers applying across the map

| ID | Dimension | Required distinction / additional evidence | Failure prevented |
|---|---|---|---|
| X01 | Predicate and scope | Adjacency/direct edge/ancestry/association, lag, endpoint, conditioning and applicable self-relations | Correct arithmetic for the wrong proposition |
| X02 | Reference and answer coverage | Requested, native-reported, captured/interpretable, reference-determinate and definitely answered scopes separately | Omitted facts becoming negatives; selection-dependent denominators |
| X03 | Alignment and measurement | Variable/coordinate identity, partial or multiple maps, feature/proxy transforms, allowed equivalences and losses | Joins by label/shape; unsupported inverse or source-truth transport |
| X04 | Temporal/streaming/changing domains | Lag conventions, epochs/windows/horizons, boundaries, overlap, censoring and versioned node availability | Lagged self-effects treated as loops; unseen time points or windows counted as independent |
| X05 | Relational/higher-order/distributed setting | Entity/perspective/path or tuple semantics, site namespaces, contributors, linkage and aggregation contract | Flattened pairwise graph replacing native meaning; equal local IDs merged; missing parties hidden |
| X06 | Environment/intervention/transport | Environment membership, targets/values, hard/soft/unknown intervention semantics and target-population applicability | Observational reference reused as intervention truth; unknown targets converted to no intervention |
| X07 | Population and contribution units | Case/query/proposition/time/entity/trial/draw/attempt distinctions, nesting/overlap, intended frame and weights | Pooling unlike units or treating recovery attempts/particles as independent trials |
| X08 | Comparison/transformation | Matching, output selection, actual condition conformance, preservation assumptions, explicit reference transport and declared contrast | Stability confused with accuracy; nonconforming observations silently enter the intended contrast; descriptive change automatically called causal influence |
| X09 | Sampling/randomization/dependence | Data, native, transformation and evaluator randomness; group/cluster assumptions and effective contribution meaning | Seed or cluster label treated as proof of independence; unrelated uncertainty sources pooled |
| X10 | Adaptive selection and stopping | Selection/tuning/interaction history, prior commitments, stopping/observation policy and multiplicity where relevant | Post-selection evidence presented as untouched confirmation; best final stage chosen silently |
| X11 | Availability and audiences | Raw versus aggregate/restricted/attested evidence, cutoff, access and actual computation authority | Inaccessible evidence fabricated; evaluation truth leaked into native interaction |
| X12 | Uncertainty and ambiguity | Native uncertainty, reference error/conflict, mapping alternatives, sampling and evaluator approximation | One interval claiming to represent every uncertainty source |
| X13 | Numerical and computational scope | Exact procedure/configuration, units/precision, finite/nonfinite/undefined rules, approximation and bounded computation | Silent clipping/repair, undefined ratios as zero, approximation claimed exact |
| X14 | Revisions and history | Question versus evidence versus calculation identity, source/version pins and explicit correction relations | Later knowledge rewriting prior cutoffs or changed semantics reusing an old identity |

Named examples of temporal, relational, cyclic, latent-variable and mixed-endpoint
graph families remain separate exact semantic contracts. A directed-graph checker
must not validate those families by discarding marks, cycles, time or entity roles.
No modifier certifies that its scientific assumptions actually hold.

## 6. Measurement targets and strength of claim

Every family can request one or more of these targets, when applicable. These are
question classes, not ordered support profiles and not automatically available:

1. Representation/conformance: is the object well formed under the stated family?
2. Fulfillment/coverage: what was requested, answered, delivered and judgeable?
3. Agreement/change: how do explicitly selected outputs differ?
4. Reference-relative quality: what is supported, contradicted or bounded?
5. Predictive/functional/interventional/counterfactual performance: at which exact
   operation and target, with which reference and identification basis?
6. Aggregated/contrasted performance: for which intended population and weighting?
7. Statistical uncertainty/inference: under which supported design and assumptions?
8. Resource/exposure/utility tradeoff: at what comparable accounting and utility scope?

A wrong native prediction may be a valid input to a quality measure. Do not reject
it merely because it is wrong. A violated representation premise may withhold a
specific scientific evaluator while still supporting a conformance/delivery
measurement. Applicability is scoped to the requested operation and quantity.

## 7. Worked combination pressure cases

**Partial graph reference plus complete native answer.** Among three requested
adjacencies, reference supports AB, denies BC and leaves AC undetermined. The native
answer asserts AB/AC and denies BC under evidenced closed semantics. A specifically
defined covered-label agreement has two correct judgments out of two; reference
coverage is two of three. This does not establish full-graph recovery or precision.
M01 combines R04 with X01-X03. The fractions are illustrative literal arithmetic,
not adopted metric definitions, measured native results or executed tests.

**Local abstention plus an unjudged decision.** Candidate A is a known parent of Z,
B a known non-parent, C undetermined. Native answers yes/abstain/no respectively.
A is judged correct, B has native abstention, C is unjudged. Native answer coverage,
reference-covered answer coverage, conditional quality and fulfillment are different
questions. Lost output bytes would be an additional evidence gap, not abstention.
M03 combines R04/R10 and X02/X07; no global graph is synthesized.

**Complete admissibility versus incomplete constraints.** A task requests a complete
sequence of A/B/C with exactly the requirements A before C and B before C. ABC and
BAC both fulfill that definition. A partial answer A before C is compatible but
does not fulfill the complete-sequence deliverable. If the reference supplies only
some necessary constraints, compatibility is narrower than complete correctness.
M04 combines R04 or R05 with R10; the reference roles cannot be substituted.

**Temporal weighted latent graphs.** A native collection contains graphs over
learned lagged variables, with keyed parameter members and weights. Potential source-
aligned event-mass evaluation needs temporal coordinates, a supported mapping or
invariant, correct associations, valid weight meaning, reference event/coverage and
the intended evaluation units. Missing alignment can withhold source-edge quality
while native-domain conformance or specified summaries remain possible. It does not
authorize the evaluator to select the mapping that maximizes the score. M01/M06/
M09/M12 compose with X03/X04/X07/X09; separate row support is insufficient.

**Adaptive intervention policy with partial collection and restricted oracle.**
Systems start from the same declared problem but choose different experiments.
Potential comparisons include achieved response quality, defined utility and
resource frontiers at established cutoffs. They require actual delivered actions,
outcomes, accounting and a compatible policy/oracle. Identical final data is not
assumed. Unknown final cost or termination remains unresolved. Restricted scoring
may support a restricted result, without releasing truth or answering native queries
from unauthorized reference evidence. M11/M14-M16 compose with X06-X12/X14.

## 8. Withholding and explicit alternatives

For each question/binding, retain requirement evidence and the affected operations:
supported, contradicted, unresolved or outside that requirement's applicability,
with disagreements preserved. This is a conceptual account, not a frozen flat enum.
Separate missing evidence, unsupported implementation, mathematical undefinedness,
scientific incompatibility, disputed premise and operational denial.

When a prerequisite fails, do not silently drop units, fill truth, normalize mass,
select a favorable representative, repair the graph or narrow the requested target.
An explicit derived/narrower question may still be valuable, with its own binding,
coverage and relation to the original question. Applicable bounds require an actual
bound procedure and premises; missing evidence is not automatically a bound.

| Design choice | Proposed direction | Strongest alternative | Cost and failure prevented |
|---|---|---|---|
| Organize breadth | Compose independent question/output/reference/design contracts | One large system-specific evaluator type, or one universal score | More compatibility tests; avoids duplicated adapter policy and lossy uniformity |
| Reference uncertainty | Preserve role, scope, conflict and uncertainty; use explicit set/bound procedures where applicable | Convert every reference into one hard truth object | Richer result accounts; avoids invented certainty and arbitrary negatives |
| Incomplete evidence | Scope each supported quantity and retain intended populations/dispositions | Drop unusable rows or fill every non-result with zero | More denominator/accounting work; prevents population drift and fabricated performance |
| Extending families | Exact named semantics plus qualified evaluators and compatibility checks | Accept arbitrary extensions as scientifically supported | More qualification work; prevents a metadata pass becoming a universal-integration claim |
| Inference | Explicit design-compatible methods, separately supported from descriptive calculations | One automatic interval/test across all rows | More prerequisite evidence and held claims; prevents unsupported precision/adaptive confirmation |

All proposed directions reuse S1 objects/domains/provenance, S2 scientific intent
and populations, and S3 evidence/authority/cutoffs. No current adapter/evaluator is
declared to satisfy an entire map row by those foundations alone.

## 9. Existing implementation boundary and source links

Inspected foundations:

- [S1 connection capability map](system-connections-capability-map-2026-11-01.md)
  and [output subtype design](system-connections-output-subtypes-2026-11-01.md).
- [S1 implemented support](subsystem1-implemented-support-2026-11-01.md) and
  [family checks](../connections/families.py). Selected structural checks preserve
  richer evidence but do not establish scientific correctness, full CPDAG/PAG
  conformance, posterior validity or generic mathematical evaluation.
- [S2 reference/response semantics](subsystem2-reference-response-semantics-2026-11-02.md),
  [composable contracts](subsystem2-family-profile-lifecycle-contract-2026-11-02.md),
  [implemented scope](subsystem2-implemented-scope-2026-11-02.md) and
  [evaluation bindings](../experiments/evaluation.py). The installed built-in
  measurement descriptor is metadata-only; it supplies no generic metric.
- [S3 implemented scope](subsystem3-implemented-scope-2026-11-04.md) supplies
  operational evidence, cutoffs and recovery, not S4 mathematical qualification.
- [S4 opening proposal](subsystem4-structure-design-2026-11-04.md) records inspected
  legacy graph/effect/calibration/ranking helpers and their compatibility limits.

Earlier pending-status documents retain their historical acceptance/implementation
history; the implemented addenda govern current support. Old paths in historical
documents are not rewritten. The new map uses current standalone links. No runtime,
old scoring convention, threshold, tolerance, result, certificate, research helper,
paper, tracker or site is changed. No new scientific execution is performed.

Documentation checks can establish source/link consistency and unchanged package
compatibility. They do not qualify M01-M17 or prove exhaustive coverage. Future
qualification needs scoped mathematical examples/oracles, semantic/refusal cases,
population/design counterexamples, justified transformation checks and native
integration evidence for the actual claims made. This pass chooses no such suite
or initial supported profile and creates no implementation DAG.

## Where we're going

Review this space and its scientific boundaries before selecting support profiles.
Then choose explicit combinations and their minimum/conditional obligations,
keeping preservation, interpretation, calculation, inference and native validation
claims distinct. Carry accepted question/applicability choices into the detailed
S4 contracts, review complete composed examples, and only then freeze serialization,
interfaces, validation gates and a build DAG. Implementation still requires an
explicit user go.
