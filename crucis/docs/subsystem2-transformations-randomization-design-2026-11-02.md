# Subsystem 2: transformations, preservation and randomization

Tickets: DLV-08, DLV-09; related DLV-10, DLV-06/07 and ADV-01.
Date: 2 Nov 2026, America/Los_Angeles.
Status: proposed design. Uzair accepted continuing from conditions/information
policy and requested concrete preservation, reference-applicability and repetition
examples. Detailed contracts below are not approved serialization, implementation,
new measurement rules or public protocol adoption.

Sources: [conditions/information](subsystem2-conditions-information-design-2026-11-02.md),
[reference/response semantics](subsystem2-reference-response-semantics-2026-11-02.md),
[case obligations](subsystem2-case-membership-minimum-2026-11-02.md),
[S1 domains/mappings](system-connections-domains-mappings-2026-11-01.md),
`audit/controls/{transforms,effects,l1}.py`, `audit/core/{harness,battery}.py`
and `audit/connections/domains.py`. Examples/counts/algebra below are illustrative,
not native executions, new empirical findings or tests of implemented S2 behavior.

## 1. Separate recipe, realization, input checks and response behavior

A transformation specification declares a typed source-to-derived operation and
its scientific purpose. A realized application identifies the actual source,
parameters/randomness, derived evidence, mappings and checks. An immutable recipe
does not prove that inputs were correctly materialized or delivered.

Preservation checks concern properties that the transformation promises to retain.
Response invariance/equivariance concerns how the native system behaves under that
change. Do not require unchanged native answers as an input-readiness gate: those
answer changes may be precisely the audit's target. Stochastic outputs require
the declared distributional/summary comparison rather than automatic byte equality.

S2 declares operations, binding times, invariants and randomization relationships.
S1 represents source/derived domains, artifacts, presentations and observations.
S3 will materialize/enforce authorized plans. S4 computes declared effects and
uncertainty; S5 assigns findings. No action or spend is authorized here.

## 2. Proposed transformation obligations

| ID | Responsibility | Failure prevented |
|---|---|---|
| T01 | Identity/exact contract revision, purpose, authoring timing and condition/task bindings | Retrospective changes to what the operation was intended to test |
| T02 | Exact source snapshots/domains/selectors and applicability prerequisites | Transforming a different version, scope or unsupported evidence family |
| T03 | Procedure/implementation/dependency identity, parameters and fitted-state provenance where applicable | A seed/function name concealing different preprocessing or defaults |
| T04 | Declared changes and preserved properties, with explicit equality/predicate meanings | Treating any changed array as a valid controlled intervention |
| T05 | Randomness roles, source/stream identity, sampling law and explicit cross-condition coupling | Accidental sharing or unestablished independence hidden behind one seed |
| T06 | Derived domain/representation identities, mappings, losses and membership/overlap lineage | Reinterpreting proxies, aggregated variables or subsets as unchanged independent evidence |
| T07 | Reference applicability target, mapping/derivation procedure and limitations | Carrying an inapplicable truth graph into a changed measurement task |
| T08 | Ordered composition/dependency bindings and constraints | Assuming operations commute or that local checks prove the entire pipeline |
| T09 | Actual realization receipt: inputs, outputs, selected indices/maps/random parameters and evidence availability | A planned recipe masquerading as a captured transformed input |
| T10 | Preservation/applicability check procedure, actual result, scope, evidence and expected values | A pass label with no demonstrated predicate, or unknown checks treated as passes |
| T11 | Information/disclosure boundaries and actual presentation handoff | Leaking evaluator maps, targets or source metadata through a transformed payload |
| T12 | Failure/amendment history and links to intended trials/populations | Redrawing until favorable outputs appear or silently removing invalid materializations |

These are logical obligations, not frozen fields or twelve required files. Reuse
shared definitions and S1 references. A historical reconstruction may identify the
observed transformation with scoped missing recipe/randomness evidence; preservation
does not grant an unsupported prospective/comparability claim.

## 3. Preservation has a stated predicate and scope

Useful distinct checks include:

