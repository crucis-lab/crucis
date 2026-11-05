# S5 finding identity and lifecycle

DLV-08, DLV-09, DLV-10. 5 November 2026. Design proposal following the
[opening review](subsystem5-structure-design-2026-11-05.md).
The examples are hypothetical. Rule names and dispositions illustrate the
semantics under review. Exact wire names, identifiers, and state vocabulary
are later design choices.

## What has an identity

| Concept | What it names | When it changes |
|---|---|---|
| Finding kind | A versioned class of claims, such as name reliance | When the catalog contract changes. A kind alone identifies no particular finding. |
| Finding question | The claim target: audited subject and configuration, intended population, control and direction, measured quantity and reference interpretation | When the scientific target changes. A pinned selection rule may define a population without enumerating realized members in advance. |
| Rule revision | The exact decision policy applied to that target, including thresholds, operators, evidence requirements and the meaning of the decision | A threshold, comparator, or decision requirement changes the revision. A change to the quantity, contrast, or population also changes the question. |
| Assessment | The disposition for a question under an exact rule and evidence basis, with a cutoff, audience and provenance | New evidence, a different basis selection or a correction leads to another immutable assessment. A separate evaluation occurrence can remain distinct even when its inputs and output match. |

A question and rule revision define the scope within which assessments
can be compared over time. The basis names the evidence actually used
and how it was selected. It preserves the planned frame and unresolved
members separately from the realized analysis set. Registration evidence
and the resulting claim status belong to the assessment. A new receipt
about timing may change claim status without changing the decision.

## One example through three cutoffs

Use one fixed system version, six intended cases, the real-name minus
swapped-name directed-F1 contrast, and a verified names-only control
where established. Suppose illustrative rule R1 requires a qualified
full-frame mean, at least five eligible pairs, and a point of at least
0.10. This borrows features from the historical K04 rule while adding an
explicit full-frame requirement for the example.

1. **Initial hold.** Four pairs are visible and average 0.12. The other
   two are unresolved at cutoff A. The four-pair descriptive value can
   be retained at its own scope. The full-frame result is held. The
   record explains the missing evidence and leaves the final eligible
   count unresolved. A complete four-case frame with four eligible
   pairs would instead establish that the minimum was unmet.
2. **Later evidence.** The two missing pairs are recovered and
   qualified by cutoff B. The six case differences sum to 0.72,
   producing a qualified full-frame mean of 0.12. An assessment links
   back to the hold and records that the rule is met on the expanded
   basis. The question, intended frame, and rule are identical.
3. **Correction.** At cutoff C, evidence establishes that one score
   had been aligned to the wrong counterpart. The affected difference
   changes from 0.22 to 0.04. S4 supplies a linked, newly qualified
   result for the same six intended cases. The sum falls from 0.72 to
   0.54, so the mean is 0.09. A new S5 assessment records that R1's
   threshold was not met and cites the correction and the affected
   earlier assessment. A view as of B still shows what was decided at B.

If the competing alignments are both plausible at cutoff C, record the
conflict and withhold the conclusion that depends on it. Selecting an
alignment requires evidence of the actual correspondence. If the correction is
to S5's interpretation instead, such as applying the wrong comparison
operator, a linked correction can reuse the same qualified S4 result
and identify the S5 error. Both paths can use the existing native evidence.

## Changes of rule and population

| Change | Identity and lifecycle consequence |
|---|---|
| R2 raises the cutoff to 0.15 while keeping the same scientific question | Compare R1 and R2 on the same qualified six-pair result of 0.12. R1 meets its cutoff and R2 misses. These are parallel assessments under different rule revisions. Each revision needs its own registration evidence. |
| Two missing cases arrive in the same intended frame | The realized set and basis change. The question is unchanged. If a rule permits a changing eligible set, preserve each actual denominator and require its declared selection policy. |
| Drop the two unresolved cases and ask for an available-pair result | That quantity is a separate descriptive target. The original full-frame hold stays open until the missing evidence is resolved. |
| Expand the intended frame from six cases to ten, or change the eligibility policy that defines the target | This creates a different question. Link it as a related analysis. Reuse compatible evidence with its original identities and apply the new population and registration requirements. |
| Discover a transcription error in the originally recorded frame | If prior evidence establishes what the intended frame actually was, preserve the erroneous record and explicitly link the corrected specification. Decisions that relied on the erroneous scope require reassessment. If the earlier intent is unresolved, preserve the uncertainty instead of calling a new design a correction. |

## Lifecycle and recovery

- Preserve the original request and cutoff. A record can state
  applicability, evidence sufficiency, a rule decision, and confirmation
  status separately. The lifecycle can begin with a hold or directly
  with a supported decision.
- Preserve asserted and observed time separately. A recovered event can
  have occurred before A and still have entered the assessor's evidence
  only at B. A later view can use it without rewriting what was available
  to the earlier assessment.
- Name the relationship between assessments. An evidence update, an
  error correction, an alternative rule, and a changed target have
  different effects. Supersession requires explicit, scoped evidence and
  an authorized decision about which assessment to use.
- Reconcile a retried write against the same intended immutable record.
  A replay or separate review may produce an independent occurrence.
  Both evaluations still share their original scientific repetitions.
  Disagreement at the same scope and basis should remain visible until
  adjudicated. A broader private assessment and a narrower authorized
  view also carry different evidence claims.

The strongest simpler alternative is a mutable verdict keyed by system
and finding kind. It makes reading the latest result easy, but combines
rule revisions, scope changes and evidence updates. The proposed design
costs more links and requires an explicit view or cutoff for reports.
It lets S6 cite the exact assessment and lets S7 validate which lifecycle
transition actually occurred.

Reuse the [S2 lifecycle distinctions](subsystem2-family-profile-lifecycle-contract-2026-11-02.md)
for intent and amendments, and the
[S4 contract](s4/approved-2026-11-04/s4-final-contract-review.md) for
measurements, qualifications and cutoffs. The next review should settle
applicability and evidence requirements before choosing the rule grammar.
