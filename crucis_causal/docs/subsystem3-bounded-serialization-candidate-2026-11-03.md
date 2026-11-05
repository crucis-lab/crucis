# S3 bounded serialization candidate

Tickets: DLV-08, DLV-09; related DLV-10. Date: 2026-11-03 (America/Los_Angeles).
Status: BS01-BS12 are recommendations pending review. Candidate common wire forms,
not an adopted protocol, implemented schema/codec, complete native fixtures or S3
acceptance evidence. No implementation authorization is inferred.

## 1. Continuation and bounded scope

The user affirmed the [minimum/conditional and support direction](subsystem3-minimum-record-capability-matrix-2026-11-03.md)
at 6f0669a4a4a2d134548de202197e456aa14e5b09 and requested exact field forms,
references, cardinalities, missingness and version rules. Record MS01-MS12 as
direction-affirmed with details open, keeping the original dated proposal intact.

This pass proposes the common encoding and closed record/role vocabulary in the
[declarative catalog](subsystem3-serialization-catalog-2026-11-03.json).
Its [four-case fragments](subsystem3-serialization-specimens-2026-11-03.json)
exercise boundaries; they are explicitly partial payload specimens with hypothetical
reference stubs, not complete wire packages or actual SC-1/SC-2 packages. They pin
the prior 117-entity traces and requirements overlay without rewriting either.

Operation-specific parameter grammars, actual owner/journal/driver guarantees,
native identity descriptor contracts and S1/S2 projections remain explicit
dependencies for the next interface/compatibility pass. A generic reference slot
does not make every target type acceptable for every operation. No unspecified
grammar, missing proof or future mapping is treated as an executable default.

SC-3 is a local candidate label. The proposed version string below neither adopts
audit protocol v1.1 nor changes historical protocol, certificate, scoring, finding,
paper, scientific population or sealed-policy versions.

## 2. Transport and bounded decoding (BS01)

Use strict UTF-8 JSON. Reject duplicate properties before overwrite; invalid UTF-8,
unpaired surrogate code points, nonstandard numeric tokens and non-JSON syntax.
No Unicode normalization, case folding, floating-point coercion or silent repair.
Every declared core field is required; objects are closed. Structural null and bare
JSON numeric tokens are disallowed. Native null/numbers/invalid encodings can remain
inside opaque captured bytes; their existence is not a structural decoding failure.

An explicit read policy bounds manifest bytes before decoding, nesting while
decoding, scalar UTF-8 bytes, collection items, records, reference occurrences and
external descriptors before recursive resolution. The catalog gives illustrative
positive integer-string limits, not universal defaults or scientific stopping rules.
Resolvers also need explicit traversal/retrieval budgets and visited identities;
no automatic network/schema fetch, sibling path search or execution follows a URI.

Exceeding a bound gives a scoped ingestion/representation diagnostic. Never truncate
and label a partial manifest valid. Native large/streaming/federated data can remain
in pinned artifacts with selectors/windows and access limits; one in-memory JSON
document or copied private raw dataset is not a universal native requirement.

## 3. Package, record, minimum and identity forms (BS02-BS03)

Candidate format: `{name:"s3.account_package", version:"0.1.0-proposal.1"}`.
Core record contract.name equals record_type and uses that exact candidate revision.
Definitions for every payload key/type are in catalog.core_payloads (33 kinds).
Unqualified type names there mean s3; explicitly qualified s1/s2 names keep ownership.

Package = {format:Contract, package_id:ID, roots:KnownRef[1], records:Record[1..n],
external_packages:ExternalPackage[], extensions:Extension[]}.

Exactly one internal account_view or projection_view root in this candidate view
package. Other material can be included or referenced; a larger archive can reference
several packages. This is a view-publication boundary, not a one-account/one-job
scientific rule. Definition-only/native evidence packages retain their own formats.

Record = {id:ID, record_type:QName, contract:Contract, producer:KnownRef(component),
created_at:K(Time), provenance:Source, payload:ClosedPayload, extensions:Extension[]}.

Local records are only recognized S3 kinds; S1/S2 records stay in their own external
packages. Producer is the S3 recorder, distinct from a reported native producer.
A component can intrinsically identify itself; self-reference is not native proof.
Source = {basis:reported|observed|reconstructed|derived|intrinsic, evidence:Ref[],
procedure:K(Contract), inputs:Ref[]}. This explicit S3 procedure-contract form is
not a verbatim change to S1/S2 Source.procedure component-reference shapes.

