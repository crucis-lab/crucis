# Crucis: Causal Discovery Auditing

Crucis is an independent framework for auditing causal discovery systems and
their claims. It preserves native evidence and declared uncertainty, supports
controlled comparisons, and produces traceable findings and reports.

The framework, its evaluation suite and its paper share the Crucis identity,
inspired by the *instantia crucis*: evidence that discriminates between competing
explanations. This repository is the extracted development version. Protocol,
implemented support and empirical coverage are versioned separately.

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

CI is configured to test Python 3.10/3.12 on Linux and 3.12 on Windows, build both
distribution formats, and inspect the installed wheel from an isolated working
directory. It preserves test/skip receipts. Prior publication checks do not
qualify new local S3 changes; those need their own remote CI results. CI does not run
paid model experiments, deploy a site or publish to a package index.
