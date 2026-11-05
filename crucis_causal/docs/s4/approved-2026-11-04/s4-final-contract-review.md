# S4 serialization, interfaces, recovery and compatibility design

DLV-08, DLV-09, related DLV-10. Design review candidate, 2026-11-04 Pacific.
The first procedure slate and worked package reviews define the mathematical
and semantic requirements. The role-cardinality review defines the reference
and output obligations. This document selects candidate wire and service
contracts for those roles and a bounded first implementation. User review
and explicit build authorization are separate entry conditions.

## 1. Bounded serialization

Use a separately versioned JSON package named s4.measurement_package at
0.1.0-proposal.1. An envelope contains exactly format, account_id, snapshot_id,
audience, frontier, roots, records, and dependencies. format is an exact
{name,version} contract. The audience is one pinned audience reference.
The frontier is a keyed set of exact source positions or frozen snapshots
with attributed unresolved history where relevant. roots contains exactly
one local account-root reference. The account root indexes at least one
supplied source, intent, observation or gap. Each record has id, kind, contract
and payload. kind and contract must agree with the installed exact family.
The envelope owns snapshot identity and frontier. Role payloads reference
that context or explicitly reference an earlier frontier where relevant.

Local IDs are case-sensitive ASCII with an initial lowercase letter,
followed by lowercase letters, digits, dot, underscore or hyphen, at most
128 bytes total. S1/S2/S3 identities use their own exact readers and syntax.
Opaque native keys or labels preserve their exact Unicode scalar sequences.
Explicitly type collection roles. A sequence preserves order. A set has
unique members and uses stable canonical order. A keyed association uses
an array of distinct keyed entries in key order. Field-name and key
sorting for canonical output uses Unicode code point order. File paths,
mutable locators and collection offsets do not stand for record identities.

Only strict UTF-8 JSON. Reject duplicate properties, bare JSON numbers,
null, nonfinite tokens, invalid Unicode scalars, undeclared fields in known
kinds, and unsupported format versions for interpretation. Preserve an
unrecognized native source via an attributable opaque source or artifact
reference under a recognized envelope. Canonical writers use the current
S3 compact sorted-key JSON rules, including its UTF-8 string escaping.
Normalize only declared mathematical or set representations. Keep the
received bytes as the integrity subject. S4 canonical packages must
re-encode byte-for-byte. S1/S2/S3 and native input digests use their original
bytes, independent of S4 canonicalization. Scientific comparison uses the
declared comparator rather than package byte equality.

### Exact forms

| Form | Candidate wire grammar and validity |
|---|---|
| Contract | Object with string name and exact version. Unsupported versions can be preserved as attributed source material. No fallback by name. |
| Local reference | ref_kind=local, target_id, expected_contract, optional selector. Resolves within the current exact snapshot. |
| External reference | ref_kind=external, dependency_key, target_id, expected_contract, optional selector. The dependency entry pins format, package identity, SHA-256 over original bytes and exact byte length. Enforce one dependency per identity and pin. |
| Artifact extent | ref_kind=artifact, artifact_record (one typed record reference), content_pin (algorithm, SHA-256, length, extent), optional typed selector. Verify the containing bytes and selected range when the role requires each. |
| Selector | One tagged variant: member with a typed member key, output with binding/role/subject key, JSON pointer for a specifically declared document role, or byte_range with exact start and exclusive end. Absence selects the whole target. Reject unknown selectors, bounds violations and ambiguous keys. |
| Exact scalar | int with canonical signed decimal text, or rational with canonical numerator and positive denominator text. Reduce by the greatest common divisor; zero is 0/1 in a rational field. Signed zero, decimal spelling and native infinities remain available through the raw source. Reject negative zero, leading zeroes, and over-limit digits in exact numeric fields. |
| Closed range | One range kind outer_interval or slot_range, exact lower and upper rationals with lower <= upper, one quantity and premise scope. An outer interval declares the containment direction. No confidence level field for this role. |
| Result | Exactly one tagged defined payload or one tagged disposition. Defined payloads include Boolean/category, exact scalar, bounded keyed ledger/vector and exact closed range under their declared role contracts. A computed undefined result references the observed emission and deciding facts. A preflight hold is a goal assessment and references its request goal, blockers and any safely visible evidence. |
| Presence and extent | Required roles contain one resolved value or an explicit unresolved/contradicted/inapplicable disposition when the containing state permits it. Omission is reserved for a schema-declared optional role. Known empty, partial, unexamined and unavailable have separate extent and basis. |
| Scoped claims | Separate axes for input/applicability, work, value, profile and comparison. Reproduction distinguishes basis mismatch, blocked, incomplete observation, agreement and disagreement. Actual quantities and claims remain separately addressable. |

