# Subsystem 1: variable domains, coordinates and mappings (1 Nov 2026)

Tickets: DLV-08, DLV-09; neighbours DLV-10, ADV-01, DLV-06.
Status: proposed semantic specification; design only, no implementation or adopted protocol change.
Parent: [Foundation contract](system-connections-foundation-contract-2026-11-01.md).

## 1. Accepted basis and this proposal

Uzair accepted the minimum preservation/interpretation distinction and the broad foundation direction, then
requested precise domain/mapping and output-family design. This document proposes fields, subtypes and
invariants; exact wire schemas/version names and each detailed rule are not adopted merely by being written.
Unknown original identity remains permissible for evidence preservation, not an invented semantic mapping.
Only subsystem 1 is in scope.

## 2. Four distinct notions

| Notion | Definition | Example |
|---|---|---|
| Variable identity | A declared variable in an identified native/measurement/model namespace | The measured quantity represented by a dataset's temperature variable |
| Domain membership | A variable or structured variable coordinate eligible for an object's claims | Temperature at relative time -1 in a particular temporal domain |
| Representation binding | Where/how that member is encoded in a particular payload/schema | Column 2, a matrix axis entry, native node token or category code |
| Presentation label | Text shown to the native system or reader under an identified view | temperature, V2, or a repeated display name |

A reusable concept label can relate variables across sources, but does not prove equal measurement,
population, sampling domain, representation or statistical identity. Default identities are source-scoped.
One display string may denote different variables; one variable may have several display labels.
The common contract never joins by label/array shape alone.

## 3. Proposed records and fields

R = required for the named interpreted contract; C = required when applicable; O = optional enrichment.
Required historical unknowns use the foundation knowledge wrapper. If unknowns block a subtype's semantics,
preserve evidence but withhold that interpretation claim. References may replace inline content.

### D1. Variable descriptor

| Field | Presence | Meaning |
|---|---|---|
| variable_ref | R | Stable source-scoped identity; separate from labels/positions |
| definition_scope | R | Dataset/schema, native model/encoder or other authority under which identity is defined |
| meaning | R | Evidenced native/measurement definition, or explicit unresolved meaning |
| roles | R | Known roles and their basis, or unresolved; roles are not one exclusive enum |
| value_space | R | Typed description/reference or explicit unresolved description |
| concept_refs | O | Related external/common concepts; relation and evidence, not automatic equivalence |
| provenance | R | Source definition/observation and producer/basis |
| derivation_refs | C | Inputs/procedure for an explicitly derived variable |

Roles include observed measurement, learned representation, latent variable, context indicator, intervention
indicator and auxiliary variable under defined role contracts. A context indicator can also be observed.
Being unobserved in this payload is not proof that a variable is scientifically latent. Unknown roles are
not silently assigned to observed measurement.

Initial value-space subtypes: boolean; categorical with identified levels/codes; integer; real; ordered
categorical with an explicit order; vector/tensor with component/axis domains; and opaque native value space.
Units, category meaning, encoding, allowed/missing/nonfinite values and measurement representation are
conditional fields. Opaque describes a limit, not universal numeric semantics. A real variable is not
automatically continuous under every scientific interpretation.

Variable definitions and schema snapshots are immutable. A changed definition creates a new descriptor or
related variable; correction/equivalence claims retain their evidence history. Stable identity does not
require silently overwriting the earlier definition.

### D2. Domain snapshot

| Field | Presence | Meaning |
|---|---|---|
| domain_ref and contract | R | Immutable domain identity and subtype/version |
| definition_scope | R | Source/model/task context defining its members |
| members or domain_expression | R | Explicit finite members, or a versioned expression with reader support |
| member_identity_rule | R | Stable member keys/references; no label-only identity |
| dimensions | C | Named coordinate dimensions with exact value/offset/unit conventions |
| extent | R | Enumerated/partial/symbolic extent and source scope; not a global completeness assertion |
| admissibility | C | Defined allowed query tuples, pairs, lags, endpoints or self-relations |
| provenance | R | Basis for membership, scope and dimensions |

