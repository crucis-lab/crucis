# W2 system connections: Block 6, the output-object index (1 Nov 2026)

Tickets: DLV-08, DLV-09; neighbours DLV-10, ADV-01, DLV-06.
Status: design discussion only. No implementation, schema adoption or stored-result change is made.
Predecessor: `system-connections-outcome-observations-design-2026-11-01.md`; broader result organization:
`system-connections-result-record-design-2026-11-01.md` and the capability map of the same date.

## 1. Accepted direction and current boundary

Uzair accepted Block 5's boundary: sourced outcome observations, explicit knowledge gaps/diagnostics, and
versioned assessments retaining their evidence history. Exact field names and reconciliation rules remain
design details. The earlier qualified outcomes, Blocks 3/4 boundaries and checkpoint-restart identity rule
remain accepted directions. No implementation go was given.

This document proposes Block 6's object descriptors, relationships and examples. None of those exact schemas
or type families is adopted by appearing here. W2-5 through W2-9 remain pending. Shared protocol and paper
contract changes still go through W5. Later identity discussions distinguish historical imports from native
execution attempts; that distinction takes precedence over the early broad sketch's combined wording.

## 2. Purpose: identify meaning, not just files

The output-object index answers: what response objects are evidenced, what do they mean, what scope do they
cover, where did they come from, and how are they related? An object might be a graph, collection of samples,
set of local claims, uncertainty table, fitted parameters, encoder, checkpoint, diagnostic or action request.

Block 7 identifies storage/evidence artifacts and their availability/integrity. One artifact can contain
several objects; one object can require several artifacts. A filename or number of files does not determine
the number of scientific responses. Object payloads can remain external, with descriptors and precise locators.

A simple result needs only a small entry and relevant links. Do not require each graph edge, array cell or
sample to become a separate top-level record. A typed collection can identify members through stable member
keys or locators bound to an immutable source snapshot. Current list position is not a durable identity when
the list may be reordered.

## 3. Small common object descriptor

The names below are semantic requirements, not frozen JSON fields. Conditional details can be references.

| Part | What it establishes |
|---|---|
| Object identity | A stable handle for this response object/occurrence or produced view; owning request/attempt or unresolved source identity. |
| Type and semantic contract | Native declared type and known interpreted type/version; graph/claim/quantity/collection meaning and relevant assumptions. Unknown formats remain explicit. |
| Role and designation | Primary answer, intermediate stage, checkpoint, supporting quantity, diagnostic, action or other defined role; final/intermediate designation and its evidence. |
| Scope and coordinate domain | Task/query, variable schema, target/candidate coverage, group/time/lag/latent identities where relevant, and meanings of absent/unreported entries. |
| Producer and origin | Native system/component versus observer, adapter reconstruction, standardized interpretation or auditor transformation, with version/configuration references. |
| Evidence and payload locators | Artifact IDs and precise source selectors/keys/offsets where known, plus observation/evidence references supporting the claimed origin and role. |
| Relationships and provenance | Collection membership, parameter/uncertainty/schema associations, representation-of, derived-from, stage succession, or other defined relations with required parameters. |
| Interpretation/availability references | What can be accessed, parsed, mapped or validated, with gaps/diagnostics from Blocks 5/7 rather than a misleading global valid flag. |

The request contract identifies expected outputs, while the index describes evidenced outputs. A required but
missing graph is a gap, not an invented empty object. If the system only declares an output exists, an entry
may preserve that declaration and its native ID with reported/unretrieved availability; it must not claim
that bytes or interpreted semantics were captured. Native type/role claims and verified properties remain distinct.

An object descriptor does not have to repeat every earlier block. It references the subject, schema, evidence,
producer and request contract already identified. Optional type contracts define payload-specific detail.

## 4. Native objects, standardized interpretations and derived views

Three related roles must remain explicit:

1. **Native response object:** an object the system actually emitted or declared, associated with its source
   occurrence/evidence. Its native meaning may be well understood or still unknown.
