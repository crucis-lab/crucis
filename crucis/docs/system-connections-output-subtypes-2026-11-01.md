# Subsystem 1: output subtypes, fields and invariants (1 Nov 2026)

Tickets: DLV-08, DLV-09; neighbours DLV-10, ADV-01, DLV-06.
Status: proposed semantic specification; design only, no implementation or public-contract adoption.
Parents: [Foundation contract](system-connections-foundation-contract-2026-11-01.md),
[Domains and mappings](system-connections-domains-mappings-2026-11-01.md).

## 1. Scope and validation language

Uzair requested precise semantic families, beginning with domains/mappings and then output subtypes. This
document defines proposed payload fields and invariants. Exact wire-schema/version names and supported
native converters remain to be finalized; this is not evidence that these subtypes are implemented.

Separate four checks: encoding/reference consistency; conformance to a particular declared semantic type;
supported native-to-common preservation claims; and scientific correctness. A checker records exactly which
invariants it checked, which passed/failed and which were not checked/unknown. A legal endpoint representation
does not prove the graph is a valid completed equivalence representation, and neither proves causal truth.

Invalid native data/claims are retained under the evidence contract with diagnostics. A failed asserted
subtype is not silently repaired, relabeled or discarded. A broader interpretation may be emitted only with
its own valid contract and explicit source/limit. Example: a cyclic directed structure can have a directed-graph
view while its native DAG assertion fails an acyclicity check.

## 2. Shared object descriptor and payload obligations

R = required for the interpreted subtype; C = required when applicable; unresolved values use foundation
knowledge wrappers. If a required unknown blocks meaning, preserve native evidence without the stronger claim.

| Shared field | Presence | Meaning |
|---|---|---|
| object_ref | R | Stable occurrence/view identity, separate from content equality |
| contract_ref | R | Exact payload family/subtype and version; native declaration is recorded separately |
| subject/source | R | Native occurrence/source evidence or explicit unresolved original association |
| producer and provenance | R | Producing component/procedure/configuration, source artifacts/locators and basis |
| role/designation | R | Native answer, intermediate, support, checkpoint, diagnostic, action or other defined role; designation evidence |
| domain/scope | R | Relevant variable/member/query/time/environment scope or justified non-applicability |
| payload | R | Inline content or exact artifact/selector references, with availability limits |
| relations | C | Representation-of, derived-from, collection membership, parameter pairing and other typed associations |
| interpretation/checks | R | Exact mapping/check procedures, input basis, checked scope and diagnostics/gaps |

Native origin, internal derivation, response role and finality are separate. A native selected graph and native
particle collection can both exist. An auditor-selected graph is a separate derived view even if its bytes match.
A reported but unretrieved object descriptor need not pretend to have an available typed payload.

Fields below are additions to this descriptor. Shared definitions/references avoid repeating large schemas.

## 3. G: graph and structural relation subtypes

### Common graph fields

| Field | Presence | Meaning |
|---|---|---|
| graph_semantics | R | Versioned family contract and what links/endpoints assert; native family assertion separately sourced |
| node_domain | R | Explicitly enumerable node identities, including structured coordinates where applicable |
| query_domain/coverage | R | Eligible pairs/links and reported/excluded/unreported scope |
| omission_rule | R | What an absent payload entry means within that scope; explicit unknown if not established |
| links | R | Stable link keys, endpoint node refs and typed relation or endpoint marks |
| link_properties | C | Native properties and their contracts/basis; unknown properties retained with interpretation limits |
| quantity_refs | C | Weights/probabilities/scores tied to exact links/propositions, not free-floating arrays |
| assertions/checks | R | Native family/property claims and named checks, including not-checked/failed scope |

An empty links list can be a valid explicitly empty graph only when domain, coverage and omission semantics
establish its meaning. Absence of a graph object is different. Unqueried pairs and gaps do not become no-edge.

### Selected graph subtypes

