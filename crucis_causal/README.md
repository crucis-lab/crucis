# `audit`: a continuous-integration check for causal claims (A3, DLV-09)

Point it at a causal-discovery system through an adapter; one command later there is a report that says what the system
gets right (L0), how its answers move under controlled change (L1: names, layout, knowledge, robustness), what each of its
stages does to each edge (L2, Python systems), and a certificate anyone can recompute. Protocol: `PROTOCOL.md` (v1).
Tickets: DLV-08 (protocol), DLV-09 (package), DLV-10 (results).

This folder also holds the earlier B5 claim checker (`adapters.py`, `rca.py`, `run_adapters.py`, `export_cc_stages.py`,
BLD-15), unchanged; its violation classes are the evidence rows of K07 and K13.

## Commands (no command spends API credit)

    python -m audit systems                      # the adapters and what each takes and gives
    python -m audit battery ca-ab06              # a battery's identity and hash (also q1s2, ca-semantic, ca-formula)
    python -m audit audit matmcd --out DIR       # one audit from recorded runs: report.json, report.md, certificate.json
    python -m audit verify DIR/certificate.json  # recompute every certified number from the raw files
    python -m audit rerun --out DIR              # every existing audit through the package: comparison table + 14 reports

Tests (NumPy only; data kept outside git is skipped when absent):

    python tests/run_tests.py --out <file outside the repo> --pattern "test_audit_*.py"

## Layout

| Path | What |
|---|---|
| `core/graph.py` | the typed mark graph every adapter returns; converters for Causal-Copilot matrices, probe results, edge lists |
| `core/adapter.py` | the adapter interface: Capabilities (takes, marks, source, confidence, variants, glass box, modes, cost), Presented, Adapter |
| `core/harness.py` | what the harness owns: the shuffled view a system is shown, and the mapping back |
| `core/battery.py`, `core/sealed.py` | battery manifests and hashes; the sealed battery (commit, check, one read per version) |
| `core/runs.py`, `core/evidence.py`, `core/canon.py` | typed run statuses and replicates; numbers with sources; canonical hashing |
| `protocol/` | the closed list of finding kinds, thresholds (hashed), regimes, truth tiers |
| `metrics/l0.py` | L0, by calling `score/` and `analysis/cc_graph.py` (one implementation of every rule) |
| `controls/` | L1 transforms (pure, seeded) and paired effects with the scenario-cluster bootstrap of `score/paired.py` |
| `trace/` | L2: the observation-only recorder for Python entry points, per-edge lineage, Causal-Copilot's stages from artifacts |
| `systems/` | adapters: pc, ges, gies, matmcd, vashishtha, pywhyllm, causaliq, causal_copilot |
| `findings.py`, `report/` | typed findings; report.json, report.md, certificate and verify |
| `run.py`, `collect.py` | one audit of one system on one battery; the standard audits (`AUDITS`) |
| `rerun/` | bundle B5: the existing audits recomputed from raw outputs and compared with the stored numbers |

## Adding a system (about 50 lines)

Subclass `core.adapter.Adapter`, declare `Capabilities`, implement `recorded(item, arm)` (read a past run into a
`RunRecord` over the item's original columns) and, if it can run, `run(presented, budget, out_dir, mode)` (return a
`RunRecord` over shown positions; the harness maps it back). Register with `@register`, import it in `systems/__init__.py`,
add a standard audit to `run.AUDITS`, and the conformance tests in `tests/test_audit_core.py` cover it. A live LLM run is
refused unless the caller passes `allow_spend=True`.
