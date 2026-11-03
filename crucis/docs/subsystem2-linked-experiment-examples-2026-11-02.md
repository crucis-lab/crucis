# Subsystem 2: complete linked experiment definitions for review

Tickets: DLV-08, DLV-09; related DLV-10, DLV-06/07 and ADV-01.
Date: 2 Nov 2026, America/Los_Angeles.
Status: design composition exercise requested by Uzair. No S2 implementation,
production wire schema, preregistration, native/paid run or public adoption.

The [companion logical registry](subsystem2-linked-experiment-examples-2026-11-02.json)
provides explicitly named records and links for this review. Its readable aliases,
object shapes and hypothetical traces are review notation, not valid SC-1 records,
a proposed final S2 serializer, executable plans or conformance fixtures that have
passed runtime checks. All subjects, input slots, outputs, actors, events and
counts are fictional; no real artifact hashes, execution grants, timestamps,
native results or restricted data are invented.

Sources: [design rebase](subsystem2-design-rebase-2026-11-02.md) and its seven-area
source map. The [closure review](subsystem2-composition-closure-review-2026-11-02.md)
records proposed resolutions and remaining work. Source-level S1 handoff: existing
`audit/connections/schema.py`; no S1 schema/record is modified by these examples.

## 1. How to read the registry

Each named review record has a conceptual kind, phase, account and explicit role
links. Only the links array defines review references; native/source identifiers
inside an account are scoped labels. A link to an evidence-gap or restricted-source
descriptor resolves the local declaration, not the missing evidence itself.

The common policy records state reference/omission, hypothetical measurement,
population and execution boundaries. An obligation map connects all 92 numbered
responsibilities from the current design tables to named accounts. This checks
whether the questions have an owner or explicit gap. It is not proof that every
obligation is satisfied, every family is supported, or any native behavior is tested.

Definition roots and hypothetical trace roots are separate. Definition dependencies
must not reach trace-phase records. Future realizations/observations refer back to
their fixed requirements, and a new run/analysis binding records the selected
realization. No cited snapshot is edited to insert an outcome.

The registry separately marks `prior_evidence`: a historical reconstruction may
legitimately depend on recovered material that predates its current analysis.
That dependency is disclosed with its exposure/chronology limits and never
upgraded to prospective commitment. Trace phase means a later branch relative to
the example's fixed definition, not every artifact ever observed.

Three claim levels remain distinct: semantic completeness for this review,
readiness assuming the fictional branch's stated facts, and real operational
readiness. The last is unestablished for every example. No actual grant exists.

## 2. Example A: prospective static name comparison

### Defined question and source

`A.plan` defines an illustrative labels-only comparison for one source scenario,
one dataset realization, three name conditions and two native repetitions per
condition: six planned trials. This small example does not change the funding
matrix or real benchmark selection.

`A.source` specifies a hypothetical generating model with observed variables
A/B/C and direct edges A -> C <- B. `A.domain` fixes their source-scoped identities.
`A.selection` and `A.case_slot` bind the intended realization procedure and count;
they do not claim captured samples. A later hypothetical materialization links
that slot to `A.case`, `A.collection` and `A.membership` with exact evidence bindings
in the fictional branch. No actual file or digest is supplied.

`A.subject` describes a hypothetical native DAG-returning subject and the intended
configuration/state contract. It is not one of the real audited systems and carries
no claim of actual dependency, model or adapter readiness.

### Task, reference, conditions and transformation

`A.task_graph` requests a complete directed graph over the declared domain, or
an explicit whole-query abstention permitted by the task. Its omission rule makes
omitted covered adjacencies negative predictions only for the complete graph case.
Partial stage objects remain distinct from a final response.

`A.reference` declares the generating structure and its scope in this fictional
source, including absence of the A/B adjacency. Its prospective exact-reference
association depends on verifying the actual source/materialization; this review
does not emit a T1 scientific result.

`A.task_order` is a separate semantic check on the same case: any topological
sequence satisfying A-before-C and B-before-C is acceptable. Both A,B,C and B,A,C
are valid examples. They are not extra independent trial outcomes, and neither
asserts direct A/B causation. This optional check does not change the graph task.

