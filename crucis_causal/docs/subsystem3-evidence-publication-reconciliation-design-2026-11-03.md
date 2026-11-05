# S3 immutable evidence publication and reconciliation

Tickets: DLV-08, DLV-09; related DLV-10.
Date: 2026-11-03, America/Los_Angeles.
Status: EP01-EP12 are recommendations pending discussion. No S3 implementation,
exact wire/API freeze, production audience/retention policy, native scientific
execution, paid campaign, protected-store access or remote publication is authorized
or performed by this design note. Local package commit and external dissemination
are separate effects; neither implies permission for the other.

## 1. Continuation and scope

The user affirmed [recovery, stopping and accounting](subsystem3-recovery-stopping-accounting-design-2026-11-03.md),
committed as f42d7b214f1c8bc6d487f22494f105d8e62ff8b5, and requested immutable
publication/reconciliation, partial packages, corrections, earlier cutoffs and
restricted audiences. RC01-RC12 are direction-affirmed with exact details open;
that is not blanket interface acceptance or implementation approval. EP01-EP12
below remain proposals. Earlier dated proposal wording retains its history.

Retain [account/cutoff rules](subsystem3-minimum-account-knowledge-design-2026-11-03.md),
[admission/settlement](subsystem3-admission-lifecycle-design-2026-11-03.md),
[input/evidence custody](subsystem3-input-realization-staging-design-2026-11-03.md)
and [observation coverage](subsystem3-observation-collection-interaction-design-2026-11-03.md).
The [methodology index](subsystem3-methodology-index-2026-11-03.json) maps proposals
to narrower existing source/tests. Examples are hypothetical. This pass does not
publish research evidence, change scientific interpretation/scoring/paper inputs,
build the separate reviewer system or adopt a public protocol.

## 2. A publication is a scoped immutable view, not a final-success verdict (EP01)

Recommend an evidence package identifying its purpose/audience, account/scientific
bindings where applicable, selected evidence and dependency contexts, collection
period and exact admitted journal/evidence frontier, procedures/versions, output/
artifact/assessment coverage, unresolved questions and obligations. Features remain
conditional; ordinary local evidence should not require distributed-store fields.
The exact S3 envelope or reuse of existing S1/S2 package relationships remains open.

A partial package must be structurally well formed. Missing evidence is represented
with supported declarations, qualified external/unresolved references, gaps and
explicit extent under the applicable codec. Partial does not excuse dangling
internal references, changing record identity or pretending unsupported wire forms
exist. An absent member of a partial index does not establish native absence.

### Example A: P1 closes collection while acceptance is unknown

At evidence cutoff c1, E1 has command C1/A1, an invocation/acknowledgement gap,
captured partial diagnostics and unresolved native identity, output, cost and stop.
Package P1 records that actual basis, its coverage and pending obligations. It can
support preservation/integrity claims whose prerequisites are established without
inventing a graph, native failure, zero cost or a fulfilled scientific response.

A package boundary is distinct from native completion, collection closure and
liability settlement. P1 can be an interim checkpoint while collection remains
open, or reference an actual closure receipt. State which. Publication time does
not fill missing native event times or prove that every source was examined.

## 3. Distinguish package, record, artifact and publication-operation identity (EP02)

Freeze the proposed manifest under an exact serialization/snapshot contract before
its publication operation. Changed content/cutoff/view gets a new package identity;
unchanged copied records retain identity, producer, creation time and content under
their record codec, with reference meaning/dependency anchors preserved. New
observations/assessments/derived views get their actual new identities and provenance.

Package identity, full-manifest digest, individual record identity, artifact content
identity, scientific occurrence and publication-operation identity answer different
questions. Equal content does not merge separately commissioned occurrences. A
retry of the same exact publication operation can reconcile/reuse the same frozen
manifest; it should not create a new package merely because acknowledgement was lost.
Existing S2 frozen() deliberately allocates a fresh package identity per freeze;
do not call it again and describe the result as a byte-identical retry of old P1.

Preserve the received bytes/digest of imported snapshots. Re-encoding or pretty
printing can produce a different byte identity even with equivalent parsed content.
Use an explicit derived representation relationship where appropriate; never
silently replace the expected digest of original evidence. S2 already distinguishes
received raw snapshot digests from its canonical package encoding.

