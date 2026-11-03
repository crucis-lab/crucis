# W2 design iteration after the Codex handoff (31 Oct 2026)

Tickets: DLV-08, DLV-09, DLV-10; neighbours DLV-05/06/07/11, ADV-01, BLD-15.
Status: design only. W2-5 through W2-9 are pending; no C1-C5 build is authorized.
This is an additive discussion record, not an adopted protocol or a replacement for the rebase.
Protocol and paper-contract proposals must be carried by Uzair to W5 for adoption.

## 1. Ground checks

Read order followed: CODEX_KICKOFF, STATE, rebase, W1 checkpoint, PROTOCOL, README, audit/AGENTS,
root AGENTS, package build and design, program excerpts, then the adapter, findings, rerun and certificate code.
Uzair authorized running the read-only Python checks and tests in this chat.

All persistent check outputs are outside cc-research, under:
`C:/Users/uzair/Documents/UCSD/Fall 2026/DSC 180A/_w2_checks/2026-10-31_codex/`.
Bytecode writes were disabled. The `py` launcher is not available in the agent shell, and its WindowsApps
`python` alias did not start. The working interpreter is Codex's bundled Windows Python 3.12.14:
`C:/Users/uzair/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe`.
It has NumPy, but not SciPy, causal-learn or ges. This distinction matters for the live-PC test.

| Check | Expected | Observed |
|---|---|---|
| Stored comparison summary | 1,298 compared, all pass, max about 0.000091 | 1,298/1,298, max 0.000091483427284475 |
| Findings grid | 210 cells; 79 measured, 30 fires, 43 clear, 6 inconclusive | exact match; 58 not_run and 73 not_checkable |
| Main, completed paired stages | n=22; S0->S1 -0.270 [-0.327,-0.200]; S1->S2 +0.007 [-0.027,+0.042] | exact match at reported precision |
| Main cycle step | 8 entering, 8 crashed, 0 completed | exact match |
| Batteries | 0 shared scenarios; 10/10 q1s2 obs_int twins | exact match |
| causaliq fields | existence and orientation in responses | handoff script checks 10/10 first real-arm responses; an additional scan finds both field names in all 30/30 recorded responses across all arms |
| MATMCD certificate | 189 numbers; no mismatches; same_host=false; tolerance=0.001 | pass; hash valid, no changed raw files or verdicts |
| Code identity | 64 files; d615f61a2ce46862b9093ee7309374c825a5684dcf0d4561453a7d71444e42ae | exact match using the handoff's Linux manifest serialization |

Hash diagnosis: Git Bash's Windows sha256sum writes `HASH *path`, whereas the Linux handoff writes
`HASH  path`. The initial aggregate was `46eb8a2ee1da72185897a5ec3b5c0588b2f57317abcc029968c2237ef9959813`.
The difference starts at manifest line 1, column 66 (the binary marker), and repeats on all 64 lines.
Replacing only that marker with a space and serializing the manifest with LF reproduces the expected hash.
The source bytes were not normalized or changed. Both manifests and the comparison are saved outside the repo.
Git Bash initialization required sandbox escalation; the check remained read-only.

The first test run discovered 55 tests: 0 failures, 4 errors, 1 skip (82.641 seconds).
The four errors are denied writes/cleanup in the sandbox's temporary directory, diagnosed to:
`audit/report/build.py:102`, `audit/core/sealed.py:51`, `audit/core/sealed.py:115`, and
`audit/report/build.py:96` reached through `audit/rerun/existing.py:337`.
Affected tests are `test_report_files`, `test_commit_then_check`,
`test_one_read_per_version_and_rotation`, and `test_one_command_reproduces_and_certifies`.
The authorized unsandboxed rerun finished: **55 discovered, 54 passed, 1 skipped; 0 failures,
0 errors; OK (106.546 seconds)**. The persistent record is `tests_audit_windows.json`, with
`tests_audit_windows.log` alongside it; the failed sandbox run remains in `tests_audit.json` and its log.
The end-to-end test independently recomputed 1,298/1,298 stored comparisons with the same maximum
difference, generated all 14 reports/certificates in a temporary directory, and verified fresh certificates
for causaliq, causal_copilot@main and gies@formula. Those three verify tests plus the stored MATMCD
verification are current Windows evidence; all 14 stored certificates were previously verified on the VM.
The skip is `TestLiveBaseline.test_pc_live_equals_stored_row`, guarded by causal-learn availability
in `tests/test_audit_rerun.py:39`.

