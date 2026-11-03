# Opt-in experiment metadata (SC-2 candidate)

Tickets: DLV-08, DLV-09, DLV-10.

This module records scientific definitions, source resolutions, request/evidence
associations and analysis intent. It does not execute discovery systems, transform
datasets, read protected stores, grant authority or compute scientific metrics.
The existing `python -m audit` and `python -m audit.connections` routes are unchanged.
The implemented version remains `0.1.0-proposal.1`; public adoption belongs to W5.

## Use

Use the project's Python interpreter and S1's exact locked dependencies (the local
implementation reused the existing offline S1 dependency directory). Examples:

```text
python -B -m audit.experiments inspect SOURCE_PACKAGE.json
python -B -m audit.experiments validate PACKAGE.json --input DEPENDENCY.json --out OUTSIDE_REPO/validation
python -B -m audit.experiments import S1_SOURCE.json --snapshot SNAPSHOT_UUID --occurrence OCCURRENCE_UUID --battery SOURCE_BATTERY --out OUTSIDE_REPO/import
python -B -m audit.experiments project IMPORT_PACKAGE.json --input SOURCE_PACKAGE.json --input CODE_PACKAGE.json --receipt RECEIPT_UUID --selection PARAMETER_UUID --out OUTSIDE_REPO/echo
```

Repeat `--input` for each explicitly supplied dependency snapshot; no locator is
followed. Import emits the receipt and selection IDs in report.json and writes
exact dependency bytes alongside package.json. Preserve those dependencies for
later use. Output roots must be outside cc-research. Publications do not overwrite
earlier files. Inspection is deterministic for the same received bytes. Validation
returns status 2 when the requested claim is withheld; a successful command never
implies scientific accuracy. There is no run, spend, grant or sealed-read command.

The CLI supports source-backed encoded legacy echo. Richer compatibility views use
the Python API with an explicit S1 LegacySelection and caller-supplied runtime
CompatibilityView. Lossless requests reject such narrow views. Projection never
chooses a best/last repetition or turns partial native evidence into a DAG.

## API and boundaries

The sixteen entry points are in core.py; exact runtime value classes are in api.py.
Construct a bounded PlanResolver from explicit bytes, ReadAccess for those package
IDs, and an S2RecordWriter whose context exposes its single transaction overlay.
FamilyRegistry, AssessmentRegistry, ProjectionRegistry and LegacyRegistry require
exact explicit versioned registrations with implementation provenance. They never
load handler code named by an input file.

PlanOp states describe the operation: rejected returns no additions; partial
retains useful records with gaps; completed can contain a failed assessment.
Preserve, interpret, bind_inputs_sources, bind_native_request and bind_evaluation
are independent scoped profiles. Unknown critical extensions, unavailable evidence
and unknown procedures withhold affected claims. Supplied source accounts can be
preserved even when scientific interpretation is unavailable.

Ordinary operations stage metadata transactionally. IdentityService.import_once
requires a caller-owned persistent OccurrenceStore. Same occurrence plus changed
inputs rejects; equal bytes under another occurrence remain distinct. Its returned
record closure can be rehydrated by another writer without changing original IDs
or creation times. This store is metadata only and is unrelated to sealed stores.

S1 compiler registration keys scientific operation, native operation, response
fulfillment rule and route kind separately. S1's native route/completion support
must also be installed. Required information must resolve to exact permitted
payloads/endpoints; unsupported families/cardinality/parameters require an exact
custom procedure or reject. Compiler context records actual S2 source identity.
Projection stages prospective request/attempt metadata. Handoff pins the supplied
immutable S1 snapshot; neither operation invokes, delivers or proves restored state.

freeze_s1 and S2RecordWriter.frozen allocate fresh publication IDs and keep copied
record contents unchanged. Self-qualified records and captured payload reference
contexts retain their verified source package. Commitments identify earlier bytes;
amendments retain both revisions. A selected adaptive action is not a delivered one.

## Evidence

See the accepted design catalog/DAG and the new implementation log and scope note
under audit/docs. External receipts under
`../_w2_checks/2026-11-02_s2_build/` retain failed attempts, environment, source and
fixture identities, full-suite outcomes, stored-number comparisons and certificates.
The final gate adds an acceptance ledger for 58 adverse cases, 20 API scenarios
and every bundle's must-show row, plus a durable recorded MatMCD CLI/binding path.

Two illustrative API expectations are refined without rewriting the accepted
design: a bare request preview cannot pass actual handoff checks (API09), and an
evidence link without the required population/native associations yields a partial
population (API11). Positive handoff and complete metadata-population paths have
separate executed tests. No stronger readiness is fabricated to match an example.
