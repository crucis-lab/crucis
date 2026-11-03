# W2 state: the audit package (read this first)

Updated 31 Oct 2026, 13:45 PT, by the W2 chat (Claude), at handover to Codex. Tickets: DLV-08, DLV-09, DLV-10.
Phase: **design iteration**. Protocol v1.1 is proposed (not built); nothing of it is on disk yet. The next build step waits
for Uzair's decisions (section 6) and his go.

## 1. Read order
1. This file.
2. `audit/docs/project/w2-rebase-2026-10-31.md`: the rebase and the v1.1 design iteration. **This is where we are.**
3. `audit/docs/project/q1-checkpoint-2026-10-31.md`: the paper's contract with the package (W1's doc; section 2a holds
   W2's notes).
4. `audit/PROTOCOL.md` (v1.0, what is built) and `audit/README.md` (the package layout and commands).
5. `audit/docs/project/audit-package-build-2026-10-31.md` (what was built, the must-shows, the findings grid) and
   `audit-package-design-2026-10-30.md` (the original design: the seven-system interface table, failure modes).
6. `audit/docs/project/program-v3-excerpts.md`: the program's section 2 (the golden version), the shared rules, the machine.
7. `AGENTS.md` (repo root) and `audit/AGENTS.md`: rules.

## 2. What is on disk (cc-research; nothing committed, last commit `cf536c1`)
| Path | What |
|---|---|
| `audit/{core,protocol,metrics,controls,trace,systems,report,rerun}/`, `audit/{__main__,run,collect,findings}.py` | the package (W2) |
| `audit/{adapters,rca,run_adapters,export_cc_stages}.py` | the B5 claim checker (BLD-15), **unchanged; do not edit** |
| `audit/__init__.py` | docstring patched by w2-01 |
| `audit/PROTOCOL.md`, `audit/README.md` | protocol v1.0; usage |
| `audit/results/rerun_v1/` | `comparison.json`/`.md` and `reports/<audit with @ as _>/{report.json, report.md, certificate.json}` for 14 audits. **This layout changes in bundle C1** (to `rerun_v1/<audit>/...`) |
| `audit/docs/`, `audit/AGENTS.md` | the handoff: this file, the project-doc copies, `checks/rebase_facts.py`, `CODEX_KICKOFF.md`; folder rules |
| `tests/test_audit_{core,l0,controls,trace,report,rerun}.py`, `tests/audit_fixtures/` | 55 tests |
| `jobs/patches/w2_01_audit_package.py` + `jobs/patches/w2_01/` | applied: `audit/__init__.py` docstring; `tools/export_q1.py` `ALLOW_AUDIT` behind `--with-audit` (off) |
| `docs/commit_msgs/w2_audit_cc-research.txt` | the commit message, waiting for Uzair |
| `../_w2_transfer/` (outside cc-research) | W2's transfer tars and test/verify outputs from the VM; **Uzair deletes it** (agents could not) |

Code identity at handover: the 64 package, test and patch files (excluding `results/`) hash to
`d615f61a2ce46862b9093ee7309374c825a5684dcf0d4561453a7d71444e42ae`. Recompute with:
`find audit tests/test_audit_*.py tests/audit_fixtures jobs/patches/w2_01* -type f -not -path "*/results/*" -not -path "*/docs/*" -not -name AGENTS.md -not -name "*.pyc" | sort | xargs sha256sum | sha256sum`
(bash, from cc-research; checked on the second laptop at handover. `audit/docs/` and `audit/AGENTS.md` are the handoff
files and are excluded).
The rebase's facts were recomputed on the second laptop at handover (`../_w2_transfer/rebase_facts.json`): all as stated.

