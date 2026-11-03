# Audit protocol v1 (DLV-08)

Status: v1.0, proposed to W5 (program chat) for adoption into the program doc; the `audit` package (DLV-09) implements it.
Design and the seven-system interface table: project doc `claude/audit-package-design-2026-10-30.md`.
Machine-readable parts: `audit/protocol/kinds.py` (the closed list), `audit/protocol/thresholds_v1.json` (hashed into every
report and certificate), `audit/protocol/regimes.py`, `audit/protocol/tiers.py`.

## 1 Units
- **Item**: one dataset with its reference graph (a battery entry).
- **Arm**: one control setting of an item (names real / neutral / swapped; columns shuffled or released; path opaque or plain;
  sample size; noise; knowledge supplier).
- **Run**: one system on one arm of one item. Status is typed: `ok`, `failed` (the system's fault), `aborted_cap`,
  `aborted_quota`, `interrupted`, `host_error` (infrastructure: excluded from scores and counted, never a crash; `host_error` is
  an OSError EIO from the host, the Windows Docker bind-mount fault seen 14 Oct), `not_run` (planned, never executed).
  Repeated runs of one arm are kept as replicates; the last run is the record, and every run count includes the earlier ones.
- **Audit**: one system x one battery x a set of levels. Produces findings, a report and a certificate.
- **Finding**: a typed, system-level statement: kind, control, effect with interval, pre-registered threshold, verdict,
  evidence files. Per-edge rows (B5's violation classes) sit under a finding as evidence.

## 2 Regimes (what the system was offered)
Reuses the score contract: `D`, `D+I`, `D+K`, `D+I+K`, plus `K` (knowledge only: a names-only system shown informative
names) and `none` (a names-only system shown neutral names: offered no information channel at all; its score is a floor,
not a result). The K channel carries a **k_source**:
`names_real`, `names_swapped` (wrong supplier), `oracle` (true order or tiers), `wrong_supplier` (a planted wrong order),
`declared` (user tiers). Neutral names close the K channel.
- **Rule R1.** A *score* is compared only within one regime and one k_source.
- **Rule R2.** A *control* is a paired difference across arms of the same items and is reported as a finding, never ranked.
  (Real minus swapped is a control; a table that ranks a D system against a D+K system is refused by the report builder.)

## 3 Truth tiers (what the reference is)
| Tier | Meaning | Examples | Allowed metric word |
|---|---|---|---|
| T1 exact | the graph the data were simulated from | CausalArena, `suite_q1s2/_reference/*_by_data.npy`, our generators | accuracy |
| T2 contested | a published consensus that the data may not follow | Sachs | agreement |
| T3 provenance-only | a reference linked to the data by documentation only | literature graphs for real tables | agreement |
| T4 mismatched | a reference known *not* to describe the data, kept as a diagnostic | the label-implied graph under swapped names (`*_swapped_by_label.npy`) | only inside a control (K11) |
- **Rule R3.** The metric layer names every number `accuracy.*` or `agreement.*` from the item's tier and refuses to pool items
  of different tiers. T4 is never scored on its own.

## 4 Metrics (L0), each with its rule in its name
| Name | Rule | Implementation (called) | Matches |
|---|---|---|---|
| `dir_f1@expect` (precision, recall) | undecided pairs oriented at random, generator seeded crc32(name of the file the system read: GIES reads the obs_int twin), pairs in sorted order | `score.graph.directed_f1` (= `probe_io.score_graph["random"]`) | AB-06, AB-01 |
| `dir_f1@committed` | only committed marks count; a both-ways mark counts both | `cc_graph.score` (`dir_f1`) | BLD-06, BND-08 |
| `adj_f1` | unordered adjacency, any mark | `cc_graph.score` (`adj_f1`) / `score.graph.coords` (`S`) | BLD-06, AB-01 |
| `S`, `c`, `q`, `a` | skeleton F1, commit rate, commit accuracy, direction accuracy | `score.graph.coords` | AB-01 |
| `dv1.precision`, `dv1.coverage` | "if I set T, does Y move?" on released targets, pooled | `score.dv` / `decision_value_v2.claims` | AB-04, AB-06 |
| `cost.usd`, `cost.calls`, `cost.seconds` | served prices from the run's own record | run summary | AB-06, BLD-06 |
| `completion` | ok runs / runs (infrastructure statuses excluded and counted) | run statuses | all |
- **Rule R4.** Every mean states its run set: `completed-only` or `delivered` (a failed run counts as an empty graph). Both are
  reported whenever completion < 1 (BLD-06's 22 of 30 is the reason).

## 5 Finding kinds: the closed list (v1)
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

**Which arm judges.** K02, K10, K12 and K15 are judged on the system's own setting, the real-names arm, when the battery
has names arms; the other arms are reported beside it. K04, K05 compare arms by definition. K01 counts every run.

**Pre-registration honesty.** K04 and K07 carry the P9/P10 rules hashed on 14 Oct (`plans/ab06_prereg.json`) before the AB-06
grid ran. Every other kind's threshold is registered on 30 Oct, *after* the existing results were known. In the rerun these
kinds are labelled `exploratory (threshold set after the data)`; they become confirmatory only on systems or rounds run
after the thresholds file was hashed. The report prints this label per finding.

**Thresholds file:** `audit/protocol/thresholds_v1.json`, hashed (sha256 of the canonical JSON) into every report and
certificate. Changing a threshold makes v1.1; a report names the version it was judged under.

## 6 Batteries
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

## 7 The certificate
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
