# S3 operation, interface and package-review closure candidate

Tickets: DLV-08, DLV-09; related DLV-10. Date: 2026-11-03, America/Los_Angeles.
Status: OC01-OC16 recommendations pending review. Design/data only; no S3 runtime,
schema, driver, native execution, paid API, public protocol adoption or build approval.

## 1. Continuation and scope

The user affirmed the [bounded serialization direction](subsystem3-bounded-serialization-candidate-2026-11-03.md)
at 9983e790b42133e554370eba0ee967f6d763b5f9, requesting closure of operations,
signatures, recovery and S1/S2 mappings, followed by complete-package review before
final S3 design review/DAG. BS01-BS12 become direction-affirmed/details-open in the
methodology index; no blanket approval of new OC details is inferred.

The [operation catalog](subsystem3-operation-contract-catalog-2026-11-03.json)
defines exact common role/parameter/signature forms. It proposes S3 revision
0.1.0-proposal.2, preserving revision1 artifacts/hashes. S1 and S2 retain their exact
existing revision1 formats. A candidate catalog is declarative data, not installed
code. General native payloads select explicit versioned driver grammars rather than
arbitrary metadata or automatic imports. Third-party drivers can implement additional
registered operation contracts with the same core admission/history requirements.

The [complete preservation-package review archive](subsystem3-complete-package-review-2026-11-03.json)
contains exact authored package bytes/pins, not partial reference stubs. Its S1/S2
companions preserve supplied fictional case evidence/intent. The original stories
never supplied actual run-binding snapshots, so those identities stay unresolved.
Complete preservation is not complete scientific eligibility, prospective temporal
admission, real owner authorization or native integration. No ready run binding,
positive grant or native occurrence is invented to turn that limit green.

These are new retrospective commissions with their own account IDs, not invented
UUIDs for the original symbolic E/A/T labels. Original labels/relationships and
reported outcomes remain in the pinned source artifacts. Actual metadata authoring
timestamps are recorded separately from unresolved historical/native clocks.

## 2. Operation bindings, role types and grammar closure (OC01-OC03)

OperationBinding = {operation:Contract, roles:RoleBinding[],
parameters:OperationParameter[]}; OperationParameter = {key:String,value:K(T)}.
Every declared role/key occurs exactly once; no extras/defaults. Role member indexes
retain scope/extent/gaps. The catalog has 31 exact operation entries, 77 family-role
positions across C01-C18, their target unions, and 19 shared payload grammars.

Role arrays permit missingness for preservation; positive effect-required counts
and established identities are admission predicates. An unknown S2 run binding can
be represented but cannot satisfy launch's exactly-one scientific-binding condition.
Unrecognized target types or raw parameter dictionaries cannot pass by omission.

| Operation group | Positive role/cardinality requirements before the effect |
|---|---|
| Realize/stage | One explicit provider/specification or recipient, one-or-more actual sources/presentations, exact output/transfer/window/state contracts |
| Launch | One request, attempt and S1 binding; exactly one S2 run binding for a scientific run; exact permitted presentations (possibly zero), prepared invocation and applicable owner commitments |
| Lookup/attach | Lookup binds one original command/query; attach binds one adequate subject/association/current ownership context; no substitute launch |
| Observe/ACK | One source/period, positive batch limits and deadline; ACK additionally needs the matching committed capture receipt and source position |
| Information/response computation | Explicit source/input, recipient/provider, information policy, expected response and spend/exposure commitments |
| Deliver/reconcile | One decision/endpoint and nonempty exact action/response correlation; lookup binds original delivery; the selected bundle contract controls multiplicity |
| Stop/restart/restore | One supported target and policy; restart has distinct predecessor/successor attempts plus exact request/state/overlap conditions; restore names its supported in-place scope |
| Owner operations | One actual owner and operation binding; original stable correlation; revision, quantities/evidence/validity specific to reserve/reconcile/renew/settle/release/authorize |
| Publish/pointer | One view/audience and exact bytes/digest; pointer additionally needs committed selection and actual expected revision |
| Retrieval/revoke/delete | Exact artifact/copy/access-owner/retention scope and actual capabilities; no global deletion inference |
| Pure compile/decode/decide | Supplied pinned inputs and exact installed procedures; no native effects/fetches concealed |
| Close collection | Exact period/frontier/stopping rule and retained obligations; no implicit stop or release |

