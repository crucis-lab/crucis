# Subsystem 1 release review

Tickets: DLV-08, DLV-09; DLV-10 compatibility.
Status: S1-A..G implementation complete, opt-in SC-1 release candidate.
Public adoption and program ticket closure are not claimed.

## Result

The accepted system-connections contract is implemented in `audit/connections/`:
strict SC-1 serialization and references, immutable evidence/package publication,
domains and mappings, selected graph/local/quantity/collection/model contracts,
scoped outcomes, history/recovery/replay/accounting, optional adapter ports, injected
services and explicit runtime authority, additive recorded legacy import and partial
prospective projection. The command line is `python -B -m audit.connections`.

The adopted audit/scoring/report/certificate path retains its contracts. No protocol
v1.1 adoption, old C1-C5 bundle execution, result migration or port map occurred.

Implementation/usage: [connections README](../connections/README.md).
Detailed guarantee cells and limitations: [support matrix](subsystem1-implemented-support-2026-11-01.md).
Bundle history: [implementation log](subsystem1-implementation-log-2026-11-01.md).
Accepted dependency chain: [implementation DAG](subsystem1-implementation-dag-2026-11-01.json).

## Validation

Final evidence directory, outside the repository:
`../_w2_checks/2026-11-01_s1_build/S1-G/gate-run2/`.

| Obligation | Actual result | Source in that directory |
|---|---|---|
| Current audit tests | 140 run, 139 pass, 1 dependency skip, 0 errors/failures | tests.json, tests.log |
| New subsystem acceptance cases | All 85 pass; none skipped | Named connection tests in tests.log |
| Frozen compositions | Eleven synthetic packages cover every 36-record/12-body type, with expected scoped pass/fail/unknown checks | Integration tests and checked-in goldens |
| Stored-number parity | All 1,298 pass; max absolute difference 0.000091483427284475 | rerun/comparison.json |
| Exact compatibility | Complete comparison-key/count parity and finding ID/kind/verdict parity | gate.json |
| Certificates | All 14 stored and 14 freshly generated certificates verify | gate.json/certificates and fresh rerun reports |
| New package paths | PC semantic, MATMCD, causaliq, Causal-Copilot bnd08 capture/store/foundation/integrity pass | connection_*/{package,receipt,validation,foundation}.json |
| Existing adapter surface | All eight recorded import/echo paths pass without calling native run | Port/semantics tests |
| Original package identity | All 64 original files unchanged | gate.json/source_identity |
| Compile/current source | New Python files compile externally; source stable across complete gate | bytecode/, implementation.sha256, after/implementation.sha256 |

The original live-PC test skips because causal-learn is absent. This narrows native
PC readiness; recorded PC evidence passes. The runtime was Python 3.12.14, NumPy
2.3.5, with the pinned structural-validation dependency set isolated outside the
repository. No API spend or production native scientific execution occurred. Local
process behavior is explicitly labeled synthetic conformance.

Stored certificate verification uses the existing verifier's unchanged same-host
and cross-host tolerances. No widening, threshold tuning, number substitution or
new scientific metric was introduced. Every S1-A..F predecessor also passed its
own complete legacy comparison/certificate gate before progression.

Original identity:
`d615f61a2ce46862b9093ee7309374c825a5684dcf0d4561453a7d71444e42ae`.
New 44-file runtime/test/schema/fixture manifest SHA256:
`b23093ae21538dd36436c7544f00e3ae1df35255924cadda97d98afa51478256`.
The manifest excludes explanatory docs; per-file hashes are retained externally.

## Practical boundaries

Preservation, interpretation, requested-scope fulfillment, native termination and
scientific correctness remain separate. A wire-valid package can preserve a failed
DAG claim, invalid probability, parser failure, missing file, contradictory outcome
or unknown native occurrence. Stronger claims require their named checks and scope.

Native model internals, complete CPDAG/PAG validation, relational grounding, factor
alignment criteria, arbitrary remote orchestration and new scientific evaluators
remain extensions. Prepared/supplied/attached ports are reusable mechanisms; the
tested concrete new native route is a deterministic offline fixture. All actual
third-party integration evidence in this increment is recorded evidence.

## Repository handoff and incident

The new files are confined to owned implementation/tests/fixtures/docs, except for
one unintended operation: Codex ran `tracker/trace.py check`, which regenerated
`tracker/trace.json` and `tracker/trace.md`. This violated the W5 ownership/no-write
boundary. Prior exact copies were not retained or found; Uzair confirmed no backup.
No rollback from the older git versions was attempted. The two derived files remain
for W5/Uzair review. [Incident details](subsystem1-trace-incident-2026-11-01.md) identify
the call sites and copies of the exact post-command outputs.

Read-only repository CI still reports the pre-existing DLV-07 evidence-pin mismatch
for `tools/export_q1.py`. That exporter was not modified by this increment. The
trace command found zero errors and two relay warnings; it is not a read-only check
and must not be rerun under this scope. Secret scanning found no issues in the
implementation set. No git write, tracker status/pin update or external message was
sent. The broader pre-existing worktree remains uncommitted.

Commit message: `docs/commit_msgs/w2_subsystem1_cc-research.txt`. Select intended
files explicitly during review because the workspace contains other workstreams'
pre-existing changes. W5 owns public adoption and evidence-list/pin changes; Uzair
owns deliberate repin/commit and snapshot-last steps. The original W2 green gate,
W2-5..9 and paper obligations remain in their own workflow.

## Where we're going

Review this subsystem-1 implementation and its evidence, resolve owner handling of
the regenerated trace outputs and existing exporter pin, then adopt/commit the
intended increment. Other subsystems begin only under their own design scope.