`A.conditions` defines real, neutral and swapped label views. Numeric samples,
row/mask identities, context, native configuration and nuisance column order stay
fixed under the declared comparison. Context is explicitly retained, so no claim
of removing all domain knowledge is made. `A.transforms` fixes the shown variable
order [C,A,B], the label maps and the required coordinate/preservation checks.
Canonical/evaluator maps and the reference are not native payload fields.

### Comparison and populations

`A.comparison` defines case/dataset matching, independent requested native repeats
without claiming shared random streams, and separate study-coverage and conditional
output-quality questions. It uses `common.adjacency_measure` only as an exact
hypothetical measurement definition: the fraction of three unordered adjacencies
matching the complete reference. No new metric implementation or public protocol
metric is registered. A real S4 binding remains required.

An available-repeat comparison is explicitly conditional on actual conforming,
interpretable final graphs and applicable references. A planned two-repeat mean
must not be manufactured from fewer observations or silently replace this target.
One case supplies no source-population uncertainty/generalization claim.

### Adverse hypothetical trace

The registry contains six separate planned slot records and this illustrative
trace, with first-attempt behavior and no automatic scientific-repeat replacement:

| Slot | Hypothetical event | Required accounting |
|---|---|---|
| real-1 | Final graph A -> C <- B after conforming input | Potential conditional final-graph comparison, subject to actual evidence/readers |
| real-2 | Native failure with a surviving one-edge stage | Retain failure and stage; no invented final graph or final completion |
| neutral-1 | Explicit allowed whole-query abstention | Response-contract assessment and abstention; no assigned graph score |
| neutral-2 | Final complete graph containing only A -> C | Omitted B/C adjacency is a negative prediction; poor quality is not an eligibility exclusion |
| swapped-1 | Final graph but delivered values contradict the condition | Retain graph and actual input; exclude from the declared conforming contrast with a visible reason, without relabeling the arm |
| swapped-2 | Not started after resource availability changes | Retain intended slot, resource gap and no native start; not a native failure |

In the hypothetical trace there are six intended slots and five native starts.
The valid-final-graph conforming comparison has one real and one neutral output;
no swapped output qualifies. This is conditional coverage, not six independently
scored cases. Response-shape completion, scientific condition conformance and
native normal completion retain their individual scopes. No scalar aggregates
the failure/abstention/resource outcomes as invented graph quality.

`A.trace`, materialization and run-binding records link to the fixed plan, realized
case and slots. The fixed `A.plan` never links to those future trace records.
Fictional authority/timing descriptors illustrate what would need evidence; they
cannot authorize or prove a real run.

## 3. Example B: historical reconstruction with conflicting references

`B.plan` defines a new retrospective evaluation of a recovered CSV and graph.
`B.case`, `B.collection` and `B.membership` identify the currently reconstructed
set, complete only for the bounded recovered material. Its original study population,
selection rule, source case/request identity, producer configuration and event
time remain explicit gaps. No original native request, attempt or scientific
repeat slot is fabricated.

`B.task` asks what supported agreement statements can be made about that surviving
graph. It does not ask whether the original request was fulfilled. `B.subject`
preserves unknown original identity and the known current reconstruction role.

Two reference definitions, `B.ref_left` and `B.ref_right`, represent documented
candidate relationships under a contested-reference interpretation. Their candidate
claims disagree; neither is silently selected as truth. They have limited annotation
coverage, not a complete negative set. `B.references` requires separately labeled
reporting if applicable, with no best-reference selection or pooled exact accuracy.

`B.conditions` and `B.transforms` preserve unresolved original inputs, information
policy, mapping and recipe. Current identity conversion is not evidence that a
past transformation never happened. `B.mapping_gap` states that array shape and
similar labels do not establish a graph-to-variable mapping or omission semantics.

`B.comparison` cannot currently emit aligned graph agreement. A later evidenced
mapping/decoder would be a new interpretation/evaluation binding with its real
creation time. It can leave original fulfillment and selection unresolved. A
reference amendment preserves each earlier evaluation version and source.

