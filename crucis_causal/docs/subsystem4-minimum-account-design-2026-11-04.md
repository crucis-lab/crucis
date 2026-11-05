# Subsystem 4: minimum account, conditional records and worked dependencies

Tickets: DLV-08, DLV-09; related DLV-10.
Date: 2026-11-04, America/Los_Angeles.
Status: semantic design proposal for review. No S4 implementation, registered
record kinds, wire/schema freeze, scientific procedure adoption, native campaign,
paper change or public protocol adoption is authorized by this document.

## 1. Continuation and example status

Uzair endorsed the [six-profile proposal](subsystem4-support-profiles-design-2026-11-04.md)
as the basis for defining the minimum S4 account and conditional records, using
complete examples to check dependencies and expose gaps. This is conceptual
continuation, not acceptance of every new record role, cardinality or resolution
below. The [capability map](subsystem4-measurement-capability-map-2026-11-04.md)
and [opening structure](subsystem4-structure-design-2026-11-04.md) remain in scope.

All examples below are filled-in semantic design examples. Their identifiers,
frontiers, observations, source values and hypothetical work are fictional design
inputs, not actual native history. They are complete for the information-role and
dependency questions stated here; they are not serialized/runtime-valid packages.
Exact byte encodings, package pins, qualified readers/evaluators and actual
qualification receipts remain unbuilt. Qualification specifications are marked
unexecuted. Expected future profile outcomes assume those qualification gates are
met; no example establishes a real S4 profile today. Numerical definitions serve
as design probes, not a selected shipped metric or inferential method.

## 2. Minimum account: identity plus an honest supplied-source account

An account is a logical identity with immutable published snapshots. A snapshot
contains its declared records/dependencies at a fixed basis; it is not the latest
mutable state of an experiment. Use existing immutable evidence/publication and
source primitives rather than introduce another execution journal or artifact store.

The semantic minimum is an account anchor and at least one supplied intent,
evidence, observation or gap entry. The encoding may inline or reference that entry;
this is not a frozen two-record wire format. A supported, explicitly scoped empty
observation can be an entry. An empty inventory alone does not prove a native empty
answer. A formal question, calculation, numerical value, reference truth, native
attempt or guarantee assessment is not mandatory for minimum preservation.

| Minimum obligation | Information retained | Important boundary |
|---|---|---|
| MIN01 Identity/version | Account identity, snapshot identity, recognized envelope/version and relation to earlier publications | Logical account, record, package and byte identities are distinct |
| MIN02 Observer/provenance | Identified current author/observer, source basis and relevant writer/procedure identity where applicable | Unknown original producer, execution or history remains unknown |
| MIN03 Intent/subjects | Supplied purpose/subjects or explicit unresolved meaning; preserved raw intent if no supported question reader exists | No invented formal measurement question or native request |
| MIN04 Source inventory | Actual supplied contents/references/selectors, source-reported versus checked integrity, availability, extent and gaps | Missing bytes are not captured; complete local inventory is not complete native/scientific scope |
| MIN05 Evidence frontier | Exact source snapshots/positions available for this account; unknown source chronology retained | Authoring/import time is not native event time, experimental cutoff or preregistration |
| MIN06 Access/dependencies | Explicit supplied dependencies, actual access limitations and publication audience | No hidden locator fetch, authority from metadata, or unauthorized truth disclosure |
| MIN07 Goals/history | Requested guarantees where known; linked observations, assessments, corrections and gaps with their own scope | No default success or self-issued whole-snapshot integrity certificate |

A foreign unsupported document may be preserved as opaque source content under a
recognized envelope. This does not validate that document's own unknown schema.
An actual P0 guarantee still needs an assessment against its criteria; writing an
account does not automatically create that assessment or prove its own byte integrity.

Frontiers can be vectors of source positions and frozen packages. Do not force
incomparable clocks into one purported global instant. Represent source availability
at its observation time; later loss of a file does not rewrite earlier capture history.

## 3. Conditional information roles

These are semantic roles, not registered payload names, modules, or one file per
role. References to sufficient S1/S2/S3 records may fulfill a role without copying
their facts into S4. Distinct identities and scope remain necessary even if encoding
co-locates some roles. No generic object blob gains scientific meaning by its label.

