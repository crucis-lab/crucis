# Subsystem 1: complete-record composition review (1 Nov 2026)

Tickets: DLV-08, DLV-09; neighbours DLV-10, ADV-01, DLV-06.
Status: design review and proposed resolutions. No implementation, frozen public serialization or adoption.
Follow-on: the bounded encoding checklist below is now resolved as a proposal in
[SC-1](system-connections-serialization-2026-11-01.md); the detailed remaining pieces and provisional gates
are collected in the [final review packet](system-connections-final-review-plan-2026-11-01.md).
Parents: [Consolidated outline](system-connections-contract-outline-2026-11-01.md),
[foundation](system-connections-foundation-contract-2026-11-01.md),
[domains/mappings](system-connections-domains-mappings-2026-11-01.md),
[output subtypes](system-connections-output-subtypes-2026-11-01.md).

## 1. What was checked and what the specimens are

Uzair requested complete records to expose composition gaps before freezing serialization, followed by the
detailed interaction/recovery contracts, exact adapter/core signatures, legacy mapping, final subsystem-1
review and bundle planning. The current step remains entirely within the complete-record design exercise.

The companion [JSON record set](system-connections-composition-records-2026-11-01.json) contains nine
hypothetical scenarios and their defined reference closure: 147 logical records, shared contract/component
definitions, raw synthetic source content, domains, mappings, source observations, object descriptors and
assessment/check expectations. Readable IDs aid review; they are not the final opaque-ID string syntax.
The examples are not stored research runs, implementation fixtures or certificates.

Shared definitions are physically included once. Each case names its root records. Follow typed references
to their closure, including definitions; unrelated cases are not dependencies merely because they share this
design document. Model-domain associations can be cyclic references. Pure derivation/continuation ancestry
must be checked separately, rather than imposing acyclicity on the whole reference graph.

The document is valid outer JSON, but not a frozen schema instance. Some subtype fields remain descriptive
pending final field tables. The deliberate truncated native response is a string inside valid outer JSON.
Every semantic check_expectation explicitly says it has not been executed. Native observations and assessments
are hypothetical scenario statements, not claims that the system was run.

## 2. Complete record walkthroughs

### C1. Reordered graph, failed optional probability

Request c1:request requires a final directed graph over age/smoking/outcome after normal completion. A
probability output is optional. The presented input contains V1/V2/V3 in outcome/age/smoking order.
The source format explicitly declares source-to-target direction, complete pair coverage and omission as
asserted absence. The response includes edge 1 -> 0, an invalid probability string and exit 0.

| Common block | Concrete content/references |
|---|---|
| 1 | c1:record is the observation snapshot; c1:attempt belongs to c1:request |
| 2 | Request-required graph, optional quantity, completion rule, scope and allowed information |
| 3 | Identified hypothetical native/observer/mapper roles; implementation identities explicitly design-only |
| 4 | c1:input, c1:binding and the actual shown-label/axis association; inverse/source labels observer-only |
| 5 | c1:termination, c1:delivery, c1:quantity-gap and a request-specific assessment expectation |
| 6 | c1:graph-native, c1:graph-view and c1:bad-probability as a reported, uninterpreted declaration |
| 7 | Included synthetic input/response content and computed digests scoped to those strings |
| 8 | Request/presentation/mapping/assessment context; no invented session, checkpoint or native transcript |

Mapping pairs p0->y, p1->a, p2->s make the common edge a->y. A failed optional probability parser does not
change the graph or native termination. The proposed fulfillment rule can accept the required graph when
its interpretation requirements hold; no causal correctness follows. A real fulfillment assertion would
need real conformance evidence, not this scenario's check expectations.

### C2. Historical graph, unknown execution, changed location

c2:old-content includes its variable domain, direction convention, coverage and omission meaning. The
import can therefore produce c2:graph while c2:origin leaves the original request/attempt unresolved. The
current decoder is identified; the original native software is not assigned the decoder's identity.

A later access to c2:location returns not-found; a still later access yields c2:new-content with a reversed
edge. Preserve both access observations and distinct byte snapshots. No rule treats the changed location
as a correction to the old prediction or a new native run. c2:later-record says its new outputs were not
examined, rather than asserting an empty graph. Original fulfillment remains unresolved.

### C3. Sample bank, paired parameters and an unselected candidate

c3:collection has s1/s2/s3 with explicit native sequence and multiplicity. g1 and g2 have equal graph content
but different parameter values. Each sample retains its graph, model descriptor and parameter association.
The source declares the hypothetical coefficient parameterization; the numbers are not confidence values.

An additional probability refers to proposition c3:candidate, y->x, although no returned graph contains
that link. The proposition resolves through its predicate, argument roles and domain, not through an
existing edge ID. This is essential for probabilities over rejected/absent candidate relations.

The captured members array is complete within its own scope. Total samples elsewhere in the original run,
target-distribution correctness and independence remain unknown. Equal empirical weights or graph-frequency
summaries would be separate derivations. A sample is not an additional native execution.

