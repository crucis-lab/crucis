# Subsystem 1: system connections

Tickets: DLV-08, DLV-09; compatibility checks also cover DLV-10.

This is the opt-in implementation of the accepted SC-1 design and S1-A..G bundle plan.
Its wire version is `0.1.0-proposal.1`. It supplies connection records, preservation,
scoped interpretation checks, optional ports and an additive legacy bridge. The
adopted `python -m audit` reports, metrics and certificates keep their existing path.
Public protocol adoption and the original C1-C5 migration remain separate owner work.

## Install and run

Tested with Python 3.12.14 and NumPy 2.3.5. Structural validation uses the exact
dependencies in `requirements.txt`. They can be installed in a separate environment
or an external `--target` directory; the interpreter must see that directory through
`PYTHONPATH`. These dependencies do not install or invoke a causal discovery system.

```text
python -B -m audit.connections describe
python -B -m audit.connections schema --out ../checks/sc1-schema.json
python -B -m audit.connections import-recorded matmcd --out ../checks/matmcd-connection
python -B -m audit.connections validate ../checks/matmcd-connection/package.json --out ../checks/matmcd-validation.json --profile evidence_foundation --require snapshot_integrity
python -B -m audit.connections gate S1-G --out ../checks/S1-G --dependencies ../checks/dependencies
```

CLI output files and gate evidence must be outside `cc-research`. Choose new paths;
the CLI refuses to overwrite prior output files. `import-recorded` selects one item
and arm from an existing audit (defaults: its first item/arm). Use `--item`/`--arm`
to select explicitly. The receipt identifies that choice and the reported legacy
status. It publishes an immutable evidence package, not a new scientific run.

Validation exits zero when wire/reference closure and every explicitly requested
check/profile pass. Without `--require`/`--profile`, failed optional semantic checks
remain in the report; they do not destroy preserved evidence. Exit 2 means the
requested claim or command was not established. `scientific_correctness` is always
`not_assessed` by this subsystem.

## Meaning and guarantees

There is no universal native success flag. Requests, attempts, observations, outputs,
assessments and selections have separate immutable identities. A recovered checkpoint
has a new attempt and an explicit recovery link. Reconnecting to an established live
episode retains its attempt. Reimport identity is designated by the caller and
persisted through `IdentityService.import_once`; equal bytes or paths do not identify
a native occurrence. Changed bindings under that occurrence key conflict.

Knowledge is tagged `known`, `unresolved` or `not_applicable`; uncertain references
have their own explicit variant. Scalar numbers preserve decimal text, nonfinite
values are tagged, and arbitrary native bytes use exact UTF-8 or base64 snapshots.
Raw JSON decoding for tensor/native numeric fields uses Decimal rather than float.

`validate_wire` checks the closed encoding and reference closure. `semantics.validate`
adds separately scoped checks; its `.ok` still means wire/reference conformance only.
Use `report.require(check_names, subjects=...)` for a stronger named claim. Checks
report `pass`, `fail` or `unknown`. Unknown foreign contracts/required extensions
withhold their affected guarantees; no schema or reader is fetched from the network.

The `core.validate` API persists check/gap references and separates satisfied from
withheld profiles. The exact executable profiles are in `core.PROFILES`: evidence
foundation, available snapshots, graph encoding, DAG, finite measure, tensor encoding,
and event history. The broader D/I/G/C/Q/L/M/H/U design families are composed from
named checks; their family labels alone are not executable all-features guarantees.

An evidence-foundation claim requires an identified new observer and at least one
observation or gap. Original intent/execution can remain unresolved. Snapshot integrity
checks the actual captured bytes and declared digest; it does not prove authorship.
External snapshots require explicit roots and their exact bound digest. A changed
file is captured separately; a missing file is not proof that the original system
did not run. Relative paths cannot escape the supplied root; `.env` is denied.

## Implementation map

| Module | Responsibility |
|---|---|
| `model`, `codec`, `schema`, `sc1.schema.json` | UUID occurrence IDs, staged immutable records, strict encoding and 36 closed record payloads |
| `validation`, `semantics`, `families`, `history` | Wire/reference and named domain/output/history checks; no scoring or scientific repair |
| `evidence`, `store` | Exact snapshots/selectors, explicit access, immutable publication, import associations and alias CAS |
| `domains` | Source-scoped variables, explicit singleton mappings, coordinate views and explicitly derived alignment views |
| `api`, `services`, `ports`, `core` | Closed runtime values, injected services, optional callables, exact core operations and runtime capabilities |
| `legacy`, `integrations/legacy_recorded` | Full-field legacy codec, recorded-only adapters, explicit partial prospective projection |
| `integrations/causaliq` | Native prompt-bound existence probability/orientation confidence extraction from recorded evidence |
| `specimens` | Authoring of labeled synthetic wire specimens; frozen copies live under `tests/audit_fixtures/sc1` |
| `gates` | Compilation, source identity, full audit tests, new recorded packages, legacy reruns and certificate verification |