The facts script reads the saved comparison summary; the end-to-end rerun test independently rebuilds
the comparison from raw evidence. Do not conflate these two checks.

## 2. Built state and the gate

B1 supplies adapters and L0 metrics; B2 supplies L1 controls; B3 supplies L2 tracing;
B4 supplies reports/certificates and sealed-battery guards; B5 reruns the stored audits.
There are 14 stored audits. All 14 certificates verified on the prior VM, per the handoff;
MATMCD has additionally verified on Windows in this session.
The sealed-battery machinery exists; this does not mean the real sealed battery has been created.

The gate is not green. The Windows suite record now exists and is OK with the disclosed live-PC skip;
this is not evidence that the live-PC path ran on Windows. W5's adoption of the eventual protocol and
Uzair's commit/repin of DLV-07 followed by snapshot last are still outstanding.
The proposed v1.1 layout also needs regenerated comparisons and verification before the port.
No port_map.json may be written before the gate is green. W1 owns all paper edits.

## 3. Coverage: measured versus explained gaps

The exact current grid is 15 kinds times 14 audits = 210 cells.
30 fires + 43 clear + 6 inconclusive = 79 measured; 79/210 = 37.6%.
There are 210-79 = 131 remaining cells. The rebase estimates about 75 capability exclusions,
about 34 free closures, about 20 spend-dependent cells, and a few requiring W3.
Its proposed coverage measure is (measured + not_applicable)/all cells:
(79+75)/210 = 73.3%; adding 34 distinct closures would give 188/210 = 89.5%.
These are planning estimates, not a certified capability census or 90% measured coverage.

The free-work row at rebase line 64 actually lists 12+8+8+4+1+4 = 37 cells, not 34.
The categories therefore need an explicit per-cell ledger before an exact target is promised.
Plain PC and GES declare only `data` and do not use presented knowledge
(`audit/systems/pc.py:10,17`, `audit/systems/ges.py:10,16`).
K09 on these adapters is a capability exclusion unless a separately identified knowledge-capable
variant is added; simply offering an ignored oracle input should not produce a failure finding.
Costs for four versions of one system also do not supply K03's minimum of three systems.

## 4. V1-V9: options, costs and failure modes

All proposed work below is free of model calls except V9 and new LLM control runs.
Engineering time and CPU time have not been estimated numerically.

| Item | Rebase proposal and cost | Strongest alternative and cost | Failure it prevents / qualification |
|---|---|---|---|
| V1 | Add not_applicable, distinct from missing evidence. Cost: capability matrix, reason codes and verdict compatibility work. | Keep the current verdict set plus structured capability reasons. Lower migration cost, more burden on every consumer. | Stops missing controls being treated as impossible properties, or exclusions being presented as measurements. |
| V2 | Certified rounds with member certificate hashes, P9 and K03. Cost: collection schema, selectors and verification. | Keep individual certificates and certify an explicitly heterogeneous legacy summary separately. More outputs, less ambiguity. | Stops uncertified paper aggregates and falsely paired cross-system comparisons. P9 cannot be an unqualified single-battery round. |
| V3 | Certified version comparisons on the same battery/arms, including completion, cost and cycle entries. Cost: pairing rules and verification. | Separate version audits plus a certified comparison sidecar. Less protocol expansion, more linking for readers. | Stops completed-only selection, unpaired deltas and loss of adversary-loop history. A development comparison cannot close a finding; program rule 4 requires a sealed read. |
| V4 | Hash external pre-registrations and carry their exact rules beside the protocol label. Cost: provenance schema and chronology checks. | Keep only protocol labels; cite historical rules separately. Simpler schema, more paper bookkeeping. | Stops M3's status being laundered into confirmatory K11, or a historical point rule being mistaken for an interval rule. |
| V5 | Margins and five fixed bootstrap-seed verdict checks. Cost: extra CPU and boundary definitions. | Publish intervals and rule boundaries only. Less computation, seed sensitivity remains unmeasured. | Stops near-threshold verdicts looking robust. Multi-condition kinds need boundary-specific components; non-bootstrap kinds and unmeasured cells need explicit not-applicable reasons. |
| V6 | Per-edge attribution by mapped arm differences, clustered intervals. Cost: alignment, denominators, descriptive table and CPU. | Stop at system-level effects plus observed stage lineage. Less work, weaker A4 evidence. | Stops unsupported per-edge stories. Use descriptive tags, allow overlap and unresolved edges; persistence under neutral names does not prove causation by data. |
| V7 | CPU-only planted-fault battery, power versus strength and null-twin alarms, certified validation@v1. Cost: experiment design, mutants and runs. | Unit/conformance/tamper tests plus a narrower validation claim. Faster, no empirical sensitivity evidence for the kinds. | Stops a reproducible implementation being mistaken for a validated detector. The current mutant table is incomplete and needs revision below. |
| V8 | Link q1s2 to CausalArena intervention targets. Cost: validate scenario, variable, graph and target mappings; compute DV-1. | Keep DV-1 gaps until a new intervention-target battery. Less immediate work, fewer usable findings or new runs later. | Stops wrong-column intervention scoring. Targets are evaluation evidence; they must not retrospectively change what was offered to the system. |
| V9 | Defer a common five-system battery until an explicit priced plan. Cost now: bounded claims; cost later: live runs and CPU. | Run a common battery before cross-system claims. Stronger comparability now, spend and schedule risk. | Stops system differences being confused with item differences. No budget is approved; provide call/token assumptions and a cap before a spend decision. |