New actual recorder creation times should be recorded from the actual recorder
clock with uncertainty. Import/native times remain separately attributed. Unknown
time is retained on actual recording failure/historical reconstruction, not replaced
by a story sequence label, guessed wall time or implied global clock.

ID is lowercase UUIDv4 lexical form, as in S1/S2. Allocate/persist occurrences
independently of content equality. Account definition/purpose is immutable; its
stable ID is referenced by later immutable view records. New contents/cutoff get a
new view/package identity. Equal bytes with distinct IDs do not merge attempts,
actions, records, repetitions or transport occurrences. Native IDs remain scoped
descriptor values, never forced into UUIDs. Fixture UUIDs are labeled synthetic.

Full-view minimum encoding:

| Minimum | Exact location/meaning |
|---|---|
| M01-M02 | Package.format, record.contract and account_view.view_role=full_account |
| M03-M04 | account_view.account and the immutable view record.id; package_id is the exact artifact boundary |
| M05 | Record.producer, created_at, provenance; component implementation can be unresolved |
| M06 | account.purpose and account.target -> closed target record (definition/scope/subjects/requirements/relations) |
| M07 | account_view.audience -> closed audience record (purpose/recipients/disclosure_policy/authority) |
| M08 | account_view.frontier -> closed frontier record |
| M09 | account_view.requirements -> requirement_context with requested_claims/coverage |
| M10-M12 | activities, evidence, assessments scoped indexes |
| M13-M15 | disposition reference, obligations index, collections index |

View = {account:KnownRef(account), view_role:full_account, audience:KnownRef(audience),
frontier:KnownRef(frontier), requirements:KnownRef(requirement_context),
activities:IndexList(Ref), evidence:IndexList(Ref),
assessments:IndexList(KnownRef(assessment)), disposition:KnownRef(disposition),
obligations:IndexList(KnownRef(obligation)),
collections:IndexList(KnownRef(collection_period|collection_closure))}.

A bootstrap can keep locally empty indexes without inventing R/A/N/cursors/holds.
The catalog's separate target/audience kinds keep the universal minimum interpretable
without requiring an arbitrary opaque operation payload decoder.

## 4. References, pinning and missingness (BS04-BS05)

Contract = {name:QName, version:String}; Code uses the QName grammar in the catalog.
Selecting a QName/version is a declaration, not installation of an interpreter.

KnownRef(T) = {binding:internal, target:ID, target_type:QName} |
{binding:external, package_id:ID, target:ID, target_type:QName}.

Ref(T) additionally permits {binding:unresolved, target_type:QName, reason:Code,
evidence:Ref[], source_labels:String[]} with no target or package_id. A union slot
still names one concrete actual target_type per reference. An unresolved reference
does not allocate a stand-in native occurrence.

Internal targets resolve uniquely to the declared local type. Qualified external
targets resolve only through the declared package and supplied resolver, checking
format/type/content pins as required by the requested claim. No fallback to a local
same-ID record, ambient package, newest version or broader alias is permitted.
S1/S2 references cannot be internal to an S3 package. Same-ID/different-content is
an identity conflict; duplicate IDs within a package are rejected even if identical.

ExternalPackage = {package_id:ID, format:Contract, locator:K(String),
expected_digest:K(Digest), access:Code}. This includes format, unlike SC-1's smaller
descriptor; convert explicitly when needed. Unknown pin/retrieval/rights can be
preserved, but cannot satisfy claims requiring verified imported bytes/semantics.
Access labels do not grant access. Retrieval is itself an admitted effect when
applicable. Versioned selectors do not confer file-read authority.

K(T) is exactly one closed variant:

```
{state:known, value:T, basis:Ref[]}
{state:unresolved, reasons:Code[1..n], evidence:Ref[]}
{state:not_applicable, rule:Contract, scope:Ref[]}
```

Known means the recorded value/claim is supplied with its provenance; it does not
certify its native truth. Non-applicability needs its scoped rule/basis, not a
convenient omission. K(KnownRef) uses only known-identity references inside known;
known(unresolved-reference) is forbidden. Use Ref when only identity is unknown;
use K(KnownRef) when non-applicability or value-level missingness is meaningful.

No new overloaded disputed/not_examined/null knowledge variants. Not-examined
coverage belongs in an index/requirement entry or an explicit unresolved reason.
Conflict belongs in separate assessments with conflicts_with/basis/frontier links.
Identity conflict is a resolver diagnostic, not an ordinary replacement value.

