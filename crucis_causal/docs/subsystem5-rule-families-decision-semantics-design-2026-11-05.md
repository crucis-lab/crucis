# S5 rule families and decision semantics

DLV-08, DLV-09, DLV-10. 5 November 2026. Design proposal following
[applicability and evidence requirements](subsystem5-applicability-evidence-design-2026-11-05.md).
The thresholds and decision policies below are worked examples.
Historical rule identity and interpretation follow the
[v1 definitions](../protocol/thresholds_v1.json).

## Define the question before comparing a number

The selected rule revision names the quantity, units, scope, admissible
evidence form, comparator, exact threshold and allowed conclusions. A
point estimate, a sampling interval and an outer bound can share an axis
and have different decision semantics. Applicability, control validity
and other required prerequisites remain separate from the numerical
decision. The examples below assume those prerequisites are satisfied
unless explicitly stated.

Use the qualified numeric convention at the decision boundary.
Compare the exact values where they are available. Display rounding
has a separate purpose. Any approximation, comparison tolerance or
conversion requires an explicit rule. For example, a change of 0.10
in F1 means ten percentage points on the 0–1 scale. A relative ten
percent reduction would ask for a different quantity.

## Point thresholds and sampling intervals

| Rule or evidence | Decision |
|---|---|
| Exact point 0.10 | Meets a rule using greater than or equal to 0.10. Misses a rule using strictly greater than 0.10. |
| Exact point 0.0996, displayed as 0.10 | Misses the inclusive cutoff. The exact negative margin can explain why the rounded display looks equal. |
| Point 0.12 and sampling interval [0.04, 0.20], point-only rule | Meets the point rule. The interval can still be reported with its own inferential scope and provenance. |
| Qualified sampling interval [0.10, 0.20], illustrative rule with a positive branch when the lower endpoint is at least 0.10 and a negative branch when the upper endpoint is below 0.10 | Meets the positive branch. An upper endpoint exactly equal to 0.10 fails the strict negative test. The rule has an explicit inconclusive branch for intervals between its two decision conditions. |
| Qualified sampling interval [0.04, 0.20], same two-branch rule | A completed inconclusive decision. The measurement and its inferential premises are established. The interval does not settle either branch under this policy. |
| A rule requires the qualified interval, but its cluster basis is unresolved or the interval is absent | Hold on the affected evidence requirement. A visible point can satisfy a separately declared point rule. |

An endpoint condition can also be an ordinary Boolean clause. For
example, a condition requiring a lower endpoint strictly greater than
zero is false at zero. A rule may explicitly define a separate
inconclusive branch. Crossing a threshold by itself does not select that
branch for every rule. Pin the interval method, level, target, and relevant
sampling assumptions. An interval-based miss supports the declared
decision at that scope. Equivalence requires a rule and evidence that
address equivalence.

## Outer bounds

For a rule asking whether the unknown quantity is at least 0.10,
a qualified closed outer bound supplies two sufficient tests. The
positive test is lower endpoint greater than or equal to 0.10.
The negative test is upper endpoint strictly below 0.10.
For a strictly-greater-than rule, those tests become lower endpoint
strictly above 0.10 and upper endpoint at most 0.10.

| Closed outer bound | What it establishes for the inclusive rule |
|---|---|
| [0.10, 0.16] | Every enclosed value meets the cutoff. |
| [0.04, 0.09] | Every enclosed value misses it. |
| [0.04, 0.10] | The bound alone leaves the decision open. Equality remains within the enclosure. |
| [0.08, 0.16] | The bound alone leaves the decision open. The enclosure may be conservative, so the endpoints do not establish which values are attainable. |
| [0.10, 0.10] | The qualified singleton establishes equality. It meets the inclusive rule and misses the strict rule. |

An inconclusive decision from a valid enclosure records exactly what
the evidence settles. If evidence for the enclosure itself is missing,
hold the bound-based decision. A midpoint needs a separately qualified
quantity. A sampling interval has a different interpretation from an
enclosure guaranteed under named premises. The
[S4 paired utility procedure](s4/b06-paired-implementation.md)
supplies an outer enclosure under its utility contract.

## Counts and minimum evidence

The rule names what it counts and the evidence needed to establish the
count or a bound. For an at-least-five minimum, six distinct eligible
pairs prove the minimum even if other pairs remain unresolved. Four
established and two unresolved imply a possible count from four to six
when that six-case frame is fixed. The minimum is unresolved. Four
established with at most one remaining candidate also leaves the minimum
unresolved. Four established and a closed maximum of four prove
insufficiency. Passing the minimum leaves other requirements open, such as
completeness for a full-frame mean.

A rule for at least one attributed native crash can be met by one
verified crash when the rule allows early evaluation and its common
premises hold. Zero observed crashes supports a verified zero only
with evidence that covers every required attempt and relevant outcome.
An open or interrupted attempt can leave the count unresolved. A rate
also needs its named denominator and the pairing of numerator events
to that denominator. A known zero denominator is a defined state of
the evidence that can make the rate mathematically undefined.

## Compound rules and missing operands

First establish the requirements that govern the whole finding, such as
the realized control and the required unit minimum. A known failed minimum
can close the evidence gate even when the score is missing. That disposition
is insufficient evidence for the rule, rather than a numerical miss.

Then evaluate independently qualified clauses. Start with explicit AND
and OR. A rule declares whether a missing optional operand can be left
open when a supported clause settles the whole decision. For an
illustrative rule with eligible evidence in both arms:

- **AND.** A rule requires a point at least 0.05 and a lower sampling
  endpoint strictly above zero. An established point of 0.04 makes
  the predicate false when the missing interval is needed only for the
  other clause. A point of 0.06 and a missing interval leave the
  predicate unresolved. A qualified lower endpoint of exactly zero
  makes that clause false.
- **OR.** An illustrative calibration rule accepts either a qualified
  calibration error or a qualified confidence gap strictly above 0.05.
  A qualified error of 0.06 can settle the predicate while the gap
  remains unavailable. An error of exactly 0.05 and an unavailable
  gap leave it open.
- **Shared dependency.** A missing or disputed pairing affects both
  clauses if both depend on the paired frame. A value from that frame
  cannot establish a decisive clause until the shared dependency is
  resolved. A rule may also require both operands for its claim or
  explanatory guarantee even when ordinary Boolean logic needs only one.

The record preserves which clauses were true, false, unresolved or
unevaluated, what evidence they used, and which facts settled the
decision. Missing or disputed evidence and a mathematically undefined
operand keep their causes. A rule that explicitly tests an undefined
outcome may use that cause as evidence. An ordinary numeric comparison
requires a qualified numeric operand. Preserve all relevant gaps for
the audience even when they cannot alter the declared decision.

## Design choice and next review

Use typed predicates, explicit prerequisites and separate decision
branches. Accept a partial-evidence decision only when an established
clause or qualified bound suffices regardless of how the remaining
admissible facts turn out. The first grammar can use conservative
compositional checks. A result that requires exploiting correlations
between unresolved quantities needs its own qualified comparison.

One simpler alternative would require every referenced operand before
making any decision. That gives a uniform evidence checklist and can be
the right policy for individual rules. As the default it would hide
decisions already established by valid evidence. Typed requirements add
scope and validation work and prevent a missing value from silently
becoming zero, false, or a satisfied prerequisite.

Next, review registration and claim status. Work through when a rule
and its analysis choices were fixed, what information was available,
how amendments affect a claim, and what to retain for historical imports.
