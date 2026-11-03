# Subsystem 1: final design review packet and proposed bundle plan (1 Nov 2026)

Tickets: DLV-08, DLV-09; neighbours DLV-10, ADV-01, DLV-06/07.
Status: proposed design package for Uzair's final review. Neither accepted/frozen nor authorized to build.
Scope: subsystem 1 only. Bundle planning below is provisional until final design acceptance; it performs
no implementation and does not replace the older program-level C1-C5 or their gates.

## 1. Review packet and precedence

Read the [consolidated outline](system-connections-contract-outline-2026-11-01.md) for the architecture and
accepted principles. The detailed current proposals are:

1. [SC-1 serialization candidate](system-connections-serialization-2026-11-01.md): exact envelope, field types,
   primitive unions, selected payload shapes, registries and reader/publication rules.
2. [SC-1 synthetic wire example](system-connections-sc1-example-2026-11-01.json): a complete small evidence-only
   package using those shapes. Fixed IDs/times/events are fictional and explicitly labeled.
3. [Interaction/recovery contracts](system-connections-interaction-recovery-2026-11-01.md): sessions, messages,
   state restoration, replay, cancellation and resource scope.
4. [Exact API and legacy mapping](system-connections-api-legacy-2026-11-01.md): optional ports, injected services,
   result types, side effects, bidirectional compatibility limits and inspected consumer seams.
5. [Composition review](system-connections-composition-review-2026-11-01.md) and its
   [nine logical scenarios](system-connections-composition-records-2026-11-01.json): provenance of design fixes.
6. [Domain/mapping](system-connections-domains-mappings-2026-11-01.md) and
   [output semantics](system-connections-output-subtypes-2026-11-01.md): family meanings and invariants.

SC-1 takes precedence over earlier illustrative field names for the serialization proposal. Earlier
logical specimens are not retroactively claimed to conform to it. Wire transcription must retain the
semantics of the composition cases. Interaction contracts specialize SC-1 through versioned payloads.
None of these documents overrides the existing adopted protocol/certificates/ownership or original gate.

## 2. Proposed supported scope for this subsystem increment

This matrix is a concrete recommendation for final review, not a claim of implementation or universal
native integration. All selected paths support evidence preservation and localized gaps. Actual adapter
feature/path claims need their own conformance and integration evidence.

| Area | Proposed initial core guarantee | Explicit limit |
|---|---|---|
| Domains | Finite variables, component/axis identity, relative/absolute time coordinates, grouped scope, encoder-scoped learned factors | No automatic cross-source equivalence, learned-factor alignment, symbolic-domain solver or relational grounding |
| Inputs | Typed evidence/presentation/schema/endpoint descriptors and explicit transformations | No universal parser for every table/image/model format; no proof of unobserved native use |
| Graphs | Directed, DAG checks, partly directed, endpoint-preserving, weighted and temporal compositions under selected contracts | Full CPDAG/PAG family validation is withheld unless its named checker is actually supplied; no repair/completion |
| Claims/orders | Typed propositions, local memberships, sets, partial/total order representations and ties/unranked scope | No inference of global negatives or direct causation from ranks/order alone |
| Quantities | Scalar/tensor/interval descriptors, range/unit/axis/association checks and named statistic semantics | No calibration/effect estimate/causal correctness claim from numeric type alone |
| Collections | Stable members, order, multiplicity, pairing, weights and finite-support normalization when prerequisites are met | No automatic IID/exact posterior claim; no replacement by marginals |
| Models/state | Artifact/domain/dependency/parameter associations and scoped load evidence | No universal native deserializer, implicit restoration or hidden-state identity proof |
| Histories | Explicit sessions/actions/retries/branches/continuations/replay/cancellation/accounting contracts | No new scientific workflow, scheduler or budget-setting engine |
| Access routes | Recorded import, prepared route, supplied direct function/process binding, existing-job observation and recorded-response replay ports | Provider-specific remote orchestration and new system installations are not generic readiness claims |
| Existing integrations | Additive recorded bridges for existing static-data and hybrid/name-based sources | New broader output families initially need explicit offline/native fixtures; synthetic checks do not prove third-party integration |

