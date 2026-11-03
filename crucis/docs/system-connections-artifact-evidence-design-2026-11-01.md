# W2 system connections: Block 7, artifact identity, availability and integrity (1 Nov 2026)

Tickets: DLV-08, DLV-09; neighbours DLV-10, ADV-01, DLV-06.
Status: design discussion only. No implementation, verification-rule change, result migration or file repair.
Predecessor: `system-connections-output-index-design-2026-11-01.md`; update/history rules:
`system-connections-outcome-observations-design-2026-11-01.md`.

## 1. Accepted direction and boundaries

Uzair accepted Block 6's boundary: a small shared output-object descriptor, explicit semantic contracts and
typed relationships between native objects, standardized interpretations and derived views. Producer, role
and derivation remain distinct; multiple objects and representations do not automatically mean multiple runs.
Earlier accepted outcome, identity, request and information-boundary directions remain in force.

This document proposes Block 7's evidence model. Exact schemas, storage, resolver behavior and integrity
policies remain open. No implementation go was given. W2-5 through W2-9 remain pending. Shared protocol and
paper-contract changes still go through W5. Nothing here authorizes moving result folders or changing pins.

## 2. Four questions that must remain separate

| Question | Meaning |
|---|---|
| Artifact identity | Which evidenced artifact declaration or captured content snapshot is referenced? |
| Location | Where can that content be obtained, or where was it observed? |
| Availability | What could a particular observer retrieve/read at a particular time and scope? |
| Integrity | Which claimed/expected content or structure did an actual check compare, and what did it establish? |

An artifact is the concrete evidence representation: a response body, file, array container, model checkpoint,
archive member, manifest or captured log segment. Block 6 describes scientific/semantic objects; Block 7
describes the evidence representations supporting them. One artifact can support several objects, and one
object can require several artifacts.

A path is a location, not immutable content identity. A digest identifies content at its stated scope, not
a unique run. An external handle is a reference, not proof that its bytes are captured or even accessible.
Byte equality, source provenance, interpretability, scientific correctness and ability to rerun are separate claims.

## 3. Artifact declarations, captured snapshots and content fingerprints

Use stable handles to reference artifacts, with the following distinctions:

- A native declaration can say an artifact exists and provide a native ID/location/digest. Preserve its source
  and reported status without claiming we captured the bytes.
- A captured snapshot identifies specific observed content and its capture circumstances. Known byte identity
  can be fingerprinted with an algorithm and digest; a later change is a different snapshot, not an unnoticed
  mutation of this evidence reference.
- Locations and their retrieval observations attach to declarations/snapshots as justified by evidence.
  Several verified copies can provide the same content at different locations.

These are semantic distinctions, not a requirement for separate files or elaborate classes. A simple local
case can use one descriptor containing its snapshot identity, observed location, digest and capture evidence.
Unknown or mismatched content must not be silently bound to the expected artifact just because its filename fits.

Multiple native occurrences can produce identical bytes. Shared storage can deduplicate those bytes while
preserving the distinct occurrence/source relationships. Conversely, copying or reimporting an existing
snapshot does not imply another native execution. Object and attempt identity use the earlier blocks.

## 4. Small common artifact descriptor and its observations

Illustrative requirements below do not freeze field names or a storage backend.

| Part | What it answers |
|---|---|
| Stable artifact/source handle | Which declaration/snapshot is this, and which native occurrence or derived producer is known? Unknown origin stays unknown. |
| Representation description | Format/type version, encoding/container or compression, known size/byte span and capture completeness at a stated interface. |
| Origin and capture provenance | Native output, supplied input, observer capture, verified copy, reconstructed artifact or auditor derivation; producing/capturing component and evidence/time references. |
| Locations and retrieval observations | Source-scoped locators, relevant package/root context, observer, time, retrieval result and actual known content association. |
| Fingerprint claims | Algorithm, digest, exact scope, expected/reported/computed basis, reference source and time. Omit unknown digests rather than inventing them. |
| Integrity-check observations | Checked snapshot, reference, procedure/version, comparison scope, result/diagnostic and relevant limitations. |
| Dependencies and source locators | Manifest members or required companion artifacts; precise selectors/keys/ranges bound to the correct immutable container version. |
| Availability and verification limits | What was or is accessible to whom, partial/incomplete capture, unsupported interpretation, unresolved identity or other evidence gaps. |

Status can change through new observations, as in Block 5. A descriptor/reference need not duplicate the whole
availability history. Current convenience views can point to selected observations, while publications and
derivations identify the exact snapshot/check evidence they used.

## 5. Availability is an observation, not a timeless boolean

Distinguish at least the following situations where relevant:

