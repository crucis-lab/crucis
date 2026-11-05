# S3 input realization and information staging

Tickets: DLV-08, DLV-09; related DLV-10.
Date: 2026-11-03, America/Los_Angeles.
Status: IS01-IS12 are recommendations pending discussion. No S3 implementation,
exact API/schema freeze, scientific protocol change, paid/native execution,
protected-store access or operational cleanup is performed by this design note.

## 1. Continuation and retained boundaries

The user affirmed [the admission lifecycle discussion](subsystem3-admission-lifecycle-design-2026-11-03.md),
committed as 55153dd835234b0ca42b837303a5bf48a1133254, and requested input realization
and information staging with transformations, access boundaries, partial staging,
uncertain disclosure and cleanup. Record AL01-AL12 as direction-affirmed with
exact contracts still open, not implementation approval. IS01-IS12 below are new
proposals. Earlier dated proposal language retains its historical meaning.

Retain S2's accepted transformation/information semantics and implementation scope:
[transformations](subsystem2-transformations-randomization-design-2026-11-02.md),
[information channels](subsystem2-conditions-information-design-2026-11-02.md),
[implemented scope](subsystem2-implemented-scope-2026-11-02.md). Those earlier design
documents retain their original paths and acceptance history. S3 executes admitted
procedures and captures actual evidence; it does not choose new transformation
meaning, sampling/recovery policy, reference truth, findings or analysis exclusions.
Examples below are hypothetical, not new empirical evidence or production defaults.
The [methodology index](subsystem3-methodology-index-2026-11-03.json) records scoped
implementation anchors, tests and explicit unsupported claims.

## 2. Preparation can precede the final native request (IS01)

S2 supplies plan/trial intent, source requirements, transform specifications,
information constraints and binding rules. Where materialization is required,
preparation operations link to those prospective identities before a finalized
S2 run binding/S1 request exists. Admission for generation, fitting, retrieval and
staging uses that exact scoped intent and actual owner authority. It cannot require
the yet-unavailable materialization receipt as proof that preparation already happened.

After realization and required checks, return evidence to S2's materialization,
resolution and binding procedures. Use its actual completeness/assessment results;
recording a receipt is not sufficient proof of readiness. Freeze the appropriate
S1 request/handoff with the actual input/presentation bindings before the native
effect requiring them. Do not create dummy ready bindings to break this dependency.
Exact timing/cardinalities remain open across request routes.

Some admitted staging can itself precede that final handoff. Its intended content,
recipient and effects must already be adequately bound under prospective authority;
a later run binding cannot retroactively authorize earlier disclosure. These are
dependency constraints, not a universal total order for every input route.

Distinguish fixed scientific inputs from authorized late-bound transport details.
A refreshed scoped locator can refer to the same established content under a
declared binding contract; it cannot silently substitute another dataset or recipient.
Changing realized scientific inputs after a frozen binding requires explicit new
versioned relationships and applicable S2 recovery/amendment rules, not mutation
of the old request. Dynamic interaction binds each admitted action/response at its
appropriate boundary; a fixed whole-episode artifact is not universally required.

## 3. Linked evidence, distinct claims (IS02)

Recommend these separable questions rather than a single staged=true field:

| Question | Evidence and limit |
|---|---|
| What source was selected? | Exact source revision/content/selector, or a scoped dynamic source/episode contract; a locator alone is insufficient |
| What was realized? | Actual admitted provider/transform invocation, inputs, parameters/state/randomness, output domains/material and failures |
| What was checked? | Named property/procedure, exact subjects/scope and actual pass/fail/unknown result; not universal scientific equivalence |
| What was prepared? | Exact native representation, members/selectors/encoding, dependencies and ownership, with partial extent |
| What became reachable? | Actual recipient/audience, permitted route, access scope and validity; no inference merely from a folder label |
| What was delivered/accessed/used? | Independently supported transfer/read/use evidence at the relevant boundary; each can remain unknown |
| What was retained or removed? | Evidence retention, locator/grant revocation, object deletion and remaining copies/obligations, scoped separately |

