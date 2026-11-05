# S3 minimum record, conditional requirements and capability/support matrix

Tickets: DLV-08, DLV-09; related DLV-10.
Date: 2026-11-03, America/Los_Angeles.
Status: MS01-MS12 are proposed semantic refinements pending review. Cardinalities
below are precise semantic obligations, not frozen wire names/enums or an implemented
SC-3 schema. No S3 implementation, native scientific run, paid campaign, production
policy, protected-store access or remote publication.

## 1. Continuation and evidence boundary

The user affirmed [the consolidated outline](subsystem3-contract-outline-worked-cases-2026-11-03.md),
committed as 0174e3655ad0dd98a0db35835ba2a10a5dcd16c2, and requested precise minimum
versus conditional records and capability/support requirements checked against its
four examples. CS01-CS12 are direction-affirmed with exact details open, not blanket
interface acceptance or implementation approval. MS01-MS12 below remain proposals.

The original [117-entry examples](subsystem3-contract-examples-2026-11-03.json) retain
their exact bytes/hash. They were documentary semantic traces, not completed SC-3
records. The new [requirements overlay and matrix](subsystem3-requirements-case-matrix-2026-11-03.json)
pins that source and explicitly supplies proposed metadata annotations where the
earlier sketches were silent. It is not a native receipt, runtime test or wire
specimen. [The methodology index](subsystem3-methodology-index-2026-11-03.json) records
this status separately from existing S1/S2 primitive evidence.

## 2. Three separate judgments (MS01)

1. **Preservable full account view:** the required semantic shape, scope and reference
   rules hold. Unknowns, failed actions, unfulfilled responses and unsettled liabilities
   may all be faithfully preserved. This does not grant execution authority.
2. **Admissible operation:** the exact next effect satisfies its applicable scientific,
   environment, owner, resource/exposure, validity and receiver prerequisites at the
   required boundary. A structurally valid partial account can still hold this effect.
3. **Supported claim/handoff:** a named claim has adequate evidence and procedure
   within its scope/cutoff. Native termination, response fulfillment, causal correctness,
   byte integrity, confidentiality and settlement remain independent questions.

An audience projection is a separate derived view. If it cannot disclose the account's
required identity/target or other minimum meaning, it declares its projection scope;
it does not label itself a complete full account view. A full view may still reference
restricted/unavailable evidence with truthful gaps when its required meanings can
be preserved without prohibited disclosure. Unrecognized/malformed source material
can be preserved as raw evidence without pretending it conforms to the full-view contract.

## 3. Precise universal minimum for a full account view (MS02)

The six account blocks remain unchanged. The following 15 obligations specify
their minimum contents. A field can be inline or satisfied by an exact shared
reference where its meaning is retained; this does not demand 15 new record types,
UUIDs or duplicated definitions. Proposed names are documentary labels.