2. **Standardized interpretation:** a versioned view translating native encoding/coordinates into a common
   semantic representation. It identifies the native object and its source, parser/mapping rules and evidence
   of preservation. Its presence alone does not certify that the translation was lossless.
3. **Derived view:** a new summary, projection, selection, reconstruction or decision produced from identified
   inputs. It records the producer, procedure/version, configuration, input views and relevant semantic loss.

All can use a common descriptor pattern, with explicit relationships. Their exact identity encoding is still
open. Recommended conceptual rule: preserve the native occurrence identity; give each persisted produced
interpretation/view its own identity/version and relationship to that source. Two encodings of one prediction
must not be counted as independent predictions. Consumers must not collapse different interpretations merely
because they share a source.

Examples of encoding/coordinate translation include parsing an endpoint matrix and applying its established
variable map. Examples of additional decisions include choosing one graph from a distribution, thresholding
weights, assigning definite directions to unresolved pairs, dropping marks for a particular metric, or aligning
learned factors to an evaluation reference. The boundary is semantic: preserve what changes and what does not.
If translation drops relevant information, identify that loss rather than calling it faithful by default.

Retaining raw evidence does not make an inadequate standardized view semantically complete. It does allow
later interpretation to recover information without fabricating a new native execution.

### Producer and derivation are separate questions

A native algorithm can itself produce a selected graph from its graph samples. Both outputs are native from
the auditor's perspective, and their internal derivation can be linked when evidenced. If the auditor selects
another graph later, that is auditor-produced, even if it happens to match the native graph exactly.
Do not infer a native procedure solely from equality of the outputs. Origin identifies who produced it;
derivation identifies the supported relationship/procedure; role identifies how it responds to the request.

## 5. Related objects and collection semantics

Typed relationships should identify their semantic endpoints rather than relying on equal array shapes,
filenames or nearest timestamps. Relevant examples:

- A graph references its variable schema and coordinate domain.
- A probability table attaches to specific propositions/claims with an explicit variable and conditioning map.
- A coefficient/parameter set attaches to a particular graph/model/sample and its units/conventions.
- A graph collection identifies members, multiplicity, member/collection roles, weights/probabilities if supplied,
  sampling basis and any graph/parameter pairing.
- An encoder/checkpoint and a learned graph share an identified learned-variable schema; evaluator alignment
  is a separate view linked to the original representation.
- Stage objects have ordered native event/component relationships. A derived change table links to both
  source stages and its inference rule; it is not itself a native stage declaration.

For posterior or bootstrap collections, repeated equal graphs can be distinct sample occurrences. Do not
deduplicate them into a set and destroy multiplicity. A compressed representation is acceptable only if the
type contract preserves the required counts/weights/member associations. Bootstrap frequency, posterior mass,
unnormalized weight and structural coefficient remain different quantities.

Averaging to edge marginals does not retain all joint graph structure. If a marginal table is derived, keep
the joint collection and transformation provenance when available. Unknown member associations must stay
unknown; array shape or incidental order cannot substitute for their documented mapping.

Scope also matters for negative claims. A local answer can be final and complete for its query without
asserting anything about other pairs. A full-graph, partial-graph, distribution and query-response contract
can assign different meanings to absent entries. The index must expose the relevant type and coverage;
it must not independently invent a universal absence-means-no-edge rule.

## 6. Choosing the answer for evaluation

There can be multiple required/co-primary outputs: for example a learned representation plus its graph.
A universal single primary_graph slot would be too narrow. A native final designation is a sourced statement,
not a selection policy for every later evaluation. An evaluator references the exact object/view it uses and
the request-compatible selection/projection procedure. Do not choose the newest file or best-scoring graph
silently. If several objects claim the same final role and evidence cannot resolve it, retain the ambiguity
in Block 5 rather than guessing.

Metrics/findings remain downstream. A scientific measurement derived by the auditor is not relabeled as a
native system output merely because a shared catalog can address it. A native system's own reported diagnostic
or score can be preserved as a native quantity claim; it does not become our independently certified metric.