## 3. What is verified, and where the evidence is
| Claim | Evidence | Where it ran |
|---|---|---|
| 1,298 stored numbers (AB-06, AB-01, AB-04, BLD-06, BND-08) recomputed from raw outputs within 0.001 (max 9.1e-05) | `audit/results/rerun_v1/comparison.json` (`summary.all`) | the VM on the second laptop |
| all 14 certificates verify (0 mismatches) | `../_w2_transfer/verify2_*.json` | VM |
| 53 of 55 tests pass | `../_w2_transfer/tests_{core,l0_trace,report}.json` (+ `tests_core2.json` after the last fix) | VM. `test_audit_rerun.py` was run as its commands (rerun + verify), not as a test; its live-PC test skips without causal-learn |
| PC and GES live through the adapter reproduce the stored AB-01 graphs (6 of 6 files each) | not on disk (W2's cloud workspace) | W2's workspace with causal-learn 0.1.4.8, ges 1.1.0 |
| the rebase's facts (stage attribution, grid counts, scenario overlap, cycle-step counts, causaliq probabilities) | `python3 audit/docs/checks/rebase_facts.py` recomputes them | run it to confirm the ground has not moved |

## 4. The green gate (from W1's doc, section 4) and its state
| Item | State |
|---|---|
| Windows test run `py -3 tests\run_tests.py --out <outside> --pattern test_audit_*.py` | **not done** (Uzair) |
| `comparison.json` all-pass within 0.001 | met (VM); after C1 it must be met again in the new layout |
| every certificate verifies | met (VM); re-check after C1 |
| W5 adopts the protocol | **not done**. W2 proposes v1.1 first (rebase section 5), so the gate becomes "v1.1 adopted" |
| commit; `tracker/verify.py --repin DLV-07`; `tracker/snapshot.py` last | **not done** (Uzair) |
Only when green: write `audit/results/rerun_v1/port_map.json` (rebase section 6, W1 section 4). Never edit `docs/paper/q1/`.

## 5. Where the design stands (summary of the rebase; the rebase is authoritative)
- Coverage: 210 cells (15 kinds x 14 audits). 79 measured (30 fire, 43 clear, 6 inconclusive), about 75 not applicable by
  capability, about 34 free to close, about 20 need spend, 2-3 need W3. Coverage (measured or not applicable) is about 73%;
  the free wave would take it to about 90%.
- Proposed v1.1 changes: V1 `not_applicable` verdict; V2 rounds; V3 version comparisons; V4 label provenance (external
  pre-registrations: P9 -> K04, P10 -> K07, M3 -> K11); V5 verdict margin and seed fragility; V6 L3-lite per-edge provenance;
  V7 validation battery of planted faults (measures the auditor); V8 q1s2 linked to CausalArena intervention targets; V9 a
  common battery for all five systems (spend; deferred).
- The paper contract to freeze (C1):
  - folders are `rerun_v1/<audit name exactly>/`;
  - findings are selected by `[id=K04]` (`kind` is the name, e.g. `name_reliance`);
  - certificate findings mirror report findings, with `effect`, `verdict`, `label`, `label_rule`, `margin`;
  - the numbers block is `{value, unit, source{file, sha256, pointer}, derivation}`.
- Planned bundles (all free): C1 contract + V1/V4/V5; C2 rounds + version comparisons; C3 free gap closures; C4
  validation battery; C5 L3-lite. Must-shows are in rebase section 8.
- Notes already given to W1 (in their doc, section 2a):
  - the 0.584 -> 0.321 loss is in the bootstrap step, not the LLM review;
  - the name-reliance sentence pools unlike measurements;
  - MATMCD's K07 interval touches 0;
  - M3 vs K11 labels;
  - the `[id=K04]` selector.

## 6. Open decisions (defaults in brackets; none taken yet by Uzair)
- W2-5 propose v1.1 to W5 before adoption [yes].
- W2-6 the paper contract of rebase section 6 [yes].
- W2-7 build the validation battery this quarter [yes].
- W2-8 a common battery across all five systems [defer: spend, ask with a cost].
- W2-9 the 6 Nov checkpoint stays on the pre-package sources [yes].
Decisions taken earlier (by default, reversible):
- W2-1: the package lives inside `audit/` beside the B5 checker.
- W2-3: the export allowlist is behind `--with-audit`, off.
- W2-4: the sealed seed store is outside DSC 180A.

## 7. Lessons from the build (each became a rule; keep them)
1. The expectation rule seeds with the name of the file the system READ: GIES reads the `obs_int` twin. Using the item name
   moved F1 by 0.0016.
2. One Causal-Copilot run failed with `OSError [Errno 5]` (the Windows Docker bind mount). That is `host_error`, not a crash;
   the arm's rerun is the record, and the failed run is a replicate.
3. A method runner's `TimeoutError` (600 s cap) is `aborted_cap`, not a crash.
4. Causal-Copilot artifacts hold causal-learn objects. They are loaded by a restricted unpickler (named builtins and NumPy
   reconstructors only; `eval` is refused), so no pickled code runs and no Causal-Copilot environment is needed.
5. Refinement v2 (branch `bld-06-refinement-v2`) records no stage artifacts, so its L2 trace is S0 -> final only.
6. A skip guard must test for the data a test actually needs (artifacts), not a folder that a reduced export also has.
7. The VM has NumPy only (no SciPy, no causal-learn). Live PC/GES and the live-PC test run on Windows or a container.

## 8. Things that must not happen
- No git writes; no API spend; no `cc.ps1`; never open `../Causal-Copilot/.env`.
- No edits to `docs/paper/q1/` (W1), the tracker or tickets (W5), `WAVE_STATE.md` (W5), or the B5 modules.
- Don't rename `audit/results/rerun_v1/` folders except as the C1 bundle, and only together with the paper contract.
- Don't write `port_map.json` before the gate is green.
