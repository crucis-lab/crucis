# S4 first procedure slate

DLV-08, DLV-09. Design review draft, 2026-11-04 Pacific.
These are proposed initial contracts. Each example is a stipulated calculation
used to review the design. Qualification requires future observed evidence.

## Shared contract

Every requested quantity binds one question definition and instance, a frozen
input frontier, an output role, and the exact procedure version. Its inputs
must resolve under the relevant audience and reader. Declare the target before
evaluating values. Record the selected input keys, origin and dispositions.
Use mathematical integers and exact rationals for the first procedures.
Representation, size limits, implementation and qualification receipts are later
decisions. An unsupported procedure, inaccessible input, incompatible binding,
unresolved premise and mathematically undefined quantity retain separate causes.

Qualification has three distinct checks. A semantic specimen establishes the
input family and prerequisites. An independent mathematical oracle checks the
specific calculation and its boundary cases. An integration specimen exercises
the actual supported S1/S2/S3-to-S4 path and checks that the output and withheld
roles retain their intended scope. Each actual receipt pins its procedure,
implementation, exact input/reader combination, scope and observed outcomes.
Native-system and population claims require evidence appropriate to those claims.

## Q01. Finite proposition judgment, P2

- Inputs. One explicitly enumerated finite scope U of unique proposition IDs,
  one supported native interpretation, one selected reference basis, and the
  mappings required by that scope. Each key has one native disposition and one
  reference disposition at the frontier. Preserve explicit yes/no, abstained,
  unreported or unresolved native evidence and determinate, conflicting or
  unresolved reference evidence. Interpret omission only under an evidenced
  closure rule. An inaccessible required reference source cannot be taken as
  evidence of no conflict.
- Rule. Let A contain keys with established captured definite responses, R
  contain keys with applicable uncontested binary references under the declared
  source policy, and J = A intersect R. Let m count equal binary judgments in J.
  Covered agreement is m / |J| for |J| > 0. Full-scope agreement is m / |U| only
  when J = U and |U| > 0. They are different output targets. Return m and |J|
  where established. Captured definite coverage |A| / |U| and applicable
  reference coverage |R| / |U| have their own roles. These sets describe what
  can be established at the supplied frontier, with any evidence gaps retained.
- Example. Three adjacency keys AB, BC, AC. Native yes/no/yes and reference
  yes/no/unknown yield covered agreement 2/2, reference coverage 2/3 and held
  full-scope agreement. A local parent query over three named candidates uses
  the same procedure with a different predicate. An explicit whole-query
  abstention gives zero definite answers and undefined conditional agreement.
  Missing native bytes may establish zero captured decisions in the supplied
  inventory while the native answer coverage remains unknown.
- Withhold. Hold affected comparisons for incompatible predicate/domain,
  ambiguous alignment, unsupported native interpretation or missing reference
  basis. When the eligible judgment set is established empty, the covered ratio
  is undefined. Unknown eligibility is an evidence gap. No fallback from the
  full-scope question to the covered question. A peer reference yields scoped
  agreement, and benchmark-relative accuracy requires the benchmark truth role.
- Qualify. Independently enumerate small binary/missing/abstention/conflict
  ledgers, including empty cases and a definite wrong prediction. Check
  renaming/reordering invariance and fixtures with the same one-edge list
  under open and closed omission. Exercise both an adjacency and a local
  membership reader, plus refusal when their predicate identities are swapped.

## Q02. Finite strict sequence and reference constraints, P2

- Inputs. One exact finite roster of at least one member, one submitted
  strict sequence, one mapped identity per member, and one declared
  reference comprising a finite set of precedence pairs on the roster.
  The reference declares whether these are all the admissibility conditions
  or only necessary conditions. Require a supported noncontradictory
  constraint basis. An explicitly empty condition set can be meaningful.