An interpreted finite graph's node set must be explicitly enumerable. Large domains can use external immutable
tables with stable keys. Symbolic query domains may be retained, but membership/coverage checks require a
supported expression reader; an arbitrary string is not an executable universe definition.

### D3. Representation binding (schema/axis view)

| Field | Presence | Meaning |
|---|---|---|
| binding_ref, contract | R | Immutable schema/view identity and meaning |
| payload_ref and source_scope | R | Which artifact/object/interface representation is described |
| axes | R | Ordered axis identifiers, lengths and coordinate/member bindings where relevant |
| index_convention | C | Zero/one based, native row/column direction and other position conventions |
| labels | C | Actual rendered/native labels keyed to members/positions; duplicates permitted |
| value_encoding | C | Units, categorical codes, dtype/precision, masks and native missing-value conventions |
| source_domain_refs | R | Domains represented, including unresolved associations explicitly |
| provenance | R | Evidence for the binding; never inferred from matching shape alone |

Sample/row axes differ from variable axes. Dataset/environment/partition/time identities must retain their
role. Do not assume row count equals effective sample size or that rows are independently exchangeable.
Tensor shape is checked against declared axes but does not establish the scientific meaning of those axes.

### D4. Mapping/transformation descriptor

| Field | Presence | Meaning |
|---|---|---|
| mapping_ref and contract | R | Immutable mapping identity, kind and version |
| source and target | R | Exact domain/schema/snapshot references |
| purpose and authority | R | Presentation, coordinate interpretation, feature construction or evaluator alignment; who supplied/derived it |
| mapping_data | R | Explicit table or identified deterministic procedure/configuration |
| coverage | R | Source/target coverage, unmapped members and ambiguous candidates |
| asserted_properties | R | Identity-preserving, injective, surjective, invertible, partial or lossy claims, each with basis |
| verification | R | Which properties were checked, against which snapshots, and result/gaps |
| lineage and losses | C | Composed inputs, derived variables, changed values/claims or omitted scope |

No identity-preserving or invertibility default. A procedure is not an invertibility proof.

## 4. Selected domain subtypes and limits

| Subtype | Additional requirements | Initial claim supported |
|---|---|---|
| Finite named variables | Unique variable/member references, explicit finite membership | Graph/claim/quantity domains over identified variables |
| Components/blocks | Parent variable, component-domain identity, stable keys and grouping | Preserve scalar versus vector/block identity without silently flattening |
| Relative temporal coordinates | Base variable, reference frame, offset units, sign convention, allowed lag window; stationarity/template claim separately stated | Interpret explicit lagged nodes/links under a named temporal extension |
| Absolute temporal coordinates | Base variable, timestamp/calendar or sequence index, precision/timezone where applicable | Distinguish particular time instances from a stationary template |
| Context/grouped domains | Dataset/environment/group dimensions and their role as scope or actual node coordinates | Preserve per-group objects and explicit context nodes without inventing pooling |
| Learned-variable domains | Native encoder/model snapshot, factor/component keys, learned-domain identity | Identify factors within that model; no automatic alignment across fitted models or truth variables |
| Relational descriptors | Schema/perspective, entity/relationship/attribute/path identities and native interpretation contract | Preserve structured relational identity; deeper path/grounding equivalence requires a supported extension |
| Native extension domain | Namespaced contract/version, source evidence and criticality | Preserve identity/content while withholding unsupported membership/mapping semantics |

Relational identity is not collapsed to a string label or promised to have a universal flat-column mapping.
The initial relational descriptor supports referencing an explicitly defined native domain. A subtype-specific
reader is needed before claiming interpretation of its relational path semantics. Similarly, an opaque
learned factor can be identified without claiming what real-world cause it represents.

## 5. Mapping kinds and invariants