- Exact byte equality over the specifically selected artifact/payload region.
- Equality under a named serialization/text normalization, including what was omitted.
- Parsed-value/schema/mask equality under declared dtype, missing/nonfinite and
  representation rules; decoded equality is not a whole-file byte claim.
- Equality after a specified coordinate/identity mapping, checked on the actual
  cells, axes, labels and associated metadata as relevant.
- Numerical agreement under a fixed tolerance rule, units, finite-value policy
  and scope; a tolerance pass is not exact equality.
- A scientific property under explicit assumptions, target and supporting evidence.
  Finite consistency checks alone do not prove universal causal equivalence.

These predicates are not one universal hierarchy. The transformation selects what
it promises. Shape equality is only one prerequisite. Mapping round trips check
the mapping but do not prove that an array or intervention mask followed it.
Statistical checks of a randomized generator also differ from exact properties
of a particular realized sample; a noise draw need not have exactly its expected
mean or variance.

Each check identifies its subject, procedure/version, expected property, actual
scope and evidence. Pass, fail, unknown and not checked remain distinct. A known
unsupported requirement produces a scoped readiness gap, not a fabricated native
crash or a favorable default.

## 4. Names and presentation order

Illustrative canonical variables are [A, B, C], with reference A -> B -> C.
A label-only operation changes selected display strings, preserving canonical
variable identities, numerical values, rows/masks, order and other declared fixed
channels. The actual payload and mapping are checked. A changed header means the
whole file is not byte-identical; select the correct value/body equality claim.

For a presentation permutation, show [C, A, B]. The shown-to-canonical index map is
[2, 0, 1]; the canonical-to-shown map is [1, 2, 0]. Thus reference A -> B becomes
shown edge 1 -> 2 and B -> C becomes 2 -> 0. These are coordinate views of the same
reference, not a new causal truth or material to give the system by default.

Required checks: unique valid domain membership for a permutation; inverse
consistency; correctly moved values/masks/labels/units; correctly aligned intervention
targets and other axis-bound metadata; and correct output/reference coordinate
bindings. Only applicable supported object families are mapped. Never map a local
claim, temporal endpoint or model quantity by assuming it is an ordinary edge array.

After mapping returned native objects to the canonical domain, differing answers
remain audit evidence. Do not repair them to pass the input transform check.
A labels-plus-order study declares both factors and their coupling. For a labels-only
contrast, hold the chosen presentation permutation fixed across its matched arms.
A different permutation draw is a distinct transformation realization.

Constraints are explicit: a requested no-fixed-point name swap is impossible for
one variable, and random relabeling/order draws may repeat content. Report support
limits and preserve draw occurrences; do not silently deduplicate or manufacture
a nontrivial intervention. Prespecified rejection sampling for an admissible map is
different from selecting maps after inspecting native performance.

## 5. Subsampling: preserve provenance, qualify reference inheritance

Example: select 500 of the 1,000 source rows without replacement. Bind the source
row identities, sampling procedure, selected indices/order and aligned data/masks/
weights/environment metadata. Check the requested actual count and membership.
No duplicate row IDs are allowed under this without-replacement contract.

For eligible iid observations from the same population/mechanism, a sample-size
control can retain the structural reference with its assumptions and identity
bindings while changing finite-sample information. A filter based on observed
outcomes, intervention composition, subject membership or time is not automatically
the same sampling intervention. State its population and reference consequences.

Nested budgets may deliberately use one sampled row order to obtain a 250-row
subset inside the 500-row subset. Another design uses separately sampled subsets
from the same parent. Both retain dependence/overlap; neither creates independent
source datasets merely by assigning two seeds. Decide nestedness in advance.

Time series may require ordered windows/blocks, panels may require subject-level
selection, and interventional cases need appropriate strata/target alignment.
Sampling individual rows uniformly is not a universal generic rule. A request
larger than available data needs an explicit cap/eligibility rule and actual-count
receipt; unchanged returned input cannot silently count as a realized smaller-N arm.

