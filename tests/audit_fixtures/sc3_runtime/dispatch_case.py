"""Explicit synthetic provider owner/client and S3 fixture bootstrap (DLV-08/09)."""
import base64
from contextlib import contextmanager
from dataclasses import dataclass, replace
import hashlib
import http.client
import json
import os
from pathlib import Path
import queue
import secrets
import subprocess
import sys
import threading
from crucis_causal.execution import api, codec
from crucis_causal.execution.authority import DriverBoundary
from crucis_causal.execution.clock import WallClock
from crucis_causal.execution.coordinator import (AdmissionRule, Coordinator, OwnerAllocation, read_with,
    root_of, typed_document)
from crucis_causal.execution.drivers import NativeCall, NativeDriver, NativeMechanics, NativeReply
from crucis_causal.execution.identity import coordinate
from crucis_causal.execution.journal import Journal, binding_digest
from crucis_causal.execution.model import (Builder, ExecutionError, canonical, contract, identity, index, known,
    not_applicable, number, qualified, reference, scope, unknown, unknown_ref)
from crucis_causal.execution.owners import LocalOwner
from crucis_causal.execution.registry import ExactDecisionRegistry, ExactDriverRegistry, PayloadRegistry, SuppliedRegistryContext, supplied_callable
import input_case

ROOT = Path(__file__).resolve().parents[3]
FIX = ROOT/'tests/audit_fixtures/sc3'
OPS = tuple(contract(op) for op in ('s3.op.launch','s3.op.lookup_launch','s3.op.attach'))
L = api.Limits()


class ReplyError(ExecutionError):
    def __init__(self, code, raw, *, complete=True):
        super().__init__(code); self.raw, self.complete = raw, complete


class Client:
    """Actual localhost binding; header auth never enters native audit bodies."""
    def __init__(self, address, token, namespace, epoch):
        if address[0] != '127.0.0.1' or not isinstance(address[1], int) or not 0 < address[1] < 65536:
            raise ValueError('owned explicit localhost endpoint required')
        self.address, self._token, self.namespace, self.epoch = tuple(address), token, namespace, epoch

    def raw(self, method, **arguments):
        body = canonical({**arguments, 'method': method})
        connection = http.client.HTTPConnection(*self.address, timeout=15)
        try:
            connection.request('POST', '/v1', body=body, headers={'Authorization': 'Bearer '+self._token, 'Content-Type': 'application/json'})
            response = connection.getresponse(); raw = response.read(1048577)
            if len(raw) > 1048576: raise ReplyError('s3.fixture_response_bound_exceeded',raw[:1048576],complete=False)
            if response.status != 200: raise ReplyError('s3.fixture_transport_unconfirmed',raw)
            try: decoded = json.loads(raw)
            except ValueError: raise ReplyError('s3.fixture_response_uninterpreted',raw) from None
            if not isinstance(decoded,dict) or set(decoded) != {'ok','value'} or decoded['ok'] is not True: raise ReplyError('s3.fixture_receiver_rejected',raw)
            return raw, decoded['value']
        except ReplyError: raise
        except (OSError, ValueError, http.client.HTTPException):
            raise ExecutionError('s3.fixture_transport_unconfirmed') from None
        finally: connection.close()

    def call(self, method, **arguments): return self.raw(method, **arguments)[1]

    def __copy__(self): raise TypeError('actual transport/auth binding is not copyable')
    def __deepcopy__(self, memo): raise TypeError('actual transport/auth binding is not copyable')
    def __reduce__(self): raise TypeError('actual transport/auth binding is not serializable')


@dataclass(frozen=True)
class Connection:
    client: Client
    descriptor: dict
    native_connection: str