These are linked assessments/events, not a universal sequence of new wire states.
Use immutable captured snapshots and existing S1/S2 references where meanings match.
Ordinary local immutable inputs should have a small record; distributed, dynamic
or protected features add only their applicable obligations. Runtime credentials,
secret URLs/tokens and protected random material are not serialized/public evidence.

## 4. Execute only declared, admitted realization (IS03-IS04)

Providers can supply existing snapshots, generate data, fit approved preprocessing,
query a service or realize an environment episode. The generic core manages common
identity, dependency, admission, evidence and handoff rules. Explicit providers/drivers
implement supported native mechanics. A recipe descriptor does not authorize importing
arbitrary executable code, fetching packages, contacting a service or reading sources.
Each such effect needs applicable authority, resources and information constraints.

Retain implementation/dependency identities, resolved parameters/defaults, ordered
input bindings and actual randomization/fitted-state provenance. Bind actual outputs,
maps/masks/selectors and useful intermediates within retention policy. A seed alone
does not establish a realization; a path change must not redraw a fixed transformation
unless path is itself a declared factor. Restricted seeds use authorized opaque
references/commitments; no protected store is opened or new public commitment rule
selected here. Commitments/digests can themselves reveal information and need the
applicable audience policy rather than automatic public export.

### Example A: relabel and permute a table

Canonical variables [A, B, C] are presented in order [C, A, B], with neutral display
labels [v0, v1, v2]. The shown-to-canonical index map is [2, 0, 1]. Check actual
column movement, labels, values, missingness masks, units, intervention targets and
other relevant axis metadata under the declared operation. Whole-file bytes change;
claim the scoped mapped-value/body invariant actually checked, not byte equality.

The evaluator retains the inverse correspondence needed to interpret native outputs.
The native recipient receives only the information its condition permits. If its
task legitimately requires units or other semantic context, preserve those or
explicitly name the different joint-masking condition; do not broaden a labels-only
claim into removal of all domain information. Do not expose hidden correspondences
through filenames, case IDs, object keys, errors or adjacent manifests.

Preservation checks concern realized inputs. Differing native answers after a valid
transform remain audit evidence; do not repair/filter answers to make input preparation
pass. A failed required invariant holds the corresponding native request, retaining
the planned slot and actual reason. Predeclared admissibility/rejection sampling is
distinct from redrawing after inspecting native outcomes.

### Example B: fitted preprocessing and changed target meaning

Suppose an approved normalizer must fit on a declared calibration subset. Record
the actual fitting subset, implementation/parameters and captured fitted state, then
which state transformed each target input. Fitting on all available rows instead
violates that specified boundary even if the final dimensions and filenames match.
No universal train/test split is imposed on all causal-discovery tasks by this example.

Discretization, added noise, feature aggregation or proxy construction can change
variable meaning and reference applicability. S3 returns the actual realized domain,
mapping/loss and check evidence to S2. It cannot inherit a clean reference merely
because column names stayed the same. Scientific meaning and relevant eligibility
stay with S2; output scoring/effect computation stays with later subsystems.

External preparation and the native system's own preprocessing remain distinguishable.
Do not silently replace native preprocessing, reset caches or disable stages under
the full native-method label. Exact content can be reused only under the declared
recipe/state/randomization and recipient/policy conditions. Cache reuse preserves
occurrence lineage and exposure history; equal bytes neither prove a new independent
draw nor merge distinct scientific units.

## 5. Representation fidelity and heterogeneous sources (IS05)

A native encoding may be a CSV, array, prompt, schema plus values, service capability,
distributed partition or input stream. Bind format/schema, selector, dtype/precision,
missing-value/units/axis conventions and any accompanying context needed for the
claimed interpretation. Adapters may perform declared encoding, not hidden scientific
transformations. Rounding, clipping, dropping rows, renaming semantic units or adding
reference hints need explicit meaning and policy; they are not harmless transport
merely because a native format demands them. Unsupported required fidelity is a gap.

