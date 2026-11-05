# Subsystem 3: execution accounts

Tickets: DLV-08, DLV-09; compatibility and methodology references also cover
DLV-10. This opt-in runtime uses SC-3 `0.1.0-proposal.3`. Its accepted source is
the pinned final design and B00–B13 DAG in `../docs/`. It does not adopt changes
to the original research protocol or paper evidence contract.

S1 owns native requests, attempts, outputs and interpretation. S2 owns scientific
case/condition/trial definitions and matching eligibility. S3 adds durable
execution history, actual owner admission and issue boundaries, collection,
interaction, recovery and immutable evidence publication. Native-specific
mechanics are explicitly supplied code; contract strings never load drivers.

## Read supplied evidence

From an installed repository build:

```powershell
python -B -m crucis_causal.execution --help
python -B -m crucis_causal.execution inspect account.json
python -B -m crucis_causal.execution validate account.json --dependency dependency.json
python -B -m crucis_causal.execution plan account.json --request operation.json --dependency dependency.json
python -B -m crucis_causal.execution recovery-plan account.json --kind restart --policy s3.example_policy
```

The module CLI reads only explicitly supplied files and prints a result. Inspect
is an inventory, while validate checks the supplied closed dependency set. The
CLI does not install live bindings or policy evaluators. Plan/recovery-plan hold
when those are unavailable. Neither help, parsing nor inspection initializes a
native provider, installs dependencies, reads environment secrets or dispatches
fixture work. Fixture bootstrap code lives in source tests, not the runtime CLI.
There is no new package-index release; the distribution remains `crucis-causal`.

Python callers can construct `Core`, supply a finite read context and explicitly
install actual drivers, decisions and policies. Live work additionally needs
actual journal/storage/owner controls and runtime transport/secret bindings.
These values cannot be reconstructed from saved JSON. The exact public port
signatures are declared in `api.py`; the methodology index maps them to actual
implementations and scoped tests.

## Responsibilities and distinctions

| Responsibility | Implementation | Boundary retained |
| --- | --- | --- |
| Identity and durable history | model, codec, identity, journal, store | Intent is not evidence that a receiver launched work; snapshots and earlier cutoffs stay immutable |
| Authority and resources | authority, owners, accounting, coordinator | Metadata eligibility is not live permission; partial owner commitments and unknown bills remain visible |
| Inputs and staging | inputs, staging, bridge, scientific | Realization, preservation checks, information exposure and scientific conditions stay distinct |
| Dispatch and attachment | drivers, effects, s1_native, native_results | No automatic retry, native-ID guess, handle resurrection or metadata-derived idempotency |
| Observation and interaction | collection, decisions, interaction | Capture, interpretation, ACK, transmission, native acceptance, policy consumption and use are separate |
| Recovery and stopping | recovery, stopping | A new checkpoint attempt is not an independent trial; stop ACK is not observed termination; closing observation does not release liabilities |
| Evidence publication | projection, publication | Exact audience/dependency closure, external receipts and revision CAS; copy revocation/deletion does not erase other copies or past exposure |

`completed` describes a call's operational result, not causal correctness, native
fulfillment, termination or complete evidence. Unknowns, partial outputs and
conflicting assessments are preserved. An uninterpreted native output can remain
available without being coerced into a graph or repaired for scoring.

The journal persists C/G/owner requests/D before the relevant effects. Reopening
the original intent never supplies another forwarding permit. In the qualified
journal/account profile, a new initiating command also cannot reuse an attempt
already claimed by another launch/restart command. Actual receiver deduplication,
fencing and negative-query closure require their own supported mechanisms; a
request digest supplies none of those guarantees.

Scientific launch/restart/restoration use real S2 matching and fixed recovery
conditions. Native response permission alone does not establish a scientific
information-channel condition. Unsupported scientific followups hold; they are
not silently relabeled probes. An unknown-origin observational interaction can
still be preserved and controlled within its explicit operational policy, while
its original scientific membership remains unestablished.

`Coordinator.recover` is a pure boundary for pinned supplied policies. Missing
policy semantics hold and known scoped obligations remain named. Plans are
proposals; they never issue authority or perform hidden lookup/cancellation.
`close_collection` is an independent expected-revision journal action.

## Qualification scope

The four controlled profiles exercise mechanisms, not real causal systems:

| Profile | Native mechanism and fixed checks | Important limit |
| --- | --- | --- |
| E01 local | Actual synchronous function; native order and explicit mapped graph view; cost0.7/cap1; cold durable history | The graph is a scripted native answer, not ground truth; missing edges stay unreported |
| E02 remote | Independent owned receiver; lost launch ACK, lookup, three captures/two native events, cold source ACK; cap10 | Negative lookup without ingress closure does not justify a duplicate launch |
| E03 interactive | Same-text distinct actions; fixed source/compute/selection; Q1 delivery1, Q2 missing-source choice/delivery0; consumed1/remain1 | Unknown-origin operational episode, not scientific eligibility under an undeclared S2 information condition; native use/termination unknown |
| E04 checkpoint | Separate explicit R2 condition; A1/A2 in one scoped trial; captured/native state sources; total9/cap20 | Original NA recovery remains held; only model/optimizer loading is established, not RNG/history or exact trajectory replay |

The receipt-backed implemented scope and release review govern which cells have
passed. Declaration shape checks are not native integration claims. Actual
process-death tests, fresh issuers and independent receiver logs are separately
identified; recreating objects in one process is not called a process restart.

The local storage/owner/journal profiles qualify cooperative same-host operation
with checked SQLite DELETE/FULL and flushed immutable artifacts. They do not
claim hostile-process isolation, distributed transactions, power-loss guarantees,
universal hard monetary bounds, remote dissemination or global erasure. Runtime
secret bindings stay out of stored commands and public projections.

## Methodology and compatibility

Use `../docs/subsystem3-methodology-index-2026-11-03.json` and the dated
implementation log for accepted rule → code → scoped test/receipt → claim/limit.
The index inventories38 wire kinds,31 operations,48 actual port signatures and
eight independently qualified support axes. Its cardinalities do not certify
every combination of native behavior, environment and scientific condition.

New mandatory acceptance cases have no availability skips. Older offline
data/dependency skips, recorded-data parity/certificate checks, installed-wheel
isolation, host matrix and real backend integration have separate receipts.
`CRUCIS_DATA_ROOT` can select explicit historical evidence for legacy qualification;
it never adds the research checkout or its analysis/harness code to imports.
No result pin, scientific threshold, population meaning, confirmatory label or
paper contract is changed by this subsystem.
