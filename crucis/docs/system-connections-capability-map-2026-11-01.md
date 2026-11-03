# W2 system connections: capability-space map (1 Nov 2026)

Tickets: DLV-08, DLV-09; neighbours DLV-10, ADV-01, DLV-06.
Status: researched design map for discussion. No implementation, protocol adoption, scope freeze, new system run,
finding-threshold change or result migration is authorized by this document.
Requirements: `system-connections-principles-2026-11-01.md`; subsystem boundaries:
`system-connections-design-2026-10-31.md`. Faithful evaluation is the first constraint.

## 1. What the map establishes

A system connection has more dimensions than a function from a numerical matrix to one graph. The design must
describe the task, information available, variable identities, interaction, result meaning, state and evidence.
Algorithm names alone do not describe this space: one algorithm can expose several interfaces, and a pipeline
can combine several algorithms. A configuration and an operating mode can change the applicable capabilities.

This map has 18 independently useful axes, a bank of 28 representative cases, four constructed combination
cases, a comparison with the current package, and requirements for preserving meaning. The case bank combines
published examples and the locally inspected integrations; the four combination cases are design probes.
The axis decomposition, proposed core boundaries and conformance requirements are our design synthesis.
They are not claims made by the cited authors.

This is broad coverage of the relevant connection space, not a proof that every future causal-discovery system
has been anticipated. A new system should either fit a documented combination or expose a named extension
that requires a contract and checks. No percentage of the entire field is asserted.

## 2. Research method and evidence status

Primary documentation, author repositories and author papers were inspected on 1 Nov 2026. Each external factual
example below links to its supporting source. The source notes in section 12 state what was checked. Search
snippets identified candidates; pages/paper excerpts were read to confirm the facts used. A Tavily extraction
rate limit was reached; browser retrieval confirmed the remaining relational, pairwise and GCM sources.
No installation, system execution, model call, benchmark run or training was performed.

These sources establish interface possibilities, not measured accuracy or working compatibility with our
package. Moving documentation branches are not executable version pins. Connecting a real system will require
checking its exact version and configuration. We do not adopt performance or privacy claims from README text.

Local claims are based on the inspected files listed in section 8. The earlier Windows test result remains
54 passed / 1 skipped; no tests were rerun for this document-only work.

## 3. The axes

### A01. Task and scope of the claim

Possibilities: discover a whole structure; identify a target's neighborhood, parents or ancestors; decide a
direction for a pair; recover causal variables and their relations; learn mechanisms alongside structure;
choose the next experiment. An effect estimate or root-cause ranking can accompany discovery but is a different
task. Preserve the target, requested variable universe, claim type and coverage of the answer.

Local discovery is a real task: GLL studies neighborhoods and Markov blankets [S18]. The causal-learn ANM/PNL
interfaces return directional test results for two input variables [S19][S20]. Thus a successful connection
need not imply a complete graph over every supplied variable.

### A02. Variable universe and identity

Possibilities: known scalar columns; mixed categorical/continuous variables; vector-valued blocks; variables at
lags; entities/attributes and relational paths; context nodes; learned latent factors; changing variable sets.
Separate stable identifiers from displayed names and integer positions. Preserve roles, types, units, category
encodings and mappings. Distinguish an observed variable, an inferred latent variable, and a context indicator.

CITRIS/iCITRIS motivate learned variables [S12]; relational causal discovery motivates relational identity [S15];
Tigramite motivates lagged identities and contemporaneous edges [S06]. A later representation must not assume
that every node is simply one original CSV column. Evaluation alignment of learned variables is a separate,
recorded procedure; reference truth must not leak into the system through that alignment.

### A03. Form of evidence accepted

Possibilities: typed raw samples; missing-value masks; sufficient statistics plus sample sizes; recorded
conditional-independence answers; a callable statistical-test/score service; variable names/descriptions;
unstructured observations; precomputed representations; supplied model artifacts. Record what was provided,
what the system accepted and which derived inputs were constructed.

pcalg explicitly accepts sufficient statistics and a user-supplied independence-test function [S03]. Our
PyWhy-LLM/causaliq adapters accept names/context without sample data [L05]. CITRIS uses image sequences [S12].
Raw-row transformations cannot automatically be applied to a correlation matrix or to an oracle endpoint.
Any conversion must have a declared purpose and preserve the evidence appropriate to that input type.

### A04. Sampling organization and data schema

Possibilities: independent rows; sequences and panels; several subjects/datasets; heterogeneous environments;
windows or streams; related entities; distributed partitions; missingness/masks and distinct measurement types.
Preserve row/subject/time/environment identities, temporal order, partition membership, and intended dependence.
Keep row count, variable count and effective sample-size meaning distinct.

Tigramite documents missing values/masks and continuous, discrete and mixed-variable testing [S06].
MultiGroupDirectLiNGAM accepts a list of datasets [S05]; FedCDI exchanges updates across distributed data [S16].
Pooling, flattening, imputation, resampling or standardization can change the audited procedure. Record whether
each operation belongs to the native system or to an explicitly defined experimental condition.

### A05. Environments and intervention information

