# W2: the audit package, built and rerun (31 Oct 2026)

Tickets: DLV-08 (protocol), DLV-09 (package), DLV-10 (results), DLV-07 (export allowlist).
Design: `claude/audit-package-design-2026-10-30.md`. The protocol of record is now `cc-research/audit/PROTOCOL.md` (v1.0); it
differs from the design doc's section 1 in the four points of section 4 below.
Nothing is committed. Commit message: `docs/commit_msgs/w2_audit_cc-research.txt`.

## 1. What is on disk (cc-research, second laptop)
- `audit/` new subpackages beside the unchanged B5 modules: `core/ protocol/ metrics/ controls/ trace/ systems/ report/
  rerun/`, plus `__main__.py run.py collect.py findings.py PROTOCOL.md README.md`.
- `tests/test_audit_{core,l0,controls,trace,report,rerun}.py`, `tests/audit_fixtures/`.
- Patch `jobs/patches/w2_01_audit_package.py` (applied): `audit/__init__.py` docstring; `tools/export_q1.py` gains
  `ALLOW_AUDIT` behind `--with-audit`, off by default.
- `audit/results/rerun_v1/`: `comparison.json`, `comparison.md`, and one folder per audit with `report.json`, `report.md`,
  `certificate.json` (+ `.sha256`). 5.3 MB.

## 2. Must-show, per bundle
| Bundle | Tests | One system end to end | Numbers equal the existing audits (<= 0.001) |
|---|---|---|---|
| B1 adapter interface + L0 | 22 (graph converters, regimes, closed list, capabilities, conformance of all 8 adapters with a planted oracle scoring 1 and a reversed one 0) | MATMCD on `ca-ab06`, recorded | 188 of 188: AB-06 (4 agents x 3 arms), AB-01 (PC, GES, GIES: S c q a F1, both arms), AB-04 (DV-1), BLD-06 L0; max 4.9e-05 |
| B2 L1 controls | 12 (name arms leave data bytes unchanged; derangement; shuffle bijection; reference moves with columns; seeded subsample and noise; oracle and wrong suppliers; effects equal score/paired.py) | MATMCD names and data-only floor; PC layout | 55 of 55: name reliance per agent, P10 lists and verdict, AB-01 layout differences, BLD-06 paired branch - main with its intervals; max 9.1e-05 |
| B3 L2 tracing | 10 (recorder is observation-only on a toy pipeline, removes its hooks after a crash and names the failing stage; lineage change kinds; restricted unpickler runs no pickled code, `eval` included) | Causal-Copilot on `q1s2` (BND-08 runs) | 1055 of 1055: every partial_stages.py row (S0/S1/S3, by data and by label, cycle flags) for gpt-4o and gpt-4o-mini, crash counts by stage, by-role table, AB-06's Causal-Copilot rows, P9 lists and verdict, M3 81 / 20 / 74 of 101 |
| B4 reports and certificates | 9 (one finding per kind; typed verdicts; deterministic certificate; every number has a derivation; verify catches a changed number and a changed raw file; cross-regime ranking refused; seed store refused inside DSC 180A; second sealed read refused; rotation after 5) | MATMCD report + certificate, verified | `audit verify` passes on all 14 certificates on the VM (89 to 220 numbers each, 0 mismatches) |
| B5 rerun | 2 (full rerun + 3 verifies; PC live = stored row, skipped where causal-learn is absent) | all 14 audits | 1298 of 1298 in one command, on the VM, max 9.1e-05; no API spend |

Free extra check (in my workspace, causal-learn 0.1.4.8 and ges 1.1.0 installed there): PC and GES run **live** through the
adapter and the harness's shuffle give exactly the stored AB-01 graphs on 6 of 6 files each. So the live path, the shuffle
and the mapping back are right, not only the recorded readers.

## 3. What the findings say (protocol v1; F fires, c clear, i inconclusive, - not checkable, . not run)
| Audit | K01 | K02 | K03 | K04 | K05 | K06 | K07 | K08 | K09 | K10 | K11 | K12 | K13 | K14 | K15 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| matmcd | c | **F** | c | **F** | c | . | **F** | . | . | c | - | c | c | - | **F** |
| vashishtha | c | c | c | c | i | . | c | . | . | c | - | i | c | - | **F** |
| pywhyllm | **F** | **F** | c | i | - | . | - | . | . | - | - | - | c | - | **F** |
| causaliq | c | c | c | **F** | - | . | - | . | . | - | - | - | c | - | **F** |
| causal_copilot@bnd08 (gpt-4o) | **F** | - | . | **F** | **F** | . | - | . | . | **F** | **F** | i | - | - | - |
| causal_copilot@ab06cc (gpt-4o-mini) | **F** | - | . | c | c | . | - | . | . | **F** | **F** | **F** | - | - | - |
| causal_copilot@main (fork main) | **F** | - | . | **F** | **F** | . | - | . | . | **F** | **F** | i | - | - | - |
| causal_copilot@bld06 (refinement v2) | c | - | . | c | c | . | - | . | . | c | - | i | - | - | - |
| pc@semantic, pc@formula | **F** | c | . | . | . | c | - | . | . | - | - | - | - | - | c |
| ges@semantic, ges@formula | **F** | c | . | . | . | c | - | . | . | - | - | - | - | - | c |
| gies@semantic, gies@formula | c | c | . | . | . | c | - | . | . | - | - | - | - | - | **F** |

