# Subsystem 2: minimum case and collection obligations

Tickets: DLV-08, DLV-09; related DLV-10, DLV-06/07 and ADV-01.
Date: 2 Nov 2026, America/Los_Angeles.
Status: design discussion only. Uzair endorsed continuing the reusable-case and
explicit-membership direction and reaffirmed genericism, faithful evidence,
scientific rigor and traceable, justified coverage. The detailed obligations below
are proposals for review, not frozen fields, implemented profiles or adopted policy.

Predecessor: [case identity and collection membership](subsystem2-case-collection-design-2026-11-01.md).
Sources: [S2 structure](subsystem2-structure-design-2026-11-01.md),
[S1 foundation](system-connections-foundation-contract-2026-11-01.md),
[capability map](system-connections-capability-map-2026-11-01.md),
`audit/core/battery.py` and `audit/connections/{model,domains,evidence}.py`.
No new native execution, scientific result, empirical coverage count or test result
is established by writing this document.

## 1. Meaning of minimum and coverage

The minimum is a complete account of the record's bounded claims and limitations,
not a requirement that every fact about an old experiment be recoverable. Unknown
history must be preserved. It cannot satisfy a later requirement for verified
identity, paired evidence, random selection or prospective commitment by default.

Separate three obligations:

1. Preserve the evidenced case/material and unresolved associations faithfully.
2. Interpret a particular case family using its named semantic contract.
3. Establish readiness for a particular planned scientific use.

These are scoped assessments, not one global valid flag. Evidence preservation
does not prove native integration, correct truth, complete membership, replayability
or statistical validity. A generic core must allow all mapped families to be
described without erasing meaning, while refusing unsupported stronger claims.

Each obligation below has a reason: identify evidence, preserve meaning, expose
selection/dependence, prevent leakage, or bind a reproducible claim. Adding a field
does not itself increase measured coverage. A null finding or a deliberate duplicate
can make a meaningful contribution; they must retain their actual role.

## 2. Common record foundation

Every newly authored catalog/release/membership record must identify its own kind,
contract version, stable scoped identity, actual authoring/importing component and
creation event/time. Original source identity/time are separate and may be unknown.
The new author cannot be replaced by an unknown historical producer. Exact wire
syntax, reference rules and packaging will be resolved later using S1 conventions.

Claims retain scope and basis: identified source evidence, source declaration,
direct observation, explicit current design choice or versioned derivation from
identified inputs. A declaration is evidence of what was declared, not independent
proof of its truth. A derivation identifies procedure/version and inputs. This
does not require an infinite proof chain for a recorded human/source statement.

Required missing information has an explicit scoped gap and reason, including
unknown reason when necessary. Not applicable requires a meaningful rationale.
False, zero, an empty population, not examined, unavailable and unknown are distinct.
Conflicting claims retain both sources. A later reconciliation has its own basis
and cannot erase the earlier record. Recording a search failure does not prove
that an artifact or case never existed.

## 3. Case revision: required responsibilities

| ID | Required account | Why it is needed |
|---|---|---|
| C1 | Stable local case identity and exact immutable revision; source-scoped aliases or unresolved source association | Prevent filename collisions and accidental merging of distinct cases |
| C2 | Evidence-situation boundary: what entities, scope, source state or bounded access situation this case denotes | Prevent one dataset, window, group or task scope from being silently substituted for another |
| C3 | Evidence bindings by role, including exact artifact/snapshot references or explicitly limited source descriptors and selectors | Make the supplied material traceable without assuming one file per case or pretending missing bytes were captured |
| C4 | Applicable domain/schema contracts, coordinate/identity mappings and their established interpretation or gaps | Preserve variable, time, group, relational and learned-representation meaning instead of inferring it from array shape |
| C5 | Origin and known lineage/overlap relations, with scope and basis; explicitly bounded knowledge when lineage is incomplete | Distinguish reuse, derivation, independent generation claims and possible shared evidence |
| C6 | Definition/revision history, change reason and affected scope; no silently mutable prior revision | Preserve the exact evidence interpretation used by an earlier study |
| C7 | Scoped evidence inventory/extent, availability/access observations, exposure provenance and limitations | Distinguish what was enumerated, captured, restricted or previously exposed; avoid false completeness or blindness claims |

Responsibilities may be satisfied by shared references rather than copying all
metadata into every case. A first revision needs no fictitious predecessor.
An unknown original case can have a known current preservation identity; that
does not establish native identity or permit an unresolved association to be
silently used as a matched scientific case.

Case attributes and assumptions must state their scope and basis. Do not force
sample count, exact causal truth, a global graph, iid sampling or a known generator
onto every family. Distinguish variable count, row count, time points, environments,
subjects and other quantities with their units/roles. Algorithm/model configuration,
task targets, allowed information and evaluation references have their separate
bindings; they are not all intrinsic case properties.

