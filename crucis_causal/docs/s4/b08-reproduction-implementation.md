# B08 exact computational replay

DLV-08, DLV-09.

The [comparator](../../measurement/reproduction.py) checks access and the
original frozen plan before comparing two independently observed and
recorded occurrences. It checks exact plan, procedure, environment and
output-role identity. The local runtime records interpreter and exact
arithmetic library pins together with the relevant configuration and
dependencies bound through planning.

A comparator chooses one output and may name associated diagnostic roles.
It distinguishes selected-role comparison, score-only comparison with a
pinned input mask, and replay that compares a rederived mask. Semantic exact
numeric equality permits an integer and an equal rational representation.
Keyed values, interval endpoints, categorical distinctions and actual
diagnostic causes retain their scope.

The focused local S3 fixtures cover independent exact agreement, same-basis
derived-mask disagreement, changed input basis, original access denial,
interrupted replay and explicitly admitted undefined diagnostics. A replay
compares recorded calculation evidence. It creates no native trial and
establishes no reference truth.