Subsets used as conditions retain the source case and derived evidence lineage.
If registered for standalone reuse as cases, retain their parent/overlap relations.
They do not become independent of their source or sibling subsets.

## 6. Noise and variable transformations: reference meaning may change

Adding measurement noise changes the observed quantities. Preserve the noise law,
scale/units, dependence structure, seed/realization, clipping/masks, calibration
statistics and their source. Bind measured proxies to their original quantities
through an explicit measurement relation; equal column names do not establish
unchanged variable meaning or causal reference applicability.

A concrete analytic counterexample explains the issue. Let X, U, V and E be
independent standard-normal variables; Y = X + U; Z = Y + V; and Y* = Y + E.
For the clean chain, Cov(X, Z | Y) = 1 - (1 x 2)/2 = 0. With the noisy middle
measurement, Cov(X, Z | Y*) = 1 - (1 x 2)/3 = 1/3. Joint Gaussianity makes the
conditional covariance informative about the corresponding conditional independence.
Thus the same missing X-Z conditional relationship cannot be assumed for the
three measured variables [X, Y*, Z]. This is illustrative algebra under the stated
model, not a newly collected result or a new audit metric.

Two different evaluation questions are possible: recovery of the explicitly
defined underlying clean structure from noisy measurements, or discovery of the
relationships among the measured proxies. Bind the actual requested target and
native output interpretation before using a reference. The latter may need a new
reference or reference family; the former requires a justified source/proxy alignment
and an honest latent/measurement target. Do not switch targets after outcomes.

Similarly, unit conversion, discretization, aggregation, feature extraction and
mixing variables have different preservation contracts. Even invertible mixing
need not preserve the original variable-level graph. A componentwise conversion
requires its own invertibility/units/assumption checks for the claimed target;
effects and thresholds may still require transformation. Preserve losses and
supported meanings instead of claiming all numeric changes retain truth.

Reference applicability can therefore be: retained under established bindings;
re-expressed through an evidenced coordinate/view mapping; newly derived for a
changed target; limited to a justified sub-scope; or unresolved/inapplicable for
the requested comparison. These are scoped assessments with reasons, not a new
truth-tier taxonomy or permission to change existing stored results.

## 7. Composition is part of the treatment

Represent an ordered dependency structure of operations and their actual inputs.
Do not assume names/order, selection/noise or preprocessing commute. Source-scoped
label maps can commute with permutations under established bindings; position-based
renaming may instead affect different variables when operations change order.

For noise scaled by the input sample's standard deviation, subsampling first can
change the scale used to generate noise. Adding noise before selecting rows is a
different recipe. Specify which source/statistics are used, whether they are fitted
on permitted data and what is revealed to the native system. Store intermediate
bindings/receipts needed to justify the final invariant/reference assessment.

Native preprocessing remains part of the native subject/configuration. Auditing
it is different from silently replacing it in the adapter. A successful check on
one pipeline step does not establish the scientific validity of the whole chain.

## 8. Randomness must have roles and coupling rules

| Role | What varies and what it does not establish |
|---|---|
| Collection selection | Chooses cases from a defined source pool; not evidence of independent system outputs |
| Data generation/episode realization | Produces new source evidence/state; repeated realizations can still share mechanisms, participants or upstream causes |
| Transformation draw | Chooses labels, permutations, rows, noise or supplier corruption; not necessarily a new dataset-generating mechanism |
| Condition assignment | Assigns treatments to experimental units under the specified scheme; distinct from randomizing variable order |
| Execution order | Randomizes/counterbalances timing/order under state constraints; does not by itself remove carryover or backend drift |
| Native inference/initialization | Controls available native stochastic settings and state; the same seed need not reproduce remote behavior or imply useful coupling |
| Adaptive action/source randomness | Governs policy decisions and subsequent source responses; equal budgets do not imply matched observations |
| Analysis resampling | Produces uncertainty calculations from captured evidence; bootstrap draws are not new native runs or independently observed cases |

