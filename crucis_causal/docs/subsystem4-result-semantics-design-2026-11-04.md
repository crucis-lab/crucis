# Subsystem 4: result semantics and premise evidence

Tickets: DLV-08, DLV-09; related DLV-10.
Date: 2026-11-04, America/Los_Angeles.
Status: design proposal. No S4 implementation, registered record kinds, wire
freeze, scientific procedure adoption, or new scientific execution.

## 1. Decision boundary

Uzair approved moving from the
[minimum-account design](subsystem4-minimum-account-design-2026-11-04.md) into
precise semantic families and premise evidence. The small preservation account
and conditional roles carry forward; the rules below are proposals for review.
This pass defines what the information must mean and how it composes. It does
not choose keys, encodings, resource limits, default metrics, statistical
methods, or a released evaluator inventory.

A result's carrier (what is stored), scientific meaning (what it answers),
source (who reported or calculated it), and guarantee (what can be supported)
are independent. An interval-shaped object, for example, can carry a native
report, a possibility bound, numerical error, or inferential uncertainty. The
shape establishes none of those meanings. Keep the original observations and
derive named views with explicit inputs and losses.

## 2. Typed quantity, result and scope

| Semantic component | Minimum meaning and invariant |
|---|---|
| Target | One primary question instance and one output role per formal VAL, with exact scientific subject and evaluation unit/scope. A joint quantity can be one VAL. Incidental co-publication, identical values and same-shaped arrays imply no association. |
| Meaning | Exact family and version, estimand or predicate, domain/codomain, units or explicit dimensionless scale, conditioning/context and conventions relevant to comparison. Meaning includes polarity for loss/score and which proposition a probability refers to. |
| Binding | Exact selected input basis and frontier, including mapped coordinates, reference role, mask and actual input provenance as required by the operation. A typed raw report without a supported binding stays source material. |
| Value or disposition | A defined value with declared domain and extent, or the reason the affected quantity has no established result. A computed definition-domain exclusion is different from an access gap. |
| Origin | Link to the actual CALC and emitted output role for computed results, or the attributable source for a reported value. Recording a native interval or value does not attest that its procedure was carried out. |
| Interpretation limits | Relevant premise assessments, coverage, precision or approximation basis, and dependencies for each claim. Scope can be established for some components and unresolved for others. |

A structured value may use named member views to expose components. Views
identify the parent, selector, interpretation and resulting question or role.
A tuple of count diagnostics is permissible, but a count, coverage fraction,
and accuracy ratio do not become interchangeable parts of a universal score.
No part's guarantee upgrades unrelated parts or the joint value.

Reuse S1 domain, proposition, quantity, mapping and artifact identities where
they suffice. Reuse S2 reference/response, comparison and unit roles and S3
frontiers/availability/authority. A new scientific interpretation of a native
value is a linked interpretation, not a change to the native object.

## 3. Numeric and non-value families

| Case | Proposed treatment | Example / guarantee boundary |
|---|---|---|
| Exact finite value | Domain and units fixed by the question; preserve required exactness. Allow mathematical integers, exact finite decimals and exact rationals where the contract needs them. Numeric equality is distinct from preservation of source spelling, signed zero or precision metadata. | Count 2 and exact ratio 2/3 are defined; display 0.667 is a rounded presentation, not exact 2/3. |
| Finite approximation | Declare target, approximation method, actual precision, relevant stopping/error evidence and limitations. Claim only the accuracy established; convergence diagnostics, error bounds and acceptance tolerance have different roles. | A method can report a finite estimate with unknown numerical error under a scoped approximation contract; withhold any requested certified error guarantee. |
| Defined extended value | Allow positive/negative infinity only where the exact mathematical domain/procedure explicitly defines it, with evidence of the applicable case. Arithmetic and aggregators must declare handling of extended inputs. | Under a stipulated binary negative log loss with the extended convention, probability 0 for the realized event gives positive infinity. This is a defined extended loss, not a finite loss or an evaluator crash. |
| Undefined on established inputs | Name the domain condition and evidence that it is violated. Record any independent diagnostics; no substitute number. | Known judged count 0 in a positive-denominator ratio gives undefined accuracy. A known denominator of 3 and numerator of 0 gives defined coverage 0. |
| Indeterminate on available evidence | Name which inputs or scope are unresolved or conflicting and why. A different, explicitly defined bound might be possible. | If the denominator is unobserved, we do not know that the ratio has zero denominator. A missing reference label does not establish mathematical undefinedness. |
| Inapplicable, unsupported or not performed | Record the cause and its domain: target or input incompatibility, unsupported exact contract, operational denial, no requested work, failed/incomplete computation, or lost observation. Keep statuses on their corresponding axes. | Shape-valid inputs with an unevidenced unit conversion can block the requested calculation. A numeric artifact from a failed process does not by itself attest a valid result. |