Availability changes can be later observations without rewriting the case. A
change to the case definition gets a new revision. New scientific realizations
or scope changes require their proper new/derived identities, not a correction
label chosen merely to keep the previous ID. Identity mappings and equivalence
claims must state the meaning preserved, procedure and evidence; different bytes
or equal dimensions do not settle scientific equivalence.

## 4. Conditional semantic coverage across the capability map

The common foundation is mandatory. Additional obligations follow from the actual
case family and intended use, never from a dispatch rule naming a system. Unsupported
extensions remain preservable as identified evidence with an interpretation gap;
they do not acquire executable or scientific support from an opaque payload.

| Map cases | Relevant case obligations; details may be referenced |
|---|---|
| C01, C03-C04, C07, C09 | Identified observed-variable domains, sample schema and relevant masks/representation; input properties remain separate from an algorithm's requested assumptions/output family |
| C05-C06 | Sufficient-statistic meaning, axes, sample-size meaning or scoped CI-answer source/interface contract; do not fabricate raw samples |
| C02, C08, C10-C11 | Group/environment identity, separate data scopes, intervention assignments/targets as known, and whether targets are hidden or uncertain; do not flatten distinct environments |
| C12-C14 | Time coordinates, units, ordering, window boundaries and source/subject overlap; multiple series retain identities |
| C15 | Evidence and domain bindings used by a posterior-producing task; graph particles/weights belong to returned S1 objects, not invented input cases |
| C16-C17 | Evidence/domain needed by pairwise or local tasks; task targets and output coverage are bound separately, without requiring a full truth graph |
| C18-C19 | Raw observations and learned/pretrained representation provenance as applicable; observed/latent/learned identities remain separate, with later evaluator alignments explicitly derived |
| C20 | Relational schema, entity/relationship scope, perspective and relevant selectors; columns alone cannot identify the variables |
| C21-C22 | Bounded simulator/expert/interaction source and applicable state/access contract; actual questions/actions/responses are subsequent evidence, not assumed pre-existing rows |
| C23 | Partition/site identities and permitted evidence boundaries; central possession of raw data is not required or implied |
| C24 | Stream/source identity, window/checkpoint constraints and state lineage where known; no implied stationary or identical replay |
| C25-C28 | Names/context/file evidence and source/version bindings as actually present; numerical data, stage history and knowledge use are not assumed from a system label |

This is an obligation mapping to all 28 existing representative cases, not proof
of 28 implemented integrations or universal future coverage. New families add
versioned contracts where a faithful existing contract is insufficient. All 18
capability axes still need review across their owning S1/S2 and later subsystems;
the case catalog alone does not implement the rest of the map.

For a live source, freeze what can genuinely be fixed: source/interface identity,
state constraints, bounded access/window and referenced protocol. Bind subsequent
realization receipts before evaluating their results. If exact state restoration
or sample identity cannot be established, report that limitation. A scientific
question about a live source can still be meaningful; it cannot claim identical
input replay or matched realized samples without evidence.

## 5. Collection release and membership

| ID | Collection-release responsibility | Failure it prevents |
|---|---|---|
| R1 | Collection identity, exact immutable release and authoring provenance | Changing a population while retaining an apparently fixed label |
| R2 | Declared collection purpose/scope and explicit enumeration extent | Mistaking an imported fragment for the whole historical study |
| R3 | Exact member entries or authorized restricted references/commitments, pinned to case revisions | A moving latest pointer or public metadata dump that changes or leaks the population |
| R4 | Source-pool identity, inclusion/exclusion/selection procedure and its timing/basis, or scoped reconstruction gaps | Claiming random or before-results selection without its evidence |
| R5 | Ordered/unordered, duplicate and selection-slot semantics, plus relevant selection strata; do not infer analysis weights or independence | Counting duplicate selections as independent evidence or confusing listing order with execution randomization |
| R6 | Release history and scoped disclosure/access/exposure evidence, including limits | Overwriting earlier populations or treating a sealed label as proof of isolation |

| ID | Membership-entry responsibility | Failure it prevents |
|---|---|---|
| M1 | Entry identity and containing release, using a packaging/reference convention that avoids circular identity definitions | Unresolvable or ambiguous membership |
| M2 | Exact case revision, or explicit unresolved association in a preservation/reconstruction record | Joining an old result to the wrong current case |
| M3 | Inclusion role in this collection and source selection event/rule, or an honest historical gap | Treating a pilot, regression example or deliberately selected stress case as an unseen random test |
| M4 | Applicable declared stratum/slot/multiplicity and links to earlier selections or source reuse | Concealing resampling, duplication or repeated exposure |
| M5 | Basis for membership and selection claims, with extent/timing and corrections retained | Inventing an original selection history at import time |