| Source/route | Required scoped realization evidence |
|---|---|
| File/object/memory snapshot | Bytes or permitted content evidence actually captured, source identity, encoding and relevant selector; mutable aliases/paths require a stable-use mechanism |
| Database or remote source | Query/selection/version/snapshot scope and actual result or owner evidence; a changing endpoint name does not identify a coherent snapshot |
| Generator or simulator | Procedure/configuration, randomization/state and realized outputs/episode evidence; a successful call is not proof of distributional correctness |
| Stream | Explicit source/partition/order/window/offset scope and captured extent; future messages are not part of a completed snapshot |
| Interactive oracle/CI/retrieval service | Admitted endpoint/action contracts and actual selected response/exposure evidence as interaction occurs; no need to precompute an imaginary full transcript |
| Multi-party or federated input | Per-owner input/partition/custody and coordination scope; local attestations can leave raw-content checks unavailable centrally |

Record unavailable content and limits rather than requiring prohibited raw-data
copies to make a manifest look complete. A local raw-byte check, owner attestation
and unretrieved declaration support different claims. Streams/interactive routes
may release admitted increments; a universal all-or-none whole-dataset upload would
exclude them. Required coherent batches instead need a mechanism that establishes
their complete consistent view before consumption.

## 6. Staging is an actual access boundary (IS06-IS07)

Recommend a recipient-specific native view, distinct from the evaluator/provenance
view. Inventory relevant data, metadata, paths, archive members, context, diagnostics,
inherited state, caches, mounts and network/service routes. Include denied/unknown
channels only to the extent actually established; declared inventory completeness
does not itself prove enforcement. Native process authority can reach beyond one
explicit file argument. Real isolation/mediation must cover the guarantee requested.

### Example C: a selected member inside a larger archive

An archive contains data.csv, an evaluator mapping and a reference graph. A selector
saying use data.csv does not restrict a native process that can open the entire
archive. Extract/construct an admitted projection or provide an enforcing selector
service under the relevant guarantees. Preserve source-to-projection evidence and
do not pass the full source archive just because S1 can represent member selectors.
Extra artifacts legitimately required by a method remain explicit condition inputs;
they are not removed solely to make an isolation label easier to claim.

### Example D: file changes between check and native read

The coordinator hashes a source path, then the file changes before the native system
opens it. The old hash proves the earlier capture only. Prefer an immutable copy,
version-pinned object, protected handle or other evidenced stable-use mechanism
appropriate to the route. A writable in-memory alias has the same issue.

Record observed mismatches and retain both identities where captured. Do not repin
the old snapshot or claim that a preflight path check proves actual native consumption.
Input identity, real access restriction and read/use observation are separate facts.
S1's explicit allowed-root resolver scopes that reader's access; it is not OS isolation
of the whole native process or a guarantee against concurrent filesystem mutation.

## 7. Partial staging and uncertain disclosure (IS08-IS09)

Separate preparation from activation where a backend actually supports protected
preparation. Bind each staged member's content/role, destination/audience, progress,
owner operation and evidence. Quarantine is an enforced custody property, not the
name of a directory. Atomic local publication can help establish a coherent bundle
within its filesystem scope; it does not establish remote all-or-none delivery or
access isolation. Activation itself requires current admission at the actual boundary.

### Example E: two files, one upload acknowledgement missing

A coherent batch needs data plus an intervention mask. Data uploads successfully;
the mask transfer becomes uncertain. Hold native launch/activation requiring the
complete batch. Preserve confirmed and unknown transfer evidence independently.

Uploading to a remote provider can itself disclose information to that recipient,
even before the job starts. Apply resource/exposure admission at that boundary.
A quarantined object in a custodian's own enforced domain has a different recipient
scope; state which boundary was crossed. Successful upload does not prove a later
native component read it; a missing reply does not establish zero disclosure.