- Bytes were captured/read by a specified observer, at a specified location/time, with a known scope.
- A reference or native declaration exists, but the observer has not retrieved the content.
- Retrieval at a location returned not-found, denied, expired/unusable reference or another evidenced result.
- Only part of a stream/file/container was captured; known byte/span coverage is preserved.
- Content is intentionally restricted to an authorized holder; the public observer can inspect only a manifest
  or allowed aggregate. Do not move restricted material to make a public record appear complete.
- Original content is unavailable, though a derived representation or other supporting evidence survives.
- Availability or original capture completeness is unknown.

Use only the retrieval reason actually supported. Access denied does not prove content absence; a missing
local path does not prove the original system failed to produce the artifact. An artifact available to one
observer need not be available to every reader. A hash in a manifest is not retrieval of the corresponding bytes.

Availability and parsing are separate: a captured file may be unreadable under the current interpreter,
well-formed but an unsupported format, or interpretable but scientifically invalid. Block 5/6 references
preserve those distinctions. A deleted file does not retroactively mean no capture occurred if the capture
is evidenced, but future independent rechecks may then be unavailable.

## 6. What integrity checks can and cannot establish

### Exact bytes

An exact-byte check records the content snapshot read, digest algorithm/value, expected reference and its
provenance, whether the whole required content was available, and the comparison result. Matching supports
the claim that observed content matches that reference under the check. Record which component computed a
digest versus which source merely reported it. A matching digest does not by itself establish native authorship,
truth of causal claims, correct parsing, complete provenance or the ability to rerun a system.

The trust/evidence basis of the expected reference matters. Two values supplied by the same unverified source
may be internally consistent without independently establishing origin. An opaque provider token is not
called a content digest unless its meaning and verification procedure are established. Signing/attestation,
if ever needed, is a separate design choice; this block does not add an approval/security workflow.

### Canonical or semantic views

A file with different whitespace, key order, line endings or packaging can have different bytes while a
defined interpretation yields equivalent values. Record this as a separate comparison under a named,
versioned canonicalization or semantic procedure, with its scope and known information loss.
Do not use a canonicalized value match to claim unchanged native bytes or silently satisfy an exact-byte gate.
The original artifact remains preserved and distinct from the canonical/derived representation.

Numerical tolerances are yet another procedure. Existing cross-host numeric tolerance does not apply to file
hashes. Equal reported scores do not establish identical underlying evidence. This proposal does not change
the current certificate's raw-file checks, count exactness or numerical tolerance.

### Consistent capture and dependency scope

Hashing one version of a changing file and parsing another must not be reported as one coherent verified
snapshot. Future capture/check mechanisms must establish which content was actually interpreted. Size/mtime
or a path alone cannot guarantee that. How stable capture is implemented is still open.

For a multi-artifact object, identify required dependencies and check the relevant members. Verifying an edge
file alone cannot establish the integrity of an unavailable node schema or associated weights. Report checks
at their actual scope rather than upgrading one successful member check into a whole-bundle pass.

## 7. Concrete cases: missing, changed, copied and restricted evidence

The following are hypothetical design cases, not new file checks or experimental results.

| Case | Situation | Required representation and conclusion |
|---|---|---|
| F01 | A captured output matches the independently recorded expected byte digest. | Record snapshot, computed digest, reference and successful check scope. Interpretation and causal accuracy remain separate. |
| F02 | A referenced local path is now missing. | Preserve expected artifact identity and the new not-found observation. Do not assert it was never produced or rewrite the native attempt as a crash. |
| F03 | The same path now contains bytes that fail the expected digest. | Preserve expected reference and observed different snapshot/candidate; record mismatch. Do not update the expected digest to make it pass. Cause may be unknown. |
| F04 | A file is renamed or copied and the new location supplies the expected content. | Add verified location/copy evidence for that content; source occurrence remains unchanged. No new native execution. |
| F05 | Two independent native attempts emit identical bytes. | Byte storage can be shared; occurrence and object provenance stay distinct. |
| F06 | JSON formatting changes but the parsed graph is equivalent under a defined procedure. | Exact-byte difference remains. Separate semantic-equivalence result names its procedure and scope. |
| F07 | Native file is unavailable but an earlier interpreted graph survives. | Retain the graph and known derivation, with native reinspection unavailable. Do not relabel the graph view as recovered original bytes. |
| F08 | Remote service provides a handle or declared checksum but content cannot be retrieved. | Preserve reference/report and actual access result; no locally verified content claim. |
| F09 | A stream/log was captured only through a particular byte span. | Identify that snapshot/span and completeness limits. Its digest covers only those bytes. |
| F10 | A native log legitimately grows after a captured snapshot. | New content observation/snapshot linked to the evolving source; earlier prefix is not automatically corrupt. |
| F11 | An archive and its extracted members have different byte identities. | Retain container/member identities, locators and extraction provenance. A container digest is not a member digest. |
| F12 | A graph depends on node/edge/weight artifacts and only some are available. | Localize availability/integrity checks; full object interpretation may remain unavailable or partial. |
| F13 | Artifact is accessible only to an authorized holder. | State who can check which evidence and what public references support; do not claim a public reader possesses it. |
| F14 | A provider reports one digest but a collector computes another for the purported object. | Preserve both claims, observed content and their source/scope; disputed association or integrity remains explicit. |
| F15 | A backup later restores the exact expected content. | Add restored availability and matching-content evidence; earlier not-found observation remains valid at its time/location. |
| F16 | A new interpreter produces a different normalized graph from unchanged native bytes. | Native byte identity is stable; new interpretation/version/provenance carries the changed meaning and diagnostics. |
| F17 | An artifact is reconstructed or a system is rerun to recreate an output. | New derivation or new native attempt as appropriate; identical bytes do not turn it into the original capture occurrence. |
| F18 | A zero-length file exists where an output was expected. | Preserve observed empty bytes. Existence alone does not establish a valid native empty graph or task fulfillment. |

