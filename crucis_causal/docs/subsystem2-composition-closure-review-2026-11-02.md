# Subsystem 2 composition review: proposed resolutions and open contracts

Tickets: DLV-08, DLV-09; related DLV-10, DLV-06/07 and ADV-01.
Date: 2 Nov 2026, America/Los_Angeles.
Status: design review following Uzair's request for complete linked examples.
Proposed resolutions require review; no wire freeze, implementation or adoption.
Companions: [linked definitions](subsystem2-linked-experiment-examples-2026-11-02.md),
[logical registry](subsystem2-linked-experiment-examples-2026-11-02.json),
[source map](subsystem2-design-rebase-2026-11-02.md).

## 1. Composition gaps and proposed resolutions

| ID | Exposed question | Proposed resolution | Cost and prevented failure |
|---|---|---|---|
| J01 | What does a plan reference before a dataset/episode exists? | A planned case/trial slot and a bounded selection/materialization requirement. Later receipts bind actual immutable cases/collection members. | More explicit lifecycle relations; prevents placeholders being counted as captured datasets or future values being invented. |
| J02 | How does a frozen plan acquire actual outputs? | It does not change. New run, observation and analysis bindings refer back to the fixed plan and its declared requirements. | Extra immutable bindings; prevents an outcome-bearing latest plan from replacing original intent. |
| J03 | How can collection/member and other legitimate links avoid recursive hash definitions? | Assign stable record identities separately from content digests; define digest/package boundaries without recursively hashing a digest that includes itself. | Requires exact later canonicalization/resolution rules; prevents unconstructible identifiers or unstable parent/child references. |
| J04 | Could a generic plan bundle leak evaluator information into native inputs? | Materialize an explicitly permitted typed presentation projection with recipient/channel scope; never forward the entire plan by default. | Native binding/isolation evidence; prevents references, inverse maps and selection metadata becoming hidden inputs. |
| J05 | Does a declared external/restricted reference count as resolved evidence? | Local descriptor closure is distinct from authorized retrieval, integrity and interpreted reference applicability. Preserve scoped unresolved states. | More readiness levels; prevents a valid link masquerading as captured truth or access authority. |
| J06 | How do native requests receive S2 intent without competing definitions? | S2 owns scientific bindings; a versioned handoff maps to the existing S1 operation/scope/deliverable/policy/completion contract mechanisms. Do not add arbitrary fields to SC-1. | Exact interfaces/parameter binding remain to be specified; prevents duplicate request truth and incompatible schemas. |
| J07 | Can one ready/complete flag summarize the experiment? | Assess preservation, semantic interpretation, materialization, invocation, metric applicability and authority at named boundaries. Each result names inputs/evidence and limits. | More scoped assessments; preserves partial and retrospective usefulness without invented guarantees. |
| J08 | Which actual records contribute to each denominator? | A versioned analysis-population receipt binds the rule, exact source observations/output selections, included and missing identities, weighting and reasons. | More evidence storage; prevents silent successful-only selection, collapsed repetitions or reference-version mixing. |
| J09 | How are incomplete reference claims and valid alternatives judged? | Bind proposition/omission meaning and admissibility rules explicitly. Compatibility, request completeness and correctness stay separate; transformations/closures are derived views. | More family readers and metric readiness; prevents fabricated negatives or arbitrary best-reference/orientation selection. |
| J10 | Can a hypothetical grant or ledger template authorize controlled evaluation? | No. Keep policy requirements, actual authority evidence and admission/exposure receipts separate, with real read limits and owner policy unchanged. | S3/owner integration remains; prevents accidental privilege or read-budget reset from a design record. |
| J11 | How is chronology represented without fake timestamps? | Distinguish declared event order, observed local sequence, source times and commitment assurance. Future instances need actual provenance; specimens use explicit hypothetical order. | Extra temporal evidence; prevents current authoring time or lexical ID order supplying original preregistration. |
| J12 | Does logical obligation coverage imply implementation/scientific coverage? | Label declared rules, gaps and illustrative branches as such; reserve native, semantic, detector and empirical claims for their evidence. | Additional claim accounting; prevents a parsed registry becoming proof of complete support. |