## 5. Scoped indexes, assessments and order (BS06-BS07)

IndexList(T) = {members:T[], extent:complete_for_scope|partial_for_scope|
not_examined|unresolved, scope:Scope, gaps:KnownRef(diagnostic)[]}.
Scope = {subjects:Ref[], qualifiers:Ref[]}.

Each scope must be meaningful by its declared subject/qualifiers and inherited
named slot context; an empty scope cannot mean global completeness. Not-examined
requires zero members. Partial/unresolved indexes may retain established members.
Empty complete means no members in that exact local scope; it does not mean a
native negative, successful abstention or discharged liability. Duplicate identity
members are rejected for set-like indexes; ordered/multiset meaning requires an
explicit contract with occurrence records, never implicit deduplication.

Assessment carries question:Contract, scope:Scope, result:K(Boolean|String|Number|
KnownRef), basis:IndexList(Ref), frontier:KnownRef(frontier), procedure:Contract,
revises:KnownRef(assessment)[], conflicts_with:KnownRef(assessment)[]. A later
assessment states whether it revises another conclusion; it does not erase its
basis or manufacture earlier knowledge. An unresolved conflict holds a claim/effect
whose declared rule requires agreement. An assessment's known result is its
attributed conclusion, not the coordinator's unqualified world truth.

Frontier = {local_records:IndexList(KnownRef), source_positions:IndexList(
KnownRef(source_frontier)), selection_rule:Contract}. It identifies admitted local
record versions, not global time or all native events. Its own assembly and the view
it constructs do not need to appear among its earlier input records. Context/self
reference is permitted; typed causality/revision/period-predecessor relations must
not cycle. Do not reject every reference cycle or infer causality from JSON order.

Source frontier preserves source/episode/protocol/filter/generation and four
separate K(Cursor) positions: fetched, durably_captured, interpreted, acknowledged.
Cursor = {contract:Contract, position:String, scope:Scope}. Position is opaque;
only the selected source contract can compare/replay it. A largest seen number is
not a proof of contiguous durable coverage. A one-shot source uses justified
not_applicable positions. Restarted native work gets a distinct source/incarnation;
reconnection can use an earlier position only under established compatible scope.

Collection period is an immutable scope/bounds/policy definition. Closure is a
separate immutable period/frontier/stopping-rule/coverage/obligation record. Late
receipt import appends evidence; resumed active collection creates a linked period.

## 6. Conditional role and operation cardinalities (BS08)

The catalog names all 18 family contracts and their exact role keys. A
requirement_case contains family, scope, applicability, rule, basis, roles, gaps,
frontier. Each RoleBinding is {role:Code, members:IndexList(Ref)}. When applies,
every listed role occurs exactly once, even if its index explicitly says unresolved
or scoped-empty. Other applicability states carry no role payload and retain
rule/basis/gaps. Generic not_examined cannot override a known positive trigger.

This is a requirement/evidence index, not an execute-anything metadata API.
Closed structural role names do not supply missing native parameter grammars.
The exact operation/claim contract must additionally establish accepted target
types, positive counts, phase constraints and actual admission predicates. Missing
such a contract withholds the operation/claim; it does not waive a required slot.

Important positive constraints for the four paths:

| Situation | Candidate constraint |
|---|---|
| Planned command | Exactly one immutable operation/binding/frontier; admission may be unresolved; zero transmissions before send |
| Existing-target attachment/control | Adequate native subject/incarnation and current ownership required before dependent effect; plain ID text is insufficient |
| Native inventory | Zero/multiple candidates retained; a supported association does not itself install the single guarded S1 active handle |
| Held action decision | Zero locally selected responses allowed; exact information gap retained; never a synthetic abstention |
| Actual delivery | Nonempty action and response indexes with an exact correlation/bundle contract; one physical request may serve several roles only under that contract |
| Coordinator reconnect | Existing native attempt remains; no new native successor inferred from changed ownership/connection |
| Native checkpoint restart | Explicit predecessor/successor relations, allowed mode and evidence for each required component/overlap boundary |
| Support claim | Exactly eight axis entries, one per catalog axis, using each axis's own status vocabulary and scoped evidence |

S1's single-action grants and guarded handles are unchanged. Composite delivery,
unknown-origin jobs and richer incarnation descriptors need the explicit subsequent
compatibility mapping/driver support. No fragment claims that mapping already exists.
Runtime handles, bearer grants, secrets and sealed values are not serialized as
replayable authority. Records retain scoped identities/receipts and truthful gaps;
reacquiring actual runtime authority is a separate admitted operation.

