# Subsystem 2 implementation evidence index

Tickets: DLV-08, DLV-09, DLV-10. Local date 2026-11-02.
This addendum preserves the accepted candidate and earlier methodology index as
historical sources. It indexes implementation and validation separately. The
machine-readable companion records final receipt hashes after completion.

## Claim-to-evidence map

| Methodology claim | Implemented source | Functional evidence |
|---|---|---|
| Typed bounded source-preserving metadata | experiments/schema.py, codec.py, resolver.py, payloads.py and catalog.json | test_audit_experiments_wire.py; all 38 accepted package snapshots, all 40 S2 record kinds, 25 parameter schemas, 11 typed formats |
| Scope and authority remain distinct | api.py, profiles.py, services.py, writer.py | test_audit_experiments_services.py and integration.py: scoped profiles, transactional rejection, exact registries, critical extensions, immutable bytes |
| Case identity and collection occurrence are explicit | contracts.py, selection.py | test_audit_experiments_definitions.py: source-scoped selection, ambiguous/missing candidates, member ownership/multiplicity |
| Scientific result meaning depends on scope | responses.py, families.py | definitions.py/families.py/integration.py tests: absence/unreported boundaries, alternative orders, temporal eligibility, party/entity identity, learned mappings, native collection associations, intervention/proxy domains |
| Supplied inputs and transformations need separate evidence | bindings.py, information.py | test_audit_experiments_families.py: supplied realization checks, missing materialization, forbidden evaluator channel, no transformation execution |
| Population, selection and measurement intent are fixed explicitly | evaluation.py | test_audit_experiments_evaluation.py/integration.py: retained intended units, missingness, stage/abstention exclusions from graph quality, no best/reference/particle/retry shortcuts; no new metric implementation |
| Chronology and exposure cannot be reconstructed by convenience | lifecycle.py | test_audit_experiments_lifecycle.py: earlier byte pins, amendment history, future-package exclusion, adaptive branches, selected versus delivered, exposure retained after failure |
| Native requests need exact scientific/native translation | handoff.py, completion.py | test_audit_experiments_handoff.py: exact registry keys, differing operation names, permitted payloads, cardinality, paired writer rollback, immutable R/H/O pins; unchanged S1 restart/history tests |
| Historical imports preserve native source meanings | legacy.py, unchanged connections/legacy.py | test_audit_experiments_legacy.py/integration.py: all eight recorded adapters, exact encoded echo, explicit losses, source-only declarations, cross-writer occurrence recovery, duplicate-key round-trip rejection |
| The interface is opt-in and recorded evidence is checkable | experiments/__main__.py | MatMCD CLI import/report/echo/validation/evidence association under final gate; no dispatch/spend/protected-read command |
| Existing scientific numbers and certificates remain unchanged | unchanged connections/gates.py, rerun/existing.py and report/certificate.py | Each bundle's preservation/gate.json: 1,298 comparisons, exact key/count/verdict parity, 14 stored plus 14 fresh certificates, original/S1 source identities |

Paths in the table are under audit/ unless prefixed test_, which names files under
tests/. These are scoped contract claims. A source snapshot passing preservation
does not establish causal correctness, native-system support, original chronology,
independence or scientific reference applicability. Supplied check records retain
their named procedure, scope and evidence; S2 does not independently repeat the
underlying scientific procedure.

## Validation lineage

The accepted design baseline is outside the repo at
`../_w2_checks/2026-11-02_s2_build/accepted-design.json`. It pins 53 source artifacts
and records Uzair's approval. The entry and A-I receipts identify interpreter,
dependencies, predecessors, source/fixture hashes and tests. The final I acceptance
ledger links all 58 adverse specifications and 20 API scenarios, and all 66 ordered
must-show rows, to executed functional tests and common preservation evidence.

Semantic adverse tests materialize their required evidence in complete functional
fixtures rather than relying on a stale-ID conflict or an unrelated unknown field.
Wire/byte adverse tests apply the exact accepted mutation. Several checks reuse
functional assertions. They are not independent empirical observations and must
not be counted as extra native-system or scientific coverage.

API09 and API11 retain the original design expectations in the ledger alongside
stricter implemented outcomes: an unestablished preview rejects handoff; an
incomplete population remains partial. Positive generated handoff and complete
metadata-population cases pass separately. The actual source records are never
rewritten to conceal a mismatch.

Failed attempts remain outside the repo, including initial environment failures and
focused implementation corrections. The final source identity excludes explanatory
Markdown but includes runtime, catalog, dependency specification, tests and fixtures.
Later prose indexing does not refresh the identity of a prior code execution.

## Reuse in the paper and next subsystem

Cite the rule/design artifact, implemented function, scoped test and exact gate
receipt together. Use the companion JSON to locate their recorded hashes. The
accepted synthetic A-H packages and capability/composition scopes are conformance
examples. Existing recorded systems supply historical compatibility evidence.
Fresh empirical runs across systems/datasets require separate execution planning,
authorization/funding and scientific analysis.

S3 can consume immutable run/request/handoff bindings, but must establish actual
dependencies, runtime grants, native dispatch/observation/delivery and recovery.
S4 supplies scientific metric/uncertainty procedures. Metadata intent does not
replace either subsystem's evidence. No S3 or S4 implementation is included here.

The unrelated whole-repository CI pin drift remains DLV-07's tools/export_q1.py
October 31 patch. Its current SHA256 equals the preserved patch source; this work
does not repin it. W5 adoption, W1 paper pointers, tracker/site updates, durable
external evidence archival and git commits remain owner actions.

## Where we're going

Use the completed metadata layer and its evidence as the next subsystem's input
contract. Review its execution/measurement responsibilities separately before any
native or paid run, keeping the existing unknowns and publication identities intact.