`api.AdapterPorts` contains only supplied callables, with `describe` required. A
recorded reader has no invoke/cancel stub. A prepared command is an executable/argv
descriptor. `supplied_connection` takes an owner-supplied execution driver, observer
and optional delivery/cancellation drivers; it does not eval an entrypoint, construct
shell commands or discover global credentials. `with_decoder` binds a named exact
reader and target contract. Parser failure returns a gap and preserves its source.

Describe, bind, prepare and decode cannot implicitly call invoke. Runtime authority
is an opaque caller-owned capability, checked against exact request, attempt,
operation, effects, policies and presentation scope. A JSON capability declaration
cannot mint it. Execution/delivery tokens are consumed to prevent implicit retries.
This is a policy boundary between trusted components, not OS isolation against
malicious Python code. Driver owners must enforce their own native spend/cap guards.
No production driver or command here invokes a live model.

Observation takes one bounded batch. `exhausted` describes that interface, not native
completion. Delivery/cancellation have separate grants and receipts. Cancellation
acknowledgment does not establish stop. Exact recorded replay has an ordered
occurrence key and exact request bytes/context; mismatch leaves its cursor unchanged.
Exhaustion stops or returns unresolved. It has no fresh-provider fallback argument.

## Semantic scope and deliberate limits

- Domains preserve distinct variable/coordinate identities, duplicate labels, temporal
  positions and grouped/learned descriptors. Labels/shape do not establish equivalence.
  Full one-hot collapse, symbolic/relational grounding and factor alignment criteria
  need their own procedures. A supplied total learned alignment creates a derived view.
- Graphs preserve relations, endpoints, coverage, omission and associated quantities.
  Selected directed/DAG/partly directed/endpoint/association checks are implemented.
  Full CPDAG/PAG validation is withheld. Unknown relation versions cannot gain a DAG
  guarantee. No cycle repair, completion or threshold choice occurs.
- Local sets, decisions, rankings/ties and orders retain their scope. Abstention,
  unreported membership, excluded variables and unranked variables remain distinct.
  A local answer or rank is not expanded into a global graph.
- Quantities check scalar ranges/counts, explicit tensor axes, selected JSON/NumPy
  numeric entry/missingness contracts and intervals. Statistic/event semantics need
  the exact declared reader. Range does not prove calibration. Exact count-ratio
  checks require counts, a positive denominator and the exact represented ratio;
  rounded ratios require a separately named rounding rule.
- Collections retain keys/order/multiplicity and explicit parameter/weight pairing.
  Finite measures use exact per-atom weights totaling one; no normalization occurs.
  Compressed multiplicity-weight interpretations and posterior/IID claims are withheld.
- Model/state support is artifact/domain/association and scoped-load support. Native
  model loading, hidden-state equality and provider-specific remote orchestration
  require supplied extensions/drivers. Unknown RNG prevents an exact full-scope load.
- Resource sums require an explicitly selected disjoint sum, common units/measurement
  contract, nonoverlapping membership and known quantities. Empty/unknown usage is
  unresolved. Inclusive totals, revisions, overlapping durations and child totals
  cannot be silently summed. Recovery does not reset a cumulative record scope.

## Legacy compatibility

The lossless codec explicitly handles all `RunRecord`/`Graph` fields, tuple-key maps,
sets, numeric NumPy arrays and float bits. It never substitutes `summary`, `canonical`,
pickle or `default=str`. Historical echo retains statuses, failure labels, graph raw
values, variants/stages, confidence, edge sources, costs, notes, `file_read`, and the
exact replicate selection/order. Files are fresh snapshots; historical hashes remain
reported claims until checked. Missing/mismatched files yield gaps.

Stage/variant labels and order get explicit relations. Costs retain legacy reported
units/basis. Unsupported confidence coordinates/statistics stay native reports/gaps.
The causaliq integration separately verifies its exact result-file identity, explicit
name permutation and recorded prompt before extracting typed native fields. It keeps
orientation as confidence versus reverse; it neither invents conditional probability
nor multiplies existence and orientation. Other legacy confidence is not retrofitted.

Prospective projection requires an explicit graph, total identity-preserving coordinate
mapping, named outcome assessment and projection rule. Unknown/conflicting outcome,
partial coverage, unsupported marks and graphless results reject. Stage projection
requires explicit unambiguous stage naming relations. Projection records its limited
provenance expressiveness. Echo is the path for faithful historical compatibility.

## Evidence and release status

See `audit/docs/subsystem1-implemented-support-2026-11-01.md` for real versus synthetic
support cells, and `audit/docs/subsystem1-implementation-log-2026-11-01.md` for bundle
gate evidence. Tests are `tests/test_audit_connections_*.py`. The frozen eleven
packages cover every declared record and output body type. Native process behavior
uses the deterministic `s1_native_fixture.py`, not a third-party scientific system.

The gate compiles new Python files to its external output directory, verifies the
original 64-file identity, exercises new recorded packages, recomputes all 1,298
legacy comparisons and verifies 14 stored plus 14 fresh certificates. The original
live-PC test remains conditional on causal-learn; the tested host lacks that package.

Uzair owns commit, public adoption and any deliberate repin. W5 owns tracker/site
updates. No result-folder move or `port_map.json` belongs to this increment.