Grammar rules are deliberately split between common policy and native mechanics:

- Function invocation names an installed callable binding and typed arguments;
  the driver supplies the callable. No eval, arbitrary entrypoint import or probe.
- Process invocation is executable/argv/cwd/environment-policy/secret-slot data with
  shell=false. Service invocation is endpoint plus typed request and secret slots.
- A native parameter payload has an exact declared contract, pure decoder and
  input/output scope. Core has to understand its required effects/information and
  guarantees; it need not hard-code every service-specific field.
- Secret slots name owner-held runtime inputs. No bearer/secret value is serialized;
  absent secret-version evidence limits claims of identical inputs/reproducibility.
- Idempotency includes actual owner/key/binding/scope/retention/validity/guarantee
  evidence. A request hash or local correlation is not provider idempotency.
- Query, subscription, bundle, amount, validity, collection-bound, pointer and
  audience-closure grammars are closed/versioned in the catalog. Numbers remain
  tagged exact decimals. Ranges, clocks, units and finite/nonnegative limits are
  validated within their actual contracts; unknown is not a useful numeric default.

### Explicit payload reference context

Revision2 adds typed_payload.reference_context={package_id:ID,format:Contract} and
uses operation_binding for effect_command.binding. Embedded parameter references
resolve in that declared context, never in the S1 artifact's storage package or the
newest account view. A copied typed payload keeps its original context and dependency
pin. If rebinding is needed, create a derived record with a new ID and bridge receipt.
This prevents equal captured bytes from silently acquiring different referents.

## 3. Return contracts and exact interfaces (OC04-OC06)

Every proposed method and argument/result type is enumerated in catalog.ports and
runtime_values. These are signatures for later implementation, not Python classes
created in this milestone. Opaque runtime objects require their actual owner and
cannot be reconstructed from JSON. Native-specific parameter/results have exact
contracts supplied by the selected driver declaration.

CallResult[T] = {state:completed|partial|rejected, value:T or runtime None,
records:RecordDelta, issues:Issue[], effects:EffectBoundary[]}.

Each EffectBoundary binds a command and distinguishes not_crossed,
may_have_crossed, crossed or not_applicable, with acceptance:K(Boolean) and evidence.
It also identifies the forwarding occurrence D where established. Logical C can
have several explicitly admitted D occurrences; a new runtime ownership epoch does
not silently mutate C's content or renew provider idempotency retention. An issue
intent's transaction identity equals its allocated D identity. Journal transaction
lookup reconciles that original identity before another forwarding is considered.
Crossing a client boundary does not establish provider acceptance or completion.
No return object after a crash means uncertainty is reconstructed from the journal,
not guessed as not_crossed. Rejected may retain useful evidence/possible effects;
partial requires useful value and gaps; completed describes the method, not native
success. Pure validation rejection has no native effect but can still have a local
diagnostic/recording cost. Each potentially effectful suboperation has its own entry.

Runtime RecordDelta partitions S3 records, owned S1 native additions and owned S2
scientific additions. They never enter one serialized records array. Freeze each
owned addition under its own exact namespace/context before constructing CommitDelta
(S3 records plus immutable dependency views). Journal.append and commit_capture take
CommitDelta; partial mutable S1/S2 staging cannot become a durable capture frontier.

**S1 Op and S2 PlanOp are not interchangeable.** S1 invoke can return rejected after
the executor or acknowledgement failed, with captured evidence and no NativeHandle.
Map that to possible effects unless adequately proved otherwise. S2 rejected PlanOp
is atomic for its metadata transaction; that property does not extend to provider
launches, owner calls, uploads or native S3 orchestration.