Initial real recorded paths to exercise: PC or GES stored method; causaliq native-response evidence where
its probability semantics can be established; MATMCD/Vashishtha hybrid outputs; Causal-Copilot state/stage
evidence through existing owned readers, without editing B5 modules. All eight existing adapters remain
available on the legacy path. Missing files/dependencies narrow claims, not the truth of whether a system
originally ran. Direct PC remains conditional on a suitable environment; the earlier Windows skip is not
resolved merely by specifying a new port.

## 3. Final review questions and recommended choices

| Decision | Recommendation | Strongest alternative and cost |
|---|---|---|
| Freeze boundary | Approve SC-1 shared shapes and selected contracts together; keep foreign/optional extensions separately versioned | Delay every base decision until every future system is modeled; unbounded scope and no demonstrable gain |
| Preservation versus interpretation | Retain accepted evidence foundation with stronger scoped claims | One graph/validity status simplifies consumers but loses partial/unknown/native output meaning |
| Adapter shape | Optional typed ports plus shared services | One mandatory large adapter interface burdens simple readers and encourages fake support |
| Identity/publication | Persist opaque occurrence IDs, immutable bases, explicit unresolved refs and scoped publication | Content/path identity is easier to create but merges occurrences and loses changed-file history |
| Legacy integration | Additive bridge and partial explicit projection; old reruns remain authoritative | Immediate replacement reduces parallel APIs but risks statuses, seeds, denominators and certificate pointers |
| Validation scope | Separate structural, semantic preservation, real-system path and scientific evidence | A single pass/fail label is shorter but falsely promotes schema checks to integration/scientific validation |

Design acceptance means the reviewer can answer the original eight review obligations: small ordinary case,
honest unknowns/conflicts, native meanings and mappings, recovery/import distinctions, actual artifact
binding, cross-system reuse, explicit support limits and a concrete compatibility gate.

No mandatory user decision is silently inferred for W2-5 through W2-9 or the original green gate. Subsystem-1
acceptance is not a spend/implementation authorization or public-contract adoption. W5 adoption remains
required where shared/public protocol/API/certificate contracts change.

## 4. Proposed dependency graph and uniform bundle gates

Bundle labels S1-A through S1-G refer only to this subsystem, not original C1-C5.

S1-A -> S1-B -> S1-C -> S1-D -> S1-E -> S1-F -> S1-G.
This serial order is deliberate for the requested incremental process. A later bundle starts after its
predecessor's review/gates; no proactive build of all bundles under an ambiguous design approval.

Every bundle must show:

- Its named positive/negative acceptance cases and documented supported limits.
- One applicable real stored system audited end to end. Early bundles can exercise the unchanged legacy
  auditor while adding evidence infrastructure; do not mislabel that as new semantic integration.
- All 1,298 stored comparisons within 0.001, exact counts/verdicts and complete certified number-key sets.
  Verify every available existing certificate; disclose missing evidence as a blocker/limit, never a pass.
  Same-host certificate tolerance remains its existing 1e-9 rule, not widened to 0.001 by this plan.
- Appropriate current/new audit tests with outputs, bytecode and temporary files outside the repo. The
  prior record is 54 pass/1 dependency skip; new runs must report their actual skips and affected claims.
- No unapproved shared/protected writes, native/API spend, result move or port map. Edits to pinned/shared
  allowed files use old-hash-guarded patch scripts; Uzair owns commit/repin/snapshot-last steps.

Use the verified interpreter for that environment; py is not assumed present. No test runs/installations
are performed by this plan. Tests add meaningful invariants/failure cases, not mirrors of dataclass fields.
No threshold tuning or scientific metric/finding change belongs to these bundles.