| ID | Required meaning/cardinality | Known versus explicitly unresolved |
|---|---|---|
| M01 Structural contract | Exactly one identified structural contract/revision for interpreting this view | Exact contract required for a conformance claim; unknown source format can instead remain raw evidence |
| M02 View role | Exactly one declared role: full account view for this minimum | A derived projection names its different role/scope; not disguised as a full view |
| M03 Account identity | Exactly one stable commission/account reference | Identity established; source/native grounding within its target can remain unknown |
| M04 View identity | Exactly one immutable view identity, distinguishable in role from the stable account | New content/cutoff gets new immutable identity; exact encoding follows later |
| M05 Recorder/provenance | Exactly one recorder/component reference and explicit provenance basis; record-time knowledge and procedure/context reference | Recorder identity and basis supplied; original native author/time or implementation assurance may remain unresolved |
| M06 Fixed target/purpose | Exactly one commissioned target definition with preparation/execution/observation purpose, exact scope and version relationships | Requested target is described; final S2 binding, original launch or native ID are conditional rather than invented |
| M07 Audience/context | Exactly one intended view audience/purpose/disclosure scope, with policy/authority references or explicit unknowns | Stated intended scope required; an authority claim needs actual owner evidence, not this declaration |
| M08 Evidence frontier | Exactly one scoped basis/frontier descriptor identifying this view's admitted local evidence/record set or positions | Local scope/basis explicit; native time, global completeness and external source positions can remain unknown |
| M09 Requirement context | Exactly one requirement-catalog/claim context, requested-claim index and applicability/assessment coverage | Catalog and claimed scope explicit; unexamined/unknown applicability and withheld claims remain visible |
| M10 Activity index | Exactly one scoped index of locally recorded activities/associations, with 0..n members | Empty/complete only for the named local scope; not a negative claim about all native work |
| M11 Evidence index | Exactly one scoped index of captured/reported evidence, artifacts, outputs and dependencies, with 0..n members | Unavailable, declared-only and unexamined evidence distinguished from known absence |
| M12 Assessment index | Exactly one scoped index of assessments, with 0..n members | No members means no completed assessment in that scope, not every predicate false |
| M13 Disposition | Exactly one scoped coordinator disposition or explicit no-selection/unresolved disposition | Intended next operations can be empty; no serialized decision creates permission |
| M14 Obligation index | Exactly one scoped index of unresolved/tracked effects and owner/resource/exposure/stop/cleanup/publication obligations, with 0..n members | Unknown owner/liability is recorded; empty local scope does not discharge external effects |
| M15 Collection index | Exactly one scoped index of collection periods/closure views, with 0..n members | Can be empty at bootstrap; an actual collection/claim triggers the applicable period/source requirements |

Every index supplies its subject/scope, membership, extent/coverage and gaps within
the existing epistemic distinctions. Explicitly partial/unexamined/unresolved
membership is valid where the contract permits it. A known internal reference must
resolve with its declared type; unknown/external/declaration mechanisms cannot be
replaced with a dangling internal reference. An unresolved outcome/liability after
a potentially effectful command needs a pending question/obligation or adequate
settlement/non-applicability evidence, not a silently empty complete obligation list.

### Bootstrap example

A new preparation commission can have known E/V/recorder/target, an exact structural
context and a local creation frontier; its activity/evidence/assessment/collection
indices can be empty within their explicit scopes. Disposition says no effect yet
selected/admitted. Locally tracked new obligations are empty. Scientific/source
requirements not yet resolved are represented in requirement coverage. There is
no R/A/N, native cursor, checkpoint or reservation to invent. The view is preservable;
it does not establish readiness, rights or zero effects outside its local scope.

Account/view/native/scientific occurrence roles remain distinguishable even where
storage co-locates meanings. A package may serve as the immutable view boundary when
the identities/contents genuinely coincide; a newer view never mutates an old identity.
Manifest-digest/publication receipts remain external to their exact hashed subjects.

## 4. Conditional requirements: explicit triggers and missingness (MS03-MS04)

Conditional means required when its trigger applies, not optional documentation.
Evaluate applicability from fixed intent, recorded/observed activity and requested
claims, including failed/uncertain effects; never only from successful execution.

- **Applies:** supply the required roles/evidence, or explicit scoped missingness/gaps
  naming what is unestablished. Preservation may remain valid; the dependent operation/
  stronger claim is held when it needs those missing facts.
- **Does not apply:** a scoped rule/basis permits omission of the payload. This is
  not unknown. A compressed scoped assessment can cover several inapplicable families.
- **Applicability unknown/not examined:** retain that coverage and withhold claims/
  effects requiring established applicability. Do not silently omit the uncertainty.

Visible positive triggers cannot be waived by a generic not-examined catalog flag.
An observed unauthorized or historical effect can be preserved with absent/unknown
original authority; do not fabricate a grant or commission. Controlled future effects
still need actual applicable admission. The following 18 families cover the common
semantics; exact field encoding/closed family catalog follows serialization review.