| Port | Exact main call forms | Responsibility and boundary |
|---|---|---|
| Coordinator | open(commission,context); plan(view,request,context); compile(run,occurrence,context); admit(prepared,expected_head,context); issue(admission,context); recover(view,goal,context); freeze(view,audience,claims,context) | plan/recover/freeze use supplied data and propose work. admit acquires/reconciles actual owners. issue commits intent and performs one authorized forwarding. No convenience retry loop. |
| Owner | inspect(binding,context); reserve/reconcile/renew/settle/release/authorize(request,context); check(grant,binding,boundary,context) | Stable exact correlation, owner revisions, actual holds/validity and live capability. Bootstrap control capability is externally supplied, not minted by admission. |
| Driver | describe(context); prepare(binding,inputs,context); realize/stage/invoke/lookup/attach/observe/ack/acquire/compute/deliver/lookup_delivery/stop/restore/read(request,context,grants,issue_token,sink); decode(request,context) | Mechanisms only. describe/prepare/decode are pure over supplied data. Every other boundary has actual grants and an issue token; no implicit launch/fallback/replay. |
| Decision | describe(context); requirements(actions,policy,context); select(actions,policy,inputs,frontier,context) | Pure bounded information requirements/selection. External oracle/LLM/tools are explicit acquire/compute operations before selection. |
| Journal | head(account,context); append(account,expected_revision,transaction,delta,context); prepare_issue(command,transmission,expected_head,grant_bindings,context); lookup_transaction(account,transaction,expected_binding,context); commit_capture(source,expected_revision,batch_occurrence,bytes,delta,next_cursor,context); snapshot(account,revision,context) | Durable history/CAS, exact snapshots and atomic capture/frontier relation within stated fault model. No provider-side atomicity inferred. |
| Storage | publish(publication_id,bytes,expected_id,expected_digest,audience,grants,issue_token,context); lookup_commit(...); cas_pointer(...); locate(...); revoke(...); delete(...) | Actual byte/commit/audience/copy-owner guarantees. Optional pointer/cleanup never follows implicitly from publish. |

Pure means no external/native I/O and no hidden clock/dependency probe, provider
call or installation. Bounded CPU and local control bookkeeping still belong to the
commission's resource context. Read contexts contain supplied pinned views; retrieval
is explicit when absent. Remote owner introspection/reservation itself needs the
already supplied control capability/allowance. There is no recursive self-grant or
unfunded emergency/control bypass.

The exact catalog additionally supplies Journal.lookup_transaction(account,
transaction,expected_binding,context), the transmission argument to prepare_issue,
and Clock.now(context). Owner correlation names the stable reservation/subject
binding; request_occurrence names a single immutable owner request. A renewal or
settlement is a new request occurrence under the same subject, with expected owner
revision. Lost-ACK reconciliation targets the original request occurrence; it never
silently issues a second reservation/renewal. Reusing a request ID with changed
parameters is a conflict.

## 4. Admission, concurrency and recovery guarantees (OC07-OC10)

An executable LiveAdmission requires exact preparation, supported operation/grammar,
scientific conditions where applicable, adequate inputs/identity, actual owner grants,
resource/exposure reservations, current validity/ownership and all requested backend
guarantees. Journal expected-head checks prevent stale local decisions. Native
exclusion/idempotency still require actual receiving-boundary enforcement.

Launch/restart's scientific binding is conditional: scientific intent/run purpose
requires exactly one established matching S2 run binding. A fixed, explicitly
non-scientific preparation/probe commission can justify NA under its exact rule;
it still records actual work, costs, disclosure and later S2 contamination/history.
Relabeling purpose after results cannot bypass visible C01 requirements. A known
native predecessor with unknown original A/R can use an explicitly supported S3
one-parent restart route, with original identities unresolved and actual state/stop/
ownership requirements met. It cannot claim an S1 recovery projection without real
S1 predecessor/successor identities. Multi-parent continuation needs its own typed
operation profile; this one-parent row is not a universal native limitation.

