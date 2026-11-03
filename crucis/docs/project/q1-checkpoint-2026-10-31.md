# W1: the Q1 checkpoint paper, and how the audit package plugs into it (31 Oct 2026)

Tickets: DLV-05 (checkpoint, 6 Nov), DLV-06 (final, 4 Dec), DLV-07 (Q1 repo), DLV-08..11 (W2's protocol, package, results,
benchmark appendix). Owner: W1 (the paper chat). Readers: W2 (audit package), W5 (tickets, contract).
Nothing is committed; Uzair commits (`docs/commit_msgs/q1_checkpoint_cc-research.txt`).

## 1. What exists (cc-research, second laptop)
| Path | What it is |
|---|---|
| `docs/paper/q1/report.tex` | the checkpoint in the course's Overleaf template: title, abstract, introduction, prior work (label `sec:prior`), data, code link, appendix A |
| `docs/paper/q1/build/report.pdf` | compiled PDF, 15 pages |
| `docs/paper/q1/numbers.json` | **the number registry**: 78 entries, each `{key, file, ptr, fmt}` or `{key, op, args, fmt}` |
| `docs/paper/q1/build_numbers.py` | reads the registry against the result files; writes `numbers.tex`, `numbers_table.tex` (appendix A), `numbers.lock.json` (value, source sha256, git state); `--check` fails on any drift |
| `docs/paper/q1/lint_report.py` | fails on any numeral not printed through `\nm{key}`, any number word from "two" up, any prior-work sentence without `\cite` or `\ours`, any cited key without a checked claim |
| `docs/paper/q1/lit_claims.json`, `verify/`, `reference.bib`, `data_facts.md` | 38 literature claims checked by agents that did not write them (23 confirmed, 15 corrected and applied), 9 data facts, 42 bib entries |
| `docs/paper/q1/DESIGN.md` | axes, binding times, failure modes, bundles |
| `docs/paper/q1/w5_requests.md` | open items for W5 and W2 |
| `docs/q1/checkpoint_skeleton.md` | index to the above, plus the final-report outline (re-cut via patch w1-01; BND-13 repinned) |

Title: "Auditing Causal-Discovery Systems: An Open Protocol and a First Audit of the Field".

## 2. What the paper currently says that the package must back
Every number below currently comes from the **pre-package** result files. When the package is green, each one moves to a
package output (section 4). Keys are `numbers.json` keys.

| Claim in the paper | Keys | Current source | Package counterpart (W2 to confirm) |
|---|---|---|---|
| Swapping names costs 3 of 4 entered systems at least 0.10 directed F1 (causaliq 0.251, Causal-Copilot 0.167, MATMCD 0.122; Vashishtha 0.020) | `ab06.p9.*`, `ab06.*.drop`, `ab06.systems` | `analysis/results/ab06/ab06.json`, `plans/ab06_prereg.json` | K04 per audit in `audit/results/rerun_v1/<audit>/certificate.json` |
| MATMCD below its own data-only graph (DV-1 0.6855 vs 0.7199) | `ab06.matmcd.dv1*` | `ab06.json` | K07, matmcd certificate |
| Inside Causal-Copilot, 81 of 101 model-set edges follow swapped labels (20 follow data) | `bnd08.m3.*` | `analysis/results/stability_s2/bnd08_summary.json` | K11, causal_copilot@bnd08 |
| Review lowers adjacency F1 0.584 → 0.321; 22 of 30 completed; 8 of 8 cycle-step entries crash | `cc.*`, `cc.cyc.*` | `analysis/results/fork/bld06_live_compare.json`, `bld06_cycles.json` | K10 and K01, causal_copilot@main |
| CausalArena: FCI gains 0.221 directed F1 from the forced-choice, index tie-break scoring; published PC 0.333 → 0.463 (maxP, shuffled) | `ab01.*` | `analysis/results/rescore_v2/leaderboard_controlled.json` | **stays a benchmark property (DLV-11, A5)**, as W2 noted: K06 is clear for PC/GES/GIES under the expectation rule. The paper already frames it as "benchmarks reward shortcuts", not as a system's layout reliance |
| CausalBench: all 4 MeanDifference rows reproduced; 0.90-0.95 of the test split's total-effect ceiling; FOR within margin of random in 3 of 4 cells | `ben13.*` | `analysis/results/ben13/summary.json` | stays (DLV-11) |
| Data shapes, tiers | `s1.*`, `s2.*`, `cb.*` | `datasets/**/MAPPING.json`, `reference_reliability/reliability.json`, `external/causalbench/*.npz.json` | could move to battery manifests (`ca-ab06`, `q1s2`) if W2 records n, d and edges there |

