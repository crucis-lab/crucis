# S4 semantic role cardinalities and references

DLV-08, DLV-09. Design review draft, 2026-11-04 Pacific.
Use this with the six procedure definitions and worked package reviews. These
are cardinalities of semantic roles and associations. Names below are design
notation. Encoding, record layout, ID syntax and resource bounds come next.

## 1. Identity and reference rules

A reference resolves one expected contract family/version and one immutable
target identity. A package-local target resolves within the named containing
snapshot by its local record identity. A cross-snapshot reference resolves an
exact frozen package/version pin plus the target record identity. An artifact
reference resolves the exact artifact revision with integrity evidence for the
consumed bytes or extent. A reference can carry one typed selector when the
role consumes a subobject, such as a proposition row, a keyed member, a
result role or an artifact extent. The selected object must satisfy the expected
contract and scope. A mutable alias may help locate bytes. It cannot fulfill an
immutable dependency. An unfulfilled required role retains a typed reason and
any safely available evidence, separately from a resolved reference.

Declare each multi-valued role as a set, ordered sequence or keyed association.
Reject ambiguity, duplicate keys and out-of-scope members. Distinct scientific
units with equal values remain distinct. The same source can serve different
roles where each relationship is evidenced. A reused premise assessment must
cover the new claim's exact subject, frontier and audience under the applicable
criterion. Exact identity and scientific compatibility require separate checks.

Use one canonical direction for dependency edges: a dependent claim references
its basis. Calculation output indexes and navigation backlinks are associations.
A proof cannot depend on its own conclusion. A local association need not know
the digest of its containing snapshot. Whole-snapshot integrity receipts target
an already frozen snapshot. Protected dependencies resolve only under authorized
access, and a projected claim cites the projection or attestation it can expose.
The public result cannot imply public access to a restricted raw basis.

## 2. Shared role counts

| Role | Cardinality and required references |
|---|---|
| Account and snapshot | One account identity, one frozen snapshot identity, one declared source frontier and audience per snapshot. One or more supplied source, intent, observation or gap entries, by inclusion or exact reference. Zero or more typed relations to other snapshots. A frontier can name multiple source positions. |
| Source or gap | One scoped subject or source-role expression, one attributed current observer or supplied origin, and one content/availability disposition. Zero or more exact supporting artifacts or observations, with actual content or a resolved reference when claiming availability. An opaque supplied report can remain a source without a formal result. |
| Question definition and instance | One exact definition per instance. One versioned target, output-role and premise contract per definition, with a typed slot declaration for each named role. Bind each target slot at its declared count before claiming a comparable instance. A definition may expose several separately addressable output roles. |
| Request and goal | One or more keyed goals per formal request. Each goal names one question instance, one output role, one requested subject/scope and one nonempty set of profile targets. It can name zero or one selected binding at request time. Later assessments can bind the same intent to separately identified evidence without updating the old request. Unresolved intent with no formal instance stays in the account as intent. |
| Evidence binding | Exactly one primary question instance and one selection/frontier basis. Each declared evidence slot has the count and collection semantics in the procedure matrix. A required slot can carry an unresolved disposition before calculation. A fulfilled calculation closes the mandatory roles for its declared scope. New selected evidence, mapping or frontier creates a new binding; changed target-defining values create a new instance. |
| Procedure and qualification | One exact procedure definition/version and one configuration per declared invocation. A computational occurrence has an attributable implementation and the transitive dependencies relevant to its claim. A supported computation needs one or more actual qualification receipts collectively covering the specific procedure, reader/implementation and claim scope. A test plan is source material. |
| Premise | Each requirement has one versioned condition, typed subject-role contract and applicability rule. Each instance supplies the exact bound subjects. Each assessment names one requirement instance, one evaluated scope, frontier, rule and audience, and one determination. Evidence for, against and gaps each have zero or more entries; the verdict needs the basis required by its rule. A derivation may supply a basis without empirical observations. |
| Calculation | One actual occurrence identity, one exact procedure/configuration, one frozen execution input basis and one observed work disposition. For a started scientific evaluation, one or more planned output entries name their exact binding and output role. A registered composite may map several questions/bindings explicitly. Zero or more observed emissions are keyed by binding, role and subject. Each emitted key occurs at most once per occurrence; a structured value carries multiple keyed members when its contract permits it. An early failed occurrence can have zero emissions. |
| Result or disposition | One primary question instance through exactly one evidence binding, one declared output role, one subject and scoped quantity, and one attributed origin. A computed origin selects exactly one occurrence and emission. A reported interpretation selects one attributed report basis, which may cite several observations. Carry exactly one defined payload or one evidenced non-value disposition. A supported computed undefined disposition links to its calculation and determining facts. A request held before work belongs in its goal assessment without an invented emission. |
| Population | One intended frame and one named functional or population-account role per scoped population account. All intended unit keys have exactly one disposition each. Matching, weighting and contribution associations follow the procedure's cardinalities. Frame and slot records may be shared by several accounts. |
| Inference | One defined inferential target and one procedure/model or design basis per scoped inference account. A claimed inferential output names one selected result role, one actual calculation origin through that result and the applicable assumptions. Link the required population account only when the method needs it. Requested or held inference may instead reference the goal with no produced output. |
| Reproduction | One original result or diagnostic role and its one attributed original calculation, one replay boundary and comparator contract per request. Zero or one actual replay occurrence per reproduction assessment. Zero or one completed comparison, conditional on a comparable observed replay. A new attempt has its own occurrence and assessment. |
| Profile assessment | One profile criterion/version, one target, one assessment frontier/audience and one disposition. Target one requested goal, one observed result role, or one explicitly defined composite target. Multiple profiles or claim scopes require separately addressable assessments. Reference precisely the applicable premise assessments, actual qualification and work/availability evidence for the claim. |
| Relation | One named relation type, one scoped source and one scoped target per binary edge, with its basis and frontier. A genuinely joint relationship uses a named typed composite subject. Derivations, corrections, continuations and projections preserve their source and target revisions. |