Preserve native NaN, overflow, underflow, clipping or infinity as observed
representation/diagnostics where evidenced. NaN is not an accepted mathematical
scalar. A floating-point overflow is not proof of an infinite target. If a
finite target cannot be represented with available precision, report the
computational limit; do not promote the bit pattern to a value. If underflow
produces zero for a quantity meant to be positive, distinguish observed zero
from established mathematical zero. Deliberate rounding, regularization and
clipping must have explicit contracts and provenance. Clipping a forecast
before scoring changes the evaluated input or score definition, depending on
the declared design. There is no cross-family tolerance, including the
historical 0.001 evidence gate.

For a count-derived rate bind numerator, denominator and their contribution
or joint-input basis. Count, weighted mass, time at risk and effective sample
size are different denominators. A defined number can still answer the wrong
question if the denominator, population or units do not match. No default
mean-of-rates, pooled ratio, one-value-per-file rule or missing-equals-zero rule.

## 4. Structured families and meaning contracts

The following are reusable result carriers with semantic overlays. They are
not a closed list of possible native objects, a registry or an assertion that
every combination is feasible.

| Family | Required scientific structure | Withheld without additional basis |
|---|---|---|
| Scalar or categorical result | Typed quantity or category vocabulary, subject, scale, applicable comparison and allowed values. Predicate-valued results distinguish established false from unknown, conflict and out-of-scope. | Common ordering for unrelated categories, truth from compatibility, probabilities from arbitrary numbers. |
| Indexed result (map, vector, table, tensor) | Role-typed axes, unique scoped keys, expected domain/extent, entry meaning, mask with reasons, and whole-object obligations if claimed. Sparse default only when a declared definition establishes the omitted value. | Position-only joins, zeros in missing cells, symmetry or validity of a covariance matrix from individual entries. |
| Ordered/unordered collection | Membership/order/multiplicity semantics, stable keys, exact associated objects, expected/captured extent and selection or generation basis. | Treating repeated draws as duplicates to discard or independent scientific trials; best-member substitution. |
| Distribution or weighted object | Event/sample space and conditioning, measure/weight type, support/completeness, normalization contract, unknown residual mass, member associations; density requires a reference measure. | Law from arbitrary weights or sample bank, joint law from marginals, renormalization of partial support. |
| Set, interval or region | Member/ambient domain and units, boundary/membership rules, set role and extent, construction and qualification. Representation may be enumerated or a named, supported membership rule with its limits. | Treating an outer enclosure as exact, an empty feasible set as an unobserved result, or every region as a statistical interval. |
| Relational, functional or executable result | Exact operation/domain/codomain or relation/predicate, typed arguments and dependencies. Preserve invocation and qualification boundaries; use S1 objects or a supported derived view. | Inferring arbitrary graph completion, interpolation, counterfactual truth or executable behavior from bytes or a label. |
| Keyed composite | Explicit roles and associations across typed carriers; link shared basis, dependencies, extent and whole-object invariants. A primary joint quantity can have several aspects without becoming a list of independent observations. | Promotion from selected components to the whole, or attributing an inferential conclusion to neighboring values. |
| Opaque/extension | Preserve exact supported observation/source boundary, descriptor, availability and interpretation gaps; expose only independently supported properties. | An unknown kind acquiring scientific comparability, validation or execution merely because it can be stored. |

Mixed units may coexist under distinct roles, for example seconds and
reference-relative quality in a resource frontier. A single scalar utility
requires a separately declared conversion/tradeoff. A known empty table or
set requires an established scope and emptiness. A complete inventory of
captured keys can coexist with missing expected keys. A mask must support
reconstructing the applicable scope and reason; explicit groups can cover
many cells without inventing entries. Report unobserved membership separately
from a validated absence.

## 5. Set, bound and uncertainty meanings

