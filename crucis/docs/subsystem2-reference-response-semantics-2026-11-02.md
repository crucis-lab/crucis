# Subsystem 2: reference coverage and response semantics

Tickets: DLV-08, DLV-09; related DLV-10, DLV-06/07 and ADV-01.
Date: 2 Nov 2026, America/Los_Angeles.
Status: focused design proposal. Uzair accepted continuing from the task/reference
outline and requested global-graph, local-answer and ordering examples, especially
omission, abstention and valid alternatives. Specific rules below remain proposals;
no implementation, schema freeze or public protocol/measurement change is adopted.

Sources: [task/reference proposal](subsystem2-task-reference-design-2026-11-02.md),
[case walkthroughs](subsystem2-case-worked-examples-2026-11-02.md),
[S1 domain/output design](system-connections-domains-mappings-2026-11-01.md),
`audit/connections/{schema,semantics,families}.py`, `audit/protocol/tiers.py`
and `audit/PROTOCOL.md`. All situations below are illustrative design examples.
They are not native executions, measured outcomes, executed tests or new findings.

## 1. Proposition scope comes first

Before interpreting an omission, bind the exact proposition universe: variables,
relationship meaning, direction/endpoint roles, time/environment, conditioning and
applicable selectors. Adjacency between A/B, direct A -> B, ancestry A => B and
whether A precedes B in a displayed sequence are different propositions.

An unordered three-variable adjacency domain contains three distinct non-self
pairs; its ordered direct-edge domain contains six. Do not combine their counts.
Self-relations, lagged self-effects or other special cases follow the selected
semantic contract, not a universal diagonal rule. Out-of-scope is not false.

Maintain separate views of the task-requested scope, native response scope,
captured/interpretably available scope and reference coverage. A global request
does not prove a globally complete answer, and a source completeness declaration
does not prove complete capture. Missing bytes or unsupported decoding remain
evidence/interpretation gaps rather than native abstentions or negative answers.

## 2. Reference and response accounts are distinct

| Reference account for a proposition | Meaning |
|---|---|
| Supported true | Identified reference evidence supports the proposition at its stated tier/scope |
| Supported false | Identified reference evidence or a justified closed-scope rule supports its negation |
| Undetermined | The reference does not establish either outcome for this use; absence of annotation is not a negative label |
| Conflict | Applicable sources/constraints disagree or cannot jointly hold; retain both and a scoped conflict |
| Outside applicability | The question/domain/condition does not belong to this reference's declared use |

| Response account | Meaning |
|---|---|
| Assert | Native response commits to the proposition under its declared meaning |
| Deny | Native response commits to its negation, explicitly or through a justified closed-scope omission rule |
| Abstain | An explicit scoped decision to withhold the relevant commitment |
| Native unresolved/ambiguous | A native uncertainty state whose precise abstention/decision meaning is not established |
| Unreported | No answer is supplied for this proposition in the established response scope |

These are conceptual accounts, not a new serialized flat enum. Conflicting native
decisions, probabilistic claims, partial endpoint knowledge, task completion and
capture failures retain their own structures. An answer can establish adjacency
while leaving orientation undecided. A native "unknown" is mapped to abstention
only when its declared meaning supports that interpretation.

For applicable determinate reference propositions, evaluate asserted/denied
responses as supported or contradicted under the selected measurement contract.
For an undetermined reference, a definite response remains unjudged at that scope.
Abstained/unreported responses do not become correct negatives. Conflicts are not
resolved by averaging truth labels, picking the best score or silently preferring
the latest file. Reference constraints may support declared logical consequences,
but those derivations need their own procedure, assumptions and provenance.

## 3. Omission needs an explicit contract

Two response/reference contracts are both useful:

- Closed for a declared scope: all applicable relationships in that scope are
  represented; a specified omitted relationship means an asserted negative there.
- Open/explicit-only: listed decisions/relationships carry the stated meaning;
  unlisted propositions remain unreported or reference-undetermined.

Either may coexist with explicitly unknown/abstained regions. An omission default
cannot overwrite an explicit local exception. The representation must establish
how those regions are distinguished; otherwise withhold the affected interpretation
and retain the ambiguity. Outside declared coverage, no assertion is inferred.