## 7. Numbers, revisions, bytes and views (BS09-BS10)

Index is unsigned integer text. Number retains the S1/S2 tagged integer,
finite_decimal and nonfinite forms. Preserve decimal lexeme/sign/exponent; Boolean
is distinct. Nonfinite numbers require an explicitly allowing semantic slot and
cannot serve as capacities, counts, budgets or finite charges. Unknown is not NaN.
Use exact decimal arithmetic for compatible quantities; do not sum unlike units,
owners, membership/interval scopes or inclusive totals without the declared rule.

Resource entries identify owner/resource/unit/scope, kind, quantity, interval,
finality, aggregation, basis and revisions. Replacing a bill differs from adding
a delta. K's bill5 revises bill3 and adds bill4 => 9. The three documents/occurrences
remain; their numerical values are not three additive charges. Exposure has its
own recipient/information/facet/policy history, never an automatic budget reset.

Time uses S1's UTC-instant or native-report forms, with S3/component/external clock
references explicitly scoped. Native-report text and uncertainty are preserved.
Local story labels l07/r08/i08/k07 are evidence selectors/order annotations, not
UTC timestamps or universal native clocks.

PayloadRef = {artifact:KnownRef(s1.artifact_snapshot), selector:K(Selector)}.
Digest identifies algorithm=sha256, exact value, byte_length:Index and byte scope.
Native bytes use S1 snapshots/declarations and remain opaque unless a supported
exact decoder/selector/domain contract is supplied. No inline arbitrary JSON bag
substitutes for typed critical native parameters. Access/integrity/semantic validity
are independent; an unavailable file may retain identity while its current location
changes in a new availability observation.

Whole-package pins hash the exact stored bytes, not reserialized JSON. For same-ID
record comparison only, propose a separately named s3.record_comparison contract:
UTF-8 encoding of the parsed closed record with object keys lexically sorted, compact
separators, arrays unchanged, no normalization or number conversion. Keep the
original byte artifact too. This is not a new scientific canonical hash and does
not change S1/S2 comparison procedures or historical manifests.

Publication receipts live outside their exact hashed package to avoid self-digest
recursion. A receipt can be in a subsequent package. A new view/package ID denotes
new contents/cutoff; journal/storage commit ordering and actual atomicity remain
the next interaction/backend contract, not established by the manifest.

## 8. Audience projections and exact-version evolution (BS11)

Projection root has view_role=audience_projection, audience, projection_contract,
members, claims and limits. It does not require a private account/target/lineage
reference. Where public metadata is allowed, public statements use their own
permitted frontier and attributed assessment, with private verification basis
explicitly unavailable in that public scope. They do not export the private
assessment's references or claim public raw verification. Private lineage/derivation
receipts remain in the authorized view.

Projection metadata, producer, diagnostics, labels, extensions and dependencies are
part of the actual audience closure. Do not export a restricted ID merely to satisfy
a universal field. A self-contained complete package/audience-closure proof is not
established by the partial specimens in this pass.

**L's unchanged policy permits exactly its two native public entities, not new S3
producer/audience/frontier metadata.** Therefore its actual public deliverable stays
in that permitted native artifact format; S3 publication/lineage bookkeeping stays
private. The new S3 projection fragments illustrate candidate metadata and are not
authorized exports under L's policy. A public S3 package would require a separately
permitted metadata closure. Do not silently broaden the policy to make the example
fit a package. This supports heterogeneous deliverable formats without weakening
the universal minimum for an actual S3 full account view.

Readers select exact package, record, family, operation, feature, payload, selector
and comparison versions. No implicit semver widening, newest-handler fallback or
contract download. Unknown core type/version is preserved as opaque evidence with
diagnostics, not accepted as a known account. Unknown extensions retain their bytes;
critical affected/dependent guarantees remain withheld. An unsupported effect
payload never becomes executable just because an extension says critical_for=[].

Any field/enum/constraint meaning change gets a separately reviewed version even
when a deployment treats it as backward compatible. Explicit compatibility
procedures create derived records/packages with source pins/procedure/loss report;
they never mutate the original identity or silently promote missing facts. Framework
release, wire version, adapter feature version, scientific policy and study contract
versions remain independent.

## 9. Four-case checks and remaining gaps (BS12)

