# W2 design rebase: system connections after the eight-block walkthrough (1 Nov 2026)

Tickets: DLV-08, DLV-09, DLV-10; neighbours DLV-06/07/11, ADV-01, BLD-15.
Phase: design iteration. No implementation go or shared-contract adoption has been given.
This additive rebase records the current conversation state. It supplements the original STATE/kickoff and
31 Oct rebase; it does not replace their ownership, no-spend, protected-file or green-gate requirements.

## 1. Where we are now

The existing v1 package B1-B5 and stored audits remain the runtime baseline. In this continuation, the new
work is design documentation. We have not implemented the broader record, changed protocol/thresholds,
migrated stored outputs, written a port map or modified W1/W5/shared scoring files.

Uzair chose a slow, incremental process: agree principles and subsystem boundaries, deeply design one
subsystem, agree its acceptance criteria, then implement/test it only after an explicit go. The work is
currently on **system connections**, the first of seven subsystems. Its eight common-record blocks are
parts of that subsystem, not eight of the seven overall subsystems.

Block 7's boundary has been accepted. Block 8 has now been proposed and worked through in a dated document;
it is not yet accepted merely because Uzair asked to discuss it. Completion of the walkthrough is not a
complete implementation-ready specification or final design approval.

## 2. Accepted architectural directions

The user's explicit messages establish these directions:

- Faithful evaluation is the first constraint. Preserve inputs, native meanings, ambiguity, failures,
  provenance and uncertainty; do not manufacture convenient outputs.
- Aim for a system-independent core whose reusable capabilities grow, making adapters progressively
  thinner. A shared feature needs a general contract and checks, not branches named for individual systems.
- Use the capability-space map rather than freezing the interface around the current eight adapters.
- Preserve broader native results. A successful response does not universally require a point graph.
- Separate execution completion, delivered response, requested fulfillment, scoped capture, faithful
  interpretation, evaluation readiness and scientific correctness.
- Keep request, native attempt and observation/import identities distinct in the architectural model.
  Explicitly accepted detail: a checkpoint restart is a new attempt with an evidenced continuation link.
- Keep intended bindings, native declarations, observed execution/input evidence and unknowns distinct.
- Preserve source observations, scoped gaps and versioned outcome assessments with their evidence history.
- Use an output-object index with semantic contracts and typed relationships among native outputs,
  standardized interpretations and derived views. Producer, role and derivation are separate questions.
- Separate artifact identity, location, observer/time-scoped availability and integrity checks.

Acceptance of boundaries is not adoption of every proposed field, enum, type, relation or ID-generation rule.
The named details still require consolidation and explicit review. The v1 protocol and historical contracts
remain as built until changes are adopted through W5.

## 3. The current architecture in plain language

A small common record says which task/attempt is being described, which system and information were intended
and observed, what happened, what outputs are evidenced, and which artifacts/context support those statements.
Optional typed contracts cover richer systems without burdening simple ones.

Native evidence, standardized interpretation, additional derived views and scientific evaluation remain
separate layers. A copied artifact or a new parser does not create another native run. A partial result can
survive a failed/capped attempt. A final response can include abstention or unresolved structure. A new
assessment can correct an earlier interpretation without overwriting the old evidence or published basis.

| Common block | Boundary and review status |
|---|---|
| 1. Record identity/version | Walkthrough reviewed; distinguishes occurrences, observations and content. Exact IDs/version mechanics still open. |
| 2. Request/task | Walkthrough reviewed; prospective intent and completion/scope bind outcomes. Required/resolved fields still need specification. |
| 3. System/connection identity | Boundary accepted; native subject/configuration/state versus execution and interpretation roles. |
| 4. Presented information | Boundary accepted; intended/allowed/presented/accessed/inferred-use evidence stays distinct. |
| 5. Outcome observations | Boundary accepted; observations, gaps and versioned assessments, with conflict/update provenance. |
| 6. Output index | Boundary accepted; typed objects, scope, producer, evidence and relationships; views do not replace native outputs. |
| 7. Artifacts/evidence | Boundary accepted; snapshots, locations, availability and scoped integrity claims. |
| 8. Conditional relationships | Proposed now; sessions, recovery/state, interactions, resources and limitations index the relevant records without duplicating their ownership. |

The capability map contains 18 axes, 28 representative cases and four constructed combination cases. Those
are design coverage examples, not implemented integrations or executed validation tests. Carrying an opaque
native artifact, faithfully interpreting a semantic type, executing a system, evaluating it and validating
that path remain separate support claims.

## 4. What remains before final review of system connections

The next review target is the **system-connections subsystem**, in keeping with the incremental process.
The overall auditor will still need later subsystem reviews. These remaining work products should be bounded
and concrete rather than more parallel narrative documents:

| Remaining work | Reviewable output | Why it is needed |
|---|---|---|
| Settle Block 8 and consolidate terminology | One current contract outline, glossary and decision log with precedence over superseded sketches. | Prevent contradictory meanings across the discussion history. |
| Fix the minimum common contract | Field/type tables or illustrative records stating required, conditional, referenced and unknown information; version/extension rules. | A walkthrough does not yet define a precise producer/consumer contract. |
| Choose actual support profiles | A feature-by-mode matrix separating native support, adapter access, semantic preservation, evaluation and test evidence for the intended first increment and future extensions. | Broad preservation was accepted, but scope of typed execution/evaluation is not automatically universal. |
| Define the necessary semantic family contracts | Precise variable/coordinate, graph/claim/collection/quantity/artifact/relation meanings for selected profiles, with honest extension handling for others. | A generic envelope cannot replace payload semantics. Exact family scope still needs Uzair's decision. |
| Specify adapter/core interactions | How identity/presentation/recorded import/direct calls/command-only routes and optional sessions are described; who owns each invariant. | Keep adapters thin without promising modes that cannot execute. Execution policy remains owned by its later subsystem. |
| Walk complete representative records | End-to-end design examples for a simple graph, uncertain/partial result, related objects, continuation/import, interaction and missing/conflicting evidence. | Check that blocks compose and the minimum case stays small. |
| Agree acceptance and compatibility plan | Concrete future conformance obligations, existing-audit parity/certificate requirements, dependency conditions and a bounded implementation increment. | Make final approval assessable without writing implementation prematurely. |

The exact ordering of the middle items can follow their dependencies. Do not require implementing every
mapped system or redesigning all other subsystems before the first subsystem can be reviewed. Equally, do not
declare a type supported simply because the envelope can archive it. Adjacent-subsystem interfaces and
unavailable prerequisites must be explicit.

The sensible immediate next step is to consolidate the eight blocks into one precise common-contract outline,
with the unresolved profile/type choices visible. Do not restart the capability survey or repeat agreed
distinctions unless consolidation exposes a genuine inconsistency.

## 5. Consistency issues to resolve in consolidation

- Early result-record sketches combined invocation/import language for attempts. The later identity design
  distinguishes native attempts from observation/import records; use that distinction.
- Response finality, task fulfillment and claim-level abstention are separate dimensions, not one enum.
- A reported artifact can be indexed without pretending bytes or semantic interpretation were captured.
- Native origin and derivation are not opposites: a native system can return its own derived selection.
- Equal content does not merge native occurrences; multiple interpretations do not multiply native runs.
- New attempt identity on checkpoint restart does not select scientific completion/resampling denominators.
- Meaning-preserving interpretation, declared projection, exact-byte integrity and numeric tolerance are
  different contracts. An explicit projection cannot silently satisfy a native-byte or native-claim requirement.
- Earlier single-status/code APIs are baseline compatibility constraints, not silently replaced by new terms.

## 6. What final review should be able to assess

A final system-connections design review should have enough concrete material to answer:

1. Is the minimum ordinary request/result small, precise and usable without irrelevant fields?
2. Are declared versus observed facts, unknowns, errors, abstention, local scope and conflicting evidence
   representable without invented defaults or discarded history?
3. Do selected semantic contracts preserve native meaning and variable mappings, with derived views explicit?
4. Can retry, checkpoint continuation, observer reconnect, planned replication, response replay and historical
   import be distinguished, without hidden counting or resource-policy changes?
5. Do storage/availability/integrity references bind the actual evidence used, including missing/changed files?
6. Can multiple structurally different systems use the same core mechanisms without system-name exceptions?
7. Are support limits, extension/version rules and actual mode readiness explicit and testable?
8. Is the compatibility/migration and future verification plan concrete, including shared-contract adoption?

The result of that review can be acceptance, targeted revision or a narrower explicitly stated first increment.
Final design acceptance still does not mean implementation has already been authorized; Uzair's go remains
the build boundary. No resource-spend authorization follows from design approval.

## 7. Wider subsystem state

| Overall subsystem | Current design-iteration position |
|---|---|
| System connections | Capability map and eight-block walkthrough; consolidation/precise contracts/review remain. |
| Test collections and experiment definitions | Boundary agreed; deeper redesign not yet walked through in this sequence. |
| Execution and collection | Boundary agreed; deeper redesign pending; connection-side requirements exposed. |
| Measurement and attribution | Boundary agreed; deeper redesign pending; existing shared scoring remains untouched. |
| Finding decisions | Boundary agreed; deeper redesign pending; existing K01-K15 semantics and issues remain. |
| Reports and certificates | Boundary agreed; deeper redesign pending; paper compatibility and port gate remain. |
| Auditor validation | Boundary agreed; deeper redesign pending; conformance and finding-detection validation must stay distinct. |

