# S3 release review, 4 November 2026

Tickets: DLV-08, DLV-09; related DLV-10.

The user approved the revision 3 design and B00–B13 implementation. B00–B12 are
locally committed after their owned source gates and enabled hooks. R01 reconciles
all predecessor receipts, accepted source pins, executed cases and fault triplets.
B13's final enabled-hook commit receipt completes this milestone; this file does
not assert its own future hash or fabricate a self-verification receipt.

| Bundle | Validated local commit |
|---|---|
| S3-B00 | `b9b316bda856` |
| S3-B01 | `78d33b3094ce` |
| S3-B02 | `91c150c2e757` |
| S3-B03 | `78de55c2b16a` |
| S3-B04 | `6b68d33d96b0` |
| S3-B05 | `222834deec4c` |
| S3-B06 | `0e84b278fbd2` |
| S3-B07 | `dcc3c180a3a9` |
| S3-B08 | `8ee184a71a2d` |
| S3-B09 | `3f1bb357dca3` |
| S3-B10 | `a9d2b47477a6` |
| S3-B11 | `914e1438a2d3` |
| S3-B12 | `704433af9fc5` |

See [implemented scope](subsystem3-implemented-scope-2026-11-04.md),
[source/methodology map](subsystem3-methodology-index-2026-11-03.json),
[release traceability](subsystem3-release-traceability-2026-11-04.json) and
[incremental log](subsystem3-implementation-log-2026-11-03.md).

## Qualification decisions

| Dimension | Result and evidence boundary |
|---|---|
| Offline contract/mechanism implementation | All 106 planned obligations and 30 inherited negative boundaries reconciled; mandatory new cases have no skips; controlled local/remote/interactive/checkpoint mechanisms exercised |
| Recovery | Exact fault triplets link declared independent oracle, retained history and recovered view; process deaths are distinguished from injected errors and evidence-only reopening |
| Legacy recorded-data compatibility | 1,298 comparisons passed at unchanged 0.001 tolerance; 14 stored + 14 fresh certificates verified from explicit historical data, external outputs |
| Installed package | Offline built/installed wheel bytes, schemas and CLI checked with research imports blocked; no index release |
| Host matrix | Fresh Windows Python 3.12 only; Linux Python 3.10/3.12 current S3 runs not performed; prepared CI is not a pass |
| Real scientific native systems | No new campaign; controlled fixtures do not establish named-system performance or scientific correctness |
| Remote publication | Not authorized or performed; local topic commits only |

The historical scientific request with NA checkpoint recovery remains held. Its
separate explicit R2 condition supports only partial component restoration, not
exact RNG/history replay. The interactive live example has unknown scientific
origin; a valid native response policy alone does not authorize an undeclared S2
scientific information channel. These limits are intentional evidence boundaries,
not skipped positive results hidden by an overall metadata check.

Failures encountered during development remain external. Corrections addressed
reference contexts, cleanup, boundary plumbing, lost receipt dependencies, bounded
immutable indexing and test-launcher/environment errors. No expected scientific
number, accepted source hash or tolerance was changed to turn a failure green.
The log and immutable receipts retain the specific failure/recovery sequence.

Final review closed two concrete gaps. Earlier F01–F03 and F17–F18 assertions
had passed without separately saved fault triplets; B12 re-executed them with
actual oracle/history/recovered-view capture, leaving the earlier receipts intact.
F06's exact required variants are also saved explicitly. N13's earlier external
self-dependency test did not cover a receipt's plain-ID self-subject: the codec
now rejects that direct known whole-package digest claim, and the corrected
negative passed in the full current-source suite. An unresolved digest remains
preservable as unknown. These corrections enforce the accepted evidence contract;
they do not change scientific goldens, tolerances or paper sources.

## Receipt location and completion rule

External receipts are organized as `<external-build-root>/S3-B00/` through
`S3-B13/`, with accepted-inputs, tests, source-before-after, support-claims, full
gate and commit records. Fault triplets sit under each qualified case directory.
B13 also contains reconciled-acceptance, legacy-rerun and certificate records.
The traceability JSON pins prior receipts without copying private operational
data into the repository. The final B13 commit receipt remains external because
it cannot be included in its own immutable hashed subject.

## Where we're going

Review this scoped implementation and decide the next subsystem's design.
Any remote PR/CI, new scientific condition, actual backend experiment or stronger
guarantee needs its own scope and evidence. The paper and research tooling
workstreams receive this methodology/support account without a manuscript rewrite
or change to frozen experimental sources.