For example, owner key H7 identifies one reservation for effect binding B. Reserve
request R1 can time out after the owner committed it. Query Q1 reconciles H7/R1;
if it establishes the existing hold, a current owner may issue a new live grant.
Renewal R2 changes validity under the same H7/B and expected owner revision. If
R2's reply is lost, query R2 rather than reserving again. Native command C1 has
its own forwarding D1 and provider lookup/idempotency contract: deduplicating H7/R1
does not deduplicate C1/D1 at the provider.

| Boundary/failure | Required recovery and retained evidence |
|---|---|
| Partial multi-owner reserve | Journal each owner/key before call; reconcile unknown replies. No execute until all required commitments established. Release only known owner-permitted surplus; compensation is not global rollback. |
| Lost reserve/renew ACK | Reconcile same key/exact binding; no replacement key or assumed failure/release. Actual expiry rules come from owner. |
| Intent committed, launch ACK lost | Keep original command/attempt and possible job/cost/exposure. Lookup under admitted control bounds. No request-hash resend. |
| Owner/coordinator takeover | New journal epoch can reject stale writes; establish current owner/receiver fences and reconcile accepted/in-flight work separately. Lease expiry is not native termination. |
| Connection lost, identity established | Attach to existing incarnation under current rights; same native attempt. Unsupported attachment yields a gap, never launch fallback. |
| Observation/capture interrupted | Reconcile capture transaction/occurrence. Advance durable cursor only with committed bytes/metadata. Re-fetch under source contract may create another capture, not a new native event. |
| Native ACK before durable capture | Only permissible under an explicit combined-consuming protocol and accepted loss/retention guarantee. Cannot claim source-safe replay by ordinary separate-ACK profile. |
| Delivery ACK lost | Preserve selected response/action/content. Lookup original receipt; retransmit only under unexpired actual receiver single-effect contract and current admission. Delivery is not use. |
| Ended/native restart | Distinct successor attempt and explicit compatible request/recovery relation; required nonoverlap/stop scope established before launch. Unknown possible predecessor effects hold strict nonoverlap. |
| Checkpoint partial state | Before launch, permitted mode and required available state/enforcement established; after launch, record actual loading. Unknown RNG does not become loaded or prohibit an expressly allowed narrower model/optimizer mode. |
| Stop requested/ACK received | Observe actual scoped stop before claiming termination; retain possible descendants/usage. Escalation requires its own current rights. |
| Settling/releasing | Use exact owner/resource/unit/member/interval/revision rule. Final A1 bill5 replaces interim3; adding A2 bill4 gives9. Unknown native use/charge remains a liability, not zero. |
| Publish commit ACK lost | Lookup same publication ID/package/digest. Do not refreeze into a new identity to resolve the old commit. |
| Pointer race | Expected revision CAS at actual owner; reject/review conflict. Value-only CAS cannot satisfy no-missed-update after A→B→A. |
| Collection deadline | Close immutable bounded view with pending effects. Active resumed observation has a new linked period. Late import does not mutate old cutoff. |

Every guarantee names fault domain (for example process crash versus host/power loss),
linearization point, durability/retention, ownership scope and tests/native evidence.
No S3 backend is implemented here. A local JSON lock/generation, fsync or rename
alone is not a blanket distributed/power-loss guarantee. An unavailable strict
guarantee holds the dependent operation/profile; preservation remains possible.

## 5. Explicit S1/S2 bridge (OC11-OC13)

