# W2: audit protocol v1 and the `audit` package (30 Oct 2026)

Tickets: DLV-08 (A2 protocol), DLV-09 (A3 package), DLV-10 (A4 results). Inputs: program-v3-2026-10-29 section 2,
w5-restart-2026-10-30, cc-research `harness/`, `score/`, `analysis/cc_graph.py`, `harness/agents/`, `analysis/ab06_*`,
`analysis/partial_stages.py`, `analysis/bld06_live_compare.py`, `analysis/score_record.py`, `tools/export_q1.py`, the Q1 repo.

**Status of this doc:** protocol v1 is a shared contract (program v3, failure mode 5), so it is a *proposal to W5*. The package
is built against it; W5 adopts it into the program doc or sends changes back.
**Update 31 Oct:** built. Section 1 is superseded by `cc-research/audit/PROTOCOL.md` (v1.0), which adds regimes `K`/`none`,
the `host_error` status and replicates, the seed-by-file-read rule, and which arm judges K02/K10/K12/K15. Build record and
results: `claude/audit-package-build-2026-10-31.md`.

---

## 0. What exists, and one conflict
| Piece | Where | Reused as |
|---|---|---|
| Agent runner (shuffle, names map, counting LLM gate, replay of recorded answers, cost) | `harness/agent_probe.py`, `probe_llm.py`, `probe_io.py`, `agents/*.py` | live and replay mode of the four agent adapters |
| Causal-Copilot recorder (observation-only hooks, state snapshots, artifacts) | `harness/cc_trace.py`, `run_traced.py` | live mode and the L2 source for Causal-Copilot |
| Scorers | `score/graph.py` (expectation-rule F1, S/c/q/a, CPDAG), `score/dv.py` (DV-1), `score/paired.py` (cluster bootstrap), `harness/probe_io.score_graph`, `analysis/cc_graph.score` | L0 metrics, **called, never re-implemented** |
| Stage reconstruction S0→S3 | `analysis/lineage.py` step functions, `analysis/partial_stages.py` | Causal-Copilot L2 |
| Score contract (regimes D / D+I / D+K / D+I+K, controls, orientation rule) | `analysis/score_record.py` | the regime axis of protocol v1 |
| Stored results to match | `analysis/results/{ab06, ab06_cc, stability_s2, fork, rescore_v2, decision_value_v2, methods}` | the 0.001 gates |

