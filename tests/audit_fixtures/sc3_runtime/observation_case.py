"""Explicit synthetic nonconsuming source mechanics; no real backend (DLV-08/09)."""
import base64
import copy
from dataclasses import replace
import json
from pathlib import Path
import dispatch_case as case
from crucis_causal.execution import api, codec
from crucis_causal.execution.authority import DriverBoundary
from crucis_causal.execution.collection import Collector, ObservationProfile
from crucis_causal.execution.coordinator import read_with, typed_document
from crucis_causal.execution.drivers import _capture
from crucis_causal.execution.effects import EffectDriver, EffectMethod
from crucis_causal.execution.identity import coordinate
from crucis_causal.execution.journal import source_binding
from crucis_causal.execution.model import (Builder, ExecutionError, canonical, contract, digest, identity,
    index, known, not_applicable, number, qualified, reference, scope, unknown, unknown_ref)
from crucis_causal.execution.registry import supplied_callable

OPS = (contract('s3.op.observe'), contract('s3.op.acknowledge'))
PROTOCOL = contract('s3.fixture.replay_stream')


def cursor(position, source):
    return {'contract': contract('s3.fixture.offset_cursor'), 'position': digest(canonical(source_binding(source)))['value'] + ':' + str(position), 'scope': scope(source.subject)}


def position(value, source):
    if value['state'] != 'known' or set(value['value']) != {'contract','position','scope'}:
        raise ExecutionError('s3.fixture_cursor_unestablished')
    item = value['value']
    prefix, _, offset = item['position'].partition(':')
    if item['contract'] != contract('s3.fixture.offset_cursor') or item['scope'] != scope(source.subject) or prefix != digest(canonical(source_binding(source)))['value'] or not offset.isdigit():
        raise ExecutionError('s3.fixture_cursor_scope_mismatch')
    return int(offset)


def resume(committed, requested, source):
    if committed['state'] == 'unresolved': return requested['state'] == 'not_applicable'
    return position(committed, source) == position(requested, source)


def advance(requested, next_cursor, source):
    start = 0 if requested['state'] == 'not_applicable' else position(requested, source)
    return start <= position(next_cursor, source) <= 3


def measure(batch): return len(batch.raw)


def source_identity(binding, inputs, context):
    entry = next(e for e in inputs.entries if e.role == 's3.role.source')
    p = entry.record['payload']; resolver = codec.Resolver(context.views, limits=context.limits)
    if p['filter']['state'] != 'known': raise ExecutionError('s3.fixture_filter_missing')
    params = case.content(resolver, p['filter']['value'], entry.source_package, contract('s3.fixture.stream_filter'))
    if set(params) != {'kind','partition','consumer'} or params['kind'] != 'all_fixture_events' or params['partition'] not in ('p0','p1') or not isinstance(params['consumer'], str) or not params['consumer']:
        raise ExecutionError('s3.fixture_filter_unsupported')
    # This explicit identity rule uses the generation value, not the changing
    # evidence about it. Original knowledge/provenance stays in the source record.
    generation = known(p['generation']['value']) if p['generation']['state'] == 'known' else p['generation']
    return api.SourceIdentity(qualified(p['source'], entry.source_package), p['protocol'], digest(canonical(params)), generation, known(params['consumer']), contract('s3.fixture.source_filter_generation_consumer'))


