# Subsystem 2: composition across temporal, distributed, learned and uncertain evidence

Tickets: DLV-08, DLV-09; related DLV-10, DLV-06/07 and ADV-01.
Date: 2 Nov 2026, America/Los_Angeles.
Status: design extension requested by Uzair. No implementation, wire freeze,
native/paid execution or public protocol adoption. Every source, identity,
observation, quantity and branch below is hypothetical; arithmetic checks are
design consistency checks, not empirical measurements or native validation.

Predecessors: [linked A/B/C examples](subsystem2-linked-experiment-examples-2026-11-02.md),
[closure review J01-J12 and X01-X05](subsystem2-composition-closure-review-2026-11-02.md).
Companions: [extension logical registry](subsystem2-extension-composition-2026-11-02.json),
[candidate family/profile/lifecycle contract](subsystem2-family-profile-lifecycle-contract-2026-11-02.md).
The registry is review notation, not SC-1, an S2 schema or executable job input.
It pins the actual parent review-document hash for local cross-registry references;
it supplies no real native data, protected material or execution authority.

## 1. X01 / D: time, groups, overlapping windows and lag boundaries

Source: one hypothetical participant trajectory, variables X/Y, sample indices
0 through 11 at one-second spacing. A declared source model has X_t = U_t and
Y_t = 0.7 X_(t-1) + V_t under its explicit stationary/innovation assumptions.
No trajectory is actually generated here.

Two case windows use half-open intervals [0,6) and [3,9). Each contains six time
points. Their source-index overlap is {3,4,5}; together they contain nine unique
time points, not twelve independent observations or two independent participants.
The target is lag-one direct structure, not an unqualified static edge X -> Y.

If the task requires both parent and child time points inside the window, eligible
child indices are {1,2,3,4,5} and {4,5,6,7,8}. The first point in each window has no
in-window lag parent. That boundary is an explicit applicability limit, not evidence
that the underlying lagged cause is absent. Context outside the window can be
supplied only under a separately specified information boundary.

Condition: reorder variable columns while preserving time identities, timestamps,
units, values, masks and subject grouping. A second representation view converts
seconds to milliseconds and maps time/lag coordinates consistently. A lag of one
sample still means one second here; -1000 milliseconds and -1 second are different
encodings of the declared same temporal offset, not unchanged numeric labels.

Row reordering is not universally forbidden or harmless. If the native input
defines time by row order, a row shuffle changes the temporal evidence. If explicit
timestamps/group IDs preserve it and the native interface supports that representation,
the study can define a presentation-order control with suitable checks. A generic
iid-row recipe cannot silently decide which interpretation applies.

Reference: a declared stationary lag template is applicable only under its source/
regime and window assumptions. Absolute-time graphs, lag templates, temporal PAGs
and online state updates require their own meanings/readers; no static flattening
or inferred stationary reference is allowed. Native checkpoint/epoch state remains
separate from participant/case identity.

The comparison binds shared source/overlap, nuisance mappings and repeated native
draws. Its analysis must handle the actual temporal/subject dependence and limited
population scope. A held-out window overlapping a previously exposed one is not
an unseen independent sample by virtue of a new case ID. Missing boundary/time or
stationarity evidence blocks the affected comparison, not evidence preservation.

## 2. X02 / E: relational perspective with distributed access

Source: two hypothetical sites, each holding employee/firm objects and a worksFor
relation. The queried variables are Employee.productivity and
Employee.worksFor.Firm.trainingBudget from an explicitly defined employee perspective.
This is a relational variable path and scope, not proof of a direct real-world cause.

Local employee ID 17 at two sites is two scoped identities until linkage evidence
establishes otherwise. Several employees can share a firm budget; repeated values
are not new independent firm-level causes. Cross-site person/firm overlap can remain
unknown. Perspective, path/cardinality, joins and population sampling assumptions
must stay explicit in cases, tasks and references.

Access: sites retain raw records and expose only permitted typed responses. Example
contracts include a scoped CI query with its conditioning set/test semantics, or a
sufficient-statistic response with axes, sample-count meaning, centering/normalization
and applicable assumptions. Neither implies centrally available rows. A native p-value
is not automatically a probability of no causal edge. Combining local answers into
a population-level conclusion requires an explicit scientific aggregation procedure;
local independence does not silently become global independence.

Condition: rename presentation fields while preserving entity/relation identity,
joins, party provenance and permitted query meaning. Changing which firm is joined
to an employee changes the evidence; it is not a label-only permutation. A partition
layout contrast requires its own union/population and access-preservation rules.