All references identify exact target contract and scope. Dependency graphs
and proof graphs are acyclic. Navigation associations can point both ways
without becoming proof edges. A record may reference a local record before
it is listed. Whole-package digests are attested from outside the frozen
subject. For the first procedures, the kind/payload matrix uses the
approved role cardinalities, exact procedure-specific role keys and no
untyped general-purpose evaluator configuration. Limits failures carry
a typed diagnostic without a fabricated scientific value.

### Candidate limits and gates

These are conservative first-version policy caps for review, rather than
measured capacity or package-schema limits for future versions. Operators
can lower them for an explicit run. Pin the actual budget for a calculation
and a replay. Apply the stricter limit wherever a reused S1–S3 reader or
carrier has its own bound.

| Resource | Proposed hard ceiling |
|---|---:|
| Canonical S4 snapshot bytes | 524288 |
| JSON/container depth | 48 |
| Records per snapshot | 4096 |
| Items in one collection | 8192 |
| UTF-8 bytes in one scalar | 32768 |
| Reference nodes per snapshot / visits per validation | 32768 / 131072 |
| Reachable external snapshots / dependency depth | 64 / 16 |
| Total bytes read across dependency closure and consumed artifacts | 33554432 |
| Decimal digits per serialized integer component | 256 |
| Decimal digits per exact intermediate component | 4096 |
| Charged rational operations per calculation | 250000 |

Check raw byte and depth limits before unrestricted object materialization.
Charge reference visits even for repeated edges; memoization cannot expand
the allowed closure or imply access. Reject over-limit numeric text before
constructing large integers. Define the work charging rule per procedure.
For the first exact evaluators, charge each declared addition, subtraction,
multiplication, division and ordering comparison, check reduced intermediate size
before any further arithmetic, and bound temporary integer components to 8193 digits for one bounded primitive.
Check the reduced result before the next primitive and bound input scanning by the collection
and reference limits. Hold the affected result on numerical budget failure.
A chunked or approximate method would have a separately qualified contract.

Validate in stages: strict wire and structural shape, exact reference
resolution and authorization, cross-role semantic applicability, then
observed calculation and claim assessment. A valid envelope can faithfully
preserve an unavailable dependency or held goal. The claim stage must
distinguish preservation from fulfillment of a required reference. No schema
result asserts truth, scientific compatibility or publication authority.

### S3 carrier and projection

S3's current snapshot reader dispatches S1–S3 formats. Use an S3 projection
view with a registered typed payload pointing to the exact S4 bytes in an
S1 artifact snapshot. Register one exact S4 payload reader. S4 reference
discriminants differ from the S3 internal/external walker tags, so S4 local
record IDs resolve within the S4 capsule. The S4-aware bridge and supplied
audience policy verify and reconcile each selected S4 external dependency
with the exact S3 carrier dependencies, or exact artifacts in those
dependencies, and check that the record, metadata and proof closure is
authorized. A carrier reference pins the carrier and the inner artifact
and contract. Multiple capsules may form an acyclic chain.