### K1. Exact coordinate relabeling/permutation

Defined on explicit source/target members; total bijection on the declared covered sets for a full permutation.
Check unique source and target keys, coverage, inverse on that scope, consistent axis lengths and all affected
references. Display labels may change without changing member identity. A column permutation is not a value
transformation or authority to reveal hidden labels.

### K2. Partial identity correspondence / subset selection

Declare matched and unmatched members plus selection scope. Injectivity, if claimed, must be checked on the
matched part. Missing members remain unmapped; do not fill outputs with zeros or negative claims. Selecting
variables can change a scientific problem, so selection is identified separately from a pure permutation.

### K3. Value representation conversion

Declare source/target value spaces, units/codes/precision, exact procedure and information loss. A documented
unit conversion or categorical recoding can preserve represented measurements under a stated contract; it is
not justified by equal shapes. Numerical round-off and native missing-value conversions remain visible.
Do not infer that arbitrary value transforms preserve causal claims or the audited algorithm's behavior.

### K4. Feature construction / aggregation / expansion

Create explicitly derived variables, with input members and procedure. Examples: one-hot features, window
averages, log-transforms and learned encodings. One-to-many or many-to-one relations cannot be advertised as
ordinary variable permutations. Grouping or collapsing resulting claims needs its own explicit derived view.

### K5. Semantic correspondence / evaluator alignment

State the criterion, procedure/version, fit/reference data, allowed information, candidates and ambiguity.
Keep it separate from native variable identity and native presentation. Alignment to evaluation truth is a
downstream derived view; it must not leak truth into the native request. Equal scores or factor labels do not
establish a unique match. Cross-model learned-factor identity requires evidence, not reuse of factor_0.

### K6. Native encoding decode

Bind native node tokens, adjacency matrix convention, edge keys or offsets to defined members and predicates.
Use documented/evidenced conventions. Unknown matrix direction/sign means interpretation is unresolved,
even if dimensions are valid. Decode and coordinate relabeling may compose, with both procedures retained.

### Shared invariants

- All source/target references resolve or are explicitly unresolved under the foundation rules.
- Members have unique scoped identities. Duplicate labels are allowed; duplicate member keys are not.
- A total/bijective claim requires demonstrated coverage and uniqueness in its scope; no implicit completion.
- Composition verifies that the intermediate domains/schema versions match and propagates unknowns/losses.
  A composite cannot claim stronger preservation than its constituent mappings justify.
- Apply mappings to every linked variable-bearing field: endpoints, confidence propositions, parameter axes,
  interventions, constraints, stage objects and collection members. Missing mappings yield scoped diagnostics.
- A reverse mapping is exposed only where its prerequisites hold. A many-to-one map has no inferred inverse.
- Context/lag/component coordinates remain attached; map base identity without dropping other dimensions.
- Reference-only/evaluator mappings are not automatically part of system-facing information.

## 6. Concrete domain and mapping examples

All examples are hypothetical design records; short IDs are explanatory labels, not final UUID syntax.

### V01. Reordered columns with neutral names

Source domain D0 has members a=age, s=smoking and y=outcome. Shown schema S1 has positions:

| Shown position (zero based) | Native display | Stable source member |
|---|---|---|
| 0 | V1 | y |
| 1 | V2 | a |
| 2 | V3 | s |

Mapping M1 binds [0,1,2] to [y,a,s] with evidence from the presentation procedure. A native edge 1 -> 0 becomes
a -> y. A quantity attached to that edge must be mapped to a -> y too. Keeping the graph mapping but leaving
the confidence matrix in shown order fails association checks. The system receives the authorized S1 view,
not the hidden source labels or inverse evaluator mapping.

### V02. Duplicate names and unresolved historical positions

Two native nodes both display score. Their distinct source keys can still identify them. If an old file
contains only those labels and no distinguishing key/order evidence, preserve both source entries and the
ambiguous correspondence. Do not choose a match by alphabetical order or artifact proximity.