| Case | Serialization checks | Constraint exposed |
|---|---|---|
| L | Six-block view fields, one-shot cursor NA, independently scoped statement | Metadata cannot inherit public export permission; retain the two-entity native public artifact and private S3 bookkeeping under the unchanged policy |
| R | Early unresolved versus later acceptance assessment, separate cutoffs, scoped durable cursor18 | A cursor/native ID string supplies no incarnation or gap-free replay proof; descriptor/source contracts remain explicit dependencies |
| I | Selected Q1 versus held empty Q2, information gap, delivered versus used facets | Empty selected is not native abstention; missing Q2 information is not a second response or proof of missing provider code |
| K | Two attempt references, model/optimizer loaded, RNG unknown, replacement bill and exact total9 | Partial permitted continuity does not become full state; numeric revision and native repetition identity stay distinct |

All specimen references are synthetic context stubs or explicitly unresolved; no
real external package is fabricated or verified. Positive common-shape checks are
documentary only. Counterexamples specify intended future rejection/withholding,
not executed S3 validator tests. Complete native wire packages, exact target-role
compatibility/parameter schemas, owner/journal/driver signatures, commit/capture/ack
proofs and runtime acceptance remain to be closed before final review/build planning.

The external documentary check passed for 33 candidate payload-key sets, four
cases with 41 payload fragments and 246 reference occurrences against their declared
synthetic contexts. It checked tagged missingness/index shapes, distinct early/late
frontiers, held Q2/no second delivery, unknown RNG loading, bill revision yielding9,
and absence of selected private references from the projection-fragment payloads.
Fourteen negative cases are documented, not executed against a nonexistent S3
validator. Original trace/overlay hashes and existing source/test/fixture pins were
checked; two additional existing S2 source anchors describe inspected primitive
ownership. These checks establish neither complete reference/package closure nor
native semantic compatibility, temporal admission, audience authorization or support.

| ID | Proposed direction | Strongest alternative | Cost / failure prevented |
|---|---|---|---|
| BS01 | Strict bounded UTF-8 transport and explicit local limits | Permissive parsers plus post-parse validation | Explicit ingestion failures; prevents overwritten duplicates/resource exhaustion being misread as native outcomes |
| BS02 | Separate closed S3 view package and recorder envelope | Extend the existing S1 package in place | New resolver ownership; preserves accepted schemas and native/recorder distinctions |
| BS03 | Occurrence UUIDs, immutable account/view roles, separate byte pins | Content-address every entity | More identities; avoids merging identical events/repetitions or cyclic self-digests |
| BS04 | Qualified exact references and explicit unresolved identities | Ambient ID lookup | Descriptor overhead; prevents wrong-package/type/version substitution |
| BS05 | Existing three knowledge variants plus separate conflict records | A single broad status enum with null | More links; prevents unknown/NA/disputed/false conflation |
| BS06 | Scoped indexes and immutable basis/frontier references | Latest-state snapshots with optional lists | More scope metadata; prevents missingness/hindsight becoming completeness |
| BS07 | Opaque scoped cursors and distinct progress stages | One numeric high-water mark | More source contracts; prevents gaps, replay mismatch and acknowledgement loss |
| BS08 | Closed family role indexes plus exact operation-specific constraints | Inline every possible native operation schema in core | More registered contracts; preserves generic representation without permissive execution |
| BS09 | Tagged decimals and explicit revision/aggregation scope | Floating totals with a newest-bill rule | Typed arithmetic/revision links; prevents precision loss and double counting |
| BS10 | Exact stored-byte pins and separately versioned record comparison | Hash one universal normalized JSON representation | Two named procedures; preserves original evidence and existing scientific receipts |
| BS11 | Audience-specific view shapes and exact-version compatibility procedures | A full private-root shape everywhere and tolerant readers | More projection/version work; prevents identity disclosure and silent semantic upgrades |
| BS12 | Labeled partial specimens and explicit remaining native-contract dependencies | Transcribe all native packages before reviewing common wire forms | Another review step; avoids invented S1 projections and false acceptance claims |

## Where we're going

Review BS01-BS12 and the bounded forms. Then close exact operation/parameter/role
constraints, journal/owner/driver/decision/storage signatures and S1/S2 mappings.
Revisit complete package and failure specimens, support-profile claims and actual
backend assumptions before final S3 design review, implementation DAG and explicit
build authorization. No S3 runtime or existing scientific evidence changes here.
