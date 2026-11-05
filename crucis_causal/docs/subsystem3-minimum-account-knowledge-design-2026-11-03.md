# S3 minimum execution account and knowledge transitions

Tickets: DLV-08, DLV-09; related DLV-10.
Date: 2026-11-03, America/Los_Angeles.
Status: semantic design recommendation for discussion; no S3 implementation,
serialization freeze, new native run or protected-data access.

## 1. Continuation and acceptance scope

Continue [execution identity and lifecycle](subsystem3-execution-identity-lifecycle-design-2026-11-03.md),
locally committed as 18d496cb0d2915d626d516744712b76dd8b882cb. The user affirmed
that direction and requested settling the minimum account, conflicting evidence,
later updates and closure with unresolved effects. This supports continuing the
conceptual account/history distinction. It is not recorded as blanket approval
of every P01-P10 detail or any exact S3 schema, backend or implementation bundle.

Existing accepted S1/S2 semantics and user constraints remain in force. The EA01-EA09
recommendations below refine P01/P04/P06/P10 and related identity/recovery boundaries.
They remain separately identified recommendations pending review. The companion
[methodology index](subsystem3-methodology-index-2026-11-03.json) preserves those
statuses and links current primitives to their scoped evidence and limitations.

## 2. Minimum account: six semantic blocks (EA01)

Recommend a small account E that points to existing S1/S2 records and owns its
operational history. It is not a new scientific unit, native result object or
permission token. These are required meanings, not frozen field names or a demand
for six new record types. Simple calls can reuse existing IDs and references.

| Block | Minimum meaning | What absence does not imply |
|---|---|---|
| Identity and fixed target | Stable E; purpose/mode; exact S2 binding or explicit observational/materialization target; recorder provenance and applicable policy references | No fabricated scientific trial or original native launch for a historical observation |
| Activity and association index | Relevant requests, attempts, commands/forwardings, native associations and coordinator occurrences, with explicit scope/extent | No recorded job ID does not prove no native job exists; a complete local journal index is not complete native visibility |
| Evidence index | Immutable source/observation/artifact references or declarations, with availability/integrity and source limits | Missing bytes do not become an empty output, a negative native outcome or zero usage |
| Scoped assessments | Current and historical conclusions, their exact subjects/questions, evidence cutoffs, named procedures and revision/conflict links | An unassessed question is not false; a successful metadata operation need not contain a passing assessment |
| Coordinator disposition and pending obligations | What the coordinator intends/is permitted to do next; unresolved effect, resource and exposure references and their accountable scope | A recorded decision does not itself grant authority, revoke a native job or discharge liability |
| Collection periods and closure views | Observation scope, stopping rule, cutoff, closure reason, captured evidence, outstanding gaps and later follow-up relationships | Closing collection does not mean native completion or final accounting |

At account creation there may be a target, recorder, locally empty history and an
open collection period, without a launched attempt. The indices must say what
they enumerate and through which cutoff. Empty/complete means no members in that
defined local scope; unknown native effects cannot be converted to an empty
complete native set. Conditional features use explicit applicability or unknowns;
an ordinary local call need not populate distributed-worker fields.

Changes to fixed intent retain their versioned S2/S1 relationships. Newly learned
native identity is recorded as later association evidence/assessment; it does not
rewrite the old prospective attempt that originally had unknown native identity.

## 3. Minimum meaning of an assessed fact (EA02)

Every changing conclusion needs enough context to answer:

1. **Question and subject:** what exact predicate/value is being assessed, for
   which command/attempt/native episode/action/artifact and within which scope?
2. **Applicability and evidence coverage:** does the question apply; was it examined;
   which evidence was available, unavailable, partial or outside coverage?
3. **Source and basis:** which immutable observations/bytes/declarations support,
   oppose or limit it, and under which admissibility/interpretation procedure?
4. **Two time/cutoff dimensions:** when does the native claim apply, if known, and
   by what observation/evidence cutoff was it available to this assessment?
5. **Conclusion and limits:** what value is supported, contradicted or unresolved;
   what conflicting or insufficient reports remain relevant?
6. **Authorship and revision:** who recorded/assessed it, using which versioned
   procedure, and which earlier assessments it revises or disputes?

Native event time/sequence may be unknown. Recorder creation time cannot fill it.
Evidence received later can describe an earlier event; it was not known earlier
merely because the event occurred earlier. Native status reports remain sourced
claims within their established semantics, not universal proof of hidden effects.

For clarity, a user-facing view might display the following labels. They are
derived descriptions, not new alternatives added to S1/S2 knowledge primitives:

