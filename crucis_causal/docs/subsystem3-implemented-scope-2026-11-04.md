# S3 implemented scope, 4 November 2026

Tickets: DLV-08, DLV-09; related DLV-10. S3 is the opt-in execution/evidence layer
in `crucis_causal.execution`. The accepted revision 3 contract and B00–B13 plan
remain the baseline. Earlier design proposals and their source identities remain
historical; this account describes the implemented, receipt-qualified scope.

## Architecture and responsibilities

| Responsibility | Owned implementation | Established boundary |
|---|---|---|
| Execution identity and durable history | `model`, `codec`, `journal`, `store` | Exact C/G/D correlation, immutable snapshots, expected revisions and historical cutoffs; intent does not prove launch |
| Admission and authority | `owners`, `authority`, `coordinator`, `clock` | Supplied live controls, complete owner groups, temporal validity, one-use local forwarding permits; persisted metadata cannot recreate permission |
| Input realization and staging | `inputs`, `staging`, `effects` | Exact supplied transform/reference context and guarded stage/cleanup; uncertain disclosure persists |
| Dispatch and attachment | `drivers`, `identity`, `scientific`, `bridge` | Actual native mechanics and scoped identity; lost ACK never silently becomes safe resubmission |
| Observation and interaction | `collection`, `decisions`, `interaction`, `native_results` | Durable raw capture before separately admitted ACK, distinct occurrence/event identities, frozen decision basis and authorized delivery |
| Recovery and accounting | `recovery`, `stopping`, `accounting` | Explicit pinned policy, actual continuation condition, component stop/loading facts, replacement billing, preserved unresolved obligations |
| Evidence publication | `projection`, `publication` | Exact audience closure, immutable bytes and external receipts, revision CAS, copy-specific revoke/delete |

Common policy uses explicit pinned evaluators and supplied capabilities; native
mechanics remain in drivers. There is no default provider, credential search,
scientific scorer, hidden locator fetch or recovery policy. `Core` and the opt-in
module CLI expose supplied-byte inspect/validate/plan/recovery-plan operations.

## Four exercised profiles

| Profile | Actual controlled mechanism and result | Limit |
|---|---|---|
| E01 local | Synchronous native function through S3, original native column order plus explicit derived mapping, one call; charge 0.7 under cap 1; cold evidence read | Fixed synthetic scientific binding; graph correctness is not established |
| E02 remote | Independent persistent receiver, launch reply loss, exact lookup/attachment, three capture occurrences/two native events, cold source ACK, existing cap 10 retained | A negative lookup is not closed ingress; no provider-wide idempotency |
| E03 interactive | Distinct same-text actions, fixed source/compute/choice; Q1: one delivery, Q2: no delivery; budget consumed 1, remaining 1; cold receipt lookup without resend | Unknown scientific origin; undeclared scientific followup channels remain held; native use/termination unknown |
| E04 checkpoint | Explicit R2 S2 condition, A1/A2 in one scoped trial, captured/native state sources, model/optimizer loaded; final bill 5 replaces interim 3, plus successor 4 gives 9 under cap 20 | RNG/history and exact trajectory continuity unknown; original NA recovery request unchanged and held |

Cold evidence reads and object reopening are identified separately from actual
process-death recovery. F01–F20 exercise their declared boundaries with retained
oracle/history/recovered-view triplets. B10 F12/F13 kill actual coordinators after
stop ACK, restart acceptance and state loading, then reconcile without duplicate
launch. Other fault cases use explicit deterministic boundary errors where stated;
they are not relabeled as OS crashes or power-loss experiments.

## Contract coverage and validation

The closed model contains 38 record kinds, 31 operations, 48 exact port signatures,
18 semantic role families/77 role positions and eight separately qualified support
axes. [The methodology index](subsystem3-methodology-index-2026-11-03.json) links
accepted rules to actual source hashes, concrete tests and scoped bundle receipts.
All 106 planned obligations, including the D00 fixed baseline and R01 release check,
are accounted for; 30 inherited negative boundaries have explicit executed-test links.
These counts describe contract coverage, not 106 independent scientific experiments
or a percentage of all possible external-system combinations.

B12 final target: 118 tests, zero failures/errors/skips. The final
integration predecessor's full suite ran 453 tests with zero failures/errors
and 26 inherited data/dependency skips in both staged-tree and enabled-hook
gates. No mandatory new S3 case was skipped. B13 repeats the full appropriate gate;
its exact final tree/commit and counts are controlled by its external post-commit
receipts, not guessed by this document before its own commit.

Installed-wheel isolation verified 159 runtime files against the wheel with
source/research imports blocked, retained
licenses, S1/S2/S3 schemas and module CLI probes. Source-distribution contents were
checked separately. No package-index release was made.

The once-after-integration recorded-data rerun passed 1,298/1,298 comparisons at the
unchanged 0.001 tolerance (max absolute difference
9.1483427284475e-05). All 14 stored and 14 freshly recomputed certificates
verified. This is legacy compatibility, not a new native scientific campaign and
not adoption of sibling framework outputs into the Q1 paper contract.

## Explicit support limits

The qualified local profile uses cooperative single-host SQLite DELETE/FULL,
flushed immutable artifacts and actual issuer-owned controls. It does not establish
hostile-code isolation, distributed transactions, host/power-loss durability,
universal hard provider charges, descendant termination, exact RNG replay, remote
publication or global erasure. Revoking access or deleting one owned copy does not
remove prior exposure or other copies. Unsupported stronger claims remain held.

Only this Windows Python 3.12 host has fresh S3 runtime receipts. The existing Linux
Python 3.10/3.12 and Windows 3.12 CI matrix is prepared; fresh remote matrix results
require separately authorized publication/CI. Real named-system integrations,
their scientific environments and paid/sealed campaigns remain unqualified here.

S1/S2, graph core, shared support, legacy scoring/rerun/report modules and frozen
scientific results were not rebaselined. No research/paper/tracker/site files were
written under this implementation scope. Private bootstrap controls and raw
operational receipts remain outside this public technical account.

## Where we're going

S3's scoped offline foundation is ready for review and future subsystem design.
Remote PR/CI qualification, actual native backend campaigns, additional scientific
interactive conditions and new recovery-policy modes remain separately scoped
work. None begins automatically from this release account.
