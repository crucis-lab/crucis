# B10 historical measurement mapping and compatibility

DLV-08, DLV-09, DLV-10.

[Legacy capture](../../measurement/legacy.py) retains exact supplied bytes
and a byte digest. An explicit, versioned, pinned attribution can identify
known reported fields. Missing source attribution, changed bytes, malformed
content and unsupported interpretations have separate dispositions.
An interpreted legacy value remains a reported historical quantity.

Historical adjacency F1, expected and committed direction, reference tiers,
completed and delivered populations, common-key paired bootstrap intervals,
calibration and ranking retain their original scope. A legacy certificate
remains a reported evidence object unless checked by the existing verifier.
S4 preparation and scientific reproduction have their own evidence.

The read-only recorded-data gate passed **1,298 of 1,298** comparisons at
the unchanged tolerance **0.001**. The maximum absolute difference was
**0.000091483427284475**. All **14 stored** and **14 freshly computed**
certificates verified. The runner checked the frozen stored certificates
and paper checkpoint bytes before and after, and verified the protected
legacy runtime paths against the approved source base. The results were
produced with Python 3.12.13 from the B09 base with the legacy route unchanged.
The external recorded-compatibility receipt has SHA-256
`5566ae1466dbcd16607d247b07fdf1b05786109632ab7eb3fdabfa5474f8bcd8`.

These data-backed checks establish historical compatibility. The offline
conformance suite and S4 fixture evidence have distinct scope.
