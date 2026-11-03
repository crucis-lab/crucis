# Subsystem 2: task definitions and reference bindings

Tickets: DLV-08, DLV-09; related DLV-10, DLV-06/07 and ADV-01.
Date: 2 Nov 2026, America/Los_Angeles.
Status: proposed design, not approved serialization, implementation, measurement
changes or public protocol adoption. Uzair approved continuing the design from the
minimum case/membership obligations. Specific contracts below remain for review.

Sources: [case walkthroughs](subsystem2-case-worked-examples-2026-11-02.md),
[minimum records](subsystem2-case-membership-minimum-2026-11-02.md),
[S2 structure](subsystem2-structure-design-2026-11-01.md),
[S1 request/outcome contract](system-connections-contract-outline-2026-11-01.md),
`audit/connections/schema.py`, `audit/protocol/tiers.py`, and `audit/PROTOCOL.md`
sections 1 and 3. No shared code, tier definition, finding rule or stored number
is changed here.

## 1. Four meanings to keep separate

1. Case: the evidence situation, including known source/realization boundaries.
2. Task: the scientific question and requested response under declared information.
3. Reference: a sourced assertion, structure, quantity or other evidence that may
   help evaluate some aspect of a response.
4. Evaluation binding: which output/reference scopes are compared, under which
   alignment, applicability and measurement rules, and with which claim limits.

The same case may support several tasks. The same reference may support several
limited comparisons. A reference is not automatically a complete answer key, a
permitted system input or a proof of identifiability. A task can be meaningful
without an accuracy reference; an eligible comparison may use a declared control
or provenance evidence instead, without inventing causal truth.

Task fulfillment, output capture, semantic interpretation and scientific quality
remain separate as established in S1. A wrong answer may satisfy the response
contract. A recovered partial output may be scientifically useful even when the
original request or completion is unknown.

## 2. Task template and concrete binding

A reusable task template states operation/response meaning. A concrete binding
identifies the case revision, target/domain, condition/information policy and
applicable parameter/configuration values. These are logical roles, not a demand
for two files or duplicate request records. New S1 request occurrences bind this
intent through supported contract references; S2 does not introduce a second
competing execution/request truth source or silently extend the closed SC-1 schema.

| ID | Task obligation | Examples and prevented ambiguity |
|---|---|---|
| Q01 | Identity/version, authoring provenance and asserted/reconstructed timing | A new retrospective definition cannot pretend to be the original request |
| Q02 | Scientific operation/question and proposition meaning | Direct parent, ancestor, adjacency, CI statement, order constraint and effect estimate are different targets |
| Q03 | Exact case/source revision, variable/domain/target scope and relevant time/environment context | A local question does not request a global graph; a time window or intervention context cannot be inferred from a label |
| Q04 | Required/optional native response families, object roles, cardinality, units and coverage semantics | Graph, partial order, pairwise claim, distribution/model reference or multiple related outputs keep their native meaning |
| Q05 | Referenced allowed information, actions/state and scientific resource constraints | Numeric data, names, knowledge, interventions and evaluator references must be accounted for explicitly |
| Q06 | Completion, partial-output, abstention and missing-deliverable rules | Allowed abstention differs from an empty graph, a timeout or no returned output |
| Q07 | Applicability prerequisites and scoped scientific assumptions, including requested identifiability target | Ground-truth orientation may exist without being identifiable from the allowed observations |
| Q08 | Evaluation intents/rule references, amendment history and known gaps | Declare what can be judged without choosing a flattering output/reference after seeing it |

These obligations use the same author/source/gap distinctions as the case records.
An ordinary task need not carry unrelated optional families. Applicable requirements
are established by the selected contracts, not inferred from a system name.

An S2 definition specifies a scientific response target; it cannot claim native
support for that target. If a system supplies an order and the comparison requires
a graph, either choose an appropriate ordering question or declare an evidenced
derived procedure as a separate evaluated object/mode. Do not fabricate native
graph support or change the algorithm inside an adapter.

## 3. Response meaning and generic semantic families

