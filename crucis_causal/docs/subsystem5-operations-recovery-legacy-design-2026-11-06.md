# S5 operations, recovery and legacy mapping

DLV-08, DLV-09, DLV-10. 6 November 2026. Candidate service contract
following the [wire review](subsystem5-cardinality-wire-design-2026-11-06.md).
The signatures specify effect and evidence boundaries for review.
The examples are hypothetical except where marked historical.

## Operation signatures

Each operation returns a typed disposition or value with scoped issues.
Read and preparation operations take caller-supplied bytes or immutable
values. Stored lookup and mutations use explicit effect ports.

| Candidate signature | Contract |
|---|---|
| inspect(bytes, limits) -> DecodedSnapshot or WireIssues | Check bounded exact bytes, known versions and local shapes. Preserve the received-byte identity. Pure. |
| resolve(snapshot, supplied_views, read_capability, limits) -> ResolvedView or ResolutionIssues | Bind authorized pins and typed references. Surface unavailability, denied scope and conflicts. No ambient fetch. |
| prepare(request_ref, resolved_view, rule_registry, limits) -> PreparedAssessment or Hold | Select one question, rule, evidence view and bounded clause graph. Resolve typed evidence and candidate prerequisites. Freeze the basis, procedure and limits. Preparation may establish a scoped hold. It grants no authority and makes no finding decision. |
| evaluate(prepared_assessment, exact_evaluator, limits) -> DecisionDraft or EvaluationIssues | Evaluate the bounded predicate and return the clause trace. Use only supplied immutable values. Pure calculation; its returned draft is distinct from durable work evidence. |
| execute(prepared_assessment, invocation_id, evaluation_context) -> ObservedAssessmentWork or WorkDisposition | The coordinator verifies the prepared identity and applicable admission, records intent and entry through S3, and invokes the selected evaluator. The observed report names the actual occurrence, basis and outcome. |
| assess_registration(target, policy, resolved_view, read_context) -> RegistrationDraft or RegistrationIssues | Assess exact commitment, exposure and conformance at a supplied cutoff. Produces an independently scoped proposed determination. A pinned decision may be reused in a later assessment with a new registration basis. |
| prepare_history(request, resolved_view, history_policy, read_context) -> HistoryDraft or HistoryIssues | Select exact target assessments and verify relationship, affected scope, authority and deciding evidence where required. Produces a proposed link, including an open dispute or scoped retraction where supported. |
| prepare_record(draft, expected_revision, record_context) -> PreparedCommit or Hold | Validate the exact assessment or history delta, origin, claims, occurrence and authored cutoff. Bind its immutable bytes, pins, expected journal head and transaction key. A preflight hold or capture can use its own observed source basis. |
| record(prepared_commit, write_context) -> CommitDisposition | Append only the pinned delta through the S3 journal and return its receipt or scoped unresolved state. Recording never calls the evaluator. |
| recover(operation_key, expected_binding, read_context) -> RecoveryDisposition | Read exact journal or storage evidence and reconcile the intended effect. Report committed, established absent, disputed or unresolved as supported. A read capability confers no write or execute effect. |
| select(history_view, selection_policy, cutoff, read_context) -> SelectedView or Hold | Select exact authorized records. Apply the declared policy and preserve open disputes. Selection is a read and stays distinct from updating a pointer. |
| prepare_handoff(selection, audience, disclosure_policy, read_context) -> HandoffDraft or Hold | Freeze the outward claims and allowed assurance in a separately pinned view. Verify both S5 proof closure and the intended S3 carrier closure under the supplied authority. |
| publish(handoff_draft, publication_id, storage_context) -> PublicationDisposition | Use the existing S3 store with the exact authorized bytes and audience. Recover via the matching publication binding. Pointer advancement is a separate authorized operation. |
| capture_legacy(bytes, attribution, mapping_registry, limits) -> LegacyCapture or CaptureIssues | Preserve original bytes and supported reported meanings under an exact mapping. The output is a preservation or interpretation draft. Independent reassessment uses the ordinary preparation and evidence path. |

The prepared identity includes the resolved question, exact rule and
implementation/configuration pins, evidence and selection, frontier,
audience and effective limits. Do not use a rule name as a loader.
An explicit versioned registry supplies decision semantics and scoped
qualification. Qualification of a registered evaluator and satisfaction
of the prerequisites for one assessment are separate.

## Who supplies what

| Party or boundary | Supplies |
|---|---|
| Requester and study owner | Exact S2 scope, selected question and rule, selection policy, and applicable prospective commitment. The historical importer supplies attribution for reported claims. |
| Evidence custodians and qualified readers | Exact S1 semantics, S2 design, S3 realization and exposure, S4 measurement, and supported source or authority receipts as needed by the rule. S3 can supply attributed operational incidents directly. |
| Rule and registration owners | Installed rule semantics and qualification, and evidence of commitment, information boundaries, amendments and analysis conformance. S5 checks the evidence at the target scope. |
| Coordinator and adjudicator | Coordinator supplies the admitted occurrence and observed work. The adjudicator supplies the scoped authority and evidence to resolve or retract a finding. Attribution identifies who asserted something. It does not confer decision authority. |
| Journal, storage and audience owners | Separate read/write capabilities, journal receipts, disclosure policy, authorized carrier and publication receipts. S6 receives only the selected authorized handoff and its verification limits. |