Use S3's publication, lookup and pointer CAS with the actual authorized
closure. The capsule cap leaves room under the S3 scalar bound for base64
of those bytes; the completed carrier and aggregate dependencies still
need the existing S3 limit checks. A public view of a restricted result is
a separately prepared projection whose bytes and dependency inventory omit
restricted references and metadata. It can include a scoped authorized
attestation. A registered syntax reader alone cannot approve its science or
disclosure. The S4 publication interface holds publication when the S4-aware bridge or audience policy is absent.
A direct S4-format dispatcher in S3 is deferred.

### Representative wire fragments

These fragments illustrate the exact value/disposition alternatives. A full
record also supplies the binding, subject, output role, scope and origin
required by its record kind.

```json
{"tag":"defined","value":{"number_kind":"rational","numerator":"1","denominator":"1"}}
{"tag":"undefined","reason":"zero_judged_denominator","basis":[{"ref_kind":"local","target_id":"val.judged-count","expected_contract":{"name":"s4.result","version":"0.1.0-proposal.1"}}]}
{"tag":"held","reason":"required_answer_unavailable","basis":[{"ref_kind":"local","target_id":"prem.answer-capture","expected_contract":{"name":"s4.premise_assessment","version":"0.1.0-proposal.1"}}]}
```

The first is a computed value, the second a computed diagnostic result, and
the third belongs to the goal assessment. The scientific scope of agreement
1/1 still carries the original match and judged counts and keyed mask as
separate pinned diagnostics. An exact reduced rational does not replace them.

### Worked round-trip obligations

- Graph covered result has rational 1/1, numerator 2, denominator 2 and keyed
  mask AB/BC. The full-scope goal has a separate held disposition for AC.
  It has no calculation emission.
- Local abstention has defined coverage 0/1 with denominator count 3,
  and an undefined ratio with zero judged denominator and evidence of scope.
  A missing answer stays an evidence hold. Byte replay cannot turn one into
  the other.
- Order fulfills the complete submission while admissibility can be held
  under necessary-only criteria. Preserve the empty violated set and exact
  supplied-constraint scope.
- Paired enclosure carries all four slot associations and endpoints 3/20
  and 13/20. Preserve the distinct full-quality hold and the two different
  zero, range or unavailable slot premises. The bound uses exact unit keys.
- Forecast stores 1/25 with timing premise. The finite posterior carries
  keyed alternatives, normalizer and posterior roles. Zero normalizer can
  accompany an undefined posterior; a missing likelihood holds entry.
- Replay pins the same original basis across new occurrence identity.
  A changed derived mask under that same basis is a completed disagreement.
  A substituted reference is a basis mismatch. Projection may withhold
  original input access while retaining scoped evidence of a restricted replay.

## 2. Interfaces and ownership

Candidate namespace crucis_causal.measurement. Public entry points take
immutable domain values and return typed reports or proposed record deltas.
Separate inspect, resolve, plan, evaluate, record, assess, compare and publish.
The first evaluators are explicitly selected pure deterministic callables
over materialized values. Registry lookup is exact by contract and version
with pinned implementation and qualification evidence. No ambient resolver,
fetch, clock, random source, credentials or storage handle enters an evaluator.
Storage, capabilities and authorization stay in supplied S3/S1/S2 ports.
Inspections and plans have no scientific execution or writes.

