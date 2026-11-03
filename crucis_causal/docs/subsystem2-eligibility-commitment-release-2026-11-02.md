# Subsystem 2: eligibility, plan commitment and controlled release

Tickets: DLV-08, DLV-09; related DLV-10, DLV-06/07 and ADV-01.
Date: 2 Nov 2026, America/Los_Angeles.
Status: proposed design. Uzair authorized continuing the S2 discussion from
comparisons/repetitions/missingness, with no implementation. Detailed contracts,
authority/release semantics and policies here remain proposals for joint review.
No public protocol, sealed-read allowance or execution authorization is changed.

Sources: [comparison/population design](subsystem2-comparisons-repetitions-missingness-2026-11-02.md),
[conditions/information](subsystem2-conditions-information-design-2026-11-02.md),
[transformations/randomization](subsystem2-transformations-randomization-design-2026-11-02.md),
[S2 structure](subsystem2-structure-design-2026-11-01.md),
`audit/core/{battery,sealed}.py`, `audit/__main__.py`,
`audit/connections/{schema,history}.py`, `tests/test_audit_report.py`,
and the [program excerpts](project/program-v3-excerpts.md), sections 2.2 and 4.
Only source code and documentation were read. No real sealed store, seeds or read
ledger was accessed; no helper, native evaluation or API call was executed.

## 1. Eligibility, readiness and authority answer different questions

| Assessment | Question | Example boundary |
|---|---|---|
| Scientific applicability/eligibility | Does this case/task/condition/comparison satisfy the declared scientific scope and assumptions? | A requested row-subsample control may be inapplicable to a names-only method or require a different sampling contract for temporal evidence |
| Operational/semantic readiness | Are the needed bindings, implementations, evidence and resources established at the relevant boundary? | A scientifically suitable interventional task may lack a working native adapter route; a supported run may later lack an aligned reference for a metric |
| Execution/disclosure authority | Does applicable authorization permit this operation, subject, recipient, information and resource scope now? | A ready paid run or restricted disclosure still requires an applicable execution/release grant |

Readiness is scoped and time/environment dependent, with procedure/version, inputs,
evidence and outstanding gaps. It is not a permanent property of a system name.
Eligibility requires its rule, basis and timing. Unknown assumptions do not become
established because an artifact parses. Operational gaps are not native failures.
Poor output quality does not retroactively make the selected case ineligible.

Assessment boundaries include planning, materialization, native invocation, output
interpretation, reference comparison and reporting. An invocation need not already
possess future interactive responses or returned latent alignments; it needs the
permitted policy and prerequisites for that invocation. Later metric readiness
checks the evidence actually required for that metric. A cost/completion study can
be meaningful without claiming reference-supported graph accuracy.

Established session authorization remains applicable within its actual scope; this
proposal does not require repetitive confirmation prompts for already authorized
steps. Missing scope cannot be inferred from a valid schema, passed test, budget
estimate or funding award. In this chat the current scope is design/documentation;
neither implementation nor paid/native/sealed execution is authorized.

## 2. Proposed lifecycle obligations