### One missing-file walkthrough

An earlier assessment references captured native content and an expected digest. A later observer cannot find
it at the recorded location. Block 7 adds that retrieval observation; Block 5 can state that fresh native-byte
verification is unavailable. Any earlier successful check remains evidence about the snapshot it checked.

A verified backup is subsequently found and supplies matching content. Add the new location/copy/check
observations, preserving earlier not-found evidence. The native attempt has not rerun, and no original delivery
time is invented. If the backup content does not match, preserve it as a different candidate snapshot; do not
quietly substitute it for the pinned evidence because it produces similar scores.

## 8. Changes, mutable sources and manifests

A logical source slot such as the latest log/checkpoint can evolve. References used for interpretation or
publication should bind to a specific evidenced snapshot, not an unpinned current path/URL. New snapshots can
link to the same source slot and their predecessor/derivation without overwriting previous content identity.

For manifests, record the member identities, relevant roles and locator/ordering semantics under a versioned
manifest contract. A directory or archive name alone does not identify a stable collection. If member metadata,
ordering or relative layout is part of a particular claim, the manifest must preserve it; do not assume it is
irrelevant. Exact packaging and hash-tree designs are still open.

Restoring bytes from a backup, reconstructing bytes from earlier evidence and reexecuting the audited system
have different provenance. Matching content can support recovery of the expected byte representation; it does
not establish that a newly reconstructed artifact was originally captured or that a rerun is the same event.
Relations to native occurrences, derivations and imports remain governed by Blocks 1/6/8.

## 9. Minimum requirements and generic core responsibilities

For a small local case, the descriptor can be compact: artifact handle, source/role, format, observed location,
capture/availability evidence, computed content digest if available, and explicit check references where a
comparison was performed. Do not invent a verification result merely because a digest was computed.

Richer cases add only relevant container/member/dependency, byte-span, multi-location or restricted-access
information. Content-addressed storage is an implementation option, not a requirement to copy all artifacts
into the repository. Existing ownership, data-retention and sealed-battery boundaries remain in force.

Reusable core mechanisms can represent artifact declarations/snapshots, resolve authorized locators, record
retrieval observations, fingerprint captured content and link checks to exact dependencies. Adapters expose
native artifact locations, formats, source identifiers and available checksums with their evidence basis.
Unknown formats/remote evidence do not require algorithm-specific changes to the artifact descriptor.

The main cost is more explicit references and observations than a path-plus-hash dictionary. The strongest
simpler alternative fits the current local recorded audits but conflates missing paths, different bytes,
external claims and observer-specific access. Keep the richer contract small in simple cases rather than
requiring every artifact to have every optional metadata category.

## 10. Current implementation, checks and next step

Current `audit/core/canon.py` fingerprints files/canonical JSON, `audit/core/evidence.py` links values to
file hashes/pointers, and `audit/report/certificate.py` checks raw-file paths/hashes plus recomputed results.
The current certificate reports absent and mismatching paths in one files_changed list. That is an existing
interface limitation to account for in a later migration, not a change made here. Current verification behavior
and every historical gate remain unchanged.

Before implementation, the design must demonstrate that F01-F18 can preserve source, location, time, actual
capture/check scope and gaps without silently replacing expected evidence, fabricating bytes/digests, erasing
earlier observations, counting a copy/import as another run, or treating a byte match as scientific correctness.
An object must reference the snapshot actually interpreted; successful checks on some members cannot stand
in for a full dependency check. Availability and interpretation remain separately representable.

No implementation or tests were written or executed. Only this new design record was written. No files were
moved, repaired, deleted or restored, and no remote artifacts or sealed material were fetched. The next
discussion can settle Block 7's identity/location/availability/integrity boundary, then develop Block 8's
conditional relationships and limitations.