class Mechanics:
    def __init__(self, env): self.env = env

    def prepare(self, binding, inputs, context):
        source = source_identity(binding, inputs, context)
        entry = next(e for e in inputs.entries if e.role == 's3.role.source')
        resolver = codec.Resolver(context.views, limits=context.limits)
        native, pid = resolver.record(entry.record['payload']['source'], entry.source_package)
        descriptor = case.content(resolver, native['payload']['descriptor'], pid, contract('s3.payload.native_descriptor'))
        coordinate(descriptor)
        if source.generation['state'] != 'known' or descriptor['incarnation']['state'] != 'known' or source.generation['value'] != descriptor['incarnation']['value']: raise ExecutionError('s3.fixture_source_incarnation_mismatch')
        filt = case.content(resolver, entry.record['payload']['filter']['value'], entry.source_package, contract('s3.fixture.stream_filter'))
        params = {p['key']: p['value'] for p in binding.record['payload']['parameters']}
        common = {'descriptor': descriptor, 'epoch': self.env.client.epoch, 'partition': filt['partition'], 'consumer': filt['consumer'], 'filter_digest': source.filter_digest['value']}
        if binding.record['payload']['operation'] == OPS[0]:
            if params['ack_mode'] != known('separate') or params['deadline_rule'] != known(contract('s3.fixture.logical_tick_deadline')) or params['deadline']['value'] != deadline():
                raise ExecutionError('s3.fixture_observation_profile_unsupported')
            offset = 0 if params['cursor']['state'] == 'not_applicable' else position(params['cursor'], source)
            return common | {'position': str(offset), 'max_events': params['max_events']['value'], 'max_bytes': params['max_bytes']['value'], 'deadline': 'fixture_tick:10'}
        if params['protocol'] != known(PROTOCOL): raise ExecutionError('s3.fixture_ack_protocol_mismatch')
        return common | {'position': str(position(params['position'], source))}

    def observe(self, call):
        try: raw, data = self.env.client.raw('observe', **call.invocation, transmission=call.transmission['target'])
        except case.ReplyError as exc: return self.rejected_reply(call,exc)
        source = source_identity(call.request.binding, call.request.inputs, call.context.read)
        actual = replace(source, generation=known(data['generation']), consumer=known(data['consumer']),
            filter_digest={**source.filter_digest, 'value': data['filter_digest']})
        b = Builder('Reported native event associations, not capture deduplication')
        envelope, envelope_view = _capture(raw, {'name': 's1.json','version': '0.1.0-proposal.1'}, call.context.read.views)
        stores, refs, captured = [envelope_view], [], []
        for entry in data['entries']:
            body = base64.b64decode(entry['bytes'], validate=True)
            meta, storage = typed_document(b, contract('s3.fixture.native_event'), {'native_event': entry['event'], 'native_sequence': entry['sequence'],
                'transport_offset': entry['offset'], 'capture': entry['capture'], 'partition': data['partition'], 'source': digest(canonical(source_binding(actual))), 'bytes_digest': digest(body)})
            refs.append(meta); stores.append(storage)
            captured.append(api.CapturedBytes(entry['capture'], actual, body, scope(source.subject), api.RecordDelta()))
        audience = b.add('audience', {'purpose': contract('s3.private_fixture'), 'recipients': index(), 'disclosure_policy': unknown_ref('s1.policy'), 'authority': unknown()})
        root = b.add('projection_view', {'view_role': 'audience_projection', 'audience': audience, 'projection_contract': contract('s3.fixture.fetched_events'),
            'members': index([envelope, *refs], extent='partial_for_scope'), 'claims': index(), 'limits': index()})
        view = case.frame(b, root, (*call.context.read.views, *stores))
        observations = api.RecordDelta(view.records, (), (*call.context.read.views, *stores, view))
        batch = api.NativeBatch(actual, data['batch'], tuple(captured), observations, known(cursor(data['next_position'], source)), scope(source.subject), not_applicable('s3.separate_source_ack'))
        return api.CallResult('completed', batch, effects=(api.EffectBoundary(call.request.command, 'crossed', known(True), (envelope,), call.transmission),))

    def ack(self, call):
        try: raw, data = self.env.client.raw('ack_source', **call.invocation)
        except case.ReplyError as exc: return self.rejected_reply(call,exc)
        ref, view = _capture(raw, {'name':'s1.json','version':'0.1.0-proposal.1'}, call.context.read.views)
        source = source_identity(call.request.binding, call.request.inputs, call.context.read)
        if data['generation'] != source.generation['value'] or data['filter_digest'] != source.filter_digest['value'] or data['consumer'] != source.consumer['value'] or data['position'] != call.invocation['position']:
            raise ExecutionError('s3.fixture_ack_response_mismatch')
        from crucis_causal.execution.collection import progress_payload
        entry = next(e for e in call.request.inputs.entries if e.role == 's3.role.source')
        receipt = next(qualified(e.reference,e.source_package) for e in call.request.inputs.entries if e.role == 's3.role.capture_receipt')
        b = Builder('Observed source ACK position, not native termination')
        frontier = b.add('source_frontier', progress_payload(entry, captured=call.parameters['position'],
            acknowledged=call.parameters['position'], interpreted=unknown('s3.raw_capture_not_interpretation'),coverage=[ref,receipt]))
        audience = b.add('audience', {'purpose':contract('s3.private_fixture'),'recipients':index(),'disclosure_policy':unknown_ref('s1.policy'),'authority':unknown()})
        root = b.add('projection_view', {'view_role':'audience_projection','audience':audience,'projection_contract':contract('s3.fixture.source_ack'),
            'members':index([frontier,ref]),'claims':index(),'limits':index()})
        projected = case.frame(b,root,(*call.context.read.views,view))
        binding = reference(call.request.binding.record['id'], 'operation_binding', call.request.binding.context['package_id'])
        evidence = api.DriverEvidence(binding, api.RecordDelta(projected.records,(),(*call.context.read.views,view,projected)), index(), index([ref]), index(), ())
        return api.CallResult('completed', evidence, records=evidence.records,
            effects=(api.EffectBoundary(call.request.command, 'crossed', known(True), (ref,), call.transmission),))

    @staticmethod
    def rejected_reply(call, error):
        ref,view=_capture(error.raw,{'name':'s1.octets','version':'0.1.0-proposal.1'},call.context.read.views)
        delta=api.RecordDelta(dependencies=(view,))
        evidence=api.DriverEvidence(reference(call.request.binding.record['id'],'operation_binding',call.request.binding.context['package_id']),delta,index(extent='unresolved'),index([ref],extent='partial_for_scope'),index(),())
        return api.CallResult('rejected',evidence,records=delta,issues=(api.Issue(error.code,scope(call.request.command),(ref,)),),
            effects=(api.EffectBoundary(call.request.command,'may_have_crossed',unknown('s3.receiver_admission_unestablished'),(ref,),call.transmission),))


