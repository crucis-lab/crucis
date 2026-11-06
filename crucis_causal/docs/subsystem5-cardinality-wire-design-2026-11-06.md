# S5 role cardinalities and bounded serialization

DLV-08, DLV-09, DLV-10. 6 November 2026. Candidate wire design following
the [consolidated contract](subsystem5-contract-outline-2026-11-06.md).
The examples review meaning and cardinality. They are design specimens.
Runtime validation and golden package tests belong to implementation.

## Envelope and references

Candidate format name s5.finding_package and version 0.1.0-proposal.1.
The envelope has exactly format, account_id, snapshot_id, audience,
frontier, roots, records and dependencies. Format is a contract pair
of name and version. Audience is one exact S3 audience reference.
Frontier is a nonempty keyed set of source positions with either an
exact reference or an explicitly attributed gap. Roots contains exactly
one local S5 account reference. The account indexes at least one
attributed capture, scoped assessment or handoff. The whole envelope
owns the default audience and cutoff. A record referring to an earlier
context uses an exact frozen dependency and its authored frontier.

Reuse the [S4 wire conventions](s4/approved-2026-11-04/s4-final-contract-review.md)
for the record shell, contract pair, reference discriminants and exact
number forms. Each record has id, kind, contract and payload. Its kind
and contract must agree. S5 IDs use a lowercase ASCII letter followed
by lowercase letters, digits, dot, underscore or hyphen, at most
128 bytes. The exact S1–S4 readers retain their own native ID rules.

| Reference | Candidate exact form and obligation |
|---|---|
| Local | ref_kind local, target_id and expected_contract. Resolve only within the referring snapshot. |
| External | ref_kind external, dependency_key, target_id and expected_contract. A dependency declares key, package_id, format and pin. The whole-package pin covers SHA-256 and byte length over the original bytes. A reused package identity with different bytes is a conflict. |
| Artifact | ref_kind artifact, artifact_record and content_pin. The record reference selects one S1 artifact snapshot. The pin names algorithm, digest, length and whole or byte-range extent. When the role requires a range, verify its selected bytes and exclusive end. |
| Selection | Default to the whole record. A role may declare one member selector with a keyed identity and expected member semantics. Selecting an S4 result role preserves its exact result and scope. Arbitrary JSON pointer interpretation is outside the first S5 rule binding. |

The expected contract must match the exact version and the role's
allowed target type. A matching name or digest alone leaves scope,
authority, selection and scientific applicability to later checks.
Dependencies and proof links must be acyclic. Account indexes and
other declared navigation links are separate from proof. In particular,
a decision or basis has no proof backlink to its owning assessment.

## Roles and cardinalities

Numbers here describe one record. Shared questions and rules may be
referenced by many assessments. Braced values name conceptual types
specified by the surrounding role, rather than general JSON objects.

| Kind | Required references and values | Conditional or repeating roles |
|---|---|---|
| Account | One attributed owner or observer. One nonempty keyed index of local capture, assessment or handoff roots. | Zero or more keyed history links and profile claims in the exact view. Index associations are navigation. |
| Capture | One attributed origin, one scoped capture extent and one availability disposition. | Zero or more source records, artifact extents or reported assertions. A captured-bytes claim requires at least one exact artifact pin. Missing capture requires a reason and a scoped observation. |
| Question | One versioned finding kind, one exact audited subject/configuration, one target scope and one measured quantity or incident predicate. | A comparison declares ordered conditions, direction, selection and unit policy. A reference-dependent question declares the reference interpretation and applicability requirements. Reuse exact S1/S2 records. |
| Rule | One exact rule revision, one compatible target contract, one evidence policy, and one rooted predicate or branch definition. | Keyed operands, shared prerequisites and rule clauses. Each operand pins its quantity, unit and accepted evidence form. A numeric comparison has one explicit operator and one qualified threshold. Conjunction and disjunction each take at least two distinct clause keys. A branch rule pins how overlap and uncovered cases are treated. |
| Basis | One question, one exact rule and one selection policy. A keyed set of evidence entries, possibly empty with scoped reason. | Each entry has one declared role and either one exact evidence reference or one explicit unavailable, conflicting or restricted state. Conflict can cite multiple competing references. A selected score binds one exact S4 result and qualifying premise support. An incident role may bind exact S3 evidence directly. |
| Assessment | One question, rule, basis, attributed origin and envelope context. Exactly one disposition per axis for applicability, execution, sufficiency, decision and registration. | At most one decision reference and one registration reference per assessment, as required by their dispositions. At most one occurrence reference, required for a claim of actual evaluated work. Held preflight uses an attributed assessment and gap basis without inventing evaluation work. |
| Decision | One exact question, rule and basis, and one outcome. | One trace entry for each clause in the declared decision slice. Each settled clause binds its observed operands and decisive evidence. Unresolved or unevaluated clauses state their basis or reason. A rule-defined inconclusive outcome identifies its branch. A hold belongs to the assessment and needs no decision record. |
| Registration | One assessment scope expressed by question, rule and its registration basis, one policy and one determination. | A confirmatory determination requires exact commitment, comparable ordering, exposure and conformance evidence. A reported label references its attributed source. Amendments and bounded adaptive choices add their actual authority, inputs and relevant timing when relied on. Registration can have a distinct basis from the decision. |
| History | One subject assessment and one or more related exact records. One relationship kind and a nonempty set of affected dimensions. | Correction, resolution and retraction require adjudication evidence. An open dispute requires at least two competing assessments. An evidence update names its prior assessment. Alternative rules and questions retain their respective identities. |
| Handoff | One authorized audience view and a nonempty set of outward statements, each with one exact scope, origin or attributed issuer, and assurance disposition. | A directly verifiable claim includes the authorized proof closure. An attributed claim includes the authorized statement or assurance receipt and its limits. A private source link is conditional on disclosure. Publication receipts are separate from preparing a view. |
| Profile claim | One profile, target and exact criterion. One supported, withheld or unevaluated disposition, scoped to a cutoff and audience. | Evidence for the claimed guarantee, with a reason for a hold. A reported historical profile label remains an attributed capture. |