Possibilities: observations only; known intervention targets, values or assignments; unknown targets; hard or
soft/imperfect interventions; several contexts; inferred context changes; adaptive interventions. Separately
record sample membership, intervention metadata supplied to the system, and metadata retained for evaluation.

DCDI treats perfect, imperfect and unknown-target interventions [S07]. JCI organizes discovery across contexts
with varying intervention knowledge [S10]. DiBS exposes per-sample intervention masks [S08]. A single boolean
named interventions cannot capture those distinctions. Unknown targets must remain unknown to the system;
an evaluator possessing targets does not authorize passing them through the connection.

### A06. Knowledge, restrictions and other information channels

Possibilities: names; descriptions; domain text; hard/soft edge requirements; forbidden edges; ordering/tiers;
ancestry/path constraints; initial graphs; candidate sets; expert answers; retrieval/tools; pretrained weights.
Preserve provider, content, strength, scope and timing. Record the actual information payloads or available
evidence for them, rather than relying solely on a broad regime tag.

pgmpy PC documents required/forbidden edges, temporal information and search restrictions [S04].
MultiGroupDirectLiNGAM's prior matrix describes directed paths, not simply direct edges [S05]. ExpertInLoop
can obtain human or LLM orientation answers [S11]. These meanings must not be collapsed into an untyped matrix.
Neutral names remove one information channel; they do not establish that domain context, pretrained priors or
other channels are absent. Existing regime definitions remain unchanged pending W5 review.

### A07. Assumptions and validity domain

Dimensions to declare or leave explicitly unknown: acyclicity versus feedback; causal sufficiency versus latent
variables; selection effects; independence/faithfulness assumptions; stationarity; mechanism/noise families;
functional forms; intervention model; which variables are measured; identifiability conditions. Distinguish a
system's claim from a condition verified by a test or asserted by the battery designer.

Tigramite lists different assumptions/output semantics for PCMCI+, LPCMCI and J-PCMCI+ [S06]. JCI's paper uses
SCMs broad enough to discuss latent causes and cycles [S10]; experiment-selection work explicitly considers
possibly cyclic and causally insufficient settings [S21]. This is not a claim that every JCI implementation
handles every setting. Declared assumptions determine applicable evaluation; they must not trigger silent
repair of outputs to satisfy a preferred model class.

### A08. Computational access and pluggable components

Possibilities: raw data access; sufficient statistics; conditional-independence or score functions; a prediction
or sampling model; an intervention/simulation endpoint; orientation/expert functions; graph-only artifacts.
Describe the operation, arguments, result semantics, version and invocation evidence. Do not replace a native
test/score/oracle with a convenient alternative without identifying a distinct system configuration.

pcalg's independence-test callback and ExpertInLoop's orientation callback establish concrete examples
[S03][S11]. A generic callback contract can reduce adapter code, but shared core code should not take over
the native discovery algorithm. An oracle used as an explicit experimental condition must be identified as such.

### A09. Interaction and authority to choose actions

Possibilities: one batch request/result; an internally staged workflow; callbacks; repeated model/tool/expert
requests; active intervention selection; stateful online updates; external user decisions. Record requests,
responses, ordering, authority and stopping conditions. Observing an action and supplying its answer are
different roles.

Adaptive online experimental design selects interventions based on sampling history [S14]. ExpertInLoop
requests orientations during discovery [S11]. A final graph alone cannot reproduce either interaction.
Core policy can limit permitted resources/actions; the native system retains its algorithmic choices.
Two adaptive systems may legitimately collect different data. Fair comparison then needs a shared initial
problem and resource protocol, not a forced identical final dataset.

### A10. Lifecycle, persistent state and randomness

Possibilities: stateless invocation; initialize/fit/infer separation; train once and infer many times; per-item
fitting; warm starts; update; checkpoint/resume; reset; caches; multiple random streams. Preserve boundaries
between training/tuning/evaluation, checkpoint identity, initialization and reset policy, seeds and carry-over.

AVICI separates pretrained prediction from training on simulated data [S13]. PC documents a cache whose data
and parameter hashes are checked [S01]; CORAL updates a model incrementally [S17]. Reusing a stateful instance
across items can alter the experiment. Replay of recorded responses is not a new experiment on transformed
inputs, and a seed alone does not establish reproducibility across remote models or changed environments.

### A11. Result objects and cardinality

Possibilities: one graph; an equivalence-class representation; weighted adjacency matrices; multiple graphs
with probabilities or weights; posterior samples; orders; local sets; pairwise test results; causal mechanisms;
learned encoders/representations; request/action histories; partial or abstained results. Results may contain
several related objects. Preserve the primary native object and identify every derived summary.

DiBS provides graph/parameter posterior samples [S08]; NOTEARS returns a weighted adjacency estimate [S09];
ANM/PNL return directional p-values [S19][S20]. A point graph selected from these outputs is an additional
decision rule. Requiring a point graph on every successful run would exclude valid discovery interfaces or
hide their actual output.

### A12. Graph and claim semantics

Distinguish: direct effects, ancestry/reachability, lagged relations, statistical associations, partial endpoint
marks, confounding claims, conflicts, and membership in an equivalence class. Declare graph family, endpoint
meaning, index convention, and the scope of absent entries. Preserve weights with their meanings and units.