Reconcile the same exact upload under supported operation/content/version semantics;
do not assume matching bytes make another upload free or authorized. If part of a
protected stream crossed the boundary, record established/possible extent. Unknown
extent remains unknown; size estimates are not proof of which records were exposed.
For incremental protocols, continuation follows the declared offset/ordering and
exposure policy rather than pretending an incomplete fixed batch was complete.

After a crash, the replacement coordinator reconstructs staged objects, rights,
partial transfers and pending exposure under the same account. Reuse established
immutable content where permitted; do not redraw transformations or reset allowances
merely because staging resumed. A required unavailable party/partition remains a
gap; no unilateral substitute changes the scientific question silently.

## 8. Cleanup, retention and concurrent ownership (IS10-IS11)

Cleanup has independent scopes: revoke future access; retire staging/activation
rights; remove owned temporary objects; release owner resources; retain or restrict
evidence under policy; reconcile remaining copies, usage and exposure. Each may
have acknowledged, unknown, failed or disputed results. Native stop or collection
closure does not automatically establish any of them.

### Example F: object deleted, job still has a copy

After a transfer, local scratch deletion is established. The provider may have
retained its object, and the native process may hold an open handle or loaded data.
Record the actual local deletion and separately seek supported remote revocation/
deletion evidence. No local deletion receipt proves erasure of native memory,
provider backups or learned state. Revoking a link can restrict future retrieval
without retracting bytes already disclosed. Cleanup does not replenish exposure.

Lost cleanup acknowledgements follow AL reconciliation rules. Restrict actions to
explicitly owned staging objects/generations and actual owner authority; never
infer that arbitrary source paths or evidence archives are temporary. Prevent stale
workers from deleting current/shared content through supported ownership and
reference/lease mechanisms; a local reference count alone cannot protect untracked
remote readers. No recursive deletion or real cleanup is performed in this pass.

Retain the authorized evidence necessary for declared reproducibility, with audiences
and retention boundaries distinct from native staging. Do not export evaluator-only
maps/raw private inputs merely to make a public methodology package self-contained.
If raw retention is prohibited or expires, preserve permitted receipts/references
and record availability loss and resulting verification limits. This is not permission
to delete historical scientific artifacts or change immutable published receipts.
Evidence publication receives its own later design pass; S3 cannot promise both
prohibited raw retention and unrestricted future byte-level verification.

## 9. Evidence handoff and minimum receipt meaning (IS12)

Return exact source/recipe/realization/output identities and domain mappings, actual
parameter/fitted/randomness evidence, scoped check results, encoding/native-view
bindings, intended and observed audience/boundaries, staging/transfer extent,
knowledge cutoffs, authority/reservation references and cleanup/retention obligations.
Reference shared definitions and use explicit unknown/non-applicability where needed;
do not require every field for every local input or expose runtime capability secrets.

Preserve source observations, declared claims, reconstruction and derived assessments
as distinct bases. Later evidence can revise current staging/disclosure assessments
without rewriting the earlier cutoff. If wrong input or excess information reached
the native system, retain intended and actual bindings, mark the scoped deviation,
and apply S2's declared population/nonconformance policy. Do not relabel conditions,
discard difficult units or turn input failure into a native crash/zero score.

## 10. Choices, alternatives and remaining work