Stage snapshots, sample members and several encodings are not additional independent runs. A knowledge-off
comparison rerun is a separate request/attempt, not an intermediate object created inside the original native
run. Related external-run objects can be linked for comparison, but their native ownership must stay distinct.

## 7. Concrete walkthroughs

These are hypothetical examples of the design, not new executions, derived measurements or stored findings.

### Example A: one graph, several representations

A system returns an endpoint matrix in shown-variable order. The native graph object points to its original
artifact/locator. A standardized graph view references that object, the endpoint-convention contract, parser
version and variable map. If an evaluation needs a projected view, its rule creates a separately identified
derived view. The native artifact is preserved throughout.

    Native graph object
      -> standardized graph interpretation (encoding/mapping provenance)
        -> evaluation-specific projected view (explicit procedure and any loss)

These are related objects/views, not separate causal-discovery attempts. If the matrix contains unsupported
marks or an unknown index convention, retain the native object and interpretation gap instead of guessing.

### Example B: graph collection and a selected graph

A native response includes graph samples paired with parameter samples. Index the collection with its member
associations. If the native system also returns its preferred graph, index that graph as a separate native
object with the evidenced role and selection relationship, where known.

An auditor-produced marginal table and an auditor-selected point graph get their own view identities and
procedures. Do not replace the native collection with either summary or infer their quantities are the same.
If some sample graphs repeat, preserve their multiplicity. If a procedure applies a DAG projection, record
it as a selection/transformation rather than implying every marginal threshold yields a valid DAG.

### Example C: graph and confidence in one file

One native artifact contains a graph payload and an uncertainty payload. These are separate semantic objects
or a typed bundle with addressable components; the exact packaging can remain flexible. Both reference the
same artifact using different locators and a shared variable/claim mapping. They are not separate attempts.

If graph interpretation succeeds while confidence interpretation fails, keep both entries/evidence and their
different interpretation assessments. If confidence was merely expected but no output is evidenced, record
the missing deliverable in Block 5 rather than inventing a confidence object filled with zeros.

The converse is also possible: one graph object can use a node-schema artifact, an edge artifact and a weight
artifact together. Artifact count is not object count.

### Example D: stages, variants and lineage

A native pipeline emits a data-stage graph and a final graph, possibly with the same edge contents. Each has
its native occurrence/stage identity and shared variable schema. Identical contents do not prove that the
two stage observations are one event. A derived stage-change table references both objects and its rule.
If stages are reconstructed from artifacts rather than directly emitted, their origin is reconstruction,
with source artifacts and reconstruction version attached.

A separately executed data-only baseline belongs to its own attempt even if its graph equals the native
data-stage graph. A relation can express their intended comparison; it cannot collapse their provenance.

### Example E: learned variables and multiple linked artifacts

A system returns an encoder checkpoint, a learned-variable schema and a graph over those variables. Index
their relationships so the graph's nodes are not misread as original input columns. A later evaluator aligns
those factors to reference variables under a declared policy, producing a derived alignment/view. Preserve
the original graph/schema and the fact that the alignment is evaluator-produced. It must not be passed back
as unrecorded system-facing knowledge or treated as native variable identification.

### Example F: local answer, active action or unknown format

A local answer identifies target/candidate scope and claim/abstention semantics. Unqueried pairs are not
filled in as negative predictions. An active step's requested experiment is an action-response object, linked
to its session; it is not the final discovered structure. A future unfamiliar artifact can be indexed through
its evidenced native declaration and artifact reference, while semantic interpretation remains unavailable.
The broader record preserves it without claiming that an arbitrary blob satisfies a graph or claim contract.

## 8. Interpretation updates, ownership and immutability

A new parser or corrected mapping produces a new interpretation/view and its diagnostic/provenance links.
The native object occurrence and original artifact evidence remain the same where established. Earlier
interpretations and evaluations remain addressable, with correction relationships through Block 5. Dependent
derived views must identify which interpretation they used; they do not silently move to a new parent.

An index snapshot can reference additions/updated assessments without overwriting the earlier snapshot.
Exact storage/append policies belong to later implementation design. Any current/default view pointer is
convenience metadata; publication/evaluation should reference a specific object/view and version.

