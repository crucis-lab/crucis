# Subsystem 1 implemented support and acceptance map

Tickets: DLV-08, DLV-09; DLV-10 compatibility evidence.
Scope: accepted SC-1 candidate, opt-in version 0.1.0-proposal.1, S1-A..G only.
This document records implementation guarantees. Scientific correctness, the original
W2 green gate and public protocol adoption remain separate.

## Capability map to implementation

| Axis | Implemented representation/check | Exercised evidence and limit |
|---|---|---|
| A01 Task/scope | Request operation, scoped deliverables/completion; local claims/sets/abstention | C9 golden; no universal fulfillment rule or local-to-global graph invention |
| A02 Variable identity | Namespaces, variable refs, finite/component/grouped/learned/temporal domains, coordinates, explicit mappings | Domain tests, C1/C4/C5; relational grounding and learned alignment criteria remain external |
| A03 Accepted evidence | Exact artifacts, payload selectors, schemas and endpoint descriptors | Recorded byte/file tests and H1; native-specific input readers are supplied |
| A04 Sampling organization | Ordered typed axes, sample/group/time descriptors separate from causal members | Tensor/domain cases and O1; no pooling or IID/effective-sample-size inference |
| A05 Interventions/environments | Presentation/schema/domain/proposition descriptors with explicit mappings | Nested mapping mechanism and presentation tests; no experimental intervention assignment engine |
| A06 Other information channels | Policy-scoped presentations and endpoint/action content | Delivery audience checks; no inference of unobserved use or OS sandbox guarantee |
| A07 Assumptions/validity domain | Versioned operation/family/predicate contracts, scope/conditioning, native declarations | Assumptions are recorded; schema/range checks do not establish causal validity |
| A08 Computational access/components | Supplied function/process/service descriptors, endpoints, dependency inventory and optional ports | Port/readiness tests; describe/bind do not install or resolve executable native entrypoints |
| A09 Interaction/authority | Sessions, endpoints, requests/responses, transmissions and scoped runtime grants | H1 plus callback/delivery fixture; no expert or experiment policy selection |
| A10 Lifecycle/state/randomness | Request/attempt distinction, state load, retry/branch/checkpoint/warm-start links, reconnect registry | Unknown-RNG negative and restart/reconnect fixture; hidden-state equality/independence withheld |
| A11 Result objects/cardinality | Twelve body families, distinct collection members, multiplicity and parameter pairing | All body types in goldens, C3/O1; no exact posterior or implicit averaging/selection |
| A12 Graph/claim semantics | Family/endpoint/coverage/omission, local claims, sets and orders | Graph/family tests and C4/C9; CPDAG/PAG/relational guarantees withheld |
| A13 Uncertainty/decisions/abstention | Scalar/interval/tensor, explicit weights, decisions, ties/unranked and abstention | Family tests and O1; no calibration or local-to-global negative inference |
| A14 Observability/provenance | New observer identity, source snapshots, native reports, scoped gaps, immutable assessments | C2/C6/C7/C8; capture, authorship, use and native success are separate |
| A15 Execution/transport | Recorded/prepared/supplied-driver/attached observation routes and exact recorded response replay | Reconnect, repeated-request, mismatch/exhaustion, no fresh fallback; no universal remote/full-system replay |
| A16 Resources/termination/partial failure | Reported units/basis/scope, disjoint accounting, scoped outcome/cancellation observations and partial evidence | Cumulative restart sums, inclusive/overlap and ack-versus-stop negatives; unknown usage is not zero |
| A17 Identity/configuration/reproducibility | Opaque occurrence IDs, component/code/configuration identity, exact versions, import bindings and CAS | Code hashes, repeat/changed import and legacy replicate echo; public adoption stays external |
| A18 Availability/access boundaries | Snapshot/declaration distinction, exact digests/selectors, explicit roots and information audiences | Missing/changed-file and unauthorized delivery tests; no automatic network fetch or OS isolation claim |

Axis labels above are shortened from the capability map; this table describes the
selected implementation, not a percentage of all causal discovery systems.

## Real recorded integration cells

All eight existing legacy adapters are exercised through the additive recorded-only
connection and full-field echo: pc, ges, gies, matmcd, vashishtha, pywhyllm, causaliq,
causal_copilot. Each test uses an existing audit's actual item/arm and patches `run`
to refuse native execution. No new execution/readiness claim follows from import.

