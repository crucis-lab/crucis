# W2 subsystem 1: system connections (31 Oct 2026)

Tickets: DLV-08, DLV-09; neighbours DLV-10, ADV-01.
Status: design discussion. No implementation authorized; no interface or protocol change adopted.

## Process decision recorded from Uzair

Uzair accepted the seven subsystem divisions discussed in this chat: system connections; test collections and
experiment definitions; execution and collection; measurement and attribution; finding decisions; reports and
certificates; auditor validation. The protocol is their shared rulebook; validation crosses subsystem boundaries.

Work proceeds incrementally: discuss each subsystem's responsibilities, current implementation, alternatives,
failure modes and acceptance criteria before its implementation/testing, then advance to the next subsystem.
The current instruction is design only for system connections. Earlier C1-C5 bundles retain their dependencies
and must-show obligations as planning context; they do not authorize implementation or override this pace.
W2-5 through W2-9 remain pending. Any shared-contract changes remain proposals to W5.

## Purpose and boundary

A connection translates between the auditor's common interface and one system's native interface.
It declares supported inputs/outputs, delivers an already prepared view through the native interface,
and translates the native result plus execution evidence into a common run record.

Experiment definition owns the test conditions; execution owns scheduling, resources, retries and budgets;
measurement owns scores; finding decisions own verdicts. The connection must preserve each system's
semantics and expose missing information without inventing it. It receives only the experimental view
needed to call the system. The reference truth remains on the evaluator side; an oracle control may supply
explicitly authorized knowledge through its declared input channel.

## Current implementation inspected

- `audit/core/adapter.py`: Capabilities, Presented input, Adapter, registration, recorded/run entry points,
  and the inherited refusal of live LLM execution without allow_spend.
- `audit/core/runs.py`: common RunRecord, optional graphs/variants/sources/confidence/stages, costs,
  evidence-file hashes, typed statuses and replicates. An ok run must include a graph.
- `audit/core/graph.py`: directed, undirected, bidirected and partial marks; source conversions,
  coordinate remapping, canonical representation, and exact retained Causal-Copilot matrix round-trips.
- `audit/core/harness.py`: prepares a shuffled view and maps graphs, variants, source labels and stages
  back to original coordinates. Confidence claim keys are not yet specified/remapped here.
- `audit/systems/`: eight adapters: PC, GES, GIES, MATMCD, Vashishtha, PyWhy-LLM, causaliq,
  Causal-Copilot. Shared recorded readers are `_methods.py` and `_probe.py`.
- `tests/test_audit_core.py`: representation/mapping checks, planted oracle/reversed checks, declared-mark
  and variant checks on recorded adapters, stable repeated identity, status validation and a spend-refusal check.

The established path is reading recorded outputs. PC/GES also have direct live algorithm calls (optional
dependencies required). GIES declares recorded only. The LLM agent adapters declare recorded/replay/live,
but their class hierarchy does not implement direct replay/live execution: it supplies command descriptions
for the existing runner. Causal-Copilot similarly provides a command description rather than direct execution.
Do not describe these mode declarations as an end-to-end package execution guarantee.

The prior full suite passed with 54 tests passed and the live-PC test skipped in bundled Python; no tests
were rerun in this design discussion. The earlier handoff describes other live checks, but those are not
newly executed evidence here.

## Choices for discussion (recommendations, not accepted decisions)

| Choice | Recommended direction | Strong alternative and tradeoff |
|---|---|---|
| Connection versus execution | Connection describes native invocation/translation; shared execution handles budgets, scheduling and retries. | Each adapter runs everything itself: fast bespoke integration, but duplicated safeguards and inconsistent run policies. Keep a small direct Python call possible under a common execution contract. |
| Common output versus native fidelity | Preserve directed/undecided/partial semantics and the raw native evidence; scorers interpret later. | Force a directed graph at ingestion: simpler downstream code, but manufactures certainty and changes the system being audited. |
| Minimum versus rich outputs | Require identity, status/evidence, and a valid graph on success; make confidence, sources, variants and stage traces optional. | Require every system to expose all metadata: stronger uniformity but excludes black boxes and encourages fabricated metadata. |
| Capability versus availability | Distinguish what a system supports, what this integration can obtain in a mode, and what one run actually contains. | One static boolean/set: simpler, but conflates absent capability with an incomplete recording, e.g. causaliq confidence. |
| Coordinate convention | Explicitly state shown versus original positions; translate once, including all edge-indexed metadata. | Require one convention at every entry point: easier callers but requires normalizing historical records; preserve originals as evidence. Existing live and recorded entry points currently differ. |
| Mode meaning | Describe recorded reading, replay execution and live execution separately, with explicit readiness/requirements. | Treat all as a single run operation: smaller API surface, greater risk of promising a route that only generates a command. Replay requires matching recorded requests; it is not equivalent to rerunning on altered data. |
| System identity | Record adapter identity separately from system version, configuration, dependencies, model and image, distinguishing pinned claims from observed evidence and unknowns. | Use a system name/adapter-file hash only: cheaper, but different prompts, runners and models can be mistaken for the same system. Record more metadata only where it changes interpretation or reproducibility. |

## Failure modes to address before freezing this subsystem

1. An adapter silently adds preprocessing, an orientation rule or graph repair and changes the audited system.
2. Output arrows or their confidence/source metadata refer to the wrong variables after a shuffle.
3. A declaration is mistaken for proof that a recording contains a field or that a mode is executable.
4. A missing artifact or parser failure is attributed to the system as a crash without distinguishing the causes.
5. Missing provenance/confidence is filled in as if the system had stated it.
6. A short stable name hides different versions/configurations; two identity() calls agreeing does not establish identity completeness.

## Next discussion

First settle the connection's responsibilities and its boundary with shared execution. Then define its
capability/input/output contract and mode semantics in detail. Only after design and acceptance criteria
are agreed should any implementation be proposed. The inherited approximately 50-line adapter goal is
an integration-effort aspiration, not a hard line-count rule or evidence that every connection is complete.