| ID | Responsibility | Failure prevented |
|---|---|---|
| L01 | Plan/release identity, exact content/version, authoring provenance and related earlier definitions | A mutable latest configuration masquerading as the original plan |
| L02 | Scoped eligibility/readiness rules, assessment procedure, evidence, boundary/time and gaps | Treating missing tooling, scientific mismatch and later poor outcomes as one exclusion reason |
| L03 | Binding schedule: which fields are fixed when, and which are generated/resolved later by a bounded rule | Inventing before-the-fact membership or rejecting valid adaptive/live designs |
| L04 | Exact reference closure for case/collection/task/condition/transform/comparison/subject contracts | Changed source data, model defaults or scoring rules hidden behind an unchanged plan label |
| L05 | Commitment event and chronology evidence, prior-exposure scope and assurance limits | Claiming preregistration or blindness from a checksum or file timestamp alone |
| L06 | Applicable actors/authority scopes for specification, amendment, execution and disclosure | Treating reviewer comments, ready status or resources as permission to act |
| L07 | Controlled information/material release, recipient/purpose scope, exposure evidence and limits | Equating a sealed label, hidden filename or outside-folder store with proven isolation |
| L08 | Amendments: old/new bindings, reason, timing, already observed information and affected analyses | Erasing outcome-informed changes or mislabeling an unchanged analysis as affected |
| L09 | Adaptive policy identity, allowed inputs/actions, decision procedure and stopping/resource bounds, with actual decision evidence | Unbounded branching or favorable stopping concealed as an advance plan |
| L10 | Actual materialization/admission/disclosure/execution receipts and partial-failure/recovery accounting | A permitted or attempted step presented as completed, or a failed exposure erased |
| L11 | Scientific claim labels and public/private evidence projections under adopted contracts | Global confirmatory labels concealing retrospective components or leaking restricted evidence |
| L12 | Staleness, nonconformance, revocation/supersession and population/report impact | Continuing to rely on an obsolete readiness result or silently replacing the intended cohort |

These are proposed logical responsibilities, not twelve new mandatory records or
a serialized state machine. Existing S1 contracts should supply actor, policy,
evidence, request/attempt and observation meaning. S3 will implement operational
enforcement; S4/S5/S6 preserve measurement, finding and reporting ownership.

## 3. Plan snapshots and binding times

A working draft can be edited. Once a particular snapshot is cited as the plan
for an experiment or commitment, retain its exact identity/content and its
dependencies. A later change has a related new snapshot and explicit history.
Content identity, event/occurrence identity, locators and scientific equivalence
remain separate as in S1.

| Binding | Typical required timing and meaning |
|---|---|
| Scientific target, eligibility, contrast, primary metrics, analysis populations, missingness and stopping rules | Fixed before the relevant outcomes/adaptive decisions if prospective status is claimed; record prior exposure and retrospective portions |
| Selected static cases and revisions | Frozen release before the corresponding selection/execution claims; a generated/adaptive population can instead bind a selection rule and later realized member receipts |
| Transform/native subject/configuration and inference/resource policies | Exact definitions and permitted resolution rules fixed before their materialization/invocation; actual versions/defaults/content checked at the specified boundary |
| Randomized assignments, row maps, source episodes and interactive responses | Later realizations under committed procedures; record actual values/snapshots, correlations and evidence, not fictitious advance knowledge |
| Reference definitions, coverage, alignment and output selection procedures | Fixed at the appropriate pre-outcome boundary for the claimed analysis; private references may be resolved only by the authorized evaluator |
| Actual assessment and analysis results | Derived from identified later evidence; a result timestamp never supplies a missing original plan timestamp |

An unresolved required prospective dependency blocks the affected readiness claim.
A deliberately later-bound value needs a specified resolution contract and authority,
not an unrestricted placeholder. Restricting future choices is compatible with
adaptation; claiming that their actual values were already enumerated is not.

Recheck relevant actual inputs/configurations when used. A cached manifest hash is
not continuous verification of mutable files. Native/provider drift, changed
preprocessing or unavailable references can require a new binding/assessment or
limit the comparison. Do not silently substitute another backend as the same frozen
subject, even if the API shape is unchanged.

## 4. What a commitment can establish

A content hash identifies the specified content. It does not by itself prove when
it existed, who approved it, what the analyst had seen or whether dependencies
remained fixed. Record the claimed event time, actual observer evidence, any
independent timing/authority evidence available and the assurance limits.

The plan should support a timing/assurance contract appropriate to the intended
claim. No new external registry/service or cryptographic timestamp system is
mandated or used here. A local declaration can be retained honestly without being
upgraded to independent chronology evidence. An externally evidenced commitment,
if later supplied, still needs the relevant content/dependency and exposure scope.

Prior public/development exposure does not automatically invalidate a prospectively
fixed analysis on fresh evidence. It does constrain claims of unseen-case evaluation
and independence from tuning. Describe separately: when the rule was fixed, what
was exposed to whom, what is newly sampled, and what target/claim is supported.
Do not equate all of these with one global confirmatory flag.