| Meaning | Existing foundation and exact mapping | Preserved limitation |
|---|---|---|
| Scientific intent/binding | S2 run_binding and exact source snapshots; core.bind_run/project_request/record_handoff through existing completion/projection registries | Metadata compilation is not launch/admission or scientific correctness; missing binding stays unresolved |
| R before O | handoff.freeze_s1 freezes request R; later observation O gets distinct snapshot identity, unchanged copied records/context | Calling frozen() again is not retrying identical publication bytes |
| Presentation/materialization | S2 record_materialization records supplied outputs/checks; S3 realize/stage executes admitted mechanics, then returns actual evidence | S1 prepare and S2 metadata writer must not execute transforms or disclose hidden evaluator content |
| Invocation | S3 prepared native call maps to S1 InvocationSpec; S1 ExecutionContext/ExecutionGrant scoped to actual request/attempt/presentations/effects | Supplied driver/RuntimeAuthority required. One-shot token consumption and rejected return do not establish no native effects |
| Native identity | Preserve raw S3 authority/namespace/id/incarnation descriptor and adequacy evidence; use literal-unique or explicit incarnation-key bridge below | No bare ID sufficiency, old-handle resurrection, fake origin attempt or bypass of HandleRegistry |
| Attachment/observation | Actual fresh runtime context and supported driver establish handle; S1 attached_connection only observes caller-established handle | S1 observe does not itself enforce every new S3 owner/cost/fence rule; S3 must establish those boundaries |
| Decisions/delivery | Exact one-action response uses S1 action_request/action_response and DeliveryGrant; S3 DecisionResult/frontier precedes send | Composite operation cannot be decomposed into separate S1 deliveries while claiming original atomicity; use explicit supported S3 bundle driver or hold |
| Stop | S1 CancellationContext/Receipt under actual owner; distinguish ACK and observed stop | Existing S1 target limitations remain. Unknown-origin native jobs require explicit S3 driver support, no invented A |
| Recovery/load | New attempt and S1 recovery/state_load evidence; S3 policy/ownership/capture continuation independently scoped | Exact continuity requires actual required components; observer reconnection is not checkpoint restart |
| Artifacts/output | S1 snapshots/declarations/selectors/domain/mapping/native-report or interpreted outputs; S3 only links/assesses under exact decoder | Unknown contract/partial bytes remain preserved; native absence/causal truth not inferred |
| Accounting/exposure | S3 owner/revision ledger may project supplied quantities to S1 output/accounting and links to S2 exposure receipts | Do not feed overlapping inclusive/replacement totals as independent disjoint inputs or reset policy at restart |
| Publication | Existing PackageStore/experiment writer own S1/S2 formats; S3 storage boundary is a new explicit service using exact bytes/pins | Existing value-based select_current is not revision CAS; no silent format widening or universal power-loss claim |

### Runtime reference qualification

Before invoking S1, the bridge verifies the exact R snapshot/type/content closure
and uses the existing S2 compiler/import mapping where applicable. S1 working-local
references are permitted only in that explicitly established working scope. A bridge
receipt pins (source package,record ID,type) to the working record; copied record
contents/identity stay unchanged. Required imports that rewrite references create
derived records with new identity and loss/context receipts. Never strip package_id
or use RecordBuffer.get's target lookup as proof of qualified external resolution.
Conflicting same-ID dependencies fail bridge admission; no latest-wins merge.

### Native incarnation mapping

Literal-unique route uses the actual S1 authority/namespace/native_id only when the
declared source scope guarantees it uniquely identifies the required incarnation.
Otherwise an explicitly supported bridge can encode the raw tuple
[authority,namespace,native_id,incarnation] as compact UTF-8 JSON, then strict base64
with a fixed `s3-incarnation-key-v1:` prefix in the derived S1 native_id. Its source
is derived, its bridge receipt retains the raw descriptor/procedure, and the driver
uses raw native coordinates for provider calls. This is an explicit registry key,
not a claimed literal provider ID, cryptographic guarantee or native dedup key.
No unestablished incarnation is encoded as a convenient empty string. A legacy
driver that expects literal native_id needs the literal-unique route or an explicit
bridge-aware driver. Unsupported mapping holds control; raw observations remain.

S1 RuntimeAuthority and HandleRegistry are process-local supplied boundaries, not
distributed hostile-worker isolation. Recreating a context does not fence the old
worker. S3 adds actual ownership/receiver requirements; it does not mutate S1 guards.

## 6. Complete package review and concrete cases (OC14-OC15)

