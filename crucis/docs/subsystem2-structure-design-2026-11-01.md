# Subsystem 2: test collections and experiment definitions

Tickets: DLV-08, DLV-09; related DLV-10, DLV-06/07, ADV-01.
Date: 1 Nov 2026, America/Los_Angeles.
Status: opening design proposal and source inspection. No subsystem-2 implementation,
contract freeze, native execution, sealed access or public protocol adoption.
Methodology entry point: [reference/evidence index](methodology-reference-index-2026-11-01.md).

## 1. Responsibility

Subsystem 2 states the scientific experiment before its observed outcomes are used
to decide how to analyze it. It identifies the cases, task, conditions, allowed
information, transformations, requested responses and intended comparisons. For a
historical import it can describe evidenced intent, with gaps where the original
plan or timing is unavailable. Such reconstruction is not preregistration.

Subsystem 1 supplies the connection language: domains, artifacts, requests,
presentations, outputs and observations. Subsystem 2 defines their experimental
meaning and relations. Subsystem 3 will execute the declared plan and enforce its
operational policies. Subsystem 4 computes referenced measurements/statistics;
subsystem 5 applies finding rules; subsystem 6 reports/certifies them. Subsystem 7
tests the auditor itself. Their detailed designs remain outside this document.

An experiment definition may bind adopted measurement/finding contracts and specify
an analysis population or scientific resource constraint. It does not implement
scoring, tune a threshold, choose undeclared retries or schedule native work.

## 2. Guiding principles proposed for subsystem 2

1. **Faithful question and scope.** Declare what comparison is intended, what is
   actually varied, and what evidence can answer it. Retain native task/output
   meaning, including local, temporal, learned-variable and interactive tasks.
2. **Generic core, explicit prerequisites.** Common definitions describe cases,
   conditions, dependencies, transformations and comparisons. Native-specific
   presentation details live at explicit bindings; no system-name dispatch in the
   scientific rules. Unsupported input transformations get an eligibility gap.
3. **Case content and experimental role are distinct.** A case can appear in more
   than one study. A content digest does not establish case lineage, pairing or an
   independent replicate. A folder or family label does not establish a common cohort.
4. **Information boundaries are explicit.** Separate what the system may receive
   from evaluator references, private metadata and analysis-only alignments. Any
   oracle control is an expressly permitted information channel. Intended/permitted
   information remains distinct from S1's observed delivery/access/use evidence.
5. **Controlled changes have checkable invariants.** Record both changed properties
   and properties that must be preserved. Specify exact-byte equality only where
   claimed; numerical or scientific equivalence needs its own stated procedure.
6. **Sampling and pairing are planned.** Distinguish scenarios, datasets, subjects,
   time windows, scientific trials, native attempts, output draws and resampling
   clusters. Repeated attempts do not automatically increase independent sample size.
7. **Missingness and eligibility remain visible.** Separate unsupported scientific
   tasks, missing adapter support, unavailable resources, insufficient references,
   planned omissions and observed failures. Do not silently discard inconvenient
   cases, invent an empty graph or modify the comparison after seeing outcomes.
8. **Versioned intent with an amendment history.** Bind case selection, generators,
   transformation procedures, configuration, randomization roles and analysis-rule
   references. Adaptive designs may specify a bounded decision procedure in advance;
   actual decisions are subsequent evidence. Changes retain timing and rationale.
9. **Honest evidence and claim labels.** Record assumptions, reference limitations,
   exposure history and what is unknown. A checksum is an identity/integrity aid,
   not proof that references were correct or sealed information remained unseen.

These apply the user's accepted principles to subsystem 2; their precise contracts
and particular defaults below remain proposals for discussion.

## 3. Proposed overall structure

The seven areas below are design responsibilities, not implementation bundles or
frozen serialization blocks. They can share records and references.

| Area | What it needs to define | Connection to neighbouring subsystems |
|---|---|---|
| Case catalog and collection release | Case identities/lineage, domain and evidence, population, explicit membership/selection, public/private release identity | Uses S1 artifacts/domains; collection membership does not itself select a task |
| Task and reference specification | Scientific question, requested response/scope, available references, tiers, assumptions and reference coverage | Binds S1 request/deliverables; supplies evaluator-only evidence to measurement |
| Conditions and information policy | Meaning of each arm, fixed versus varied factors, allowed channels/context/knowledge, supplied resource constraints | Becomes explicit S1 presentations/policies; S3 records actual use and enforcement |
| Transformations and randomization | Source-to-derived lineage, invariant checks, native representation prerequisites, ordering, randomization roles/procedures | Reuses S1 mappings without assuming identity after arbitrary feature changes |
| Comparison and repetition structure | Contrast direction, paired members, trial/repetition identities, native variants versus external reruns, grouping/dependence, analysis contract refs | S3 produces attempts; S4 performs the declared analysis with explicit units |
| Eligibility and incomplete coverage | Operation/adapter/reference prerequisites, intended analysis populations, treatment of missing arms/outputs, visible reasons and denominators | Uses S1 declarations/checks; observed execution failure remains S1/S3 evidence |
| Plan commitment and controlled release | Plan/version identity, temporal evidence, amendments, development/sealed policy, permissions and release limits | References authority and S3 enforcement; carries metadata for later claim labels |

