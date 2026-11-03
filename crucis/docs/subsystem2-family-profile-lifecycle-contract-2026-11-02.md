# Subsystem 2: candidate semantic families, support profiles and lifecycle rules

Tickets: DLV-08, DLV-09; related DLV-10, DLV-06/07 and ADV-01.
Date: 2 Nov 2026, America/Los_Angeles.
Status: precise conceptual candidate for discussion, not final wire/schema/API,
implemented support or adopted public protocol. Uzair authorized the extension
composition and family/profile design pass; particular choices remain for review.
Basis: [extension examples](subsystem2-extension-composition-2026-11-02.md),
[registry](subsystem2-extension-composition-2026-11-02.json),
[J01-J12 closure](subsystem2-composition-closure-review-2026-11-02.md),
[source map](subsystem2-design-rebase-2026-11-02.md),
[capability map](system-connections-capability-map-2026-11-01.md),
and inspected S1 `audit/connections/{schema,domains,families,history}.py`.

## 1. Composition, not a giant type per system

Use independently versioned semantic contracts for the dimensions below. A single
experiment chooses compatible contracts and binds their identities/parameters.
A new combination such as distributed temporal intervention data need not acquire
a system-named scientific rule. It still needs a compatibility contract/check at
each joined boundary; the cross-product is not automatically supported.

| Family dimension | Required meaning and conditional extensions |
|---|---|
| Evidence population/source | Static snapshots, bounded generation/episodes, streams/windows, groups/sites; selectors, sampling frame, scope/completeness and lineage |
| Access representation | Captured samples, sufficient statistics, callable/remote interfaces, partitioned sources, model/state references; actual availability and limits |
| Variable/domain identity | Atomic/component, temporal coordinates, grouped/context, relational perspective and learned domains; canonical identity, native coordinates, units/roles and mappings |
| Question/response | Global/local/temporal/relational claims, graph family, orders/constraints, quantities, models and collections; target universe, omission, abstention and valid alternatives |
| Reference/evaluation target | Complete/partial assertions, exact/contested/provenance/mismatched legacy association, admissibility/alignment, baseline/environment/proxy/latent target and coverage |
| Transformation/information | Presentation bijections, value conversion, sampling/measurement/feature construction, knowledge and interactive policies; preservation/losses, source-to-derived bindings and disclosure |
| Comparison/randomization | Matching/cardinality, trial/draw/attempt identity, overlap/nesting/weighting, native/transform/data randomness, adaptive and missingness rules |
| Commitment/authority | Binding times, prior/future evidence, immutable snapshots, source resolution, readiness assessments, grants, disclosure/exposure and amendments |

The baseline foundation remains source-scoped identity, contract version, actual
author/importer provenance, explicit observations/claims/gaps and reference extent.
S1 supplies reusable artifacts/domains/output/policy/history contracts; S2 supplies
scientific bindings and relations. Exact wire encoding comes later. Unknown native
semantics remain evidence-preservable, not automatically interpreted/evaluable.

## 2. Minimum contract declaration and composition checks

Every selected family contract must identify:

1. Its exact identity/version and scientific meaning, including target and scope.
2. Required/conditional evidence, domains, parameters and supported native bindings.
3. Interpretation of absence, uncertainty, ambiguity, alternatives and incomplete
   coverage where applicable; no implicit graph or negative-answer defaults.
4. Allowed transformations/relations and the properties, losses, prerequisites and
   reference-applicability changes that each claim requires.
5. Relevant unit, grouping, multiplicity, state and randomization relationships.
6. Information/access/exposure boundaries and when facts must be resolved.
7. Named assessment procedures/required evidence and their precise claim limits.
8. Compatibility requirements for other selected contracts and a defined unsupported
   case behavior that preserves evidence while withholding affected guarantees.

Do not treat a foreign contract name/URI as executable code or fetch a handler
automatically. A reader claims a supported exact contract or an explicitly justified
compatibility interpretation. Native adapters translate evidenced representations;
the common core grows reusable scientific semantics/readiness rules rather than
duplicating them per system. Unknown extensions are not swallowed into successful
interpretation by an arbitrary metadata object.

## 3. Five proposed support profiles

These names are design handles, not registered SC-1/S2 profile identifiers or claims
that the implementation exists. A profile is a set of scoped obligations, not a
universal ladder or one global valid flag.

| Profile | Required claim scope | Required basis and limits |
|---|---|---|
| Preserve | Preserve the identified case/plan/source/observation and its bounded claims/gaps | Local identities/reference closure, author/source basis and extent; unresolved native meaning/history is allowed and limits use |
| Interpret | Interpret named semantic contracts for specific domains/tasks/relations | Supported readers, mappings, coverage/omission and applicable invariants; not proof of truth, execution, complete capture or all-family support |
| Bind inputs/sources | Bind a declared condition to materialized inputs or a bounded interactive/distributed source policy | Exact sources/recipes/realizations, actual mappings/checks and per-boundary state/access limitations; source access need not produce central raw samples; actual authority/execution remain separate |
| Bind evaluation | Bind a specific comparison to eligible outputs/references, metric contracts and exact analysis populations | Supported response/reference alignment, applicability, selection and missingness/weighting/dependence rules; may apply to historical evidence without fresh input materialization; no computation or stronger inference implied |
| Commit/release account | Account for fixed intent, bounded later choices, chronology, amendments, authority and controlled disclosure | Exact snapshots/dependencies, timing/exposure evidence, decision/admission/disclosure receipts at required scope; not automatic preregistration, blindness or permission to execute |

