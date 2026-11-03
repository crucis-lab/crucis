<!-- Current status: S2-A through S2-I implemented; final S2-I/run3 passed. Repository CI has the separate existing DLV-07 pin drift. -->
# Subsystem 2 implementation log

Tickets: DLV-08, DLV-09, DLV-10.
Local date: 2 Nov 2026, America/Los_Angeles.

Uzair accepted the final S2 design and authorized detailed implementation of all
nine bundles in this chat: "I'll approve this final design. Let's proceed onward
with the detailed implementations of the bundles." This supersedes the earlier
candidate documents' pending-acceptance/build status, not their frozen contents.
Public protocol adoption, spending, native execution and owner-controlled actions
remain separate. No git writes or protected/shared logic edits are authorized.

## Accepted baseline and entry checks

The 53 accepted candidate file hashes match the final review receipt and are pinned
in `../_w2_checks/2026-11-02_s2_build/accepted-design.json`. An execution-only copy of
the DAG supplies the legacy plan-check tool's date/approval fields without changing
the accepted candidate. `tracker/plan_check.py` passed for nine bundles and no API
spend. This check is read-only; mutating tracker trace checks are not run.

The original 64-file digest is
`d615f61a2ce46862b9093ee7309374c825a5684dcf0d4561453a7d71444e42ae`.
The approved S1 44-file manifest digest is
`b23093ae21538dd36436c7544f00e3ae1df35255924cadda97d98afa51478256`.
Both match before implementation. Python is the local Codex 3.12.14 runtime;
NumPy 2.3.5 is present. Exact S1 dependencies, including jsonschema 4.25.1, are
reused from the existing `_w2_checks/2026-11-01_s1_build/dependencies` directory;
no installation or network operation is necessary.

Entry attempts are retained separately. The default sandbox temporary directory
denied nested writes. An explicit visualization temporary root fixed ordinary
writes but sandbox hard-link restrictions prevented immutable-store publication.
Normal filesystem access fixed hard links; its long temporary path then exposed
Windows alias-filename length failures at `audit/connections/store.py:38`.
The next attempt uses a short system-temporary subdirectory outside DSC under
normal filesystem access. No S1 source, test, publication rule or tolerance is
changed to bypass these environmental failures. Synthetic tests alone access
temporary dummy sealed fixtures; real stores, seeds and read ledgers are untouched.

## Bundle evidence

Execution state and gate receipts are recorded outside the repo under
`../_w2_checks/2026-11-02_s2_build/`. A bundle advances only after its required
predecessor and common preservation gates pass. Product tests and actual evidence
will be distinguished from the earlier documentation-only checks.

## Where we're going

Finish the entry gate, then implement S2-A through S2-I in dependency order with
exact scoped acceptance tests, stored result/certificate preservation and explicit
limitations. No source account or synthetic example becomes native scientific
evidence merely because its record validates.

## Entry and A-F results

The short-temp entry gate passed: 140 tests (139 passed, one optional native-PC
skip), 1,298 stored-number comparisons with maximum absolute difference
0.000091483427284475, exact key/count/verdict parity, 14 stored and 14 fresh
certificates verified. Receipts: `entry-short-temp/gate.json`.

| Bundle | Accepted receipt under the external evidence root | Full suite tests | Scope added |
|---|---|---:|---|
| S2-A | S2-A/run2/gate.json | 158 | Exact wire, 40 record kinds, 25 parameter schemas, 11 typed payload formats, explicit resolver |
| S2-B | S2-B/run1/gate.json | 173 | Atomic staging, identity services, exact registries, independent profiles |
| S2-C | S2-C/run1/gate.json | 182 | Case and collection ownership, selection, reference and response semantics |
| S2-D | S2-D/run1/gate.json | 198 | Information channels, materialization evidence, domain/family boundaries, run binding |
| S2-E | S2-E/run1/gate.json | 210 | Explicit populations, missingness and evaluation bindings without metric computation |
| S2-F | S2-F/run1/gate.json | 220 | Earlier-byte commitments, amendments, adaptive decisions and retained exposure |