| ID | Trigger | Required conditional meaning and cardinality |
|---|---|---|
| C01 Scientific binding | S2 intent is used, or scientific membership/conformance is claimed | Exact applicable intent/task/condition/source/trial references and timing; final binding 0..n while prospectively unresolved, required exact applicable binding before the native effect that depends on it |
| C02 Source/transform realization | A recipe/provider/fitted/generated input is intended, attempted or reported | Spec/procedure/inputs, resolved parameters and actual output/check/gap indices; randomness/fitted-state/domain/reference evidence where applicable; 0 outputs permitted after failed/unattempted realization |
| C03 Presentation/staging | Native inputs are prepared, made reachable, transferred or claimed | Exact content/selector/encoding/domain roles, intended/actual audience/endpoint, stable-use guarantee, staged-member/transfer extent and disclosure gaps; no final B required for independently admitted prospective staging |
| C04 Effect/admission | A controlled effect command is planned/issued, or a native/owner effect is observed | Exact command if commissioned here, target/operation/dependencies, evidence cutoff, authority/requirements/reservations, transmissions/receipts/uncertainty; observed unknown original intent remains unknown rather than reconstructed as prospective |
| C05 Native association/attachment | Native work is invoked/reported/targeted, or lookup/attachment/control requires identity | Scoped episode/candidate inventory and association evidence; launch may precede assigned N; local external-ID non-applicability justified; existing-target control needs adequate identity; 0..n runtime connections as supported |
| C06 Ownership/concurrency | Shared writer/effect ownership, takeover, competing consumers or exclusion/revocation is relevant | Actual owner/context scope, validity and sender/receiver enforcement or limits; current authority separate from historical native work |
| C07 Collection/progress | Observation/capture starts, resumes, closes, or coverage/replay is claimed | Period/scope/bounds/frontier and per-source/episode/protocol/filter/generation; fetched/captured/interpreted/acknowledged progress as applicable; no fabricated cursor for a one-shot/noncursor source |
| C08 Artifacts/interpretation | Captured/reported material or derived output/interpretation exists or is claimed | Exact content identity or declared-only gap, extent/availability/format/selector and output role/domain/coverage; procedure/version/basis for derived interpretation; partial bytes are not an invented full answer |
| C09 Native action | Native action/question is observed or targeted | Session/episode/action correlation, typed arguments/content/source scope and pending validity; text equality alone cannot establish identity; unknown original attempt remains explicit |
| C10 Native-action decision/provider | A native-action response decision is evaluated/selected, or a planned response choice depends on required information | Permitted rule/provider and exact information frontier, selected-index/cardinality and gaps; failed/held choice can have no selected member, not a fabricated V2; coordinator dispositions and S2 output selection retain their own C04/C01/C08 requirements |
| C11 Delivery | A response/abstention is intended, transmitted, observed or reconciled | Exact correlated action(s), response bundle, recipient/endpoint and applicable validity/authority/resource/exposure, command/transmission/receipt scope; successful delivery is distinct from selection/access/use |
| C12 Recovery/state | Coordinator recovery/reconnection, native retry/restart/restore/continuation or continuity claim occurs | Actual recovery kind/policy and request/association relations; predecessor/successor attempt roles only when applicable; checkpoint/component/load evidence where used, unknown state, overlap eligibility and all retained attempts; reconnection does not invent a successor native attempt |
| C13 Stopping/control | Native termination/stop is assessed/reported/controlled or escalation is proposed | Exact target/component/descendant scope, requested versus acknowledged/observed outcome, applicable policy/authority and bounds; assessing unknown stop does not require a fictitious cancellation command |
| C14 Resources | Resource policy, capacity/reservation, usage/billing/limit/settlement is relevant | Kind/units/owner/member/time scope, quantities or explicit unknowns, measurement/aggregation/revision/finality, remaining liability and control overhead; no universal all-resource meter required |
| C15 Information/exposure | Information constraints, disclosure/access/use or allowance history is relevant | Permitted source/recipient/purpose, actual/possible extent, owner scope/holds/policy consumption and carryover; unrestricted/no-count dimensions need actual scoped non-applicability |
| C16 Publication/projection | A frozen package/projection/commit or assurance claim is prepared/published | Exact view/dependencies/subject identity, actual allowed serialized membership, external verification/commit receipt, cutoff/claims and missing commit/availability; derived public view need not export full account identity |
| C17 Current pointer | Mutable selection/pointer is requested, changed, observed or claimed | Named purpose/selection, actual owner operation/precondition, current/revision evidence and uncertainty; stronger no-missed-update claim needs actual revision enforcement |
| C18 Availability/retention/cleanup | Retrieval/retention/access changes or cleanup/erasure claims occur | Pinned content versus new locator/availability evidence, ownership/retention rights, actual revoke/delete outcomes and remaining copies/obligations; no silent historical deletion or allowance reset |