def deadline():
    return {'time_type': 'native_report', 'text': 'fixture_tick:10', 'timezone': not_applicable(), 'precision': known('logical_tick')}


class Environment(case.Environment):
    def __init__(self, root, client, descriptor, *, max_events='6', max_bytes='65536', fault=None):
        resources = {'s3.fixture_work': {'unit': contract('fixture_unit'), 'capacity': number('20')},
            's3.fixture_fetch_events': {'unit': contract('fixture_event'), 'capacity': number('12')}}
        super().__init__(root, client, scientific_path=None, fault=fault, native_operations=(*case.OPS, *OPS), resources=resources)
        self.descriptor = descriptor; self.mechanics_stream = Mechanics(self)
        self.profile = ObservationProfile(PROTOCOL, supplied_callable(source_identity), supplied_callable(measure), supplied_callable(resume), supplied_callable(advance), self.pin)
        self.collector = Collector((self.profile,)); self.collector.install(self.registry); self.coordinator.collector = self.collector
        boundary = DriverBoundary(self.journal, self.jctx, ((self.owner, self.octx),))
        self.stream_driver = EffectDriver(self.component, self.pin, boundary, self.component, contract('s3.fixture.http'),
            tuple(EffectMethod(op, supplied_callable(self.mechanics_stream.prepare), supplied_callable(method), contract('s3.fixture.stream_evidence')) for op,method in zip(OPS,(self.mechanics_stream.observe,self.mechanics_stream.ack))))
        self.stream_driver.install(self.registry)
        self.sources = {}
        self.native_subject = None
        self.max_events, self.max_bytes = max_events, max_bytes
        self.source, self.period = self.add_source()

    def operation_amounts(self, actual):
        entries = list(super().operation_amounts(actual))
        amount = next((p['value']['value'] for p in actual.record['payload']['parameters'] if p['key'] == 'max_events'), '0') if actual.record['payload']['operation'] == OPS[0] else '0'
        entries.append({'resource': contract('s3.fixture_fetch_events'), 'unit': contract('fixture_event'), 'quantity': number(amount), 'aggregation': contract('s3.aggregation.replace_then_disjoint_members')})
        return tuple(entries)

    def add_source(self, *, partition='p0', consumer='auditor', generation=None):
        b = Builder('Explicit source/collection context')
        if self.native_subject is None:
            native_doc, a = typed_document(b, contract('s3.payload.native_descriptor'), self.descriptor)
            native = b.add('native_subject', {'descriptor': native_doc, 'origin_attempt': unknown_ref('s1.attempt'), 'scope': scope(), 'basis': []}, basis='reported')
        else:
            native, a = self.native_subject, None
        filt, c = typed_document(b, contract('s3.fixture.stream_filter'), {'kind': 'all_fixture_events', 'partition': partition, 'consumer': consumer})
        source = b.add('source_frontier', {'source': native, 'episode': known(native), 'protocol': PROTOCOL, 'filter': known(filt),
            'generation': generation or self.descriptor['incarnation'], 'fetched': unknown(), 'durably_captured': unknown(), 'interpreted': unknown(), 'acknowledged': unknown(), 'coverage': index(extent='unresolved')})
        bounds, d = typed_document(b, contract('s3.payload.collection_bounds'), {'max_events': known(self.max_events), 'max_bytes': known(self.max_bytes),
            'deadline': known(deadline()), 'stopping_rule': contract('s3.fixture.capture_bound')})
        period = b.add('collection_period', {'scope': scope(native), 'bounds': bounds, 'predecessors': [], 'policy': contract('s3.fixture.capture_bound')})
        audience = b.add('audience', {'purpose': contract('s3.private_fixture'), 'recipients': index(), 'disclosure_policy': unknown_ref('s1.policy'), 'authority': unknown()})
        root = b.add('projection_view', {'view_role': 'audience_projection', 'audience': audience, 'projection_contract': contract('s3.fixture.source_collection'), 'members': index([source, period]), 'claims': index(), 'limits': index()})
        added = (a,c,d) if a is not None else (c,d)
        view = case.frame(b, root, (*self.context.read.views, *added)); self.include(*added,view)
        if self.native_subject is None: self.native_subject = qualified(native, view.package_id)
        qsource, qperiod = qualified(source,view.package_id), qualified(period,view.package_id)
        self.sources[qsource['target']] = (qperiod, partition, consumer)
        return qsource, qperiod

    def observe(self, *, source=None, cursor_value=None, max_events='3', max_bytes='4096', ack_mode='separate'):
        selected = source or self.source; period = self.sources[selected['target']][0]
        resolver = codec.Resolver(self.context.read.views, limits=self.context.limits)
        s, pid = resolver.record(selected, selected['package_id'])
        roles = tuple({'role':'s3.role.'+role,'members':index([ref])} for role,ref in [('subject',qualified(s['payload']['source'],pid)),('source',selected),('period',period)])
        params = {'cursor': cursor_value or not_applicable('s3.fixture.initial_position'), 'max_events':known(max_events), 'max_bytes':known(max_bytes),
            'deadline':known(deadline()), 'ack_mode':known(ack_mode), 'deadline_rule':known(contract('s3.fixture.logical_tick_deadline'))}
        return api.OperationRequest(OPS[0],roles,tuple({'key':k,'value':v} for k,v in params.items()),identity())

    def acknowledge(self, capture, *, source=None, position_value=None):
        params={'position':position_value or capture.durable_cursor,'protocol':known(PROTOCOL)}
        roles=tuple({'role':'s3.role.'+role,'members':index([ref])} for role,ref in [('source',source or self.source),('capture_receipt',capture.commit.receipt)])
        return api.OperationRequest(OPS[1], roles, tuple({'key':k,'value':v} for k,v in params.items()),identity())

    def captures(self):
        with self.journal._db() as db:
            return [r['id'] for r in db.execute('SELECT id FROM transactions WHERE kind=? ORDER BY revision',('capture',))]

    def capture(self, occurrence=None):
        result = self.journal.capture_transaction(self.account, occurrence or self.captures()[-1], self.jctx)
        if result.state != 'completed': raise AssertionError(result.issues)
        self.include(*self.journal.head(self.account,self.jctx).records.dependencies, result.value.commit.head.snapshot)
        return result.value

    def oracle_ack(self):
        period, partition, consumer = self.sources[self.source['target']]
        return self.client.call('query_ack', descriptor=self.descriptor, epoch=self.client.epoch, partition=partition,
            consumer=consumer, filter_digest=digest(canonical({'kind':'all_fixture_events','partition':partition,'consumer':consumer}))['value'])