Where an assessed relationship repeats the question, rule or scope,
the resolved identities must agree with the owning assessment. Compare
resolved targets and selected members, rather than reference spellings.
A linked registration-only update may reuse the original decision by
exact reference. Its evidence view must authorize and cover that
decision and preserve its original frontier. The new receipt belongs
to the registration basis. A substantive correction with changed
measurement creates a new basis and decision.

## Dispositions and canonical encoding

Use closed tagged forms. For the decision axis, a completed state
carries exactly one decision reference. A held state carries a reason
and a scoped gap basis. An unevaluated state carries a reason.
Use the following required states and associated members. Status
tokens describe the evidence in the assessment's own view.

| Axis | Allowed state and its associated members |
|---|---|
| Applicability | applicable with basis, inapplicable with reason and basis, unresolved or disputed with reason and basis, unevaluated with reason |
| Execution | established, unrun or deviated with basis, unresolved or disputed with reason and basis, inapplicable or unevaluated with reason |
| Sufficiency | sufficient with basis, insufficient or held with reason and basis, unevaluated with reason |
| Decision | completed with decision, held with reason and basis, unevaluated with reason |
| Registration | unrequested, unevaluated with reason, unresolved or disputed with reason and basis, assessed with registration |

Historical reported labels remain capture or attribution payloads.
A completed decision has an outcome of met, missed or inconclusive.
Inconclusive requires a named rule branch. A numeric operand that is
mathematically undefined remains a scoped evidence disposition.
Omission is permitted only for explicitly conditional roles. Known empty,
partial, unavailable, restricted and disputed use explicit states.

Use strict UTF-8 JSON with compact sorted keys and S3/S4 string
escaping. Reject duplicate keys, undeclared fields, bare JSON numbers,
null, nonfinite values and invalid Unicode scalar sequences. Explicitly
tag integers and reduced rationals with canonical decimal strings,
positive denominators and zero represented as 0/1 in rational fields.
Compare exact qualified values and preserve display text separately.
Sets are unique and canonically ordered. Keyed arrays are unique and
sorted by key. Sequences preserve declared order. Canonical S5 bytes
must re-encode exactly. Preserve original incoming S1–S4 and native
artifact bytes for dependency identity. Unsupported versions may be
preserved opaquely with provenance. Interpretation requires an exact
reader or explicit versioned conversion with new bytes and source pins.

Use the following candidate limits. They are policy ceilings for the
first support scope. Readers may apply stricter explicit limits.

| Resource | Ceiling |
|---|---:|
| Snapshot bytes and depth | 524288 bytes and 48 levels |
| Records and entries per collection | 4096 records and 8192 entries |
| Bytes per UTF-8 scalar and digits per serialized integer component | 32768 bytes and 256 digits |
| Reference nodes and resolution visits | 32768 nodes and 131072 visits |
| External packages, depth and aggregate closure bytes | 64 packages, 16 levels and 33554432 bytes |
| Predicate nodes, depth and decision visits | 4096 nodes, 32 levels and 32768 visits |