| Role | Required when | Information that must be established or explicitly unresolved |
|---|---|---|
| ACCT Account/snapshot | Every account | The seven minimum obligations, bounded record inventory and source context |
| SRC Source/intent/gap entry | At least one in every account | Exact supplied basis, role, content/reference, availability/extent, origin and limitations |
| Q Question definition | Formal scientific meaning is interpreted or requested | Quantity/predicate, target scope/units, conventions, reference role/selection and declared input slots; population/inferential target where applicable |
| REQ Measurement request/goals | A formal request or guarantee goal is recorded | Question references, bound targets/output roles, requested profiles, source intent and relevant policy; separate from native S1 requests and S3 commands |
| BIND Evidence binding | Question inputs or interpretations are selected | Exact selected sources/outputs/reference versions, mappings/derived views, coverage masks, source frontier and selection basis; no unresolved latest alias |
| PROC Procedure description | An interpretation or computation relies on a named procedure | Mathematical/semantic definition, version/configuration, input/output roles and numerical conventions; actual implementation/transitive dependencies when computation is claimed |
| QUAL Qualification evidence | An implemented/support guarantee is asserted | Actual receipt kind, subject procedure/implementation, tested combination/environment, outcomes and limits; a planned specification is not an executed receipt |
| PREM Requirements/premises/assessments | Applicability or a stronger claim depends on a condition | Named versioned condition, subject scope, evidence for/against, factual versus stipulated/assumed role, judgment basis and unresolved conflicts |
| CALC Calculation occurrence/evidence | Invocation, computational work or a computational attempt is actually evidenced | Exact procedure/configuration and inputs, observed execution/outcome facts, output extent/gaps and relevant S3 operation links; no run inferred from intent alone |
| VAL Result/contribution/disposition | A result, component, externally reported quantity or non-value disposition exists | Primary question binding, output role, scientific subject/unit, source occurrence or reported basis, typed value/object, numerical domain, contributions/denominators, coverage and limitations as needed |
| POP Population/contrast account | A frame, estimator, aggregate or contrast is claimed | Intended units, selections, matching/weights/grouping/deviations, all dispositions and explicit per-unit or joint-input/result associations; no surviving-file denominator |
| INF Inference account | Inferential intent/applicability or an inferential result is described | Exact target/procedure/results, model/design/premise basis, uncertainty components and actual limits; distinguish requested, assessed and performed work |
| REPRO Reproduction account | A reproduction request, attempt or agreement claim is described | Original frozen calculation/results and basis, comparison rule, actual source access, recomputation occurrence if it exists and comparison evidence/limits |
| GUAR Scoped profile assessment | A profile guarantee is assessed or asserted | Criterion/version, exact target binding/result/subjects, frontier, audience, actual qualification and premise evidence; requested, assessed and established are distinct |
| REL Relationship/update | A derivation, correction, continuation, supersession or projection is asserted | Exact related identities, relation meaning, evidence and scope; no overwrite or implied semantic equivalence from equal bytes |

PROC's mathematical definition and its implementation identity are different.
Readers can interpret a named quantity while its numerical implementation remains
unavailable. REQ may reference sufficient S2 intent instead of inventing a duplicate
experiment. QUAL and GUAR are different: tested capability for a combination does
not establish applicability on this particular binding.

Each result item has an explicit primary question binding and output role. A joint
vector or structured collection retains its axes/member/parameter associations;
it need not be flattened into independent scalar rows. One computation may emit
several values, but a guarantee on one role does not cover every output of that call.
An imported value can have a source-reported basis without a local CALC occurrence.

Retrieving another observation of an established calculation does not create new
computational work. A new actual computation has a new occurrence, with explicit
relations to an earlier one where appropriate. An uncertain launch stays uncertain;
use S3 reconciliation evidence rather than infer safe resubmission from a request
hash. Neither a new calculation nor its reproduction creates an independent native
scientific trial by default. Exact interaction/recovery contracts remain to review.

## 4. Profile dependencies and absence

