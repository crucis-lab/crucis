# Subsystem 1 implementation log

Tickets: DLV-08, DLV-09, DLV-10.

Uzair accepted the full design and S1-A..G plan and explicitly authorized implementation through all gates.
The permission supersedes the earlier design-only/provisional wording. It does not authorize API spend,
protected/shared edits, git writes, W1/W5 changes, result migration or a port map. Public adoption is separate.

Implementation is additive in audit/connections. The original legacy package and its public certificates
remain unchanged. Each bundle gate uses fresh external outputs under ../_w2_checks/2026-11-01_s1_build/.
The project DAG check passed; the subsystem DAG advances existing tickets and does not close program tickets.
Pre-existing worktree changes were inspected and are left untouched.

Validation dependency jsonschema 4.25.1 is isolated under that external directory. The existing Python
3.12.14/NumPy runtime remains unchanged. causal-learn and SciPy are absent; live-PC readiness is not claimed.

Bundle evidence (external paths relative to the shared DSC folder):

| Bundle | Successful gate | Tests run / skips | Stored comparisons | Certificates |
|---|---|---|---|---|
| S1-A | `_w2_checks/2026-11-01_s1_build/S1-A/gate-run3/gate.json` | 65 / 1 | 1,298 pass | 14 stored + 14 fresh pass |
| S1-B | `_w2_checks/2026-11-01_s1_build/S1-B/gate-run1/gate.json` | 76 / 1 | 1,298 pass | 14 stored + 14 fresh pass |
| S1-C | `_w2_checks/2026-11-01_s1_build/S1-C/gate-run2/gate.json` | 89 / 1 | 1,298 pass | 14 stored + 14 fresh pass |
| S1-D | `_w2_checks/2026-11-01_s1_build/S1-D/gate-run1/gate.json` | 98 / 1 | 1,298 pass | 14 stored + 14 fresh pass |
| S1-E | `_w2_checks/2026-11-01_s1_build/S1-E/gate-run1/gate.json` | 109 / 1 | 1,298 pass | 14 stored + 14 fresh pass |
| S1-F | `_w2_checks/2026-11-01_s1_build/S1-F/gate-run1/gate.json` | 125 / 1 | 1,298 pass | 14 stored + 14 fresh pass |
| S1-G | `_w2_checks/2026-11-01_s1_build/S1-G/gate-run2/gate.json` | 140 / 1 | 1,298 pass | 14 stored + 14 fresh pass |

Every listed gate checked exact comparison-key/count parity and finding ID/kind/verdict parity.
Maximum absolute difference was 0.000091483427284475 throughout; certificate tolerance was not widened.
The remaining skip is the original live-PC dependency test. No native scientific system or provider was invoked.
The S1-E process test runs a labeled deterministic local fixture with no network or spend.

Failures were diagnosed before progression: the initial A fixture used an unwrapped event reference where
SC-1 requires K(Ref(event)); the fixture was corrected. A's first full run placed synthetic sealed storage
inside the shared folder; the gate now uses Windows temporary storage outside it. Sandbox Windows temporary
write denials require escalated tests; they are not counted as successful gates. The first E targeted run
used Ref(artifact_snapshot) rather than PayloadRef for model artifacts, and the legacy adapter's hyphenated
display name rather than its registered underscore name; both were corrected before E passed. Original
legacy/runtime files were not changed to make these tests pass. Failed outputs remain in the external check folder.

The final suite has 139 passes and one skip: all 85 new subsystem-1 tests pass,
alongside the original 54 passes and dependency skip. Four new CLI capture/store/
foundation/integrity paths pass (PC, MATMCD, causaliq, Causal-Copilot bnd08). All
eight existing adapters pass additive recorded import/echo tests. Eleven frozen
synthetic packages cover all 36 records and 12 body types. Compilation passes with
bytecode outside the repository. The implementation was stable throughout G.

The original 64-file identity remains
`d615f61a2ce46862b9093ee7309374c825a5684dcf0d4561453a7d71444e42ae`.
G's new 44-file runtime/test/schema/fixture manifest digest is
`b23093ae21538dd36436c7544f00e3ae1df35255924cadda97d98afa51478256`.
The exact file list/hashes are in `S1-G/gate-run2/implementation.sha256`; explanatory
docs are excluded from that identity. Dependencies use a complete isolated lock.

G's first successful full gate was followed by a concrete extra malformed-number
case. The numeric constructor now reports unsupported lexemes as WireError, allowing
native importers to retain raw evidence with a gap; unfamiliar file/cost declarations
also preserve their original fields. G was rerun fully after that source change.
Other G review checks cover empty evidence, foreign graph relations, tiny distinct
coordinates, wrong parameter pairing, exact ratio values, mapping an empty graph
twice, unresolved predecessors, branch ancestry and unsupported route readiness.

## Handoff checks and scope incident

Final targeted secret scanning passed: 51 implementation/fixture/doc files, zero
findings (`S1-G/secret-scan-final.log`). A final 44-file hash check found no source
changes after G (`S1-G/final-source-check.json`). Read-only repository CI reports one pre-existing error:
DLV-07's pin for `tools/export_q1.py` needs owner review. That file was already
modified at kickoff and has not been edited by this implementation.

Codex incorrectly ran `tracker/trace.py check` as a read-only handoff check. It
regenerated `tracker/trace.json` and `tracker/trace.md`, contrary to Uzair's scope
restriction. No new IDs were locked. Exact pre-run copies were unavailable, and
Uzair confirmed he has no backup; the derived outputs remain for W5/Uzair review.
See [the incident report](subsystem1-trace-incident-2026-11-01.md), which records the
two outputs and external copies. This violation is disclosed separately from the
passing implementation gates. No ticket status/pin, W1/B5/shared scientific code,
public report/certificate, result-folder layout, API account or git index/ref was changed
by subsystem-1 implementation.

## Where we're going

S1-A..G implementation gates are complete. Review the release evidence and the two
unintentionally regenerated trace outputs; W5/Uzair owns public adoption, deliberate
pin/evidence-list updates and commit/snapshot steps. Wider W2 decisions and other
subsystems remain outside this completed increment.