These settle proposed conceptual direction only. Reference/cardinality, canonical
digest, state/gap encodings and assessment-reader algorithms are not frozen here.
When the user accepts a particular resolution, retain its scope and alternatives;
do not treat an instruction to continue as approval of all future wire choices.

## 2. Source-obligation map

The registry inventories the current numbered responsibilities:

| Source category | IDs | Count |
|---|---|---:|
| Case/revision | C1-C7 | 7 |
| Collection release | R1-R6 | 6 |
| Membership | M1-M5 | 5 |
| Task | Q01-Q08 | 8 |
| Reference | F01-F08 | 8 |
| Reference/response semantics | S01-S12 | 12 |
| Condition/information | I01-I10 | 10 |
| Transformation | T01-T12 | 12 |
| Comparison/repetition/missingness | C01-C12, separately namespaced from case IDs | 12 |
| Lifecycle/commitment/release | L01-L12 | 12 |
| Total ownership/traceability obligations | | **92** |

For each obligation the registry names owning records, their review-account paths
and whether the example declares a rule or preserves a gap. This is an inventory
of design coverage, not an independent proof of the rule, exact field sufficiency,
scientific validity or tested support. No omission is interpreted as passed.

## 3. Extension variants required before a broader freeze

| ID | Variant | Required closure checks |
|---|---|---|
| X01 | Temporal/grouped evidence with overlapping windows | Explicit coordinates and source overlap; a row-shuffle/subset cannot silently erase time or subject structure; temporal response/reference scope must align. |
| X02 | Relational or distributed evidence | Domain/perspective and party/partition identity; restricted references and actual permitted message/remote access; no assumed central sample table. |
| X03 | Learned variables/encoders | Distinguish observed and learned domains; alignment procedure, ambiguity/valid alternatives and provenance; no best-score latent matching hidden in the adapter. |
| X04 | Posterior/model/graph collections and confidence | Member/weight meaning, native versus derived thresholds and event scopes; one request's samples do not become independent scientific cases; partial truth limits calibration. |
| X05 | Multi-environment interventions and changed measurements | Match targets, intervention semantics, sample/group membership and noise/proxy references; preserve underlying-versus-observed target distinctions. |

These are review requirements, not implemented integrations or completed detailed
specimens. Map them to the existing capability axes/cases and define profiles that
can honestly preserve/interpret/evaluate them; unsupported combinations retain gaps.

Follow-on design pass: [D-H extension definitions](subsystem2-extension-composition-2026-11-02.md)
and their [logical registry](subsystem2-extension-composition-2026-11-02.json) now
compose X01-X05 with explicit adverse/ambiguous outcomes. The
[candidate family/profile/lifecycle contract](subsystem2-family-profile-lifecycle-contract-2026-11-02.md)
proposes joined-boundary requirements. The earlier table remains the historical
review requirement; this follow-on records a design treatment, not native support,
executed conformance or final semantic/wire acceptance.

## 4. Bounded work remaining

1. Review the linked examples and J01-J12 resolutions; resolve exact family and
   profile obligations, including X01-X05 and missing-assessment semantics.
2. Specify record/reference and lifecycle/cardinality contracts: source declarations,
   planned slots, realizations, case revisions, run bindings and population receipts.
3. Perform serialization/canonicalization, external/restricted resolution, exact
   S1/S2 interface/ownership and legacy item/arm/replicates mapping passes. Preserve
   existing stored numbers, certificate rules, finding identities and paper pointers.
4. Recompose complete examples under that candidate contract, including negative
   cases. Logical review alone is not executable schema or runtime acceptance.
5. Final subsystem-2 design review, followed by implementation DAG/bundles and their
   must-show gates. Building still requires its own explicit go.

No public truth-tier, regime, finding or sealed policy changes are adopted. No
protected/shared files, native code, actual sealed data or results are altered.

## Where we're going

Use the gaps exposed by composition to settle precise semantic/lifecycle contracts
before convenient serialization decisions. Keep proposed resolutions and actual
acceptance distinct, maintain the methodology trail, and continue design only.
