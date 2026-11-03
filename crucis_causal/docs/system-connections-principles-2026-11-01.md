# W2 system connections: generic core and faithful evaluation (1 Nov 2026)

Tickets: DLV-08, DLV-09; neighbours DLV-10, ADV-01.
Status: design only. Adds requirements from Uzair's discussion; no implementation or protocol change adopted.
Prior discussion: `system-connections-design-2026-10-31.md`.

## Direction established by Uzair

- Faithful evaluation takes priority over convenience, uniformity and adapter size.
- Aim for a system-independent core, with a balance between common policies/mechanisms and native system specifics.
- As reusable core capabilities improve, individual adapters should become simpler, including for complex systems.
- Map the broader space of causal-discovery systems before freezing the connection contract. The current eight
  adapters are examples to test a design against, not the boundary of the intended design space.
- Continue subsystem-by-subsystem design, implementation and testing. The present phase remains design only.

This accepts a direction, not every earlier proposed interface detail. W2-5 through W2-9 remain pending.
Shared protocol changes must go to W5; no implementation go has been given.

## Architectural interpretation proposed for discussion

The core supplies reusable contracts, policies and mechanisms. The adapter supplies native invocation,
configuration and translation details that cannot yet be expressed through those general contracts.
A shared feature should have a system-independent meaning and conformance checks. Moving special cases
into a common file, while still branching on system names, does not meet the generic-core objective.

Small adapters are an outcome of good abstractions, not a line-count constraint. A necessary native
integration may remain substantial until genuinely reusable support exists.

Faithfulness means preserving the system's information inputs, configuration, output meaning, ambiguity,
failures and evidence. Operational wrappers may be needed; semantic changes must be explicit and separately
identified. Keep native evidence and a documented mapping alongside standard representations. If a meaning
cannot be represented faithfully, expose that limitation rather than silently invent a direction, confidence,
source, or an equivalent-looking output.

Genericism cannot be established by claiming to anticipate every future system. It needs an explicit
supported scope, extension points, and observable limits when a system exceeds that scope.

## First design artifact: a capability-space map

The following is an initial checklist to investigate, not a completed literature survey or adopted scope.
Before claiming field coverage, validate it against representative systems and primary documentation.

| Axis | Questions and possibilities to investigate |
|---|---|
| Information inputs | Samples, names/text, intervention information, background constraints, summary statistics; what is supplied, accepted and actually available? |
| Data organization | Static tables, temporal observations, multiple environments, streaming/incremental inputs; what identities and relationships must survive translation? |
| Interaction | One request/result, staged pipelines, repeated queries, adaptive requests for observations or interventions; who chooses each action and under which policy? |
| Output meaning | Directed graphs, unresolved/equivalence representations, latent-variable marks, probabilities or graph collections, orders, individual causal claims; which fall within our scope? |
| Observation depth | Final output only, intermediate states, calls/events, system-stated sources, confidence; what is native versus auditor-inferred? |
| Execution access | Python function, command, container, remote service, recorded artifacts; what can be invoked versus only read, and under which environment? |
| State and randomness | Seeds, repeated samples, persistent state, caches, warm starts, model/configuration changes; what makes two runs comparable and reproducible? |

Do not force every axis into the existing interface before reviewing the map. In particular, the existing
requirement that an ok RunRecord must include a Graph is a scope decision to revisit if we include systems
that return other causal outputs. Representing a result and having an appropriate evaluation metric are
separate capabilities.

## Support must be explicit at several layers

For each proposed feature, distinguish:
1. The native system supports it.
2. The adapter can deliver/read it in the requested mode.
3. The core can represent it without losing relevant meaning.
4. An evaluation procedure is defined for it.
5. Conformance and evaluation checks cover it.

One static capability boolean cannot stand in for all five. Avoid claiming full support from one successful
historical import or from the mere existence of an output field.

## Proposed design sequence within system connections

1. Build and check the capability-space map, including cases far from the current integrations.
2. Choose the supported scope and distinguish future extension points from current guarantees.
3. Define the minimal common request/result envelope and optional capability modules.
4. Assign responsibilities among core, adapter and adjacent subsystems, including interactive execution boundaries.
5. Walk representative cases end to end and specify what information changes, what is preserved, and what cannot be scored.
6. Agree on acceptance criteria and a bounded implementation increment before writing code.

Possible acceptance checks for later design: variable-identity preservation across every indexed field;
semantic preservation of output marks; no invented optional metadata; declared mode availability matches
what can actually execute; native evidence is retained; adapter/parse/host/system failures remain distinguishable;
core contracts are exercised by multiple structurally different integrations without system-name exceptions.

Only the design discussion and this requirements record were produced in this turn. No implementation,
execution mode, schema, protocol, result layout or tests changed.