Existing paper/report confirmatory/exploratory fields and their owner-adopted rules
remain unchanged. Richer provenance can justify their scoped projection after
adoption; this note does not retroactively upgrade historical finding labels.

## 5. Amendments and corrections

Every material amendment identifies the original and revised snapshot, change,
reason, timing/basis, relevant information already observed, affected trials and
analyses, and consequences for authorization and scientific labels. Preserve the
old binding and actual executed evidence. Do not relabel a completed arm to make
its input policy compliant.

| Change | Treatment |
|---|---|
| Relocated identical artifact | New locator/availability evidence may suffice when immutable bindings remain satisfied; verify the promised identity |
| Editorial clarification | Retain its provenance; whether it changes scientific meaning needs a scoped basis, not the author's label alone |
| New model, prompt, native mode, reference procedure or metric rule | Assess and bind the substantive change; preserve versions and affected comparisons rather than hiding it as a routine fix |
| Reference-only correction | New reference/evaluation version with affected outputs/populations and honest timing; input case identity need not change |
| Reduction to a predeclared budget tier | Follow the actual tier/stopping/selection rule, retaining intended and unexecuted slots; no outcome-based case substitution |
| Unplanned outcome-informed scope change | New amendment and appropriate retrospective/exploratory limits; unaffected or not-yet-exposed components need their own justified status |

If an amendment occurs before the relevant new outcomes, its prospective scope can
be assessed from evidence. It does not erase earlier exposure or guarantee pristine
confirmation. A correction to software used for analysis must name which outputs
are recomputed and why; old results stay traceable. W1/W5 adoption and the paper
number contract control public updates, not this internal proposal.

## 6. Adaptive rules and actual decisions

An adaptive design commits the decision policy, eligible inputs, allowed alternatives,
selection/stop bounds, randomness, resource limits and analysis consequences. Its
actual branches are later evidence. Examples include a predetermined resource-tier
release, action selection in an interactive episode or a bounded sequential sample
rule with a valid declared analysis. Exact statistical procedures remain for their
own contract; a decision log alone cannot make optional stopping statistically sound.

A decision receipt identifies policy revision, decision point, information actually
available/used, resulting branch, actor/procedure, timing, resources and affected
trial/member identities. Future unavailable inputs are not reconstructed as known
at decision time. If the policy cannot handle a situation, report the gap or amend
it; do not improvise a favorable branch and call it predeclared.

Feedback and adaptive selection also affect exposure and dependence. Record every
feedback event under its permitted scope, including information from failed or
partial evaluations. An aggregate score can influence later design even if no
individual case graph was disclosed.

## 7. Authority, release and disclosure are separate events

Logical roles include plan author, scientific reviewer, data/evaluation custodian,
operator and report recipient. One person may hold several roles; record that
fact rather than inventing independent review or isolation. These are responsibility
boundaries, not a new requirement for staffing or repeated approval prompts.

Bind the relevant authorization source and its scope: actors/subjects, operation,
condition/version, recipient, data/actions/resources, validity and any constraints.
An existing valid grant can cover its intended steps. An operation outside that
scope needs applicable authorization; it cannot inherit it merely from the same
project or a passed test. Do not confuse an immutable collection release, a plan
commitment, execution admission and disclosure to a recipient.

Controlled disclosure records actual recipients, subject/material or authorized
restricted references, event/boundary, extent, policy/grant and evidence. Attempted
or permitted disclosure is not proof of actual delivery or access. Retain partial
delivery, errors, interruptions and state carried into retries. Whether an exposure
consumes a limited read must be defined before relying on that limit, including
crashes before a report is written. Do not infer that no report means no exposure.

Atomic admission/reservation and durable exposure accounting are future S3/owner
integration requirements where bounded reads or concurrent execution require them.
This proposal does not establish them merely by describing a ledger. Existing
read-consumption policy cannot be silently expanded or replaced here.

