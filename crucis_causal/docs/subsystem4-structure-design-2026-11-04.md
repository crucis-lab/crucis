# Subsystem 4: measurement and statistical procedures

Tickets: DLV-08, DLV-09; related DLV-10.
Date: 2026-11-04, America/Los_Angeles.
Status: opening design proposal based on source inspection. No S4 implementation,
contract freeze, mathematical procedure adoption, scientific campaign or paper
change is authorized by this note. Recommendations below await user adjudication.

## 1. Continuation and evidence boundary

The user requested S4's overall structure, guiding principles, existing foundations
and important choices/tradeoffs, with no implementation. This follows S3's completed
local implementation at `bc926d39ac224df0ef1d09234a665aa2afeef130`.

S3's prior receipts establish 118 S3 tests with no failures/errors/skips; final full
gates of 453 tests with no failures/errors and 26 inherited availability skips;
1,298 legacy comparisons at unchanged 0.001 tolerance; and 14 stored plus 14 fresh
certificate verifications. These are existing receipts, not freshly rerun S4 checks.
No S4 measurement family, inference method or native integration is thereby qualified.

See [S3 implemented scope](subsystem3-implemented-scope-2026-11-04.md),
[release review](subsystem3-release-review-2026-11-04.md) and
[methodology index](subsystem3-methodology-index-2026-11-03.json). Historical docs
retain their earlier paths and pending statuses; current source uses `crucis_causal`.

## 2. Responsibility and neighboring subsystems

S4 should produce a reproducible, scoped measurement from selected evidence and
an explicit scientific question. A number's computational availability is distinct
from its mathematical applicability and the scientific interpretation it supports.

| Owner | Responsibility retained |
|---|---|
| S1 | Native output objects, domains/mappings, artifacts, interpretations and provenance |
| S2 | Experimental questions, conditions, units, populations, selected outputs/references/mappings, declared evaluation and analysis rules |
| S3 | Actual execution, input realization, observation cutoffs, permissions, resource/exposure facts, recovery and publication |
| S4, proposed here | Measurement semantics, applicability checks, per-unit calculations, explicit aggregation, statistical procedures and traceable measurement results |
| Later finding layer | Whether measured evidence satisfies a separately versioned finding/decision rule |
| Later reporting/certification layer | Presentation and certification of the appropriately scoped evidence and findings |
| Auditor-validation work | Independent validation of auditor behavior and scientific detection performance; S4's mathematical tests are only one foundation |
| Separate research-tooling project | Generic research/evidence workflow and reviewer engine; do not duplicate that engine in Crucis |

S4 must not create authority, choose a more convenient experiment, reconstruct
unknown native history, change an output selection silently or overwrite a prior
measurement when later evidence arrives. It must not collapse around graph-only
adapters or the existing benchmark harness.

## 3. Existing foundations inspected

These source observations are not new mathematical validation results.

