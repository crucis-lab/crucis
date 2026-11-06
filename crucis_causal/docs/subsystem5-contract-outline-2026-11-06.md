# S5 contract outline and support profiles

DLV-08, DLV-09, DLV-10. 6 November 2026. Consolidated design proposal.
The examples are hypothetical. The profile names describe support claims
for review. Exact wire forms, identifiers, and interface signatures follow
this review.

## Minimum account

S5 accounts for one assessment of one finding question under one exact
rule revision. The finding kind groups questions. It carries neither
the scientific target nor a decision by itself. A request can ask for
several findings. Each assessment retains its own target and scope.

| Block | Required for a scoped assessment |
|---|---|
| Identity and origin | Assessment identity and attributed origin or assessor. Distinguish a new assessment from a preserved historical assertion. Bind an actual evaluation occurrence when one is claimed. |
| Question and scope | One question with the audited subject and configuration, intended target or population, control and direction where relevant, measured quantity, and applicable reference interpretation. Reuse exact S1/S2 identities. Keep intended units and the analyzed set separate where selection matters. |
| Rule | One exact revision with a supported decision definition. Bind its prerequisites, operands, evidence policy, comparator and allowed outcomes. A human-facing finding label is insufficient to identify the rule. |
| Cutoff and audience | The evidence view available for the assessment and its audience or read boundary. An authored cutoff is distinct from event time and publication time. |
| Basis | The evidence and its roles, how it was selected, and known gaps, conflicts or restrictions. Each decisive clause or supported disposition has a traceable basis. An empty selection must be scoped and explained. |
| Dispositions | Separate applicability, observed execution where relevant, sufficiency, decision and registration status. Distinguish an evaluated inconclusive result from a hold, an unevaluated check, and an unrequested claim. State the reasons and the limits of the conclusion. |

The preservation floor is smaller. An opaque or incomplete historical
source can be retained with attributable origin, captured identity and
extent, import cutoff and audience, and explicit gaps. Its reported
values and labels stay attributable. A scoped assessment needs the
question, rule and basis above. Unknown scope or rule provenance can
hold that stronger interpretation without creating a synthetic finding
question or evaluation occurrence.

## Evidence added only when the claim calls for it

| Claim or operation | Conditional evidence |
|---|---|
| Interpreting a native result or control | Actual S1 meaning and mapping, S2 intent and reference applicability, and S3 realization, exposure or closure for facts claimed about the run. An operational incident rule may use verified S3 outcomes directly. |
| Measuring and deciding | Selected S4 quantity, scope, origin and qualification. Bind clause premises and decisive evidence. A preflight hold can identify missing operands without producing a score. |
| Counts, comparison or uncertainty | Named units and population or closure, actual eligibility and pairing, dependence and missingness where relevant. Point, sampling interval, outer bound and compound rules require their own evidence and interpretation. |
| Registration | Exact commitment and scope, anchored chronology relative to relevant exposure, conformance, and any permitted amendment or adaptive choice. A historical reported label can be preserved with its source alone. |
| History | Typed predecessor or competing assessments and affected dimensions. A correction, resolution or retraction requires its scoped evidence and adjudication basis. A mere association can remain descriptive. |
| S6 handoff | Explicit selection, audience authority, outward claim scope, dependency closure and verification limits. Exact outward bytes and storage receipts become relevant when a publication is claimed. |

## Proposed support profiles

These profiles make independent claims about named parts of the account.
They do not form one scale. Each assessed profile names its target,
criterion or policy, evidence, cutoff, audience and supported scope.
Request, assessment and establishment remain separate. Scope-specific
qualification is needed to claim an evaluator supports a rule family.

| Profile | Guarantee and minimum evidence | What remains withheld |
|---|---|---|
| Preservation | Trace the attributed source, captured content or reported statement, exact extent and any unavailable material. | Original history, interpretation and scientific decision where the source cannot establish them. |
| Scoped assessment | Interpret the exact question and rule and account for the applicable prerequisites, execution state and evidence gaps using scoped support. A faithful hold can satisfy this profile. | A numerical or predicate decision where the necessary evidence is absent or contested. |
| Rule decision | Scoped assessment plus applicable, sufficient evidence for the exact decision branch, qualified decision semantics, and a recorded clause trace. A rule-defined inconclusive branch can be an established result. | Broader claims, alternative metrics or rule revisions, and confirmation status without its separate evidence. |
| Registration | Scoped assessment plus the exact commitment, ordering and conformance evidence appropriate to the status being asserted. Can stand independently of a completed verdict. | Confirmation when ordering, relevant scope or conformance is unresolved or contradicted. |
| History | Scoped assessments or attributable records with exact identities and supported relationships. Adjudication additionally needs a scoped authority and a deciding basis. | A resolved current conclusion when the dispute remains open. Alternate rules or populations retain their own claims. |
| Handoff | Attributed, authorized selection for the intended audience, with outward dependencies and assurance scope established. Can carry preserved statements, holds or supported findings. | Independent verification beyond accessible proof or the accepted assurance mechanism. Handoff establishes no additional scientific claims. |

Preservation underlies all profiles. A decision and an assertion about
its registration can be paired when both support claims are established.
History can establish that a conflict is open or support an adjudication.
Handoff can disclose only established claims and faithfully labeled
observations or gaps, as allowed by the audience. Producing a projection
does not confer publication authority. Qualification of S4 arithmetic
or compatibility with a legacy report is not S5 rule qualification.