The reference is a hypothetical documented relational claim with limited coverage,
supporting scoped agreement, not complete flat-graph truth. It must match the path,
perspective, entity universe and site/population scope. Unknown relationships do
not become negatives, and an aggregate employee variable is not automatically the
same as the firm-level relation path.

Adverse branch: one site's access/response is evidenced and the other remains
unavailable. Preserve planned two-site membership, actual messages, resource/gap
evidence and unknown overlap. A one-site output cannot be reported as a completed
two-site pooled study. Access and aggregate scientific readiness remain independently
scoped. No actual site, individual, endpoint, message or permission is involved.

## 3. X03 / F: learned variables and evaluator alignment

Source: hypothetical image/trajectory evidence with source-factor reference domains.
Native encoder/checkpoint E1 and E2 each expose a coordinate called factor_0; those
are different learned-domain members. Shared strings or equal dimension do not
establish equality to each other or to the source factors.

Task: preserve native learned-structure objects and evaluate only the explicitly
defined source/invariant target for which alignment is justified. Training/fitting
data, pretrained state, checkpoint identity, initialization and exposure are bound
separately from evaluation cases. A method whose output is already over observed
variables need not invent a learned-variable domain merely because it uses a model.

An evaluator alignment procedure is fixed before evaluation outcomes are used for
selection. Its calibration evidence may come from separately selected intervention
signatures with their own authority and information boundary. It can be resolved
after fitting because the native domain may not exist earlier; actual alignment
values are later evidence, not changes to the fixed procedure.

Illustrative ambiguity: calibration leaves two remaining permutation candidates
within its declared hypothesis family between learned coordinates z0/z1 and source
factors p/q. Preserve both candidates without claiming either is the established
true alignment.
They are not automatically probabilities, and the reader must not choose whichever
gives the best graph score. A comparison may use a predeclared invariant target,
an explicitly labeled range/ambiguity analysis, or withhold source-graph evaluation
until the needed alignment is established. A best-match oracle diagnostic would
be a separate declared question, not ordinary recovery accuracy.

The permutation hypothesis is specific to this example. Entangled/mixed, many-to-one,
dimension-changing and noninvertible representations require different mapping/
loss and causal-target contracts. Invertible feature mixing alone does not preserve
the original variable-level causal graph. Encoder interventions or calibration
truth are not native evaluation inputs unless a condition expressly permits them.

Comparison across E1/E2 binds their separate domain/model snapshots, source cases,
alignment procedures and target meanings. Training repeats can create new native
domains without creating new observed datasets. Unknown factor interpretation
can block aligned graph scoring while preserving meaningful native structure,
artifact provenance and other scoped observations.

## 4. X04 / G: weighted graph collections and confidence

One hypothetical native request returns four graph/parameter members:

| Member | Native graph | Unnormalized weight | Association |
|---|---|---:|---|
| g1 | X -> Y, Y -> Z | 2 | parameter object theta1 |
| g2 | X -> Y, Y -> Z | 1 | distinct parameter object theta2 |
| g3 | Y -> X, Y -> Z | 1 | parameter object theta3 |
| g4 | Y -> Z only | 2 | parameter object theta4 |

The supplied native contract claims these are weighted approximate posterior
members. Preserve that source claim and inference/model identity; a bootstrap
ensemble does not become a Bayesian posterior merely by sharing this container.
Normalization is a named derived operation with nonnegative/finite/positive-total
requirements and its own quantity/event semantics.

With total mass six, this illustrative finite measure gives adjacency mass
P(X adjacent Y)=4/6=2/3, directed mass P(X -> Y)=3/6=1/2 and conditional orientation
P(X -> Y | X adjacent Y)=3/4. These are different events. They are illustrative
arithmetic on specified members, not native probability estimates observed here.
Equal graph bytes for g1/g2 do not erase their distinct parameters/weights. A
declared marginal graph-mass view may aggregate them while retaining derivation.

The four members are not four independent datasets, trials or truth labels.
Monte Carlo dependence, shared training/data and native sampling meaning remain
explicit. Partial reference coverage cannot support calibration over all edges,
and event probabilities, heuristic scores, coefficients and p-values keep their
separate contracts. One case with several particles does not establish calibration.

A thresholded graph or selected representative is a separate derived object. For
another illustrative distribution, three equally weighted DAGs contain respectively
{A->B,B->C}, {B->C,C->A} and {C->A,A->B}. Every member is acyclic, but every cycle
edge has marginal mass 2/3. Thresholding marginals at one-half returns a directed
cycle. Do not silently repair it into a DAG or call it a native posterior member.