Requirements can share one record/reference or physical operation where meanings
match. Combined callback ACK/answer, composite native outputs and joint operations
obey their actual typed cardinalities; no universal one-message/one-row/one-job rule.
Existing S1 single-action grants and guarded handles are not silently widened by this
catalog. A stronger/composite mapping needs its explicit supported contract.

### Phase-dependent knowledge

Before launch, exact recipient/request/permission can be required while the not-yet-
assigned native job ID is unknown. After lost acknowledgement, record the possible
job/charge/exposure and hold actions needing established identity. Before attachment/
cancellation of existing work, adequate target incarnation becomes a prerequisite.
A preservation view may retain unknown restored RNG or pending final bills without
being a failed record. The exact-continuity or settled-total claim remains withheld.

## 5. Support entries are scoped evidence, not one capability ladder (MS05)

Each support entry identifies one exact operation/feature/guarantee in a named scope.
Its logical fields are: contract/revision; supplier/component/role; input/output/route/
subject/effect scope; guarantee and limitations; dependencies/preconditions; declared
mechanism and actual availability; actual authority/validity; relevant scoped test
receipts; native evidence/operating conditions; evidence cutoff/procedure/source.
Shared references are allowed; runtime secrets are not serialized.

Keep these axes separate:

| Axis | Question | Non-inference |
|---|---|---|
| Representation | Can the exact semantics be preserved/interpreted under the named contracts? | No driver, authority or successful native execution follows |
| Mechanism | Is the exact driver/provider/owner/backend implementation supplied? | An advertised callable alone does not prove its behavioral guarantee |
| Readiness | Are actual version/input/environment/dependency conditions established now? | Unavailability here does not erase representability or imply native failure |
| Authority | Do actual relevant owners permit this exact current effect? | Declaration/test pass cannot mint runtime rights |
| Enforcement | Does the real boundary enforce the requested guarantee in this scope? | A cap, path label or local generation number does not prove it |
| Tests | Which exact cases/versions/environments passed, failed, skipped or were not run? | Skips and synthetic fixtures do not become native integration passes |
| Native evidence | Which actual native observations/receipts support this guarantee under what conditions? | One receipt/configuration does not establish universal system support |
| Coverage/limits | What was not examined, is unresolved, unsupported or outside scope? | Not requested and not applicable are different from unknown/unsupported |

Known code can exist while permission is denied; a driver can support launch without
post-crash attachment; an enforcement mechanism can exist while a particular action's
state remains unknown. All axes retain scope/cutoff and source basis. S1 SupportClaim
already separates conditions/native/connection/validation evidence and limits; its
port-declaration check verifies callable names, not every S3 mechanism above.

## 6. Capability catalog and composed requirements (MS06-MS07)

The 20 capability entries in the companion matrix use documentary CAP labels:

