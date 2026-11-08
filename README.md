# Crucis: Causal Discovery Auditing

Crucis is an independent framework for auditing causal discovery systems and
their claims. It preserves native evidence and declared uncertainty, supports
controlled comparisons, and produces traceable findings and reports.

The framework, its evaluation suite and its paper share the Crucis identity,
inspired by the *instantia crucis*: evidence that discriminates between competing
explanations. This repository is the extracted development version. Protocol,
implemented support and empirical coverage are versioned separately.

**Human and AI contributions.** Uzair Gheewala directed the research and design,
approved subsystem boundaries and implementation bundles, and retained scientific
and release decisions. AI assistance was extensive in architecture, code, tests,
debugging, documentation and review. See [AI_USE.md](AI_USE.md) for important
prompt summaries, exact excerpts, testing and historical coverage limits.

This code-checkpoint snapshot includes the public S1–S4 implementation and these
disclosure documents. Subsequent findings-subsystem development is separate.
Recorded paper results remain in the research repository; software conformance
checks are distinct from new native-system experiments and scientific validity.

## Install and inspect

```sh
git clone https://github.com/crucis-lab/crucis.git
cd crucis
python -m pip install .
python -m crucis_causal --help
python -m crucis_causal systems
python -m crucis_causal.connections --help
python -m crucis_causal.experiments --help
python -m crucis_causal.execution --help
python -m crucis_causal.measurement --help
```

Python 3.10 or newer, NumPy and jsonschema are required. Optional native PC/GES
execution uses `pip install '.[classical]'`. LLM execution retains the existing
explicit spending guards. Installation does not run an experiment.

Install from this checkout. The distribution is `crucis-causal`, the Python
namespace is `crucis_causal`, and the command is `crucis-causal`. No package-index
release has been published. Bare `pip install crucis` obtains an
[unrelated coding-agent project](https://pypi.org/project/crucis/).

## Execution and evidence lifecycle

The opt-in S3 layer provides durable execution accounts, admission and owner
controls, guarded native dispatch, capture and interaction, recovery and immutable
evidence publication. Its CLI inspects and plans from supplied bytes; live drivers,
authority and policy implementations are explicitly injected in Python. See the
[execution guide](crucis_causal/execution/README.md) for the four controlled
mechanism profiles and their scientific and operational limits. Those fixture
results do not establish universal native-system or causal-correctness coverage.

## Measurement

S4 binds a measurement question to specific output, reference and execution
evidence. Its CLI inspects snapshots and plans with explicitly supplied
dependencies and procedure declarations. Calculation, durable recording,
profile assessment and publication use the typed Python interfaces.
See the [S4 release review](crucis_causal/docs/s4/release-review-2026-11-05.md)
for the qualified procedures, recovery tests and limits.

## Evidence and research

The package imports its own code. Historical research inputs are supplied
explicitly through `CRUCIS_DATA_ROOT`, pointing at an evidence tree containing
the relevant `datasets/`, `plans/`, `runs/` and `external/` files. This setting
selects data and recorded provenance; no code from that tree is imported.
Without the setting, relative evidence paths use the current working directory.
Do not infer scientific support from an installed adapter name alone.

The `cc-research` repository retains the paper, frozen study results and
interactive research presentation. Its November 6 checkpoint keeps its existing
number sources. `provenance/extraction.json` records every copied source hash,
including the research-derived helpers now owned under `crucis_causal/_support/`.
The four historical B5 modules remain in the research repository.

## Development

```sh
python -B tools/setup_repo.py
python -B tests/run_tests.py --out ../crucis-test-report.json
```

Data-dependent tests require the declared research evidence; a skip is not a
completed reproduction. The extraction verification receipt distinguishes
offline package tests, data-backed compatibility, and installed-wheel checks.

The current development gate records the actual standalone source identity and
test outcomes:

```sh
python -m crucis_causal.dev.gates standalone --out ../crucis-check
```

Prior research-layout gate implementations are retained as historical records
under `provenance/historical-gates/`. Their original bundle-acceptance claims
are not recreated by this development check. Use installed dependencies rather
than adding external source directories to the import path.

Read `AGENTS.md` for the automatic local milestone commit policy. The GitHub home
is [crucis-lab/crucis](https://github.com/crucis-lab/crucis). Hosting code does not
itself publish a package release or a benchmark result.
Run `python -B tools/setup_repo.py` when starting in a new clone; it installs
this repository's validation hook through local Git configuration.

## Publication and attribution

Original code and accompanying technical documentation are licensed under
[Apache-2.0](LICENSE), copyright 2026 Uzair Gheewala. Software citation is in
[CITATION.cff](CITATION.cff). Third-party source attribution and retained terms
are in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

The unpublished extraction history was cleaned before its first push to exclude
eight correspondence/budget-planning files. An original-history backup is kept
outside this repository. [Publication provenance](provenance/publication.json)
records the commit mapping and the namespace move without altering captured
source hashes or frozen research results. Historical development notes retain
their original paths/commands; this README gives the current installation route.

GitHub source history contains development/design records as well as runtime
code and tests. Installed wheels exclude `crucis_causal/docs/`; source distributions
retain the S1/S2 technical JSON examples and S3 methodology index needed by tests, along
with test fixtures and tooling. Research datasets, recorded runs, sealed battery
seeds and credentials are not bundled. Excluded-data tests report explicit skips.

CI tests Python 3.10 and 3.12 on Linux and Python 3.12 on Windows. It builds both
distribution formats, checks the installed wheel in isolation and preserves test
and skip receipts. The S1–S4 baseline passed this matrix. Its Windows package job
took about 26 minutes. A follow-up on the stable source ran the cursor-isolation
test to completion after an earlier 45-second diagnostic timeout. Check the
[CI runs](https://github.com/crucis-lab/crucis/actions) for the status of each
commit. Successful main-branch checks trigger the documentation deployment.