## Worked assessments

All current assessments below name an assessor, a fixed subject and
configuration, an exact hypothetical rule, and a cutoff and authorized
internal audience unless another audience is specified. Each selected
measurement stands for the named S4 quantity, origin, scope and
qualification. Registration, history and publication are unrequested
unless shown. These defaults apply only within the examples.

### A. Paired point with a minimum count and a late receipt

Question A asks for the full-frame mean real-minus-swapped directed-F1
difference on six fixed cases. Rule A requires a verified names-only
change, five eligible pairs and a qualified point at least 0.10.

At cutoff A1, four pairs are visible and two are unresolved. A separate
available-pair description is 0.12. S5 records that applicability is
supported, execution of the arms is established at the stated boundary,
and the full-frame measurement and minimum count remain unresolved.
The exact rule decision is held. Preservation and scoped assessment
can be established. The reported four-pair value has its own scope.

At A2, all six eligible pairs and the realized swap are qualified.
The full-frame result is 0.12. Both the count and point clauses are
supported. The threshold is met. Registration is assessed but remains
unresolved on same-day records. At A3, an authenticated receipt and
the existing comparable exposure and conformance evidence establish
confirmation for the same rule and scope. The new assessment reuses
the decision trace and qualifies the registration claim. History
links the hold, decision and status update with separate cutoffs.

### B. Outer bound with no point substitute

Question B asks about real-minus-swapped delivery utility over a
fixed paired frame, with its named utility and delivery policy.
Rule B compares the true scoped utility difference to 0.10 using a
closed outer enclosure. S3 delivery and capture evidence, including
the unresolved slots, supports the S4 enclosure [0.08, 0.16] under
the stated utility policy. S5 records applicability and sufficient
evidence for the enclosure, then a completed inconclusive decision
because neither sufficient endpoint test settles the threshold.
Preservation, scoped assessment and rule decision can be established.
A point, a sampling inference and a claim about attainable endpoints
remain withheld. If the enclosure basis itself is unavailable, the
decision instead remains held at scoped assessment.

### C. Compound predicate with a missing interval

Question C asks about a scoped paired contrast. Rule C requires its
matched-control and unit prerequisites and tests both a point at
least 0.05 and a lower sampling endpoint strictly above zero.
The rule explicitly allows a decisive clause to settle the predicate
while the other operand is missing. At C1 the common prerequisites
hold, the qualified point is 0.04, and the interval's cluster basis
is unavailable. S5 records a false point clause, the held interval
clause and a supported miss for the compound predicate. Sufficiency
is scoped to that decision. It establishes no interval claim. If the
qualified point were 0.06, the missing interval would hold the decision.
If the pairing itself were disputed, that gap would affect both clauses.

### D. Attributed incident count without a reference graph

Question D asks whether at least one native crash occurred in a
declared run set. Rule D permits an early positive decision on one
verified native crash. At D1 the attempt account and attribution
establish one such crash and leave another attempt unresolved.
S5 records an established lower count of one and a supported meet.
An exact total and a crash rate remain unestablished. A closed
account showing all required attempts and zero attributed crashes
could support a miss. This rule uses qualified operational evidence
and its own unit and attribution requirements.

### E. Historical label and a restricted handoff

An imported certificate reports a rule and verdict with a
confirmatory label. The import can retain exact bytes, attribution,
extent, cutoff and its restricted audience. If the original analysis
or event order is unresolved, preservation is established and the
independent scientific decision or registration claim stays withheld
as appropriate. A public projection may present the permitted attributed
statement and source identity at a dated cutoff. It identifies its
verification limits. A reproducibility claim requires a separate
authorized basis. If an internal correction later withdraws support
and the relationship is disclosable, link a new authorized view. A
current public claim needs an authorized current assessment.

### F. Conflicting alignments and retraction

Use Question A and Rule A. At F1 two assessments assert the same
scientific scope using competing alignment receipts. One reports
0.12 and meets the rule. The other reports 0.09 and misses it.
Preserve both attributed decisions. The current scoped assessment
records disputed pairing and holds a resolved decision. History
supports the existence of a conflict with exact links to its sources.
At F2 an authorized review establishes that the first alignment was
invalid and leaves the second unqualified. Record a scoped retraction
of the first conclusion and a held replacement. History supports the
retraction with its basis. A valid replacement decision still needs
qualified evidence. An earlier view retains its own decision and cutoff.

## Gaps exposed by the examples

- A held or partially evaluated record needs a supported reason and
  scope even when it contains no measurement. A smaller preservation
  floor avoids inventing rule or assessment identities for imports.
- Sufficiency attaches to a decision or clause. An interval can be
  unavailable while the declared compound decision is supported.
  A bound can be supported while its threshold comparison is
  inconclusive. A count bound may settle a rule while the rate stays open.
- Registration and decision have separate bases. A later receipt can
  change one without authorizing a new claim about the other.
- Evidence scope, assessment audience and publication authority need
  distinct roles. A projection must state which earlier assessment it
  presents or withholds, to the extent disclosure allows.

Reuse the [S4 support account](s4/release-review-2026-11-05.md) for
measurement evidence and the
[S6 handoff proposal](subsystem5-decision-history-s6-handoff-design-2026-11-05.md)
for scope and verification limits. Before freezing serialization,
enumerate role cardinalities, typed references and version rules.
Round-trip the held, decisive, inconclusive, corrected and restricted
cases with explicit missingness and dependency pins.