## 5. Points to settle before the contract freezes

### P9 and round identity

The overlap check gives 0 shared scenarios. P9 also combines agents' final expectation-rule scores with
Causal-Copilot's S3 committed-rule scores. `audit/rerun/existing.py:272-285` reconstructs this legacy aggregate.
Reproducing its pre-registered statistic is legitimate; calling it a matched comparison is not.
Proposed refinement for discussion: single-battery rounds remain strict; a separately scoped legacy P9 aggregate
references both batteries, member certificates, metrics, stages and exclusions. Final output naming goes to W5.
Alternative: one composite collection with an explicit heterogeneous scope and per-member battery identities.
Neither option authorizes pooling or ranking these scores.

### K03 already has a specification/implementation discrepancy

`audit/PROTOCOL.md:63` says USD per ok run. `audit/protocol/kinds.py:24` and
`audit/rerun/existing.py:309-318` use USD per executed run (ok or failed), pooled across arms and four agents.
The latter also mixes D+K/D and K/none; the protocol's K03 wording requires the same battery and regime.
There are only two data-plus-names and two names-only systems in the current agent set, below the
three-system minimum within either real-arm regime.
Recomputation passes do not resolve this semantic inconsistency.
Proposed refinement: preserve the legacy descriptive cost table and its denominator explicitly; have W5 settle
the valid K03 comparator set and denominator before C2. Do not silently relabel old results or move thresholds.
If valid peers are too few, say so. This may change the measured-cell census, so 90% is not a guarantee.

### V7 needs a full validation matrix

The proposed mutants explicitly target 11 kinds; K02, K03, K08 and K13 are missing.
Add a null-level predictor, a controlled cost-inflated peer in a valid round, a transformation-sensitive system,
and a system that declares provenance but omits it on a planted share of committed arrows.
K09 is oracle versus none (`audit/protocol/kinds.py:37-38`), not oracle versus wrong.
It needs a knowledge-ignoring mutant on a battery where a healthy knowledge-capable twin can gain at least 0.05.
Each mutant may affect several legitimate findings; record the expected response matrix rather than promise
that one injected mechanism can make exactly one kind fire.

The claim that every null twin stays clear is too strong under the existing rules:
no flips makes K12 inconclusive (`audit/findings.py:145-152`), and minimum sample counts also matter.
Count false alarms as fires on null twins, and report clear/inconclusive/excluded counts separately.
Use evaluable healthy twins where possible; never change a threshold merely to make validation pass.
Fix strength grids, seeds, minimum units and expected cross-effects before observing the validation outputs.
Report detection fractions and false-alarm uncertainty over independent replicates/clusters.
Success on a finite planted grid supports that grid; it does not prove universal detection at every greater strength.

### New extraction is not new data

The blanket confirmatory wording for C3 in rebase line 186 needs qualification.
New transforms run after the fixed rule can be prospective; newly parsing old calls or reconstructing old
K11 traces does not erase their original data dates. Keep the run chronology and external pre-registration
scope for every label. No automatic upgrade to confirmatory merely because the package was extended today.