This table describes the redesign discussion, not absence of v1 code. The existing package already implements
parts of all these responsibilities. Broader-system capability needs may inform future designs without
silently expanding claims made by today's metrics or certificates.

## 8. Last verified runtime evidence, not a fresh run today

On 31 Oct this chat ran read-only checks and the Windows suite, using bundled Python 3.12.14 because the py
launcher was unavailable in the agent shell. Persistent outputs are outside the repo:
`../_w2_checks/2026-10-31_codex/`.

| Evidence | Last recorded result |
|---|---|
| tests_audit_windows.json / log | 55 discovered: 54 passed, 1 skipped; zero failures/errors. Live PC skipped because causal-learn was absent in that interpreter. |
| End-to-end rerun within that test log | 1,298/1,298 comparisons pass; max absolute difference 0.000091483427284475. |
| verify_matmcd.json | Pass, 189 numbers, zero mismatches; same_host=false, tolerance=0.001. |
| Fresh certificate verifies in the test | causaliq, causal_copilot@main and gies@formula verified. All 14 stored certificates had prior VM evidence; do not claim all 14 were freshly checked on Windows. |
| code_identity_comparison.json | 64-file identity matches STATE after accounting for Windows versus Linux sha256sum manifest formatting. |
| rebase_facts.json | 210 cells, 79 measured; stage/cycle/overlap facts match handoff. |

These files were reread for this rebase; no runtime checks were rerun today. Their evidence date must stay
visible. This chat's subsequent changes have been new design docs, not implementation. These old tests are
not validation of the new proposed record model.

## 9. Original W2 obligations that remain open

The earlier v1.1/C1-C5 proposals have not been built. Their must-show obligations still need reconciliation
with the subsystem-by-subsystem implementation plan before any build begins. Do not assume that the much
broader record architecture automatically fits the old v1.1 scope/version label.

Open scientific/contract issues from the 31 Oct design review remain, with details in
`w2-design-iteration-2026-10-31.md`: heterogeneous P9 scope; K03 denominator and cross-regime peers; a complete
K01-K15 planted-fault matrix and valid null/unknown handling; chronology of labels when old evidence is newly
parsed; capability-aware coverage accounting. These are not silently solved by the connection envelope.
They belong in the relevant later subsystem/contract discussions, except where an immediate interface depends on them.

W2-5 through W2-9 are still unaccepted defaults: protocol proposal/adoption sequence, paper contract,
this-quarter validation battery, common five-system battery/spend decision, and keeping the 6 Nov checkpoint
on pre-package sources. Agreement to individual record boundaries does not decide those program-level choices.

The gate is not green. The Windows suite record exists with its disclosed skip; W5 adoption and Uzair's
commit/repin DLV-07/snapshot-last steps remain outstanding in this conversation. C1's agreed migration must
again meet parity and certificate checks before a port. Never write port_map.json before green; never move
rerun_v1 folders except in the authorized C1 bundle. W1 owns paper edits; W5 owns tracker/site and coordinates
adoption of shared contracts. W2 retains ownership of its protocol/package proposals.

## 10. Reading index for continuation and final review

Use this rebase for the current discussion state, then read only the detailed document relevant to the next
decision. Original kickoff/STATE remain necessary for ownership, runtime evidence history and hard boundaries.

- [Principles](system-connections-principles-2026-11-01.md)
- [Capability map and primary sources](system-connections-capability-map-2026-11-01.md)
- [Broader common-record proposal](system-connections-result-record-design-2026-11-01.md)
- [Outcome definitions and cases](system-connections-outcome-cases-2026-11-01.md)
- [Blocks 1-2: identity and requests](system-connections-identity-request-design-2026-11-01.md)
- [Blocks 3-4: system identity and information](system-connections-system-information-design-2026-11-01.md)
- [Block 5: outcome observations](system-connections-outcome-observations-design-2026-11-01.md)
- [Block 6: output-object index](system-connections-output-index-design-2026-11-01.md)
- [Block 7: artifacts and integrity](system-connections-artifact-evidence-design-2026-11-01.md)
- [Block 8: relationships and limitations, proposed](system-connections-relationships-design-2026-11-01.md)
- [31 Oct Codex review and unresolved W2 proposals](w2-design-iteration-2026-10-31.md)

Only new dated W2 design documents were written for this task. No implementation/tests, protocol, results,
paper, tracker/site, protected B5 modules, shared analysis/score/harness logic or git state were written.