Keep the full-manifest digest/commit-verification receipt outside the exact bytes
whose digest it describes. A declaration inside a package can name intended checks;
the actual report can bind the frozen bytes separately. Do not create a self-hash
fixed point or mutate P1 after publication to insert its own publication receipt.

## 4. Later evidence changes current knowledge, not earlier cutoffs (EP03-EP04)

### Example B: P2 learns acceptance happened before c1

At c2 an adequately bound native receipt establishes N1 was accepted before c1.
Capture it at its actual acquisition time and create a new assessment/publication
P2 linked to P1 and the same E1/C1/A1. P1 still supports acceptance unknown at its
recorded evidence frontier. P2 supports acceptance based on later-acquired evidence,
within the receipt's native-time and authenticity scope. No new native attempt
or scientific repetition is created merely by learning the result.

Distinguish native event boundary, evidence acquisition, assessment basis/cutoff,
package commit and analysis cutoff. A later package can explain an earlier event;
it cannot put that evidence into an earlier decision view. The package must state
its actual selected basis and coverage rather than claim every fact was known or
examined by a wall-clock date. Multiple producers can require multiple frontier
positions/partial order, not one invented global timestamp.

S2's declared timing/selection rule determines whether late evidence can enter an
analysis. Updating the operational view does not silently change eligibility,
population, labels, scores, certificates or the frozen paper contract.

### Example C: decoder correction or disputed native association

P1 includes raw artifact B and derived output G1. A later decoder establishes a
different interpretation G2, or new native identity evidence disputes the earlier
job association. Preserve B/G1 and the earlier assessment, then publish the new
procedure/version, basis, G2 or association assessment, and exact revision/dispute
links. Do not rewrite G1 under its old record ID, refresh copied timestamps, or
call the new interpretation a newly observed native run.

A revised assessment can weaken or retract support for an earlier conclusion.
The old observation remains evidence of what was reported/captured, not necessarily
true native state. Retain disagreement and resolution reasons; latest arrival,
package number, preferred source or convenient result does not resolve a conflict.
Adjudication remains scoped/versioned and cannot grant itself scientific authority.

## 5. Verification has several independent scopes (EP05)

| Question | What adequate evidence can establish | What it cannot establish alone |
|---|---|---|
| Structure/references | Conformance to exact wire contracts and required reference rules | Native execution, truth or complete source coverage |
| Byte integrity | Bytes match an established expected identity within the checked scope | Source authenticity, historical existence time or scientific correctness |
| Source/time assurance | The actual issuer/attestation mechanism supports its named provenance/time claim | Every downstream interpretation or unchanged hidden native state |
| Coverage/knowledge view | Named sources/frontiers, examined evidence and gaps support the scoped view | Unobserved absence or a universal complete history |
| Audience/authority | Actual owner policy and destination mechanism permit/constrain the publication | Native non-use, erasure or rights created by metadata |
| Interpretation/scientific applicability | Named procedures and S2 prerequisites support the particular use | Universal causal correctness or automatic paper adoption |

Validation reports identify exact manifest/artifact subjects, procedures/code/contract
versions, actual permitted evidence, results and withheld scope. A package can be
validly preserved while interpretation remains unsupported. A stronger requested
profile with missing/failed prerequisites is withheld; do not reduce its requirements
silently or label the whole package scientifically verified.

A digest requires an established expected pin to detect change. A self-declared
hash or local timestamp does not provide external authorship or preregistration
assurance. Use actual supported trust/storage mechanisms for the requested claim;
do not require remote signatures or a particular storage vendor for every local
case. Metadata can represent a claimed assurance without establishing it.

## 6. Audience-specific projection before dissemination (EP06-EP07)

### Example D: private evidence, approved reviewer access and a public view

One authorized view may contain raw data and evaluator-only mappings; another
approved audience may access a defined subset; a public package may contain only
permitted summaries, provenance and scoped verification results. These are separate
destinations/effects with their own actual authority, information/resource admission
and retention rules. This is an audience design, not an implementation of a reviewer
engine. No real protected material is read/copied here.