Every row passed the common preservation gate and retained the same one optional
skip, all 1,298 comparisons, certificates and original/S1 implementation identities.
The tests establish metadata semantics and recorded compatibility, not fresh native
system accuracy, causal validity, execution authority or public protocol adoption.

G focused testing exposed an in-memory versus encoded package ordering mismatch in
`S2RecordWriter.frozen`. Frozen and staging views now reparse their canonical bytes;
the resolver continues rejecting any caller-constructed view whose bytes disagree.
All ten G focused tests pass after this correction. The full G receipt is pending.

Implementation clarifications: the exact projection registry's response key is the
response definition's versioned fulfillment rule. S2 compiler provenance captures
the actual S2 implementation manifest; it does not reuse S1's default manifest.
Recorded imports consume explicitly supplied S1 snapshots, never locator discovery.

## G/H handoff and compatibility scope

S2-G/run1 passed with 230 full-suite tests, including ten new handoff tests, and
all common preservation checks. The compiled request uses the exact native
operation, response roles/cardinalities, information policy and permitted payloads.
It does not dispatch or create runtime authority. R and O use fresh package IDs;
copied records retain exact IDs/content. H pins the verified R bytes.

H focused checks pass for all eight existing recorded adapters, without native
run calls. Source-backed echo has the S1 encoded-value contract scope, including
status, graph/variants/stages, confidence, reported costs and nested occurrences.
It does not promise original-file bytes. The new importer consumes supplied S1
snapshots and does not traverse historical RunRecord.files locators. Item/battery
manifests can be preserved through a separately named safe S1 codec. No typed
scientific task, commitment, independence, repetition or complete population is
reconstructed from legacy labels. A narrow explicit compatibility view delegates
the actual graph/status/coordinate projection to unchanged S1 code and reports
lost guarantees. Repeated legacy keys reject; neither last nor best is selected.

The accepted design, source mappings and earlier methodology index remain frozen
historical artifacts. New implementation evidence will be indexed in a separately
dated release note/addendum so those accepted hashes retain their original meaning.

## I acceptance refinements and final-gate preparation

S2-H/run1 passed with 239 full-suite tests and the existing optional skip; all
common comparisons/certificates and original/S1 identities remained unchanged.
The final integration focused pass ran 91 tests successfully. It executes all 58
adverse specifications and 20 API scenarios, with additional scope/recovery/CLI
checks. Semantic scenarios reuse functional fixtures with established prerequisites;
wire/byte scenarios apply their exact accepted mutations. These are overlapping
conformance assertions, not 78 independent experiments or measured native coverage.

Two illustrative expected operation states required stricter implemented outcomes:
API09's unestablished run/request preview rejects actual handoff admission rather
than passing without native-support/compiler correspondence. A generated supported
R/H path passes separately. API11's evidence link does not establish a complete
intended population or sourced native trial/output associations, so it retains a
partial receipt. A complete current metadata-population path passes separately.
The accepted source files remain unchanged; the final ledger records both original
expectations and these refinements. Scientific faithfulness takes precedence over
making an illustrative preview appear ready.

Final review added direct response-cardinality bounds, referenced/package critical
extension checks, conservative graph/order scope, rejection of particle/retry units
and unsupported population weights, retained missing particle associations, explicit
source-only declaration import, cross-writer durable import recovery, and rollback
when an injected legacy callback commits staging then rejects. All 28 capability
and composite review scopes preserve without automatically satisfying native binding.

A durable recorded MatMCD preflight passed under S2-I-recorded-preflight: deterministic
inspection, import/report, exact encoded echo, validation and a pinned S2 evidence
association. This is observer metadata about already captured evidence, not a fresh
native run or recovered original native history. The final I gate repeats it.