@contextmanager
def service(root, *, program=None):
    root = Path(root).resolve(); token = secrets.token_hex(32)
    process = subprocess.Popen([sys.executable, '-B', str(program or FIX/'native_service.py'), '--root', str(root)],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
    messages = queue.Queue()
    reader = threading.Thread(target=lambda: messages.put(process.stdout.readline()), daemon=True); reader.start()
    try:
        process.stdin.write(json.dumps({'token': token})+'\n'); process.stdin.flush()
        line = messages.get(timeout=30)
        if not line.strip():
            process.wait(timeout=10)
            raise AssertionError('owned fixture startup failed: '+process.stderr.read())
        ready = json.loads(line)
        client = Client(ready['address'], token, ready['namespace'], ready['epoch'])
        yield client, process
    finally:
        if process.poll() is None:
            process.terminate()
            try: process.wait(timeout=15)
            except subprocess.TimeoutExpired: process.kill(); process.wait(timeout=15)
        reader.join(timeout=5)
        for stream in (process.stdin, process.stdout, process.stderr): stream.close()
        if reader.is_alive(): raise AssertionError('owned fixture startup reader survived cleanup')


def frame(builder, root, dependencies):
    return codec.parse_snapshot(codec.dumps(builder.package(root, dependencies), L), L)


def pin():
    from test_audit_execution_wire import implementation
    files = [p for p in sorted((ROOT/'crucis_causal/execution').iterdir()) if p.suffix in ('.py','.json')]
    files += [Path(__file__), Path(input_case.__file__), FIX/'native_service.py', FIX/'native_program.py',
              ROOT/'tests/audit_fixtures/sc3_runtime/process_echo.py']
    test = ROOT/'tests/test_audit_execution_dispatch.py'
    if test.exists(): files.append(test)
    worker = ROOT/'tests/audit_fixtures/sc3_runtime/dispatch_worker.py'
    if worker.exists(): files.append(worker)
    files += [p for p in sorted((ROOT/'tests/audit_fixtures/sc3_runtime').glob('*.py')) if p not in files]
    extra = ROOT/'tests/test_audit_execution_collection.py'
    if extra.exists(): files.append(extra)
    files += [p for p in sorted((ROOT/'tests').glob('test_audit_execution_*.py')) if p not in files]
    return implementation(canonical({p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}))


def document(selected, value, dependencies):
    b = Builder('Explicit native fixture parameter bytes')
    ref, storage = typed_document(b, selected, value)
    audience = b.add('audience', {'purpose': contract('s3.private_fixture'), 'recipients': index(), 'disclosure_policy': unknown_ref('s1.policy'), 'authority': unknown()})
    root = b.add('projection_view', {'view_role': 'audience_projection', 'audience': audience,
        'projection_contract': contract('s3.fixture.parameters'), 'members': index([ref]), 'claims': index(), 'limits': index()})
    view = frame(b, root, (*dependencies, storage))
    return qualified(ref, view.package_id), (storage, view)


def content(resolver, ref, anchor, selected):
    record, pid = resolver.record(ref, anchor)
    if record['record_type'] != 's3.typed_payload' or record['payload']['payload_contract'] != selected:
        raise ExecutionError('s3.fixture_parameter_contract')
    from crucis_causal.connections.validation import content_bytes
    artifact, _ = resolver.record(record['payload']['content']['artifact'], pid)
    if record['payload']['content']['selector']['state'] != 'not_applicable': raise ExecutionError('s3.fixture_whole_parameters_required')
    return json.loads(content_bytes(artifact['payload']['content']))


class Mechanics:
    def __init__(self, component, client, expected_mode=None): self.component, self.client, self.expected_mode = component, client, expected_mode

    def prepare(self, binding, inputs, context):
        resolver = codec.Resolver(context.views, limits=context.limits)
        params = {p['key']: p['value'] for p in binding.record['payload']['parameters']}
        op = binding.record['payload']['operation']['name']; pid = binding.context['package_id']
        if op == 's3.op.launch':
            value = content(resolver, params['invocation']['value'], pid, contract('s3.fixture.launch_arguments'))
            required = {'mode','data','epoch','pause','drop_reply','native_id'}
            if set(value) != required or value['mode'] not in ('local','remote','interactive','checkpoint') or not isinstance(value['pause'], bool) or not isinstance(value['drop_reply'], bool):
                raise ExecutionError('s3.fixture_launch_arguments')
            if value['native_id'] is not None and (not isinstance(value['native_id'], str) or not value['native_id']): raise ExecutionError('s3.fixture_native_id_form')
            base64.b64decode(value['data'], validate=True)
            if self.expected_mode is not None and value['mode'] != self.expected_mode: raise ExecutionError('s3.fixture_native_configuration_mismatch')
            request = next(e for e in inputs.entries if e.role == 's3.role.request')
            attempt = next(e for e in inputs.entries if e.role == 's3.role.attempt')
            native_binding = next(e for e in inputs.entries if e.role == 's3.role.binding')
            if native_binding.record['payload']['state'] != 'ready' or native_binding.record['payload']['request']['target'] != request.record['id'] or attempt.record['payload']['request']['target'] != request.record['id']:
                raise ExecutionError('s3.fixture_native_request_binding_mismatch')
            presentations = [e for e in inputs.entries if e.role == 's3.role.presentations']
            if len(presentations) != 1: raise ExecutionError('s3.fixture_exact_single_input_required')
            shown = presentations[0]; p = shown.record['payload']
            if p['state'] != 'permitted' or p['payload']['state'] != 'known' or p['payload']['value']['selector']['state'] != 'not_applicable':
                raise ExecutionError('s3.fixture_permitted_whole_input_required')
            from crucis_causal.connections.validation import content_bytes
            source, _ = resolver.record(p['payload']['value']['artifact'], shown.source_package)
            if base64.b64decode(value['data'], validate=True) != content_bytes(source['payload']['content']):
                raise ExecutionError('s3.fixture_native_input_substituted')
            if params['idempotency']['state'] != 'not_applicable': raise ExecutionError('s3.fixture_no_command_idempotency')
            return value
        if op == 's3.op.lookup_launch':
            command = next(e for e in inputs.entries if e.role == 's3.role.command')
            owner = next(e for e in inputs.entries if e.role == 's3.role.owner')
            if owner.reference != self.component: raise ExecutionError('s3.fixture_query_owner_mismatch')
            query = content(resolver, params['query']['value'], pid, contract('s3.payload.query'))
            subject, _ = resolver.record(query['subject'], params['query']['value']['package_id'])
            if subject['id'] != command.record['id'] or params['coverage_rule']['value'] != contract('s3.fixture.exact_command_history') or query['retention'] != contract('s3.fixture.retained_history') or query['negative_coverage'] != contract('s3.fixture.authenticated_http_ingress'):
                raise ExecutionError('s3.fixture_query_scope_unestablished')
            keys = content(resolver, query['keys'], params['query']['value']['package_id'], contract('s3.fixture.command_key'))
            if set(keys) != {'command','unavailable'} or keys['command'] != command.record['id'] or not isinstance(keys['unavailable'], bool):
                raise ExecutionError('s3.fixture_query_key_mismatch')
            if params['native_idempotency']['state'] != 'not_applicable': raise ExecutionError('s3.fixture_no_command_idempotency')
            return keys
        if op == 's3.op.attach':
            if params['connection_role']['value'] == 'consumer': raise ExecutionError('s3.fixture_consumer_semantics_not_installed')
            subject = next(e for e in inputs.entries if e.role == 's3.role.subject')
            association = next(e for e in inputs.entries if e.role == 's3.role.association')
            ownership = next(e for e in inputs.entries if e.role == 's3.role.ownership')
            if association.record['payload']['native_subject']['target'] != subject.record['id'] or association.record['payload']['relation'] not in ('reported','supported'):
                raise ExecutionError('s3.fixture_native_association_unestablished')
            descriptor = content(resolver, subject.record['payload']['descriptor'], subject.source_package, contract('s3.payload.native_descriptor'))
            coordinate(descriptor)
            if descriptor['namespace'] != self.client.namespace or descriptor['authority'] != 'S3_owned_fixture_provider': raise ExecutionError('s3.fixture_native_namespace_mismatch')
            owned = ownership.record['payload']
            if owned['owner'] != self.component or not any(r['target'] == subject.record['id'] for r in owned['scope']['subjects']): raise ExecutionError('s3.fixture_native_ownership_scope')
            validity = content(resolver, owned['validity'], ownership.source_package, contract('s3.fixture.receiver_validity'))
            subscription = content(resolver, params['subscription']['value'], pid, contract('s3.payload.observation_subscription'))
            if subscription['native_subject']['target'] != subject.record['id'] or subscription['generation'] != descriptor['incarnation'] or validity['namespace'] != descriptor['namespace']:
                raise ExecutionError('s3.fixture_subscription_incarnation_mismatch')
            return {'descriptor': descriptor, 'epoch': validity['epoch'], 'role': params['connection_role']['value']}
        raise ExecutionError('s3.fixture_native_operation_unavailable')

    def invoke(self, call):
        raw, data = self.client.raw('launch', **call.invocation, command=call.request.command['target'], transmission=call.transmission['target'], binding_digest=binding_digest(call.request.binding))
        origin = next(qualified(e.reference, e.source_package) for e in call.request.inputs.entries if e.role == 's3.role.attempt')
        # This receiver creates on the exact D or replays only that identical D;
        # it never returns a different command's cached work as a fresh creation.
        return NativeReply(raw, {'name': 's1.json', 'version': '0.1.0-proposal.1'}, data['acceptance'], descriptor=data.get('descriptor'), epoch=data.get('epoch'), origin_attempt=origin)

    def lookup(self, call):
        raw, data = self.client.raw('query', **call.invocation)
        original = next(e for e in call.request.inputs.entries if e.role == 's3.role.command')
        coverage = api.QueryCoverage(scope(qualified(original.reference, original.source_package)),
            (contract('s3.fixture.authenticated_http_ingress'),), unknown('s3.fixture.query_time_not_reported'),
            contract('s3.fixture.retained_history'), known(data['complete']), api.RecordDelta(), known(data['no_late_acceptance']))
        return NativeReply(raw, {'name': 's1.json', 'version': '0.1.0-proposal.1'}, known(True), classification=data['classification'], matches=tuple(data['matches']), coverage=coverage)

    def attach(self, call):
        raw, data = self.client.raw('attach', **call.invocation)
        runtime = Connection(self.client, data['descriptor'], data['connection'])
        return NativeReply(raw, {'name': 's1.json', 'version': '0.1.0-proposal.1'}, known(True), descriptor=data['descriptor'], runtime=runtime, epoch=data['epoch'])


def eligible(binding, requirements, frontier, context):
    # Exact native mechanics and B04's independent scientific guard supply the
    # specific tested prerequisites. No unrequested isolation/accuracy claim.
    return api.RequirementEvaluation(requirements, (), (), (), frontier)


def scientific_inputs(path):
    from crucis_causal.execution.bridge import working_s1
    from crucis_causal.connections import api as s1
    from crucis_causal.connections.model import Builder as B1, contract as c1
    from crucis_causal.connections.ports import prepared_connection
    from crucis_causal.connections.services import RecordBuffer, IdentityService, ContractRegistry
    if path == 'checkpoint_r2':
        folder = ROOT/'tests/audit_fixtures/sc3_recovery_r2'
        row = json.loads((folder/'manifest.json').read_bytes())
        row = {**row, 'R_package_id': row['request']['package_id']}
        views = tuple(codec.parse_snapshot((folder/item['path']).read_bytes(), L) for item in row['files'])
    else:
        manifest = json.loads((FIX/'manifest.json').read_bytes())
        row = next(r for r in manifest['bindings'] if r['path'] == path)
        views = tuple(codec.parse_snapshot((FIX/name).read_bytes(), L) for name in row['dependencies'])
        # B00 froze R before S3 existed, without a request-binding receipt. Complete
        # that metadata handoff through the real S2 API; never recompile/replace R/A.
        from crucis_causal.experiments.api import ReaderLimits, ProjectionOccurrence
        from crucis_causal.experiments.handoff import record_handoff
        from crucis_causal.experiments.resolver import PlanResolver, ReadAccess
        from crucis_causal.experiments.writer import S2RecordWriter
        limits = ReaderLimits.standard()
        prior = PlanResolver([v.source_bytes for v in views], limits=limits)
        writer = S2RecordWriter(prior, ReadAccess(frozenset(prior._views)), limits)
        draft = writer.context()
        r_view = next(v for v in views if v.package_id == row['R_package_id'])
        handoff = record_handoff(row['run_binding'], ProjectionOccurrence(row['request']['target'], row['attempt']['target']), r_view, draft)
        if handoff.state != 'completed': raise AssertionError(handoff.issues)
        frozen = writer.frozen([handoff.value])
        views = tuple({v.package_id: v for v in (*views,
            *(codec.parse_snapshot(v.source_bytes, L) for v in writer.base._views.values()),
            codec.parse_snapshot(frozen.source_bytes, L))}.values())
    resolver = codec.Resolver(views, limits=L)
    buffer = RecordBuffer(B1('Actual native binding fixture'))
    working = working_s1(row['request'], row['attempt'], resolver, buffer)
    request = buffer.get(working.request)['payload']
    presentations = tuple(reference(r['id'], 's1.presentation') for r in buffer.snapshot() if r['record_type'] == 's1.presentation')
    if not presentations: raise AssertionError('frozen fixture presentation absent')
    component = buffer.get(presentations[0])['payload']['recipient']
    registry = ContractRegistry(); registry.register_route(request['operation'], 'direct')
    services = s1.AdapterServices(IdentityService(), buffer, registry)
    ports = prepared_connection(component, services, {'kind': 'function', 'entrypoint': c1('fixture_native'), 'arguments': []}, _routes=('direct',))
    route = s1.RouteSpec('direct', c1('fixture_transport'), request['operation'])
    bound = ports.bind(working.request, s1.PresentedBundle(presentations, request['presentation_policy']), route,
        s1.DependencyInventory((), scope(working.request)), s1.BindContext(services, scope(working.request)))
    if bound.state != 'completed': raise AssertionError(bound.diagnostics)
    snapshot = input_case.snapshot1(buffer.builder, [bound.value.binding], working.source_views)
    roles = [{'role': 's3.role.request', 'members': index([row['request']])}, {'role': 's3.role.attempt', 'members': index([row['attempt']])},
        {'role': 's3.role.binding', 'members': index([qualified(bound.value.binding, snapshot.package_id)])},
        {'role': 's3.role.presentations', 'members': index([qualified(p, row['R_package_id']) for p in presentations])},
        {'role': 's3.role.scientific_binding', 'members': index([row['run_binding']])}]
    return (*views, snapshot), roles


class Environment:
    def __init__(self, root, client, *, scientific_path='remote', fault=None, native_operations=OPS, resources=None, collector=None, mechanics_factory=None, native_channel=None):
        self.root, self.client, self.fault = Path(root).resolve(), client, fault
        self.pin = pin(); self.component, actor = input_case.actor(self.pin)
        if scientific_path is None: sources, self.launch_roles = (), None
        else: sources, self.launch_roles = scientific_inputs(scientific_path)
        b = Builder('Declared synthetic native audit profile')
        audience = b.add('audience', {'purpose': contract('s3.private_fixture'), 'recipients': index(), 'disclosure_policy': unknown_ref('s1.policy'), 'authority': unknown()})
        req = b.add('requirement_context', {'catalog': contract('s3.fixture.native_profile'), 'requested_claims': index(), 'coverage': index()})
        root_ref = b.add('projection_view', {'view_role': 'audience_projection', 'audience': audience,
            'projection_contract': contract('s3.fixture.native_profile'), 'members': index([req]), 'claims': index(), 'limits': index()})
        metadata = frame(b, root_ref, (self.pin.source_view, actor, *sources))
        self.registry = SuppliedRegistryContext(ExactDriverRegistry(), ExactDecisionRegistry(), PayloadRegistry())
        views = (self.pin.source_view, actor, *sources, metadata)
        read = api.PinnedReadContext(views, api.supplied_read(v.package_id for v in views), self.registry, L)
        self.account = reference(identity(), 'account'); self.journal = Journal(self.root/'journal')
        self.jctx = api.RuntimeContext(read, self.journal.control(self.account))
        self.owner = LocalOwner(self.root/'owner', resources or {'s3.fixture_work': {'unit': contract('fixture_unit'), 'capacity': number('20')}},
            native_operations=native_operations, ttl_ns='300000000000')
        self.allocation = identity(); control = self.owner.control(self.allocation, max_calls='1000')
        with self.owner._db() as db:
            owner_views = tuple(codec.parse_snapshot(bytes(row[0]), L) for row in db.execute('SELECT data FROM views'))
        read = read_with(read, *owner_views); self.octx = api.RuntimeContext(read, control)
        boundary = DriverBoundary(self.journal, self.jctx, ((self.owner, self.octx),))
        self.mechanics = (mechanics_factory or Mechanics)(self.component, client, 'checkpoint' if scientific_path == 'checkpoint_r2' else scientific_path)
        supplied = NativeMechanics(self.component, native_channel or contract('s3.fixture.http'), supplied_callable(self.mechanics.prepare),
            tuple((selected, supplied_callable(getattr(self.mechanics, method))) for selected, method in zip(OPS, ('invoke','lookup','attach'))))
        self.driver = NativeDriver(self.component, self.pin, boundary, supplied); self.driver.install(self.registry)
        rule = AdmissionRule(contract('s3.fixture.native_profile'), native_operations, self.pin, supplied_callable(eligible))
        self.coordinator = Coordinator((rule,), collector=collector); runtime = api.RuntimeContext(read, None)
        allocation = OwnerAllocation('native_owner', self.owner, self.octx, self.amounts('0'), contract('s3.owner.same_request_exact_replay'), '0')
        cap = self.coordinator.bind(self.journal, self.jctx, self.journal, (allocation,), ('native_owner',), runtime, runtime,
            not_applicable('s3.no_absolute_deadline'), None, fault)
        self.context = api.CoordinatorContext(read, self.journal, self.journal, {'native_owner': self.owner}, self.registry.drivers,
            self.registry.decisions, cap, WallClock(), L)
        target = {'definition': contract('s3.native_observation' if scientific_path is None else 's3.scientific_execution'),
            'scope': scope(), 'subjects': index(), 'requirements': index(), 'relations': index()}
        commission = api.CommissionSpec(self.account['target'], 'observe' if scientific_path is None else 'execute', target,
            qualified(audience, metadata.package_id), qualified(req, metadata.package_id))
        opened = self.coordinator.open(commission, self.context)
        if opened.state != 'completed': raise AssertionError(opened.issues)
        self.view = opened.value
        self.include(*opened.records.dependencies, self.view)

    @staticmethod
    def amounts(quantity):
        return ({'resource': contract('s3.fixture_work'), 'unit': contract('fixture_unit'), 'quantity': number(quantity),
            'aggregation': contract('s3.aggregation.replace_then_disjoint_members')},)

    def include(self, *views):
        self.context = replace(self.context, read=read_with(self.context.read, *views))

    def launch(self, *, mode='remote', pause=False, drop_reply=False, native_id=None):
        if self.launch_roles is None: raise AssertionError('no discovery R/A in an observation-only account')
        values = {'mode': mode, 'data': base64.b64encode(input_case.SOURCE).decode(), 'epoch': self.client.epoch,
            'pause': pause, 'drop_reply': drop_reply, 'native_id': native_id}
        invocation, views = document(contract('s3.fixture.launch_arguments'), values, self.context.read.views); self.include(*views)
        parameters = {'invocation': known(invocation), 'request_relation': known('same_request'), 'idempotency': not_applicable(),
            'purpose': known('scientific_run'), 'scientific_rule': contract('s3.require_exact_scientific_binding')}
        parameters['scientific_rule'] = known(parameters['scientific_rule'])
        return api.OperationRequest(contract('s3.op.launch'), tuple(self.launch_roles), tuple({'key': k, 'value': v} for k,v in parameters.items()), identity())

    def lookup(self, command, *, unavailable=False):
        keys, views = document(contract('s3.fixture.command_key'), {'command': command['target'], 'unavailable': unavailable}, self.context.read.views); self.include(*views)
        window, views = document(contract('s3.fixture.current_snapshot'), {'scope': command, 'clock_domain': 'provider_sqlite_transaction'}, self.context.read.views); self.include(*views)
        query = {'subject': command, 'keys': keys, 'time_scope': window, 'retention': contract('s3.fixture.retained_history'), 'negative_coverage': contract('s3.fixture.authenticated_http_ingress')}
        ref, views = document(contract('s3.payload.query'), query, self.context.read.views); self.include(*views)
        roles = ({'role': 's3.role.command', 'members': index([command])}, {'role': 's3.role.owner', 'members': index([self.component])})
        params = {'query': known(ref), 'coverage_rule': known(contract('s3.fixture.exact_command_history')), 'native_idempotency': not_applicable()}
        return api.OperationRequest(contract('s3.op.lookup_launch'), roles, tuple({'key': k, 'value': v} for k,v in params.items()), identity())

    def existing(self, descriptor, *, attempt=None, role='observer', epoch=None):
        b = Builder('Supplied exact native observation target')
        ref, storage = typed_document(b, contract('s3.payload.native_descriptor'), descriptor)
        native = b.add('native_subject', {'descriptor': ref, 'origin_attempt': attempt or unknown_ref('s1.attempt'), 'scope': scope(), 'basis': []}, basis='reported')
        association = b.add('native_association', {'attempt': attempt or unknown_ref('s1.attempt'), 'native_subject': native,
            'relation': 'reported', 'basis': [], 'assessment': unknown()})
        validity, validity_storage = typed_document(b, contract('s3.fixture.receiver_validity'), {'epoch': epoch or self.client.epoch, 'namespace': descriptor['namespace']})
        ownership = b.add('ownership_context', {'owner': self.component, 'scope': scope(native), 'validity': validity,
            'receiver_guarantee': unknown('s3.no_global_receiver_guarantee'), 'basis': [], 'supersedes': []})
        subscription, subscription_storage = typed_document(b, contract('s3.payload.observation_subscription'), {
            'source_contract': contract('s3.fixture.native_events'), 'native_subject': native, 'filter': unknown_ref('typed_payload'),
            'generation': descriptor['incarnation'], 'consumer_group': unknown(), 'retention_rule': contract('s3.fixture.retained_history')})
        audience = b.add('audience', {'purpose': contract('s3.private_fixture'), 'recipients': index(), 'disclosure_policy': unknown_ref('s1.policy'), 'authority': unknown()})
        root = b.add('projection_view', {'view_role': 'audience_projection', 'audience': audience,
            'projection_contract': contract('s3.fixture.existing_native'), 'members': index([native, association, ownership, subscription]), 'claims': index(), 'limits': index()})
        view = frame(b, root, (*self.context.read.views, storage, validity_storage, subscription_storage)); self.include(storage, validity_storage, subscription_storage, view)
        roles = tuple({'role': 's3.role.'+name, 'members': index([qualified(r, view.package_id)])} for name,r in [('subject',native),('association',association),('ownership',ownership)])
        parameters = ({'key': 'connection_role', 'value': known(role)}, {'key': 'subscription', 'value': known(qualified(subscription, view.package_id))})
        return api.OperationRequest(contract('s3.op.attach'), roles, parameters, identity())

    def plan(self, request):
        result = self.coordinator.plan(self.view, request, self.context.read)
        if result.state == 'completed': self.include(*result.value.dependencies.views)
        return result

    def admit(self, plan, *, group=None):
        # Explicit caller-owned revision observation, not a hidden RPC inside
        # Coordinator.admit. Its actual bounded owner history is retained.
        actual, _, _ = self.coordinator._actual(plan, self.context.read)
        self.octx = replace(self.octx, read=read_with(self.octx.read, *self.context.read.views))
        observed = self.owner.inspect(actual, self.octx)
        if observed.state != 'completed': raise AssertionError(observed.issues)
        self.include(*observed.value.evidence.dependencies)
        allocation = OwnerAllocation('native_owner', self.owner, self.octx, self.operation_amounts(actual), contract('s3.owner.same_request_exact_replay'), observed.value.revision['value'])
        runtime = api.RuntimeContext(self.context.read, None)
        cap = self.coordinator.bind(self.journal, self.jctx, self.journal, (allocation,), ('native_owner',), runtime, runtime,
            not_applicable('s3.no_absolute_deadline'), None, self.fault)
        self.context = replace(self.context, control_capability=cap)
        current = self.journal.head(self.account, self.jctx)
        result = self.coordinator.admit(plan, current.value, self.context, group or identity())
        return result

    def operation_amounts(self, actual):
        return self.amounts('4' if actual.record['payload']['operation'] == contract('s3.op.launch') else '0')

    def issue(self, admission, *, transmission=None):
        result = self.coordinator.issue(admission, self.context, transmission or identity())
        current = self.journal.head(self.account, self.jctx)
        self.include(*current.records.dependencies, current.value.snapshot, *result.records.dependencies)
        return result

    def run(self, request):
        planned = self.plan(request)
        if planned.state != 'completed': return planned
        admitted = self.admit(planned.value)
        if admitted.state != 'completed': return admitted
        return self.issue(admitted.value)


def packet(env, plan, group, transmission):
    pin = env.pin
    return {'root': str(env.root), 'account': env.account, 'component': env.component, 'allocation': env.allocation,
        'address': list(env.client.address), 'namespace': env.client.namespace, 'epoch': env.client.epoch,
        'expected_mode': env.mechanics.expected_mode,
        'command': plan.command, 'source': plan.source_view.package_id, 'group': group, 'transmission': transmission,
        'pin': {'reference': pin.reference, 'content_digest': pin.content_digest, 'selector': pin.selector, 'source': pin.source_view.package_id},
        'views': [base64.b64encode(v.source_bytes).decode() for v in plan.dependencies.views]}


def reopen(value, token, fault=None):
    """Trusted supervisor bootstrap, never authority from audit JSON alone."""
    env = object.__new__(Environment)
    env.root = Path(value['root']).resolve(); env.fault = fault
    env.client = Client(value['address'], token, value['namespace'], value['epoch'])
    views = tuple(codec.parse_snapshot(base64.b64decode(raw, validate=True), L) for raw in value['views'])
    resolver = codec.Resolver(views, limits=L); p = value['pin']
    env.pin = api.PinnedArtifactIdentity(p['reference'], p['content_digest'], p['selector'], resolver.view(p['source']))
    env.component, env.account, env.allocation = value['component'], value['account'], value['allocation']
    env.launch_roles = None
    env.registry = SuppliedRegistryContext(ExactDriverRegistry(), ExactDecisionRegistry(), PayloadRegistry())
    read = api.PinnedReadContext(views, api.supplied_read(v.package_id for v in views), env.registry, L)
    env.journal = Journal(env.root/'journal'); env.jctx = api.RuntimeContext(read, env.journal.control(env.account))
    env.owner = LocalOwner(env.root/'owner', {'s3.fixture_work': {'unit': contract('fixture_unit'), 'capacity': number('20')}}, native_operations=OPS, ttl_ns='300000000000')
    env.octx = api.RuntimeContext(read, env.owner.control(env.allocation, max_calls='1000'))
    boundary = DriverBoundary(env.journal, env.jctx, ((env.owner, env.octx),))
    env.mechanics = Mechanics(env.component, env.client, value['expected_mode'])
    mechanics = NativeMechanics(env.component, contract('s3.fixture.http'), supplied_callable(env.mechanics.prepare),
        tuple((op, supplied_callable(getattr(env.mechanics, method))) for op,method in zip(OPS, ('invoke','lookup','attach'))))
    env.driver = NativeDriver(env.component, env.pin, boundary, mechanics); env.driver.install(env.registry)
    env.coordinator = Coordinator((AdmissionRule(contract('s3.fixture.native_profile'), OPS, env.pin, supplied_callable(eligible)),))
    allocation = OwnerAllocation('native_owner', env.owner, env.octx, env.amounts('4'), contract('s3.owner.same_request_exact_replay'), '0')
    runtime = api.RuntimeContext(read, None)
    cap = env.coordinator.bind(env.journal, env.jctx, env.journal, (allocation,), ('native_owner',), runtime, runtime, not_applicable('s3.no_absolute_deadline'), None, fault)
    env.context = api.CoordinatorContext(read, env.journal, env.journal, {'native_owner': env.owner}, env.registry.drivers, env.registry.decisions, cap, WallClock(), L)
    source = resolver.view(value['source'])
    original = env.coordinator.restore_prepared(value['command'], source, read)
    if original.state != 'completed': raise AssertionError(original.issues)
    # Keep the original account's cutoff for new operations, not a refrozen R.
    account = root_of(source, resolver)['account']
    candidate = next(v for v in views if v.package_id == account['package_id'])
    env.view = candidate
    return env, original.value