| ID | Proposed direction | Strongest alternative | Cost / failure prevented | Reuse / still open |
|---|---|---|---|---|
| IS01 | Prospective preparation links precede final realized run/request binding | Require final run binding for every preparation operation | Conditional links; avoids circular readiness and dummy frozen requests | S2 materialization/bind_run/handoff; exact timing and interfaces open |
| IS02 | Separate source, realization, checks, staging, exposure and cleanup facts | One ready/staged input flag plus a log | More evidence; prevents capture or staging becoming proof of delivery/use | S1 snapshots/presentations and EA knowledge; predicates open |
| IS03 | Explicit admitted provider/transform execution with actual provenance | Call a recipe name with a seed and save the final output | Invocation/state records; prevents hidden defaults, unauthorized effects and untraceable redraws | S2 transform specs/receipts; execution providers unbuilt |
| IS04 | Declared input invariants, fitted-state scope and reference applicability | Gate on unchanged native answers or matching dimensions | More checks; prevents outcome filtering, fitted leakage and unsupported truth inheritance | S2 family/information rules; actual check execution contracts open |
| IS05 | Typed faithful representations for batch, dynamic and distributed inputs | Convert everything to one numeric table/full file | More contracts; prevents loss, unsupported coercion and false coherent snapshots | S1 selectors/domains and S2 sources; provider/encoding profiles open |
| IS06 | Recipient-specific views with actual access enforcement evidence | Supply a source package and tell the native system which member to use | Projection/mediation cost; prevents evaluator or metadata leakage | S1 audiences/S2 channels; backend isolation support unbuilt |
| IS07 | Stable-use binding appropriate to actual consumption boundary | Hash a mutable path immediately before launch | Storage/handles or backend support; prevents checked bytes differing from consumed input | S1 capture/identity; stable-use mechanics and observation scope open |
| IS08 | Track partial staging; coherent activation or declared incremental consumption | Assume local rename implies atomic remote batch delivery | Backend/extent records; prevents partial inputs masquerading as complete trials | AL operations/owner validity; staging/activation protocol open |
| IS09 | Admit disclosure at the actual crossed boundary; retain uncertain extent | Count exposure only on successful native launch/read receipt | Earlier holds; prevents upload leakage and crash-based allowance reset | S2 exposure/AL acknowledgement rules; custodian route integration open |
| IS10 | Scoped cleanup outcomes, ownership and persistent obligations | Delete the workspace on timeout and mark everything clean | Reconciliation/later cleanup; prevents stale deletion and false erasure/settlement claims | AL fencing/settlement; cleanup protocols unbuilt |
| IS11 | Separate native staging from audience/retention-controlled evidence | Preserve every raw input in one public reproducibility bundle | Storage/access/verification tradeoffs; prevents evidence export violating information policy | S1 evidence availability; publication/retention profiles remain open |
| IS12 | Source-linked S2/S1 handoff preserving intended/actual deviations | Rebuild a clean successful request after the run | Versioned records; prevents hindsight, condition relabeling and silent denominator changes | S2 frozen handoff/lifecycle; S3 integration unbuilt |

## 11. Prospective acceptance obligations and existing evidence

Future cases need declared positive controls and failures for: preparation before
final binding; exact relabel/permutation/mask alignment; permitted versus forbidden
fitting inputs; lossy encoding and reference-applicability gaps; native output
changes surviving input checks; selected archive member versus full archive access;
mutable file/memory races; partial remote upload before launch; uncertain extent;
incremental stream continuation; federated owner evidence without central raw copies;
stale coordinator cleanup of shared staging; lost deletion acknowledgement; retention
restrictions and later evidence correcting an earlier staging assessment.

These are planned tests, not executed S3 acceptance evidence. Existing S2 bindings
record supplied realization/check evidence and retain gaps without executing transforms.
Its information checks compare supplied policy/presentation records, not all actual
native channels. S1 captures and verifies bytes/selectors within reader scope;
its interrupted package-publication test is not remote native-input staging or
distributed cleanup validation. Existing source hashes are preserved and additional
anchors identify current code, not new guarantees.

The mandatory staged-tree gate checks offline package compatibility and publication
constraints only. No historical numerical rerun/certificate, scoring, checkpoint
contract, private source, sealed seed or production native campaign is changed here.

## Where we're going

Review the prospective binding order, transformation/access examples and partial
staging/cleanup boundaries. Then deepen dispatch and attachment, carrying exact
realized presentations, current authority and supported stable-use guarantees into
the actual invocation/attachment boundary. Observation/interaction, recovery,
publication, full S3 reconciliation, exact interfaces and build planning remain
later design work; implementation still requires explicit authorization.
