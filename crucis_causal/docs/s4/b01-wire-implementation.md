# B01 bounded measurement wire

DLV-08, DLV-09. This milestone implements the first S4 measurement package
codec under the [approved build entry](approved-2026-11-04/build-entry.json).

The [wire schema](../../measurement/wire.schema.json) defines the closed
record families and exact reference, number and disposition forms.
The [codec](../../measurement/codec.py) checks strict bytes, canonical
ordering, bounded size and traversal, local targets and selectors,
artifact range consistency, and the local proof graph. It checks both
directions of the calculation-to-emission association. Calculation
emission backlinks and typed relation endpoints are navigation edges.

The wire fixtures cover graph and local judgment, ordering, forecast loss,
paired enclosure, finite posterior and exact replay. Their external
sources are symbolic. The fixtures qualify codec behavior at this scope.
External dependency resolution, audience access, applicability, actual
calculation evidence, evaluator arithmetic, and scientific qualification
are gates of subsequent bundles. Resource limits for those operations
are carried by the limits contract for their respective consumers.

The focused suite uses committed canonical fixture bytes and pressure
cases for malformed shape, wrong versions, duplicate fields and emissions,
unresolved versus undefined outcomes, exact limits, bad local selectors
and circular proof dependencies. Run it with:

```text
python -B -m unittest discover -s tests -p test_audit_measurement_wire.py -v
```