The separate read-only repository CI check reports one existing DLV-07 pin drift at
tools/export_q1.py. STATE.md lines 28 and 55 already identify the October 31 optional
ALLOW_AUDIT export patch and pending owner repin. The current diff is that same
optional --with-audit addition. This S2 implementation does not edit that file or
repin tracker evidence. The final S2 gate and whole-repository CI are reported
separately; a green S2 gate must not be called a wholly green repository check.

## Final integrity and profile corrections

I/run1 and I/run2 passed their respective code snapshots; they remain historical
receipts. The release run is I/run3, which must pass before final completion.
Two byte/value checks were added and tested: snapshot input must be immutable bytes,
and safe legacy decoding must round-trip its exact encoded value. An encoded dict
with duplicate keys cannot silently lose an entry while claiming lossless echo.
The original captured bytes remain available after rejecting that interpretation.

The final profile review also found that a partial injected assessment procedure's
passing subrecord could incorrectly satisfy the aggregate profile. Its explicit
gaps now withhold that profile; the useful passing assertion is retained as its own
source record. An unknown finite response-group bound now produces an unknown
assessment with a gap rather than a false failure or observer exception. Both new
regression cases passed in S2-I-profile-final.log. I/run3 repeats the full common
gate and all acceptance cases for this final code.

The read-only export diagnosis confirms tools/export_q1.py has SHA256
345e60638dc34190765b04f0f269a106ddb7a4b0639eed02c05a73f562a21f47,
exactly equal to jobs/patches/w2_01/export_q1.py. This establishes that the CI pin
drift is the preserved earlier patch, not an S2 change.

## Release result: all nine implementation bundles passed

Final receipt: ../_w2_checks/2026-11-02_s2_build/S2-I/run3/gate.json.
All S2-A through S2-I predecessor/common gates passed. The final full appropriate
audit suite ran 334 tests: 333 passed, no failures/errors, one existing optional
native-PC skip (test_audit_rerun.TestLiveBaseline.test_pc_live_equals_stored_row;
causal-learn is absent). This comprises the original/S1 140-test inventory and
194 S2 tests. Acceptance assertions overlap; these are not empirical sample counts.

The final ledger executes 58 adverse cases, 20 API scenarios and maps all 66
must-show rows. Its SHA256 is
f2f56ee8c737faca1438defd3107f9c1f9634e956de5a09aab1c91d223face91.
The final gate records 79 new runtime/catalog/dependency/test/fixture identities,
compiles Python outside the repo, and confirms those identities stayed unchanged
during the gate. The original 64-file and S1 44-file identities match their expected
values above. All 53 accepted design source hashes still match.

All 1,298 stored comparisons pass at the unchanged 0.001 tolerance; maximum absolute
difference is 0.000091483427284475. Comparison keys, exact counts and finding
kinds/verdicts match. Four recorded S1 import/validation paths pass. All 14 stored
and 14 freshly recomputed certificates verify. The durable S2 MatMCD CLI/import/
report/echo/validation/evidence-binding path passes under S2-I/run3/s2-recorded-matmcd.
It uses captured history and makes no fresh-native accuracy claim.

S2-G/run1 (230 tests), S2-H/run1 (239) and final S2-I/run3 (334) complete the A-F
ledger above. I/run1 and I/run2 remain passed earlier source snapshots; run3 is the
release receipt and includes the final profile/unknown-bound fixes. Failed entry
and focused attempts remain retained for diagnosis.

The implemented-scope note, methodology implementation index/JSON, runtime README
and prepared commit message form the review handoff. The separate repository CI
check still reports the pre-existing DLV-07 export pin drift; no tracker/paper/site
updates or git writes are made. No API spend, native causal-discovery dispatch,
real protected-store access, result moves or port_map publication occurred.

## Where we're going after this release

Subsystem 2's approved metadata scope is implemented and its gates passed. Use the
new methodology index with the frozen accepted design when describing the method
in the paper. Review subsystem 3's execution, authority, observation and recovery
design next; scientific measurements belong to S4. Neither is implemented here.
Uzair/W5 retain review/commit, DLV-07 repinning, public adoption and durable archival
of external evidence and paper pointers.