## 8. Development, held-out and sealed evidence

Separate declared collection role from evidence of access/exposure. Public development
data can legitimately support software tests and exploratory studies. A fixed
protocol can also be evaluated on fresh draws or newly collected evidence, with
the actual novelty and generalization scope stated. Renaming a reused case as
held-out or sealed does not reverse earlier exposure.

A controlled confirmation claim needs scoped evidence about relevant source/case,
reference, protocol and outcome exposure to the evaluated subject and developers/
analysts, as applicable. Native pretraining exposure can remain unknown. Physical
location, a visibility label or a digest is not proof of secrecy or independence.
An authorized private verifier may resolve evidence that is not disclosed publicly;
traceability does not require publishing protected material.

The adopted program separates A's development battery from B's sealed battery and
allows one declared B version read of that sealed battery. Its new finding kinds
are fixed before evaluation on B, and a finding closes only through the adopted
sealed-read workflow. Do not reinterpret these program rules as a new general
read allowance for every configuration or as an implementation already present.

The inspected helper's additional current cap is five logged reads per battery
hash across versions/systems, plus its one-(system,version,battery) check. The
eight-system starting panel therefore cannot be promised eight reads of one such
battery under that unchanged cap. This is an owner-level scope/policy issue, not
permission to split identities, relabel versions or reset accounting. Any authorized
rotation or policy change must preserve exposure and comparability limits; different
batteries are not automatically the same matched cohort.

Renaming a configuration cannot establish a scientifically new version or restore
blindness. A meaningful subject/version identity must bind relevant code, model,
prompts, native preprocessing and configuration, with actual drift/unknowns visible.
Changed auditor/reference/analysis definitions also retain their own identities.
Exact version-equivalence/read-eligibility rules need owner adoption before use.

For a limited-exposure protocol, keep full authorized private evidence and a defined
public projection. Rounding aggregates or suppressing case identifiers is not by
itself a proof that repeated feedback cannot inform tuning. Who sees what, when,
under what read/feedback limits remains part of the claimed isolation scope.

## 9. Concrete lifecycle walkthroughs

### A. Public prospective study

A draft describes cases, names conditions, repetitions, missingness and analysis.
The author snapshots it with exact dependencies before the relevant outcomes,
records known development exposure, and later materializes randomized inputs under
the specified rules. Readiness is assessed at each needed boundary. Authorized
execution then produces attempts, actual-input receipts and outputs. Analysis binds
that snapshot and actual populations. This can establish prospectively specified
parts to their evidenced scope; it does not assert that public cases were unseen.
No such plan is committed or executed by this illustrative walkthrough.

### B. Historical reconstruction

Recovered outputs and an old plan fragment get current preservation identities.
The fragment's original time/authority is recorded only to its available basis.
Missing chronology/exposure remains unresolved. A newly written comparison can
analyze supported outputs retrospectively, preserving its actual creation time.
A current hash does not turn the recovered study into preregistration.

### C. Predeclared adaptive budget

A hypothetical pilot policy specifies which cost summaries may be viewed and how
they select an eligible later tier, with bounds and analysis consequences. The
selected branch and available information are later recorded. If case difficulty
or preliminary effects drive an unplanned choice, record an amendment rather than
claiming the original cost-only policy selected it. Budget/funding approval and
the exact execution authorization remain distinct. No funding award beyond the
user-reported sent request has been reported in this chat.

### D. Failed or partially exposed confirmation

The prospective policy must identify eligibility, authorization and consumption
boundaries before disclosure. A crash after delivery retains its actual exposure
and recovery history, whether or not graph scoring completes. Another attempt
does not automatically regain unseen status or a fresh read allowance. If an
authorized run instead never reached disclosure, retain that evidence and apply
the adopted consumption rule. This note decides no real read eligibility and
opens no restricted store or ledger.

## 10. Current footing and its limits

- `audit/core/battery.py` hashes a manifest including files and caches that value;
  its mutable items list is not the proposed immutable plan/release lifecycle.