For the held six-case name-swap example, the study owner supplies the
six-case intent and R1. The evidence view supplies four qualified pairs
and scoped gaps for the other two. Preparation can return a hold and
its basis. An authorized recorder can save that hold without claiming
an evaluator occurrence or using a four-pair score as the full frame.
For a later rule-decision assessment, S4 supplies the exact full-frame
result and qualification, and the coordinator observes actual S5
evaluation. A new registration receipt can support a separate linked
status update using the already recorded decision.

## Recovery examples and invariants

| Event | Required behavior |
|---|---|
| Append reply lost for assessment A2 | Look up the transaction using the exact prepared binding, including account, expected revision and delta identity. A matching committed receipt reconciles the original assessment without another evaluation. An unavailable lookup leaves the commit unresolved. A matching transaction key with changed bytes is disputed. |
| Owner establishes absence and permits retry | Retry only the same prepared operation with the same transaction binding and applicable authority. If the head advanced, obtain an authorized reprepare or reconciliation under the new revision. A changed expected head changes the transaction binding. Preserve the exact original assessment and basis if still valid, and link the distinct commit attempt. |
| Evaluation entry recorded, result absent after interruption | Preserve the known entry and unresolved outcome. An explicit authorized replay gets a new occurrence and links the original. A pure calculation makes a replay feasible, while the original work history and its scientific units stay distinct. |
| Two new pairs or an alignment correction arrive | Prepare a new assessment with a new basis and cutoff. Evaluate again if the decision depends on changed evidence. Link the earlier hold or decision. Recovering an old write cannot install a new decision. |
| Registration receipt arrives after a verdict | Record a new linked status assessment with its own registration evidence. Reuse the pinned decision and its earlier frontier. The update need not rerun evaluation. |
| Publication succeeds and pointer update fails | Reconcile the committed exact view. Record the pointer conflict or unresolved effect separately. Reopen the latest authorized pointer revision before any new advancement, and never treat a lost pointer reply as publication failure. |

Reuse the existing [S3 journal and storage ports](../execution/api.py),
the [S4 work lifecycle](s4/b03-calculation-implementation.md) and
[S4 carrier pattern](s4/b09-publication-implementation.md). Do not add
another independent authority or durability system for S5. Keep
operation key, assessment, work occurrence, frozen view and pointer
revision separate. Reopening old bytes rechecks access without changing
the original cutoff.

## Legacy mapping

The legacy [finding engine](../findings.py),
[rule catalog](../protocol/kinds.py) and
[certificate writer and verifier](../report/certificate.py) have their
own behavior. Use a read-only capture and explicit versioned mapping.
Pin the source bytes and the source locator or selector, report or
certificate format, finding ID, and any rule, metric and population
evidence actually available. If a legacy report and its certificate
carry different detail, retain separate source roles. Resolve any
disagreement with evidence rather than merging fields by convenience.
Preserve numeric spelling, units, labels and the original rule identity.

| Historical material | What can carry forward |
|---|---|
| Exact K01–K15 report or certificate fields | Attributed finding ID, kind, reported verdict and label, and available effect, interval, scope and reason. An absent field stays absent at that source's scope. |
| Reported fires or clear | Preserve the verdict and its particular rule. A historical clear can mean a predicate was false under that rule. It does not establish equivalence, safety or system-wide absence. |
| Inconclusive, not_checkable or not_run | Retain the original disposition and reason. Map to a more specific modern claim only with evidence. A historical not_checkable can refer to inapplicability or missing capture. |
| Verified legacy certificate | Carry a separate verification receipt with what the legacy verifier actually checked, tolerance and environment. That receipt does not supply missing native evidence, stronger rule qualification or independent registration chronology. |
| Unknown version, missing attribution, changed bytes or unresolved scope | Preserve the observable source with its corresponding gap or integrity disposition. Hold interpretation or reassessment where the required identity or scope is unavailable. |

The historical
[checkpoint account](project/q1-checkpoint-2026-10-31.md)
gives two useful checks. For Causal-Copilot, its 0.167 used a committed
direction score at stage S3 by family. The other named AB-06 systems
used expected direction on final output by scenario. Preserve both
meanings and the P9 and K04 provenance separately. For BND-08, preserve
the 81-of-101 observation, the pre-registered M3 verdict and the package
K11 exploratory label as distinct claims. A shared count does not
make the two rules or their registrations identical.

An independently established S5 decision from historical inputs needs
the same exact rule, sufficient admissible evidence, scoped qualification
and recorded work as a new assessment. It can be linked to the historical
statement with an explicit comparison of rule and scope. Keep the frozen
paper and certificate evidence as separate historical identities. Use
the [S4 historical compatibility receipt](s4/b10-legacy-implementation.md)
as a model for preserving parity without promoting scientific claims.

Next, review the complete S5 design and prepare the bundle DAG. Check
normal and adverse paths for the four wire specimens, including a
lost commit reply, changed scope, unresolved legacy timing and a public
view whose proof closure excludes restricted material.