| Candidate signature | Contract |
|---|---|
| inspect(bytes, limits) -> DecodedSnapshot or WireIssues | Pure bounded decoding, canonical check, shape and local graph. No dependency fetch. |
| resolve(snapshot, supplied_views, read_capability, limits) -> ResolvedView or ResolutionIssues | Check exact pins and typed selections with established access. Return resolved or explicitly held scoped roles. |
| plan(goal, resolved_view, registry, limits) -> PlanReport | Select exact procedure, required premise stages, execution basis, output roles and typed blockers. Plan identity pins the versioned selection. |
| evaluate(prepared_inputs, exact_evaluator, arithmetic_budget) -> EmissionBatch | Pure computation with deterministic keyed results and diagnostics. Establish during-work mathematical facts, such as a zero normalizer. No publication or authorization. |
| execute(plan, invocation_id, run_context) -> WorkReport | Coordinator validates the frozen plan and admission, correlates one observed calculation occurrence and bounds, and calls evaluate. WorkReport identifies actual outputs, extent and effects. This is the sole normal calculation entry point. |
| record(work_report, expected_head, journal_context) -> RecordedWork or CommitDisposition | Validate origin, exact planned roles, derivation and dispositions. Use S3 journal append and transaction lookup. Recording operates on the existing work report; it never calls evaluate. |
| assess(target, recorded_view, criterion, read_context) -> ProfileAssessment | Check actual qualifications, inputs, work and claims for one target, profile and audience. Return an assessment value for explicit recording. |
| compare(reproduction_goal, original_view, replay_view, comparator, read_context) -> ComparisonDisposition | Pure basis match and role-scoped exact comparison after actual recorded replay. Comparator declares values, masks, diagnostic causes and key ordering. |
| prepare_projection(snapshot, audience, supplied_policy, read_context) -> ProjectionPlan | Construct an S4 projection and S3 carrier, verify both closures and pin the complete draft. Separate from commit. |
| publish(projection_plan, publication_id, authorized_storage_context) -> PublicationDisposition | Invoke existing S3 storage with the pinned authorized bytes. Lookup and CAS use the existing operational mechanisms. |

The CLI initially exposes inspect and plan over explicit supplied bytes,
including machine-readable blockers. An ordinary CLI inspection never
selects live capabilities. Future execution uses the typed service boundary.
S4 consumes S1 source/output and mapping, S2 intent/population/selection,
and S3 actual execution, time, delivery and publication. S4 supplies
measurement records and evidence to downstream findings. It does not own
scientific decision thresholds. Exact registry metadata never alone proves
evaluator qualification for a requested combination.

## 3. Recovery and effect accounting

Keep goal, prepared plan, invocation, calculation occurrence, journal
transaction, published snapshot and mutable pointer identities distinct.
Persist invocation intent before authorized work and store any observation
that establishes work with its exact basis. An invocation key alone proves
neither execution nor exactly-once evaluation. Use the S3 journal/owner
mechanisms for durable operations. An explicit rerun under a fresh occurrence
can be admitted independently when allowed, even if an earlier calculation
stays uncertain. A computational occurrence is separate from a scientific
unit or a native trial.

| Interruption or change | Recovery decision and required evidence |
|---|---|
| Planned or admitted with no execution observation | Record unknown occurrence if the boundary could have crossed. Establish whether it crossed from the exact journal/owner evidence. Reuse the original only if its work and basis are established. A separately admitted fresh calculation has a new occurrence. |
| Calculation reported partial outputs or exceeded arithmetic budget | Preserve actual emitted roles, extent and diagnostic. Re-evaluate affected claims individually. An explicit fresh run can use the original pinned basis; a changed budget or configuration is a new calculation basis. |
| Work observed and journal commit acknowledgment lost | Look up the exact transaction and binding. Reconcile a known commit, append an already observed report only where admissible, or retain unknown status. Recording does not recalculate. A same key with different basis is a conflict. |
| Interrupted write leaves content staged without publication receipt | Staged bytes alone establish staging. Look up the exact publication ID/package/digest/closure; preserve unknown if owner evidence is unavailable. Reuse S3 authorization and storage correlation for any permitted retry. |
| Publication committed and pointer CAS fails | Preserve the committed immutable snapshot. Read the current pointer and reconcile. A new CAS requires the known expected revision and authorized selection. |
| Input missing, access revoked, or locator changed | Compare access and bytes against the original pins. Denial or wrong bytes hold the affected replay or claim. A new source binding preserves the old frontier and uncertainty. |
| Worker state lost | The first procedures have no evaluator checkpoint contract. A permitted fresh calculation starts from pinned inputs. A replay requires its own explicit goal, actual work and comparison. |