| Profile | Required information for the claimed scope | Conditional / absent cases |
|---|---|---|
| P0 | ACCT/SRC plus actual criterion and observation evidence if a GUAR claim is made | No formal Q, CALC or VAL is required; preserve unsupported raw intent and unknown original history |
| P1 | Q, sufficient REQ intent, BIND, exact semantic readers and scoped PREM account, with qualification/assessment evidence for claims | Unresolved calculation prerequisites may remain visible; unknown critical meaning withholds the affected interpretation |
| P2 | P1 meanings, PROC/actual QUAL, applicable PREM, actual CALC evidence and scoped VAL/results or diagnostics | A held request needs no invented CALC; a failed/unfinished attempt may have no numerical result; undefined requested numbers stay withheld |
| P3 | P2 computation plus POP with all intended units/dispositions and actual functional/input associations | Joint estimators need no fabricated scalar decomposition; explicit observed-set targets do not imply an original unknown frame |
| P4 | P2 computation, INF, model/design/premise and qualification evidence, exact result targets | POP when the method's population/contrast reasoning requires it; no automatic inference from an interval-shaped VAL |
| P5 | Original frozen CALC/VAL/basis, REPRO, actual source access, new computation/comparison evidence and fixed rule | Preflight can record missing inputs without claiming a recomputation; no implicit native rerun or wider scientific validation |

Distinguish information axes rather than one flat success enum:

- Knowledge: established content, unresolved facts, scoped non-applicability.
- Inventory/capture: known empty, complete for a stated scope, partial or unresolved.
- Applicability: evidence supports, challenges or leaves a named requirement open.
- Work: requested, attempted, completed or unresolved as actually observed.
- Mathematical result: defined value, permitted nonfinite value, set/bound, or a
  supported non-value disposition such as an undefined ratio.
- Guarantee: requested/not requested, not assessed, established or withheld for
  named targets and reasons, with contradictions retained.

Exact forms and names remain open. A completed evaluation can return counts and an
undefined requested ratio. Preserve both, withhold the numeric ratio guarantee, and
do not call that a native execution failure. A meaningful partial result does not
establish a completed native run. Missing, unsupported, undefined, denied and not
requested do not become interchangeable nulls, zeroes or empty collections.

## 5. Publication and dependency invariants

Scientific lineage and guarantee premises cannot use their own conclusion as proof.
Ordinary associations are not automatically proof dependencies or causal edges;
do not prohibit every bidirectional association merely because proof must not be
self-justifying. Exact bounded reference grammars will be reviewed separately.

A whole-snapshot verification with a known full-content digest must target an
already frozen snapshot from another receipt/publication. It cannot include the
known digest of its own containing bytes. Per-record scientific assessments may
be co-packaged with their subjects if they do not rely on their own verdict or the
final containing-snapshot digest. This preserves the existing
[S3 circular-publication boundary](../execution/codec.py) rather than recreating
the N13 self-digest bug. An ID is not its full-content hash.

Use S3 publication/audience closure for actual releases. A public projection of a
restricted calculation must identify its narrower attested/available basis; it
cannot silently remove required inputs and retain a full public-reproduction claim.
Restrictions cover metadata as well as raw contents. Profile claims name their
audience and exact target, not just an account-wide badge.

## 6. Complete semantic examples

Shared conventions: all source contents and work below are stipulated design
content with observer `design.author`; T0/T1 are fictional source frontiers, not
UTC or native chronology. Snapshot labels are symbolic frozen views for this design
pass, not real package pins. Each example's source inventory is complete for the
listed design inputs, not a claim about native history. Public audience applies
unless stated otherwise. For every required QUAL, only an unexecuted qualification
specification is supplied as SRC; the actual qualification receipt is absent.
It is not an actual profile-satisfaction receipt. The tables account for all fifteen
roles, grouping related roles for readability. Future exact fixtures must supply
actual encodings/pins and real qualification before runtime guarantees are claimed.

### E01 Opaque historical report: the actual minimum

| Roles | Filled-in account |
|---|---|
| ACCT/SRC | Account A0, snapshot S0, purpose preserve received report R0. Supplied report text is `score=0.91`; its metric, units, original producer, native time and original input files are unresolved. SRC-report preserves this exact supplied text; SRC-gap records unavailable original artifacts. Frontier is current receipt of the report only. |
| Q/REQ/BIND | No supported formal Q or calculation request. Raw reported score intent is SRC content. No BIND invents a reference, domain or trial. |
| PROC/QUAL/PREM | Preservation reader/writer is the future named procedure; qualification remains unexecuted. Premise account records that reported label/number do not establish metric meaning or truth. |
| CALC/VAL | No local CALC. The string is a source report, not an auditor-computed VAL or validated probability. A later qualified reader could create a separately identified interpreted quantity. |
| POP/INF/REPRO | Absent: no population, inference or reproduction was requested/performed; original history is not reconstructed. |
| GUAR/REL | Prospective P0 at supplied-content scope only. P1 scientific-score meaning and P2-P5 are unestablished/not requested, as applicable. Any whole-snapshot integrity assessment must be a later receipt targeting frozen S0. |