Proposed bindings identify stable case/realization/condition/transformation/repeat
keys and the randomness role. Shared randomness uses an explicit coupling-group
identity and procedure. Independent streams use their documented separation and
assumptions. Exact key/seed derivation and generator/version contracts remain open.
Do not derive one undifferentiated seed from execution order or assume different
integers prove independence. Known source/provider/state limitations stay visible.

Reproducibility needs the actual procedure/library, stable input ordering, random
state/stream contract where available, parameters and realized maps/indices/artifacts.
A seed alone is insufficient. Moving a file should not change a scientifically
fixed transformation unless path is a declared factor; new bindings should use
stable scoped identities accordingly. Existing filename-based legacy behavior is
retained rather than silently changed.

Public development randomization can use declared public seeds. Restricted/sealed
procedures use authorized commitments/references rather than exposing protected
random material. No real seed store is opened, copied, generated or altered here.

## 9. Matched conditions and independent repetitions

Illustrative design: ten source scenarios, one materialized dataset per scenario,
three name conditions and three requested native repetitions per condition.
This defines 10 x 1 x 3 x 3 = 90 planned scientific trials. Matching can occur at
the case/dataset level while native draws are independently requested within and
across arms. Shared native randomness is a separate optional design choice.

| Design element | Meaning |
|---|---|
| Same dataset across real/neutral/swapped | Matched source evidence for the name contrast |
| Same nuisance permutation across those arms | A controlled nuisance factor, not a new source realization |
| Three native draws per arm | Repetition for conditional native variability, subject to actual state/backend independence assumptions |
| A new data sample from a scenario | A new realized case nested in that scenario; it can support a separately matched set of arms |
| A new generator/mechanism or new population | Another scientific dimension whose selection and dependence must be declared |
| A retry, reconnect or checkpoint restart | Another attempt/continuation under the existing trial policy, not an automatic new scientific repetition |

Equal repetition indices do not prove paired random draws. If no valid coupling
is established, comparisons can still be paired by case/dataset using the declared
repetition summary/hierarchical analysis. Do not invent pair identity by joining
outputs in returned order or require only successful arms without an analysis rule.

Common-random-number coupling is permissible when the native interface and design
support it. The same seed may be consumed differently after branching, and coupling
does not guarantee reduced contrast variance. Record its actual scope/evidence;
do not assert bitwise identical internal randomness or universal independence.

If each scenario instead has three independently requested data realizations, the
layout defines 10 x 3 x 3 x 3 = 270 planned trials and 30 realized dataset cases,
still grouped by ten source scenarios. This does not establish 270 independent
datasets or 30 independent mechanisms. Overlapping people, sites, windows and other
sources may require additional dependence relationships beyond scenario identity.

One extra retry attempt does not change the 90-trial design into 91 scientific
repetitions. Captured attempts, started native work and cost remain separate actual
counts. Equal response bytes do not merge genuinely separate occurrences; replayed
responses do not create fresh stochastic samples.

Condition assignment/execution scheduling, independent data generation, shared
transformation draws and native repetitions must remain distinguishable. Randomized
execution order can reduce particular time/order confounding under its assumptions;
it is not proof of equivalent backend versions, reset state or information exposure.

## 10. Materialization gates and failure handling

Before an eligible prospective native request, bind the required exact source,
transformation realization, derived domain and reference applicability, and retain
required check evidence. Delivery/actual-input evidence follows its own boundary.
Receipts include failures/unknowns with actual scope; a cached manifest digest is
not proof that currently used bytes still match it.

A failed required input invariant blocks the corresponding ready-to-run claim.
Retain the intended slot and reason. Do not call it a native crash, silently change
the condition, redraw until native outputs look favorable or drop the slot from
the original population. A predeclared admissibility/rejection procedure may draw
until a valid input transformation is obtained within its resource/stopping rules;
its sampling distribution and attempts remain documented.

Post-output response checks are scientific observations under the analysis contract,
not eligibility filters that remove non-invariant systems. If the wrong input was
actually delivered, retain intended and observed bindings and apply the declared
nonconformance/missingness policy. Reconstruction of old inputs/recipes keeps its
actual timing and unknowns rather than acquiring prospective commitment.