| Subtype | Additional semantics/fields | Required invariants and limits |
|---|---|---|
| G-directed | Directed relation predicate, node scope, reciprocal-edge/self-link policy | References in domain; direction convention explicit; unique link keys; cycles permitted unless stronger contract restricts them |
| G-DAG | G-directed plus an asserted DAG contract | No same-node self-links and acyclicity required for validated-DAG conformance; retain contradiction/source if failed |
| G-partly-directed | Directed versus unresolved adjacency relations and their family meaning | Do not treat unresolved adjacency as two definite arrows; CPDAG/completedness assertion distinct from merely parsing a partial graph |
| G-endpoint-marked | Marks at each endpoint, source family and legal mark/property meanings | Preserve tail/arrowhead/circle or explicit extensions; symbol alone does not establish causal meaning; PAG/ancestral-family checks named and scoped |
| G-weighted-structure | Link/domain association plus Q quantities, threshold/topology rule if native | A nonzero weight is not automatically an edge or probability; native topology extraction and auditor thresholding remain distinct |
| G-association | Explicit association relation/predicate and scope | No promotion to direct causal or ancestral claims |
| G-temporal | One of the above plus selected temporal coordinate/template contract | Preserve lag sign, units, reference frame and time coverage; no collapse to a static base-variable graph |

Several directed/bidirected links may share a pair only if their graph-family contract permits that structure.
Duplicate links or parallel scientific relations must not be silently merged. Reciprocal directed links,
a single bidirected edge, unresolved orientation and conflicting source assertions are distinct. A conflict
is represented through evidence/claims, not automatically encoded as a confounding mark. Do not force one
exclusive mark per unordered pair when the native contract permits multiple relation types.

Graph-family interpretation claims have limited check scopes. A representation can preserve a native CPDAG
or PAG declaration and endpoints while full family-conformance checking remains unavailable. It must not then
claim full family validation or complete native semantics if relevant properties were not interpreted.
Unknown endpoint combinations/properties retain native evidence and explicit gaps; never coerce them to
undirected and call that a lossless translation.

The motivating FCI documentation returns a PAG and additional edge properties [S1]. The proposed contract
therefore preserves properties alongside endpoints rather than assuming an adjacency matrix is the whole answer.

### O01. Ordinary graph with shuffled axes

Using domain example V01, native edge 1 -> 0 maps to age -> outcome. Its coefficient/probability, if supplied,
must attach to the mapped proposition. A reverse edge caused by a guessed matrix convention is a mapping
failure even if the graph remains syntactically valid. Store both native snapshot and mapped view provenance.

### O02. Partial graph and bounded absence

Native A o-> B is retained under the endpoint-family contract without selecting A -> B. If C was outside
the queried domain, no edge involving C is implied. For a complete reported pair domain, a defined omitted
pair can mean asserted absence, but only under that domain's omission rule.

### O03. Native weighted estimate

A native matrix has entry W[A,B] = -0.7. Q identifies its actual parameter/weight meaning, scale, model and
axis convention. Unless the native output defines a topology rule, the common graph does not silently turn
all nonzeros into causal arrows. A later thresholded graph is a derived object with its rule/configuration.

## 4. C: proposition, set and order subtypes

### C-propositions: individual or local claims

| Field | Presence | Meaning |
|---|---|---|
| proposition_contract | R | Predicate meaning/version, e.g. adjacency, direct relation, ancestry or conditional independence |
| arguments | R | Named role bindings to domain members, not an untyped pair |
| conditioning/context | C | Conditioning variables/values, environment/time scope and relevant native assumptions |
| decision | R | Native assertion, denial, abstention or unresolved answer under the subtype contract |
| query/coverage | R | Which question/domain is answered and whether other entries were queried/reported |
| quantity_refs | C | Specific probability/test/score objects linked to this exact proposition |

Unreported is an absence within an explicitly described query/response coverage, not fabricated native
abstention. Native unresolved direction is distinct from an auditor not knowing what the output means.
Contradictory propositions from different evidence sources retain source identity and can remain in conflict.
Conditional-independence assertions are not silently converted to causal non-adjacency or direction.

### C-set: neighborhoods, parents, blankets and other membership answers

Fields: set predicate/version, target(s), explicit candidate domain, member refs, membership coverage,
omission rule and optional exclusions/abstentions with basis. Duplicate member identities are invalid for
set semantics; a multiset is a different collection contract. Target membership/self rules are subtype-specific.

The predicate distinguishes parents from ancestors, neighbors or a Markov blanket. Complete membership can
justify excluded candidates under that contract; it does not extend beyond the candidate domain. A native
blanket membership statement is not automatically a direct-edge claim.

### C-order and C-ranking