The archive embeds exact UTF-8 bytes/digests of complete S1 evidence packages, S2
case-intent packages and before/final S3 preservation views. External package IDs,
formats, record types, byte pins, typed-payload contexts and all known reference
targets are supplied; unresolved references explicitly omit target IDs. No ambient
fixture stubs or runtime credentials. The authoring tool stays outside the repo;
these are immutable synthetic design data, not new runtime implementation/tests.

The S2 companions preserve archival case/domain/evidence; S3's pinned source retains
the reported task/response intent. They do not fabricate original task/response
contracts, plan/run-binding/commitment receipts or unreported abstention defaults.
C01 includes a diagnostic/unresolved identity for that scientific gap.
Thus these packages can support preservation/closure review, not prospective
launch eligibility for a new campaign. This is an intentional historical-import
boundary, not an assertion that the fictional histories were newly authorized.

| Case | Package/contract review |
|---|---|
| L local | Preserve original CSV/permutation/output evidence, trusted argument scope and reported0.7 job units. One-shot progress uses scoped NA. Public output remains exactly its two permitted native entities; all added S3 metadata/lineage is private. No new public S3 root is smuggled into that policy. |
| R remote | Before view preserves lost ACK; final view references later lookup/association and three captures/two native events. Exact earlier view bytes/pin remain. Late receipt is excluded from early decision basis. Reconnect keeps A; no resubmit/cost-zero inference. |
| I interactive | Pre-send Q1 information frontier excludes later receipt. Q2 has distinct action/source context, no selected response and no delivery. Delivered/policy-consumed does not establish use/termination; obligations survive closure. |
| K restart | One scientific intent/two attempt identities, G1 retained, permitted partial model/optimizer state versus unknown RNG/history, predecessor stop before successor launch as an authored trace condition, final9 after replacement. No new independent repetition or exact-state claim. |

Temporal review uses authored local evidence/decision/effect ordering and explicit
basis membership, not fabricated UTC/native clocks. It checks a prospective rule's
necessary nonfuture-basis condition in the hypothetical trace. Equal source step
labels alone do not establish within-step precedence; an actual issue needs its
exact frontier/receiver evidence. The review does not certify native receipt
truth or run a coordinator. Extra negative scenarios deliberately introduce a late
basis, altered dependency pin, ambiguous lookup, stale writer, zero-action delivery,
wrong restart identity or private-public metadata crossing. These specify intended
rejection/withholding at exact boundaries. A scoped preservation account can retain
the underlying nonconforming observation while refusing the stronger claim/effect.

### Projection and dependency cycle boundaries

Actual audience closure includes producer, metadata, diagnostics, aliases, embedded
typed payloads, external descriptors, locators and byte pins, not just root fields.
A full private account may reference restricted bytes with explicit availability
limits. Public proof cannot depend on private IDs it is not permitted to export.
Where public metadata is allowed, author new public statements/frontier/basis with
weaker assurance as necessary; private derivation receipts remain private. L's
unchanged policy allows only the original two-entity native public artifact.

S3 package pins S1/S2 artifacts; S1-hosted typed payload bytes may contain refs whose
explicit S3 context is the consuming S3 package. That is not an S1 external-descriptor
cycle: reference interpretation belongs to the declared S3 payload context, and the
source bytes/host package stay independently pinned. No package embeds its own
whole-byte digest. Publication/verification receipt lives outside its hashed subject,
and later receipts cannot be inserted into the earlier view's admitted basis.

## 7. Decisions, alternatives and validation limits (OC16)