FCI returns a PAG [S02]; pgmpy PC can return a partial structure or a chosen DAG orientation [S04].
PC conflict handling includes an option to orient bidirected [S01]. Thus a visual symbol cannot by itself
identify the causal meaning of every source's output. Two opposite directed assertions, a confounding edge,
an unresolved direction and legitimate feedback require distinct interpretations.
An edge from X at t-1 to X at t is not a contemporaneous self-loop. A missing edge in an unqueried part of a
local answer is not necessarily an asserted absence. Do not delete cycles or invent orientations during ingestion.

### A13. Uncertainty, decisions and abstention

Possibilities: no uncertainty output; p-values; structural coefficients; edge marginal probabilities; conditional
orientation probabilities; graph probabilities; posterior particles; bootstrap frequencies; intervals;
scores/ranks; explicit refusal; unresolved equivalence; unqueried or unreported pairs. Record the proposition,
conditioning, scale, sampling basis, decision threshold, and whether the number is system-stated or derived.

LiNGAM's bootstrap interface reports frequencies/probabilities and effects [S22]; DiBS provides posterior
samples [S08]; ANM/PNL produce p-values [S19][S20]. These are different quantities. In particular, a small
p-value is not a probability that an arrow exists, and a coefficient is not confidence. Preserve joint graph
samples when available: edge marginals alone do not preserve dependence between edges.
Distinguish declared no-edge, omitted/not evaluated, undecided and explicit abstention before measuring them.

### A14. Observability and provenance

Possibilities: final output only; native intermediate states; logs; queries and tool/model calls; native
per-claim sources; observation-only hooks; reconstructed stages; auditor-inferred arm attribution.
For each item of evidence record its origin, scope, completeness and mapping to the affected output/state.

The local package already distinguishes some sources and reconstructed Causal-Copilot stages [L04][L05][L06].
Do not promote an auditor inference to a system's own source declaration. A process log alone does not prove
that a particular call caused an edge. Hooks require a behavior-preservation check; unavailable internals must
remain unavailable rather than excluding all black-box systems from the audit.

### A15. Native execution and transport

Possibilities: in-process function; separate process/CLI; file exchange; container; remote synchronous request;
asynchronous job/polling; session or streaming endpoint; distributed coordinator; recorded artifact import.
Preserve native argument/configuration meaning, serialization versions and environment requirements. Describe
whether an adapter can execute, only prepare a command, or only read results in each mode.

These transport categories are engineering design possibilities, not claims that a cited system implements
every category. Our PC/GES direct calls and the LLM command-description route are distinct existing examples
[L05]. Reusable transport drivers may live in the core; endpoint-specific serialization stays in an adapter
until a general contract exists. Evaluation truth is not part of the native request unless explicitly authorized.

### A16. Resources, termination, partial results and failure

Dimensions: CPU/GPU time, memory, parallel workers, model calls/tokens, money, samples, interventions, queries,
human time; native convergence/termination versus externally imposed caps; completed versus usable partial
outputs; system exceptions versus adapter/parse failures, unavailable inputs, host faults, interruption and
unknown cause. Preserve attempts and partial evidence; do not turn malformed output into an empty successful graph.

Adaptive discovery has a native stopping condition [S14]; the local run type already separates some caps/host
failures [L02]. Resource policy is shared; native stopping decisions are part of the system. A refused action,
cache hit, repeated attempt and resumed run must not silently change the denominator of cost or completion.
Detailed accounting belongs to execution, while the connection must expose enough evidence to do it correctly.

### A17. Identity, configuration and reproducibility

Dimensions: system code and dependencies; adapter and all relevant shared translation code; hyperparameters;
preprocessing; prompt/templates; model/checkpoint and served snapshot; container/environment; seed streams;
cache/state snapshot; hardware/backend where relevant. Distinguish declared/pinned identity, observed identity,
and unknown identity. Record a resolved configuration rather than relying on unversioned defaults.

AVICI's pretrained checkpoints and DiBS's graph/likelihood models are examples of identity beyond an algorithm
name [S13][S08]. The local adapter-file hash and selected runner hashes are a start [L01][L05]; a thin wrapper's
hash alone cannot cover later changes to its shared converters. Reproducibility can mean deterministic
recomputation, verification of recorded evidence, or repeatable stochastic evaluation; identify which is offered.

### A18. Evidence availability and access boundaries

Dimensions: raw inputs/outputs available; hashed artifact references; aggregate-only output; remote service
records; distributed updates; inaccessible model internals; incomplete historical records; withheld ground
truth; permitted knowledge endpoints. Describe what can be checked, by whom and from which evidence.

FedCDI motivates data that remain distributed while updates are exchanged [S16]. This does not establish a
privacy guarantee for our auditor. A connection may preserve an artifact reference without possessing the
artifact; a certificate must then state the narrower verification claim. Unknown/inaccessible information must
not be fabricated or requested through a forbidden channel. Native-system, adapter-mode, representation,
evaluation and validation support are separate layers (section 7).

## 4. Representative case bank

Each row is an interface case, not a performance comparison, implementation commitment or claim of complete
support for the named library. Sources establish the stated feature; the contract pressure is our inference.

