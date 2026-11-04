"""Durable bounded capture and separately authorized acknowledgement (DLV-08/09).

Cursor order, event measurement and source identity have explicit supplied rules.
The core never infers gap-free replay, interpretation, or native termination.
"""
import copy
from dataclasses import dataclass, replace
import inspect
from . import api, codec
from .coordinator import correlation_id, frozen, read_with, root_of, typed_document
from .journal import delta_binding, source_binding
from .model import Builder, ExecutionError, canonical, contract, digest, index, known, qualified, reference, scope, unknown
from .registry import callable_value, key, _verify_implementation
from .schema import validate_value


@dataclass(frozen=True, slots=True)
class ObservationProfile:
    protocol: dict
    source: api.SuppliedCallable
    measure: api.SuppliedCallable
    resume: api.SuppliedCallable
    advance: api.SuppliedCallable
    implementation: api.PinnedArtifactIdentity
    ack_mode: str = 'separate'


def usage(value):
    if not isinstance(value, dict) or set(value) != {'batch','period','source','events','bytes','batch_digest'}:
        raise ExecutionError('s3.capture_usage_shape')
    for field, expr in [('batch','ID'),('period','KnownRef(collection_period)'),('source','Digest'),
                        ('events','Index'),('bytes','Index'),('batch_digest','Digest')]:
        validate_value(value[field], expr)
    return copy.deepcopy(value)


def progress_payload(entry, *, fetched=None, captured=None, interpreted=None, acknowledged=None, coverage=()):
    """Pure projection only; the caller must supply actual evidence for updates."""
    from .coordinator import relocate
    p = relocate(entry.record['payload'], entry.source_package)
    for field, value in [('fetched',fetched),('durably_captured',captured),('interpreted',interpreted),('acknowledged',acknowledged)]:
        if value is not None:
            validate_value(value, 'K(Cursor)'); p[field] = copy.deepcopy(value)
    p['coverage'] = index(coverage, extent='partial_for_scope')
    return p