| Capability | Guarantee to qualify precisely |
|---|---|
| CAP01 Account preservation | Full-view/projection shape, identity and reference semantics |
| CAP02 Scientific handoff | Exact S2 intent/binding/selection and partial-population handoff |
| CAP03 Realization | Admitted source/transform/fitting procedure and actual evidence |
| CAP04 Presentation | Faithful encoding, permitted recipient view and applicable stable-use boundary |
| CAP05 Effect admission | Actual owner decisions/reservations/validity for the exact operation |
| CAP06 Native invocation | Explicit admitted driver dispatch with boundary/acceptance evidence |
| CAP07 Native identity | Adequate existing episode/incarnation association, distinct from launch identity still unknown |
| CAP08 Native reconciliation | Scoped positive/negative lookup; idempotent retransmission is a separately stated subguarantee, never inferred |
| CAP09 Attachment | Supported connection to established work without hidden launch/reset |
| CAP10 Ownership | Current writer/effect/consumer ownership and actual receiver exclusion where requested |
| CAP11 Capture/replay | Durable permitted capture/frontier and exact source replay/acknowledgement scope |
| CAP12 Interpretation | Explicit decoding/domain/coverage semantics with preserved raw evidence and partialness |
| CAP13 Decision | Supported permitted procedure/input frontier, including unavailable information and fallback rules |
| CAP14 Delivery | Exact action/response/recipient validity and actual transmission/reconciliation evidence |
| CAP15 Restoration | Successor/state/component load and only the continuity scope actually established |
| CAP16 Stopping | Actual cancellation/escalation/observed stop scope, independent from collection closure |
| CAP17 Accounting | Typed owner-scoped metering/revisions/bounds/settlement, not one universal sum |
| CAP18 Exposure | Actual information custody/history/consumption and uncertainty, independent from money |
| CAP19 Publication | Exact commit/projection/dependencies/claim assurance with no implied remote dissemination |
| CAP20 Pointer/retention operations | Explicit optional pointer, relocation/retention/revoke/delete guarantees, evaluated as separate named suboperations |

Catalog rows organize requirements; they do not merge their suboperations or grant
all of them together. For example lookup does not imply resend, observed stop does
not imply cancellation permission, and immutable publication needs no mutable pointer.
The matrix marks all new S3 mechanisms/acceptance/native evidence as unimplemented/
unestablished here, while separately linking narrower existing S1/S2 foundations.

Recommend composable claim requirements, not ranked universal system tiers:

| Claim composition | Required additional predicate |
|---|---|
| Base preservation | M01-M15 and applicable conditional presence/missingness/reference rules |
| Admitted operation(op) | Exact operation's scientific/readiness/authority/resource/exposure/validity/receiver requirements are established |
| Resumed capture(source) | Actual durable evidence/frontier plus the requested replay/retention/ack semantics; no global exactly-once assumption |
| Attachment(episode) | Adequate native identity and current supported ownership/attachment, with no hidden launch |
| Delivery(action) | Exact permitted choice and correlated native delivery evidence; single-effect retransmission needs its own receiver guarantee |
| Restoration(component scope) | Actual available/loaded/evidenced components match that exact required scope; full hidden-state claims are not inherited |
| Hard bound(resource scope) | Actual owner capacity/enforcement covers every effect in the stated bound; estimates remain distinct |
| Audience publication(view, claims) | Actual permitted serialized closure, exact commit/dependency pins and adequate evidence for each requested check |
| Scientific handoff(scope) | Exact S2 intent, actual attempts/evidence/missingness/selection and cutoff preserved; eligible final response is an additional S2-specific question |

Preservation/handoff can succeed while a requested next operation or final-response
claim remains withheld. Causal correctness is not a conclusion of these S3 compositions.
Named implementation profiles and their precise versioned mapping remain later work;
none of these labels is a newly adopted public protocol or current S1 profile name.

## 7. Applying the minimum to the four prior traces (MS08-MS09)

The overlay pins the previous example bytes and references their existing IDs.
Every M obligation maps to those facts or an explicitly proposed annotation; no
retroactive native receipt is invented. These annotations supply view role/identity,
recorder context, declared audience, exact documentary frontier and index extent,
requirement coverage and the collection-period description omitted in the sketch.

Use one account collection period per main example, with actual source subscopes.
R's earlier P1/P2 and K's earlier P1/P2 are interim publications, not inferred
collection closures. K's new native episode has its own source identity; no old
cursor is reused. If a period actually closes and active observation later resumes,
the earlier EA rule still requires a new linked collection period. Native stop or
publication alone never supplies that closure fact.