Equal artifact bytes or equal graph values do not establish occurrence identity across attempts. A shared
artifact store may deduplicate bytes while preserving distinct object/attempt provenance. Conversely, a new
serialization of an existing logical output need not be represented as another independent prediction.
Relationships and supporting evidence must establish the distinction, not content hashes alone.

Derivation provenance should avoid circular dependencies between a view and its own inputs. This constraint
concerns evidence lineage, not the causal graph being represented: it does not impose acyclicity on every
native causal model.

## 9. Edge-case acceptance examples

| Case | Situation | Required distinction |
|---|---|---|
| X01 | Native graph parsed and remapped | Native object versus standardized representation, with preserved semantics and mapping evidence. |
| X02 | Auditor orients unresolved pairs | Derived decision view, not a new native assertion. |
| X03 | Native system returns samples and its chosen graph | Multiple native objects and evidenced native derivation; auditor selections remain separately produced. |
| X04 | Posterior contains repeated equal graphs | Member multiplicity and associations survive; not a deduplicated set of unique graphs. |
| X05 | Graph and uncertainty share one artifact | Distinct semantic components with precise locators and shared variable/claim mapping. |
| X06 | One graph is spread across node/edge/weight files | One semantic object can have multiple evidence dependencies. |
| X07 | Native stages return identical graph contents | Distinct stage occurrences, not automatically one output event or additional independent runs. |
| X08 | Intermediate stages are reconstructed later | Reconstruction provenance, not invented native stage emission. |
| X09 | Local answer leaves most pairs unqueried | Declared coverage/absence semantics, not a complete negative graph. |
| X10 | Learned graph and encoder are jointly returned | Shared learned-variable identity plus separate evaluator alignment. |
| X11 | Required artifact missing or merely reported | Expected deliverable/availability claim, not invented captured output. |
| X12 | One object's interpretation fails | Localize diagnostics while preserving interpretable sibling objects. |
| X13 | Parser upgrade changes standardized graph | New interpretation and correction lineage, unchanged native execution/evidence. |
| X14 | Two native attempts return equal bytes | Distinct native occurrences even if the bytes share storage. |
| X15 | Active step emits an experiment request | Action-response role with session scope, not final discovery graph. |
| X16 | Several candidates claim final status | Preserve role evidence/conflict; no silent latest/best selection. |
| X17 | Native probability/graph assertion is invalid | Preserve the value/claim and diagnostic; no clamping or graph repair. |
| X18 | Unknown native result type | Archive/index what is evidenced; no claim of semantic/evaluation support. |

The family-specific contracts will define exact graph endpoints, collection weights, claim coverage and
uncertainty meanings later. This common index establishes how those meanings, evidence and relationships
are addressed; it does not replace the semantic contracts with an unrestricted dictionary.

## 10. Current code, tradeoffs and next step

The current `RunRecord` has one graph and optional variants, confidence, sources, stages and files; the
graph implementation supplies current conversions/canonicalization. These are useful foundations, not a
complete generic object index. No field or converter was edited. Existing shared scoring/protocol rules,
historical results, certificates and paper pointers remain unchanged.

The recommendation costs more explicit references than a single graph slot. It permits reuse of a common
descriptor and relationship pattern across simple/rich systems, keeps artifacts external when large, and
avoids one mandatory top-level field per future algorithm. The strongest simpler alternative is a flat set
of graph/variants/confidence slots; it fits the current audits but leaves arbitrary result families, joint
associations and derived/native distinctions underspecified.

Adapters should supply native objects/locators and source conventions. Shared core mechanisms can manage
identities, relationship validation, mapping/interpretation provenance and type-aware consumption. No
system-specific parser is made generic by merely moving its special cases into an untyped shared field.

No tests or implementation were created or run. Only this new design record was written. The next discussion
can settle Block 6's distinction between native objects, standardized interpretations and derived views,
then proceed to Block 7's artifact/evidence availability and integrity representation.