A file named "final_graph", a square array, an empty list or a graph image does
not establish a closed contract. If the native format has established closed
semantics, retain them, including when its negative predictions are wrong. Do not
relabel a sparse closed graph as selective reporting to improve its score.

Closed reference coverage additionally needs a source/basis. Complete enumeration
of all positive annotations in a document does not establish a complete truth graph.
A partially annotated reference may support consequences under an expressly bound
logical model, but annotation omissions alone cannot supply them.

## 4. Global graph examples

Use an illustrative complete generating DAG A -> B -> C with no direct A/C edge.
Its adjacency reference supports AB and BC and denies AC. It also supports A as
an ancestor of C. The latter is not a direct-edge or adjacency claim.

| Response or reference situation | Faithful meaning and permitted comparison |
|---|---|
| Closed full-domain graph containing only A -> B | AB is present; BC and AC are predicted absent. The BC prediction contradicts this reference. Orientation is evaluated separately at the declared target. |
| Open reported-edge list containing only A -> B | AB is asserted; BC and AC are unreported. Do not infer native denials. A global-request coverage gap remains visible; any penalty for an unanswered required relationship follows the declared evaluation rule. |
| Explicit empty graph with closed full-domain semantics | All covered adjacencies are denied. It is an actual substantive prediction, not abstention. |
| Empty open report with no explicit decisions | No relationship is answered; it is not an empty-graph prediction. |
| Partly oriented A -- B under an established partial-graph contract | Positive adjacency may be known while direction remains unresolved according to that family. Do not convert to two directed edges or two negative orientation decisions. |
| Partial reference documents A -> B and B -> C but does not claim complete direct-edge coverage | Direct A -> C remains undetermined on those annotations alone. Do not score that direct edge as absent merely because it is unlisted. |
| Returned edge under an unknown variable mapping or incomplete capture | Preserve the output evidence; withhold the affected aligned comparison rather than interpreting missing/ambiguous content as no edge. |

Graph family remains part of the semantics. Endpoint marks in latent-variable or
temporal graph families cannot be interpreted by an ordinary directed-graph rule.
An undirected or uncertain endpoint does not have one universal abstention meaning.
Declared graph-family validation and a supported interpretation are prerequisites.

The reference's exact generating DAG and an output representing an observational
equivalence class require compatible evaluation targets and supported derived
reference views. Do not orient uncertain edges arbitrarily or select one convenient
representative and call that the native answer. Returning an entire class and
returning one member are different commitments even if both contain a compatible
possibility.

## 5. Local answer examples

Task: identify direct parents of Z within candidate set {A, B, C}. For this
illustration the complete local reference supports A and denies B/C as parents.
It establishes nothing about relationships elsewhere in the global domain.

| Native local response | Meaning |
|---|---|
| Complete parent set {A} within the declared candidate scope | Assert A; deny B and C. No global negatives follow. |
| Reported parents {A}, explicitly non-exhaustive | Assert A; B/C are unreported. |
| A yes, B no, C abstain | Three distinct decisions. A/B can be compared to the reference; C has abstention and contributes to answer-coverage accounting. |
| No parents, explicitly exhaustive over {A, B, C} | Deny all three; this contradicts the reference on A. |
| Whole-query abstention | No parent-membership commitment for this query, with explicit scope. |
| No returned local object after failure or capture loss | Missing output/evidence, not a native decision to abstain. |

If the reference only establishes A as a parent, predictions about B/C remain
unjudged unless another applicable basis supplies their labels. Report which
requested propositions are reference-covered and which are answered; neither set
is inferred from the other. The designated parent-candidate scope may itself be
incomplete for the wider world; a claim of all parents needs its own coverage basis.

Parenthood, ancestry, association and Markov-blanket membership must use different
predicates. In A -> B -> Z, A is an ancestor of Z but is not thereby a direct parent.
A local method's returned set is evaluated at its actual predicate and scope.

## 6. Ordering examples and valid alternatives