- Rule. Fulfillment requires that the sequence contains every roster member
  exactly once. For a fulfilled sequence, count pairs (a,b) for which
  position(a) >= position(b). Return the count and violated pair IDs.
  Under complete criteria, zero violations gives admissibility and one
  violation suffices to rule it out. Under necessary-only criteria, zero
  violations establishes that all supplied constraints are satisfied and
  leaves full admissibility undetermined. An established necessary
  violation rules out admissibility under that scoped reference.
- Example. Roster A/B/C, conditions A<C and B<C. ABC and BAC both pass a
  complete reference. ACB violates B<C. A partial relation A<C has no
  complete-sequence evaluation. A known complete delivered artifact missing
  B can establish nonfulfillment; a truncated capture cannot establish that
  the native sequence omitted B.
- Withhold. Hold the affected result for unresolved roster, ambiguous mapping,
  incoherent reference, unsupported ties/partial orders or incomplete capture.
  Keep supported fulfillment diagnostics. Relative positions answer the
  precedence task specified by the reference.
- Qualify. Use independent hand-enumeration of all six three-member
  permutations and the expected acceptance set {ABC, BAC}. Include duplicate,
  out-of-roster, tied, partial and truncated inputs, a cyclic reference,
  an explicitly empty rule and a necessary-only reference.

## Q03. Single-event binary squared probability loss, P2

- Inputs. Exactly one event and conditioning context, one probability p
  interpreted for that event with 0 <= p <= 1, and one applicable outcome y
  in {0,1} with adequate basis. If the task evaluates a prospective forecast,
  require evidence of its issuance frontier relative to outcome availability.
- Rule. L = (p - y)^2, one exact dimensionless value in [0,1], lower is better.
  The definition uses one binary event coordinate. It follows the loss
  orientation of the binary quadratic rule in Gneiting and Raftery (2007),
  Table 1, https://sites.stat.washington.edu/people/raftery/Research/PDF/Gneiting2007jasa.pdf.
- Example. p = 4/5 and y = 1 gives 1/25. p = 0 with y = 1 gives 1.
- Withhold. An unknown or contested outcome, unmatched event/conditioning,
  a p-value, an unlabeled confidence field, or a value outside [0,1]
  cannot satisfy the input contract. Preserve the exact observed report.
  Calibration and comparative population performance require separate targets.
- Qualify. Test against exact independent values for both labels, both
  endpoints, 1/2 and 4/5. Check complement symmetry and the expected
  difference from a two-coordinate sum. Include a numerically valid
  p-value, wrong event, unknown outcome and invalid p as refusal cases.

## Q04. Equal-case paired descriptive contrast, P3

- Inputs. Exactly one finite nonempty intended case frame, two declared
  arms A and B, exactly one selected slot per case/arm, and exactly one
  compatible established scalar value per slot for the full-frame target.
  Bind keys, unit/scale, effect orientation A minus B, selection, and the
  declared assigned or received condition basis. Retain all intended slots
  and their evidence dispositions. Equal case weights are part of this
  definition.
- Rule. D = sum_i (a_i - b_i) / n. Return the case differences and frame
  count. Count established complete pairs as a separate diagnostic, with
  unknown dispositions visible. The first version proposes only the
  full-frame point target. An available-pair mean has its own denominator
  and would require a separate procedure version or definition.
- Example. Two pairs (4/5,1/2) and (1/5,3/10) give differences 3/10 and
  -1/10 and mean 1/10. If the second pair is missing, retain the first
  contribution 3/10 and complete-pair coverage 1/2 on this frame. Hold D.
- Withhold. Unresolved intended membership, duplicate slots without a
  selection basis, incompatible quantities, any unresolved required value,
  or an unestablished condition basis holds the full-frame point result.
  A known empty frame gives an undefined equal-case mean.
- Qualify. Compare with an independently calculated average of arm totals
  on complete frames. Reverse arm roles and reorder records while keeping
  keys. Pressure-test ambiguous matching, incompatible units and the
  tempting surviving-pair answer. The named frame supports a descriptive
  contrast. Causal attribution and sampling inference have separate premises.

