"""Explicit native return validation/projection; no dataclass wire guessing.

DLV-08/09. Lookup evidence has a different runtime type from start/connection
evidence. Preserve all its coverage fields, rather than an empty fallback view.
"""
from dataclasses import replace
from . import api, codec
from .model import (Builder, ExecutionError, canonical, contract, index, qualified,
    reference, unknown, unknown_ref)
from .schema import validate_value


def combine_deltas(*deltas):
    records, views = {}, {}
    native, scientific, roots = [], [], []
    for delta in deltas:
        if not isinstance(delta, api.RecordDelta): raise ExecutionError('s3.typed_native_evidence_delta_required')
        for record in delta.records:
            if record['id'] in records and canonical(records[record['id']]) != canonical(record): raise ExecutionError('s3.record_identity_conflict')
            records[record['id']] = record
        for view in delta.dependencies:
            if view.package_id in views and views[view.package_id].source_bytes != view.source_bytes: raise ExecutionError('s3.package_identity_conflict')
            views[view.package_id] = view
        native.extend(delta.native_additions); scientific.extend(delta.scientific_additions); roots.extend(delta.roots)
    return api.RecordDelta(tuple(records.values()), tuple(roots), tuple(views.values()), tuple(native), tuple(scientific))


def result_evidence(result, binding, read):
    """Validate the declared return shape and retain the original runtime handles."""
    if not isinstance(result, api.CallResult): raise ExecutionError('s3.driver_return_contract')
    value = result.value
    if result.state == 'rejected':
        if isinstance(value, api.DriverEvidence): return replace(value, records=combine_deltas(result.records, value.records))
        return api.DriverEvidence(binding, result.records, index(extent='unresolved'), index(extent='unresolved'), index(), ())
    # Resolve the exact declared port, not a result class chosen by data.
    resolver = codec.Resolver(read.views, limits=read.limits)
    bound, _ = resolver.record(binding, binding['package_id'])
    from .schema import operation
    port = operation(bound['payload']['operation'])['port']
    expected = {'Driver.invoke': api.NativeStart, 'Driver.lookup': api.LookupResult,
        'Driver.attach': api.NativeConnection, 'Driver.observe': api.NativeBatch}.get(port, api.DriverEvidence)
    if not isinstance(value, expected): raise ExecutionError('s3.native_port_return_type_mismatch')
    if isinstance(value, api.DriverEvidence):
        if value.binding != binding: raise ExecutionError('s3.native_evidence_binding_mismatch')
        return replace(value, records=combine_deltas(result.records, value.records))
    if isinstance(value, api.NativeBatch):
        raise ExecutionError('s3.native_batch_requires_capture_handler')
    if isinstance(value, (api.NativeStart, api.NativeConnection)):
        evidence = value.evidence
        if not isinstance(evidence, api.DriverEvidence) or evidence.binding != binding:
            raise ExecutionError('s3.native_evidence_binding_mismatch')
        if isinstance(value, api.NativeStart):
            validate_value(value.attempt, 'KnownRef(s1.attempt)')
            validate_value(value.native_subject, 'K(KnownRef(native_subject))')
            handle = value.connection
        else:
            validate_value(value.subject, 'KnownRef(native_subject)'); validate_value(value.attempt, 'Ref(s1.attempt)')
            validate_value(value.role, 'Code')
            if not isinstance(value.owner_epoch, str) or not value.owner_epoch: raise ExecutionError('s3.native_connection_epoch_required')
            handle = value.handle
        if handle is not None and not isinstance(handle, api.OpaqueHandle): raise ExecutionError('s3.actual_native_connection_required')
        if isinstance(value, api.NativeConnection) and handle is None: raise ExecutionError('s3.actual_native_connection_required')
        handles = list(evidence.live_handles)
        if handle is not None and not any(h is handle for h in handles): handles.append(handle)
        if any(not isinstance(h, api.OpaqueHandle) for h in handles): raise ExecutionError('s3.actual_native_connection_required')
        return replace(evidence, records=combine_deltas(result.records, evidence.records), live_handles=tuple(handles))
    if not isinstance(value.coverage, api.QueryCoverage) or not isinstance(value.evidence, api.RecordDelta):
        raise ExecutionError('s3.lookup_coverage_evidence_required')
    from .drivers import lookup_evidence, _document
    coverage = value.coverage
    data = lookup_evidence({'classification': value.classification, 'query_binding': value.query_binding,
        'matches': list(value.matches), 'scope': coverage.scope, 'paths': list(coverage.paths), 'interval': coverage.interval,
        'retention': coverage.retention, 'complete': coverage.complete, 'no_late_acceptance': coverage.no_late_acceptance})
    # A query digest is exact scope, not a provider deduplication promise.
    from .journal import binding_digest, resolve_binding
    actual = resolve_binding(binding, binding['package_id'], resolver)
    if value.query_binding != binding_digest(actual): raise ExecutionError('s3.lookup_query_binding_mismatch')
    base = combine_deltas(result.records, value.evidence, coverage.evidence)
    from .coordinator import read_with
    selected = read_with(read, *base.dependencies)
    b = Builder('Explicit native lookup runtime projection')
    doc, storage = _document(b, contract('s3.native.lookup_evidence'), data, selected.views)
    audience = b.add('audience', {'purpose': contract('s3.private_lookup_evidence'), 'recipients': index(),
        'disclosure_policy': unknown_ref('s1.policy'), 'authority': unknown()})
    root = b.add('projection_view', {'view_role': 'audience_projection', 'audience': audience,
        'projection_contract': contract('s3.lookup_runtime_projection'), 'members': index([doc]), 'claims': index(), 'limits': index()})
    selected = read_with(selected, storage)
    view = codec.parse_snapshot(codec.dumps(b.package(root, selected.views), read.limits), read.limits)
    subjects = []
    for record in base.records:
        if record['record_type'] != 's3.native_subject': continue
        source = next((v for v in base.dependencies if any(r['id'] == record['id'] for r in v.records)), None)
        if source is not None: subjects.append(reference(record['id'], 'native_subject', source.package_id))
    delta = combine_deltas(base, api.RecordDelta(view.records, (), (*selected.views, view)))
    return api.DriverEvidence(binding, delta, index(subjects, extent='partial_for_scope' if value.classification == 'positive' else 'unresolved'),
        index([qualified(doc, view.package_id)]), index(), ())