class Collector:
    def __init__(self, profiles):
        self.profiles = {}
        for profile in profiles:
            if not isinstance(profile, ObservationProfile) or profile.ack_mode not in ('separate','none'):
                raise ExecutionError('s3.explicit_nonconsuming_capture_profile_required')
            _verify_implementation(profile.implementation)
            for function, arguments in [(profile.source,['binding','inputs','context']), (profile.measure,['batch']),
                (profile.resume,['committed','requested','source']), (profile.advance,['requested','next_cursor','source'])]:
                if list(inspect.signature(callable_value(function)).parameters) != arguments:
                    raise ExecutionError('s3.capture_profile_signature')
            selected = key(profile.protocol)
            if selected in self.profiles: raise ExecutionError('s3.duplicate_capture_profile')
            self.profiles[selected] = profile

    def install(self, registry):
        if not registry.payloads.supports(contract('s3.capture.usage')):
            registry.payloads.register(contract('s3.capture.usage'), usage)

    def _profile(self, binding):
        source = next((e for e in binding.inputs.entries if e.role == 's3.role.source'), None)
        if source is None or source.record['record_type'] != 's3.source_frontier': raise ExecutionError('s3.capture_source_role_required')
        profile = self.profiles.get(key(source.record['payload']['protocol']))
        if profile is None: raise ExecutionError('s3.capture_protocol_unavailable')
        return profile, source

    def dependencies(self, payload, anchor, resolver):
        refs = next(r['members']['members'] for r in payload['roles'] if r['role'] == 's3.role.source')
        if len(refs) != 1: raise ExecutionError('s3.capture_source_role_required')
        # These are explicit new request inputs, not references asserted to be
        # present in the earlier account cutoff. The staged C declares their
        # supplied source packages before any effect can be admitted.
        record, _ = resolver.record(refs[0], refs[0]['package_id'] if refs[0]['binding'] == 'external' else anchor)
        profile = self.profiles.get(key(record['payload']['protocol']))
        if profile is None: raise ExecutionError('s3.capture_protocol_unavailable')
        _verify_implementation(profile.implementation)
        if payload['operation'] == contract('s3.op.observe'):
            mode = next(p['value'] for p in payload['parameters'] if p['key'] == 'ack_mode')
            if mode['state'] != 'known' or mode['value'] != profile.ack_mode: raise ExecutionError('s3.capture_ack_profile_mismatch')
        return (profile.implementation,)

    def _source(self, request, read):
        profile, entry = self._profile(request.binding)
        _verify_implementation(profile.implementation)
        command, pid = codec.Resolver(read.views, limits=read.limits).record(request.command, request.source_view.package_id)
        declared = command['payload']['dependencies']['members']
        if profile.implementation.reference not in declared: raise ExecutionError('s3.capture_rule_source_unpinned')
        expected = callable_value(profile.source)(request.binding, request.inputs, read)
        source_binding(expected)
        if expected.protocol != profile.protocol or expected.subject != qualified(entry.record['payload']['source'], entry.source_package):
            raise ExecutionError('s3.capture_source_binding_mismatch')
        if expected.generation['state'] != 'known' or not expected.generation['value']:
            raise ExecutionError('s3.capture_generation_unestablished')
        if profile.ack_mode == 'separate' and (expected.consumer['state'] != 'known' or not expected.consumer['value']):
            raise ExecutionError('s3.capture_consumer_unestablished')
        return profile, entry, expected

    @staticmethod
    def _current(journal, account, jctx, read):
        result = journal.head(account, jctx)
        if result.state != 'completed': raise ExecutionError('s3.capture_history_unavailable')
        return result.value, read_with(read, *result.records.dependencies, result.value.snapshot)

    def _bounds(self, request, read):
        period = next(e for e in request.inputs.entries if e.role == 's3.role.period')
        resolver = codec.Resolver(read.views, limits=read.limits)
        bounds = resolver.payload(period.record['payload']['bounds'], period.source_package, read.registry.payloads)
        return qualified(period.reference, period.source_package), bounds

    @staticmethod
    def _used(view, read, period):
        totals = [0, 0]; resolver = codec.Resolver(read.views, limits=read.limits)
        seen = set()
        for record in view.records:
            if record['record_type'] != 's3.typed_payload' or record['payload']['payload_contract'] != contract('s3.capture.usage'): continue
            body = resolver.payload(reference(record['id'], 'typed_payload', view.package_id), view.package_id, read.registry.payloads)
            if body['period'] != period: continue
            if body['batch'] in seen: raise ExecutionError('s3.duplicate_capture_accounting')
            seen.add(body['batch']); totals[0] += int(body['events']); totals[1] += int(body['bytes'])
        return totals

    def before(self, request, token, journal, jctx, read):
        profile, _, expected = self._source(request, read)
        params = {p['key']: p['value'] for p in request.binding.record['payload']['parameters']}
        if params['ack_mode']['value'] != profile.ack_mode: raise ExecutionError('s3.capture_ack_profile_mismatch')
        period, bounds = self._bounds(request, read)
        head, current_read = self._current(journal, token.intent_commit.head.account, jctx, read)
        used = self._used(head.snapshot, current_read, period)
        for i, name in enumerate(('max_events','max_bytes')):
            if bounds[name]['state'] == 'known' and used[i] + int(params[name]['value']) > int(bounds[name]['value']):
                raise ExecutionError('s3.collection_bound_exhausted')
        committed = journal.checkpoint(head.account, expected, jctx)
        requested = params['cursor']
        if callable_value(profile.resume)(committed, requested, expected) is not True:
            raise ExecutionError('s3.capture_resume_not_established')
        return expected

    def collect(self, batch, result, request, token, journal, jctx, read):
        if not isinstance(batch, api.NativeBatch): raise ExecutionError('s3.actual_native_batch_required')
        if not isinstance(batch.observations, api.RecordDelta) or result.records.native_additions or result.records.scientific_additions:
            raise ExecutionError('s3.capture_owned_additions_require_freeze')
        profile, original, expected = self._source(request, read)
        if source_binding(batch.source) != source_binding(expected): raise ExecutionError('s3.capture_returned_source_mismatch')
        validate_value(batch.occurrence, 'ID'); validate_value(batch.next_cursor, 'K(Cursor)'); validate_value(batch.coverage, 'Scope')
        if not isinstance(batch.raw, tuple) or not batch.raw or any(not isinstance(r, api.CapturedBytes) for r in batch.raw):
            raise ExecutionError('s3.raw_capture_occurrences_required')
        if batch.source_ack.get('state') == 'known': raise ExecutionError('s3.combined_ack_not_qualified')
        if any(source_binding(r.source) != source_binding(expected) for r in batch.raw): raise ExecutionError('s3.capture_raw_source_mismatch')
        events = callable_value(profile.measure)(batch)
        if isinstance(events, bool) or not isinstance(events, int) or events < 0: raise ExecutionError('s3.capture_measurement_required')
        params = {p['key']: p['value'] for p in request.binding.record['payload']['parameters']}
        byte_count = sum(len(r.bytes) for r in batch.raw)
        if events > int(params['max_events']['value']) or byte_count > int(params['max_bytes']['value']): raise ExecutionError('s3.capture_batch_limit_exceeded')
        if callable_value(profile.advance)(params['cursor'], batch.next_cursor, expected) is not True:
            raise ExecutionError('s3.capture_next_cursor_unestablished')
        period, bounds = self._bounds(request, read)
        raw_binding = [{'occurrence': r.occurrence, 'bytes': digest(r.bytes), 'extent': r.extent,
            'metadata': delta_binding(api.CommitDelta(r.metadata.records, (), r.metadata.dependencies), read.limits)} for r in batch.raw]
        if batch.observations.native_additions or batch.observations.scientific_additions or batch.observations.roots:
            raise ExecutionError('s3.capture_owned_additions_require_freeze')
        batch_hash = digest(canonical({'source': source_binding(expected), 'period': period, 'raw': raw_binding,
            'observations': delta_binding(api.CommitDelta(batch.observations.records, (), batch.observations.dependencies), read.limits),
            'cursor': batch.next_cursor, 'coverage': batch.coverage, 'source_ack': batch.source_ack,
            'command': request.command, 'events': str(events)}))
        head, selected = self._current(journal, token.intent_commit.head.account, jctx, read)
        rid = correlation_id('s3.capture.usage', batch.occurrence)
        prior = journal.capture_transaction(head.account, batch.occurrence, jctx)
        if prior.state == 'completed':
            resolver = codec.Resolver(selected.views, limits=selected.limits)
            body = resolver.payload(reference(rid, 'typed_payload', head.snapshot.package_id), head.snapshot.package_id, selected.registry.payloads)
            if body['batch_digest'] != batch_hash or source_binding(prior.value.source) != source_binding(expected):
                raise ExecutionError('s3.capture_occurrence_conflict')
            return self._evidence(request, prior.value, selected)
        if prior.issues[0].code != 's3.capture_transaction_not_established': raise ExecutionError('s3.capture_commit_unconfirmed')
        totals = self._used(head.snapshot, selected, period)
        for i, name in enumerate(('max_events','max_bytes')):
            if bounds[name]['state'] == 'known' and totals[i] + (events, byte_count)[i] > int(bounds[name]['value']):
                raise ExecutionError('s3.collection_bound_exhausted')
        if head.revision != token.intent_commit.head.revision: raise ExecutionError('s3.capture_head_changed')
        b = Builder('Durable source capture, not interpretation')
        uref, storage = typed_document(b, contract('s3.capture.usage'), usage({'batch': batch.occurrence, 'period': period,
            'source': digest(canonical(source_binding(expected))), 'events': str(events), 'bytes': str(byte_count), 'batch_digest': batch_hash}))
        # Caller-stable capture identity; copied records retain their old identity.
        record = b._records.pop(uref['target']); record['id'] = rid; b._records[rid] = record
        uref = reference(rid, 'typed_payload')
        frontier = b.add('source_frontier', progress_payload(original, fetched=batch.next_cursor, captured=batch.next_cursor,
            interpreted=unknown('s3.raw_capture_not_interpretation'), acknowledged=unknown('s3.separate_ack_not_observed'), coverage=[uref]),
            record_id=correlation_id('s3.capture.frontier', batch.occurrence))
        root = root_of(request.source_view, codec.Resolver(selected.views, limits=read.limits))
        projection = b.add('projection_view', {'view_role': 'audience_projection', 'audience': qualified(root['audience'], request.source_view.package_id),
            'projection_contract': contract('s3.durable_capture'), 'members': index([uref, frontier]), 'claims': index(), 'limits': index()})
        selected = read_with(selected, storage, *result.records.dependencies, *batch.observations.dependencies)
        view = frozen(b, projection, selected)
        delta = api.CommitDelta((*result.records.records, *batch.observations.records, *view.records), (), (*selected.views, view))
        committed = journal.commit_capture(expected, head.revision, batch.occurrence, batch.raw, delta, batch.next_cursor, replace(jctx, read=selected))
        if committed.state != 'completed': raise ExecutionError(committed.issues[0].code)
        _, retained = self._current(journal, head.account, jctx, read_with(selected, view))
        return self._evidence(request, committed.value, retained)

    @staticmethod
    def _evidence(request, capture, read):
        view = capture.commit.head.snapshot
        refs = index([capture.commit.receipt, *capture.artifacts])
        return api.DriverEvidence(reference(request.binding.record['id'], 'operation_binding', request.binding.context['package_id']),
            api.RecordDelta(dependencies=(*read.views, view)), index([capture.source.subject]), refs, index(), ())

    def acknowledgement(self, request, token, journal, jctx, read):
        """Actual retained transaction proof, not a deserialized receipt grant."""
        profile, _, expected = self._source(request, read)
        if profile.ack_mode != 'separate': raise ExecutionError('s3.source_ack_not_supported')
        entry = next(e for e in request.inputs.entries if e.role == 's3.role.capture_receipt')
        payload = entry.record['payload']
        if payload['account']['target'] != token.intent_commit.head.account['target']: raise ExecutionError('s3.ack_capture_account_mismatch')
        original = journal.capture_transaction(token.intent_commit.head.account, payload['transaction'], jctx)
        if original.state != 'completed' or original.value.commit.receipt['target'] != entry.record['id']:
            raise ExecutionError('s3.ack_capture_not_established')
        params = {p['key']: p['value'] for p in request.binding.record['payload']['parameters']}
        cursor = original.value.durable_cursor
        if source_binding(original.value.source) != source_binding(expected) or cursor['state'] != 'known' or params['position']['state'] != 'known' or cursor['value'] != params['position']['value']:
            raise ExecutionError('s3.ack_source_or_position_mismatch')
        if params['protocol']['value'] != profile.protocol: raise ExecutionError('s3.ack_protocol_mismatch')
        return original.value

    @staticmethod
    def salvage(batch, result, request, read, code):
        """Return bounded original bytes without granting durable source progress."""
        from .drivers import _capture
        views, artifacts = [], []
        if not isinstance(batch.raw, tuple) or sum(len(r.bytes) for r in batch.raw if isinstance(r, api.CapturedBytes) and isinstance(r.bytes, bytes)) > int(read.limits.max_external_bytes):
            raise ExecutionError('s3.failed_capture_retention_limit')
        for raw in batch.raw:
            if not isinstance(raw, api.CapturedBytes) or not isinstance(raw.bytes, bytes): continue
            ref, view = _capture(raw.bytes, {'name': 's1.octets', 'version': '0.1.0-proposal.1'}, read.views)
            artifacts.append(ref); views.append(view)
        selected = read_with(read, *views)
        b = Builder('Uncommitted raw observation retention')
        gap = b.add('diagnostic', {'code': code, 'scope': scope(request.command),
            'details': 'Original bounded raw bytes retained; no committed source progress, interpretation or ACK established.', 'evidence': artifacts})
        root = root_of(request.source_view, codec.Resolver(read.views, limits=read.limits))
        projection = b.add('projection_view', {'view_role': 'audience_projection', 'audience': qualified(root['audience'], request.source_view.package_id),
            'projection_contract': contract('s3.uncommitted_raw_retention'), 'members': index([gap, *artifacts], extent='partial_for_scope'), 'claims': index(), 'limits': index([gap])})
        view = frozen(b, projection, selected)
        extras = [d for d in (result.records, batch.observations, *(r.metadata for r in batch.raw if isinstance(r, api.CapturedBytes))) if isinstance(d, api.RecordDelta)]
        return api.DriverEvidence(reference(request.binding.record['id'], 'operation_binding', request.binding.context['package_id']),
            api.RecordDelta(view.records, (), (*selected.views, view), tuple(x for d in extras for x in d.native_additions),
                tuple(x for d in extras for x in d.scientific_additions)), index(extent='unresolved'), index(artifacts), index(), ())