A calculation plan and each selected output role declare the applicable
requirements. For each applicable instantiated requirement, select exactly
one assessment per claim at its declared evaluation frontier. Earlier or
conflicting assessments remain preserved. The selected assessment references
that conflict when material, and its disposition must reflect it. Keep an
unresolved prerequisite explicit. Independent premise sets can differ across
outputs of one call. No count of positive observations is a substitute for a
required basis. A formula's prerequisites are distinct from permissions and
from actual procedure qualification. Mark when each requirement is evaluated.
A prerequisite for starting work can block the occurrence. A condition learned
during calculation can block only the affected value. For example, Q06 checks
the input model and evidence before computing the normalizer. The posterior
uses the positive-normalizer assessment after the normalizer is produced.
The normalizer never depends on that downstream assessment. A computed
undefined disposition can cite the failed condition and the calculation that
established it. Qualifications and profile claims cite the observed work and
its output where applicable.

A result has one scoped comparison or evaluation expression. A noncomparative
output may use a declared subject-only expression. A comparative expression
identifies the quantity, relevant target universe/frame, comparison side
roles, actual mask or pairing, and numerator/denominator or functional when
applicable. Share a pinned expression where the exact scope is identical.
A comparison of two outputs also needs a named compatibility rule for that
comparison. Reproduction uses its explicit comparator rather than treating
equal values as comparable. The expression can refer through the binding,
ledger or population account, provided the exact roles resolve unambiguously.

## 3. Initial procedure slots

Counts describe ready supported inputs. The held branch retains required role
names and their unresolved or failed premises. Selection of one reference
basis can require examining several source artifacts. One interpreted answer
can draw on multiple native evidence records.