Build an actual permitted record/artifact/dependency projection. Review transitive
references, payload selectors, source context, filenames/locations, diagnostics,
code/configuration provenance and metadata as part of the audience boundary.
Neither package roots nor choosing a data member inside a larger artifact removes
other serialized content. S1 Builder.package and S2 writer package creation include
their staged record sets; current stores serialize supplied package records. No
automatic complete redaction/audience projection is implemented by those helpers.

Unchanged safe records can be copied exactly where their reference meaning remains
valid. Redacted summaries or changed references/content require new derived records
with permitted provenance. Do not strip fields from an old record while retaining
its identity. Source IDs, digests, links, counts or even existence of restricted
objects can reveal information; expose only what the applicable policy permits.
Use supported scoped unresolved/declaration mechanisms or a faithful derived view
where direct references cannot be disclosed; exact projection contracts remain open.

A public view cannot claim direct raw-byte verification unavailable to that audience.
It may support permitted metadata checks or a scoped owner/validator attestation,
with that different basis explicit. Private verification is not automatically public
reproducibility. Runtime capability objects, credentials, secret URLs and protected
seeds remain outside serialized/public packages. Read authority does not create
publication authority; validation reads and destination writes also need their own
applicable permissions. A local path/policy label alone does not enforce an audience.

Release timing matters: permitted disclosure now can change later experiment exposure.
Record actual publication/access evidence and applicable custodian decisions; do
not reset history because the data later became public or a new attempt was created.
Remote release, package/site deployment, push or messaging remains a separately
authorized operation; this design authorizes none of them.

## 7. Publication commit, interruption and acknowledgement (EP08)

### Example E: manifest committed, local publication acknowledgement lost

Publication intent binds the exact proposed manifest ID/digest, audience/destination,
applicable checks/authority and actual owner operation. Prepare/validate within the
allowed staging scope, then commit under the backend's evidenced guarantees. Retain
the publication receipt/verification separately from the frozen subject bytes.

If the acknowledgement is lost, query the exact intended destination/identity under
current authority and compare established expected bytes/digest and required checks.
An adequately established committed P1 can be reused. Do not launch native work,
rebuild its outputs or allocate a fresh P1 merely to recover a missing receipt.
A rejected publication port operation may leave commit outcome unknown; distinguish
adequate pre-write denial from uncertain post-write outcome.

Records or staged files without a committed manifest are not a committed package.
Existing PackageStore writes immutable record files before its package manifest;
partial failure can leave record files without that manifest. Do not call the store
one all-or-none multi-file transaction or delete unexplained state as a recovery
shortcut. Reconciliation checks exact identities, completeness and ownership.

Local per-file atomic creation and fsync/conflict checks do not establish universal
power-loss durability, replicated-store commit, adversarial tamper resistance or
atomic publication across S1/S2 stores. A multi-package view needs its explicit
pinned dependencies/commit evidence and honest completeness. Do not claim a complete
root view from one successful component receipt. Stronger storage/commit profiles
need actual mechanisms/evidence; exact protocol remains open.

## 8. Current aliases and concurrent publication branches (EP09-EP10)

### Example F: two coordinators publish from P1

One publishes P2 with a late stop receipt; another publishes P3 with billing evidence.
Both can be valid immutable packages with different cutoffs/coverage. Their relationship
is not automatically a single total chain. A reconciled P4 may reference both, retain
distinct observations, recognize adequately established duplicate native occurrences,
and revise assessments with explicit basis. It is not a concatenation that sums
duplicate charges, ignores record conflicts or selects the best native answer.

A mutable current pointer is a convenience view selected for a named purpose under
an actual rule. Preserve immutable selection/alias-operation receipts if history is
required. Pin analyses to exact packages, records, procedures and cutoffs, rather
than whatever current resolves to later. Pointer advancement does not itself establish
truth, scientific selection eligibility, chronology or settlement of conflicts.

Use the actual concurrency precondition required by the alias purpose. Existing
PackageStore.select_current locks a local alias and compares expected_previous to
the selected value. It emits a generation but does not take/check an expected
generation. If a selection changes A -> B -> A, value comparison alone cannot detect
every intervening update. A stronger no-missed-update profile needs an actual
revision/generation precondition or equivalent mechanism; it is not already supplied.
Value-based CAS can remain truthful within its narrower contract.