| Claim | Evidence needed to support the exact claim | What the same endpoints cannot establish |
|---|---|---|
| Exact attainable/identified set or admissibility set | Meaningful domain, complete defining constraints and valid membership or derivation. Exactness needs both directions: retained possibilities are attainable/admissible and all applicable ones are retained. | A few sampled or feasible members are not proof of completeness. |
| Outer or inner bound, including one-sided | Target, construction, applicable assumptions/constraints, endpoint inclusion and evidence for the direction of containment. Record any proven sharpness and its scope; attainment is separate from enclosure. | An outer bound need not consist entirely of attainable values; midpoint, confidence level and sharpness do not follow. An unknown endpoint is not an unbounded endpoint. |
| Numerical enclosure or error description | Exact computational target, arithmetic/algorithm, proved enclosure or characterized approximation basis, precision and applicable input domain. An estimated error indicator is not a proved enclosure. | Sampling coverage, reference truth and causal identification. |
| Inferential set/interval | Exact target and uncertainty interpretation, procedure/model/design, conditioning, level and scope where relevant, and method-specific premise evidence. Name pointwise versus simultaneous coverage where claimed. | Confidence coverage from one inclusion, credible mass from width, joint coverage from marginal intervals, or future prediction coverage from a parameter interval. |
| Reported interval with unresolved meaning | Preserve observed endpoints, inclusion/units if supplied, exact source and unresolved construction/level. | S4 inference, coverage, exactness or validated numeric scale from a label. |