| ID | Recommended direction | Strongest alternative | Cost / failure prevented |
|---|---|---|---|
| OC01 | Closed typed operation rows and phase-specific admission counts | One permissive execute request with driver validation | Catalog/registration effort; common policy cannot disappear into adapters |
| OC02 | Explicit parameter/context grammars and revision2 | Keep artifact-host-relative interpretation | More context pins; prevents silent reference rebinding |
| OC03 | Separate pure selection from information/model effects | Let decision providers acquire inputs internally | More explicit operations; prevents hidden spend/evaluator disclosure |
| OC04 | CallResult plus per-command boundary/acceptance evidence | Reuse S2 atomic rejection everywhere | More result dimensions; preserves launch/charge uncertainty after failures |
| OC05 | Typed coordinator/owner/driver/decision/journal/storage ports | A single orchestrator object with backend-specific branches | More interfaces; thin adapters and testable common ownership rules |
| OC06 | Runtime-only grants and explicit control bootstrap | Deserialize or infer grants from permission records | Owner integration; prevents self-grants and recursive admission fiction |
| OC07 | Per-owner correlation/revision plus conservative partial admission | A distributed transaction across all owners | Longer holds/reconciliation; works with heterogeneous owners without claiming global rollback |
| OC08 | Journal intent/capture barriers plus actual receiver guarantees | Treat local durable intent as exactly-once launch | Backend qualification; prevents duplicate effects/lost evidence claims |
| OC09 | Explicit recovery kinds and state/overlap scope | Uniform retry/restart command | More state distinctions; prevents attempt/trial inflation and unsafe overlap |
| OC10 | Independent stop, settlement, closure and projection guarantees | One final-success/closed flag | Retained obligations; preserves bounded observation and later evidence |
| OC11 | Explicit exact S1/S2 projection/working context | Strip qualification and reuse matching IDs | Bridge receipts; prevents cross-package substitution |
| OC12 | Literal-unique or explicit lossless incarnation-key bridge | Assume provider IDs never repeat | Driver capability checks; preserves actual incarnation without changing S1 schema |
| OC13 | Mark S1 single-action/value-CAS/process-local limits | Present all S3 guarantees as already supplied by S1 ports | Additional S3 mechanisms; avoids unsupported native coverage |
| OC14 | Complete preservation packages with honest scientific gaps | Invent missing ready S2 bindings for positive examples | Withheld eligibility; avoids manufacturing history/authority |
| OC15 | Exact dependency/cutoff/audience review and separate native public payload | One uniform public package format | Extra publication representations; preserves original disclosure policy |
| OC16 | Documentary closure/pin checks and existing package gates separately | Count authored receipts as executed S3 acceptance | Scoped evidence account; prevents synthetic/native conflation |

Existing offline package tests and source inspection support only their scoped
implemented primitives. Native/backend guarantees and these proposed S3 mechanisms
remain unbuilt. Complete byte/reference closure is not a claim of complete scientific
coverage. No original result, certificate, threshold, policy, paper or historical
hash is updated. Current design recommendations require review before freeze.

Documentary checks passed for 31 operations, 48 signatures, 77 family-role positions,
19 shared grammars and 28 complete authored packages: 16 S1, four S2, eight S3
before/final preservation views. There are 4,553 known reference occurrences, 36
embedded payload-reference occurrences and 40 pinned external descriptor edges;
all known targets resolve, global record identities agree and descriptor graphs
are acyclic. The existing S1/S2 parser/resolver checked all 20 companion closures.
Twenty-four internal payload references fail resolution under the wrong artifact
host context, as expected, and a changed byte fails its stored pin. Four authored
incarnation tuples round-trip under the proposed lossless encoding. These are
documentary checks, not a new S3 parser or native identity/control test.

Six existing S2/S1 metadata handoff tests passed without skips: native-field-only
projection, missing-support rejection without invocation, same-occurrence idempotency,
immutable distinct R/O snapshots, exact handoff pins, changed-binding occurrence
rejection. Source-linked methods/limits are in the methodology index. Sixteen
additional S3 negative scenarios remain documented acceptance expectations, not
executed S3 validator tests. The original trace, overlay and serialization hashes
remain unchanged; new revision2 files have separately pinned identities.

## Where we're going

Review OC01-OC16 and the complete preservation/negative package review. Adjudicate
any remaining design objection, then conduct S3's final design review against the
accepted S1/S2 foundations and versioned methodology/support account. Only after
that review define the detailed implementation DAG/bundles, each with fault-model,
native/support limitations and concrete acceptance gates. Implementation still
requires explicit authorization; no backend capability is silently assumed.