| Path | New guarantee exercised | Evidence |
|---|---|---|
| PC stored semantic method | Original-position graph/domain, exact native files, legacy echo | Semantics/ports tests; final CLI capture/publication path |
| GES/GIES stored methods | Full legacy record/file preservation and echo | All-eight recorded test; existing rerun/certificate paths |
| MATMCD hybrid | Related outputs/stages, source files, status/cost preservation | Semantics/ports tests; final CLI capture/publication path |
| Vashishtha hybrid | Related legacy output objects and exact echo | All-eight recorded test and unchanged legacy audit |
| PyWhy-LLM recorded names | Native evidence and legacy fields | All-eight recorded test; no live LLM port claimed |
| causaliq recorded names | Legacy echo; separate native response field decoder bound to result digest, names/permutation and prompt | Native field test; legacy CLI capture/publication separately |
| Causal-Copilot bnd08 | Existing state/stage reader, failed run with surviving stages, exact echo | History lineage test asserts actual stages; final CLI preservation path |
| Causal-Copilot ab06cc/main/bld06 | Existing audits/certificates recomputed unchanged | Full legacy rerun; no blanket new decoder equivalence for every internal state |

The native causaliq decoder establishes prompt-bound fields, not calibration or a
conditional orientation probability. Foreign predicates remain foreign to generic
proposition/statistic validators. Native logs are never treated as a spending grant.
The native PC dependency remains absent; its original live test is the disclosed skip.

## Synthetic conformance cells

The frozen C1-C9 packages transcribe the design cases into SC-1. H1 adds optional
history records; O1 adds finite measure, tensor, interval, order and opaque extension
compositions. Fixed IDs/times are explicitly fictional. All 36 record types and
12 output body types occur across these packages, and expected named pass/fail/unknown
checks are asserted. Their content is not a certificate or third-party run.

`tests/audit_fixtures/s1_native_fixture.py` is the no-spend process fixture. Tests
exercise same-process reconnect, duplicate submission receipt, callback response,
checkpoint/termination/restart, and cancellation acknowledgment without stop.
Pure runtime-port tests exercise exact grants, refusal, bounded observation and
separate delivery/cancellation authority. Replay consumes a finite explicit transcript.

## Bundle obligations and evidence locations

| Bundle | Main acceptance cases | Tests/source |
|---|---|---|
| S1-A | Closed wire shapes, encoding, knowledge, IDs/refs, unknown critical extensions | schema tests and generated schema |
| S1-B | Exact bytes/selectors, missing/changed files, immutable store, partial evidence, import identity/CAS | evidence tests, evidence/store |
| S1-C | Domain identity, complete/partial mapping, graph/quantity closure and native probability meaning | semantics tests, domains, causaliq integration |
| S1-D | Local decisions/ranking/order, explicit sample pairing, exact finite mass, tensors/intervals/models | family tests and selected family checks |
| S1-E | Episode/recovery/event precedence, partial state, ack versus stop, replay and cumulative usage | history tests and process fixture |
| S1-F | Optional ports, supplied authority, diagnostics, full legacy codec/echo, partial projection | ports tests and all-eight recorded bridge |
| S1-G | Eleven complete frozen packages, supported/unsupported composition, CLI, source identity, compilation and complete compatibility | integration tests and final gate |

Every completed bundle's gate recomputes 1,298 comparisons, exact number-key/count
parity and finding ID/kind/verdict parity, and verifies 14 stored plus 14 fresh
certificates using the existing verifier's unchanged tolerance. Gate JSON/logs and
runtime outputs live outside the repository at `_w2_checks/2026-11-01_s1_build/`.
The implementation log records exact successful run directories and counts.

The final gate also produces `implementation.sha256`, original-source comparison,
external compiled bytecode, and new CLI capture/publication/validation artifacts for
PC, MATMCD, causaliq and Causal-Copilot. The source manifest excludes explanatory docs
and includes the runtime/schema/dependency lock, baseline pins, tests and goldens.

## Owner steps and public boundary

The original 64-file baseline and adopted protocol/report/certificate paths stay
pinned. W2 supplies an opt-in implementation and evidence; it does not set DLV-09
or DLV-10's tracker status to done. W5 can adopt public API/protocol/evidence-list
changes, then Uzair can deliberately repin/commit and run snapshot last under the
program workflow. No W1 edit, B5 edit, analysis/score/harness edit, API spend, git
write, result migration, or port map is part of this implementation.

## Where we're going

Review the completed subsystem-1 release evidence and owner adoption proposal.
Keep the original wider W2 decisions/green gate and other subsystems in their
respective design workflows; subsystem-1 completion does not silently resolve them.