If pointer acknowledgement is lost, reconcile the operation and actual current
state under its supported guarantee. Seeing the intended target currently selected
does not alone prove this particular operation caused the update. Do not force
overwrite after conflict or infer exact mutation count without supporting evidence.
Publishing immutable P2 can succeed while pointer advancement remains unresolved.

## 9. Availability, relocation and retention (EP11)

### Example G: artifact disappears or a locator now serves different bytes

P1's artifact pin remains unchanged. A new availability observation records current
absence, denial or mismatch; earlier successful capture/integrity evidence remains
time-scoped. Missing content is not proof of zero native output. Different bytes
at the same path become separately captured evidence when authorized, not a silently
updated historical digest. Distinguish known unavailable, unexamined, denied and
integrity-unestablished scope using the applicable representations.

An authorized relocation can preserve artifact content identity while changing
retrieval evidence/locations. Use new location/availability records or a supported
resolver relationship without mutating the old snapshot. A new mirror is not assumed
authentic merely because the basename matches. Current readers do not implement a
universal relocation/retention service.

Immutability does not require unrestricted permanent raw-data retention. If retention
expires or access is revoked under actual policy, retain permitted receipts/references
and publish new availability/verification limits. Never promise unrestricted future
byte verification when the necessary content cannot be retained or accessed.
This is not permission to delete historical evidence or rewrite published identities.

If restricted material was already disclosed, a corrected public view does not
retract earlier copies or prove erasure. Any actual owner-approved access removal/
revocation requires its own scope and receipt. Preserve the exposure/deviation facts;
do not make a redacted replacement appear to be the original publication.

## 10. Handoff and minimum receipt meaning (EP12)

Return exact frozen subjects and digest/serialization scope; package/record/artifact
and dependency identities; account/trial/request/attempt and collection relationships;
admitted evidence frontier and assessed coverage; procedures/check results with
withheld claims; audience/projection/authority references without secrets; actual
destination commit/availability evidence; revision/dispute/branch relationships;
pointer selection state where applicable; pending publication/resource/exposure/
retention obligations. Share references and use conditional features rather than
requiring every local package to instantiate every distributed concept.

The common core should coordinate snapshot identity, dependency/claim consistency,
audience policy, cutoff/revision meaning and reconciliation. Explicit backends/owners
supply actual storage, access, commit, attestation, retention and pointer guarantees.
No single preserve/verified/final flag establishes all those dimensions.

The scientific handoff remains rule/proposal -> exact implementation -> scoped
test/receipt -> supported claim and limitation. Later evidence or reviewer findings
are inputs for adjudication, not authority to alter fixed experiments, certificates
or the manuscript. Generic research/reviewer tooling remains outside Crucis.

## 11. Choices, alternatives and open contracts