- `audit/core/sealed.py` defines an outside-shared-folder store guard, generator/
  commitment/check helpers, read eligibility/recording and aggregate filtering.
  Its eligibility function reads a ledger; recording rechecks and appends. These
  helper boundaries do not establish an atomically reserved production admission,
  pre-disclosure enforcement or complete partial-exposure accounting.
- The inspected CLI registers `sealed-check`, which queries eligibility; it does
  not register `sealed-read`. Do not present helper existence as a complete native
  sealed evaluation orchestration or operational access isolation.
- `tests/test_audit_report.py` contains controlled test-store/read-limit/generation
  tests. They were source-inspected here, not run, and provide no observation of
  a real sealed store. Prior engineering gates remain their own recorded evidence.
- S1 contains authority, action, continuation and scoped evidence structures; it
  does not choose the scientific plan, authorize new work or enforce all S3 policies.

Existing code/policies were inspected but not modified. No real seeds, stores or
ledger contents were accessed. No inference about the currently consumed read
budget, live access permissions or operational isolation is made.

## 11. Alternatives and future acceptance examples

| Proposed direction | Strong alternative | Cost and prevented failure |
|---|---|---|
| Scoped eligibility/readiness/authority assessments | One ready flag | More explicit evidence/bindings; prevents support, applicability and permission being conflated |
| Immutable cited snapshots with later bounded realizations | Editable live configuration or one fully enumerated static grid | More history/resolution rules; supports adaptive/live studies without hiding changes or inventing future observations |
| Chronology/exposure evidence alongside hashes | Treat a checksum as preregistration | More provenance and honest assurance limits; prevents retrospective confirmation claims |
| Versioned amendments and decision receipts | Update the plan in place | More bookkeeping; preserves outcome-informed changes and original populations |
| Scoped controlled release with private/public evidence projection | Publish everything or infer isolation from a sealed label | More access/authority integration; prevents disclosure and unsupported blindness claims |

| ID | Future acceptance example |
|---|---|
| E01 | A scientifically eligible case lacking an adapter route stays operationally unready without being labeled a native failure |
| E02 | A ready paid operation without matching execution authority does not start; existing applicable authority is reused within scope |
| E03 | A committed rule followed by later generated membership preserves binding times rather than inventing advance enumeration |
| E04 | A changed source/model invalidates affected stale bindings/readiness without rewriting prior receipts |
| E05 | A local current hash cannot supply missing original chronology or exposure evidence |
| E06 | An outcome-aware amendment preserves old/new rules, observed information, affected analyses and scoped labels |
| E07 | An adaptive branch identifies the bounded policy and actual available inputs; an unhandled branch remains a gap/amendment |
| E08 | Public/pilot exposure remains visible after a later held-out/sealed role assignment |
| E09 | A partial failed disclosure retains actual exposure and applies the adopted read-consumption policy |
| E10 | Version relabeling or an eight-member panel does not bypass the existing one-version/five-total helper limits |
| E11 | Reference correction or private/public projection retains source versions and owner-adopted paper/claim rules |
| E12 | Missing real operational evidence cannot be replaced by dummy-store tests or the existence of a sealed-check command |

These are proposed acceptance obligations, not passed tests or new measured coverage.
Open details include exact lifecycle/assessment records, binding schedules, chronology
assurance and authority adapters, adaptive policy families, release/consumption
semantics, historical mappings and bounded serializer/API contracts. Resolve them
with complete cross-linked examples and owner decisions before implementation.

## Where we're going

All seven S2 responsibilities now have a first design treatment, not a frozen
contract. Use the [design rebase](subsystem2-design-rebase-2026-11-02.md) to compose
complete prospective, historical and adaptive/controlled experiment definitions.
Check reference closure, timelines, readiness claims, population accounting and
cross-family coverage together. Resolve semantic and lifecycle gaps before the
bounded serialization/API/legacy pass, final S2 design review and implementation
bundle planning. No build or public adoption is authorized by this design work.