| Case | Representative | Input / interaction / output feature | Contract pressure |
|---|---|---|---|
| C01 | Current PC/GES [L05] | Static data; direct or recorded route; partly directed graph | Separate native invocation from stored import and preserve orientation rules. |
| C02 | Current GIES [L05] | Interventional data and targets; recorded-only adapter | Describe intervention information and actual mode readiness independently. |
| C03 | FCI [S02] | Data and CI configuration; PAG plus edge properties | Preserve graph family and endpoints; current generic method converter is not a general FCI integration. |
| C04 | PC/MV-PC configuration [S01] | Configurable CI tests, missing-value handling, caches | Configuration and data treatment are part of system identity. |
| C05 | pcalg with Gaussian sufficient statistics [S03] | Correlation matrix plus sample size and test function | Samples cannot be assumed present; a matrix's axes must be identified. |
| C06 | pcalg custom independence-test interface [S03] | Algorithm obtains CI answers through a callback | Query semantics, implementation identity and permitted evidence access must be explicit. |
| C07 | pgmpy PC [S04] | Knowledge restrictions and selectable partial/DAG result | Know which outputs are native and which are chosen orientations. |
| C08 | MultiGroupDirectLiNGAM [S05] | Several datasets; path priors; several adjacency matrices | Keep group identities and ancestry constraints separate from direct edges. |
| C09 | NOTEARS [S09] | Numerical data; configured optimization and weight threshold; weighted estimate | Preserve coefficients, threshold and any native preprocessing; do not treat weight as probability. |
| C10 | DCDI [S07] | Interventional datasets with perfect/imperfect or unknown targets | Preserve known-versus-hidden targets and the intervention model. |
| C11 | JCI framework/implementation choice [S10] | Multiple contexts and background assumptions | Context variables are explicit; framework name alone does not determine algorithm capability. |
| C12 | PCMCI+ [S06] | Time series; lagged and contemporaneous partial structure | Preserve lag, temporal order and graph semantics. |
| C13 | LPCMCI [S06] | Time series with latent-variable allowance; temporal PAG | Combine lagged identity with partial endpoint semantics. |
| C14 | J-PCMCI+ [S06] | Multiple time-series datasets; joint structure | Preserve dataset/context identity instead of silently concatenating rows. |
| C15 | DiBS [S08] | Data, graph/likelihood models, optional intervention mask; posterior particles | Retain graph collections and parameter associations, not just an averaged adjacency. |
| C16 | ANM/PNL interface [S19][S20] | Two variables; two directional p-values | A valid native result may not be a graph or an edge probability. |
| C17 | GLL local discovery [S18] | Target-specific local neighborhood/blanket | Preserve local coverage; unreturned distant edges are not negative predictions. |
| C18 | AVICI [S13] | Pretrained inference or separately configured training | Checkpoint/training distribution and reset/fit policy matter. |
| C19 | CITRIS/iCITRIS [S12] | Images in temporal intervention sequences; learned factors and structure | Preserve encoders and latent identities; evaluator alignment is separate from ingestion. |
| C20 | Relational causal discovery [S15] | Relational models and relational structure | Variable identity can involve schema/perspective, not flat column positions. |
| C21 | Adaptive online experiment design [S14] | Iterative intervention choice, sampling history and stopping | Requires a session/action transcript and comparable resource protocol. |
| C22 | ExpertInLoop [S11] | Iterative data analysis plus human/LLM orientation callback | Expert identity, questions, responses and cache history are evidence. |
| C23 | FedCDI [S16] | Distributed observations/interventions; exchanged updates | Partition identity and evidence access can matter even without centralized samples. |
| C24 | CORAL discovery component [S17] | Incremental graph updates inside an online RCA workflow | Preserve state/time; evaluate graph learning separately from the root-cause ranking. |
| C25 | Current PyWhy-LLM [L05] | Names/context only; recorded directed graph | Do not pretend numeric data were consumed. |
| C26 | Current causaliq [L05] | Names/context; underlying probabilistic output, incompletely extracted today | Native support differs from adapter extraction and calibration readiness. |
| C27 | Current MATMCD/Vashishtha [L05] | Data plus knowledge; variants and stated edge sources | Shared optional metadata with native semantics and valid variant comparisons. |
| C28 | Current Causal-Copilot [L06] | File/query interface; state/artifacts and reconstructed stages | Native file layout, version-specific traces, failures and reconstruction provenance all matter. |

DoWhy's GCM documentation provides an adjacent boundary example: a graph plus mechanisms can support
interventional/counterfactual tasks [S23]. A request to estimate an effect from a supplied graph does not by
itself test whether a system discovered that graph. Such outputs can be represented later without expanding
the present findings to cover them automatically.

The crosswalk below makes the coverage check explicit. A case being represented in this map does not mean
that our package supports it; section 8 records the current support boundary.