| Display | Meaning |
|---|---|
| Not assessed | No completed assessment for this question/scope/cutoff |
| Unknown | Examined, but no adequate basis establishes the requested value |
| Supported value | Adequate evidence under the named rule supports that value |
| Supported negative | Adequate evidence supports an explicitly scoped negative claim |
| Disputed | Material admissible evidence supports incompatible values for the same question/scope |
| Not applicable | A named applicability rule establishes that the question does not apply |

Applicability, assessment coverage, evidence availability and evidential support
are separate dimensions. Unavailable evidence can coexist with a supported claim
from another adequate source. A conflicting raw report can be retained while its
admissibility is unresolved or insufficient; merely counting reports is no vote.
Existing S1 can retain unresolved values with disputed evidence; no new global
wire state is selected here. Unknown applicability is not not-applicable.

## 4. Update and conflict rules (EA03-EA05)

Recommend append-only observations and new assessment versions. History grows;
certainty need not grow monotonically. A once-supported conclusion may become
disputed or unknown when new evidence exposes a broken premise. Preserve the
earlier conclusion as the conclusion reached from its earlier basis/cutoff.

| Update | Required interpretation |
|---|---|
| No assessment -> assessment with insufficient evidence | Record unknown with the actual missing prerequisite; do not infer a negative |
| Unknown -> supported value/negative | New adequate evidence supports the scoped value; retain the earlier unknown assessment |
| Supported value -> same compatible value | Add corroboration/provenance if useful; duplicated native evidence does not multiply effects or independent support |
| Supported value -> admissible incompatible evidence | Record the dispute and withhold claims/actions requiring a uniquely established value |
| Disputed -> resolved value or unknown | Record why evidence was reconciled, scoped differently, retracted or shown inadequate; retain all original observations and the resolution basis |
| Assessor fails or a required procedure is unavailable | Record observer/assessment gap; do not attribute a native failure or invent a failed scientific predicate |
| New legitimate native state at another time | Record state progression at that time; do not misclassify ordered running -> completed reports as a contradiction |

Before declaring a conflict, compare the subject, native namespace/generation,
predicate meanings, event/interval scope and relevant contract versions. Child
completion versus parent running, observer timeout versus native running, or
partial capture versus native completion are different questions and can coexist.

Before declaring a resolution, require an explanation and evidence. A later arrival,
more convenient result, newer file mtime or preferred system name is insufficient.
Admissibility/authority rules must be explicit, versioned and appropriate to the
claim. Authenticity, identity binding and native semantic guarantees remain actual
backend/owner prerequisites; metadata alone does not establish them.

### Example 1: delayed state versus genuine conflict

Native job N1 reports running at native sequence 17, then completed at sequence
18. The sequence-18 observation reaches Crucis first. Receiving sequence 17 later
adds history; it does not roll N1 back to running or contradict sequence 18.

Now suppose two admissible records describe the same N1 generation and the same
native state boundary, with the same exclusive status semantics, but one says
running and the other says terminated. That is a real dispute. Do not choose the
last arrival. If a later correction demonstrates that one receipt belonged to a
different generation, publish that association correction and a revised assessment.
If no resolution exists, retain disputed state. Unknown event ordering cannot be
replaced with an assumed timestamp order just to resolve a disagreement.

### Example 2: partial output and failed termination

A1 produced graph G, and G's captured bytes verify. A1 later failed in a separate
postprocessing step. The output and the failure can both be established. Keep G's
actual role/extent and the termination evidence. Neither fact establishes full
response fulfillment or causal correctness. S2's declared selection and S4's
measurement prerequisites determine whether and how G is usable.

If the original output file later disappears, current retrieval can be unavailable
while the earlier capture observation remains valid. If a locator now contains
different bytes, record that change; do not replace the earlier pinned snapshot
or infer that the native system never produced G.

## 5. Two honest views of later evidence (EA06)

Retain both of these questions explicitly:

- **What was known at cutoff c?** Use only evidence admitted/available under that
  recorded cutoff. A late receipt cannot enter that earlier knowledge view.
- **What does the later evidence say happened by native boundary t?** A new
  assessment can incorporate later-acquired evidence about an earlier event,
  with the native-time/sequence uncertainty it actually carries.

Do not conflate collection cutoff, source event time, artifact capture time and
analysis data cutoff. Whether late evidence can enter a declared analysis depends
on S2's predeclared selection/timing rule. A rule based on witnessed event time
may allow late capture with adequate evidence; one based on receipt by a cutoff
may not. A new operational assessment does not silently change the analysis rule,
population, confirmatory/exploratory status or existing paper evidence contract.