This example closes its local links by referencing explicit gaps. It does not
"close" the scientific gaps. Preservation and current reconstruction are the
supported conceptual uses; random sampling, complete original coverage, paired
cross-system analysis and preregistration remain unestablished.

## 4. Example C: adaptive interaction and controlled exposure

`C.plan` binds a hypothetical local parent-query task for Z within candidate domain
{X,Y}, a source/episode-selection policy and at most two action rounds. Its primary
observable question is operation/response coverage under that policy. A secondary
parent-reference comparison requires episode/reference alignment and supported
semantics; it cannot be assumed ready from the primary question.

`C.case_slot`, `C.selection` and `C.source` describe bounded source access and an
episode to be resolved later. A hypothetical materialization records `C.case` and
its collection membership, preserving unknown restoration/state limitations.
No fixed pre-existing matrix or independent episode is invented.

`C.task` permits scoped parent decisions, including abstention, under explicit
local coverage. `C.reference` is a symbolic restricted descriptor: an authorized
evaluator would need to resolve the episode-matching reference. It contains no
real location, graph, seed, digest or read ledger. Resolving that descriptor is
not accomplished by this document or its local link checker.

`C.conditions` identifies permitted simulator action/response channels and excludes
the evaluator reference/metric feedback from native delivery. `C.transforms` has
no numerical batch alteration; it specifies the bounded source/presentation mapping
and honest non-applicability of unrelated iid-row/label controls.

`C.adaptive_rule` makes the branch explicit: first request X=0; if the permitted
first response's declared mean-Z summary is nonnegative, choose Y=1 next; otherwise
choose Y=-1. No evaluation score participates. This policy is illustrative, not
an asserted efficient causal experiment or a newly chosen scientific method.

In `C.trace`, a fictional first response has summary +0.25, so the recorded policy
decision selects Y=1. A crash after first-response delivery prevents the second
round and final parent answer. The event remains exposure even though no final
accuracy is available. Its read-consumption consequence depends on an adopted
owner rule; the registry records that unresolved policy instead of granting a
fresh read. Replay is not a new episode or fresh confirmation.

The authority/read descriptors preserve the distinction between a required grant,
a hypothetical scenario assertion and real admission evidence. Actual authority,
capacity and isolation are not established. No real helper or read ledger is
queried. The existing one-version/five-total helper constraints remain unchanged.
An eight-system panel receives no extra allowance from this example.

## 5. Cross-example invariants

- All local role links resolve to named records, including typed gaps/requirements.
  That establishes review reference closure only.
- Frozen definition dependencies do not point into hypothetical trace records.
  A later resolution, observation or assessment links back to its requirement.
- Planned source slots, realized cases and observed analysis sets are separate.
  No slot or bootstrap/retry/candidate member creates an independent dataset.
- A valid parsed record does not automatically establish interpretation, scientific
  readiness, authority, delivery, reference applicability or correct inference.
- Native inputs use a permitted projection; the whole evaluator plan is not a
  native payload. Restricted reference descriptors remain unresolved at this scope.
- Sources, bindings, native output semantics and missingness reasons determine
  comparisons; no latest/best/available match is substituted silently.

## 6. Coverage and limits

These three experiments exercise the seven responsibilities jointly, including
global/local/order meanings, late binding, adverse outcomes, uncertain history and
adaptive exposure. The 92-obligation map is an ownership/traceability inventory,
not 92 passing tests, three measured studies or proof of all combinations.

Temporal, relational, distributed, learned-variable and posterior-collection
extensions still require their exact semantic/lifecycle closure. The companion
review identifies those variants for the next pass. The existing 28-example map
is a reference scope, not a universal finite denominator of possible systems.

## Where we're going

Review the complete definitions and explicit gaps using the closure decisions.
Settle required semantic families/profiles and late-binding/assessment rules,
then perform the bounded serialization, exact interface and legacy mapping pass.
No implementation or public adoption begins until its own approved scope and go.