| Axis | Cases that put pressure on it |
|---|---|
| A01 task/scope | C16 pairwise, C17 local, C19 representation learning, C21 experiment selection |
| A02 variable identity | C11 context nodes, C12-C14 lagged nodes, C19 learned factors, C20 relational identity |
| A03 evidence form | C05-C06 statistics/callbacks, C19 images, C25-C26 names/context |
| A04 sampling/schema | C04 missing data, C08 groups, C12-C14 time, C20 relations, C23 partitions |
| A05 interventions/contexts | C02 targets, C10 unknown/imperfect targets, C11 contexts, C21 adaptive experiments |
| A06 knowledge/channels | C07 edge restrictions, C08 path priors, C18 pretrained weights, C22 expert answers |
| A07 assumptions | C03 latent-variable output, C10-C14 environment/time assumptions, C20 relational setting; S21 feedback setting |
| A08 computational access | C06 statistical callback, C21 experiment endpoint, C22 orientation callback |
| A09 interaction | C21 active sampling, C22 expert queries, C24 online workflow, C28 stages |
| A10 state/lifecycle | C04 caches, C18 training/inference, C21 history, C24 updates |
| A11 result families | C03 partial graph, C08-C09 weights, C15 particles, C16 tests, C17 local set, C19 encoder/factors |
| A12 graph/claim meaning | C03 PAG, C07 partial/chosen DAG, C08 path prior, C12-C14 time, C17 local coverage |
| A13 uncertainty/abstention | C09 coefficients, C15 posterior, C16 p-values, C26 native probabilities; S22 bootstrap |
| A14 provenance | C22 callbacks, C27 native source labels, C28 reconstructed stages |
| A15 execution/transport | C01 direct versus recorded, C02 recorded-only, C23 distributed, C25-C28 command-described routes; H01 remote job |
| A16 resources/failures | C21 sampling/stopping, C22 expert requests, C28 recorded failures/costs |
| A17 identity | C04 test/cache/configuration, C15 graph/likelihood model, C18 checkpoint, C28 code/model/image |
| A18 evidence/access | C23 distributed data, C25-C28 historical artifacts, H01 remote evidence, H04 restricted partitions |

There is no requirement to enumerate the entire Cartesian product: some combinations are incompatible with
a method's assumptions. The obligations are to state those conditions, check every axis, and exercise important
interactions between axes before claiming support.

## 5. Combination probes: independent axes must compose

These four cases are constructed design exercises, not claims about a deployed system. They identify gaps
that a list of individually supported features could hide.

| Probe | Combination | What a faithful connection must preserve |
|---|---|---|
| H01 | Time-series latent-variable discovery returning bootstrap graph collections through a remote job | Lagged identifiers and endpoints inside every replicate; job identity; no bootstrap-frequency/posterior conflation. |
| H02 | Active discovery with unknown intervention targets and a bounded experiment service | Intended action, permitted response, actual target knowledge exposed, sampling history, cap and stopping reason; no evaluator-only target leak. |
| H03 | Stateful hybrid with numerical data, retrieved text and an expert callback, resumed from a checkpoint | All supplied information, checkpoint/cache identity, native action sequence and per-attempt resource evidence. |
| H04 | Learned latent factors across distributed temporal datasets | Dataset/partition identity, observed-versus-learned variable roles, versioned encoders, alignment policy and the limit of accessible evidence. |

An architecture that needs a branch named after one of these systems to interpret its semantics has not yet
generalized that capability. Conversely, an arbitrary dictionary that stores the bytes without a specified
meaning has not established semantic support.

## 6. Semantic distinctions that cannot be erased

| Distinction | Why it changes evaluation |
|---|---|
| Direct edge versus ancestor/path constraint | A prior or result about reachability is not an assertion of an immediate connection. |
| PAG endpoint versus arbitrary undecided pair | The retained endpoint can constrain ancestry even when a complete direction is unresolved. |
| Confounding versus conflicting arrows versus feedback | Similar drawings can encode different causal claims or inconsistent output. |
| Whole graph versus local/query coverage | Unasked pairs must not count as asserted absences. |
| Point graph versus joint graph distribution | Independent marginals cannot recover all joint structural uncertainty. |
| Coefficient versus score versus p-value versus probability versus bootstrap frequency | They have different events, scales, conditioning and calibration targets. |
| Native source declaration versus logged event versus inferred attribution | Only the first is what the system itself claims as provenance. |
| Native thresholding versus evaluator projection | Both must be identified; applying either silently changes the reported system output. |
| Known-to-evaluator versus supplied-to-system | Evaluation truth must not become an unintended information advantage. |
| Native no-edge versus abstention versus unresolved versus unreported | Completion and abstention findings depend on the distinction. |
| Training/pretraining versus per-item discovery versus online updating | Reused state or learned priors change both system identity and the experiment. |
| Same-problem static comparison versus same-budget adaptive comparison | Legitimate adaptive policies can produce different acquired datasets. |

These are representation requirements. They do not authorize replacing existing scorers or thresholds.
If an existing metric intentionally projects partial marks under a stated rule, retain that rule as an explicit
evaluation view, alongside the native result. Preserve the current historical comparisons as historical ones.

## 7. What the word supported must mean

For each feature and mode, a future capability record should answer at least these questions:

1. **Native support:** can the exact system/configuration produce or accept it? Evidence may be documentation,
   a system declaration, an observed artifact or a controlled check; identify which.
2. **Connection access:** can this adapter actually deliver/read it in this mode? Preparing a command is not
   executing it. An absent historical file differs from an inaccessible interface.