### Example 3: lost submission, closed collection, later receipt

At c1, E1 has durable submit intent C1/A1, but acceptance is unknown. Collection
period L1 closes at its declared observation deadline. Its immutable view says:
intent recorded; acceptance unknown; output unavailable; native termination and
charges unresolved; follow-up obligations retained.

At c2, an appropriately bound receipt establishes that the provider acknowledged
N1 before c1. Append the receipt and a new assessment: acceptance is now supported
within the receipt's scope. L1's old knowledge view remains unknown at c1. E1 can
acquire this later evidence without a new scientific trial or an invented A2.
The receipt still does not establish start, completion, output capture or final
cost. Any active lookup or resumed observation needs its own applicable authority.

## 6. Closure with unresolved effects (EA07-EA08)

Recommend allowing a collection period to close with unresolved effects, with a
closure receipt that is explicit about them. Requiring every native effect to be
resolved would make bounded observation impossible for inaccessible or continuing
systems. Treating closure as native completion would manufacture evidence.

Minimum closure meaning:

| Item | Required content or limit |
|---|---|
| Account and observation boundary | Which E and collection period/scope closes; applicable policy and declared stopping reason |
| Evidence cutoff | Which immutable journal/evidence snapshot the closure assessed; source-time bounds remain separate |
| Capture coverage | What was observed/captured, what was not examined or remains unavailable, and any partial-index limits |
| Outstanding effects | Exact pending commands/attempts/native associations and unresolved receipt, stop, delivery, cost or exposure questions |
| Control disposition | What this coordinator stops or proposes next; actual revocation/fencing/stop enforcement needs separate evidence |
| Obligation disposition | Responsible scope and applicable follow-up/handoff references; no fabricated release, zero charge or allowance reset |
| Scientific handoff | Preserve intended-unit links and missingness reasons for S2's declared population/selection rules |
| Revision/follow-up | Immutable closure identity and links to later evidence, assessments or collection periods |

Distinguish three independent closures: the observer stops collecting; native work
is established stopped/terminated; resource/exposure obligations are settled or
explicitly handed off under an applicable policy. None automatically implies the
others. Administrative archival may retain pending obligations; it must not label
them discharged. This pass does not select a read-consumption or budget policy.

A closure marker does not itself revoke issued capabilities or stop a stale worker.
If actual enforcement is unavailable, record that limit and possible outstanding
effects. No future effect may be justified merely by the old closure record.
Detailed authority, ownership/fencing and reservation transitions remain separate
design topics. Optional follow-up polling cannot quietly continue a closed period
or bypass access, cost and exposure constraints.

### Example 4: cancellation acknowledgement

Collection reaches its deadline. A cancellation acknowledgement establishes receipt
of the cancellation request, while a subsequent native observation still reports
N1 running. These facts are compatible. Close L1 with cancellation acknowledged,
stop unestablished and possible ongoing resource consumption. Do not report a
confirmed stop or final zero usage.

Later stop evidence can establish a scoped stop time and revise the current
assessment. It does not retroactively make stop known at L1's closure, and may
leave the amount of intervening usage unknown. Reservation release requires the
actual applicable resource policy/evidence, not collection closure alone.

### Example 5: an interactive answer may have been exposed

S2 selected answer V for native action Q1. S3 recorded delivery command C2, but
the recipient acknowledgement is missing after a crash. L1 can close with delivery
unknown and exposure pending. Do not count V as definitely delivered, definitely
unseen, or permission for another read. Identical later question text does not
prove it is Q1. A matched delivery receipt can later support receipt of V; access
or use still needs its own evidence and permitted interpretation.

The applicable exposure owner may enforce a conservative hold or another explicit
policy while the effect is unknown. S3 records that policy's actual decision; it
does not invent a new production sealed-read rule here.

## 7. Follow-up after closure (EA09)

Late artifact/receipt import appends evidence and assessments under the same E
with their actual recorder times. It does not rewrite L1 or require a native job
to be relaunched. Resuming active observation opens a new explicit collection
period L2 linked to L1, with its current scope, authority and cutoff rules. L2 is
an observation boundary, not automatically a native session, attempt or scientific
repetition. Exact serialization may reuse existing event/session scope where valid.

If the same established native episode continues, retain its attempt identity.
A checkpoint relaunch still creates a successor attempt and continuation evidence.
A changed scientific target retains the appropriate new S2 binding/request history.
In all cases, claims about the earlier cutoff remain reproducible from their
original evidence set. Partial records remain available without pretending an
analysis population is complete or scoring an unobserved output as zero.