### C4. Temporal output with narrow coverage

c4:domain identifies x at offsets -1 and 0, plus y at 0. The explicit decoder maps native positive lag 1
to relative offset -1. c4:graph asserts x[-1]->x[0] only in its declared query scope. These are different
nodes; no same-coordinate self-loop is introduced. The system makes no assertion about y or unqueried pairs.
Stationary-template meaning is unresolved rather than inferred from a temporal filename or graph shape.

### C5. Learned-domain graph and reference-side alignment

c5:encoder defines the learned-factor namespace used by c5:learned-domain and c5:graph. c5:alignment uses a
separate reference artifact to produce c5:aligned-view. Native node identities remain encoder-scoped; the
reference-labeled view has a different producer, purpose and derivation.

The reference artifact is evaluator-only for this import/alignment operation. The original native inputs
remain unknown: possessing a label or marking today's artifact evaluator-only does not prove what the
original system knew. A future binding must explicitly select the system-facing bundle, not forward every
artifact available to the observer. No native invocation occurs in this case.

### C6. Conflicting event observations and pinned assessments

Both exit observations reference c6:terminal-event for the same established process occurrence. Their values
0 and 1 are a genuine conflict candidate, rather than different lifecycle moments. The earlier assessment
uses source1 only; the later assessment uses both and leaves exit unresolved.

c6:published-basis pins c6:assessment1 and c6:earlier-record. The current pointer selects assessment2 under
an explicit policy. Neither changes the earlier basis. The earlier publication must not point to the later
expanded evidence snapshot merely because they concern the same attempt.

### C7. Parser correction on unchanged content

c7:matrix states row-source/column-target. The older view reverses that convention; the corrected view uses
it. Both reference one unchanged snapshot. A typed correction names the affected interpretation, reason,
scope and evidence. Syntax can be legal while preservation fails. This is a new interpretation, not a
native rerun and not newly discovered terminal-event evidence as in C6.

### C8. Closed package containing partial evidence

c8:prefix contains only a truncated response prefix. c8:declared-full preserves a separate report of a full
response at an external descriptor, without bytes or a computed digest. No complete graph is interpreted.

All internal metadata references are defined, so this evidence package can be published as deliberately
partial. Package closure and manifest publication do not claim complete native capture. The prefix digest
binds exactly its 15 captured UTF-8 bytes; it says nothing about the unseen remainder or declared full object.

### C9. Local membership, abstention and ranking

The known request asks for parents of Y among A/B/C and explicitly permits a final per-candidate abstention.
The answer asserts A, abstains on B and denies C. That can satisfy the stated response contract without
settling B scientifically. D is outside that candidate domain.

A distinct predictive ranking groups A/B as tied ahead of C, leaves D unranked and excludes Y. Neither the
rank nor local membership is promoted into a complete causal graph or causal precedence order.

## 3. Gaps exposed and proposed resolutions

| ID | Gap or incompatible assumption | Resolution applied to the design | Cost / failure prevented |
|---|---|---|---|
| X01 | Record kind and mapping subtype both used kind; authoring overwrote mapping record tags | Reserve record_type for the envelope, mapping_kind for subtype, target_type in typed references | More explicit names; prevents silent tag collisions and incorrect reference checks |
| X02 | Quantity assumed to require an emitted graph link | Address propositions independently through predicate/argument/domain records | One reusable proposition identity; preserves probabilities for absent/unselected candidates |
| X03 | Coverage and omission were prose, or inferred from the request | Use structured pair-domain/coverage and omission fields, backed by native format/source evidence | Requires a real source rule; prevents missing entries becoming invented no-edge claims |
| X04 | Understanding an output assumed knowledge of original request | Distinguish object interpretation, delivery/designation and request fulfillment | Additional scoped assessments; permits useful historical interpretation without invented intent |
| X05 | Native producer identity was supplied by an importer-wide default | Keep original producer unresolved when unknown; identify current observer/decoder independently | Localized identity gaps; prevents attribution of old behavior to today's software |
| X06 | Earlier publication used the later expanded record | Pin exact earlier observation/assessment basis; expose current pointer separately | Retains snapshots; prevents changing the historical evidential basis |
| X07 | Parameter array paired by order alone or graph equality | Stable member keys and explicit graph/model/parameter associations; define parameterization | Association records; prevents member deduplication or incorrect parameter joins |
| X08 | Every internal reference graph was assumed acyclic | Allow association cycles; constrain derivation/continuation ancestry under their own relation contracts | Two-pass ID resolution and typed checks; avoids rejecting valid model/domain references |
| X09 | Closed package meant complete native evidence | Separate manifest closure, available content and original-capture extent | Scope metadata; allows honest publication of partial evidence |
| X10 | Evaluator-only labels proved native isolation | Scope access labels to this processing operation and require explicit presented bundles/evidence | Presentation bindings; avoids retroactive claims and accidental reference leakage |
| X11 | A later source and corrected parser were one generic update | Distinguish new evidence, state transition and interpretation correction with pinned inputs | Explicit update type; prevents false reruns or silent evidence replacement |
| X12 | Native content was assumed to be parseable JSON or valid UTF-8 | Keep raw bytes separate from manifest fields; inline UTF-8 text only when exact, otherwise base64 bytes or external snapshots | Payload discriminator; preserves malformed/binary content without corrupting the envelope |
| X13 | Stored record order defined event/sample order | Record explicit event/correlation and collection ordering semantics; general registry order is not execution order | Explicit sequence fields; prevents incidental serializer order becoming scientific history |