| Source | What exists | Boundary |
|---|---|---|
| [S1 connections](../connections/) | Native output families, domains, mappings, artifacts and declared interpretations | Preservation/shape does not establish correctness or universal family interpretation |
| [S2 evaluation](../experiments/evaluation.py), `record_population`, `bind_evaluation`, `install_metadata_descriptor` | Intended units retained, unresolved dispositions, selection/applicability checks and exact external measurement descriptors | The built-in descriptor is explicitly metadata-only; no generic scientific measurement implementation follows from a binding |
| [S2 evaluation tests](../../tests/test_audit_experiments_evaluation.py) | Missing observations are retained without zero scores; ambiguous finals, outcome-based exclusions and unsupported descriptors are checked | Existing scoped tests do not qualify future S4 numerical procedures |
| [S3 core](../execution/core.py), [collection](../execution/collection.py), [recovery](../execution/recovery.py), [publication](../execution/publication.py) | Supplied service boundaries, actual evidence/cutoffs, interrupted-effect accounting and immutable publication | S4 should reuse these operational mechanisms rather than build another runner or permission system |
| [Legacy L0 metrics](../metrics/l0.py), `truth`, `score_graph`, `score_record`, `summarise_arm` | Graph/reference routing; expected versus committed direction measures; coverage/accuracy coordinates; selected intervention-target claims; historical summaries | Existing protocol-specific semantics, not generic defaults |
| [Legacy effects](../controls/effects.py) and [paired helpers](../_support/score/paired.py) | Paired differences, pooled ratios, cluster resampling, intervals and other existing numerical routines | Their units, pairing, randomization and assumptions need explicit applicability before generic reuse |
| [Calibration helpers](../_support/score/calib.py), [ranking helpers](../_support/score/rca.py) | Retained confidence/coverage and root-cause ranking calculations | Presence of helpers is not a completed generic evaluation path; the legacy finding layer still marks some capabilities unrun |
| [Legacy findings](../findings.py) | Existing versioned finding decisions, thresholds and labels | Numeric procedures and decisions coexist in legacy code; preserve that historical route and keep proposed S4 ownership distinct |
| [Legacy rerun tests](../../tests/test_audit_rerun.py), [certificate verification](../report/certificate.py) | Recorded compatibility and certificate routes | Prior numerical parity is neither proof of all mathematical definitions nor universal statistical validity |
| [Evidence paths](../core/paths.py) | Explicit `CRUCIS_DATA_ROOT`; `import_paths` is a compatibility no-op | Data access does not authorize importing sibling research, harness or analysis code |

Important inherited choices visible in source:

- `score_graph` retains both a historically randomized orientation convention
  for undecided pairs and committed-direction measures. Neither is a universal
  interpretation of uncertainty in all causal output families.
- `summarise_arm` distinguishes completed-run summaries from a historical
  delivered measure assigning zero to failed executions. It also uses legacy
  missing-value/cost conventions. Preserve those meanings under their original
  profile; do not silently install them as S4 defaults.
- Reference tiers distinguish legacy accuracy from agreement; a mismatched
  reference is refused in the ordinary route. Generic S4 should retain the
  evidence and applicability behind those distinctions, not merely copy a tier name.
- Legacy paired routines operate on common keys and scenario clusters. Generic
  S4 needs an explicit intended frame, unmatched dispositions and a justified
  dependence model rather than silently reducing every question to common keys.

No listed runtime, scientific helper, threshold, legacy result or paper file is
changed by this opening proposal. Retained helpers are Crucis-owned sources with
extraction provenance; the four research B5 modules remain outside this scope.

## 4. Proposed guiding principles

1. Start with the quantity/question and its scope. An identical metric label can
   hide different outputs, references, denominators or uncertainty conventions.
2. Preserve native meaning. Derivations and alignments are explicit, separately
   identified views; adapters do not invent grading policy.
3. Separate a computed value from the support for interpreting it. Structural
   validity, applicability, evidence availability and inferential assumptions are
   distinct. Declared independence is not proof of independence.
4. Keep intended units and missingness visible. Zero, unreported, abstained,
   outside-reference scope, mathematically undefined and unsupported are not
   interchangeable. Legitimate combined delivery/quality measures require an
   explicit definition and retain their component outcomes.
5. Generalize common machinery while allowing explicit semantic families. Share
   identity, provenance, units, masks, selection, aggregation and result handling;
   do not impose one graph metric on local answers, orders, weighted collections,
   temporal objects, latent mappings or intervention questions.
6. Make every scientific convention inspectable and versioned. No automatic
   best-reference, best-mapping, latest-output or most favorable procedure selection.
7. Keep measurement distinct from finding decisions. S4 may compute a statistic,
   interval or p-value under an applicable procedure. A later layer decides how
   that evidence supports a registered finding; current thresholds are unchanged.
8. Treat each uncertainty source explicitly. Native uncertainty, incomplete
   references, ambiguous mappings, sampling variation and evaluator Monte Carlo
   variation must not silently become one purported confidence interval.
9. Preserve evidence cutoffs and audience boundaries. Later data produces a new
   result and relation to its predecessor, not a rewritten earlier assessment.
   Access to scoring truth does not permit leaking it into an interactive system.