Every stronger interpretation claims preservation for its scope. Evaluation binding
needs the relevant interpreted families and applicable evidence, not a new run by
default. Input/source binding and commitment accounting can be independently useful;
neither alone implies a metric is scoreable. Authority is required for a real
effectful operation under its actual scope, not produced by profile conformance.

A support declaration therefore names the profile, family/feature contracts,
subject/mode/environment, scope, procedure/implementation versions, validation
evidence and limitations. Current S2 status for every profile is proposed/unbuilt.
Existing S1 features retain only their separately evidenced support. No native
integration is added by including a system in the capability-map relation.

## 4. Logical lifecycle and cardinality rules

| Subject/relation | Proposed rule |
|---|---|
| Cited definition | Exact immutable snapshot; working drafts remain distinct. Corrections/amendments create related snapshots, not changed historical contents. |
| Planned slot | One intended role/unit under a requirement/selection rule, not an actual data case, native attempt or independent sample. |
| Resolution candidate/receipt | Zero or several candidate observations may exist. An effective run/analysis binding requires an explicit selected realization for each required single-valued role; no default latest/best candidate selection. |
| Source/case realization | Binds actual evidence/domain/state snapshots under a rule. Distinct draws/episodes receive appropriate identities and shared-source/dependence links. |
| Collection/member | Release pins exact members/case revisions; deliberate multiplicity/selection slots are explicit. Reuse does not create independence. |
| Domain/model mapping | Source/model/domain identities and coordinates remain immutable; a new encoder/window/perspective cannot silently reuse old identity. Alternative/lossy mappings retain ambiguity and derivation. |
| Run binding | Selects exact plan and permitted materialized/source/subject mappings under its frozen resolution rules; S1 request occurrences remain the execution-intent records. |
| Observation/history | New scoped observation/receipt references its actual subjects and earlier requirements. Prior evidence may inform a retrospective plan; future outcomes cannot be dependencies of its earlier fixed intent. |
| Analysis population | Names the exact comparison rule, selected output/reference interpretations, included/unmatched/missing identities and weights/reasons. One observation may legitimately support several dependent analyses. |
| Assessment | Names claim/profile, subjects, input revisions, boundary/time, procedure, evidence, outcome and explicit gaps/conflicts/limits. Structurally valid evidence is not one universal readiness result. |
| Authority/exposure | Policy requirements, actual applicable grants, admission and actual disclosure/use observations stay separate; failed/partial events retain their consequences under owner policy. |

These rules constrain cardinality/meaning without choosing final field names, tagged
unions, canonicalization or reference syntax. Opaque assigned identities and content
digests remain distinct to avoid recursive hash definitions. Exact single-valued
resolution, cycle rules, external/restricted references and conflict projections
must be settled in the serializer/interface pass.

Adverse outcomes retain all applicable dimensions: a native failure with a stage,
permitted abstention, unsupported interpretation, missing reference, nonconforming
input and unknown authority cannot collapse into one generic missing value. Unknown
does not mean none, zero, false, no intervention, no edge or no prior exposure.

## 5. Cross-family decisions exposed by D-H

- Time/group windows preserve coordinates and overlap, not a fictitious iid table.
- Relational/distributed bindings preserve perspective, party identity and actual
  access evidence; callbacks/statistics are not invented raw rows or pooled truth.
- Learned alignment is a separate late derived relation under a fixed procedure,
  not identity by index or reference-score maximization.
- Collections preserve native measure/member/parameter/event meaning; derived
  marginal graphs may have different properties than their native graph members.
- Intervention and measurement targets are explicit; baseline mechanism discovery,
  environment-specific graphs and proxy-variable discovery do not share one default
  reference merely because they reuse variables or files.

These constraints are proposed generic core semantics. They require exact supported
reader/assessment procedures later; metadata alone does not establish conformance.
Useful evidence can still be preserved when a stronger family or composition is
unsupported. Do not narrow native outputs silently to make an evaluator appear ready.

## 6. Alternatives, costs and readiness for the next pass

The main alternative is a fixed table/graph experiment format with special-case
handlers for broader systems. It is simpler initially but entangles scientific
meaning with adapters and forces lossy or fabricated mappings. The proposed family
composition costs more explicit contracts and cross-boundary validation. It lets
the core accumulate reusable mechanisms while keeping native adapters focused on
faithful translation, execution binding and provenance.

A single support ladder is also simpler to report, but cannot faithfully describe
historical evaluation without a fresh run, remote access without central rows or
preservation without a semantic reader. The proposed profiles require more scoped
reporting and prevent those false prerequisites or inflated guarantees.

The five variants have now been composed at the logical design level. Exact
family algorithms, source/target validity proofs, statistical procedures, native
converters and operational authority are not thereby implemented or validated.
The next pass can choose bounded serializer/API contracts against these defined
requirements after review. It must not invent additional scientific behavior merely
to satisfy a chosen data shape. Existing protocol, tiers, regimes, results, finding
identities, sealed allowances and paper pointers remain unchanged.

## Where we're going

Review these family obligations, five scoped profiles and lifecycle/cardinality
rules against A-H. Then specify bounded record/reference serialization, exact
S1/S2 interface ownership and legacy mapping, keeping unresolved semantic/owner
issues explicit. Recompose the complete examples under that candidate before
final subsystem-2 design review and implementation DAG/gates. No build is authorized.
