# S5 applicability and evidence requirements

DLV-08, DLV-09, DLV-10. 5 November 2026. Design proposal following
[finding identity and lifecycle](subsystem5-finding-identity-lifecycle-design-2026-11-05.md).
The cases are hypothetical and the state descriptions are conceptual.

## Keep four questions separate

| Question | Evidence needed | Example disposition |
|---|---|---|
| Can the scientific question apply at this scope? | Exact subject, configuration, relevant capability or information channel, target and reference semantics where required | Applicable, inapplicable with a demonstrated reason, or unresolved |
| What happened in the intended comparison? | S2 design and S3/S1 evidence of execution, realized conditions, deviations and capture, at a named cutoff | Unrun on closed evidence, executed as required, deviated, or unresolved |
| Can this rule use the evidence? | Exact selected measurement and qualification, required population and units, relevant premises, and evidence available for this assessment | Sufficient, proven insufficient, or held on an unresolved, conflicting or restricted premise |
| What does the rule decide? | Sufficient evidence for the named decision branch and the exact rule revision | Threshold met, threshold missed, or a rule-defined inconclusive outcome |

A record can faithfully establish that a control was inapplicable or
never run while leaving the scientific decision unevaluated. Confirmatory
status is a separate assessment of registration and exposure history.

## Worked name-swap cases

Reuse the illustrative six-case rule R1 from the identity review. It
requires a qualified full-frame mean, at least five eligible pairs,
and a drop of at least 0.10. This is an example and the historical
[K04 definition](../protocol/thresholds_v1.json) remains a separate rule.

| Situation | Evidence and disposition |
|---|---|
| **Inapplicable for this configuration** | The exact path takes only a numeric array, and verified realization and interface evidence establish that headings are removed before invocation and excluded from all relevant inputs in scope. The question about using names in that path is inapplicable. A behavior-invariance control on the wrapper can be a separate applicable question. An algorithm's name or a data-only capability declaration alone leaves other paths unresolved. |
| **Applicable, control unrun** | The wrapper can receive names. The campaign's closed attempt account establishes that the swapped arm was never launched. Record the unrun control. If the launch acknowledgement was lost and the attempt account stays open, record unresolved execution instead. |
| **Ran, evidence incomplete** | Four visible pairs average 0.12, with two unknown. The observed count is four and the eligible count may be higher. The descriptive value stays available at its own scope. Hold the full-frame decision and identify the missing pairs. With a complete account proving exactly four eligible pairs, the minimum is established as unmet. |
| **Ran, control deviated** | The same 0.12 comes from inputs that change both names and column order, violating the names-only comparison. Preserve the observation and the deviation. Withhold the name-specific finding. A compound comparison would have its own question and scope. |
| **Ran, sufficient evidence, threshold missed** | All six eligible pairs are qualified, with matched conditions and a verified swap. The exact full-frame mean is 0.09. Record the miss under R1 at this scope. The result supports a claim about the tested threshold, while a claim of name invariance needs its own design and rule. |

## Evidence checks should name what they establish

1. **Subject and realization.** Bind the system version, configuration,
   relevant boundary and scientific target. Reuse S2's intended controls
   and S3's evidence of what was actually delivered, executed or exposed.
   A declaration answers what was planned. A realized fact needs evidence
   from the boundary it describes.
2. **Meaning and measurement.** Bind the metric, reference interpretation
   and coverage, units, contrast direction, and supported numerical form.
   A committed-direction score and an expected-direction score can both be
   valid and still answer different questions. A contested reference can
   support an agreement rule. Accuracy requires a reference with that
   meaning. A reference-free crash rule can instead require verified
   attribution of the failure to the native system.
3. **Frame and selection.** Bind intended and analyzed units, eligibility,
   pairing, and unresolved members. A retry shares its scientific unit
   with the original attempt. A rule that counts clusters cannot use the
   number of edges, attempts or files as a substitute. A prespecified
   missingness policy can support a different quantity, with its own
   scope and qualification.
4. **Qualification and exact references.** Bind the S4 result, its
   calculation or other declared origin, and qualification for the
   selected quantity and scope. Qualification of arithmetic alone leaves
   finding-specific premises open. An exact match on the basis of a replay
   establishes reproducibility at that scope. It supplies no independent
   reference truth, population membership or new trial.
5. **Cutoff, conflicts and access.** Record the evidence considered, which
   requirements it supports or contradicts, and why anything remains
   unresolved. Evidence can be known to exist and unavailable to the
   assessment audience. A public projection may cite an authorized
   private assessment at its permitted disclosure scope. Independent
   public verification requires accessible evidence for the claim it makes.

Preflight can establish facts about the intended question and what evidence
would be required. Later assessment can establish realized control,
eligibility and measurement from actual evidence. At each cutoff, preserve
the results of the checks that ran and label checks left unevaluated.
For example, verified closed records can prove a minimum was missed even
when a separate score is unavailable. A newly received source supports
another linked assessment. A conflict remains open until a scoped basis
resolves it.

## Design choice and next review

Use typed, rule-specific evidence requirements with shared checks for
identity, scope, authority and provenance. A single readiness flag or a
first-failure status is simpler to consume. The proposed design carries
more evidence and needs explicit mappings for summaries. In return, S6
can distinguish an unsupported case from a tested miss and show which
gaps are addressable. S7 can independently test each distinction.

Reuse [S2's lifecycle and support contracts](subsystem2-family-profile-lifecycle-contract-2026-11-02.md)
and [S4's qualified evidence scopes](s4/release-review-2026-11-05.md).
The next review should map rule families and the decision evidence each
needs. Use point rules, interval and bound rules, count rules, and
compound rules to test strict boundaries, partial evidence and the
meaning of an inconclusive decision.