Keep uncertainty sources separate: ambiguity or partial identification,
reference error, data sampling or assignment, model uncertainty, prediction,
native randomness and numerical approximation can coexist. Combine them
only under a named joint construction with its own evidence. A range across
selected model assumptions is a sensitivity description unless stronger
containment/coverage is demonstrated. Causal identification and estimation
premises remain separate; see [Pearl (2009)](https://web.cs.ucla.edu/~kaoru/SS-2009-57-Sup.pdf).
No inferential construction is adopted here.

A supported empty feasible set can diagnose incompatible constraints. It
does not mean the missing estimate is zero or the target scientifically
impossible outside those premises. Finite or infinite bounds require their
declared endpoint conventions; the real interval (0,1] excludes 0 even if
its infimum is known to be 0. Two distinct points are a two-member set, not
the filled interval between them. An envelope or projection of a joint
region is a named derived value with declared information loss.

## 6. Premise and assessment families

A premise assessment answers whether a *particular* requirement is supported
for a *particular* claim/binding at a frontier. It needs three distinguishable
roles, which can reuse existing records:

1. **Requirement.** Exact versioned predicate, typed subject roles and scope,
   required evidence or derivation, and the operation, output role or
   guarantee it gates. State whether it requires an observed/design fact,
   a mathematical condition on stipulated inputs, or a declared assumption
   for an explicitly conditional target. A definition/domain rule differs
   from an empirical assumption and from an operational permission.
2. **Evidence.** Identify each assertion, observation or derivation, source,
   applicable scope, source frontier and method. Preserve evidence for and
   against, relevant gaps, and a link to original material when permitted.
   Exact meaning, relevance, source independence, authority and strength
   require evidence; repeated copies do not create corroboration.
3. **Assessment.** Identify the exact requirement and bound subject, applied
   rule, scope/frontier/audience, admissible evidence for and against, gaps,
   result and effect on the target. Distinguish supported, contradicted,
   unresolved, disputed and justified non-applicability. These are semantic
   distinctions; the encoding and condition cardinalities remain open.
   No verdict from an empty evidence list, an access denial or a default
   inference rule. A theorem or a stipulated definition may itself supply
   an appropriate non-empirical basis.

Observational/reference applicability, mapping validity, experimental design,
mathematical domain, missingness, identification and numerical convergence
are different requirements. QUAL establishes scoped capability from an actual
receipt; it does not certify this binding's premises. S3 determines evidence
access and action authority, not scientific validity. Downstream guarantees
point to the exact assessment scope rather than a global pass flag.

When observations genuinely conflict on the same predicate and scope, retain
both and withhold affected definite judgments unless a versioned
adjudication rule with evidence resolves the selected basis. A mismatch
in time, estimand, conditioning or population may instead be noncomparability;
do not manufacture a contradiction by dropping qualifiers. Do not count votes,
use latest-wins, or choose the most favorable score. Two alternative hypotheses
within a declared model do not, by themselves, constitute contradictory
observations. A new adjudication/frontier can produce a new assessment and
binding without rewriting older ones. Restricted evidence can support an
authorized result while its public projection has a narrower basis.

A model assumption can support a calculation *conditional on that model*
without establishing the assumption as a fact about the experiment. If
the requested method requires independently sampled, disjoint units and
observed windows overlap, the disjointness prerequisite fails. Overlap alone
does not prove dependence for every statistic; this method cannot pass as
inference for the actual design on the required basis. A separately requested hypothetical
iid target can be calculated under its stated model and assessed separately.
For alternative requirement routes, the procedure specifies which route
suffices and identifies the one used; an unresolved prerequisite on one
route neither rules out every alternative nor authorizes switching routes
after seeing results. No universal combination or adjudication logic chosen.

## 7. Identity and profile checks

Propose three levels for question identity, independent of actual work:

- **Definition:** versioned target/estimand, comparison and selection
  meaning, allowable slot types and bindings, quantity/units, and applicable
  scope, denominator, missingness, assumptions and conventions.
- **Question instance:** definition plus exact scientifically meaningful slot
  values that instantiate the target, for example the named benchmark frame,
  the event and conditioning, the predicate/domain, the comparison arms,
  or the hypothetical model when the model defines the estimand. No silent
  defaults; mark slots as target-defining or evidence inputs in the definition.
- **Evidence binding:** exact eligible, selected source versions, outputs,
  masks, mappings, alignment/selection rationale and frontier. Known coverage
  changes can change binding without changing a declared covered-label
  estimand; changing the rule that chooses coverage changes the question.
  Replacing a target-defining reference domain changes the instance. Replacing
  a reference artifact or judgments within a declared reference-evidence slot
  changes the binding. Changing a definition's loss, target or semantics
  requires a new definition/version. A code correction with the same promised
  mathematics and bound basis is a new procedure implementation and calculation.

A new basis can make values incomparable for the intended contrast even if
the definition/instance is unchanged. Compare only under an explicit compatible
comparison contract. Matching a hash or accepting identical outputs does not
prove scientific equivalence. Exact slot families/cardinalities and any
supported equivalence procedure remain open.

| Profile | Dependence on this pass |
|---|---|
| P0 preservation | Raw value, shape and labels can be captured without interpreted result or inferred meaning. A preservation assessment has its own scoped criteria. |
| P1 interpretation | Named meaning, exact scope/binding and relevant requirements; a supported coordinate interpretation can coexist with a held scientific comparison. |
| P2 calculation | Procedure/actual qualification/observed work, exact prerequisites and role-specific disposition. Defined counts or bounds can qualify where the requested point value is held. Defined infinity qualifies only for the extended target with applicable evidence. |
| P3 population/contrast | P2 plus POP and functional basis. Preserve the full intended frame, missingness, dependence/overlap and weights where relevant. A vector or set can be a joint result; no forced scalar decomposition. |
| P4 inference | P2 and INF with exact scope and required P3 basis where applicable. Level, model/design, uncertainty interpretation and premises must match; shape alone supplies no inference. |
| P5 reproduction | Frozen original basis and actual new work/comparison as applicable. Name comparison semantics for ordered keys, masks, undefined dispositions, nonfinite values and approximation. Bit or shape agreement cannot promote semantic/scientific claims. |

Undefined-to-undefined agreement might reproduce a *diagnostic disposition*
under a declared rule; it cannot establish a numerical ratio. Published
projections must retain audience-specific proof and availability boundaries.
S3 package integrity and profile satisfaction remain separate.

## 8. Semantic field obligations before encoding

These are role counts and admissible meanings, not a wire field map. An
upstream reference may fulfill a role only if its resolved exact contract
supplies that meaning and scope. No requirement to duplicate upstream data.

| Object | Required types and semantic cardinalities | Conditional obligations |
|---|---|---|
| Question definition / instance | One exact definition per instance; each declared slot has one role name, role class (target or evidence), input contract, and declared cardinality. Each target slot is instantiated at that cardinality before claiming a bound instance. | Required missing target values preserve unresolved request intent; they do not produce a comparable formal instance. Optional absence has an explicitly defined meaning; repeated slots define set, ordered list or multiplicity semantics. |
| Binding | One primary question instance and one frozen selection basis/frontier. Zero or more inputs across declared roles, subject to each slot's cardinality. | Unresolved mandatory inputs are permitted in a proposed/held binding only. A supported calculation resolves the required inputs and checks their exact cross-role relations. Zero-input mathematical procedures need an explicit closed definition, not a missing-input exception. |
| Formal result / disposition | One primary question instance, one associated binding, one output role, one scoped subject expression and one attributed origin (computed occurrence or reported basis). One primary defined value or one scoped non-value disposition; a named compound carrier can contain many parts. | Multiple source observations can support one attributed result. Unsupported or merely requested work stays on REQ/PREM/GUAR absent an actual result/disposition basis. Required parts of a defined joint result follow its family contract; per-part gaps cannot be silently dropped. |
| Structured payload | One exact family/extent contract. Zero or more keyed entries where allowed by that family; an empty collection requires established empty scope. Entries have unique identity within the relevant axis/role, not necessarily unique content. | Preserve declared order/multiplicity, expected scope and reason-bearing masks or grouped gaps. Additional constraints such as common measure, support disjointness and joint normalization are family-specific. |
| Requirement and assessment | One versioned predicate/role contract per requirement. Each assessment binds one requirement instance and exact subject, frontier, rule and audience, with a determination and effect on the affected claim. Evidence for, against and gaps can each contain zero or more exact sources. | An affirmative or contradictory verdict needs a sufficient evidenced or deductive basis; zero empirical observations may be valid for a purely definitional check. A grouped assessment is valid only where the requirement defines the grouped subject and proof scope. |
| Calculation and guarantee | Each CALC has one actual occurrence identity and a pinned procedure/configuration, with zero or more observed outputs and a recorded extent. Each guarantee assessment names one exact criterion/profile version and an explicit target (which may be a declared composite), basis/frontier and audience. | No output required to evidence a failed attempt. One call may produce many roles; a supported output and a disputed output can coexist. Each targeted claim closes its own procedure, premise and qualification dependencies. |

One result can be the input to another through an explicit selected role and
basis, for example per-unit losses feeding a pooled contrast. That relationship
does not make the downstream claim equivalent to its inputs. With two cases
scoring 1/1 and 0/3, pooling judgments gives 1/4; weighting cases equally
gives 1/2. Both can be correctly calculated, but the population unit and
functional define different questions. Neither is the default.

## 9. Worked dependency probes

These are stipulated semantic probes using the previous examples, not native
runs, serialized records, qualification receipts or proposed default methods.
Assume public fictional inputs except the already restricted reference in E06.
All prospective profile claims still require actual qualifications and work.

| Probe | Declared input, operation and result | Held claim and gap exposed |
|---|---|---|
| V01 Report / E01 | Preserve literal 'score=0.91' in SRC with original producer and quantity unresolved. No inferred formal VAL. | Holds interpretation, scale, score/probability calibration, and reproduction. A raw scalar-shaped observation needs no fictitious Q or CALC. |
| V02 Graph / E02 and E06 | Complete native AB=true, BC=false, AC=true; partial reference true/false/unknown. Covered judgment is exact 2/2; reference coverage 2/3. At conflict frontier AB has evidence both ways; full accuracy still held. A predeclared uncontested-only rule could score BC alone (1/1 with judgment scope 1/3), if requested and qualified. Adjudicated R2=true/false/false gives both covered and full results 2/3 with separate roles. | Conflict is not false. Mask changes alter basis even when native output is identical. Corrected result 2/3 and display 0.667 have distinct exactness; difference is 1/3000. Public attestation to a restricted aggregate does not supply its reference labels or public reproduction. |
| V03 Matched bound / E03 | K1 difference 4/5 - 1/2 = 3/10. K2/A unknown utility u in [0,1], K2/B known failure utility 0 by definition. Equal-case utility contrast is (3/10+u)/2, enclosed by [3/20,13/20]. If all u in [0,1] are jointly feasible with the fixed inputs this is the exact attainable interval; the marginal range alone supports an outer bound. | Full ordinary answer-quality mean is still held. Available-pair value 3/10 has frame coverage 1/2. No sampling confidence level, assumed quality zero or sharpness without feasibility evidence. |
| V04 Local and order / E04 | For whole-query abstention, zero definite answers of 3 gives coverage 0; judged accuracy 0/0 is undefined on known inputs. A lost artifact gives unknown coverage rather than the same zero. Complete admissible order set is {ABC,BAC}; supplied partial constraint A<C is compatible but fails the complete-sequence deliverable. | Abstention, missing evidence, and a wrong answer have distinct bases. A compatible constraint is not a valid complete answer. If reference constraints are necessary-only, a compatible sequence still does not establish complete correctness. |
| V05 Probabilistic / E05 | Forecast p(E)=4/5, y=1 gives squared error 1/25. Separate M/D target gives posterior 4/5. For an explicitly extended negative log loss, new forecast p(E)=0 with y=1 gives positive infinity; overflow on positive p does not. | No population calibration, model truth, native use of M, automatic clipping or finite score claim. The mathematical logarithmic convention follows the negative of the log score described by [Gneiting and Raftery (2007)](https://doi.org/10.1198/016214506000001437). |
| V06 Partial support and joint association | A finite law has known disjoint members of masses 1/5 (event true), 3/10 (false), and residual mass 1/2 with unresolved event membership. Event mass lies in [1/5,7/10]. Conditional on being in the captured members it is 2/5, a separate target. A sample bank can instead have two equal graph objects with distinct parameter members; both occurrences and associations remain. | Without the total-mass and disjointness premises, the residual 1/2 cannot be inferred. Neither conditional normalization nor marginal graph frequency gives the original joint law. A sampled approximate bank is not an exact finite target distribution. |
| V07 Joint range and coordinate scope | Joint possibilities (x,y)={(0,0),(1,1)} give x-y={0}; independently projecting coordinates to [0,1] gives conservative outer contrast [-1,1]. An indexed result on A/B with known A, unobserved B can report A; joining to reversed B/A coordinates uses identity mapping, not shape. | An outer contrast is not a sharp bound. Marginal information, inferred zero, or a relabeled axis cannot establish joint contrast or complete support. |
| V08 Premise, provenance and reproduction | A procedure requires disjoint independently sampled windows; recorded overlap contradicts its disjointness premise. Keep the actual-design target held. An explicit hypothetical iid model is a separate target; any resulting conditional inference depends on that model. At a new cutoff old reference bytes are unavailable while a locator resolves changed bytes. | A model stipulation cannot resolve a design fact. A reproduction request cannot create an actual recomputation; an alias or digest cannot replace exact original inputs. |

V03 and V07 deliberately test the difference between obtaining a sound
enclosure and identifying the exact possible set. V05 and V06 test the
difference between a native probability, a score, a conditional distribution
and evidence about population behavior. V02, V04 and V08 make a failed
prerequisite visible on the correct axis and at the correct frontier.

## 10. Choices and implementation boundary

| Choice | Proposed direction | Strongest alternative | Cost and failure prevented |
|---|---|---|---|
| Meaning and representation | Composable typed carriers with named semantic overlays and conditional guarantees | One opaque generic result or one class per adapter | More compatibility/qualification work; prevents shape-based claims and duplicated adapter policy. |
| Numbers and gaps | Exact/approximate/extended/undefined distinct, with raw observations retained | Uniform floating point with NaN/null sentinels | More domain checks; prevents zero, infinity, overflow and missing evidence becoming interchangeable. |
| Joint and partial results | Preserve coordinate/member association and qualified extent | Flatten to independent rows or normalize observed members | More indexing and proof of coverage; prevents lost dependence, changed targets and false completeness. |
| Set and uncertainty | Explicit containment, sharpness and inference semantics | One generic lower/upper result | More prerequisite evidence; prevents false precision and probabilistic claims from possibility bounds. |
| Premises | Exact claim, rule, cutoff and evidence for/against, separate from authorization | A single applicable flag or trust a source label | More assessment records; prevents conflict erasure and passing actual-design claims on hypothetical inputs. |
| Identity | Definition, instance, exact evidence binding and actual occurrence | Reuse metric labels or allocate a different definition for every input revision | More explicit slot design; preserves meaningful comparisons without conflating semantics with byte identity. |

Reuse the existing [S1 number and knowledge forms](../connections/model.py),
[S1 structural/quantity checks](../connections/semantics.py),
[S1 subtype design](system-connections-output-subtypes-2026-11-01.md),
[S2 reference and response semantics](subsystem2-reference-response-semantics-2026-11-02.md),
[S2 evaluation bindings](../experiments/evaluation.py), and
[S3 publication and authority scope](subsystem3-implemented-scope-2026-11-04.md).
S1's finite decimal lexeme can preserve native data; it does not settle
S4's exact rational encoding, numerical rules or domain validity. S2's
installed descriptor is metadata-only. Existing contracts are not widened by
these proposals. No scientific checks, schemas, runtime, legacy metrics,
research results, certificate, paper, tracker or site changes.

## Where we're going

Review these semantic choices, especially the target-defining slots, exact
versus outer bounds, and which kinds of premise a conditional claim can use.
Then select the initial procedure combinations and give each its full
definition, exact slot/field cardinalities, refusal conditions, and
independent qualification plan. Use worked packages to
exercise those decisions before bounded serialization, interfaces, recovery,
legacy mapping and a final build DAG. Implementation still requires an
explicit user go.
