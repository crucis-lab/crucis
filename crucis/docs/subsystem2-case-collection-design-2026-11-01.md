# Subsystem 2: case identity and collection membership

Tickets: DLV-08, DLV-09; related DLV-10, DLV-06/07 and ADV-01.
Date: 1 Nov 2026, America/Los_Angeles.
Status: first focused design proposal. The user authorized this discussion and
documentation, not implementation or the particular decisions proposed below.
No schema, identifier syntax, task contract or public protocol is frozen here.

Sources: [S2 structure](subsystem2-structure-design-2026-11-01.md),
[methodology index](methodology-reference-index-2026-11-01.md),
[S1 contract](system-connections-contract-outline-2026-11-01.md),
`audit/core/battery.py` and the previously verified
[historical cohort rebase](project/w2-rebase-2026-10-31.md).

## 1. What this part must establish

Identify the evidence situation being studied, bind its exact definition, and
record why it is included in a particular collection. Preserve relationships
without assuming independence, pairing, scientific equivalence or eligibility.

This is independent of an eventual system request. A case can support global
discovery, a local question or another supported task, subject to the task's own
requirements. It need not consist of a matrix and truth DAG. It might describe
several intervention datasets, a time-series window, relational evidence, a
model/simulator state or a bounded interactive source. Such cases still need
explicit evidence/domain boundaries. A source recipe does not establish that
its data have been generated or delivered.

S1 already supplies domains, artifacts, mappings and request/attempt identities.
S2 should reference those contracts rather than invent parallel file hashing,
variable mapping or execution records. Cataloging a case does not execute it,
score it, reveal its references to a system or claim its evidence is available.

## 2. Proposed concepts

| Concept | Meaning | What it does not establish |
|---|---|---|
| Case | A stable, source-scoped identity for one declared evidence situation | A filename, complete truth graph, particular task or independent statistical unit |
| Case revision | An immutable definition of that case: its evidence/domain bindings, origin and stated limits | That files still exist, that every source claim is true, or that a changed realization is merely a correction |
| Collection release | An immutable version of a collection's declared membership and selection description | A scientific experiment, a public release, or a population inferred from successful outputs |
| Membership entry | An identified inclusion of an exact case revision in that release, with its role and selection information | A new case, new model draw or independent observation |

A collection can have a stable logical name across releases. New releases retain
their predecessors. Each membership binds an exact case revision, not a moving
"latest" reference. Equal collection contents do not automatically merge distinct
declarations or erase how they were selected.

Names are explanatory labels; scoped IDs identify catalog entities; content hashes
check the specified content/representation. None substitutes for the other two.
Source IDs retain their publisher/release scope so that two publishers' "case 17"
cannot silently collide. A source-scoped alias or equivalence claim needs evidence.

## 3. Running example and identity boundaries

Use an illustrative scenario S, with a fixed set of causal mechanisms. It produces
dataset realization A. The case binds A's specified evidence situation; S is an
optional source/lineage identity, not the case's universal meaning.

| Event | Proposed identity treatment | Reason |
|---|---|---|
| Copy A or move its file | Same case/revision when its bindings remain satisfied; new location/availability evidence as needed | Storage location does not create a scientific replicate |
| Rewrite CSV as another format | Preserve the case association only with an evidenced conversion/mapping; represent the new encoding explicitly | Different byte hashes do not prove different scientific content, nor does equal shape prove equivalence |
| Present A with neutral/swapped labels or reordered variables | Same source case, distinct condition and presentation/materialization identities | The experiment changes what the system sees without pretending to sample a new dataset |
| Draw B afresh from S | A distinct case when registered as a distinct evidence realization, linked to S and any shared sources | Common mechanisms do not make realized data identical or draws statistically independent by themselves |
| Subsample A for a condition | Same planned source case with a derived evidence object and explicit row-selection lineage | Reduced data are not byte-identical, and a subset is not a fresh independent dataset |
| Catalog that subset for reuse as a standalone case | An explicitly registered derived case, linked to A and the selection procedure | Reuse must retain overlap/dependence instead of manufacturing a new independent source |
| Correct a mistaken domain/evidence binding | New case revision with correction basis; preserve old membership bindings | An old experiment must remain reconstructible |
| Correct only the evaluator's reference graph | New reference version and later task/evaluation binding; do not automatically change the evidence case | Scoring evidence and system inputs have separate identities; if case-defining content also changes, revise that part explicitly |
| Ask a new local target question about A | New task/request binding to the same case, if compatible | Case identity should not be duplicated for each question |
| Retry a failed execution or restart from a checkpoint | Same case; S1/S3 retain distinct attempts and explicit continuation relationships | Attempt count is not dataset count |

The same artifact can support more than one case situation (for example overlapping
time windows or different scoped populations). Their scope selectors and shared
source relationships must be explicit. Conversely, one case may require many
artifacts. There is no universal case-equals-one-file rule.

Changing task/input scope can require a new scoped or derived case. A deliberate
new condition, data realization or population must not be disguised as a corrective
revision to keep a favorable ID. The declared change and evidence determine the
relationship; a checksum cannot make that scientific decision.

## 4. Membership is study context, not case identity

A single case revision may belong to a pricing-pilot collection, a development
collection and a later reproduction collection. Its role in each collection is
separate from its identity. Prior exposure stays recorded; a later "held-out" or
"sealed" role cannot erase earlier public access or pilot use.