Proposed conceptual handoff: case/reference selection plus a versioned experiment
definition and explicit per-system bindings. It should make each requested evaluation
traceable to a case, condition, request, presentation recipe and comparison membership.
It need not flatten an adaptive or sequential experiment into a Cartesian grid.
Its exact field names and materialization boundary are intentionally not frozen.

## 4. What is already built and inspected

| Source | Existing behavior | Boundary or gap for the broader design |
|---|---|---|
| `audit/core/battery.py` | Item IDs, scenario cluster, family, file/reference roles and tiers, arms, metadata; manifests/hash; four registered development battery builders | Dataset/graph-oriented. Collection and arm metadata carry study choices; no independent generic experiment-plan contract |
| `audit/core/harness.py` | Seeded shown order, name/context/file-label presentation, mapping graphs/variants/edge-source/stages to original positions | Requires unique shown names; legacy confidence is not mapped here; presentation helper is tailored to CausalArena arrays |
| `audit/controls/transforms.py` | Recorded/generated name maps, column/path changes, subsampling, noise and knowledge suppliers | Useful implementations with particular data assumptions; declaring a transform is not proof it preserves the intended task for arbitrary evidence types |
| `audit/protocol/regimes.py` | Current offered-input regime rules, knowledge-source labels and cross-regime ranking refusal | Coarse categories cannot replace exact channel/content/context bindings; keep existing semantics unchanged during design |
| `audit/protocol/tiers.py` | T1 exact, T2 contested, T3 provenance-only and T4 deliberately mismatched reference categories | Broader local/order/model tasks need explicit reference meaning and coverage, not automatically a full truth graph |
| `audit/run.py` | Standard audit definitions choose system, battery, arms, stage/source/metric options and historical run dates | Several experiment choices are constants/dictionaries or `extra` fields rather than a separately versioned scientific plan |
| `audit/collect.py` | Reads recorded item/arm combinations; skips arms not listed by an item; scores final/variant outputs as supported | Intended membership and actual observed/scoreable membership must become distinguishable; collector does not execute live/replay modes |
| `audit/controls/l1.py`, `effects.py` | Current name/layout/data-only contrasts, successful/available run selection, common-unit pairing and scenario-cluster analysis; calls shared score code | Establish historical behavior, not universal analysis defaults. S2 should bind analysis sets and rule refs; S4 owns calculation |
| `audit/core/sealed.py` | External-store guard, public commitments, regeneration/hash checks, read eligibility/recording helpers and aggregate filtering | Existing helpers/tests are not proof of an operationally isolated production sealed evaluation |
| `audit/__main__.py` | Recorded audit commands and `sealed-check` eligibility query | No `sealed-read` command is registered here, despite the broader protocol describing that workflow |

Inspected tests: `tests/test_audit_core.py` (battery identity, regimes, presentation,
recorded adapter conformance), `test_audit_controls.py` (transform invariants,
recorded maps, paired effects and stored MATMCD results), and `test_audit_report.py`
(sealed-store/one-read/rotation rules, synthetic commit/check and aggregate filtering).
These were part of S1's final passing legacy suite. They were inspected without
rerunning them during this design pass.
The sealed tests use controlled dummy data; no real seed store was opened.

Concrete seams to carry into the design deep dives:

- `Item.n` is populated from the variable count in current builders. It is not a
  general observation/sample count. New contracts need separate named quantities.
- `Battery.hash()` caches its first computed value while `Battery.items` is a mutable
  list. A frozen release and later actual-input rechecks need explicit lifecycle
  rules; the current cache is not continuous tamper detection. No existing code is
  changed in this pass.
- Current pairing intersects available units and some analyses require successful
  final runs. A future plan must name the question/analysis set and account for
  unavailable units; historical rules remain preserved as such.
- Existing regime tags describe a specific convention. Neutral labels do not prove
  the absence of all information from context, metadata or pretrained components.