| Case | Universal minimum | Conditional requirements exposed | Claims supported only in the hypothetical story | Withheld/not requested |
|---|---|---|---|---|
| L local | Six blocks plus explicit proposed header/frontier/period annotations | Prospective realization before final binding, trusted argument presentation, ordering interpretation, scoped job settlement and actual private/public projection | One local invocation and requested ordering fulfillment; scoped 0.7/1 job units; admitted public summary with weaker assurance | No provider ID/post-crash lookup, no OS-wide isolation, no public raw-map verification or causal correctness |
| R remote | Same minimum; P1 unknowns preserved at its earlier frontier | Current owner/context, native lookup/attachment, source window after16, event associations, durable capture18, scoped charge4/10 | One native invocation/attempt, two native events from three captures, reconnect to existing N42, native graph fulfillment | No automatic resend invoked, no claim full earlier event history, no mutable pointer; P1 acceptance/cost/stop stay unknown |
| I interactive | Minimum remains preservable at bounded close | Exact Q1/Q2 contexts, fixed V1 basis and uncertain/reconciled delivery, actual exposure policy, missing Q2 source and pending native stop | Q1 delivery and one policy unit consumed, not native use; actual partial output retained | Q2 selection/delivery held with no fallback; final fulfillment/native termination unestablished, no silent abstention, no all-resource monetary total |
| K checkpoint | Same minimum; source/attempt scopes remain explicit | Declared partial recovery, predecessor stop, successor/load, retained G1, first eligible G2 and revised bills5+4 | Two attempts under one trial, evidenced model/optimizer continuity, scoped 9/20 job units after settlement | Full RNG/history continuity, second independent scientific repetition, best-score selection and causal correctness not claimed |

The examples are compatible with the proposed minimum once those explicit metadata
annotations are supplied; they are not already wire-conformant S3 records. All four
leave causal correctness unassessed. I's pending Q2 is a dependency/evidence gap,
not proof that the decision-provider mechanism cannot exist or that the record is
malformed. K's unknown full state does not invalidate the narrower recovery mode
the fixed condition explicitly permits.

## 8. Boundary checks and counterexamples (MS10-MS11)

- Bootstrap with no effects: minimum indexes can be locally empty; no fake R/A/N,
  reservation, cursor or scientific repetition is required.
- Failed/unknown native submission: preserve the actual command/attempt and scoped
  pending effects. Native-ID-unknown is expected before an assigned receipt; it is
  insufficient for later identity-dependent control without reconciliation.
- Unauthorized historical delivery: preserve the source/actual deviation and unknown
  original authority. Valid preservation is not permission to repeat it.
- Unknown-origin external job: exact native observation target may exist without
  original A/T; no fake origin is added. Its stronger S1 mapping/driver remains required.
- Two unexpected jobs: C05 retains both and their known associations. S1 guards stay
  intact; prospective attempt count is not actual native episode or scientific count.
- Dynamic/federated input: C02/C03/C07/C08 bind actual episode/window/partition/custody;
  private raw copies and one CSV are not universal minimum requirements. These four
  traces do not establish such native support; additional profiles/tests are needed.
- Combined/batched native operation: logical actions and quantities keep exact scope
  even if one physical request serves several roles. Current single-action S1 APIs
  are not silently declared to support atomic native batch delivery.
- Public summary: uses projection requirements, not false six-block completeness;
  lineage stays privately traceable where it cannot be exported.
- Current pointer: C17 is not triggered by the four main cases. If requested later,
  value-based CAS and stronger revision-based guarantees retain their actual limits.
- Stronger request on weak backend: preserve the evidence and deny/hold only the
  dependent operation/claim; do not relabel the scientific condition or claim every
  dimension unknown merely because one guarantee is unavailable.

## 9. Decisions, alternatives and remaining precision

