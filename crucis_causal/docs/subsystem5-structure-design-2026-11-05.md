# Subsystem 5 findings and decisions

DLV-08, DLV-09, DLV-10. 5 November 2026. Opening design proposal.
The proposed responsibility boundaries and examples are for review. They
carry no protocol adoption or implementation approval.

## Responsibility

S5 decides what one specified audit rule warrants at one scientific scope
and evidence cutoff. A finding account should let a reader recover the
question, applicable rule, evidence considered, decision, and limits of
the resulting claim. It should explain an absent decision as precisely as
a positive finding.

S1 provides native semantics and evidence. S2 supplies intended controls,
populations and comparison design. S3 supplies realized execution and
information history. S4 supplies qualified quantities, comparisons and
their scopes. S5 applies a finding rule to those premises. S6 consumes
the scoped finding and its evidence for reporting and certification.
S7 uses known faults and clean controls to validate the auditor.

## Worked boundary

The historical [K04 rule](../protocol/thresholds_v1.json) examines the
paired mean of real-name minus swapped-name directed F1, with at least
five eligible pairs and a point threshold of 0.10. Its historical metric
and population have specific meanings. This illustration borrows the
shape of the rule without changing that rule or asserting a new result.

- Suppose a future compatible rule binds a qualified difference of 0.12
  for six eligible pairs under a demonstrated names-only change to the
  input presentation. The scoped decision can say the threshold was met
  for that metric, population and control. A point rule stays a point
  rule even if a separately reported sampling interval crosses 0.10.
  It warrants no blanket claim about the system's internal mechanism or
  its behavior on other cases.
- If only four eligible pairs are established, the same point value
  fails the minimum-evidence gate. If the control also changed column
  order and that change violates the declared design, hold the
  name-specific decision. The descriptive difference can remain visible.
- If the system is demonstrated to lack any applicable name channel for
  this configuration, the requested control may be inapplicable. Missing
  capture or unknown exposure leaves a different, potentially resolvable
  gap. A declared data-only mode by itself supplies no evidence that the
  names could never reach the system in another channel.
- An S4 delivery-utility bound of [0.08, 0.16] cannot substitute for the
  directed-F1 point. A separately versioned rule targeting that utility
  bound can explicitly decide what it means when the bound straddles its
  own cutoff. A bound over possible utilities and a sampling interval
  carry different scientific premises.
- Exactly 0.10 meets an inclusive threshold when the other premises are
  established. A result just below 0.10 misses that threshold even if
  both values display as 0.10. That outcome is local to the declared
  threshold and scope.

The current generic S4 procedures include an exact paired-point
functional over compatible supplied scores. Qualification of the
historical directed-F1 basis for a new generic finding would be a separate
step. See the [S4 support review](s4/release-review-2026-11-05.md).

## Proposed responsibility boundaries

1. **Rule identity and selection.** Pin the rule version, typed quantity,
   operator, threshold, units, minimum evidence, selector policy, and
   intended wording. Pin the protocol separately from individual rule
   definitions. Distinguish a kind from a rule revision and an instance
   evaluated on a particular subject and evidence basis.
2. **Applicability and evidence binding.** Bind exactly one requested
   claim scope. Check planned versus realized control, reference meaning,
   population and units, available evidence, and required S4 qualification.
   Track those checks separately so missing records cannot settle a
   capability question or become an observed negative.
3. **Rule evaluation and decision.** Apply the explicit decision rule to
   typed evidence. Keep the scientific disposition and reasons separate
   from whether evaluation was attempted and whether it was recorded.
   A compound rule can have several decisive clauses. An exact margin is
   meaningful only with respect to a named clause.
4. **Registration and claim status.** Link to the exact dated rule,
   eligible scope, and information history. Same-day or unavailable
   ordering may leave confirmation status unresolved. Check whether the
   same rule and analysis choices were committed before the relevant
   exposure. External preregistration and a later package rule can
   coexist, each with its own provenance and verdict.
5. **History and handoff.** Preserve scoped decisions with rule, evidence
   frontier, and dependencies. New evidence or a revised rule can lead to
   a new assessment linked to the earlier one. Record disagreement
   explicitly. Pass typed claims, limitations, and audience constraints
   to S6, and leave publication authority with the established evidence
   path. S7 can exercise these same decisions on known cases.

These are responsibilities for design discussion. Record layout, exact
status vocabulary, support profiles, and implementation bundles follow
after worked cases and design review.

## Important design choices

| Choice | Proposed direction and strongest alternative | Cost and failure addressed |
|---|---|---|
| Measurement versus decision | Reuse qualified S4 outputs and evaluate a separate rule. The strongest alternative is one callable that scores and decides, as in parts of the historical route. | Extra contracts make the exact population, quantity and judgment visible. This prevents a change in metric or denominator from quietly changing a finding. |
| Common policy versus bespoke rules | Start from reusable typed checks for scope, evidence, comparison and numeric predicates. Allow explicitly installed and independently qualified rule extensions for cases the common grammar cannot express. The alternative is a fully programmable rule for every finding. | The common core needs a bounded grammar and extension boundary. It avoids hidden system-specific rules and lets supported behaviors be tested independently. |
| Decision vocabulary | Keep applicability, evidence sufficiency, decision and confirmation separate. A single flat verdict would be simpler for display. | Separate facts require an explicit report mapping. They prevent a missing run, a failed minimum, and a tested threshold miss from being interpreted as the same event. |
| Threshold and uncertainty | Bind each comparison operator and specify whether it uses a point, endpoint, count, or compound condition. The alternative is one uniform interval policy. | Each rule needs its own boundary tests. This preserves the meaning of point rules, sampling intervals and outer bounds, including strict versus inclusive comparisons. |
| Registration | Require evidence of the relevant rule, scope and temporal ordering. The alternative is an inherited label derived from a rule date and run date. | Some historical labels will be representable only as reported labels or unresolved for new analysis. This prevents retroactive promotion through date or protocol similarity. |
| History and scope | Add an immutable assessment at a new cutoff and explicitly link it to its predecessor. The alternative is updating a single current verdict per kind. | Consumers must choose a view or cutoff. They can recover what evidence was available at each decision and keep distinct results across subjects, audiences and revisions. |

## Existing foundations and historical boundary

- [Protocol v1](../PROTOCOL.md), its [catalog](../protocol/kinds.py),
  [thresholds](../protocol/thresholds_v1.json), and
  [finding engine](../findings.py) provide the historical K01–K15 vocabulary,
  controls, verdicts and date-label behavior. Parts of that engine compute
  measurements and apply rules together. Its reported outputs and evidence
  identity remain the basis for historical compatibility.
- [S4 planning](../measurement/planning.py),
  [recorded work materialization](../measurement/evidence.py) and
  [profile assessment](../measurement/assessment.py) supply pinned scope,
  recorded results and explicit qualification boundaries. Qualification
  of a quantity does not settle an S5 finding rule.
- The [October protocol proposals](project/w2-rebase-2026-10-31.md)
  surface useful design questions about applicability, rule-specific
  preregistration, verdict margins, rounds and version comparisons.
  Historical rule and label behavior require deliberate compatibility
  mapping. A new rule or protocol version requires its own review.

## Next review

Start with the identity and lifecycle of one finding. Compare a matched
name-control case, a missing-evidence case, a scope mismatch, and a later
correction. Resolve what makes two assessments the same question and what
changes the rule, claim scope, basis, or outcome. Then cover applicability,
evidence requirements, rule families, registration, and history before
selecting initial support and planning implementation.