- The earlier rebase found no scenario overlap between ca-ab06 and q1s2. Similar
  family names and arm labels do not make their results paired or their scores a
  common-cohort comparison. See the existing rebase/facts evidence; no new overlap
  computation or data access was performed here.

## 5. Opening design choices and tradeoffs

All recommendations in this table are proposed, not decisions attributed to Uzair.

| Choice | Proposed direction | Strongest alternative and cost | Failure mode prevented |
|---|---|---|---|
| Collection versus experiment | Reusable frozen collection plus separate versioned experiment definition, with shared refs | One self-contained battery per study is simpler to read, but repeats data identity and entangles case reuse with changed questions | Reusing an ID while changing the study, or duplicating cases into apparently independent populations |
| Meaning of a case | Task-independent evidence/domain identity; task/reference binding is explicit | One case equals one matrix plus truth graph is convenient for present baselines but narrower than S1's supported native outputs | Excluding graphless/local/interactive systems or inventing unsuitable truth graphs |
| Cross-system comparability | Common question/cohort with explicit information, resource and output requirements; record eligibility limits | Let every system use its best native setup: useful for a declared native-performance question, but requires careful qualifications and separate information profiles | Unqualified rankings across different inputs, populations or resource conditions |
| Experimental layout | Explicit factors/contrasts with validation of intended membership; allow bounded sequential/adaptive designs | A fixed Cartesian arm grid is simpler to enumerate/test, but forces awkward or misleading representations of adaptive tasks | Hidden confounding, invented static arms or accidental missing combinations |
| Transform contract | Declared changes, invariants, variable/value mappings and exact procedure/source identity | A seeded transform function is faster to integrate but leaves preservation assumptions implicit | Changing data, leakage or task meaning while claiming that only names/order changed |
| Analysis populations and retries | Predeclare trial/pair/group roles and missing-output treatment; later observations show actual coverage | Available complete pairs simplify historical comparison, but must be labeled and accompanied by completion/coverage reporting | Survivor selection, silent denominator changes or counting transport retries as independent trials |
| Commitment and adaptation | Immutable plan releases plus timed amendments and explicit adaptive policies | Editable configuration offers flexibility but makes original intent and post-outcome changes hard to distinguish | Retroactive preregistration and outcome-driven protocol changes hidden as routine edits |
| Sealed information | Preserve existing owner-controlled policy; distinguish public descriptors, restricted artifacts and release authority | Full case-level publication eases reproducibility for development data but can invalidate an intended unseen evaluation | Treating a metadata label or a local folder boundary as evidence of blindness |

Exact eligibility vocabularies, version rules, randomization schedules, mandatory
profiles and analysis policies remain open. No new finding verdict, threshold,
sealed-read allowance or historical denominator is adopted by these proposals.

## 6. Running example for the next discussion

A name-sensitivity study starts with identified cases. The plan specifies the
requested discovery/local task, the real/neutral/swapped-name conditions, exact
context and other permitted information, and the variable correspondence between
those conditions. It states which data values/rows/masks must remain fixed and
which presented labels may change. Any shared column permutation is a distinct
controlled factor with an explicit mapping.

Comparison definitions then identify which case/condition outputs form each
contrast, what counts as a scientific repeat, the grouping/dependence structure,
the referenced measurement and what happens if one arm is unavailable. Reference
graphs/labels stay evaluator-side unless a distinct oracle condition authorizes
their delivery. If one system cannot accept samples, its information profile and
the question that remains comparable must be made explicit.

S1 records requests/presentations and returned evidence. S3 will manage permitted
execution and attempts. S4 will compute the planned contrasts. This example is a
design walkthrough, not a new executed study, accepted analysis or preregistration.

## 7. Design sequence and methodology record

First review responsibility boundaries, principles and the overall areas above.
Next deep-dive case/collection identity and membership with concrete examples,
followed by tasks/references, conditions and information, transformations and
randomization, comparisons/repetitions/missingness, then commitment and eligibility.
Revisit interacting choices together rather than freezing names before meanings.

For each decision retain alternatives, rationale, cost, prevented failure mode,
acceptance evidence needed, approval status and a link to affected contracts.
Later compose complete example plans to expose gaps, settle bounded serialization/
API and compatibility contracts, perform final subsystem-2 design review, and only
then propose implementation bundles and gates. No such implementation is authorized.

## Where we're going

Discuss this structure and its tradeoffs with Uzair, then begin the first bounded
deep dive: what constitutes a case and a collection release, including reused data,
changed references, derived conditions and historical imports. The next step remains
design only. Public protocol, W1/W5 files, S1 runtime, existing batteries/results,
real sealed material and shared scientific logic are unchanged.