Threshold conventions, output role, representative/tie selection, losses and
reference applicability must be fixed for their own comparison. A malformed or
undefined derived view does not invalidate faithful preservation of the native
collection; it withholds the affected stronger interpretation/evaluation claim.

## 5. X05 / H: environments, interventions and measurement targets

Source: a hypothetical clean mechanism graph X -> Y -> Z, with three environment
descriptors: observational e0, perfect intervention e1 on Y, and an intervention
environment e2 whose target is not disclosed. Unknown target information is not
the same as an empty target set or an observational environment.

Two tasks must remain distinct:

- Recover the baseline mechanism graph using the declared multi-environment evidence.
  Its reference can remain the baseline X -> Y -> Z under the source assumptions.
- Recover the active manipulated graph in e1. Under the specified perfect-surgery
  model, the incoming X -> Y edge is removed; the reference/question differs.

Interventional input therefore does not automatically mean the evaluator should
cut edges in every reference. Bind the actual task. Soft/uncertain interventions,
latent targets and observational identifiability require their own contracts rather
than inheriting perfect-surgery semantics from a flag.

Group IDs, sample membership, intervention status/target/value/uncertainty and
information visibility must move with transformed evidence. A native route that
requires fully known targets is not ready for e2 unless it has an explicitly supported
unknown-target mode. Guessing targets or disabling a native stage silently would
change the evaluated method. A target-oracle control is separately identified.

Add a noisy measurement Y* = Y + E in a declared condition. Y* is a proxy with
its own measurement relation; a do(Y) action is not automatically a do(Y*) action.
The clean-source recovery target and observed-proxy structure target need different
applicability/alignment assessments. The proxy target may need an extended or
latent-variable reference family, or remain unestablished. Keeping the column label
Y cannot establish the missing scientific mapping.

A source-matched observational-versus-interventional comparison changes available
information and possibly realized rows. It is an explicitly declared control,
not identical-data ranking across regimes. Repetitions remain nested in source and
environment/measurement realizations, and partial target/measurement metadata
cannot be flattened into all-zero masks or silently pooled rows.

## 6. Common lifecycle and cross-family composition

Every variant binds source/case requirements, exact domains/task/reference meaning,
conditions/transforms, repetitions/comparison and commitment/authority limitations.
Future source/model/domain realizations and analysis receipts append to fixed
requirements. Interpretable local descriptors are not actual snapshots, grants,
alignment proofs or complete reference coverage.

Combine contracts at their actual interfaces. Temporal learned domains must preserve
both lag coordinates and encoder identity. Distributed interventional cases retain
site-specific targets/visibility and population structure. Posterior collections
over learned or temporal graphs retain each member's applicable domain/weight
meaning. Supporting components separately does not prove their combination valid.

The registry maps these requirements to the existing capability axes/cases. Such
mapping is a scope/obligation relation, not empirical evidence for those named
systems. Selected examples do not exhaust all combinations or justify a universal
coverage percentage. Unknown combinations stay preservable with scoped gaps.

## 7. Further composition resolutions

| ID | Proposed requirement | Cost and prevented failure |
|---|---|---|
| K01 | Temporal coordinates/window eligibility and participant overlap are explicit independent dimensions | More selectors/group evidence; prevents false independent cases and boundary negatives |
| K02 | Relational perspective and party provenance stay attached through remote/sufficient-statistic access | More typed interfaces/population rules; prevents invented central samples or global CI from local responses |
| K03 | Learned domains and calibration-derived alignments have separate identities, timing and ambiguity | More mapping contracts; prevents best-score alignment and identity by factor name |
| K04 | Native weighted collections preserve member/parameter/weight semantics and derived views separately | More event/measure checks; prevents pseudo-replication, false calibration and arbitrary graph repair |
| K05 | Reference targets distinguish baseline mechanisms, manipulated environments and measured proxies | More task/reference variants; prevents wrong-target accuracy and hidden intervention knowledge |
| K06 | Cross-family support requires compatibility evidence at the joined boundaries | Additional composed specimens/checks; prevents unsupported guarantees from a set of individually supported parts |

These are design proposals with examples, not implemented semantic readers or
validation gates that have passed. The candidate contract specifies the minimum
joint obligations and profiles to review before a bounded serializer/API pass.

## Where we're going

Review these five variants and K01-K06 alongside the candidate family/profile and
lifecycle rules. Resolve their semantic meanings and prerequisite/cardinality
contracts before freezing representation. Then proceed to bounded serialization,
exact S1/S2 handoff and legacy mappings, followed by recomposed examples and final
subsystem-2 design review. No implementation begins here.