| Procedure | Input role cardinalities | Result roles and comparison scope |
|---|---|---|
| Q01 finite judgment | One finite requested proposition universe, one interpreted native answer, one mapping basis, one selected reference basis and applicable source policy. Exactly one native and one reference disposition plus one judgment eligibility disposition per requested key. | Per bound question, at most one covered or full agreement result/disposition for that role and subject per calculation. A keyed ledger and selected count/coverage roles name their own scope. Covered ratio uses J; full-scope ratio uses U and requires J=U. |
| Q02 strict order | One nonempty finite roster, one interpreted sequence, one mapping basis, one reference basis. The latter declares complete or necessary-only criteria and zero or more uniquely keyed precedence constraints. | Fulfillment uses the roster and captured submission extent. Violations name the supplied constraints, count and violated IDs. Admissibility references the applicable criterion assessment and its completeness or an evidenced necessary violation. |
| Q03 binary loss | One event and context, one interpreted probability, one applicable binary outcome and one match assessment. Prospective role requires one selected issuance-order assessment, supported by as many exact sources as needed. | One exact loss or evidenced disposition in the declared domain per event/outcome role. Prospective timing and event match are explicit premises. Population calibration is a different target. |
| Q04 equal-case point | One finite nonempty frame of n cases, exactly two distinct ordered arms, exactly one selected planned slot per case/arm, and one compatible established score per slot for a point result. Exactly one slot disposition for each of the 2n slots. | Named case difference and complete-pair count roles can have their own work and scope. The full point role uses all n pairs, equal weights and A minus B. |
| Q05 equal-case enclosure | Same frame, arm and slot counts as Q04. One utility rule, one selection and horizon policy, and one closed evidenced range per slot. Each slot has one delivery disposition and one selection disposition. Candidate observations may be zero or more. One exact selected answer when selection is established as a delivery. | One outer interval over the full frame, with both endpoint roles under the same joint target. Keep each range's delivery, selection and value evidence. Q05 can use per-slot quality results without a Q04 full point. |
| Q06 finite posterior | One model, one finite partition with at least two unique hypothesis keys, exactly one prior and one applicable likelihood per key, and one observed event bound to the model's protocol. | One keyed weight collection, one normalizer and one keyed posterior or undefined disposition, as separately declared output roles. One entry per hypothesis in defined keyed outputs. The inference scope is conditional on the named model and observation. |
| P5 exact replay | One original calculation and one exact original role, one boundary and one comparator. A ready replay pins every required original input and relevant implementation, configuration and environment dependency. | Compare the corresponding role under the fixed input basis. Pin input masks for score-only replay. Compare rederived masks as outputs when the replay boundary includes their derivation. A basis mismatch holds comparison. A divergent result on the same pinned basis can establish disagreement. |

## 4. Worked traces

- Graph covered agreement. The result 2/2 selects the covered question's
  binding, the covered emission from one Q01 calculation, and the comparison
  expression with U={AB,BC,AC} and J={AB,BC}. Its applicable closure, mapping
  and selected-reference assessments cover those judgments. The request for
  full-scope agreement has a separate goal and assessment showing AC is
  undetermined. It has no numeric emission. If a corrected reference makes
  both roles 2/3, they remain distinct even when one composite invocation
  emits both.
- Local abstention. A supported scoped abstention produces a defined coverage
  result 0/3 and an undefined covered-ratio disposition. Both can select
  emissions from the same Q01 occurrence. The ratio links the established
  empty eligible set and positive-denominator rule. The coverage result uses
  the three requested candidates. A missing answer holds entry and can
  separately support a captured-inventory diagnostic.
- Paired utility. One shared frame supplies two case keys and four slot
  keys. Q04's full-point assessment names the missing K2/A score and the
  absent qualifying answer for K2/B. Q05's bound [3/20,13/20] references its
  own binding, calculation, same frame and four utility ranges. K2/A range
  [0,1] links unresolved delivery and a total utility rule. K2/B [0,0] links
  authoritative eligible history through the horizon and that rule's zero
  branch. The Q04 point is not a prerequisite of Q05.
- Ordering. A BAC fulfillment role depends on the roster, mapping and
  complete submission. A zero-violations role references r1 and r2. The
  admissibility result additionally needs the assessment that those rules
  exhaust the criteria. Under a necessary-only reference the first two
  results can hold while positive admissibility is unresolved.
- Forecast and posterior. Forecast loss 1/25 links the exact event, probability,
  observed label and issuance-order assessment. The posterior role is keyed by
  model alternatives and linked to the normalizer and observation-protocol
  assessment. With normalizer zero, the defined zero diagnostic and the
  undefined posterior disposition are distinct. Conditional inference targets
  the posterior role, with no multi-case population dependency for this model.
- Replay. A scoped reproduction goal selects the original covered result and
  calculation. The new replay has a separate identity. If rederiving the mask
  from the same frozen basis produces {AB} instead of {AB,BC}, the comparison
  can complete with disagreement even though both ratios equal 1. With a
  substituted reference, the basis check holds the requested comparison.
  A comparison of two undefined ratios needs the explicitly declared
  diagnostic comparator, same cause and same scope.

## 5. Serialization review

The next pass can choose how record identities, exact reference targets,
selectors, keyed associations, value/disposition alternatives and extents
are encoded. Pressure-test reference resolution, audience closure, omitted
required roles, double emissions, changed basis and immutable frontiers.
Preserve the scientific scope and output-specific dependencies across the
wire representation. This draft records design choices and fixtures.