Use a reference task asking for any topological sequence compatible with a complete
illustrative graph A -> C <- B. The constraints require A and B before C, without
requiring a relative placement of A and B in that sequence.

| Response | Meaning under this task |
|---|---|
| A, B, C | A valid complete sequence. A before B here does not assert A causes B. |
| B, A, C | Another valid complete sequence; it must not be penalized for differing from one stored example sequence. |
| A, C, B | Violates the required B-before-C constraint. |
| Only the constraint A before C | A partial constraint answer. It can be compatible with the reference while not fulfilling a required complete-sequence deliverable. |
| {A, B} in one tier, then C | Requires an explicit tier meaning. If it leaves within-tier placement unspecified and the task permits a partial-tier response, preserve that meaning; do not invent equal causal status or a unique sequence. |

A sequence chooses one arrangement. A partial order can assert required precedence
constraints. A ranking tie can assert equality in a ranking quantity. Incomparability
in a declared order, unknown precedence, unreported pairs and membership in the
same display tier are not interchangeable. The task must identify which is requested.

Representation matters. Cover pairs A < B and B < C can entail A < C under a
declared strict-order transitive-closure contract. Its omission is not unreported
or an asserted negative there. An arbitrary partial relation list does not claim
that all other pairs are incomparable. Any closure is an explicitly versioned
derived view; it is not a claim that the native file enumerated every entailed pair.

For a task requesting a complete partial-order relation, stronger extra precedence
claims may be erroneous. The same sequence can be acceptable as one linearization
and inappropriate if interpreted as a claim that every earlier node is an ancestor
of every later node. Evaluation binds the actual predicate and answer family.

Valid alternatives have to be established at the requested target. A complete
admissibility contract may define all acceptable sequences, an equivalence class
or several solutions. Merely satisfying a few necessary constraints in an incomplete
reference establishes compatibility, not complete correctness. Distinguish this
from observational identifiability and from tolerance to numerical error.

Check joint consistency as well as individual claims: self-precedence, cycles,
duplicate members in a required permutation, and mutually inconsistent endpoint
claims cannot be repaired by selecting favorable entries. Preserve the native
output and record the scoped failure/gap; any repaired object is separately derived.
Conflicting alternative members of a declared hypothesis collection are not the
same as contradictory claims inside one purported single solution.

## 7. Abstention, coverage and finite denominators

Abstention identifies subject/proposition scope, source/native meaning and any
reported reason or quantity. It can apply to an orientation while retaining a
positive adjacency, to one candidate, to a whole query or to an entire deliverable.
An arbitrary omission or uncertain output value is not converted into abstention.

The response contract decides whether that abstention fulfills the request. The
scientific analysis separately accounts for answer coverage and quality. Allowing
abstention does not excuse hiding its extent, and forbidding it does not justify
discarding the resulting native evidence.

Retrieval recall, required-answer coverage or a declared task loss may count an
unreturned required positive as a miss without pretending the system asserted its
negation. Preserve the native decision semantics and label the derived metric's
treatment separately. Unfulfilled or unavailable responses remain in the intended
population accounting; a selective answered-only score cannot silently replace it.

For each relevant analysis scope, retain the requested propositions, native output
coverage, interpretable/captured scope, determinate reference support, definite
answers, explicit abstentions, unreported decisions and other unavailable/ambiguous
regions. These are related sets and dimensions, not automatically mutually exclusive
categories that can be added. Name the denominator for each reported rate and
retain the case/trial/grouping units for later inference.

Illustrative adjacency example: three reference-covered pairs, but an open report
answers only AB correctly. It has one correct definite answer and answers one of
three pairs; it has not established perfect full-graph recovery. A closed graph
containing only AB answers all three and misclassifies BC. An all-abstaining response
has no definite-answer correctness denominator; do not silently report 100% or 0%
as an observed conditional accuracy. The requested-task coverage may still be
measurable under its declared policy. Exact formulas and uncertainty are S4 design.

If scoring incorporates a utility/loss for abstention, missingness or answer sets,
that rule must be explicit and committed at the appropriate time. A retrospective
analysis may be useful with its honest label; it cannot acquire preregistration
by being written later. Do not optimize thresholds or selection rules against the
same outcomes and present them as untouched confirmation.

