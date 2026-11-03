# Methodology reference index: subsystem 1 completion and subsystem 2 opening

Tickets: DLV-08, DLV-09; related DLV-10 and paper owners DLV-05/06/07.
Recorded local date: 1 Nov 2026, America/Los_Angeles.
Last updated: 2 Nov 2026; subsystem-2 closure, final review candidate and proposed DAG.
Purpose: durable source map for writing the auditor's methods and limitations.
This is research documentation in W2, not an edit to W1's paper or an adopted public contract.

## 1. Status and document precedence

Uzair explicitly requested that the design, implementation and validation history
be retained as references for the eventual methodology paper. He authorized opening
subsystem 2's design discussion, with no subsystem-2 implementation.

The original STATE/kickoff and early system-connection design notes retain their
historical dates. Their descriptions of subsystem 1 as unbuilt have been superseded
by the user-authorized implementation and its release evidence. They are not edited
retroactively. Their protected ownership, no-spend, adoption and paper boundaries
remain in force.

| Topic | Current reference | How it can be used |
|---|---|---|
| Motivation and requirements | [Connection principles](system-connections-principles-2026-11-01.md) and [capability map](system-connections-capability-map-2026-11-01.md) | Explain why the core preserves broader results and separates guarantees; external examples have their own source notes |
| Chosen connection design | [Contract outline](system-connections-contract-outline-2026-11-01.md), [serialization](system-connections-serialization-2026-11-01.md), [interaction](system-connections-interaction-recovery-2026-11-01.md), [API/legacy contract](system-connections-api-legacy-2026-11-01.md) | Describe accepted design and exact candidate contracts; distinguish historical proposal wording from later authorization |
| Implemented scope and limits | [S1 release review](subsystem1-release-review-2026-11-01.md), [support matrix](subsystem1-implemented-support-2026-11-01.md), [runtime README](../connections/README.md) | State which mechanisms and integration cells exist, and what is withheld |
| Implementation and corrections | [Implementation log](subsystem1-implementation-log-2026-11-01.md), [bundle DAG](subsystem1-implementation-dag-2026-11-01.json) | Explain dependency order, acceptance gates and concrete corrections |
| Executable validation | `tests/test_audit_connections_*.py`, frozen `tests/audit_fixtures/sc1/`, final external gate | Support tested behavior and explicit negative cases; synthetic fixtures are labeled |
| Ownership incident | [Trace incident](subsystem1-trace-incident-2026-11-01.md) | Retain the known deviation and recovery limit; do not claim complete scope compliance |
| Subsystem 2 | [Current rebase/source map](subsystem2-design-rebase-2026-11-02.md), [closure/service contracts](subsystem2-contract-closure-2026-11-02.md), [exact catalog](subsystem2-contract-catalog-2026-11-02.json), [wire corpus/source mappings](subsystem2-specimens-2026-11-02/manifest.json), [final review](subsystem2-final-design-review-2026-11-02.md), [DAG](subsystem2-implementation-dag-2026-11-02.json) | Seven areas composed in A-H candidates; 40 core kinds, 25 parameter schemas, 11 payload formats and 16 metadata entry points. 38 synthetic packages; 58 adverse specifications and 20 API scenarios await executable S2 tests. Documentation checks are not native/scientific support. Final acceptance/build go/public adoption remain pending |
| Q1 study scope and funding | [Proposed empirical matrix](q1-study-matrix-2026-11-01.md), budget ledger (archived research planning record), short email reported sent (archived research planning record), scope correction (archived research planning record) | User approved and reported sending the short proposal. Funding remains pending; historical costs are provisional proxies. The old Causal-Copilot-centered $100 full request is superseded. No final experiment or paid-run go is approved |
| Paper source/adoption rules | [Q1 checkpoint contract](project/q1-checkpoint-2026-10-31.md), sections 2a-4 | Preserve number provenance, labels, tracked-source requirements and W1/W5 responsibilities |

## 2. Evidence ledger for subsystem 1

The final implementation gate is outside the repository:
`../_w2_checks/2026-11-01_s1_build/S1-G/gate-run2/`.
Its source UTC test timestamp is 2026-11-02T04:24:07Z (1 Nov locally).
The [companion JSON index](methodology-reference-index-2026-11-01.json) records source
artifact paths, exact hashes and pointers.