### E02 Partial graph reference: one source, two explicitly requested questions

| Roles | Filled-in account |
|---|---|
| ACCT/SRC | A1/S0 at T0. Domain A/B/C and unordered adjacency pairs AB/BC/AC. Native output O1 has established closed-scope semantics: assert AB, deny BC, assert AC. Reference R0 supports AB=true, BC=false, AC=undetermined. These literal objects are the complete supplied design sources. |
| Q/REQ/BIND | Q-covered asks fraction correct among definite native decisions with determinate uncontested reference labels; Q-full asks full-domain adjacency accuracy. REQ1 explicitly requests P1/P2 for both, not an automatic fallback. BIND1 pins O1/R0, identity mapping, requested/native scope {AB,BC,AC}, judged scope {AB,BC}. |
| PROC/QUAL/PREM | Toy covered-agreement definition: numerator correct eligible judgments, denominator eligible judgments, positive denominator required. Full quantity uses correct judgments over all three pairs, denominator 3, requiring all three reference labels. QUAL specifications are unexecuted. PREM records closed output/mapping established within the fiction, full reference coverage unresolved. |
| CALC/VAL | Expected covered CALC1 has contributions AB=(1,1), BC=(1,1), AC=unjudged with its native assertion retained; VAL-covered=(2,2,1). Reference coverage is 2/3, not the same denominator. No full-accuracy CALC is invented for the blocked request; its PREM/GUAR account retains the missing AC label. |
| POP/INF/REPRO | Absent: no cross-case estimator, inference or recomputation is requested. The per-pair count is not an iid population claim. |
| GUAR/REL | Future P1/P2 eligibility for the covered value is separate from withheld full-domain accuracy. Actual S4 qualification is absent today. Relationships retain both requested quantities and do not relabel covered agreement as full recovery. |

### E03 Two matched cases: unknown capture, observed failure and a bound

| Roles | Filled-in account |
|---|---|
| ACCT/SRC | A2/S0 at T0, two cases K1/K2 and conditions A/B, four distinct planned slots. Fixture source quantities for valid answers lie in [0,1]: K1/A=4/5, K1/B=1/2. K2/A has a capture gap with native outcome unknown. K2/B has an observed native failure and no answer. Values are stipulated toy inputs, not measured native quality. |
| Q/REQ/BIND | REQ2 requests P3 for three distinct quantities: full two-case mean quality contrast; explicitly available-complete-pair descriptive contrast; and a full-frame delivery utility bound. Utility is defined in this question as the supplied quality for a valid answer, 0 for observed native failure, and unresolved within [0,1] for unknown capture. BIND2 retains every slot and its source/disposition. |
| PROC/QUAL/PREM | Case difference is A-B; equal case weights are 1/2. Bound definition propagates the unresolved utility range without selecting a missing value. PREM distinguishes undefined answer quality for observed failure from unknown capture. These definitions and qualifications are design specifications only. |
| CALC/VAL | Expected available-pair CALC gives 3/10 on K1 only, with matched coverage 1/2. Full ordinary-quality point contrast is withheld. Utility difference for K1 is 3/10; K2 is u-0 with u in [0,1]. The full utility mean is (3/10+u)/2, so VAL-bound=[3/20,13/20], inclusive, under the explicit utility definition. It is a possibility bound, not a confidence interval. |
| POP/INF/REPRO | POP2 lists K1/K2 and all four slots, pairing, weights and dispositions, and links each target to its actual joint inputs/contributions. It does not drop K2 or call one matched pair the full frame. INF/REPRO absent: not requested; no sampling confidence level is invented. |
| GUAR/REL | Prospective P2/P3 eligibility is target-specific for the available-pair value and full-frame utility bound. Full-quality point contrast remains withheld. Qualification remains unexecuted; no inference or native attribution follows. |