### V03. Temporal autorelation

Domain DT defines relative coordinates with offset 0 at the target time, negative integer steps in the past,
and a stated sampling step. Members (x,-1) and (x,0) are different nodes. The edge (x,-1) -> (x,0) is not a
same-coordinate self-loop. A source using positive lag 1 must be decoded under its own convention, not merely
copied into offset +1. A stationary template claim is separate from recording one time-specific relation.
Tigramite's native documentation distinguishes time-series CPDAG and PAG outputs [S1]; the proposed coordinate
contract is our design, not an assertion that all temporal outputs share one encoding.

### V04. One-hot expansion

Native category variable c has levels red/blue/green. The adapter constructs r/b/g indicator features.
Each feature has a new derived-variable identity and mapping from c's value space. A graph over indicators
is a graph over that expanded domain. Turning it into a graph over c is an additional projection, with an
explicit aggregation/ambiguity policy; no universal collapsing rule is assumed.

### V05. Learned factors across fits

Model E1's factor_0 and E2's factor_0 have different learned-domain identities. A proposed alignment can link
them with a criterion and evidence; it does not rename them into the same native variable. An alignment that
uses evaluation references is retained only in the evaluation-derived context.

### V06. Groups versus graph nodes

Two environments provide measurements of x and y under declared schemas. Graphs G_A and G_B can share an
evidenced variable domain while differing in environment scope. Environment A is not automatically a graph
node. If a native system explicitly includes a context variable, that variable has its own member identity
and role. Equal labels across independently measured datasets alone do not prove a shared domain.

### V07. Changed variable universe

An online system's D1=[x,y] later becomes D2=[x,y,z]. The new domain snapshot explicitly retains established
identities of x/y and adds z. Earlier graphs over D1 make no prediction about z. A new mapping cannot turn
their missing z entries into no-edge statements.

### V08. Relational perspective

Employee.salary and a department-related salary aggregate require different structured identities, including
perspective and derivation. A raw token salary is insufficient to merge them. If the reader does not support
the native path semantics, retain the relational descriptor/source with an interpretation gap; do not flatten
it into an ordinary observed column and claim equivalence.

### V09. Matrix axes and value codes

A sufficient-statistics matrix can have separate row/column axis bindings referring to D0, plus a sample-size
quantity with its own meaning. It is not a raw-sample table. Likewise, a category code 0 is not a numeric zero
measurement unless its value-space contract says so. Any conversion must preserve those distinctions.

### V10. Partial mapping

A native graph contains u,v,w; only u/v are associated with target-domain members. Preserve the whole native
graph. A mapped view can cover u/v with explicit unmatched w and cannot claim full graph equivalence. Edges
incident to w do not silently disappear into negative predictions or zero-valued confidence.

## 7. Boundary and next specification

The generic core checks schema/reference/axis consistency, mapping properties and declared preservation scope.
Adapters provide native conventions, source bindings and evidence. Neither invents semantic equivalence from
labels, shared shape or convenient evaluation outcomes. Scientific alignment and metric choices remain
separate consumers, not hidden mapping defaults.

The companion [output subtype specification](system-connections-output-subtypes-2026-11-01.md) uses these domain
and mapping contracts. Wire JSON schemas, exact API signatures, full composition examples and compatibility
mapping remain before final subsystem-1 design review. These semantic fields/invariants are proposed, not
runtime-validated. No source code, tests, results, protocol, public contracts or protected paths changed.

## Sources

[S1] [Tigramite native method/output overview](https://github.com/jakobrunge/tigramite), consulted 1 Nov 2026.
Source evidence supports the motivating output distinctions; field names, subtypes and rules here are proposed design.

## Where we're going

Review these domain identities and mapping guarantees alongside the output subtype contracts, then exercise
them in complete records. Resolve any unsupported domain extensions explicitly before final schema/interface
review and subsystem-1 bundle planning. No implementation is authorized.