## 6. Paper contract proposal (C1)

Freeze these together before any move:

1. `audit/results/rerun_v1/<audit>/{report.json,report.md,certificate.json}`; exact audit names including @.
2. Findings addressed by id, e.g. `#/body/findings/[id=K04]/effect/point` in the certificate;
   `kind` remains the descriptive name. These selectors are W1's extension, not plain positional JSON pointers.
3. Report and certificate findings mirror effect, threshold, verdict, labels/rule provenance, margin,
   measured/judged run sets, stage and reasons. Define null/absent fields for unmeasured findings.
4. Number records carry value, unit, source file/hash/pointer and derivation. The source is report.json.
   Hash report.json before building its certificate; do not create a report/certificate hash cycle.
5. Only `audit rerun` regenerates the stored release. Verification checks values, raw-file hashes and verdicts.
   Host metadata and source hashes can change; do not promise byte identity across hosts or hide allowed
   sub-0.001 numeric differences. W1's lock must expose file changes.
6. C1 dry-runs W1's selector against every registry key with a package counterpart, using an external output
   table. Benchmark/data/threshold sources that remain authoritative stay where W1 specifies.
   P9 and version-comparison pointers require C2 before the complete port can be green.

Strongest alternative: preserve the v1 folder layout and add a versioned compatibility index/sidecar schema.
It avoids immediate moves but leaves duplicate representations, more maintenance, and more possible pointer drift.
The proposed one-time migration costs regeneration and W1 coordination; it prevents unstable paths, silent
positional selection and labels becoming detached from numbers. The final contract requires W5 adoption.

Paper claims to carry to W1/W5: the -0.270 loss is bootstrap, while review is +0.007 with an interval including zero;
P9 mixes batteries/stages/scoring rules; MATMCD's K07 interval reaches +0.001 despite the P10 point-rule verdict;
81/101 is reproduced, but external M3 and protocol K11 have distinct provenance; 8/8 main cycle entries crash.
No paper file has been edited.

## 7. Decision log (no defaults accepted yet)

| Decision | Default proposed in STATE/rebase | Current state |
|---|---|---|
| W2-5 | Propose v1.1 to W5 before adoption | Pending Uzair; include the refinements above in discussion |
| W2-6 | Freeze the section-6 paper contract, exact @ folders and id selectors | Pending Uzair; settle aggregate scope and cost semantics before final pointer freeze |
| W2-7 | Build the validation battery this quarter | Pending Uzair; recommend a complete K01-K15 matrix |
| W2-8 | Defer a common five-system battery; ask later with a price/cap | Pending Uzair; no spend authorized |
| W2-9 | Keep the 6 Nov checkpoint on pre-package sources | Pending Uzair |

Earlier W2-1, W2-3 and W2-4 defaults remain as handed off. User permission to run checks is not permission to build.

## 8. Build sequence after decisions and a separate go

| Bundle | Must show |
|---|---|
| C1: contract, V1/V4/V5 | 14 regenerated audits in agreed layout; external dry-run port table resolved with W1's selector; old values within 0.001; certificates verify; all 1,298 comparisons still pass |
| C2: V2/V3 | P9 lists/verdict in an honestly scoped certified output; K03 under adopted semantics; paired BLD-06 L1-L3 points/intervals, completion, costs, cycle entries/crashes; both aggregate types verify |
| C3: free closures | Explicit per-cell before/after ledger, appropriate capability exclusions, source/target mappings, chronological labels; recompute the actual coverage rather than require an estimated 90% |
| C4: V7 | Power/strength and null alarms for every kind, minimum-unit accounting and uncertainty; each top-strength failure is flagged, not hidden |
| C5: V6 | Mapped per-edge descriptive tags and unresolved/overlap counts, denominators and cluster intervals; investigate consistency with K04/K11 without claiming that different statistics must coincide |

Every build bundle keeps stored-number comparisons within 0.001 and verifies its certificates.
Pinned/shared edits use a hash-guarded w2_NN patch; checks output outside the repo; Uzair owns git writes,
repins and snapshot last. The B5 modules, shared scoring/harness logic, W1 paper, and W5 tracker/site stay untouched.
No folder move, protocol edit, port map or implementation was made in this design session.