These are proposed design resolutions, not adopted public schema changes. The initial field collision was
observed mechanically, not conjectured: nine references expected mapping while their targets had subtype
strings as record kinds. All nine now resolve after separating the discriminators. Other gaps were exposed
by tracing the scenarios and source evidence, not by a newly implemented semantic validator.

## 4. What is ready to freeze, and what is still a candidate

The composition supports freezing the conceptual separation and the following serialization commitments
after Uzair's review:

- Versioned typed records with reserved envelope discriminators, explicit references and namespaces.
- Structured domain/coverage/mapping/omission data rather than prose interpreted as executable meaning.
- Explicit known/unresolved/non-applicable states and conditional-presence rules; no overloaded null.
- Distinct native declarations, captured snapshots, produced interpretations and assessments.
- Exact source selectors/content bindings, scoped availability and independently versioned contracts.
- Separate immutable bases and current selections; explicit publication versus capture completeness.
- Namespaced versioned extensions with scoped criticality, so richer relation families can be added without
  silently changing existing meaning.

Do not label the current JSON a frozen production wire schema. Finalize this bounded encoding checklist:

| Item | Proposed freeze rule | Remaining decision/work |
|---|---|---|
| Envelope and references | id, record_type, contract/version and explicit internal/external/unresolved reference forms | Publish exact required/conditional field tables and the ID lexical format |
| Payload variants | Explicit discriminator per family; raw native fields cannot overwrite envelope fields | Convert remaining descriptive specimen fields to schema-defined enums/typed records |
| Bytes and numbers | UTF-8 outer JSON; inline UTF-8/base64/external payload union; typed decimals/nonfinite/missing values as needed | Exact numeric/time/byte-span field shapes and range/encoding rules |
| Coverage and knowledge | Supported domain expressions, scoped index extent and reason codes | Final reason/predicate/domain-expression catalogs and unknown-extension behavior |
| Contracts and extensions | Separate versions; criticality scoped to affected operations/claims | Exact extension declaration and compatibility rules; no guessed automatic downgrade |
| Scope of a freeze | Freeze only defined shared shapes and selected subtype contracts | Detailed interaction/recovery extensions can be versioned independently; the base cannot promise their unchecked conformance |

Detailed interaction/recovery contracts and exact interfaces are next, as requested. They should confirm
that selected extension and reference slots suffice before public serialization is adopted. Legacy mapping
must also confirm that no shared meaning or historical consumer changes silently. There is no implementation
gate or requirement to design other subsystems before that review.

## 5. Mechanical inspection and its limits

Read-only inspection of the authored JSON and direct hashing of synthetic strings found:

- Nine cases, 147 defined records and 15 semantic check expectations.
- 613 internal references: zero unresolved targets and zero target-type mismatches after X01.
- 42 explicit domain-member references: zero unknown member keys; no duplicate domain keys or record IDs.
- Fourteen included snapshot strings: their computed byte digests match the recorded claims.
- All included complete native JSON strings parse; c8:prefix intentionally fails native JSON parsing.
- Zero implemented/executed semantic conformance checks and zero native executions.

Report: `../_w2_checks/2026-11-01_s1_design/composition-inspection.json`. The first inspection, including
the nine mismatches, is preserved as `composition-inspection-first.json` in the same external directory.
These are authoring checks, not the 55-test audit suite, certificate verification, proof of preservation
against actual systems, or scientific validation. No runtime baseline checks were rerun for this design step.

Only new owned design artifacts and current owned design-document indexes were written. No implementation,
test fixtures/library code, existing protocol, certificates, results, paper/tracker/site, B5 modules, shared
analysis/score/harness logic, port map or git state changed. No spend or native/replay runs occurred.

## Where we're going

Review the composition resolutions and finish the bounded serialization checklist. Then specify detailed
interaction/recovery contracts, exact adapter/core signatures and legacy compatibility mapping. Reconcile
the remaining subsystem-1 design gaps for final review, then plan implementation bundles with acceptance
criteria and validation gates. Implementation still requires an explicit go.

Update: these follow-on proposals are now written; use the final review packet above for current review
status. The older complete logical specimens and their mechanical evidence remain unchanged.