A membership explanation can be a reference to the common rule plus evidence that
it applies; it need not be a repetitive paragraph. A current reconstruction may
explain why it includes an artifact without claiming to know the original author's
motivation. Collection role remains separate from exposure facts.

A planned collection cannot drop cases because outputs later failed. Eligibility,
attempted/completed coverage and metric-specific scoreability are separate bound
populations. An experiment referencing a partially reconstructed collection can
study its declared known subset; it cannot claim the unknown original population
was completely captured or sampled representatively.

For generated or adaptive membership, distinguish the committed generation/selection
rule from the realized collection release. The rule binds source/version, policy,
seed commitments where relevant, stopping/budget constraints and timing; its later
realized member list is separately recorded with provenance. A seed alone is not
the collection. Do not retroactively describe the later list as enumerated before
it existed. Sequential policy design will be handled in its owning S2 areas.

Restricted/sealed references may hide sensitive identifiers and counts under the
adopted policy. Traceability means resolvability by the authorized evaluator and
an honest public claim scope, not disclosure of all private material. No actual
sealed store, seeds or permissions are accessed or altered here.

## 6. Concrete design checks and their claim limits

| Example | What the record can establish | What remains unestablished |
|---|---|---|
| A fully captured synthetic dataset, fixed generation procedure and 30 planned entries from ten cases | Exact evidence bindings, ten case revisions and explicitly related selection/trial roles | Thirty independent datasets; correct generator assumptions merely because a seed is recorded |
| An old graph and CSV with no reliable original case ID or selection plan | Current artifact identity, known content and an explicitly provisional source association | Original request, representative sampling, prospective registration or matched pairing |
| Two overlapping time windows from one participant | Distinct case scopes, shared source identity and overlap evidence | Statistical independence just because two window IDs exist |
| An external callback with no replayable state | Identified access contract and later captured query/answer receipts at their actual scope | Identical answers on retry or proof of a fixed unseen underlying dataset |
| A public development case later assigned a confirmation role | The new intended role and the earlier exposure | A restored unseen/isolated status |
| Three failures among twenty selected cases | Twenty intended members plus later completion/scoreability evidence | A silently rewritten seventeen-case original selection |

These are design walkthroughs and future acceptance obligations, not tests run or
empirical findings. For the first example, experiment trial slots need not be
duplicated as collection entries: their ownership and multiplicity must be explicit.

## 7. Traceable contribution to coverage

For each claimed capability/control, the eventual plan should connect:

    requirement/question
      -> applicable semantic family and assumptions
      -> selected cases/revisions and reason for selection
      -> declared contrast/reference and required evidence
      -> validation criterion and actual validation evidence
      -> scoped result or explicit gap

Distinguish designed representation coverage, implemented interpretation coverage,
native integration coverage, auditor-validation coverage and scientific finding
coverage. None is a replacement for the others. Unique case count, membership
count, successful executions and independent analysis units are separate counts.
Define a denominator before reporting a coverage percentage; an extensible space
of possible systems has no justified universal finite denominator.

A repeated case can test a new condition, reproducibility or output variability.
Record that purpose and dependence. A difficult/inconclusive case can establish a
limitation. Do not exclude either merely to improve a coverage number. Extra cases
with no stated role should not inflate claims about tested capabilities.

## 8. Tradeoffs and status

The proposed common foundation plus conditional semantic obligations costs more
explicit references, contracts and validation work than a fixed table-and-graph
record. It prevents silent loss of temporal, intervention, distributed or interactive
meaning. Requiring every family-specific field on every case would instead create
irrelevant defaults and false meaning. An unrestricted metadata bag would preserve
bytes but leave interpretation and scientific use unjustified.

Separating preservation from use-specific readiness retains incomplete historical
evidence while withholding stronger claims. Rejecting all incomplete evidence would
lose useful history; accepting it as fully comparable would manufacture certainty.
Neither a blank field nor a fully populated record demonstrates scientific rigor.

These records remain proposed. Existing Item/Battery behavior, S1 runtime and all
stored numbers/certificates are unchanged. No serialization, API, sealed policy,
analysis denominator or public paper contract has been adopted by this note.

## Where we're going

Review the C/R/M responsibilities and scoped unknown handling, then test them with
complete prospective, historical and live-source examples. Develop task/reference
binding next, including what a reference asserts, its version/coverage/assumptions
and evaluator-only boundary. Reconcile those pieces before serialization or any
implementation plan. Keep the methodology index current as decisions are accepted.
