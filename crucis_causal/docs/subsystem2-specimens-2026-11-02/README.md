# SC-2 design specimens: how to read this corpus

Tickets: DLV-08, DLV-09; related DLV-10.
Date: 2 Nov 2026, America/Los_Angeles.
Status: synthetic design artifacts, not an implemented S2 package or native study.

Start with [manifest.json](manifest.json). It gives the exact file/pin/package
identities, readable aliases and A-H roots. Aliases are review metadata outside
the closed wire packages; the packages themselves contain UUID identities.
S2 publication bytes are compact canonical JSON. S1 snapshots use their existing
pretty JSON byte convention; those digests are not interchanged.

For each group, the S1 definitions package holds explicit toy domain/reference
and structured payload definitions. The S2 plan holds fixed requirements. Later
S1 traces and S2 receipts hold hypothetical later accounts. B's recovered sources
are explicitly prior evidence; its later assessment-source package is separate.
This separation prevents a definition's dependency digest from secretly pinning
future trace content, even when the definition has no direct link to that record.

The bridge-M/R/H/P2 files exercise partial input binding, request preview,
association and amendment. The schema-preservation package demonstrates all 25
parameter schemas with unresolved values. It cannot satisfy their interpretation
or scientific readiness merely by having structurally valid fields.

All native/variable/case/output identities and branches are synthetic. Record
creation times identify actual document authoring, not original native event
times. Missing data/parameter artifacts are declarations. No data generation,
native calls, protected-store reads, grants or scientific metrics were performed.

[negative-cases.json](negative-cases.json) contains 58 future acceptance
specifications. Forty identify concrete baseline mutation paths; the others specify
byte-level and composition adversaries. A future test harness must use isolated
drafts or new changed-record/package identities and correctly rebound pins so an
unrelated integrity failure does not mask the intended semantic case. It must not
rewrite these positive baselines. These are not 58 executed product tests.

[api-scenarios.json](api-scenarios.json) describes 20 scenarios covering 16 entry
points. File/ref specifications stand for supplied byte/view/runtime inputs; they
are not serialized callables or executable jobs. Variant scenarios describe
required future fixtures, including supported and rejected projections.

The [traceability index](../subsystem2-review-traceability-2026-11-02.json) joins
92 source obligations, the 18 capability axes and 28 capability cases to design
responsibilities and future bundles. Mapping is an inventory, not empirical or
native support. Raw source accounts preserve discussion separately from typed
scientific parameters; no account blob supplies missing semantic evidence.

## Where we're going

Use these immutable candidate specimens for final design review. After acceptance
and a build go, promote the accepted artifacts into explicit test fixtures with
executed expected outcomes; retain unsupported/native/scientific limits in the
release support matrix.