## 5. Bundle-by-bundle must-show lists

### S1-A. Schema and primitive contracts

Build only the approved wire-schema transcription, typed records/refs/knowledge/numeric/time/byte unions,
code registry and structural reader. Transcribe representative logical scenarios into exact positive and
negative golden specimens; keep native raw content unchanged during transcription. No default consumer swap.

Acceptance: duplicate keys/IDs, wrong target type, unknown required extension, overloaded null, invalid
decimal/UUID, malformed/base64/binary bytes, and invalid typed shape reject the affected claim while native
evidence can be wrapped. Declaration with no bytes cannot claim a computed digest. Reference cycles used
for associations are legal. Structural success never emits a scientific pass. Audit one stored method via
the existing auditor and verify its certificate. Gate A: schema/encoding obligations plus uniform gates.

### S1-B. Evidence, identity, references and publication

Implement core identity/import maps, snapshot capture/selectors, scoped availability/integrity, staged
publication, partial-capture recovery and correction/current-view pins. An evidence-only importer reads an
existing source through explicitly scoped access; no original execution is invented.

Acceptance: changed bytes with same path/mtime detected; missing versus denied versus unexamined preserved;
internal missing target differs from unavailable external reference; import same occurrence/input is stable,
changed input under the key conflicts; interrupted publication is not complete; partial evidence can publish
as partial; arbitrary bytes preserved exactly; copies add locations not runs. End-to-end stored MATMCD
audit plus its evidence package. Gate B: C2/C6/C7/C8 preservation behavior and uniform gates.

### S1-C. Domains, input bindings, graphs and quantities

Implement selected finite/time/group/learned-domain identity, schema axes, mappings and typed graph/quantity
contracts. Adapt at least one recorded method and one structurally different recorded name/hybrid path using
shared mechanisms. Interpret causaliq quantities only where raw proposition/conditioning semantics are known;
unknown fields remain reported data. Preserve old scoring seeds and mapped coordinate conventions.

Acceptance: graph, probability keys, parameter axes, interventions and stage fields map consistently;
duplicate labels do not merge variables; restricted legacy route rejects unsupported duplicate labels;
one-hot/partial mappings do not claim bijection; temporal self-history stays distinct; invalid DAG/range
claims survive with diagnostics; absent candidate probability does not require an emitted link. Existing
metric outputs remain unchanged. Gate C: domain V cases and C1/C3/C4 quantity/mapping cases plus uniform gates.

### S1-D. Remaining result families and associations

Implement typed local claims/sets/orders/rankings, collections/finite measures, tensor/interval descriptors
and model/state references. Native-specific model internals remain extensions. Use explicit synthetic/native
offline specimens for broader families absent from stored integrations; label which evidence is synthetic.

Acceptance: preserve repeated equal graph draws with different parameters; no incidental pairing by array
shape; incomplete masses never silently normalized; tied/unranked and abstained/unreported states differ;
learned alignment yields a derived view; invalid intervals/denominators and unsupported symbolic/relational
semantics produce scoped diagnostics. Include a real stored-system end-to-end audit as a separate compatibility
check. Gate D: C3/C5/C9 composition plus explicit collection/interval negatives and uniform gates.

### S1-E. Interaction, recovery, replay and accounting

Implement selected history records/checks and observation/response channels through controlled fixtures and
existing stored trace evidence. Use a deterministic no-spend reference native process for interruption,
reconnect, duplicate submission, callback and replay tests; it is conformance evidence, not a third-party
scientific integration. Never launch a live model or cc.ps1.

Acceptance: new attempt on checkpoint restart, same established attempt on reconnect; branch and state-load
scope preserved; unknown RNG prevents exact restoration claim; duplicate transport requires evidence before
native occurrence deduplication; cancellation receipt does not imply stop; parent may wait after child
completion; replay exhaustion cannot invoke fresh calls; cumulative counts/caps and inclusive totals remain
honest. Read existing Causal-Copilot stage evidence without protected writes and run its stored audit. Gate E:
all interaction/recovery acceptance cases and uniform gates.