3. **Semantic preservation:** can the core retain its relevant meaning and coordinate relationships?
4. **Evaluation availability:** is an appropriate procedure defined for this task/output/reference, and are its
   required inputs present? Carrying a result is not scoring it.
5. **Validation evidence:** which conformance checks and evaluation checks have run on this path and version?

Conditions attach to features: data types, graph family, known targets, mode, required artifacts and dependencies.
Distinguish supported/observed from unsupported, unknown, unrecorded and unavailable. These are conceptual
availability states, not additions to the protocol's finding-verdict enum. Do not label a scientific property
not_applicable merely because an adapter has not implemented a way to examine it.

Example: causaliq has native probabilities, but its current recorded adapter leaves RunRecord.confidence empty.
The current core has an untyped confidence slot, while K14 extraction/evaluation is incomplete. The native
feature is present; the whole evaluation path is not [L02][L05].

## 8. Comparison with the current audit package

The inventory below concerns the inspected `audit` package, not every tool elsewhere in the repository.
Labels: existing = implemented for the current paths; partial = a useful foundation with narrower semantics;
absent = no documented connection contract/integration in the inspected package. No new runtime checks were run.

| Area | Current state | Consequence for generalization |
|---|---|---|
| Static numerical inputs, names, context | Existing Presented fields and current adapters [L01][L05] | Retain foundation; make information delivery and types explicit. |
| Interventions and knowledge | Partial: optional dictionaries; recorded GIES; transforms and limited regime labels [L01][L05][L07] | Need typed meanings, visibility and capability conditions, not just presence. |
| Missing/mixed/temporal/relational/distributed data | No corresponding general connection contract in the inspected package | A NumPy object or metadata dictionary alone does not establish faithful support. |
| Variable remapping | Existing positional permutation for graphs, variants, source labels and stages [L03] | Rich variable identities, lag/partition roles and confidence-key remapping remain unspecified. |
| Directed, undirected, bidirected and partial marks | Existing representation and Causal-Copilot conversions [L04] | Need graph-family meaning and stronger source-specific preservation contracts. |
| Generic method converter | Partial: other non-directed endpoint combinations become undecided [L05] | Cannot be advertised as lossless ingestion for arbitrary PAG-producing methods. |
| Weights, joint graph collections, orders, local claims, learned encoders, mechanisms | No first-class contract in inspected RunRecord/Graph [L02][L04] | A mandatory single-graph success result is too narrow for the mapped space. |
| Confidence and edge sources | Partial: optional fields; some sources extracted, confidence not parsed for causaliq [L02][L05] | Need quantity/proposition semantics, missingness and evidence origin. |
| Recorded/direct/command-only routes | Existing, but heterogeneous [L01][L05][L06] | Mode readiness must describe the actual route and prerequisites. |
| Sessions, active requests, online state, distributed protocols | No general connection/session contract in inspected package | Optional session/action semantics must be designed before these are claimed. |
| Traces and variants | Existing optional records and generic observation hooks; specialized CC reconstruction [L02][L06][L08] | Preserve observed versus reconstructed versus inferred provenance; no universal stage promise. |
| Status, costs and attempts | Existing typed statuses, cost dictionaries, CC replicates [L02][L06] | Extend conceptual accounting to additional resource types and distinguish adapter versus native failures. |
| Identity and evidence hashes | Existing adapter/selected runner/raw artifact hashes [L01][L05][L06] | Shared semantic code, resolved configuration, state and observed runtime identity need an explicit coverage contract. |
| Scientific evaluation | Existing graph and DV-1 metrics route to shared implementations [L09] | No automatic evaluation claim for new output families, temporal relations or local scopes. |
| Capability checks | Existing conformance tests and prior recorded-run evidence [L10] | Not a guarantee of every advertised mode, all metadata, or every mapped system family. |

One specific semantic boundary deserves W5 discussion: `audit/protocol/regimes.py` recognizes names/knowledge
as K but does not use context text in that decision [L07]. Richer information accounting should preserve actual
payloads before any proposed change to regimes. The existing historical labels are not rewritten by this map.

## 9. Reusable core capabilities suggested by the map

The following are architectural seams to discuss, not modules approved for implementation:

| Reusable responsibility | What it could standardize | What remains native/system-specific |
|---|---|---|
| Variable/schema handling | Stable IDs, types, mappings, lags, roles and declared coverage | Discovering the meaning of undocumented output positions or learned factors. |
| Information presentation | Explicit payloads, permitted channels, derived-input lineage, content hashes | Native format, prompts and configuration meaning. |
| Result representations | Named semantic families for graphs, collections, claims, uncertainty and artifact references | Parsing an idiosyncratic output and resolving documented conventions. |
| Execution transports | Function/process/container/service/artifact routes and shared resource enforcement | Entry point, arguments, installation and service-specific job protocol. |
| Optional interaction | Typed requests/responses, action authorization, transcript and state links | Which algorithmic action the system chooses next and how it updates. |
| Provenance and identity | Native/observed/reconstructed/derived origins, dependency/configuration/artifact identities | Which native artifacts establish those identities and meanings. |
| Conformance | Common invariants and capability-path checks | Version-specific fixtures demonstrating a native translation. |