def reopen(previous):
    """Actual fresh local issuers; same persistent stores/control allocation."""
    from crucis_causal.execution.clock import WallClock
    from crucis_causal.execution.coordinator import AdmissionRule, Coordinator, OwnerAllocation
    from crucis_causal.execution.journal import Journal
    from crucis_causal.execution.owners import LocalOwner
    from crucis_causal.execution.registry import SuppliedRegistryContext, ExactDriverRegistry, ExactDecisionRegistry, PayloadRegistry
    env = object.__new__(Environment)
    for name in ('root','client','pin','component','account','allocation','view','descriptor','profile','sources','source','period','max_events','max_bytes','native_subject'):
        setattr(env, name, getattr(previous, name))
    env.fault = None; env.launch_roles = None
    env.registry = SuppliedRegistryContext(ExactDriverRegistry(), ExactDecisionRegistry(), PayloadRegistry())
    env.collector = Collector((env.profile,)); env.collector.install(env.registry)
    read = replace(previous.context.read, registry=env.registry)
    env.journal = Journal(env.root/'journal'); env.jctx = api.RuntimeContext(read, env.journal.control(env.account))
    current = env.journal.head(env.account, env.jctx)
    read = read_with(read, *current.records.dependencies, current.value.snapshot)
    env.owner = LocalOwner(env.root/'owner', previous.owner.resources, native_operations=previous.owner.native_operations, ttl_ns='300000000000')
    env.octx = api.RuntimeContext(read, env.owner.control(env.allocation, max_calls='1000'))
    env.mechanics_stream = Mechanics(env)
    boundary = DriverBoundary(env.journal, env.jctx, ((env.owner,env.octx),))
    env.stream_driver = EffectDriver(env.component, env.pin, boundary, env.component, contract('s3.fixture.http'),
        tuple(EffectMethod(op,supplied_callable(env.mechanics_stream.prepare),supplied_callable(method),contract('s3.fixture.stream_evidence')) for op,method in zip(OPS,(env.mechanics_stream.observe,env.mechanics_stream.ack))))
    env.stream_driver.install(env.registry)
    rule = AdmissionRule(contract('s3.fixture.native_profile'), (*case.OPS,*OPS), env.pin, supplied_callable(case.eligible))
    env.coordinator = Coordinator((rule,), collector=env.collector)
    allocation = OwnerAllocation('native_owner',env.owner,env.octx,env.amounts('0'),contract('s3.owner.same_request_exact_replay'),'0')
    runtime = api.RuntimeContext(read,None)
    cap = env.coordinator.bind(env.journal, env.jctx, env.journal,(allocation,),('native_owner',),runtime,runtime,not_applicable('s3.no_absolute_deadline'),None)
    env.context = api.CoordinatorContext(read, env.journal, env.journal, {'native_owner':env.owner}, env.registry.drivers,env.registry.decisions,cap,WallClock(),case.L)
    return env