## 8. Alternative answers, sets and probabilities

A response containing several candidates must say whether they are alternatives,
samples, weighted posterior members or a joint set of assertions. A reported
probability is a claim about a specified event/distribution, not a hard positive
or negative until an explicitly declared decision rule produces a derived decision.
Nonsignificance, a small coefficient or missing confidence does not independently
establish absence of a causal relationship.

Do not award full single-answer correctness merely because one member of a large
candidate set matches. A set-valued target can use declared coverage, specificity,
size or distributional rules, but those are separate measurement contracts with
their own assumptions. Returning every possible graph must not silently become
perfect graph recovery. Valid alternative reference answers likewise need an
evidenced admissibility definition; no arbitrary maximum-score matching by default.

## 9. Proposed semantic requirements and future acceptance examples

| ID | Requirement | Design example to carry into later validation |
|---|---|---|
| S01 | Bind proposition meaning and scope before comparing | A-C direct absence coexists with A as an ancestor of C |
| S02 | Keep reference support independent of response commitment | A prediction on an unannotated pair remains unjudged |
| S03 | Omission defaults require scoped native/reference contracts | Identical one-edge lists have different meanings under closed and open semantics |
| S04 | Explicit exceptions and outside-scope regions stay visible | Local orientation abstention cannot be overwritten by a broad no-edge default |
| S05 | Capture/interpretation gaps do not fabricate decisions | Truncated graph bytes do not establish absent edges |
| S06 | Partial structure preserves each established component | Known adjacency survives unresolved orientation |
| S07 | Local answers imply no global completion | A parent set supplies no negatives for unrelated variable pairs |
| S08 | Orders retain predicate, representation and closure meaning | Both permitted topological sequences are valid; cover-pair closure is a derived view |
| S09 | Compatibility, complete correctness and fulfillment are separate | A partial constraint answer may be compatible but incomplete |
| S10 | Preserve inconsistency and distinguish alternative hypotheses | Cycles are reported without repair; alternative collection members retain their roles |
| S11 | Abstention and answer/reference coverage have explicit units and denominators | One correct answer of three requested pairs is not perfect full recovery |
| S12 | Sets/probabilities/decision rules keep their native meaning and selection basis | One matching candidate does not turn an unbounded answer set into a correct single answer |

These are design acceptance obligations, not tests that have passed. Native adapter,
semantic-contract, evaluator and statistical support each require their own evidence.

## 10. Existing footing, alternatives and boundaries

S1 already represents graph pair coverage and omission policies; claims/sets have
scoped decisions including assert/deny/abstain/native-unresolved. Orders distinguish
sequence, relation pairs and cover pairs; family checks detect selected structural
problems and deliberately withhold a completeness claim for partial relation lists.
This inspected behavior is not a complete S2 evaluation/coverage implementation.
No runtime or existing metrics are changed here.

The strongest simple alternative is to evaluate complete graphs/sets against one
complete reference and reject everything else from that analysis. That can be
faithful for an expressly narrow study, but cannot silently define support for
the broader native families. The proposed conditional semantic contracts cost
additional checks, scoped populations and measurement procedures. They prevent
manufactured negatives, false completeness and invalid penalties for alternatives.

Exact truth still requires valid source/binding/assumptions; contested and
provenance-only references retain agreement labels; mismatched references remain
diagnostic-only under existing tiers. New reference views, procedures or protocol
changes remain proposals to W5. Stored numbers, finding kinds, paper pointers and
certificate formats are unchanged.

Open details include exact predicate/omission contracts and supported converters,
closure/admissibility algorithms, complete specimen encodings, compatible native
bindings, analysis formulas and joint readiness checks. The proposed semantics
must be reconciled with later conditions, transformations and missingness design
before serialization or implementation approval.

## Where we're going

Review these meanings against the global, local and ordering examples. Next develop
conditions and information policy: the exact channels each condition permits,
what must remain fixed, how evaluator references stay separate, and how intended
delivery differs from observed access/use. Continue to retain unresolved contract
and measurement details for the joint design review; no implementation begins here.