10. Qualify support by actual procedure/input/profile tests. A registry entry,
    callable, valid result schema or historical parity pass is insufficient alone.

## 5. Proposed seven responsibility boundaries

These are discussion boundaries, not approved modules or frozen record blocks.

| Responsibility | Question to answer | Main failure prevented |
|---|---|---|
| 1. Measurement question and applicability | What quantity is requested, against what reference/evidence, under which premises? | Correct arithmetic for the wrong scientific question |
| 2. Evidence selection and semantic preparation | Which exact outputs, domains, mappings, masks, references and S3 cutoffs are inputs? | Silent coercion, post-hoc selection, future leakage or unsupported absence |
| 3. Per-unit measurement | What can the installed semantic procedure establish for one declared unit? | Forcing heterogeneous or partly known answers into one scalar/graph |
| 4. Population, contrasts and aggregation | Which units contribute, with what weights, pairing, dependence and denominator? | Dropped failures, duplicated retries or changed target population |
| 5. Uncertainty and inference | Which procedure is applicable to that design and actual selection/stopping history? | A generic interval/test making unsupported validity claims |
| 6. Calculation reproducibility and operational handoff | Which exact implementation, parameters, randomization and numerical environment were used, and which effects require S3? | Hidden defaults, unrecorded Monte Carlo choices or a duplicate execution/authority engine |
| 7. Measurement result and evidence account | Which values, bounds, contributions, limitations and provenance can be published at this cutoff/audience? | A scalar concealing unavailable evidence, invalid assumptions or later corrections |

A result may legitimately be a count, ratio with its numerator/denominator, vector,
table, admissible set, bound, or a withheld calculation with a reason. Exact forms
and the minimum/conditional record remain to be designed; this is not a schema.

## 6. Important choices and alternatives

| Choice | Proposed direction | Strongest alternative | Cost and failure prevented |
|---|---|---|---|
| Common policy versus native semantics | Common accounting/validity machinery with explicit versioned semantic evaluators; native adapters retain mechanics and meaning | One universal representation/score, or independently scoring each adapter | More explicit family contracts and tests; prevents graph-only coercion and incomparable adapter-specific grades |
| Legacy reuse | Preserve the old route; expose any future reuse through an explicit compatibility profile after semantic review | Generalize/refactor old numerical code in place immediately | Some wrappers/parallel contracts; preserves paper evidence and exposes historical conventions |
| Metric selection | Bind quantity, inputs, conventions and procedure version explicitly | Choose an available metric from the output type or adapter name | More setup and held cases; prevents silently answering a different question |
| Multiple valid answers and ambiguous mappings | Use a declared equivalence/invariant, set/bound or scientifically justified selection procedure | Pick one convenient representative or optimize the score | More complex results and potentially expensive evaluation; avoids arbitrary penalties and optimistic selection. A declared optimization still needs justification |
| Missing/failed/abstained results | Retain distinct dispositions; qualify each requested estimand and denominator | Drop unavailable cases or assign every non-result zero | More explicit results; prevents population drift and unknowns becoming poor-quality answers |
| Population aggregation | Explicit weighting, matches, exclusions, dependence and component counts | Average all scalar rows, or intersect available keys silently | More population bookkeeping; avoids treating claims, attempts and scientific repetitions as equivalent units |
| Inference | Explicit installed procedures with assumptions and design/selection applicability; descriptive quantities may remain available when inference is withheld | One default bootstrap or automatic procedure guessing | More applicability work; prevents unsupported intervals, adaptive-selection claims and false precision |
| Timing and access | Post-run evaluation as the ordinary starting profile; explicit separately admitted online procedures where the experiment permits them | Give measurement code unrestricted access during every native run | More cutoff/audience checks; avoids truth leakage while retaining future interactive scope |
| Extensibility and computation | Explicit pinned evaluator implementations; pure calculations where possible, authorized effectful computation through S3 | Load arbitrary code from metadata or build a separate S4 job runner | More declaration/preparation work; avoids untraceable code selection and duplicated operational semantics |

