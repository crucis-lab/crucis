# B09 measurement capsule and local publication

DLV-08, DLV-09, DLV-10.

The [carrier bridge](../../measurement/publication.py) reads the exact
S4 snapshot, resolves its scoped dependency and proof closure and pins
the original canonical bytes in an S1 artifact. An S3 projection declares
the registered S4 typed payload and the complete native dependencies.
Nested S4 dependencies use their already pinned S3 carriers. The bridge
checks both reference dialects and the inner byte identity. An installed
reader does not confer audience approval.

The authorized S3 disclosure policy freezes the exact outward view.
A narrower projection is a separately authored snapshot with its own
scope and dependencies. Publication uses existing S3 admission, storage
and lookup. Pointer CAS has a separate effect boundary.

Local fixtures exercise exact inner bytes, withheld access, nested
dependencies, a narrowed view, loss before and after commit, and stale
pointer revision. They use the actual local S3 store and its receipts.
Remote publication and wider evidence audience authority remain outside
this milestone.