### E04 Local answers, undefined accuracy and ordering alternatives

| Roles | Filled-in account |
|---|---|
| ACCT/SRC | A3/S0 at T0. Local task: parents of Z among A/B/C. Reference: A=true, B=false, C=undetermined. Output L1: A assert, B explicit abstain, C deny. Separately supplied L2 is explicit whole-query abstention, not capture loss. Order task: complete permutation of A/B/C satisfying exactly A<C and B<C. Outputs O-order=BAC and O-partial={A<C}. |
| Q/REQ/BIND | Explicit questions request P2 for local conditional judged accuracy, definite-answer coverage, order admissibility, known-constraint compatibility and complete-sequence fulfillment. Bindings select L1/L2 or each order object independently; the answer variants do not share one ambiguous selected-output field. |
| PROC/QUAL/PREM | Local ratio uses definite, reference-determinate decisions and requires positive denominator. Order reference is a complete admissibility definition for this task. These are toy definitions; QUAL remains unexecuted. Native response completion/allowed abstention is separate from the requested measurements. |
| CALC/VAL | L1 yields one correct judgment out of one, definite-answer coverage 2/3 and reference-covered definite-answer coverage 1/2. L2 yields numerator=0, denominator=0 and an explicit undefined conditional-accuracy disposition, while coverage 0/3 is defined. A completed evaluation may report those diagnostics without a numerical accuracy. BAC is admissible; ABC would also be admissible. O-partial is compatible with known constraints but fails the complete-sequence deliverable; complete-sequence quality is not fabricated from that partial object. |
| POP/INF/REPRO | No cross-query POP, INF or REPRO is requested. Candidate counts are not independent experimental repetitions. |
| GUAR/REL | Future scoped P2 claims distinguish defined counts/coverage/admissibility from the withheld numerical accuracy for L2 and the inappropriate complete-order quality for O-partial. A shared CALC may emit multiple roles, but each VAL and GUAR names its own question/binding. No real qualification is established here. |

### E05 Probability score and model-conditional inference in one account

| Roles | Filled-in account |
|---|---|
| ACCT/SRC | A4/S0 at T0. A native forecast states p(E)=4/5 for a specified binary event E; an applicable toy benchmark label is y=1. Separately supplied finite model M has alternatives H1=E and H0=not E, prior masses 1/2 each and likelihoods P(D\|H1)=4/5, P(D\|H0)=1/5 for observed event D. The model is stipulated; no claim that the native forecaster used it or that it describes the world. |
| Q/REQ/BIND | Q-score asks the declared squared probability error for this forecast/label, requesting P2. Q-post asks P(H1\|D,M), requesting P4. Q-cal requests P3 population calibration. Separate bindings choose forecast/label, or M/D, respectively. Calibration lacks a supplied evaluation frame and wider outcomes. Equal event names do not merge those bindings. |
| PROC/QUAL/PREM | Toy score definition (p-y)^2 and exact finite Bayes rule are explicit mathematical probes. Model priors/likelihoods and positive normalizer are stipulated inputs, not empirically verified world facts. QUAL specifications remain unexecuted. No calibration or sampling-interval procedure is selected. |
| CALC/VAL | Expected CALC-score returns VAL-score=1/25. Expected CALC-post uses numerator 2/5 and normalizer 1/2, returning VAL-post=4/5. These equal/native-related numbers have distinct quantity and provenance roles. No CALC-calibration is invented. |
| POP/INF/REPRO | POP for calibration is unresolved and the requested population quantity is withheld. INF-post targets only VAL-post conditional on M/D and its prior/likelihood law, with exact finite arithmetic and no approximation. Its alternatives are hypotheses, not independent trials; no multi-case POP is needed for this conditional query. REPRO is not requested. |
| GUAR/REL | Future P2 eligibility for the score is separate from P4 eligibility for the model-conditional posterior, subject to actual qualification. No P4 claim covers the score or the original native forecast; no calibration, real-world model validity or native reasoning faithfulness is established. All actual S4 guarantees remain unqualified in this design pass. |