### S1-F. Adapter ports, support declarations and legacy bridge

Implement approved optional interfaces and injected services, route readiness, additive legacy import and
partial explicit legacy projection. Keep legacy report/certificate path as default unless separately adopted.
Do not make the old collector execute prepared/live/replay routes implicitly.

Acceptance: recorded-only adapter works without invoke; prepared command does not claim execution;
unknown dependency/authority blocks required readiness; no operation launches native work while describing/
binding/decoding; diagnostics resolve in returned records/buffer; graph selection explicit; unknown outcome
and graphless success cannot be forced into legacy enums; all original statuses/notes/file_read/replicate
selection survive supported echo. Broad nonrepresentable cases reject without lost evidence. Gate F: exact
API/consumer compatibility matrix and uniform gates across all eight existing adapters.

### S1-G. Integration and release candidate

Run the approved complete conformance battery and supported recorded end-to-end paths. Verify that the
ordinary record stays small through reusable refs, larger cases compose and generic core code has no
system-name exceptions. Document exact supported adapter/path/type/version cells with their evidence.

Acceptance: every approved positive/negative golden case; real versus synthetic evidence labeled; no false
full CPDAG/PAG/model/remote-service claims; all 14 existing stored audits/certificates checked when their raw
evidence is available; 1,298 comparison keys/counts/verdicts preserved within their required rules. Release
candidate includes implementation/code identity, limitations, checks and proposed public adoption changes.
Gate G: all predecessor gates, final integrated evidence and owner adoption/repin requirements satisfied.
This gate does not authorize the original C1 folder migration or port_map.json.

## 6. Review result and outstanding authorization

Technical self-review produced concrete serialization, optional-behavior, API and compatibility proposals.
It caught and resolved discriminant collisions, row-axis versus variable identity, hidden service dependencies,
legacy confidence/name constraints and pointer-root behavior. This is not independent agent review or executed
runtime validation. No subsystem-1 design approval is recorded on Uzair's behalf.

Remaining decisions are final acceptance/revision of SC-1, selected support scope, optional port boundaries
and additive legacy strategy. They are review choices, not missing technical placeholder implementations.
The schema transcription and executable proofs are implementation work explicitly deferred until go.

The original W2 green gate, W2-5..9, paper contract, protected ownership, no-spend conditions and C1-C5
must-show lists remain in force. A later authorized implementation must reconcile these plans with those
obligations rather than assume subsystem design acceptance resolves them.

No source implementation, tests, result migration, protocol/certificate changes, protected edits, native/API
execution or git writes occurred in preparing this packet.

Authoring checks: 36 declared core/history record types have no duplicate declarations or undefined concrete
Ref targets in the catalogs. The six-record synthetic SC-1 example has 33 resolving internal references and
IDs matching the proposed lexical form. This is JSON/reference inspection, not structural-schema or semantic
validation. Local document links resolve and all seven proposed bundle labels are present.

A fresh read-only comparison of the 64 files in the original package-identity manifest found zero changes;
the identity remains d615f61a2ce46862b9093ee7309374c825a5684dcf0d4561453a7d71444e42ae.
Reports are outside the repo in `../_w2_checks/2026-11-01_s1_design/`:
final-design-inspection.json, sc1-example-inspection.json and final-design-source-identity.json.
No audit tests, stored-number reruns, native jobs or certificate verifies were rerun in this design step;
their last runtime evidence date remains the earlier rebase's date.

## Where we're going

Uzair reviews the complete subsystem-1 candidate and requests any targeted revisions. After acceptance,
confirm the ordered bundle plan and give a separate implementation go for the intended scope. Build/test
one bundle at a time and review its gate evidence before moving on; do not expand into other subsystems.