Check bytes, depth and integer text before unbounded decoding or
conversion. Charge repeated reference and predicate visits. Predicate
evaluation consumes qualified inputs and bounded exact comparisons.
It delegates estimator arithmetic to S4. Any stricter predecessor
reader or S3 carrier limit applies. A limit failure records a typed
blocker where a safe assessment can be recorded.

Verify bounded syntax and local shapes first, then exact reference
integrity and access, cross-role semantics, then evidence sufficiency
and claimed guarantees. For publication, an S3 carrier can hold the
exact authorized S5 snapshot as a typed artifact, following S4's
carrier pattern. Verify both dependency closures under the authorized
audience before publish. A content pin has no disclosure authority.

## Four wire walkthroughs

Each row below is one complete logical envelope inventory. The shared
contract identities and evidence sources are the ones named in the
scenario. The JSON fragments show the discriminating payload members,
with fully spelled reference shapes. External evidence is described by
role, so these examples make no claim of cross-package test coverage.

| Snapshot | Local inventory and external evidence | Required round-trip distinction |
|---|---|---|
| Held at A1 | Account, six-case question and R1, basis, held assessment, and scoped assessment profile. Pins intended frame, run observations and the two unresolved members. An optional separately scoped available-pair diagnostic can pin its own S4 result. | Four observed eligible pairs, two unresolved, held full-frame decision, no decision or evaluation occurrence. |
| Inconclusive at B | Account, utility question and bound rule, basis, assessment, decision, and rule decision profile. Pins S4 utility enclosure, its qualifications and applicable S2/S3 delivery scope. | The decision is complete and inconclusive, with a qualified enclosure of [0.08, 0.16]. No point or sampling claim is inferred. |
| Corrected at C | Account, basis, assessment, decision, history and relevant profile claims. Pins the earlier S5 snapshot, its exact question and R1, and the corrected S4 value and alignment evidence. | The corrected 0.09 misses R1. The earlier 0.12 assessment stays resolvable at its own cutoff. A single history link identifies the changed basis and decision. |
| Public restricted view at D | Account, authorized attributed statement or capture, handoff and handoff profile. Pins the public disclosure or assurance evidence only. A private source relation remains with its authorized custodian. | A dated attributed statement and its verification limits survive. The public bytes contain no dependency on hidden case records, private digests or undeclared identifiers. |

Held decision axis. The reference identifies the named gap in the
scoped evidence basis.

~~~json
{"basis":{"expected_contract":{"name":"s5.basis","version":"0.1.0-proposal.1"},"ref_kind":"local","selector":{"key":"full-frame","selector_kind":"member"},"target_id":"basis.a1"},"reason":"full_frame_unresolved","state":"held"}
~~~

Completed decision axis for B. The selected decision record carries
the inconclusive branch and both endpoint checks.

~~~json
{"decision":{"expected_contract":{"name":"s5.decision","version":"0.1.0-proposal.1"},"ref_kind":"local","target_id":"decision.b"},"state":"completed"}
~~~

The outcome in that record keeps the decision distinct from a hold.
Its clause trace references the qualified enclosing quantity and
records that both sufficient endpoint tests evaluated false.

~~~json
{"branch":"enclosure_straddles_cutoff","state":"inconclusive"}
~~~

Corrected history target for C. Its dependency descriptor pins the
whole earlier S5 snapshot. The local successor and adjudication basis
are separate required history roles.

~~~json
{"dependency_key":"prior","expected_contract":{"name":"s5.assessment","version":"0.1.0-proposal.1"},"ref_kind":"external","target_id":"assessment.a2"}
~~~

Restricted public assurance for D. Its source is a local attributed
statement whose proof and permitted scope resolve within the public
closure. A public audience does not obtain private evidence through it.

~~~json
{"mode":"attributed","source":{"expected_contract":{"name":"s5.capture","version":"0.1.0-proposal.1"},"ref_kind":"local","target_id":"statement.d"},"verification":"statement_integrity"}
~~~

These cases expose four validation requirements. A hold can reference
a basis member with explicit missingness. A completed inconclusive
decision requires an actual decision record. A correction needs a
pinned historical target and independent adjudication basis. An
authorized attributed handoff can stand without a public reference to
the private assessment. Check these together in golden package round
trips, including equal-looking payloads under changed versions or
different audience pins.

Next, review operation signatures, recovery and explicit legacy
mapping. Specify who supplies scoped evidence and authority, how a
recording retry differs from reassessment, and which historical
claims can be mapped without expanding their meaning.