| ID | Proposed direction | Strongest alternative | Cost / failure prevented | Reuse / still open |
|---|---|---|---|---|
| EP01 | Structurally valid partial views with explicit scope/gaps/obligations | Publish only final success or flatten missing evidence into absent output | More states/coverage; prevents hidden failed units and fabricated completeness | S1 snapshots/indexes/EA closure; S3 snapshot envelope open |
| EP02 | Distinct immutable identities and exact-byte receipts outside their subject | Rewrite one result file or canonicalize imported bytes under the old pin | Versioned storage; prevents identity mutation, self-hash cycles and loss of original bytes | S1 store/S2 frozen/raw digests; publication-operation protocol open |
| EP03 | Evidence frontier and analysis cutoff stay distinct from native event/commit time | Rebuild every historical view from newest evidence | More reproducible views; prevents hindsight and changed populations | EA/OC cutoffs/S2 timing; as-of closure contracts open |
| EP04 | Explicit new corrections/disputes with original evidence preserved | Replace wrong fields or take latest package as truth | More provenance; prevents hidden decoder/association changes and false consensus | S1 assessments/S2 snapshots; reconciliation procedures open |
| EP05 | Scoped verification dimensions and actual trust mechanisms | One verified badge from schema/hash pass | Withheld claims/support detail; prevents integrity becoming authorship/scientific proof | Existing profiles/digests; S3 assurance matrix open |
| EP06 | Actual audience-specific projection over records/artifacts/dependencies | Choose roots or redact display while exporting the whole package | Projection/verification work; prevents transitive metadata/private evidence leakage | S1/S2 packages and IS custody; projection contracts unbuilt |
| EP07 | Owner-admitted dissemination with independent audience/retention effects | Read permission or local commit implies permission to share anywhere | More scoped decisions; prevents unauthorized disclosure and exposure reset | AL owner/exposure rules; backend enforcement unbuilt |
| EP08 | Reconcile exact commit identity after interruption, state backend guarantees | Re-publish fresh identities or assume atomic multi-store success | Commit evidence/partial state; prevents duplicated occurrences and false durability | PackageStore per-file guards; multi-package commit protocol open |
| EP09 | Mutable current pointer separate from pinned views; exact concurrency scope | Use current/latest as the scientific evidence and assume every CAS checks generations | Versioned receipts; prevents drift, missed-update overclaims and forced overwrite | S1 selected-value CAS; stronger generation contract unbuilt |
| EP10 | Explicit compatible merge/association/dispute across branches | Append all records/counts or choose one convenient branch | Reconciliation work; prevents double counting and favorable selection | Immutable records/EA/OC identity; branch merge protocol open |
| EP11 | Immutable content pins with new availability/retention evidence | Update old digests/locations or promise permanent unrestricted retrieval | Ongoing access/limits; prevents repinning and false reproducibility/erasure | S1 Resolver/S2 pins; relocation/retention integration unbuilt |
| EP12 | Source-linked S2/scientific handoff with support limits | Treat publication as scientific adoption or rebuild reviewer tooling here | More explicit claim mapping; prevents scope transfer and paper-contract changes | Existing methodology index/S2 handoff; full S3 reconciliation remains |

## 12. Prospective validation and actual evidence boundary

Future cases should publish a valid partial package with no graph, then later
acceptance/output/stop/cost evidence without mutating prior cutoffs or trial counts.
Test decoder/association corrections, same-ID changed-content rejection, raw versus
re-encoded snapshot identities, external receipt subject pins and no self-hash cycle.

Exercise missing versus broken internal references; valid unavailable external
content; failed/unknown stronger checks without a scientific verified label; restricted
records hidden behind safe roots/selectors; transitive metadata/locator/provenance
disclosure; derived redaction with new IDs; appropriate audience-specific claim limits.
Use dummy material only, not real sealed/private data.

Interrupt publication before/after record writes, manifest commit and pointer update;
recover exact committed bytes without native rerun. Include S1/S2 partial commit,
concurrent branches, legitimate duplicate observations versus conflicting records,
value CAS conflict and A -> B -> A semantics, lost pointer acknowledgement and pinned
analyses independent of current. Exercise relocation, denied/unavailable/changed
artifacts, authorized retention loss and corrected views without false erasure.

These are planned S3 acceptance obligations, not newly executed tests. Existing
S1 fixtures check immutable local publication, partial bytes without a fake graph,
interrupted staged-file distinction and selected-value CAS. S2 tests check distinct
frozen packages with unchanged records, exact handoff pins, raw received digests,
explicit supplied access and record/dependency conflicts. They do not implement
S3 audience projection, full temporal reconciliation, distributed commit, stronger
generation CAS, external trusted time or unrestricted retention guarantees.

Source/test hashes are preserved; additional anchors identify current primitives.
Mandatory staged-tree gates check offline compatibility/public-source boundaries,
not the new protocols. No historical numeric campaign/certificate, scoring, private
source, production policy, paper contract or remote publication changes here.

## Where we're going

Review partial/corrected/audience-specific views, commit recovery and current-pointer
limits. Then consolidate the complete S3 contract across all seven responsibilities:
resolve outstanding identities/cardinalities, dependency order, owner/cursor/handle/
decision/verification interfaces and support profiles using complete worked records
and interruption cases. Only after that reconciliation and final design review do
we freeze exact contracts and implementation bundles with acceptance gates;
implementation still requires explicit authorization.