| Requested family | Required distinctions before evaluation |
|---|---|
| Structural discovery | Domain, graph family, edge/endpoint semantics, absent-versus-unreported coverage and applicable equivalence/identifiability target |
| Local/pairwise claims | Target/proposition universe, conditioning/environment scope, direct versus ancestral meaning, positive/negative/unknown/abstained responses |
| Orders/constraints | Partial versus total order, permitted ties/incomparability, ancestry versus direct adjacency, valid alternative orders |
| Temporal/relational structure | Time-lag/instantaneous meaning, units/window and relational perspective/entity/schema identity |
| Quantities/distributions | Estimand/event, units/support, conditioning/intervention context and uncertainty meaning; coefficient, p-value and probability remain distinct |
| Graph/model collections | Member identity, weights/counts and native ensemble/posterior meaning; no inference of independent draws from list length |
| Learned representations/models | Native model/latent domain, observable mappings and separately justified evaluator alignment; no invented unique latent labels |
| Interactive/adaptive work | Eligible actions/questions, target episode/state, resource/stopping rules, response evidence and policy-level comparison question |

Conditional families reuse S1's semantic contracts and evidence mechanisms where
implemented. Defining a task for a broader family does not implement its converter,
alignment or evaluator. Ancillary prediction/effect tasks must be labeled for their
actual question; answering one does not establish graph-discovery performance.

## 4. Reference definition

| ID | Reference obligation | Failure prevented |
|---|---|---|
| F01 | Stable identity/exact revision, author/source provenance, creation and source-event timing as known | Replacing an answer key without preserving the evaluated version |
| F02 | Assertion/quantity/structure type and exact scientific meaning | Calling an ancestry constraint a direct edge or a label-implied graph data truth |
| F03 | Applicable case/source revision, domain, population, environment, time/state and conditions | Scoring transformed or changing-source evidence against an inapplicable reference |
| F04 | Basis and derivation procedure/inputs, assumptions and existing truth-tier association where applicable | Treating a documentation link or source declaration as independently verified exact truth |
| F05 | Coverage and completeness, positive/negative support, uncertainty, conflicts and known gaps | Treating unannotated pairs as absent edges or incomplete consensus as a complete graph |
| F06 | Payload/evidence bindings, availability/integrity scope and domain/alignment references | Comparing same-shaped but misaligned structures or citing bytes never captured |
| F07 | Disclosure/access policy and relevant exposure/independence evidence | Delivering evaluator answers to the system or assuming the reference is independent of evaluated outputs |
| F08 | Revision/conflict history, correction rationale and resulting claim limitations | Retrospective cherry-picking or silent changes to historical results |

A reference may be exact within a limited scope. For example, known direct parents
of Z do not establish a complete graph over all variables. Unknown reference values
remain unknown even if the evaluated system gives a definite answer. A supplied
reference's apparent completeness needs an explicit scope/basis, not a filename.

References can share a source with the evaluated system or be constructed using
its outputs. Preserve that dependence. Agreement in such a comparison is not
independent confirmation; the applicable study question and limits must say so.

## 5. Evaluation binding and permitted conclusions

The binding identifies the exact task/case/reference revisions, selected output
roles/stages, eligible proposition domain, condition/trial scope, mapping/derivation
procedures, requested metric contracts and planned analysis populations. It also
states evidence/readiness requirements, missing/abstained-output treatment and
the permitted scientific label. S4 computes measurements; S5 applies finding rules;
S2 binds the intended question rather than copying their logic.

Alignment is an evidenced, versioned operation. Renaming permutations can preserve
variable identity; projection, thresholding, graph completion and learned-factor
matching can change the evaluated object or meaning. Declare their losses and
assumptions, whether they were selected before outcomes, and whether they produce
native or derived views. Do not pick the best stage/reference/alignment separately
for each output unless that selection is the expressly declared analysis.

Reference readiness is metric-specific. A partial annotation may support a scoped
comparison on labeled propositions but not an all-pairs false-positive rate. That
restricted comparison must expose its coverage and selection limits; it cannot
be generalized automatically to all propositions or missing cases.

An exact source DAG and an observational equivalence-class response require a
declared compatible target/procedure; arbitrary orientation repair is not allowed.
An exact generating reference can support structural recovery evaluation while
requested orientation identifiability and information-regime limits remain visible.
Source assumptions, source-reference correctness, domain alignment and statistical
identifiability are distinct claims with their own evidence/limits.

For confidence evaluation, bind the reported quantity to a particular event and
applicable outcome reference. Native confidence, p-value, heuristic score and
probability cannot be silently interchanged. Calibration populations, dependence,
binning/estimation and intervals belong to their declared later measurement rules.