The introduction's protocol paragraph describes: levels L0-L2 now and L3/L4 later; finding kinds from a closed list;
pre-registered, hashed thresholds; regimes; reliability tiers exact / contested / provenance-only / mismatched; the
certificate (system identity, battery hash, every number with its source, rerun command). It must stay consistent with
`audit/PROTOCOL.md` v1.0. Known differences to reconcile at the port: v1.0 adds regimes `K` and `none`, status
`host_error`, and the "exploratory vs confirmatory" label (only K04 and K07 for the AB-06 agents are confirmatory). The
final paper must print that label beside every finding it quotes.

### 2a. W2's notes on this section (31 Oct, before any port; detail in `claude/w2-rebase-2026-10-31.md` section 7)
1. **"Review lowers adjacency F1 0.584 → 0.321" misattributes the loss.**
   - On fork main, over the 22 completed runs, the drop is almost all in the bootstrap step (S0 → S1: −0.270
     [−0.327, −0.200]), which makes no model call. The LLM review step (S1 → S2) is +0.007 [−0.027, +0.042]. KCI and the
     cycle step change nothing measurable.
   - BND-08's gpt-4o runs agree (−0.281 at the bootstrap step, −0.003 at review).
   - Suggested: "Causal-Copilot's refinement lowers adjacency F1 from 0.584 to 0.321; the loss is in its bootstrap step,
     not in the model's review."
   - The two means come from different run sets (S0 over 30 runs, final over 22 completed). The completed-only S0 mean is
     also 0.584, so the numbers stand; the package will cite the paired, completed-only form.
2. **The name-reliance sentence pools unlike measurements.**
   - Causal-Copilot's 0.167 is directed F1 on S3 (the graph handed to the cycle step) under the committed-marks rule, by
     family. The agents' numbers are final-graph F1 under the expectation rule, by scenario.
   - The two groups share 0 of 10 scenarios.
   - It stands as P9, which was pre-registered that way. But the text should say what Causal-Copilot's number measures, and
     that under protocol v1 its K04 is exploratory (its runs predate the 14 Oct pre-registration, which declared them
     "already measured").
3. **MATMCD below its own data-only graph.** K07 fires under P10's point rule (confirmatory), with interval
   [−0.066, 0.001]: the upper end touches zero. Print the interval, or say "below on the point estimate".
4. **81 of 101.** The counts reproduce exactly (K11), but K11's own threshold is exploratory. The pre-registered verdict is
   BND-08's M3; under the proposed v1.1 the certificate carries both rules.
5. **"8 of 8 cycle-step entries crash."** Reproduced: 8 runs enter the cycle step, all 8 crash, 0 complete.
6. **Benchmark and data keys stay**, agreed: `ab01.*`, `ben13.*` (DLV-11); `s1.*`, `s2.*`, `cb.*` (`MAPPING.json` is the
   source of record; the battery hash covers it). `ab06.p9.threshold` stays on `plans/ab06_prereg.json`: the
   pre-registration is the source of record for a threshold.