Membership should establish: its containing release, exact case revision, inclusion
role, selection basis and any declared stratum/slot/multiplicity semantics. These
are conceptual obligations, not frozen JSON fields. Order is explicit when it has
meaning. A stable listing order is not automatically randomized execution order.
Scientific repetition, weighting and analysis clusters belong to the corresponding
experiment/analysis contracts; membership may reference them but cannot imply them.

If the same case is selected twice, the release must either reject an unintended
duplicate or preserve two explicitly meaningful selection slots. Neither treatment
can turn one source case into two independent cases. Deliberate resampling or
sampling with replacement needs its own declared procedure and slot relationships.

Adding/removing a member, changing its pinned revision, or correcting membership
metadata produces a new release. Do not edit a frozen list in place. An experiment
pins the release and declares eligible subsets; it cannot quietly replace that
population with whatever outputs happened to arrive.

Collection membership is not the same as eligibility. A selected case can later
have an unsupported task, missing adapter route, inaccessible artifact or failed
execution. Retain its intended inclusion and report the relevant reason at the
proper boundary. Different systems may have different eligible sets; the plan
must account for that before making a common-cohort claim.

## 5. Selection, dependence and historical reconstruction

For a new collection, retain the source-pool release/commitment, selection rule,
criteria/strata, randomization procedure where applicable, and explicit resulting
members. Bind timing/evidence without inventing preregistration. A full sampling
frame may be restricted or unknown; record that limit. A seed without the pool,
procedure, ordering and versions does not fully describe selection.

Distinguish four relations:

- Same case revision: the same catalog definition is reused.
- Shared source/scenario/subject: cases may have related or overlapping evidence.
- Planned pairing: a particular comparison explicitly connects members.
- Analysis dependence: an analysis declares the appropriate clustering/unit rules.

No one relation establishes all the others. Patient groups, sites, time windows,
mechanism families and overlapping samples can require more than one grouping.
Cases can record known source relations; analysis chooses and justifies the
appropriate dependence handling. Unknown dependence remains unknown.

The existing ca-ab06 and q1s2 collections each contain ten scenarios but have zero
shared scenarios according to the prior rebase checks. Their similar arms do not
make them paired. A new shared cohort must list actual common eligible identities.
For the proposed Q1 study, "20 cases" remains a planning count until a release with
twenty explicitly selected members and their source relationships is frozen.

For a historical import, create current catalog/import identities and preserve
known source aliases, hashes, timestamps and membership evidence. If the original
selection rule or case association is not established, say so. Do not manufacture
original IDs, independence, random selection or a before-results commitment. An
unresolved case association can still be preserved through S1 evidence records;
it cannot enter a claimed matched comparison without enough association evidence.

## 6. Alternatives and costs

| Proposed direction | Strongest simpler alternative | Cost and failure mode |
|---|---|---|
| Stable case identity plus immutable revisions | Use content hash as the whole identity | Extra lineage/version relations; avoids treating format changes as new cases or equal bytes as independent occurrences |
| Reusable case catalog plus explicit membership | Self-contained battery copies for every study | More references to resolve; avoids case duplication and hidden changes in membership or study role |
| Task/reference bindings separate from case evidence | One matrix/truth-graph record | More explicit bindings; supports local/temporal/graphless cases and reference corrections without rewriting source identity |
| Frozen releases plus explicit selection history | Recompute a live directory glob when needed | Release creation/storage overhead; prevents silently changed cohorts and lost selection intent |
| Explicit grouping, duplicate and overlap relations | Assume each list row is independent | Additional declarations and sometimes lower effective sample size; prevents inflated precision and concealed reuse |

The long-term generic core should implement common identity, revision, membership,
provenance and reference-resolution rules. A native adapter translates source
identifiers and representation details; it does not decide scientific independence,
selection roles or case pairing from a system name. Small ordinary cases should
still be expressible with a compact record and references to shared definitions.

## 7. What already exists and what remains a proposal

`audit/core/battery.py` already has item IDs, scenario clusters, family, files,
references, arms and metadata. It rejects duplicate item IDs within a Battery and
hashes a manifest including file digests. These are useful foundations.

It currently mixes case and experiment details: arms/references live on Item;
builders select members from plans, datasets or benchmark files. Its cached hash
and mutable member list are not an immutable release lifecycle. `Item.n` currently
means variable count, not general sample count. The source was inspected, not
changed or executed during this discussion.

Separate generic case/revision/membership records, frozen release behavior and
the legacy mapping are proposed new design, not implemented features. S1's
domains/artifacts are implemented reusable building blocks, not an already built
S2 collection manager. Task/reference binding is the next topic and may refine
these boundaries before any serialization freeze.

Future acceptance examples should show stable identity after moving evidence,
visible new revisions/releases after corrections, retained source overlap after
derivation, no fabricated historical intent, and no denominator change when a
selected case fails. These are design requirements, not newly run tests.

## Where we're going

Review the case/revision/release/membership distinction using these examples. Next
resolve the smallest required identity/selection information, unknowns and relation
types, then develop task/reference binding and test the two designs together.
Keep numerical scoring, execution policy, schema/API freeze and implementation out
of this pass. No real sealed material, shared scientific code or public contracts
have been changed.