The recommendation is the proposed direction in each row. No user acceptance of
these individual choices is inferred from the request to open S4 discussion.

## 7. Concrete pressure examples

**Global graph with partial reference.** A pair not covered by the reference is
not established absent. A per-pair correctness calculation must expose its eligible
scope; that does not by itself identify whole-graph precision/recall. An undirected
native relationship is not automatically randomly oriented or scored as a false
directed edge. The requested convention and family semantics determine what can
be measured. No new graph metric definition is adopted here.

**Local answer or abstention.** A system answering a question about X need not
return a global graph. Evaluate the declared local question and available reference
coverage. A valid abstention and an unobserved response remain distinct. Conditional
quality and response coverage can be separate quantities; a combined measure needs
its own explicit definition.

**Ordering and valid alternatives.** A reference may permit several orders, for
example because some variables have no required precedence relation. Comparing
every output with one arbitrary total ordering changes the question. A procedure
must specify which precedence claims or admissible alternatives it assesses.

**Matched conditions and repeated attempts.** A name-condition contrast must use
the S2 scientific units and intended matches, retaining unmatched outcomes. An
S3 checkpoint restart is not a new independent scientific repetition. A cluster
label or random seed is a declaration, not by itself evidence that an inferential
assumption holds. Neither a per-case average nor a pooled claim ratio is the
automatic answer for every scientific target.

**Probabilistic, weighted or richer outputs.** A confidence score, probability of
an edge, probability over graphs, ranking and interval for an intervention effect
refer to different objects/events. Their reference requirements and contribution
units differ. Preserve particle weights, associations, variable domains and any
alignment ambiguity. Calibration is not established by matching arrays' shapes.

**Interrupted execution or unavailable cost.** A closed collection can retain an
unknown native outcome. A captured partial output may support one descriptive
quantity but not final-output quality. Missing cost is not free execution; an
unsettled bill or incomparable resource scope may prevent an aggregate.

**Later evidence and restricted scoring.** A new reference or observation creates
a new evaluation basis. Earlier results retain their original cutoff. A private
reference may permit a restricted computation or attestation without permitting
publication of its raw inputs or feedback to the system under audit. A reproducible
public statement must distinguish available raw verification from restricted evidence.

## 8. Validation direction, not an implementation plan

Future evaluator qualification should combine independently specified small
examples, mathematical edge cases, justified invariance checks, population and
missingness counterexamples, appropriate numerical/reference checks and explicit
failure/withholding cases. Metamorphic checks require a reason the proposed
transformation preserves the particular quantity; they are not automatic tests
of every metric. Examples should span graph, local, ordering and richer output
families instead of only the current legacy battery.

Any reuse of legacy routines needs its own scoped validation and once-appropriate
compatibility evidence, without changing stored goldens or the 0.001 legacy
tolerance. A mathematical oracle or external benchmark would require its actual
source/version and limitations. No new numerical, statistical or native evidence
is claimed by this source-inspection note. Broader auditor-validation experiments
and the generic reviewer engine remain separate work.

## 9. Open work and acceptance history

Already accepted foundations remain S1/S2/S3 and their recorded decisions. The
present user authorization is S4 design discussion only. Still open: the supported
measurement capability map, initial scope/profiles, request semantics, minimum and
conditional result account, applicability/evaluator contracts, exact interaction
and recovery rules, legacy mapping, mathematical validation plans and final build
DAG. No serialization, method signatures, inference default or build bundle is
frozen here. No S4 implementation begins until explicitly authorized.

The current milestone reviews local source anchors and preserves the existing
subsystem/scientific boundaries. Its ordinary staged-tree gate is separate from
future S4 mathematical or integration qualification. Local commits do not imply
remote publication, native execution or paper adoption.

## Where we're going

Discuss this structure and its boundaries first. If the structure is accepted,
deepen measurement-question identity and applicability using complete global,
local, ordering and richer-output examples, then map the full capability space
before selecting supported profiles. Iterate the complete design before freezing
contracts and an implementation DAG. Keep accepted choices separate from proposals
and preserve a source-linked methodology account for the paper workstream.