Read with care:
- **Only K04 and K07 are confirmatory**, and only for the AB-06 agents (P9/P10, hashed 14 Oct before the grid ran). Every
  other verdict is exploratory: its threshold was set on 30 Oct, after these runs. Causal-Copilot's K04 is exploratory too
  (its gpt-4o runs are from 11 Oct; the AB-06 pre-registration declared them "already measured").
- New numbers, not in any earlier audit, with intervals:
  - K02: on real names, MATMCD's DV-1 precision is 0.015 above the empty graph's, interval [-0.009, 0.040]; PyWhy-LLM's is
    0.122 below it, interval [-0.261, 0.060]. Neither is shown better than predicting that nothing moves. Vashishtha et al.
    (+0.053) and causaliq (+0.042) are.
  - K10: Causal-Copilot's worst stage is the bootstrap step (S0 -> S1, real names): adjacency F1 -0.28, interval about
    [-0.33, -0.23]. On refinement v2 the change from S0 to the final graph is clear.
  - K15: every LLM agent commits on every pair (DV-1 coverage 1.0) at precision 0.54-0.72.
  - K01 on PC and GES: 49 of 500 semantic runs fail (10%), and 132-148 of about 500 formula runs (27-30%), from singular
    correlation matrices on exact deterministic relations (the documented jitter case). Two GES formula runs hit the
    runner's 600 s cap; they are typed `aborted_cap`, not crashes.
- K06 is clear for PC/GES/GIES under the expectation rule. AB-01's layout claim is about CausalArena's published
  "lower" orientation rule, a benchmark property (A5), not a system's reliance; W1 should cite it that way.

## 4. What building it changed in the protocol (for W5 to adopt)
1. **Regimes `K` and `none`.** A names-only system shown real or swapped names has no data channel, so it is `K`, not
   `D+K`; shown neutral names it is offered nothing (`none`). The score contract has neither.
2. **Status `host_error`.** One gpt-4o-mini run (q042 neutral, 14 Oct) failed with `OSError [Errno 5]` on the Windows
   Docker bind mount, the same fault AB-05 retried around. It is now infrastructure, never a crash, and the rerun of that
   arm is the record with the failed run kept as a replicate.
3. **The expectation rule seeds with the file the system read.** GIES reads the `obs_int` twin of an item; AB-01 seeded
   with that name, and using the item's `obs_only` name moved GIES's F1 by 0.0016. Stated in the metric's definition.
4. **Which arm judges.** K02, K10, K12 and K15 are judged on real names (the system's own setting), other arms beside.

## 5. Typed gaps (stated in every report)
- K08 and K09: transforms written and tested; not run (they need new runs).
- K11 for the four agents: no T4 label reference is registered for `ca-ab06` yet. It can be built from the recorded swap
  maps; next version.
- K14 for causaliq: it states probabilities, but `result.json` keeps only the decided graph; the probabilities are in
  `calls.jsonl`, unparsed in v1.
- L2 for refinement v2: the branch records no stage artifacts, so its trace is S0 -> final only. Adding its own hooks is
  W3's branch.
- L2 for the four agents goes from their exposed data-only variant to final. Hooks under replay are written as a
  recorder; the replay job needs the probe image (next wave, $0).
- BND-08's M1 came from a separate replay job on CausalArena dev (`jobs/bootstrap_replay_ca_dev`) and is not rerun here.
  Nor are the cycle-step model calls, which need `llm_calls.jsonl`.

## 6. For W5 (contract and tickets; W2 changes none)
- Adopt protocol v1 (`audit/PROTOCOL.md`) into the program doc, or send changes back.
- Evidence for DLV-08 (`audit/PROTOCOL.md`, `audit/protocol/*`), DLV-09 (`audit/**`, `tests/test_audit_*.py`) and DLV-10
  (`audit/results/rerun_v1/comparison.json`, with a check that `summary.all.pass` is true and `max_abs_diff <= 0.001`).
  DLV-10's criterion asks for per-system L0-L2 tables; the 14 report.md files are those.
- BLD-15 is auditor logic under BLD. Suggest a link `BLD-15 implements DLV-09`.
- Repin after review: DLV-07 (`tools/export_q1.py` changed by w2-01). BLD-15's pins are untouched.

## 7. Decisions (defaults taken; all reversible)
- W2-1: the package sits inside the existing `audit/`, B5 modules untouched [taken].
- W2-3: the export allowlist is behind `--with-audit`, off until W1's 6 Nov export is done [taken]. Turning it on adds 74
  files: code and tests only. It adds no data, so the data-dependent tests skip in the Q1 repo. Which recorded data
  the final Q1 repo should carry is a W1 / DLV-07 decision for the 4 Dec final.
- W2-4: the sealed seed store goes outside DSC 180A [taken; code refuses otherwise].

## 8. Next wave (nothing here spends)
- H, Uzair's machine: `py -3 tests\run_tests.py --out <outside> --pattern test_audit_*.py` on Windows. causal-learn is
  present in his environment, so the live-PC test runs there too.
- M, Uzair: build `sealed-v1` (`audit.core.sealed.commit("sealed-v1")` on Windows; the seeds stay in
  `%USERPROFILE%\.causal-audit\sealed`).
- Build (W2): K11 label references for `ca-ab06`; K14 from `calls.jsonl`; the replay-under-hooks job for the four agents;
  K08 / K09 runs on PC and GES (CPU only).