## 11. Existing footing and tradeoffs

The existing transform helpers provide seeded name maps, permutations, reference
index moves, row subsets, noise and knowledge corruptions. Their exact assumptions
are narrower than this proposal: row selection is not a general temporal/grouped
sampler; no-op behavior for requests at least as large as available data must not
be misread as a realized smaller sample. Noise uses the supplied X's column standard
deviations. The hash helper checks normalized header-free text, not arbitrary
scientific equivalence or exact original file bytes.

The current harness permutes columns and maps selected graph/variant/source/stage
outputs back. It does not supply a universal reader for every S1 output family.
Its shown permutation depends on item/filename conventions. S1 domains distinguish
source identities, labels and mapped coordinates; broader transformation and
reference-applicability validation remains proposed S2 work.

Existing effects code intersects available units and clusters paired differences;
L1 helpers use particular successful-output populations and scenario summaries.
Preserve their historical meaning/results. The new repetition structure needs
explicit intended/eligible/attempted/answered/paired/scoreable populations, not an
unannounced replacement of existing denominator or interval rules.

| Proposed direction | Strong alternative | Cost and failure prevented |
|---|---|---|
| Typed recipes plus realized receipts/checks | Store only a function name and seed | More provenance/storage; prevents unsupported reproduction and preservation claims |
| Reference applicability assessed per target/operation | Reuse the original graph after every numeric change | More derivation/validation work or visible gaps; prevents wrong-target accuracy claims |
| Separate input invariants and native response outcomes | Require output invariance as a gate | More scoped assessments; prevents removing the very failures the audit should measure |
| Role-specific randomness with explicit coupling | One global seed and flat repeat counter | More bindings; prevents false pairing, pseudoreplication and accidental stream dependence |
| Explicit composition and native preprocessing boundary | Treat transforms as an unordered bag | More pipeline checks; prevents changed variable targets, fitted-state leakage and silent native-method modifications |

No stored number, certificate, threshold, regime, tier, shared score logic or native
source was changed. Contract/metric changes remain proposals to the relevant owners.

## 12. Future acceptance examples and open decisions

| ID | Required design/validation example |
|---|---|
| A01 | Header-only rename preserves the promised value/schema/mask scope without claiming whole-file byte identity |
| A02 | [C,A,B] presentation and its inverse correctly map values, labels, intervention targets and supported outputs/references |
| A03 | A native output change survives input-readiness checks as audit evidence rather than an exclusion |
| A04 | A 500-row subset binds its source indices/metadata; a nested 250-row subset retains overlap/dependence |
| A05 | Temporal/grouped/interventional evidence rejects an unsupported iid-row recipe or uses its declared family-specific procedure |
| A06 | Measurement-noise reference applicability distinguishes clean-source recovery from proxy-variable discovery |
| A07 | Selection/noise composition records the statistics and order actually used |
| A08 | Shared nuisance maps are matched across arms while native repetitions retain their own roles and independence limits |
| A09 | Different data realizations remain nested in their shared source; replay, bootstrap and retries do not add independent cases |
| A10 | Moving evidence does not accidentally reseed a declared fixed new transform; legacy mappings remain reproducible as originally specified |
| A11 | Missing/failing preservation evidence retains intended population membership and cannot silently pass |
| A12 | Unsupported no-fixed-point swaps, repeated random maps and prespecified rejection draws retain honest applicability and multiplicity |

These are future acceptance obligations, not passed runtime tests or added empirical
coverage. Open choices include exact transformation families and parameter contracts,
state/materialization lifecycle, equality/tolerance and reference procedures, stream
derivation/coupling algorithms, scheduling/carryover, comparison populations and
missingness. They require joint examples and review before serialization freeze.

## Where we're going

Review the preservation/reference cases and randomization roles. Next develop
comparison, repetition and missingness contracts: the precise contrast, population,
matching unit, nesting/dependence, handling of incomplete arms and scientific meaning
of retries/resumed attempts. Reconcile them with these transformation bindings;
implementation and public adoption remain separate later decisions.