Per-event scores and population calibration answer different questions; see
[Gneiting and Raftery (2007)](https://sites.stat.washington.edu/raftery/Research/PDF/Gneiting2007jasa.pdf).
Conditional model inference does not establish the model's empirical truth; see
[Pearl (2009)](https://web.cs.ucla.edu/~kaoru/SS-2009-57-Sup.pdf). These sources support
scientific distinctions, not our record-role taxonomy or adoption of these toy methods.

### E06 Conflicting evidence, new cutoffs, restricted results and reproduction

| Roles | Filled-in account |
|---|---|
| ACCT/SRC | Continue A1 with immutable S0 from E02. Snapshot SC at T1 adds an applicable source contradicting AB=true by asserting AB=false; both assertions are preserved. Snapshot S2 at T2 adds an identified adjudication/correction account under a declared source-selection policy supplying R2: AB=true, BC=false, AC=false, complete for this three-pair benchmark. R2 is restricted; the example policy permits public aggregate values/attestation but not raw labels or restricted metadata. No actual private data exists in this fictional example. |
| Q/REQ/BIND | The declared rule in Q-covered can be reused with a new binding if reference values are input slots; a definition that hard-codes the old reference instead needs a revised Q. BIND-conflict preserves the T1 dispute and does not silently select the newest or best-scoring source. BIND2 selects R2 under the evidenced correction policy at T2. Native O1 is unchanged. New REQ3 requests P2 for both new question bindings; original REQ1 is unchanged. Separate P5 requests name old CALC1/S0 or new CALC2/R2. |
| PROC/QUAL/PREM | PREM-conflict withholds a definite AB judgment while the dispute is unresolved. The correction assessment identifies its rule, source basis and limits; it is not truth from timestamp order. Qualifications remain unexecuted specifications. Reproduction requires actual original bytes, implementation/configuration and a fixed comparison rule; known digest strings alone are insufficient. |
| CALC/VAL | Expected composite CALC2 against R2 gives two correct judgments out of three. It emits VAL2-covered=2/3 for Q-covered's new binding and VAL2-full=2/3 for Q-full's new binding, with an explicit output-role map and qualification requirement for each. Equality of values does not merge the questions. A difference from the old covered value 1 reflects a changed evaluation basis; it does not establish native performance deterioration. A later prospective recomputation against the original R0 would still yield 1. No overwritten old VAL or original CALC is created. |
| POP/INF/REPRO | No population/inference requested. REPRO-old targets frozen CALC1/VAL-covered/R0 and, if all original inputs are available, links a new actual recomputation plus its agreement comparison. If a later availability observation finds original bytes missing and a locator now returns different bytes, P5 is withheld for the old basis; new bytes require a new binding. No actual CALC/comparison is claimed merely from a reproduction request. |
| GUAR/REL | Scoped expected claims distinguish old and current reference judgments, correction provenance and audiences. Restricted P2 can be qualified later for CALC2's audience; the public projection is an identified aggregate/attestation with a withheld raw basis, not full public verification or P5. Whole-snapshot integrity GUAR must target an earlier frozen publication from a later receipt. Ordinary scientific records can be co-packaged without a known full digest of their own containing bytes. Actual S4 qualifications remain absent. |

At T1 any numerical result on remaining uncontested claims must follow a separately
explicit eligible-scope rule and retain the conflict/coverage. It cannot silently
replace the originally requested full-domain result. At T2 the source correction
resolves the selected reference basis only under its stated authority/assumptions;
retaining that assessment is not erasing the conflicting source or proving universal
truth. Later loss of R0 affects current reproduction availability, not a rewrite
of what S0 captured or claimed at its old frontier.

## 7. Gaps exposed and proposed resolutions

| Gap | Proposed resolution / requirement |
|---|---|
| G01 A score-shaped foreign report can look like a completed measurement | Minimum ACCT/SRC preserves it without inventing Q, CALC, native attempts or scientific meaning |
| G02 A requested guarantee can look like performed work | REQ goals, actual CALC observations and GUAR conclusions are distinct; absent work is accounted for without a fake run |
| G03 One timestamp can conflate authoring, selection and native history | Explicit source frontier plus authoring/original-time provenance; no invented global clock or retrospective preregistration |
| G04 Completed evaluation can have no defined requested scalar | VAL retains count diagnostics and mathematical disposition; numerical guarantee withheld without converting to zero or native failure |
| G05 One computation's successful role can upgrade unrelated outputs | Each VAL has a primary binding/role; INF/GUAR target exact results and premises, not an account-wide success flag |
| G06 Missing cases and failures can disappear into a denominator or interval | POP retains all intended units/dispositions; utility loss explicit; possibility bounds and sampling intervals keep different meanings |
| G07 Inference can be forced through unnecessary population machinery | INF carries method-specific conditional model/design evidence; POP is required only where the inferential target needs it |
| G08 Fully filled examples can look like actual qualified support | QUAL specifications stay unexecuted; semantic example outcomes are prospective; no real scientific profile pass from document completeness |
| G09 Later conflicting evidence can silently overwrite earlier labels | New PREM/BIND/REL accounts preserve both sources, cutoffs, correction rule and qualification limits |
| G10 A changed reference/mask can look like native improvement or decline | Evaluation-basis identity stays explicit; descriptive value difference is not automatically a native-performance contrast |
| G11 An integrity assessment can require its own impossible full-content hash | Whole-snapshot verification targets a frozen predecessor; proof dependencies cannot self-justify; ordinary associations are not all proof edges |
| G12 Restricted or changed/missing inputs can acquire a public reproduction badge | Audience-specific projection and availability observations; old-basis REPRO requires actual original inputs, not an alias, digest or attestation |

These are proposed resolutions within the bounded examples, not proof that every
future incompatibility is closed. They do not choose a general scoring, imputation,
calibration, inference, reference-adjudication or stochastic-reproduction method.

## 8. Reuse, alternatives and remaining design

| Choice | Proposed direction | Strongest alternative | Cost / failure prevented |
|---|---|---|---|
| Minimum account | Small source/provenance anchor with conditional scientific records | Mandatory metric/result/native-run record for every import | More explicit unavailable-role handling; avoids fabricated history and excludes fewer native objects |
| Typed roles | Shared reusable identities/bindings with targeted results and assessments | One large mutable measurement row or unrelated per-profile documents | More reference/dependency checks; prevents drift and accidental guarantee promotion |
| Work/result separation | Record actual calculation evidence and values/dispositions independently | One success flag requiring a scalar | More scoped status accounting; preserves undefined/partial results and diagnostic evidence |
| Population/inference | Explicit joint or per-unit association and method-specific premises | Always mean rows and bootstrap them | More scientific contracts; prevents wrong units, hidden exclusions and unsupported uncertainty |
| Publication/reproduction | Reuse immutable S3 publication and audience mechanisms | Rewrite records to latest data or build another runner/store | More pinned relations; preserves earlier cutoffs, authority boundaries and actual verification scope |

Reuse [S1 implemented support](subsystem1-implemented-support-2026-11-01.md) and
[S1 source/output primitives](../connections/model.py),
[S2 evaluation bindings](../experiments/evaluation.py) and
[S2 model primitives](../experiments/model.py), and
[S3 implemented scope](subsystem3-implemented-scope-2026-11-04.md),
[S3 model primitives](../execution/model.py) and its publication/closure contracts.
S2's installed measurement descriptor is metadata-only. No foundation or profile
label supplies a new S4 scientific evaluator or native-system qualification.

Still to settle: exact field/type/cardinality forms; question-template and bound-
instance rules; evidence/knowledge/disposition grammars; numerical/structured
result families; premise/adjudication contracts; exact mathematical procedure
inventory; source/qualification and transitive implementation pins; bounded
serialization and dependency validation; interfaces and interruption/recovery;
legacy compatibility; scoped validation gates and final build DAG.

This milestone changes only design documentation. It creates no S4 runtime, schemas,
product tests, native executions, new paper quantities, threshold/tolerance changes,
stored-result/certificate edits, research-helper changes, tracker updates or site
publication. Document/link/arithmetic checks and existing package gates are scoped
compatibility/design-consistency evidence, not S4 scientific qualification.

## Where we're going

Review the minimum and conditional roles with these examples and their proposed
gap resolutions. Then specify the precise semantic/result families and premise
contracts, close the concrete procedure inventory and qualification obligations,
and use exact examples to review serialization, references and profile dependencies.
Only after interfaces, recovery, legacy mapping and final review should the build
DAG be frozen. Implementation still requires an explicit user go.