| ID | Recommended direction | Strongest alternative | Cost / failure prevented |
|---|---|---|---|
| MS01 | Separate preservable account, admitted effect and supported claim/projection | One valid/ready/success flag | More explicit judgments; prevents metadata becoming permission or native success |
| MS02 | Fifteen shared semantic obligations inside six blocks, conditional empty indices | Require every native/distributed field in every record | Some scoped descriptors; prevents fabricated IDs and heavyweight local minimum |
| MS03 | Triggered families with explicit missingness and applicability coverage | Optional fields omitted without explanation | More requirement evidence; prevents unknown becoming non-applicable |
| MS04 | Knowledge requirements depend on phase/operation | Demand native job ID before launch or permit control with a bare ID | More conditions; prevents circular startup and wrong-target effects |
| MS05 | Orthogonal support axes and exact claim scope | A single support score/tier from declared ports | More evidence links; prevents schema/callable/test/native guarantee conflation |
| MS06 | Composed exact capability guarantees and claim predicates | System-name profiles or one all-live tier | More granular profiles; preserves genericism and truthful partial support |
| MS07 | Actual admission predicates for each effect/strong claim | Implement admission policy independently in each driver | Shared owner/backend contracts; prevents diverging policy, unsafe retries and hidden exposure |
| MS08 | Pin old examples; add explicit documentary metadata overlay | Publish a new complete replacement edition of the examples | Extra versioned artifact; makes added assumptions distinguishable from original story evidence |
| MS09 | I partial closure and K scoped continuity remain valid preservation | Require complete final execution/full state for any valid account | Withheld claims; prevents fabricated answers or exclusion of difficult trials |
| MS10 | Explicit bootstrap/projection/historical cases and no universal one-to-one counts | Force every example into prospective one-job one-result shape | Conditional roles; prevents false launch/repetition history |
| MS11 | Dynamic/multi-party/composite/unknown-origin support is conditional and separately evidenced | Restrict the initial contract to the four simpler execution paths | Additional profiles/tests; avoids baking current examples into universal limitations |
| MS12 | Documentary requirement checks distinct from implementation acceptance | One combined validation report with explicit documentary/runtime sections | Separate scoped receipts; reduces the chance that fictional capabilities become implemented guarantees |

Review MS recommendations before selecting exact wire names/enums or versions.
Remaining precision: minimum/conditional field encodings and closed catalogs;
phase-specific reference/cardinality constraints; native identity/S1 projection;
owner/journal/driver/decision signatures; actual storage/capture/ack atomicity;
evidence/projection/claim validators; support profile versioning and conformance cases.
No S3 source or existing S1/S2 semantics are changed in this milestone.

The reference overlay also makes family boundaries explicit: a pre-existing oracle
evidence source is governed by C10/C15, with C02 separately triggered only if an
actual source-generation/realization procedure is intended, attempted or reported.
Native internal model computation alone is not an auditor input-realization command.
All four cases preserve basic artifact availability; none requests deletion or a
mutable pointer. Those optional suboperations are not inferred from publication.

## 10. Documentary validation and actual checks (MS12)

The external documentary consistency check passed: 60 minimum obligation bindings
(15 per case), 72 conditional coverage entries (18 per case), 80 capability-demand
entries (20 per case), eight support axes and nine claim compositions. It checked
source/annotation references, the exact unchanged prior-example digest and 117
source entities, explicit proposed annotations, I's held Q2 and K's withheld
full-state claim, optional pointers not requested and the projection excluded from
false full-account validation. The 25 existing source, ten test-file and one fixture
anchor hashes stayed unchanged; named existing test methods resolve in their source
trees. All story evidence remains hypothetical; this is not an S3 runtime validator.

Existing source/tests provide narrower S1/S2 preservation, exact registry lookup,
port/capability declarations, scoped assessment, handoff and native fixture behavior.
Actual S3 mechanisms, acceptance and native evidence for these new guarantees remain
unimplemented/unestablished. Offline package gates do not turn matrix assumptions
or skipped dependency/data tests into native integration proof. No historical
scientific rerun/certificate, threshold, score, paper or production policy changes.

## Where we're going

Review the minimum/conditional distinction and scoped support/claim matrix. Then
perform bounded serialization with exact field/reference/catalog constraints, followed
by journal/owner/driver/decision interaction and recovery signatures and explicit
S1/S2 compatibility mappings. Recheck complete records and failure boundaries before
final S3 design review and implementation DAG/bundles. Implementation still requires
explicit authorization.