A small common envelope plus optional, explicit capability contracts is a promising direction. An enormous
mandatory interface would burden simple systems; an unrestricted payload without semantics would burden every
downstream consumer and allow silent disagreement. Both costs need to be evaluated when we design the contract.
Core growth should be justified by a reusable invariant and examples, while keeping native evidence available.
Adapter length is not an acceptance metric.

## 10. Candidate acceptance checks, to define before implementation

These are design obligations, not tests written or executed in this mapping step:

- A variable permutation preserves every graph, sample axis, prior, probability, variant and stage relation;
  inverse mapping restores meaning, including temporal and partial-endpoint orientation.
- Lossless translations preserve semantics; any non-invertible projection records what was lost and its rule.
  Retaining native evidence is required even when a standardized view is adequate for one metric.
- Raw rows, sufficient statistics and oracle queries retain distinct input identities; incompatible controls
  are refused or reported unavailable instead of being approximated silently.
- Direct edges, path constraints, cycles, local coverage and partial endpoints retain their declared meaning.
- Every uncertainty quantity identifies its event and source; no fabricated probabilities or provenance.
- A native non-graph result can be recorded as such even if no compatible evaluator is available yet.
- Advertised execution routes match their demonstrated readiness; command preparation does not pass execution
  conformance. Recorded import, response replay and fresh execution are tested separately.
- Sessions preserve ordering, state/reset/checkpoint policy, permitted information, attempt/resource accounting
  and native versus forced stopping; recorded replay refuses unmatched requests without falling back to spend.
- Adapter/translation failures remain distinguishable from native failures and host interruptions where the
  evidence permits; unknown causes stay unknown.
- Declared versus observed identity and missing evidence are explicit. Shared converter changes cannot evade
  identity just because the thin wrapper file is unchanged.
- Each shared capability is exercised by structurally different examples; H01-H04 reveal composition failures.
- Existing stored-number and certificate obligations remain separate checks before any later migration.

## 11. Scope choices now made visible, but not decided

| Choice | Broad option | Narrower option | Cost / failure to avoid |
|---|---|---|---|
| Success result | Envelope supports several semantic result families | Graph outputs only for the first supported scope | Broader design needs typed optional objects; narrower scope must reject/preserve other results honestly rather than invent a graph. |
| Dataset contract | Explicit typed dataset families | Static tabular data initially | Broad implementation is costly; premature flattening destroys temporal/relational meaning. |
| Interaction | Optional sessions/actions and transcript | Batch/recorded interfaces initially | Session policy and state add complexity; a batch-only scope must not claim faithful active/online evaluation. |
| Scope of knowledge | Record separate supplied channels and their origins | Keep current labels for current historical audits | Channel detail expands records; broad labels can hide context, tools and training priors. Historical protocol edits require adoption. |
| Output normalization | Preserve native object plus declared standard views | Only standardized objects for a selected family | Raw evidence adds storage; undocumented normalization changes evaluated claims. |
| Support claims | Layered, conditional support by mode/version | A short capability list | Layering adds bookkeeping; booleans overstate extraction, execution and evaluation readiness. |

No option is accepted merely by appearing here. The next discussion should choose the intended supported scope
from this map, then define the common contract and capability modules. Implementation still waits for Uzair's go.
All changes to shared protocol/contract meanings remain proposals to W5.

## 12. Source notes

External sources below were accessed 1 Nov 2026. Notes identify the narrow facts relied on, not an endorsement
of all author claims or a guarantee of present package compatibility.

- **S01 — causal-learn PC documentation.** Configurable tests, missing-value mode, conflict-orientation policy,
  background knowledge and hash-checked CI caches [S01].
- **S02 — causal-learn FCI documentation.** PAG result and separate edge properties, plus CI/background inputs [S02].
- **S03 — pcalg author software paper and manual.** Sufficient-statistics example uses correlation and sample size;
  user-supplied CI callback takes variables, conditioning set and sufficient statistics [S03][S03b].
- **S04 — pgmpy PC documentation.** Required/forbidden/temporal/search knowledge and partial versus selected DAG outputs [S04].
- **S05 — MultiGroupDirectLiNGAM documentation.** List of datasets, adjacency matrices and directed-path prior semantics [S05].
- **S06 — Tigramite author repository.** Method/assumption/output table, lagged and contemporaneous structure,
  LPCMCI PAG, joint datasets, missing masks and different data/test types [S06].
- **S07 — DCDI author paper, contributions and intervention sections.** Perfect, imperfect and unknown-target settings [S07].
- **S08 — DiBS author repository, overview/quick start.** Graph and parameter particles, graph/likelihood models
  and sample-by-variable intervention mask [S08].
- **S09 — NOTEARS author implementation.** Weighted estimate, configured losses and explicit weight threshold [S09].
- **S10 — JCI author paper/abstract.** Multiple-context framework, background knowledge, intervention varieties;
  paper's SCM discussion includes latent causes and cycles [S10][S10b].
- **S11 — pgmpy ExpertInLoop documentation.** Iterative orientations supplied through a human/LLM/custom callback;
  cache option and orientation/knowledge arguments [S11]. The page is a legacy API entry; this is an interface
  example, not a recommendation to integrate that deprecated path.