**Conflict: `cc-research/audit/` already exists.** It holds the B5 claim-checking adapter (BLD-15: `adapters.py`, `rca.py`,
`run_adapters.py`, `export_cc_stages.py`), imported by `analysis/b2_generator.py`, `intervention_audit.py`,
`sortability_audit.py`, `site/registry.py`, `tracker/*`. Decision (default taken, reversible):
- the existing modules stay byte-identical; the new package lives in subpackages beside them (`audit/core`, `audit/systems`, ...);
- B5's five violation classes become the **evidence-row types** of finding kinds K07 and K13 (one implementation, not two);
- `audit/__init__.py` gets a docstring-only patch through `jobs/patches/` listing both halves.
- **For W5:** BLD-15 sits under BLD (Q2), but its code is auditor logic (it checks other agents' claims). Suggest re-homing it
  under DLV-09 or linking it `implements DLV-09`.

---

## 1. Protocol v1

### 1.1 Units
- **Item**: one dataset with its reference graph (a battery entry).
- **Arm**: one control setting of an item (names real / neutral / swapped; columns shuffled or released; path opaque or plain;
  sample size; noise; knowledge supplier).
- **Run**: one system on one arm of one item. Status is typed: `ok`, `failed` (the system's fault), `aborted_cap`,
  `aborted_quota`, `interrupted` (infrastructure: excluded from scores and counted, never a crash).
- **Audit**: one system x one battery x a set of levels. Produces findings, a report and a certificate.
- **Finding**: a typed, system-level statement: kind, control, effect with interval, pre-registered threshold, verdict,
  evidence files. Per-edge rows (B5's violation classes) sit under a finding as evidence.

### 1.2 Regimes (what the system was offered)
Reuses the score contract: `D`, `D+I`, `D+K`, `D+I+K`, plus `none` for a names-only system shown neutral names (it is offered
no information channel at all; its score is a floor, not a result). The K channel carries a **k_source**:
`names_real`, `names_swapped` (wrong supplier), `oracle` (true order or tiers), `wrong_supplier` (a planted wrong order),
`declared` (user tiers). Neutral names close the K channel.
- **Rule R1.** A *score* is compared only within one regime and one k_source.
- **Rule R2.** A *control* is a paired difference across arms of the same items and is reported as a finding, never ranked.
  (Real minus swapped is a control; a table that ranks a D system against a D+K system is refused by the report builder.)

### 1.3 Truth tiers (what the reference is)
| Tier | Meaning | Examples | Allowed metric word |
|---|---|---|---|
| T1 exact | the graph the data were simulated from | CausalArena, `suite_q1s2/_reference/*_by_data.npy`, our generators | accuracy |
| T2 contested | a published consensus that the data may not follow | Sachs | agreement |
| T3 provenance-only | a reference linked to the data by documentation only | literature graphs for real tables | agreement |
| T4 mismatched | a reference known *not* to describe the data, kept as a diagnostic | the label-implied graph under swapped names (`*_swapped_by_label.npy`) | only inside a control (K11) |
- **Rule R3.** The metric layer names every number `accuracy.*` or `agreement.*` from the item's tier and refuses to pool items
  of different tiers. T4 is never scored on its own.

### 1.4 Metrics (L0), each with its rule in its name
| Name | Rule | Implementation (called) | Matches |
|---|---|---|---|
| `dir_f1@expect` (precision, recall) | undecided pairs oriented at random, generator seeded crc32(file name), pairs in sorted order | `score.graph.directed_f1` (= `probe_io.score_graph["random"]`) | AB-06, AB-01 |
| `dir_f1@committed` | only committed marks count; a both-ways mark counts both | `cc_graph.score` (`dir_f1`) | BLD-06, BND-08 |
| `adj_f1` | unordered adjacency, any mark | `cc_graph.score` (`adj_f1`) / `score.graph.coords` (`S`) | BLD-06, AB-01 |
| `S`, `c`, `q`, `a` | skeleton F1, commit rate, commit accuracy, direction accuracy | `score.graph.coords` | AB-01 |
| `dv1.precision`, `dv1.coverage` | "if I set T, does Y move?" on released targets, pooled | `score.dv` / `decision_value_v2.claims` | AB-04, AB-06 |
| `cost.usd`, `cost.calls`, `cost.seconds` | served prices from the run's own record | run summary | AB-06, BLD-06 |
| `completion` | ok runs / runs (infrastructure statuses excluded and counted) | run statuses | all |
- **Rule R4.** Every mean states its run set: `completed-only` or `delivered` (a failed run counts as an empty graph). Both are
  reported whenever completion < 1 (BLD-06's 22 of 30 is the reason).

### 1.5 Finding kinds: the closed list (v1)
Every kind has one statistic, one threshold, a minimum number of units, and the interval rule: scenario-cluster bootstrap,
B = 2000, seed 20261014, percentile 95% (`score.paired`). Verdicts are typed: `fires`, `clear`, `inconclusive` (fewer units
than the minimum, or the interval straddles the threshold where the rule uses it), `not_checkable` (the system lacks the
capability, e.g. no data-only variant), `not_run` (control defined, not executed in this audit).

| ID | Kind | Level | Control (comparison) | Statistic | Fires when | Min units | Origin |
|---|---|---|---|---|---|---|---|
| K01 | `crash` | L0 (L2 adds where) | none | failed runs / runs, Wilson 95% | at least 1 failed run | 1 run | BLD-06 |
| K02 | `no_better_than_null` | L0 | system vs the empty graph on the same files | paired DV-1 precision difference | interval lower end <= 0 | 5 clusters | AB-04 floor |
| K03 | `cost_outlier` | L0 | across systems of the round, same battery and regime | USD per ok run / median of the round | ratio >= 10 | 3 systems | new |
| K04 | `name_reliance` | L1 | names real vs swapped, same data | paired mean dF1 = F1(real) - F1(swapped) | point >= 0.10 (P9) | 5 pairs | P9, pre-registered 14 Oct |
| K05 | `wrong_knowledge_harm` | L1 | names neutral vs swapped | paired mean F1(neutral) - F1(swapped) | point >= 0.05 and lower end > 0 | 5 pairs | new |
| K06 | `layout_reliance` | L1 | columns released vs shuffled; path plain vs opaque | paired mean of the metric | abs(point) >= 0.05 and interval excludes 0 | 5 clusters | AB-01 |
| K07 | `knowledge_degrades_data` | L1 | final vs the system's own data-only variant (black box: the knowledge-off arm) | pooled DV-1 precision final - data-only | point < 0 (P10) | 5 items | P10, pre-registered 14 Oct; rows: B5 I5/I3 classes |
| K08 | `robustness_drop` | L1 | sample size / noise / mechanism family | paired mean dF1 (base - transformed) | point >= 0.10 and lower end > 0 | 5 pairs | new |
| K09 | `knowledge_ignored` | L1 | oracle supplier vs none | paired mean gain | point < 0.05 | 5 pairs | new |
| K10 | `stage_deletes_supported_links` | L2 | a stage's output vs its input | paired mean adj F1 (out - in), per stage | point <= -0.10 and upper end < 0 | 5 runs | BLD-06, BND-08 M1 |
| K11 | `stage_follows_names` | L2 | swapped arm: a stage's changed pairs vs the T1 reference and the T4 label reference | count agreeing with labels only vs data only | data-only count below the binomial(0.5) 5% quantile of the decided pairs | 20 decided pairs | BND-08 M3 |
| K12 | `stage_flips_data_direction` | L2 | a stage's input vs output on true adjacencies the input had committed | right->wrong flips minus wrong->right flips | net > 0, sign test p < 0.05 | 10 flips | new; rows: B5 I3 |
| K13 | `unsourced_claims` | L3-lite | none | committed arrows whose source the system does not expose / committed arrows | share > 0 for a system that declares provenance | 1 run | B5 G4 |
| K14 | `overconfident` | calibration | stated confidence vs realised precision | ECE (10 bins) and mean(conf) - precision | ECE > 0.05 or gap > 0.05 | 100 claims | new |
| K15 | `never_abstains` | L0 | none | DV-1 coverage, DV-1 precision | coverage >= 0.99 and precision < 0.90 | 5 items | new |

**Pre-registration honesty.** K04 and K07 carry the P9/P10 rules hashed on 14 Oct (`plans/ab06_prereg.json`) before the AB-06
grid ran. Every other kind's threshold is registered on 30 Oct, *after* the existing results were known. In the rerun these
kinds are labelled `exploratory (threshold set after the data)`; they become confirmatory only on systems or rounds run
after the thresholds file was hashed. The report prints this label per finding.

**Thresholds file:** `audit/protocol/thresholds_v1.json`, hashed (sha256 of the canonical JSON) into every report and
certificate. Changing a threshold makes v1.1; a report names the version it was judged under.

### 1.6 Batteries
- **Manifest.** `{battery_id, version, visibility, items:[{item_id, cluster, family, files:{role: {path, sha256}},
  reference:{path or key, sha256, tier}, n, d, arms}], generator?:{code_path, code_sha256, params}}`. The battery hash is the
  sha256 of the manifest's canonical JSON (sorted keys, no whitespace). Every run record carries it.
- **Development batteries (public; anyone may tune on them).** v1 registers the ones the existing audits used:
  - `ca-ab06` (10 CausalArena semantic scenarios, rep000, obs_only plus obs_int for released targets; T1);
  - `q1s2` (the same family of 10 scenarios x real / neutral / swapped as CSVs with opaque paths; T1 by data, T4 by label);
  - `ca-semantic`, `ca-formula` (all public obs_only files; the kernel's own dev/test split is carried as item metadata).
- **Sealed battery (`sealed-v1`).** Generated by a seeded generator (the AB-08 generator, `analysis/b2_generator.py`, wrapped
  so its draws come from a secret seed). Commit, then reveal per read:
  - the seed file lives **outside the DSC 180A folder** (default `%USERPROFILE%\.causal-audit\sealed\`), because every chat of
    this project can read that folder, W3 included;
  - the public manifest holds the generator's code hash and parameters, the seed file's sha256, and each generated item's
    sha256 (none of which reveal a graph);
  - `audit sealed-read` regenerates the items into a temporary folder outside the shared folder, checks every item hash, runs
    the system, writes **aggregates and verdicts only** (two decimals) to the shared folder, and keeps per-item results in the
    seed store;
  - `audit/sealed/READS.jsonl` (public) logs each read: system identity, version, battery hash, UTC, report hash. A second
    read by the same (system, version) is refused. After 5 reads the battery rotates to `sealed-v2` with new seeds.
  - Building the sealed battery is an M step (Uzair runs the generator on his machine); the agent never sees the seeds.

### 1.7 The certificate
`certificate.json`, canonical JSON, with its own sha256 in `certificate.sha256`:
- `protocol`: version, thresholds sha256, kinds list sha256;
- `system`: adapter name and file sha256, system repo commit (pinned and observed), served model snapshots, image id when
  Docker ran it, capabilities declared;
- `battery`: id, version, hash, visibility;
- `runs`: per run, item, arm, status, input sha256 (data as shown), output sha256 (graph canonical form), cost;
- `numbers`: every number in the report as `{value, unit, source: {file, sha256, pointer}, derivation: {function, args}}`;
- `findings`: kind, verdict, effect, threshold, label (confirmatory / exploratory);
- `environment`: python, numpy, platform, CPU flags, BLAS family;
- `rerun`: the one command that recomputes the report from the evidence.
`audit verify CERT` recomputes every number from its evidence and compares (exact for counts; 1e-9 on the same host; 0.001
across hosts, the CAP-11 lesson).

---

## 2. The adapter interface, designed against seven systems

### 2.1 What each system needs and gives (the design table)
| | PC | GES | MATMCD | Vashishtha et al. | PyWhy-LLM | causaliq | Causal-Copilot |
|---|---|---|---|---|---|---|---|
| Data in | matrix | matrix | matrix | matrix | **none** | **none** | **CSV file in a dataset folder** |
| Names in | no | no | yes | yes | yes | yes | yes (CSV header) |
| Context text | no | no | theme | no | analysis_context | domain | query text |
| Interventions | no | no (GIES yes) | no | no | no | no | not in our use |
| Marks out | ->, -- | ->, -- | ->, --, <-> | ->, -- | -> only | ->, -- (PDG) | CC codes 1-7 incl. PAG marks |
| Per-edge source | n/a (data) | n/a | yes (C matrix) | yes | all llm | all llm | no (L2 recovers it) |
| Confidence | no | no | no | no | no | **PDG probabilities** | no |
| Data-only variant | itself | itself | `pc_only_initial` | `pc_only` | none | none | S0 (the algorithm's graph) |
| Glass box (L2) | causal-learn phases | GES phases | ConstrainAgent + PC | PC + order | suggester calls | one call | recorder, stages S0-S4 |
| Modes | live (causal-learn), recorded (`analysis/results/methods`) | same | live, replay, recorded | same | same | same | live (Docker, `cc.ps1`), recorded (`runs/<id>`) |
| Cost | CPU | CPU | LLM (~$0.3/run) | LLM | LLM | LLM (1 call) | LLM ($0.16-0.42/run) |
| Determinism | deterministic | deterministic | stochastic (LLM) | stochastic | stochastic | stochastic | stochastic |

What the table forced into the interface (each would be a CC-specific leak otherwise):
1. Inputs are **offered channels**, and an adapter declares which it takes; the harness derives the regime from offered x taken
   (PyWhy-LLM under neutral names gets regime `none`).
2. Data are handed over as a matrix *and* an opaque file label; an adapter that needs a file (Causal-Copilot) writes it under
   that label, so the path control applies to every system the same way.
3. The output graph is a **typed mark set**, not an edge list: directed, undirected, bidirected, and PAG marks, so CC codes 4-7
   and causaliq's PDG states survive to the report (the metrics map them by stated rules).
4. Source, confidence and variants are optional, declared outputs; findings that need them return `not_checkable`.
5. Three modes. `recorded` reads a past run, so the existing audits rerun with no spend; `replay` re-executes with recorded
   model answers (free, needs the system's environment); `live` spends and refuses to start without caps and `--allow-spend`.
6. The harness, not the adapter, owns the column shuffle and maps graphs back (the AB-05 rule: the system never sees the true
   order); adapters see shown positions only.

### 2.2 The interface (frozen at v1 after the B1 conformance tests pass)
```python
@dataclass(frozen=True)
class Capabilities:
    takes: frozenset          # subset of {"data", "names", "context", "interventions", "knowledge"}
    marks: frozenset          # subset of {"->", "--", "<->", "o->", "o-o", "o-", "~"}
    edge_source: bool         # labels each committed arrow (data / knowledge / ...)
    confidence: bool          # a probability per claim
    variants: dict            # role -> variant name, e.g. {"data_only": "pc_only_initial"}
    glass_box: dict | None    # {"entry": "module:function", "stages": [...]} for L2
    modes: frozenset          # subset of {"live", "replay", "recorded"}
    cost: str                 # "cpu" | "llm"

@dataclass
class Presented:              # what the system may see, in SHOWN order
    data: "ndarray | None"; names: list; context: str | None; file_label: str
    interventions: dict | None; knowledge: dict | None; seed: int

@dataclass
class RunResult:              # in SHOWN positions; the harness maps back
    status: str; graph: Graph | None; variants: dict; edge_source: dict; confidence: dict
    cost: dict; failure: dict | None; stages: list | None; notes: dict

class Adapter:
    name: str; capabilities: Capabilities
    def identity(self) -> dict                         # code sha256, repo commit, model
    def run(self, p: Presented, budget, out_dir) -> RunResult        # live / replay
    def recorded(self, item, arm, ref) -> RunResult                  # read a past run (original positions)
```
`Graph(n, directed, undirected, bidirected, partial)` with converters `from_cc_matrix` (cc_graph's convention: M[i, j] = 1
means j -> i), `from_probe_result` (result.json over original indices), `from_method_row` (`directed_edges`,
`undecided_pairs`), and a canonical form for hashing. Undecided = undirected plus every mark that does not commit a direction.

### 2.3 Conformance (the gate that freezes the interface)
Every adapter passes, in recorded mode, a shared suite: index round-trip under a shuffle; a planted oracle system scores
`dir_f1@expect = 1`; a planted reversed system scores 0; marks it does not declare never appear; a declared variant is present
in every ok run; identity is stable across two calls.

---

## 3. Package architecture
```
audit/                       (existing B5 modules unchanged: adapters.py rca.py run_adapters.py export_cc_stages.py)
  PROTOCOL.md                protocol v1, the human spec (this doc's section 1)
  protocol/                  kinds.py (the closed list as data), thresholds_v1.json (hashed), regimes.py, tiers.py
  core/                      graph.py, adapter.py (interface above), battery.py (manifests, hashing, sealed commit and
                             read log), evidence.py (numbers with sources), runs.py (run records, statuses), canon.py
  metrics/l0.py              L0, delegating to score.graph / score.dv / cc_graph / decision_value_v2 truth
  controls/                  transforms.py (column order, path label, names, sample size, noise, knowledge supplier;
                             pure and seeded), effects.py (paired differences, cluster bootstrap), l1.py (K04-K09)
  trace/                     recorder.py (generic observation-only hooks for Python entry points), stages.py (per-edge
                             lineage across stages; K10-K12), cc_stages.py (Causal-Copilot S0-S3 from recorded artifacts)
  systems/                   pc.py ges.py gies.py matmcd.py vashishtha.py pywhyllm.py causaliq.py causal_copilot.py
  findings.py                evaluate kinds -> typed findings
  report/                    build.py (report.json, report.md), certificate.py (build, hash, verify)
  rerun/                     existing.py: AB-06, AB-01, AB-04, BLD-06, BND-08 through the package; comparison table
  __main__.py                python -m audit systems | battery | run | report | verify | rerun
tests/test_audit_*.py        unittest, NumPy only (runs in the VM and in CI)
```
Dependency rule: `audit` imports `score/`, `analysis/cc_graph.py`, `analysis/lineage.py` (step functions),
`analysis/decision_value_v2.py`, `harness/probe_io.py`; it never imports agent packages at module level (live adapters import
them inside `run`).

---

## 4. Bundles (each verifiable in one run; classes F free / H heavy / L live / M manual)
| # | Bundle | Builds | One system end to end | Must show |
|---|---|---|---|---|
| B1 | Adapter interface + L0 | core/, protocol/ (data), metrics/l0.py, systems/* recorded mode, conformance suite | MATMCD on `ca-ab06`, recorded, L0 | tests pass; conformance for all 7 adapters; L0 per agent and arm equals `ab06.json` (f1_mean, dv1_precision, dv1_coverage); PC / GES / GIES S, c, q, a, F1 equal `rescore_v2.json`; DV-1 equals `decision_value_v2.json`; max abs diff <= 0.001 |
| B2 | L1 controls | controls/, K04-K09 | MATMCD names + data-only floor; PC layout | tests (transform invariants: data bytes identical across name arms, perm bijection, truth mapped); name reliance per system equals `ab06.json` incl. Causal-Copilot gpt-4o and gpt-4o-mini; P9 and P10 verdicts equal; AB-01 released - shuffled differences equal; intervals reported (new) |
| B3 | L2 tracing (Python systems) | trace/, K10-K12, CC stage extractor; agent two-stage traces from recorded variants | Causal-Copilot on `q1s2` (BND-08 runs) | tests (recorder is observation-only: hooked output == unhooked on a toy pipeline; crash localised to its stage); S0/S1/S3 adj and dir F1 per run equal `partial_stages.json`; crashes 6 cyclic, 0 completed; M3 81 / 20 / 74 of 101; M1 19 of 23; BLD-06 main S0 0.584 -> final 0.321 |
| B4 | Reports and certificates | findings.py, report/, sealed commit and read-log code (no seeds) | MATMCD full report + certificate | tests (hash determinism; tampered number caught by verify; every number has a source; cross-regime ranking refused; second sealed read refused); `audit verify` passes on the MATMCD certificate |
| B5 | Rerun the existing audits | rerun/existing.py, reports for 7 systems + GIES | all | one comparison table, every stored number vs recomputed, max abs diff <= 0.001; no API spend (all recorded) |

Not in this wave, as run-sheet jobs: live PC/GES through causal-learn (H, Uzair's machine: the VM has no SciPy); L2 hooks on the
four agents under replay (H, probe images, $0); sealed battery build (M). Each is written but not run.

## 5. Failure modes, named before they happen
1. **Index mapping bug** (shown vs original positions): silent wrong scores. Conformance suite, planted oracle and reversed systems.
2. **Orientation-rule mix-up** (expectation vs committed): metric names carry the rule; the comparison table checks the rule
   field of the stored number.
3. **Tier misuse** (contested reference called accuracy): R3, enforced in metrics.
4. **Cross-regime ranking**: R1, enforced in the report builder.
5. **Infrastructure counted as crash** (quota, caps): typed statuses; K01 excludes them and counts them.
6. **Selection by completion** (CC 22 of 30): R4, both run sets.
7. **Two scorers drifting**: the package calls `score/` and `cc_graph`; tests compare on random graphs.
8. **Thresholds fitted after the data**: hashed thresholds, `exploratory` labels for kinds set after the existing results.
9. **Sealed seeds visible to B**: seeds outside the shared folder; agent never reads them.
10. **Adaptive overfitting through repeated sealed reads**: one read per version, two-decimal aggregates, rotation after 5.
11. **Hooks change behaviour**: observation-only contract and a toy-pipeline equality test.
12. **Host float differences**: environment in the certificate; cross-host tolerance 0.001.
13. **Interface overfits Causal-Copilot**: the seven-system table above; conformance on all seven before freezing.
14. **Names-only systems under neutral names**: regime `none`; excluded from K05's neutral leg as not_checkable.
15. **Rerun matches only because it reads the stored summary**: the rerun reads raw run outputs (result.json, state files,
    artifacts, method rows) and never the stored aggregate it is compared with, except Causal-Copilot's partial_stages rows in
    B2, which B3 then rebuilds from artifacts.

## 6. Decisions (defaults in brackets)
- **W2-1** New package inside the existing `audit/`, B5 modules untouched [yes].
- **W2-2** Protocol v1 as section 1, to W5 for adoption [yes].
- **W2-3** Q1 export: the audit package joins the allowlist behind `--with-audit`, off until W1's 6 Nov export is done, so the
  checkpoint repo does not change under W1 [yes].
- **W2-4** Sealed seed store outside DSC 180A, `%USERPROFILE%\.causal-audit\sealed\` [yes].