## 6. Existing tiers and historical compatibility

The current protocol and `audit/protocol/tiers.py` establish:

- T1: exact simulated reference, labeled accuracy.
- T2: contested reference, labeled agreement.
- T3: provenance-only reference, labeled agreement.
- T4: known mismatched reference, diagnostic inside a control; never scored alone.
- Different tiers are not pooled under the existing rule.

Keep those meanings and existing results unchanged. Richer assertion/coverage/
applicability metadata is a proposal alongside that legacy mapping, not a silent
replacement tier taxonomy. A T1 label alone does not prove correct materialization,
alignment, native delivery, identifiability or complete evaluation coverage.

Reference-free controls may assess declared invariants or observed changes. They
do not invent a truth tier or automatically establish a cause of the change.
No reference-supported correctness measure is emitted merely because a graph exists.

## 7. Concrete examples and edge cases

1. Synthetic chain: source graph A -> B -> C is exact under its specification.
   Bind realized evidence and domains before recovery scoring. For observational
   outputs, retain the declared equivalence/orientation target and information
   regime. A successful graph response can still be wrong against that target.
2. Partial real-world annotation: two documented parent relationships with no
   full negative set can support the declared comparison on those relationships.
   Unannotated edges remain unjudged; do not report full-graph specificity.
3. Valid alternative orders: a reference partial order need not select one unique
   total order. Compare the declared constraints rather than penalizing every
   alternative linear arrangement. Direct-edge scoring is a different question.
4. Historical surviving graph: established mapping/reference can enable a new
   retrospective output comparison while original request/fulfillment remains
   unknown. New authoring time does not supply original preregistration.
5. Conflicting references: preserve both and predeclare a justified selection,
   stratified reporting or explicit sensitivity comparison. Do not average graph
   truth claims into probabilities without a defined justified model/procedure.
6. Corrected reference: retain the original evaluation's exact reference version.
   New evaluation/amendment identifies the correction and affected outputs/
   populations. A reference-only correction need not change case evidence identity.
7. Oracle delivery: evaluator-only reference becomes system input only through an
   explicitly allowed oracle condition with actual delivery evidence. That changes
   the information regime/question; it cannot remain a hidden baseline advantage.
8. Interactive changing source: reference applicability must match episode/state.
   A missing stable causal reference can block parent-accuracy scoring while
   leaving separately evidenced action-policy/completion measurements meaningful.
9. Abstention: a permitted scoped abstention can fulfill the response rule and
   still reduce answer coverage. Missing output or a fabricated empty graph is
   not an equivalent response. Quality/coverage analysis follows declared rules.

## 8. Alternatives, costs and open details

| Proposed direction | Strong alternative | Cost and prevented failure |
|---|---|---|
| Separate case, task, reference and evaluation meanings | One self-contained dataset/answer record per experiment | More explicit references; prevents duplicated cases and silent coupling of truth, system inputs and scientific question |
| Semantic family contracts plus scoped extensions | Force every result to a DAG | More family-specific checks/evaluators; prevents losing partial, local, temporal, learned and interactive meaning |
| Explicit reference coverage and applicability | Trust one answer file and its tier tag | More source/alignment metadata; prevents unsupported negatives and mismatched truth claims |
| Bind selected native/derived output roles and measurement procedures | Score whichever available object looks most useful | More up-front design and amendment history; prevents best-stage/reference/projection selection hidden in reporting |
| Preserve missing/conflicting history with scoped readiness | Reject old data or fill missing facts from current defaults | More visible limits; retains evidence without manufacturing intent or certainty |

Still open: exact contracts for each requested response subtype, case/materialization
lifecycle, reference index/closed-world rules, alignment readiness and extension
validation, historical compatibility mapping, and exact serialization/API bindings.
Conditions/information, transformations, comparisons/repeats, missingness and plan
commitment need their own deep dives before a joint completeness review. This is
not a final subsystem-2 contract or an implementation bundle plan.

## Where we're going

Review these task/reference boundaries against the three complete case walkthroughs.
Next resolve reference coverage and requested-response semantics in concrete global,
local/order and interactive examples, then proceed to conditions and information
policy. Keep all future profile claims conditional on implemented and scientifically
validated support. No S1 runtime, stored certificates, shared analysis logic, W1/W5
files or sealed material is changed by this discussion.