| Claim | Source | Meaning and boundary |
|---|---|---|
| 140 tests run, zero failures/errors, one skip | `gate.json#/tests`, `tests.json` | 139 passed = 140 run minus 1 skipped, with zero failures/errors |
| 85 additional tests; all pass | Final 140-test suite versus unchanged original 55-test baseline in `../_w2_checks/2026-10-31_codex/tests_audit_windows.json` | Engineering acceptance cases; this is not a measured finding-detector sensitivity/specificity study |
| Eleven frozen complete specimens cover 36 record and 12 body types | `tests/test_audit_connections_integration.py`, frozen `tests/audit_fixtures/sc1/*.json` | Structural and selected semantic composition; all specimens are synthetic |
| All eight legacy adapters have recorded import/echo checks | `tests/test_audit_connections_ports.py` | Selected recorded examples per adapter; not every mode/configuration or fresh native execution |
| Four new CLI package paths pass | `gate.json#/new_connection_paths`, `connection_*` receipts/validation | PC, MATMCD, causaliq, Causal-Copilot bnd08; capture/publication/integrity, not new accuracy experiments |
| 1,298 stored comparisons pass, max difference 0.000091483427284475 | `gate.json#/comparison`, `rerun/comparison.json#/summary/all` | Existing scientific results reproduced through the unchanged legacy auditor within 0.001 |
| Exact comparison-key/count parity | `gate.json#/comparison_key_parity`, `/exact_count_parity` | Counts and compared quantity identities were retained |
| 14 stored and 14 fresh certificates verify | `gate.json#/certificates` | Two versions of certificates for the same 14 audits; not 28 independent audits. Finding ID/kind/verdict parity is checked |
| Fresh same-host tolerance remains 1e-9; stored cross-host tolerance is 0.001 | Entries in `gate.json#/certificates` | Existing verifier rules; no tolerance widening |
| Original 64-file identity unchanged | `gate.json#/source_identity` | Applies to the declared original file set, not every pre-existing workspace file |
| New runtime/test identity stable | `implementation.sha256`, `after/implementation.sha256`, `gate.json#/source_stable_during_gate` | 44 files; explanatory docs excluded. Final handoff hash check is `S1-G/final-source-check.json` |

Native-PC readiness remains unproven on this host because causal-learn is absent;
its existing test is the skip. The new process tests use a deterministic offline
fixture. The recorded Causal-Copilot example has a failed wrapper status and four
surviving stages; preservation of those stages is not normal-termination evidence.

Every S1-A..F predecessor passed its own gate before progression. The implementation
log identifies the exact successful directories; failed attempts are retained and
are not counted as successes. No test rerun or scientific experiment was performed
while opening subsystem 2 and writing this index.

## 3. Writing rules for subsequent methodological notes

Each substantive design decision should retain its question, proposed/accepted
choice, strongest alternative, reason, cost, prevented failure mode and evidence.
Record who accepted it and when; do not turn a proposal into a user decision.

Separate these kinds of statements:

- **Design intent:** what a mechanism is meant to preserve/prevent.
- **Inspected implementation:** what identified code currently does.
- **Executed validation:** the exact case, environment, outputs and observed result.
- **Scientific finding:** a result with its metric, population, run set, reference,
  uncertainty and confirmatory/exploratory status.
- **Unsupported or unknown:** the prerequisite or evidence that is missing.

Keep historical sources and corrections. A later interpretation or plan amendment
gets a new identity/version and explicit relation; it does not erase what was known
at the original decision point. Record partial results, exclusions, denominators,
case pairing, dependence/grouping, randomization roles and observability limits.

Existing studies are historical. A newly written design cannot retroactively make
their analyses preregistered. S1's conformance tests do not close the original V7
auditor-validation battery or the wider finding-coverage gaps. Representation of a
result family is not proof of a working third-party integration or a scientific
evaluator for that family.

## 4. Retention and paper preparation

These notes organize source material; they are not a replacement for the raw
validation artifacts. A recorded digest identifies an artifact and detects change;
it cannot recreate a missing artifact. Preserve external gate reports/logs/manifests
and their source references for later controlled archival/adoption.

Before a quantitative statement enters the paper, W1/W5 must arrange the adopted,
tracked source and pointer, revision/lock and relevant scientific labels under the
paper contract. Do not make the paper depend on an ephemeral machine-local path.
The engineering-validation results also need a durable referenced source if quoted.
No paper registry, public certificate, tracker pin, export allowlist, port map or
result layout is changed by this index.

## Where we're going

Use this index as the entry point for method writing and extend the evidence trail
through dated subsystem notes. Subsystem 2 begins with structure and principles,
then concrete examples and decisions; detailed contracts and implementation gates
come only after that design work and an implementation go.
