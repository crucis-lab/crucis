# Crucis

Crucis is an independent framework for auditing causal discovery systems and
their claims. It preserves native evidence and declared uncertainty, supports
controlled comparisons, and produces traceable findings and reports.

The framework, its evaluation suite and its paper share the Crucis identity,
inspired by the *instantia crucis*: evidence that discriminates between competing
explanations. This repository is the extracted development version. Protocol,
implemented support and empirical coverage are versioned separately.

## Install and inspect

```sh
python -m pip install .
python -m crucis --help
python -m crucis systems
python -m crucis.connections --help
python -m crucis.experiments --help
```

Python 3.10 or newer, NumPy and jsonschema are required. Optional native PC/GES
execution uses `pip install '.[classical]'`. LLM execution retains the existing
explicit spending guards. Installation does not run an experiment.

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
including the research-derived helpers now owned under `crucis/_support/`.
The four historical B5 modules remain in the research repository.

## Development

```sh
python -m unittest discover -s tests -p 'test_audit_*.py'
```

Data-dependent tests require the declared research evidence; a skip is not a
completed reproduction. The extraction verification receipt distinguishes
offline package tests, data-backed compatibility, and installed-wheel checks.

The current development gate records the actual standalone source identity and
test outcomes:

```sh
python -m crucis.dev.gates standalone --out ../crucis-check
```

Prior research-layout gate implementations are retained as historical records
under `provenance/historical-gates/`. Their original bundle-acceptance claims
are not recreated by this development check. Use installed dependencies rather
than adding external source directories to the import path.

Read `AGENTS.md` for the automatic local milestone commit policy. Public hosting,
licensing, releases and the final GitHub owner are separate publication decisions.
Run `python -B tools/setup_repo.py` when starting in a new clone; it installs
this repository's validation hook through local Git configuration.
