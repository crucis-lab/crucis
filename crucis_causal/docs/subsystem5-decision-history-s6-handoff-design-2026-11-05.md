# S5 decision history and handoff to S6

DLV-08, DLV-09, DLV-10. 5 November 2026. Design proposal following
[registration and claim status](subsystem5-registration-claim-status-design-2026-11-05.md).
The cases are hypothetical. The record and assurance names describe
semantics for review before wire and interface design.

## A finding history is a set of related assessments

Preserve each assessment at its exact question, rule revision,
evidence basis, cutoff and audience. Keep its applicability, evidence
sufficiency, decision and registration status visible. An evidence
update, correction, retraction, alternative rule, alternative target
and audience projection each express a different relationship.
Chronological order can help reconstruct the history. Selection for a
report needs an explicit policy and evidence that the chosen relationship
and scope justify the selection.

For an assessment presented as corrected or superseded, identify the
affected earlier assessment, the dimensions affected, the reason and
basis, and the authority or process that adjudicated the change. A
retraction can withdraw support at that scope while leaving the replacement
decision held. It needs no substitute verdict. Preserve prior views so
S6 can reproduce what was known and stated at their cutoffs.

## Case A. Two assessments disagree

Use the six-case name-swap question and rule R1 from the
[identity review](subsystem5-finding-identity-lifecycle-design-2026-11-05.md).
Both assessments say they used R1's inclusive 0.10 cutoff on the same
six intended cases. One reports 0.12 and meets the rule. The other
reports 0.09 and misses it.

- Compare the actual bases first. If one uses committed direction and the
  other expected direction, or one uses a different frame, distinguish
  their scopes. If a rule requires one of those bases, assess the
  conflicting binding claim under that rule.
- If both assert the same scientific scope but use different alignment
  receipts, preserve both accounts. With unresolved competing alignment
  evidence, the current conclusion is disputed. The report can show the
  competing decisions and their scoped reason where disclosure permits.
- If the rule, admissible evidence, declared basis selection and inputs
  really are identical, incompatible decisions indicate a disagreement
  in interpretation, evaluation or recording. Retain both occurrences
  and investigate the trace. An independent replay uses the same
  scientific units and can check the decision path.
- If an authenticated mapping resolves the alignment, select the linked
  corrected assessment on that evidence and record why the earlier
  one was affected. If the only established fact is that the original
  mapping is invalid, retract support for the earlier conclusion and
  keep the replacement held pending qualified evidence.

An earlier report can still be reproduced as of its cutoff. A current
report needs to distinguish open dispute, correction and retraction
within its authorized evidence view. Choosing the latest timestamp or
majority verdict would be simpler, but could select an unqualified
result or count repeated review of the same evidence as corroboration.

## Case B. A late receipt changes only registration status

At cutoff A, the six qualified pairs give 0.12 and R1's threshold is
met. The assessor has the exact rule, but the available same-day dates
leave the order of registration and exposure unresolved.

At cutoff B, an authenticated receipt becomes available. It anchors
the exact rule and material analysis choices at 09:00. The established
exposure boundary was 11:00 on the same comparable clock. The receipt
matches the same scope, and the remaining policy and conformance
requirements are already supported. A linked reassessment can carry
confirmatory status while reusing the pinned decision basis and its
0.12 result. The receipt's asserted event time is earlier than the
time at which it became available for assessment. The report for
cutoff A still says the threshold was met with registration unresolved.

A receipt naming a different rule version, an incomparable clock, or
a scope with earlier relevant exposure leaves the ordering or policy
claim unresolved or contradicted as appropriate. A later established
withdrawal of an essential receipt can likewise change registration
status without changing a qualified numerical decision. Preserve the
affected status, the prior status and the evidence for the transition.

## Case C. A public report uses a restricted evidence base

Suppose authorized private reviewers can resolve the six paired
records and the registration receipt. The public audience is allowed
to see the aggregate 0.12, the tested scope, the rule and an attributed
statement from the audit team. The permitted public statement can
say the team found that the threshold was met under R1 and describe
the allowed registration status. It also identifies the available
verification scope, such as public verification of the statement's
identity and a restricted derivation.

- A public integrity check can establish that the released report bytes
  match their pin. Independent reproduction of a finding needs the
  evidence and authority appropriate to that claim. If a trusted
  assurance mechanism is explicitly allowed, identify its issuer,
  verified scope and limits separately from reproducibility.
- Publish a separately authorized view with its own identity and cutoff.
  Check the closure of what the view reveals, including labels,
  cohort size, timestamps, reason text, identifiers, pointers, digests
  and whether evidence or a dispute exists. Retain a link to the
  private assessment in authorized records. Publish that link only
  when disclosure permits it.
- If a public correction can safely say the earlier result is
  superseded, state that with the authorized reason or status. If a
  restricted change cannot be disclosed, a still-permitted earlier
  snapshot can be presented as a dated release. A claim about the current
  state needs an authorized, supportable current view. If even an
  attribution would disclose restricted information, withhold that
  statement under the audience policy.

## Handoff contract for review

S5 should hand S6 an explicitly selected assessment or audience view,
and enough authorized structure to present its actual claims. At the
applicable scope the handoff identifies:

- The question, rule and exact assessment, plus subject, frame, and
  cutoff or release identity.
- The scientific disposition and its reason, separate from applicability,
  evidence sufficiency and registration status.
- The decisive clauses, permitted measurement references and qualifications,
  the evidence supporting each claim and the limitations that travel with it.
- The permitted history relationships and any adjudication, retraction or
  unresolved dispute relevant to the chosen view.
- The audience, disclosure authority, and what a reader can verify
  independently or only through attributed assurance.

S6 can select and present eligible claims and bind the rendered output to
their evidence. Changes to thresholds, scope, adjudication or claim
status require their corresponding S5 account. Report certification can
make distinct claims about integrity, provenance and reproducibility.
Reuse [S3's audience and publication controls](subsystem3-operational-contract-closure-2026-11-03.md)
and [S4's pinned carrier pattern](s4/b09-publication-implementation.md)
for disclosed evidence and publication receipts. A report pointer is a
separate selection effect from an immutable evidence view.

Next, consolidate the S5 contract around the minimum finding account,
conditional evidence roles and support profiles. Use complete cases
from each rule family to check how the pieces fit before serialization.