## Q05. Equal-case paired utility enclosure, P3

- Inputs. Same intended frame, slot identity and contrast direction as
  Q04. One explicit utility rule and one evidenced closed rational range
  [L,U] per slot on the same scale. A known utility is a singleton range.
  Each range must contain all slot values allowed by the stated premises.
  Pin the source of each range and record which joint constraints are unused.
- Rule. Return the outer interval with lower endpoint
  sum_i (L_Ai - U_Bi) / n and upper endpoint sum_i (U_Ai - L_Bi) / n.
  For each term the minimum uses the lower A and upper B, and the maximum
  uses the upper A and lower B. These extremes bound the sum even when
  joint restrictions narrow the attainable set. The result carries no
  sharpness guarantee.
- Example. K1 gives 3/10. K2/A has an evidenced utility range [0,1].
  K2/B has evidenced failure and utility 0 under this task's rule. The
  outer interval is [3/20,13/20]. The ordinary-quality point target in Q04
  remains held. With singleton ranges throughout, the interval collapses
  to the point for the same utility contrast.
- Withhold. A missing range, unsupported utility assignment, reversed
  endpoints, unresolved pairing or inconsistent evidenced premises holds
  the requested bound. An execution failure supplies zero utility only
  where the task definition makes that assignment. Treat a missing or
  unknown execution outcome by the evidenced range for that case.
- Qualify. Independently enumerate corners on small boxes, compare with
  Q04 for singleton ranges on the same scale, and use coupled feasible
  pairs such as (0,0),(1,1) to check containment with no sharpness promotion.
  Include failure-versus-capture-gap and unknown-range cases.

## Q06. Finite model-conditional posterior, P2 and P4

- Inputs. One explicit finite model with at least two uniquely keyed,
  mutually exclusive and exhaustive alternatives in the declared model,
  exact nonnegative priors summing to one, and exactly one applicable
  likelihood in [0,1] per alternative for the same evidenced event D.
  The target names the model, observation and keyed posterior distribution.
- Rule. Compute w_i = prior_i * P(D given i) and Z = sum_i w_i. For Z > 0
  the output keyed distribution is w_i / Z. Retain w_i and Z as supporting
  values. Its P4 scope is the stated model and evidence.
- Example. Priors 1/2 and 1/2, likelihoods 4/5 and 1/5 give weights 2/5
  and 1/10, normalizer 1/2 and posterior (4/5,1/5).
- Withhold. A missing hypothesis likelihood, invalid prior mass, unresolved
  partition, mismatched observation or contradicted claim that the actual
  data came from a stipulated model holds the affected claim. With established
  Z = 0 the conditional posterior is undefined. A native forecast and
  a computed posterior can have identical values and independent provenance.
- Qualify. Independently construct joint mass tables and condition on D.
  Check exact posterior sum, permutation by key, identical likelihoods,
  zero-prior entries, zero evidence mass and malformed or mismatched models.
  Actual inference evidence records the conditional target and its model
  premises. This procedure uses no fitted models or simulation.

## Initial P5 mode for this slate

For a requested reproduction, require the pinned original calculation,
inputs, procedure, configuration, environment and output role, actual access
for the audience, and an observed separate recomputation. Compare keyed output
values in their declared exact domain, including role, units, scope, masks
and any relevant order. Integer and rational equality are exact. Compare an
undefined disposition only under a rule that identifies its cause and scope.
An equal disposition establishes that diagnostic agreement. Missing original
bytes or incompatible roles withhold a reproduction conclusion. A matching
number with a different mask is a negative fixture. A mismatch on comparable
exact bases is a completed comparison with disagreement.

The first slate favors these small independently checkable procedures.
Calibration, general graph distance, equivalence-class scoring, general
ranking scores, data-based inferential intervals and approximate or stochastic
reproduction remain later procedure-design decisions. Next review full
packages through selection, interpretation, applicability, computation,
population or inference, and reproduction. Close any unresolved dependency
or role before encoding and before implementation planning.