Fields: ordered domain; relation meaning; representation kind (complete order, strict partial order,
cover relations, tied rank groups or score-based ranking); ordered members/pairs/groups; coverage; tie and
unranked-member policy. Scores use Q with direction/scale. A ranking is not necessarily a causal ordering.

Check reference closure, unique member occurrence where required, declared tie grouping and applicable
irreflexivity/acyclicity/completeness. Do not demand transitive closure from a representation declared to store
cover relations; do not treat a missing pair as incomparability unless its coverage/representation establishes
that meaning. A complete order can be supplied as a unique sequence over its exact covered domain.
Neither a causal order nor an ancestry answer invents direct graph edges.

### O04. Local answer with abstention

For target Y, candidates are A,B,C. A complete parent-set response includes A, explicitly abstains on B,
and denies C under the response contract. Those are three distinct statements. It says nothing about D
outside the candidate domain or about edges among A,B,C. A simpler native set containing only A implies
negative membership for B/C only if that set's omission/coverage contract establishes it.

### O05. Ties and unranked members

Ranking [[A,B],[C]] states a tie followed by C under the defined ranking direction. D remains unranked if
coverage excludes it. Flattening to [A,B,C,D] invents a tie-break and a rank for D. If the object is instead a
causal precedence order, that predicate must be explicit; it still does not say A directly causes C.

## 5. Q: scalar, array, interval and uncertainty subtypes

### Common quantity fields

| Field | Presence | Meaning |
|---|---|---|
| quantity_kind | R | Probability, p-value, coefficient/parameter, frequency, weight, count, duration, currency amount, statistic or named score |
| subject/proposition | R | Exact claim/link/object/member/model/accounting scope the quantity describes |
| value and representation | R | Typed scalar/array/interval content with precision, missingness and nonfinite conventions |
| axes/domain | C | Every tensor axis and key; scalar non-applicability explicit where needed |
| units/scale/direction | C | Physical units, currency/price basis, score direction, transformations or log scale |
| conditioning/basis | R | Relevant conditioning, sample/normalization/measurement basis or explicit unresolved basis |
| procedure/source | R | Native-reported, observer-measured or derived procedure/version/configuration |
| associated rule | C | Native decision threshold, normalization, interval construction or statistic definition |

Candidate propositions have their own typed predicate/argument/domain identity. A quantity need not attach
to an emitted graph link: it can describe a relation rejected or absent from a selected graph. Reference
closure checks that the proposition resolves, not that the graph contains the asserted relation. The
[composition review](system-connections-composition-review-2026-11-01.md) demonstrates this distinction and
the resulting explicit record/reference discriminator names.

Specific requirements:

- Probability: exact event/proposition and conditioning; finite value in [0,1] for a validated probability
  value. Joint, marginal and conditional probabilities are different subtypes/conditions.
- P-value: test statistic/procedure and hypothesis meaning, directional setup and conditioning as applicable.
  An unresolved test meaning can preserve a native p-value label but blocks the stronger interpreted-test claim.
  It is not a posterior edge probability.
- Coefficient/parameter: associated model/link, parameterization and axes, units/scale where relevant.
  A signed magnitude does not assert confidence, direct causation or comparable scale across models.
- Frequency: counted event, denominator/replicate scope, counts if available and sampling basis. A fraction
  without a known denominator is not automatically an exact count-derived frequency.
- Weight: nonnegative/normalized/log-weight constraints only under its declared contract. Signed coefficients
  must not be forced into nonnegative weight semantics. Normalization of unnormalized weights is a derivation.
- Count/resource amount: units, measurement scope/source, interval/event and aggregation membership. Missing
  amounts are unknown, not zero. A resource measurement is not a budget or spend authorization.
- Interval: endpoint values/inclusion, target quantity and construction meaning; confidence/credible/prediction
  label, nominal level and method/basis as relevant. Unknown construction is explicitly unresolved, not guessed.
- Array/tensor: axis coordinates and entry meaning; no shape-only matching. Missing, unreported, zero and
  nonfinite entries remain distinct. Invalid native values are retained with diagnostics rather than clamped.

Subtype checks include numeric encoding/precision and axis lengths; actual count values must be nonnegative
integers under a count contract (signed changes require a different quantity meaning). A count-derived rate
identifies numerator/denominator and cannot silently turn a zero/unknown denominator into zero. Ordered
interval bounds must satisfy lower <= upper under the declared scale, with permitted open/infinite endpoints
explicit. Normalization/range checks apply only to quantities claiming those semantics; dimensionally
incompatible units or differently conditioned propositions cannot be combined merely because shapes match.