## 8. Choices, alternatives, reuse and remaining design

| ID | Recommended direction | Strongest alternative | Cost / failure prevented | Reuse / remaining design |
|---|---|---|---|---|
| EA01 Minimum account | Six reference-oriented semantic blocks; conditional features remain small | Single run summary plus arbitrary metadata | More explicit links; prevents hidden omissions and universal native assumptions | S1/S2 refs/indexes; exact minimum fields and cardinalities remain open |
| EA02 Fact meaning | Question/subject/scope, coverage, source, two cutoffs, procedure and revision | One status/value with a timestamp | More assessment context; prevents unscoped negatives and time confusion | S1 observations/assessments, S2 assessment_context; scoped S3 predicates unbuilt |
| EA03 Updates | Append evidence and version assessments; confidence may weaken | Overwrite the current fact in place with an audit log | History/recomputation cost; prevents unrepeatable earlier conclusions | Immutable packages/record identity; journal/view transactions remain open |
| EA04 Conflict | Compare meanings/scopes and retain material incompatible evidence | Latest-arrival wins or a global source-priority rule | Can leave more disputed results; prevents false conflict or arbitrary resolution | S1 disputed basis; admission/interpretation and reconciliation procedures need exact contracts |
| EA05 Negative/NA | Require positive justification for scoped absence and non-applicability | Missing record means false or irrelevant | More evidence/withheld claims; prevents missingness becoming a scientific negative | Existing knowledge/index states; exact native coverage guarantees are driver prerequisites |
| EA06 Later evidence | Separate knowledge cutoff from the event being described; honor S2 timing rules | Rebuild history/analysis using all newest evidence | Multiple explicit views; prevents hindsight and silent population/label changes | S2 commitment/selection/population contracts; precise as-of views remain to design |
| EA07 Collection closure | Close with an immutable cutoff, coverage and explicit pending effects | Wait until everything resolves, or collapse closure into a final run status | Pending-obligation handling; enables bounded collection without fabricated termination | S1 scoped outcomes and S2 gaps; closure/revocation interfaces remain open |
| EA08 Liabilities | Native-stop and resource/exposure settlement remain independently evidenced | Release resources/allowances whenever collection ends | Longer holds or explicit handoff; prevents understated cost and repeated exposure | S1 accounting/S2 exposure; authoritative reservation/release policy deferred |
| EA09 Follow-up | Late evidence appends; active collection resumes in a linked new period | Reopen/overwrite the old final record | More boundaries; prevents changing old cutoffs and confusing observation with a new trial | S1 history/publication; exact collection-period lifecycle still unbuilt |

Current primitives are substrates, not implementations of these S3 guarantees.
In particular, connections.core.outcome_observations groups supplied outcome facets
and preserves conflicting values; it does not adjudicate native event time,
coverage, authenticity or all the scope distinctions defined here. S3 cannot call
it over mixed-time evidence and claim these proposed temporal semantics already
exist. S2 profiles withhold incomplete checks and retain assessment context; they
do not implement the execution account or closure protocol.

## 9. Prospective conformance examples

Future S3 tests must cover the ordinary minimal account and targeted cases where:

- Running then completed native states arrive out of order without false conflict.
- Same-subject/same-boundary incompatible evidence remains disputed, including
  failed or unsupported resolution procedures.
- A source correction weakens a once-supported conclusion without deleting history.
- Missing evidence, not-assessed, scoped negative and not-applicable stay distinct.
- Native failure coexists with captured useful output and unknown response fulfillment.
- Collection closes while launch, termination, delivery, cost or exposure is unknown.
- Late evidence changes current knowledge while preserving the earlier cutoff view.
- The declared analysis rule admits or excludes late capture for its own evidenced
  timing criterion; no implicit change to the scientific population or labels.
- Closure does not fabricate cancellation enforcement or release/reset liabilities.
- Follow-up collection retains the native attempt where appropriate and uses a new
  observation boundary; checkpoint restart still creates a successor attempt.

These are hypothetical design examples, not executed S3 acceptance tests. The
required staged-tree package gate validates this documentation milestone's package
compatibility and publication boundary; it does not establish these new semantics.
Historical S1/S2 and qualified data-backed receipts retain their original scope.

## Where we're going

Review the six minimum blocks, evidence transitions and closure/follow-up rules
together. Once these meanings are accepted, detail admission, authority, resource
and exposure ownership so the coordinator's permitted actions agree with the
knowledge it actually has. Later reconcile the full S3 examples before exact
serialization, APIs, support profiles, final review or implementation bundles.