7. **The pointer example must change.** In the package, a finding's `id` is `K04` and its `kind` is `name_reliance`, so
   the selector is `[id=K04]`. The proposed frozen form is
   `audit/results/rerun_v1/<audit>/certificate.json#/body/findings/[id=K04]/effect/point`, with `verdict`, `label`,
   `label_rule` and `margin` beside it. Folder names are the audit names exactly (`causal_copilot@bnd08`). Today's
   layout (`reports/`, `@` rewritten as `_`) changes in W2's next bundle (C1), before `port_map.json` is written.
8. **Two keys need package outputs that do not exist yet.** The P9 lists and verdict (`ab06.p9.*`, `ab06.systems`) are
   round-level, and the `cc.*` / `cc.cyc.*` keys are a version comparison. W2's C2 adds `round@ca-ab06` and
   `versions@causal_copilot-bld06-vs-main` as certified outputs, so those keys get file-plus-pointer counterparts.
9. **Gate wording.** W2 proposes PROTOCOL v1.1 (an added `not_applicable` verdict, rounds, version comparisons, label
   provenance, verdict margins) before W5 adopts. The gate becomes "W5 has adopted v1.1". No kind or threshold changes.

## 3. The contract between the package and the paper
1. **A paper number is a file + JSON pointer.** The paper never computes. It reads a value the package already wrote,
   with `ops` limited to sub, div, add, len, min, max, sum, mean, count_true, count_notnull, and regex extraction from a
   pre-registered text field. Anything else is computed in the package and written to a file first.
2. **Preferred source: the certificate's `numbers` block** (`{value, unit, source: {file, sha256, pointer}, derivation}`).
   Then `audit verify` and `build_numbers.py --check` together prove the chain: raw run → certificate → paper.
3. **Stable pointers.** The paper's registry addresses findings by kind and audit name, e.g.
   `audit/results/rerun_v1/matmcd/certificate.json#/findings/[kind=K04]/effect/point`. If W2 renames an audit folder or
   reorders a list, the paper's build fails loudly (good); a selector `[k=v;k2=v2]` is supported, so lists can be addressed
   by field, not position.
4. **Tracked and clean.** Sources must be tracked in git and unchanged against the commit the paper prints; the lock
   records the state per file.
5. **Labels travel with numbers.** For each finding quoted, the registry also pulls its verdict and its
   `confirmatory`/`exploratory` label, so the text cannot drop the label.

## 4. The port (when W2 says the package is green)
Gate for "green": W2's must-show met on Uzair's Windows run (`py -3 tests\run_tests.py --out <outside> --pattern
test_audit_*.py`), `comparison.json` `summary.all.pass` true with `max_abs_diff <= 0.001`, all certificates verify, and
W5 has adopted PROTOCOL.md v1.0 (or sent changes back).

Steps:
1. **W2 writes `audit/results/rerun_v1/port_map.json`**: for each `numbers.json` key in section 2 marked as having a package
   counterpart, `{"key": ..., "file": ..., "ptr": ..., "fmt": ...}` pointing into a certificate or report; `"stays"` for the
   benchmark and data keys. W2 does not edit `docs/paper/q1/` (W1's files).
2. **W1 applies it** with a patch script: rewrite those registry entries, run `build_numbers.py` (the lock shows any value
   that changed; every change is explained or the port stops), lint, compile.
3. **W1 updates the protocol paragraph** to PROTOCOL.md v1.0 wording and adds the exploratory/confirmatory labels.
4. **DLV-07:** for the 4 Dec final, export with `--with-audit` and decide which recorded data the Q1 repo carries
   (W2-3 leaves this to W1).
5. The 6 Nov checkpoint is **not** ported: it ships on the pre-package sources (all already reproduced by the package to
   0.001 per W2's B1-B5), so the submission does not wait on the package.

## 5. Open items
- `tests/test_core.py::ScoreContract` fails on `analysis/results/refinement_r3` (W3's folder, 31 Oct).
- Program v3 section 2.3 item 1 misstates the CausalBench share (W5; details in `docs/paper/q1/w5_requests.md`).
- The template's `dsc180bibstyle.bst` is not in the repo; local builds use CTAN econ.bst. Overleaf uses the real one.