An unrecognized scalar statistic can use a namespaced score/statistic contract with its actual known scale;
it does not receive probability or calibration semantics. Arithmetic tolerances are procedure-specific and
recorded; the historical 0.001 stored-result gate is not a universal semantic-validation tolerance.

### O06. Existence versus orientation probability

Hypothetically, native output gives P(adjacency(A,B))=0.8 and P(A->B | adjacency(A,B))=0.6. These attach to
different propositions/conditioning. An unconditional arrow probability is a separately derived quantity;
it may be 0.48 only when the definitions establish the required event identity and conditioning. The adapter
does not multiply unlabeled matrix entries or assume complementary directions in every graph family.

### O07. Directional tests and invalid values

The ANM native interface documents separate forward/backward p-values [S2]. Preserve their directional test
meaning; do not turn 0.03 and 0.4 into edge probabilities or a graph without a declared decision procedure.
If a native field labeled probability contains 1.2, capture it and its label, diagnose the range failure and
withhold validated-probability conformance. Do not replace it with 1.0 or a missing-value sentinel.

## 6. L: collections, draws and finite distributions

| Field | Presence | Meaning |
|---|---|---|
| collection_kind | R | Ordered sequence, set, multiset, sample/particle bank, weighted support or finite probability measure |
| member_contracts | R | Permitted typed member contracts; mixed collections need explicit member typing |
| member_keys/references | R | Stable keys/immutable locators and membership/order semantics |
| extent/coverage | R | Expected/observed member scope and partial/missing membership evidence |
| multiplicity | C | Repeated occurrences or explicit counts; omission must not erase repeated draws |
| weights | C | Q references or keyed values with exact meaning and normalization/completeness basis |
| generation/basis | R | Native procedure, claimed target distribution/resampling basis, or explicit unknown |
| associated_objects | C | Parameter/model/quantity references keyed to exact members; no incidental-order pairing |

Set equality, repeated samples and finite measures have different contracts. Equal graphs can be distinct
draws with different associated parameters. Compression is allowed only if required multiplicity, ordering
and associations survive; graph equality alone cannot justify combining parameter-associated members.

A fully normalized finite probability measure requires finite nonnegative masses and total mass 1 under
its stated comparison rule, with complete support or explicitly represented residual mass/domain. An incomplete
support list with unknown omitted mass cannot claim a complete normalized distribution. Particle/sample banks
preserve native generation and target-distribution claims without asserting exact posterior inference or
independent draws. Samples with implicit equal empirical weights do not claim a full exact target law.

Derived marginals, selections and summaries are separate objects with procedure/version and member inputs.
They do not replace the native joint collection or become additional independent runs.

### O08. Repeated graphs with different parameters

Members s1 and s2 contain equal graph G but parameter objects theta1 and theta2 differ. Preserve both sample
occurrences and associations. Member s3 contains graph H. A graph-only multiplicity summary {G:2,H:1} can
be derived, but does not preserve the full graph/parameter joint output. DiBS's documented example returns
graph and parameter samples together [S3], motivating this association contract rather than a graph-only list.

### O09. Partial probability support

A native list supplies masses 0.4 for G1 and 0.3 for G2. Preserve those entries. Without evidence about omitted
mass or normalization, do not rescale to sum to 1 or call the list a complete distribution. A residual-mass
statement can be represented if native evidence or an identified derivation supports it; the possible omitted
graph domain must remain explicit or unresolved.

## 7. M: models, learned representations, mechanisms and state

Initial support is a semantic reference/association contract, not a universal model deserializer.

Fields: role/subtype (fitted model, mechanism, encoder/decoder, parameter bundle, checkpoint/state snapshot),
artifact references, native format/reader contract, component/producer identity, input/output/learned domains,
dependencies and associated graph/member/model references, declared operation interfaces where available,
and interpretation/availability limits. State snapshots include known state-component coverage, with RNG,
optimizer, cache, cursor and action history described only where evidenced.

Mechanism references identify target/parent or input domains and functional/noise interface claims where known.
Numerical parameter tensors use Q and explicit axes. A model file does not prove callable execution, restored
state, independence of noise, learned-variable alignment or causal correctness. Invocation and restoration
are separate operations with evidence. Rich native internals need a documented extension and checked reader.