State order for recoverable design fixtures: prepared plan, admitted work
intent, observed start or unknown, observed emissions and extent, recorded
work commit, audience projection, publication commit, optional pointer CAS.
Each step can hold independently. Exact agreement establishes computational
reproduction at its declared boundary. Neither resume nor successful recovery
supplies new reference truth. Recovery fixtures must exercise success,
partial completion, lost replies, conflicting correlation, denial and fresh
occurrence identity at the relevant seams.

## 4. Legacy mappings

Preserve legacy route identity, inputs, scope, source bytes and historical
receipts. Initial migration is an explicit read-only compatibility mapping.
Use P0 preservation for opaque or insufficient artifacts. Use scoped P1
only where the historical quantity, population, reference or convention
can be established. Generic P2–P5 claims require the exact S4 contracts and
actual relevant qualification/work. A new calculation from pinned historical
source evidence has a new occurrence and must pass the selected contract.
No historical value or certificate is rewritten by import.

| Legacy source | Initial S4 mapping and boundary |
|---|---|
| metrics/l0.py reference tiers and score_graph | Preserve reference tier and role, selected source, exact historical metric IDs, target pairs, seed derivation and expected versus committed orientation basis. Historical adjacency F1 and Q01 agreement remain separately named quantities. A future Q01 binding must derive its own eligibility ledger. |
| metrics/l0.py completed versus delivered summaries | Preserve original execution statuses and the completed/executed/scored selection rules. Keep historical failure-as-zero and missing cost conventions local to their metrics. Q05 needs its own delivery horizon and qualifying-answer evidence. |
| controls/effects.py and _support/score/paired.py | Preserve observed common-key set, clustering, weights, pooled versus unit-average functional, resampling count and seed where evidenced. Q04 uses its explicit intended frame and exact point functional. Q05 is an outer bound. Historical bootstrap intervals retain their own method scope. |
| _support/score/calib.py and _support/score/rca.py | Preserve named calibration, coverage or ranking semantics and inputs where supported. Q03 handles one binary forecast loss. Q02 handles a strict precedence deliverable. Similar input shapes carry no automatic mapping. |
| findings.py, reruns and certificates | Findings remain downstream. Keep report and certificate provenance as historical compatibility evidence. Exact S4 replay has its own observed basis, comparator and audience. |
| Historical run without a stable original basis | Preserve the supplied report or artifact plus its unknowns. Withhold claims that require original execution, selection, sources, or replay inputs. |

The recorded-data gate stays at 1298 comparisons with unchanged tolerance
0.001 and verification of 14 stored and 14 freshly recomputed certificates,
against explicitly supplied historical evidence and external scratch outputs.
These are compatibility targets inherited from S3. This design review did
not rerun them. The research checkpoint still points to its frozen sources.

## 5. Acceptance and implementation order

The companion candidate DAG assigns exact predecessor bundles, acceptance
evidence and recovery checks. Review and pin this design, the role matrix,
procedure slate, case reviews and DAG. Verify the repository base, governing
instructions and interpreter. Build begins only after the user's explicit
authorization. Each bundle must meet its predecessor gates, scoped math or
mechanism qualification, checked source and validated local commit before
dependent work advances. Separate fixture, recorded-data and native claims.
Release requires full scope traceability, both data availability regimes
reported separately, and review of unresolved support gaps.

## Source anchors

- [S3 exact byte reader and resolver](../../../execution/codec.py)
- [S3 typed payload registry](../../../execution/registry.py)
- [S3 audience closure](../../../execution/projection.py)
- [S3 journal and storage ports](../../../execution/api.py)
- [S3 publication and recovery](../../../execution/publication.py)
- [S2 evaluation boundary](../../../experiments/evaluation.py)
- [Historical scoring](../../../metrics/l0.py)
- [Historical effects](../../../controls/effects.py)
- [S3 compatibility receipt summary](../../../docs/subsystem3-release-review-2026-11-04.md)
- [Candidate bundle DAG](s4-candidate-build-dag.json)