- **S12 — CITRIS/iCITRIS author repository.** Temporal image sequences, causal representation learning, learned
  factors and instantaneous/temporal structure under stated intervention assumptions [S12].
- **S13 — AVICI author repository.** Pretrained prediction and separate training support, with checkpoint choices [S13].
- **S14 — adaptive online experimental-design author paper/abstract.** Intervention selection from history and
  a native confidence-dependent stopping condition [S14].
- **S15 — relational causal discovery author paper abstract.** Discovery of relational causal models rather
  than only a flat variable DAG [S15]. Detailed relational serialization has not been selected or verified here.
- **S16 — FedCDI author repository.** Distributed observational/interventional data and exchanged updates [S16].
  No security/privacy property is claimed by our map from that description.
- **S17 — CORAL authors' NEC Labs publication page.** Incremental graph learning inside a triggered online RCA
  workflow and a separate root-cause localization step [S17].
- **S18 — GLL author paper abstract.** Target-local direct-cause/effect and Markov-blanket discovery [S18].
- **S19/S20 — causal-learn ANM/PNL API documentation.** Pairwise input and forward/backward p-values [S19][S20].
- **S21 — experiment-selection author paper abstract.** Explicitly includes possibly cyclic/causally insufficient settings [S21].
- **S22 — LiNGAM bootstrap API.** Adjacency collections, direction counts, bootstrap probabilities and total effects [S22].
- **S23 — DoWhy GCM types documentation.** Structure plus mechanisms and distinct intervention/counterfactual tasks [S23].

Local inspected sources:

- **L01:** `audit/core/adapter.py` — inputs, Capabilities, Presented, registry and Adapter methods.
- **L02:** `audit/core/runs.py` — graph-required successful RunRecord, optional metadata, statuses and replicates.
- **L03:** `audit/core/harness.py` — existing presentation and positional remapping.
- **L04:** `audit/core/graph.py` — graph marks, source conversions, retained CC raw matrix and canonical form.
- **L05:** `audit/systems/{_methods,_probe,pc,ges,gies,matmcd,vashishtha,pywhyllm,causaliq}.py` — native declarations
  and recorded/direct/command routes. LLM confidence extraction remains incomplete.
- **L06:** `audit/systems/causal_copilot.py`, `audit/trace/cc_stages.py` — stored versions, command description,
  recorded artifacts and reconstructed stages.
- **L07:** `audit/protocol/regimes.py`, `audit/controls/transforms.py` — existing information labels and transforms.
- **L08:** `audit/trace/recorder.py` — observation hooks and stage evidence.
- **L09:** `audit/metrics/l0.py` — calls shared scoring, with explicit historical projection/orientation rules.
- **L10:** `tests/test_audit_{core,trace,rerun}.py` — inspected conformance and prior evidence, no new test execution.

[S01]: https://causal-learn.readthedocs.io/en/latest/search_methods_index/Constraint-based%20causal%20discovery%20methods/PC.html
[S02]: https://causal-learn.readthedocs.io/en/latest/search_methods_index/Constraint-based%20causal%20discovery%20methods/FCI.html
[S03]: https://stat.ethz.ch/Manuscripts/buhlmann/pcalg-software.pdf
[S03b]: https://cran.r-project.org/web/packages/pcalg/refman/pcalg.html
[S04]: https://pgmpy.org/api/generated/structure_learning/pgmpy.causal_discovery.PC.html
[S05]: https://lingam.readthedocs.io/en/latest/reference/multi_group_direct_lingam.html
[S06]: https://github.com/jakobrunge/tigramite
[S07]: https://proceedings.neurips.cc/paper/2020/file/f8b7aa3a0d349d9562b424160ad18612-Paper.pdf
[S08]: https://github.com/larslorch/dibs
[S09]: https://github.com/xunzheng/notears/blob/master/notears/linear.py
[S10]: https://jmlr.org/papers/v21/17-123.html
[S10b]: https://jmlr.org/papers/volume21/17-123/17-123.pdf
[S11]: https://pgmpy.org/api/generated/structure_learning/pgmpy.estimators.ExpertInLoop.html
[S12]: https://github.com/phlippe/CITRIS
[S13]: https://github.com/larslorch/avici
[S14]: https://proceedings.mlr.press/v235/elahi24a.html
[S15]: https://arxiv.org/abs/1309.6843
[S16]: https://github.com/aminabyaneh/fed-cdi
[S17]: https://www.nec-labs.com/blog/incremental-causal-graph-learning-for-online-root-cause-localization
[S18]: https://www.jmlr.org/papers/v11/aliferis10a.html
[S19]: https://causal-learn.readthedocs.io/en/latest/search_methods_index/Causal%20discovery%20methods%20based%20on%20constrained%20functional%20causal%20models/anm.html
[S20]: https://causal-learn.readthedocs.io/en/latest/search_methods_index/Causal%20discovery%20methods%20based%20on%20constrained%20functional%20causal%20models/pnl.html
[S21]: https://jmlr.org/papers/v14/hyttinen13a.html
[S22]: https://lingam.readthedocs.io/en/latest/reference/var_bootstrap.html
[S23]: https://www.pywhy.org/dowhy/v0.14/user_guide/modeling_gcm/graphical_causal_model_types.html