### O10. Encoder plus learned graph

Encoder E1 defines learned domain Z1. Graph G1 refers to Z1; its parameter object refers to G1/model E1 under
explicit association. An evaluator alignment from Z1 to observed truth variables is a separate derived mapping.
Replacing G1's node IDs with truth labels would erase native identity and introduce unevidenced equivalence.

## 8. T: interaction messages, diagnostics and explicit abstention

These output roles use named contracts and remain scoped to their operation, not a generic graph slot.

| Subtype | Required additional fields | Boundary |
|---|---|---|
| Action request | Operation/endpoint contract, arguments/domain, requesting actor, correlation/session scope and authority-request evidence | Does not execute or authorize the action; unknown/forbidden requests can still be preserved |
| Action response | Referenced request/correlation or explicit unresolved association, responding actor, delivered content/schema and response outcome | A completed action is not a completed parent discovery task |
| Diagnostic | Code/meaning, phase/component, affected subject, source/basis, details and attribution uncertainty | Not automatically a native failure or a scientific finding |
| Explicit abstention | Native decision/source, answered query/deliverable scope and stated reason if supplied | Not absence of response, parser failure or universal task failure |

T contracts share H session/event relations and I information delivery. Detailed authority/action endpoint
contracts remain connection-side review work; no experiment-policy or workflow engine is introduced here.
Output messages may be partial/final at their own boundary without implying parent fulfillment.

### O11. Action delivered, parent still waiting

A discovery session asks for an independence-test result. The response records its conditioning set and test
quantity under the endpoint contract. This child response may complete while the parent graph search remains
active. If no response was observed, record the gap rather than fabricate an abstention or negative test.

## 9. Cross-family invariants and example coverage

- Domain/member/selector references resolve or are explicitly unresolved; no shape/label-based semantic joins.
- Every variable-bearing field follows the same supported mapping lineage, including quantities and members.
- Coverage and omission rules stay attached through views. Missing capture and local scope cannot become
  negative scientific assertions.
- Unknown required semantics block the affected interpreted claim; native evidence survives.
- Preserve native reported identity/roles separately from checked properties. A new parser/view is not a new run.
- Do not infer final selection, independence, family validity, posterior correctness or evaluation eligibility
  from a payload type or number of files.
- Native output ownership is distinct from auditor-derived summaries and measurements.
- Typed validation checks contract invariants and supported preservation, not causal correctness. Family-level
  checks that are absent remain not-checked, even when lower-level representation checks pass.

Domain examples V01-V10 and output examples O01-O11 form design probes. They cover reordering, ambiguous labels,
time coordinates, feature expansion, learned/group/relational domains, partial mappings, graph endpoints,
local answers, quantities, collections, model associations and interaction boundaries. They are not runtime
tests or a claim that every capability-map case now has implemented semantic support.

## 10. Remaining concrete design work

Review these semantic requirements and select any revisions/subtype limits. Then specify exact serialized
schemas/default-free encodings, full sample records and expected check results, adapter/core operation
signatures, selected interaction/recovery/resource relation details and compatibility mappings. Inventory
native converters separately: naming a subtype does not implement a reader for any system producing it.

Shared protocol/public-schema adoption remains W5-coordinated. No implementation, tests, source changes,
result migration, certificate changes, paper/tracker/site edits, API spend or git writes occurred.

## Sources

[S1] [causal-learn FCI output documentation](https://causal-learn.readthedocs.io/en/latest/search_methods_index/Constraint-based%20causal%20discovery%20methods/FCI.html).
[S2] [causal-learn ANM directional p-value documentation](https://causal-learn.readthedocs.io/en/latest/search_methods_index/Causal%20discovery%20methods%20based%20on%20constrained%20functional%20causal%20models/anm.html).
[S3] [DiBS native graph/parameter sample example](https://github.com/larslorch/dibs).
Consulted 1 Nov 2026. These support motivating native-output facts; schema/type design and hypothetical
numeric examples are our proposals, not claims about newly executed systems or measured results.

## Where we're going

Use complete serialized examples to check that domains, payloads, provenance, gaps and profile claims compose.
Resolve subtype/operation/compatibility details before final subsystem-1 review and its implementation plan.
No implementation is authorized.
