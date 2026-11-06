# S5 registration and claim status

DLV-08, DLV-09, DLV-10. 5 November 2026. Design proposal following
[rule families and decision semantics](subsystem5-rule-families-decision-semantics-design-2026-11-05.md).
The examples are hypothetical except where explicitly marked historical.
Status labels are conceptual. Existing protocol and checkpoint labels
retain their own provenance.

## A separate assessment

A finding decision says what an exact rule concluded. Registration
status says what the evidence establishes about how that rule and its
analysis choices were selected. A threshold meet, miss, or inconclusive
result can each be assessed against the same prospective protocol.
Confirmation status does not establish control validity, measurement
qualification, adequate evidence or a positive finding. Keep all of
those assessments distinct.

For a claim of confirmatory status, the proposed minimum is:

1. **Exact prior commitment.** Identify what was fixed, by whom, for
   which questions, systems, cases, controls and analysis scope, under
   which registration policy. Pin the rule and material analysis choices,
   including eligibility, selection, metric, missingness and stopping,
   and any error or multiplicity controls required by the claimed design.
   An internal durable commitment or an external registration can
   establish the specific commitment claim allowed by that policy.
2. **Supported timing and exposure scope.** Establish that the required
   choices were committed before the applicable boundary. Identify the
   relevant people or services, what information they could access or
   use, and which evidence establishes that boundary. Depending on the
   design, relevant information may include partial results, pilot
   outcomes, reference or holdout information, or proxies that can
   influence a choice. Run start, outcome capture, delivery, access and
   analysis are distinct events. Apply the boundary specified in
   advance, including a before-execution requirement if the policy has one.
3. **Conformance.** Match the performed analysis and assessment to the
   committed rule, allowed discretion, population and other material
   choices. If an amendment or adaptive decision is relied on, pin the
   authority, inputs, timing and scope that make that specific action
   admissible under the policy.

A digest establishes content identity. Timing needs evidence that
anchors those bytes, such as a trusted registration receipt or a scoped
durable event order under the policy. A local file date, a filename,
or a date written inside an imported file supplies a weaker historical
claim. Same-day timestamps or overlapping time windows leave ordering
unresolved unless independent evidence establishes sequence. Preserve
time precision and clock comparability. Distinguish evidence of delivery
from evidence of access and from evidence of actual use. An exposure gap
can leave the required information boundary unresolved.

## Worked examples

| Case | Assessment |
|---|---|
| **Rule fixed before exposure** | A receipt anchors the exact 0.10 rule, paired frame, eligibility, metric and analysis choices before the relevant access boundary. The applicable information history and actual analysis match that commitment. A qualified 0.12 meets the rule and supports confirmatory status for this assessment. A qualified 0.09 would miss under the same confirmatory design. |
| **Threshold changed after seeing results** | R1 fixes 0.10. After the analyst sees 0.12, R2 changes the cutoff to 0.15. On the same qualified basis, R1 meets and R2 misses. R2 is a separate, exploratory assessment on those results. R1's own confirmation claim can still be assessed against its original commitment and conformance, including any rule about which analyses must be reported. |
| **Revised plan for new cases** | If R2 is fixed after the development cases were seen, it can support a separate prospective assessment on genuinely unexposed confirmation cases under an eligible protocol. Preserve the development influence and the new scope. Combining exposed and unexposed cases needs a rule and analysis that explicitly allow the combination. |
| **Permitted repair** | A predeclared policy allows replacing an unreachable evidence mirror with a byte-identical copy. Record the trigger, byte pin, authorization, and timing. If the population, inputs, analysis and information boundary conform, confirmation can remain supported. A source change that alters selected bytes needs its own assessment. |
| **Permitted adaptive choice** | The commitment allows replacement of an objectively ineligible case, using a fixed reserve order and an eligibility check restricted to structural metadata. Record the failed check, the permitted inputs, chosen replacement and applicable frontier. Conformance may preserve confirmation when both the selection and analysis policies accommodate it. If score information entered the decision contrary to policy, a signed amendment alone cannot establish conformance. |
| **Historical import with uncertain timing** | A certificate reports confirmatory status and provides a rule digest and same-day date. Retain that as the original reported label with its source. S5's own status is unresolved if ordering, exact rule applicability, or exposure evidence is insufficient. A later authenticated receipt can support a new linked assessment while preserving the earlier cutoff. |

A documented post-exposure choice supports an exploratory designation
for the affected scope. An absent or inconclusive registration history
supports an unresolved designation. If evidence conflicts, retain the
dispute and the specific gap. A reported label is a sourced historical
statement. It can coexist with an independent assessment and its
different provenance. When a record contains mixed histories, expose
the applicable scopes. A single claim over the combined frame requires
its own supported registration basis.

## Historical mapping and handoff

The historical [protocol catalog](../protocol/kinds.py) derives its label
using the kind's registered date and the reported runs date. Preserve
that behavior as historical evidence. The
[checkpoint account](project/q1-checkpoint-2026-10-31.md) distinguishes
the AB-06 K04/K07 labels from the earlier Causal-Copilot measurements and
the BND-08 M3 preregistration from the package K11 threshold. A shared
statistic or kind can have two provenance paths. Any linkage between an
external commitment and a package rule requires explicit comparison of
their quantity, population, conditions, operator and decision scope.

Reuse [S2 commitment, amendment and exposure records](../experiments/lifecycle.py)
and the [S3 temporal and disclosure model](subsystem3-operational-contract-closure-2026-11-03.md).
S5 consumes their evidence under a named claim policy. The public view
can carry a permitted, attributed status with a restricted basis. A
claim of independent verification requires accessible evidence or an
explicitly accepted assurance mechanism at the claimed scope.

The strongest simpler alternative is to use the reported registration
and run dates as the generic decision rule. It is easy to apply and
recovers legacy display behavior. Exact commitment and exposure evidence
requires more provenance and can leave historical assessments unresolved.
It prevents retrospective analyses and revised rules from inheriting
confirmation through shared dates or labels.

Next, review decision history and handoff to S6. Work through disputed
assessments, later qualification or exposure receipts, and public versus
restricted views before consolidating the S5 contract.
