"""B06 coordinator integration, independent custody/owner oracles (DLV-08/09)."""
import copy
import base64
import hashlib
from contextlib import closing
from dataclasses import replace
import json
from pathlib import Path
import sqlite3
import sys
import os
import queue
import subprocess
import threading
import unittest
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT/'tests/audit_fixtures/sc3_runtime'))
import input_case as case
from audit_fixtures.sc3_runtime.receipt_case import snapshot as retained_snapshot, triplet
from test_audit_execution_wire import covers, LIMITS, implementation
from test_audit_execution_journal import scratch
from crucis_causal.execution import api, codec
from crucis_causal.execution.authority import DriverBoundary
from crucis_causal.execution.clock import require_before, WallClock
from crucis_causal.execution.coordinator import Coordinator, AdmissionRule, OwnerAllocation, read_with, typed_document, root_of
from crucis_causal.execution.inputs import InputDriver
from crucis_causal.execution.journal import Journal
from crucis_causal.execution.model import (Builder, ExecutionError, contract, identity, index, known,
    not_applicable, number, qualified, reference, scope, unknown, unknown_ref, canonical)
from crucis_causal.execution.owners import LocalOwner
from crucis_causal.execution.registry import (ExactDriverRegistry, ExactDecisionRegistry, PayloadRegistry,
    SuppliedRegistryContext, supplied_callable, DeclaredDriver, native_invocation)
from crucis_causal.execution.staging import LocalCustodian


def stage_eligibility(binding, requirements, frontier, context):
    entries = [e for e in binding.inputs.entries if e.role == 's3.role.presentations']
    issues = () if entries and all(e.record['payload']['state'] == 'permitted' for e in entries) else (api.Issue('s3.presentation_not_permitted', scope(), ()),)
    return api.RequirementEvaluation(requirements, (), (), issues, frontier)


def coordinator_pin():
    files = sorted(p for p in (ROOT/'crucis_causal/execution').iterdir() if p.suffix in ('.py', '.json')) + [Path(__file__), Path(case.__file__)]
    worker = ROOT/'tests/audit_fixtures/sc3_runtime/coordinator_worker.py'
    if worker.exists(): files.append(worker)
    return implementation(canonical({p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}))


def setup(root, *, capacities=('20',), required=None, fault=None, deadline=None, owner_clock=None, probe=None):
    pin = coordinator_pin(); component, actor = case.actor(pin)
    custodian = LocalCustodian(root/'custody'); custody_control = custodian.control(('transfer', 'inspect', 'activate', 'revoke'))
    native, _, binding_ref, _, _ = case.staging_metadata(component, (pin.source_view, actor), namespace=custodian.namespace)
    source = native[-1]
    binding_record = next(r for r in source.records if r['id'] == binding_ref['target'])
    roles = [r for r in binding_record['payload']['roles'] if r['role'] != 's3.role.account']
    parameters = tuple(binding_record['payload']['parameters'])
    selected_operation = contract('s3.op.stage_input' if probe is None else 's3.op.launch')
    profile = contract('s3.fixture.trusted_stage_profile' if probe is None else 's3.fixture.fixed_probe_profile')
    if probe is not None:
        extra, roles, parameters = probe_metadata()
        native = (*native, *extra)
    # Explicit tested profile; an empty coverage table is not interpreted by the
    # core as universal readiness. This supplied rule scopes it to trusted stage.
    b = Builder('Fixed trusted-staging eligibility profile')
    audience = b.add('audience', {'purpose': contract('s3.private_fixture'), 'recipients': index(),
        'disclosure_policy': unknown_ref('s1.policy'), 'authority': unknown()})
    requirements = b.add('requirement_context', {'catalog': profile,
        'requested_claims': index(), 'coverage': index()})
    projection = b.add('projection_view', {'view_role': 'audience_projection', 'audience': audience,
        'projection_contract': contract('s3.fixture.profile'), 'members': index([requirements]), 'claims': index(), 'limits': index()})
    metadata = case.frame(b, projection, native)
    registry = SuppliedRegistryContext(ExactDriverRegistry(), ExactDecisionRegistry(), PayloadRegistry())
    read = api.PinnedReadContext((*native, metadata), api.supplied_read(v.package_id for v in (*native, metadata)), registry, LIMITS)
    account_id = identity(); account = reference(account_id, 'account')
    journal = Journal(root/'journal'); jctx = api.RuntimeContext(read, journal.control(account))
    allocations = []
    for i, cap in enumerate(capacities):
        owner = LocalOwner(root/('owner'+str(i)), {'s3.fixture_work': {'unit': contract('fixture_unit'), 'capacity': number(cap)}},
            native_operations=(selected_operation,), clock=owner_clock, ttl_ns='300000000000')
        with owner._db() as db:
            views = tuple(codec.parse_snapshot(bytes(r[0]), LIMITS) for r in db.execute('SELECT data FROM views'))
        read = read_with(read, *views)
        octx = api.RuntimeContext(read, owner.control(identity(), max_calls='1000'))
        allocations.append(OwnerAllocation('owner'+str(i), owner, octx,
            ({'resource': contract('s3.fixture_work'), 'unit': contract('fixture_unit'), 'quantity': number('1'),
              'aggregation': contract('s3.aggregation.replace_then_disjoint_members')},), contract('s3.owner.same_request_exact_replay'), '0'))
    boundary = DriverBoundary(journal, jctx, tuple((a.owner, a.context) for a in allocations))
    driver = (InputDriver(component, pin, boundary, custodian=custodian, custody_control=custody_control) if probe is None else
        ProbeDriver(component, pin, boundary, allocations[0].owner, probe))
    driver.install(registry)
    rule = AdmissionRule(profile, (selected_operation,), pin, supplied_callable(stage_eligibility if probe is None else probe_eligibility))
    coordinator = Coordinator((rule,))
    runtime = api.RuntimeContext(read, None)
    control = coordinator.bind(journal, jctx, journal, tuple(allocations), required or tuple(a.role for a in allocations),
        runtime, runtime, deadline or not_applicable('s3.no_absolute_deadline'), None, fault)
    ctx = api.CoordinatorContext(read, journal, journal, {a.role: a.owner for a in allocations}, registry.drivers,
        registry.decisions, control, WallClock(), LIMITS)
    target = {'definition': contract('s3.prospective_preparation'), 'scope': scope(), 'subjects': index(), 'requirements': index(), 'relations': index()}
    commission = api.CommissionSpec(account_id, 'prepare', target, qualified(audience, metadata.package_id), qualified(requirements, metadata.package_id))
    opened = coordinator.open(commission, ctx)
    if opened.state != 'completed': raise AssertionError(opened.issues)
    ctx = replace(ctx, read=read_with(read, *opened.records.dependencies, opened.value))
    if probe is None: roles.append({'role': 's3.role.account', 'members': index([reference(account_id, 'account', opened.value.package_id)])})
    request = api.OperationRequest(selected_operation, tuple(roles), parameters, identity())
    return coordinator, ctx, opened.value, request, journal, jctx, allocations, custodian, commission


def probe_eligibility(binding, requirements, frontier, context):
    # A fixed nonscientific probe needs no S2 trial; core independently checks
    # positive scientific intent and exact rule. Native authority remains separate.
    return api.RequirementEvaluation(requirements, (), (), (), frontier)


def probe_metadata():
    from crucis_causal.connections.model import Builder as B1
    from test_audit_connections_history import request, attempt
    b = B1('Fixed B06 local connection probe, no discovery dataset')
    req, _ = request(b); att = attempt(b, req)
    binding = b.add('binding', {'request': req, 'adapter': b.producer, 'route': 's1.fixture', 'presented': [],
        'resolved_configuration': [], 'prerequisites': [], 'state': 'ready', 'gaps': []})
    native = case.snapshot1(b, [req, att, binding])
    params = Builder('Pinned fixed probe invocation')
    invocation, store = typed_document(params, contract('s3.fixture.fixed_probe_invocation'), {'token': 'health'})
    audience = params.add('audience', {'purpose': contract('s3.private_fixture'), 'recipients': index(), 'disclosure_policy': unknown_ref('s1.policy'), 'authority': unknown()})
    root = params.add('projection_view', {'view_role': 'audience_projection', 'audience': audience,
        'projection_contract': contract('s3.fixture.probe'), 'members': index([invocation]), 'claims': index(), 'limits': index()})
    view = case.frame(params, root, (native, store))
    roles = [{'role': 's3.role.'+role, 'members': index([qualified(ref, native.package_id)])} for role, ref in [('request', req), ('attempt', att), ('binding', binding)]]
    roles += [{'role': 's3.role.presentations', 'members': index()}, {'role': 's3.role.scientific_binding', 'members': index()}]
    parameters = {'invocation': known(qualified(invocation, view.package_id)), 'request_relation': known('same_request'),
        'idempotency': not_applicable(), 'purpose': known('connection_probe'), 'scientific_rule': known(contract('s3.fixed_nonscientific_probe'))}
    return (native, store, view), roles, tuple({'key': k, 'value': v} for k, v in parameters.items())


class ProbeDriver(DeclaredDriver):
    def __init__(self, component, implementation, boundary, owner, calls):
        self.component, self.pin, self.boundary, self.owner, self.calls = component, implementation, boundary, owner, calls
        self.descriptor = api.ExactDriverDescriptor(component, contract('s3.op.launch'), contract('s3.fixture.probe_envelope'),
            contract('s3.native_start'), implementation, (), supplied_callable(self.invoke))
        super().__init__(api.DriverDeclaration(component, (self.descriptor,), ()), self._prepare)

    def install(self, registry):
        def envelope(value):
            if value != native_invocation(self.component, contract('s3.fixture.python_call'), contract('s3.fixture.probe_envelope'), {'token': 'health'}):
                raise ExecutionError('s3.fixture_probe_envelope_mismatch')
            return value
        registry.payloads.register(contract('s3.fixture.probe_envelope'), envelope)
        registry.drivers.install(self, registry)

    def _prepare(self, binding, inputs, context):
        from crucis_causal.execution.schema import validate_binding
        validate_binding(binding.record['payload'], admission=True)
        parameters = {p['key']: p['value'] for p in binding.record['payload']['parameters']}
        from crucis_causal.connections.validation import content_bytes
        resolver = codec.Resolver(context.views, limits=context.limits)
        typed, pid = resolver.record(parameters['invocation']['value'], binding.context['package_id'])
        artifact, _ = resolver.record(typed['payload']['content']['artifact'], pid)
        if typed['payload']['payload_contract'] != contract('s3.fixture.fixed_probe_invocation') or json.loads(content_bytes(artifact['payload']['content'])) != {'token': 'health'}:
            raise ExecutionError('s3.fixture_probe_invocation_mismatch')
        return native_invocation(self.component, contract('s3.fixture.python_call'), contract('s3.fixture.probe_envelope'), {'token': 'health'})

    def invoke(self, request, context, grants, issue_token, sink):
        entry = self.boundary.enter(request, context, grants, issue_token, self.descriptor, self.component, contract('s3.fixture.python_call'))
        self.calls.append(b'health')  # Actual explicitly supplied offline native probe.
        b = Builder('Observed local probe occurrence and metered unit')
        native_id = str(len(self.calls))
        descriptor, store = typed_document(b, contract('s3.payload.native_descriptor'), {'authority': self.component['target'],
            'namespace': 'B06_owned_python_probe', 'native_id': native_id, 'incarnation': known(issue_token.transmission['target']),
            'identity_rule': contract('s3.fixture.probe_call_occurrence'), 'validity': unknown_ref('typed_payload'), 'basis': []})
        attempt = next(qualified(e.reference, e.source_package) for e in request.inputs.entries if e.role == 's3.role.attempt')
        subject = b.add('native_subject', {'descriptor': descriptor, 'origin_attempt': attempt, 'scope': scope(request.command), 'basis': []})
        usage = b.add('resource_entry', {'scope': scope(request.command), 'owner': self.owner.owner, 'resource': contract('s3.fixture_work'),
            'unit': self.owner.units['s3.fixture_work'], 'entry_kind': 'usage', 'quantity': known(number('1')),
            'interval': not_applicable('s3.fixture.atomic_probe'), 'finality': 'final', 'revises': [],
            'aggregation': contract('s3.aggregation.replace_then_disjoint_members'), 'basis': [subject]})
        exposure = b.add('exposure_entry', {'scope': scope(request.command), 'owner': self.component, 'recipient': self.component,
            'information': index(), 'facet': 'transmitted', 'extent': known(number('0')), 'policy': contract('s3.fixture.no_scientific_inputs'), 'basis': [subject], 'revises': []})
        original = root_of(request.source_view, entry.resolver)
        root = b.add('projection_view', {'view_role': 'audience_projection', 'audience': qualified(original['audience'], request.source_view.package_id),
            'projection_contract': contract('s3.fixture.probe_observation'), 'members': index([subject, usage, exposure]), 'claims': index(), 'limits': index()})
        view = case.frame(b, root, (*context.read.views, store))
        records = api.RecordDelta(view.records, (), (*context.read.views, store, view))
        evidence = api.DriverEvidence(request.binding and reference(request.binding.record['id'], 'operation_binding', request.binding.context['package_id']), records,
            index([qualified(subject, view.package_id)]), index(), index(), ())
        return api.CallResult('completed', api.NativeStart(attempt, known(qualified(subject, view.package_id)), None, evidence), records=records,
            effects=(replace(entry.effect, boundary='crossed', acceptance=known(True)),))


def prepared(env):
    c, ctx, view, request, *_ = env
    out = c.plan(view, request, ctx.read)
    if out.state != 'completed': raise AssertionError(out.issues)
    return out.value


def admitted(env, plan, group=None):
    c, ctx, _, _, journal, jctx, *_ = env
    out = c.admit(plan, journal.head(reference(env[-1].account_id, 'account'), jctx).value,
        ctx, group or identity())
    if out.state != 'completed': raise AssertionError(out.issues)
    return out.value


def holds(owner):
    with closing(sqlite3.connect(owner.path)) as db:
        return db.execute('SELECT COUNT(*) FROM subjects WHERE status=?', ('active',)).fetchone()[0]


def consumed(custody):
    with closing(sqlite3.connect(custody.path)) as db:
        return int(db.execute('SELECT value FROM meta WHERE key=?', ('consumed',)).fetchone()[0])


def packet(env, plan, group, transmission):
    _, _, _, _, journal, _, owners, custody, commission = env
    pin = plan.driver.implementation
    return {'root': str(journal.root.parent), 'account': commission.account_id, 'command': plan.command,
        'source': plan.source_view.package_id, 'group': group, 'transmission': transmission,
        'component': plan.driver.component, 'pin': {'reference': pin.reference, 'content_digest': pin.content_digest,
            'selector': pin.selector, 'source_view': pin.source_view.package_id},
        'views': [base64.b64encode(v.source_bytes).decode('ascii') for v in plan.dependencies.views],
        'owners': [{'role': o.role, 'resources': o.owner.resources, 'allocation': o.owner._controls[o.context.control]['allocation'],
            'amounts': list(o.amounts), 'expected_revision': o.expected_revision} for o in owners]}


def reopen_packet(value, fault=None):
    root = Path(value['root']).resolve()
    views = tuple(codec.parse_snapshot(base64.b64decode(raw, validate=True), LIMITS) for raw in value['views'])
    registry = SuppliedRegistryContext(ExactDriverRegistry(), ExactDecisionRegistry(), PayloadRegistry())
    read = api.PinnedReadContext(views, api.supplied_read(v.package_id for v in views), registry, LIMITS)
    resolver = codec.Resolver(views, limits=LIMITS)
    p = value['pin']; pin = api.PinnedArtifactIdentity(p['reference'], p['content_digest'], p['selector'], resolver.view(p['source_view']))
    account = reference(value['account'], 'account'); journal = Journal(root/'journal')
    jctx = api.RuntimeContext(read, journal.control(account))
    allocations = []
    for saved in value['owners']:
        owner = LocalOwner(root/saved['role'], saved['resources'], native_operations=(contract('s3.op.stage_input'),), ttl_ns='300000000000')
        control = owner.control(saved['allocation'], max_calls='1000')
        allocations.append(OwnerAllocation(saved['role'], owner, api.RuntimeContext(read, control), tuple(saved['amounts']), contract('s3.owner.same_request_exact_replay'), saved['expected_revision']))
    custody = LocalCustodian(root/'custody')
    boundary = DriverBoundary(journal, jctx, tuple((o.owner, o.context) for o in allocations))
    driver = InputDriver(value['component'], pin, boundary, custodian=custody, custody_control=custody.control())
    driver.install(registry)
    rule = AdmissionRule(contract('s3.fixture.trusted_stage_profile'), (contract('s3.op.stage_input'),), pin, supplied_callable(stage_eligibility))
    coordinator = Coordinator((rule,)); runtime = api.RuntimeContext(read, None)
    control = coordinator.bind(journal, jctx, journal, tuple(allocations), tuple(o.role for o in allocations), runtime, runtime,
        not_applicable('s3.no_absolute_deadline'), None, fault)
    ctx = api.CoordinatorContext(read, journal, journal, {o.role: o.owner for o in allocations}, registry.drivers, registry.decisions, control, WallClock(), LIMITS)
    restored = coordinator.restore_prepared(value['command'], resolver.view(value['source']), read)
    if restored.state != 'completed': raise AssertionError(restored.issues)
    return coordinator, ctx, restored.value, journal, jctx, allocations, custody


def fault_receipt(case_id, variant, name, value):
    destination = os.environ.get('CRUCIS_S3_CASE_RECEIPTS')
    if not destination: return
    directory = Path(destination).resolve()/'faults'/case_id/variant
    if directory.is_relative_to(ROOT): raise AssertionError('external fault receipt required')
    directory.mkdir(parents=True, exist_ok=True)
    path = directory/(name+'.json')
    if path.exists(): raise AssertionError('preserve earlier fault receipt')
    path.write_bytes(canonical(value))


class CoordinatorCases(unittest.TestCase):
    @covers('T01', 'W02')
    def test_unknown_admission_critical_extension_holds_but_unrequested_claim_bytes_survive(self):
        with scratch() as root:
            env = setup(root); c, ctx, view, request, _, _, owners, custody, _ = env
            for critical, expected in [('s3.operational_admission', 'rejected'), ('s3.unrequested_future_claim', 'completed')]:
                body = view.package; body['package_id'] = identity()
                body['extensions'] = [{'contract': contract('s3.fixture.future_native_condition'), 'affects': [],
                    'critical_for': [critical], 'payload': {'content_form': 'inline_utf8', 'text': '{"condition":"uninterpreted"}'}}]
                extended = codec.parse_snapshot(codec.dumps(body, LIMITS), LIMITS)
                result = c.plan(extended, request, read_with(ctx.read, extended))
                self.assertEqual(result.state, expected, result.issues)
                if expected == 'rejected': self.assertEqual(result.issues[0].code, 's3.critical_extension_uninterpreted')
                self.assertEqual(extended.package['extensions'][0]['payload']['text'], '{"condition":"uninterpreted"}')
            self.assertEqual(consumed(custody), 0)
            for owner in owners:
                self.assertEqual(holds(owner.owner), 0)
                with closing(sqlite3.connect(owner.owner.path)) as db:
                    self.assertEqual(db.execute('SELECT COUNT(*) FROM calls').fetchone()[0], 0)

    @covers('F04', 'T01')
    def test_complete_exact_admission_plan_precedes_any_owner_RPC(self):
        with scratch() as root:
            reached = []
            def fault(point):
                if point != 'after_admission_plan': return
                head = env[4].head(reference(env[-1].account_id, 'account'), env[5]).value
                self.assertTrue(any(r['id'] == group for r in head.snapshot.records))
                for allocation in env[6]:
                    with closing(sqlite3.connect(allocation.owner.path)) as db:
                        self.assertEqual(db.execute('SELECT COUNT(*) FROM calls').fetchone()[0], 0)
                        self.assertEqual(db.execute('SELECT COUNT(*) FROM requests').fetchone()[0], 0)
                reached.append(point)
                raise OSError('interrupted after durable R, before any owner RPC')
            env = setup(root, fault=fault); plan = prepared(env); group = identity()
            result = env[0].admit(plan, env[4].head(reference(env[-1].account_id, 'account'), env[5]).value, env[1], group)
            self.assertEqual(result.state, 'rejected'); self.assertEqual(reached, ['after_admission_plan'])
            self.assertEqual(consumed(env[-2]), 0); self.assertEqual(holds(env[6][0].owner), 0)

    @covers('F18')
    def test_copied_spent_and_forged_tokens_cannot_enter_native_and_changed_receipt_holds(self):
        from unittest.mock import patch
        from crucis_causal.execution.registry import callable_value
        with scratch() as root:
            env = setup(root); plan = prepared(env); admission = admitted(env, plan)
            c, ctx, _, _, journal, jctx, _, custody, _ = env
            first = c.issue(admission, ctx, identity())
            self.assertEqual(first.state, 'completed', first.issues)
            current = journal.head(first.value.token.intent_commit.head.account, jctx)
            read = read_with(ctx.read, *current.records.dependencies, current.value.snapshot)
            binding, _, _ = c._actual(plan, read)
            request = api.ExactOperationRequest(plan.command, binding, binding.inputs, plan.driver, plan.source_view)
            token = first.value.token
            for changed in (replace(token), replace(token, runtime_permit=object.__new__(api.OpaqueIssuePermit)),
                            replace(token, binding_digest={**token.binding_digest, 'value': '0' * 64})):
                with patch.object(custody, 'transfer', wraps=custody.transfer) as forward:
                    held = callable_value(plan.driver.method)(request, api.RuntimeContext(read, None), admission.live_grants, changed, None)
                    self.assertEqual(held.state, 'rejected'); self.assertEqual(held.effects[0].boundary, 'not_crossed')
                    self.assertEqual(forward.call_count, 0)
            admission.owner_receipts[0]['target'] = identity()
            self.assertEqual(c.issue(admission, ctx, identity()).issues[0].code, 's3.live_admission_owner_binding_changed')
            self.assertEqual(consumed(custody), 1)
            triplet('F18','forged_or_copied_token',{'actual_custody_consumed':consumed(custody),'attempted_forged_entries':3,'additional_forward_calls':0},
                {'original_intent':retained_snapshot(token.intent_commit.head.snapshot),'command':plan.command,'transmission':token.transmission},
                {'current':retained_snapshot(journal.head(token.intent_commit.head.account,jctx).value.snapshot),'changed_owner_binding':'held'})

    @covers('X11')
    def test_fixed_probe_records_real_effect_usage_exposure_and_scientific_relabel_holds(self):
        from test_audit_execution_wire import fixture_views, MANIFEST
        calls = []
        with scratch() as root:
            env = setup(root, probe=calls); plan = prepared(env); admission = admitted(env, plan)
            c, ctx, view, request, _, _, owners, _, _ = env
            out = c.issue(admission, ctx, identity())
            self.assertEqual(out.state, 'completed', out.issues)
            self.assertEqual(calls, [b'health']); self.assertEqual(out.effects[0].boundary, 'crossed')
            usage = [r['payload'] for r in out.value.result.records.records if r['record_type'] == 's3.resource_entry']
            self.assertEqual([(r['entry_kind'], r['quantity']['value']['text']) for r in usage], [('usage', '1')])
            self.assertEqual(holds(owners[0].owner), 1)  # Usage is not settlement/release.
            exposure = [r['payload'] for r in out.value.result.records.records if r['record_type'] == 's3.exposure_entry']
            self.assertEqual([(r['facet'], r['extent']['value']['text']) for r in exposure], [('transmitted', '0')])
            historical = next(r for r in MANIFEST['bindings'] if r['path'] == 'local')
            roles = copy.deepcopy(request.roles)
            for role in roles:
                if role['role'] == 's3.role.request': role['members'] = index([historical['request']])
                if role['role'] == 's3.role.attempt': role['members'] = index([historical['attempt']])
            for label in ('connection_probe', 'non_scientific_execution'):
                parameters = copy.deepcopy(request.parameters)
                next(p for p in parameters if p['key'] == 'purpose')['value'] = known(label)
                changed = replace(request, roles=roles, parameters=parameters, request_occurrence=identity())
                result = c.plan(view, changed, read_with(ctx.read, *fixture_views()))
                self.assertEqual(result.state, 'rejected')
                self.assertEqual(result.issues[0].code, 's3.matching_scientific_run_unestablished')
            self.assertEqual(calls, [b'health'])

    @covers('F04', 'F05', 'F18')
    def test_process_death_and_fresh_coordinator_reuse_original_group_and_D(self):
        for point in ('after_owner_0', 'after_issue_intent'):
            with self.subTest(point=point), scratch() as root:
                env = setup(root, capacities=('20', '20'))
                plan = prepared(env); group, d = identity(), identity()
                value = packet(env, plan, group, d)
                path = root/'coordinator-packet.json'; path.write_bytes(canonical(value))
                process = subprocess.Popen([sys.executable, '-B', str(ROOT/'tests/audit_fixtures/sc3_runtime/coordinator_worker.py'), str(path), point],
                    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
                messages = queue.Queue()
                reader = threading.Thread(target=lambda: messages.put(process.stdout.readline()), daemon=True); reader.start()
                try:
                    line = messages.get(timeout=60)
                    if line.strip() != 'READY:' + point:
                        raise AssertionError('barrier absent: ' + line + process.stderr.read())
                    process.kill(); process.wait(timeout=15)
                finally:
                    if process.poll() is None: process.kill(); process.wait(timeout=15)
                    reader.join(timeout=5)
                    process.stdin.close(); process.stdout.close(); process.stderr.close()
                self.assertFalse(reader.is_alive())
                self.assertEqual(consumed(env[-2]), 0)
                before = env[4].head(reference(value['account'], 'account'), env[5]).value
                fault_id = 'F04' if point == 'after_owner_0' else 'F05'
                fault_receipt(fault_id, point, 'history-prefix', {'package_id': before.snapshot.package_id,
                    'revision': before.revision, 'digest': before.snapshot.digest, 'bytes': base64.b64encode(before.snapshot.source_bytes).decode('ascii')})
                fault_receipt(fault_id, point, 'receiver-oracle', {'custody_consumed': consumed(env[-2]),
                    'active_holds': [holds(o.owner) for o in env[6]], 'coordinator_killed': True,
                    'native_scientific_execution': False, 'scope': 'cooperative same-host process death before native entry'})
                c, ctx, original, journal, jctx, owners, custody = reopen_packet(value)
                account = reference(value['account'], 'account')
                current = journal.head(account, jctx)
                self.assertTrue(any(r['id'] == group for r in current.value.snapshot.records))
                result = c.admit(original, current.value, ctx, group)
                self.assertEqual(result.state, 'completed', result.issues)
                self.assertTrue(all(holds(o.owner) == 1 for o in owners))
                out = c.issue(result.value, ctx, d)
                if point == 'after_issue_intent':
                    self.assertEqual(out.state, 'partial', out.issues)
                    self.assertIsNone(out.value.token.runtime_permit); self.assertEqual(consumed(custody), 0)
                else:
                    self.assertEqual(out.state, 'completed', out.issues); self.assertEqual(consumed(custody), 1)
                    replay = c.issue(result.value, ctx, d)
                    self.assertEqual(replay.state, 'completed', replay.issues)
                    self.assertEqual(consumed(custody), 1)
                after = journal.head(account, jctx).value
                fault_receipt(fault_id, point, 'recovered-view', {'package_id': after.snapshot.package_id,
                    'digest': after.snapshot.digest, 'revision': after.revision, 'same_group': group,
                    'same_D': d, 'issue_state': out.state, 'custody_consumed': consumed(custody),
                    'active_holds': [holds(o.owner) for o in owners], 'bytes': base64.b64encode(after.snapshot.source_bytes).decode('ascii')})

    @covers('T01')
    def test_immutable_validation_cache_does_not_cache_access_or_widen_limits(self):
        from unittest.mock import patch
        from test_audit_execution_wire import fixture
        view, _ = fixture()
        original = codec._parse_snapshot_uncached
        with codec._VALIDATED_LOCK:
            codec._VALIDATED.clear(); codec._VALIDATED_BYTES = 0
        with patch.object(codec, '_parse_snapshot_uncached', wraps=original) as checked:
            first = codec.parse_snapshot(view.source_bytes, LIMITS)
            codec.parse_snapshot(view.source_bytes, LIMITS)
            self.assertEqual(checked.call_count, 1)
            with self.assertRaisesRegex(ExecutionError, 'read_denied'):
                codec.parse_snapshot(view.source_bytes, LIMITS, access=api.supplied_read([identity()]))
            with self.assertRaises(ExecutionError):
                codec.parse_snapshot(view.source_bytes, replace(LIMITS, max_records='1'))
            with self.assertRaises(ExecutionError):
                codec.parse_snapshot(view.source_bytes+b'broken', LIMITS)
            changed = copy.deepcopy(first.digest); changed['value'] = '0' * 64
            with self.assertRaisesRegex(ExecutionError, 'pinned_view_mismatch'):
                codec.Resolver((replace(first, digest=changed),), limits=LIMITS)
        self.assertLessEqual(codec._VALIDATED_BYTES, codec._VALIDATED_MAX_BYTES)

    @covers('T01')
    def test_pure_plan_open_replay_and_original_frontier(self):
        with scratch() as root:
            env = setup(root); c, ctx, view, request, journal, jctx, allocations, custody, commission = env
            first = c.open(commission, ctx)
            self.assertEqual(first.value.package_id, view.package_id)
            self.assertEqual(c.open(replace(commission, purpose='execute'), ctx).state, 'rejected')
            p = prepared(env)
            self.assertEqual(holds(allocations[0].owner), 0)
            self.assertEqual(consumed(custody), 0)
            original_frontier = p.requirements.frontier
            a = admitted(env, p)
            self.assertEqual(a.prepared.requirements.frontier, original_frontier)
            out = c.issue(a, ctx, identity())
            self.assertEqual(out.state, 'completed', out.issues)
            self.assertEqual(consumed(custody), 1)
            self.assertEqual(holds(allocations[0].owner), 1)

    @covers('F04', 'X03')
    def test_partial_owners_and_missing_participant_cannot_forward_or_release(self):
        with scratch() as root:
            env = setup(root, capacities=('20', '0'))
            p = prepared(env); c, ctx, _, _, journal, jctx, owners, custody, commission = env
            group = identity(); result = c.admit(p, journal.head(reference(commission.account_id, 'account'), jctx).value, ctx, group)
            self.assertEqual(result.state, 'rejected'); self.assertNotIsInstance(result.value, api.LiveAdmission)
            self.assertEqual(holds(owners[0].owner), 1); self.assertEqual(holds(owners[1].owner), 0)
            self.assertEqual(consumed(custody), 0)
            self.assertTrue(any(r['id'] == group for r in journal.head(reference(commission.account_id, 'account'), jctx).value.snapshot.records))
        with scratch() as root:
            env = setup(root, required=('owner0', 'unavailable_participant')); p = prepared(env)
            c, ctx, _, _, journal, jctx, owners, custody, commission = env
            result = c.admit(p, journal.head(reference(commission.account_id, 'account'), jctx).value, ctx, identity())
            self.assertEqual(result.issues[0].code, 's3.required_owner_missing')
            self.assertEqual(holds(owners[0].owner), 0); self.assertEqual(consumed(custody), 0)

    @covers('F18')
    def test_lost_admit_and_issue_replies_reconcile_original_occurrences(self):
        for label in ('before_admit_reply', 'before_issue_reply'):
            with self.subTest(label=label), scratch() as root:
                enabled = [True]
                def fault(point):
                    if point == label and enabled[0]: enabled[0] = False; raise OSError('injected lost reply')
                env = setup(root, fault=fault); c, ctx, _, _, journal, jctx, owners, custody, commission = env
                p = prepared(env); group = identity(); account = reference(commission.account_id, 'account')
                first = c.admit(p, journal.head(account, jctx).value, ctx, group)
                if label == 'before_admit_reply': self.assertEqual(first.state, 'rejected')
                replay = c.admit(p, journal.head(account, jctx).value, ctx, group)
                self.assertEqual(replay.state, 'completed', replay.issues)
                self.assertEqual(replay.value.admission_occurrence, group); self.assertEqual(holds(owners[0].owner), 1)
                d = identity(); result = c.issue(replay.value, ctx, d)
                if label == 'before_issue_reply':
                    self.assertEqual(result.state, 'partial')
                    self.assertTrue(result.value.result.live_handles)
                again = c.issue(replay.value, ctx, d)
                self.assertEqual(again.state, 'completed', again.issues)
                self.assertIsNone(again.value.token.runtime_permit)
                self.assertEqual(again.value.transmission['target'], d); self.assertEqual(consumed(custody), 1)
                self.assertEqual(c.issue(replay.value, ctx, identity()).state, 'rejected')
                self.assertEqual(c.issue(replace(replay.value), ctx, d).issues[0].code, 's3.actual_live_admission_required')
                with self.assertRaises(TypeError): copy.copy(again.value.token.runtime_permit) if again.value.token.runtime_permit else copy.copy(replay.value.live_grants[0])
                changed = c.plan(env[2], replace(env[3], request_occurrence=identity()), ctx.read)
                self.assertEqual(changed.state, 'completed', changed.issues)
                conflicted = c.admit(changed.value, journal.head(account, jctx).value, ctx, group)
                self.assertEqual(conflicted.issues[0].code, 's3.admission_occurrence_binding_conflict')
                self.assertEqual(holds(owners[0].owner), 1); self.assertEqual(consumed(custody), 1)
                variant='admit_reply_lost' if label=='before_admit_reply' else 'issue_reply_lost'
                prefix={'request_view':retained_snapshot(p.source_view),'command':p.command,'group':group,'D':d,'injected_boundary':label}
                observed={'current':retained_snapshot(journal.head(account,jctx).value.snapshot),'same_group':replay.value.admission_occurrence,
                    'same_D':again.value.transmission,'runtime_permit_on_replay':False,'changed_binding':'conflict'}
                actual={'custody_consumed':consumed(custody),'owner_holds':holds(owners[0].owner),'native_scientific_calls':0}
                triplet('F18',variant,actual,prefix,observed)
                if label=='before_issue_reply':triplet('F18','same_D_receipt_replayed',actual,prefix,observed)

    @covers('F05')
    def test_durable_intent_before_entry_never_resends_after_lost_reply(self):
        with scratch() as root:
            def fault(point):
                if point == 'after_issue_intent': raise OSError('interruption before native entry')
            env = setup(root, fault=fault); p = prepared(env); a = admitted(env, p)
            c, ctx, _, _, journal, jctx, owners, custody, commission = env
            d = identity(); self.assertEqual(c.issue(a, ctx, d).state, 'rejected')
            out = c.issue(a, ctx, d)
            self.assertEqual(out.state, 'partial', out.issues); self.assertIsNone(out.value.token.runtime_permit)
            self.assertEqual(out.effects[0].boundary, 'may_have_crossed'); self.assertEqual(consumed(custody), 0)

    @covers('F17', 'T01')
    def test_owner_expiry_and_unknown_clock_hold_native_entry(self):
        now = [100]
        with scratch() as root:
            env = setup(root, owner_clock=lambda: now[0]); p = prepared(env); a = admitted(env, p)
            now[0] += 300000000001
            out = env[0].issue(a, env[1], identity())
            self.assertEqual(out.state, 'rejected'); self.assertEqual(consumed(env[-2]), 0)
            account=reference(env[-1].account_id,'account')
            triplet('F17','owner_expired',{'custody_consumed':consumed(env[-2])},
                {'admission_view':retained_snapshot(a.prepared.source_view),'clock_ticks':str(now[0])},
                {'current':retained_snapshot(env[4].head(account,env[5]).value.snapshot),'issues':[i.code for i in out.issues]})

        with scratch() as root:
            deadline = known({'time_type': 'utc_instant', 'value': '2099-01-01T00:00:00Z', 'precision': 'second',
                'clock': unknown(), 'uncertainty_seconds': known(number('0'))})
            env = setup(root, deadline=deadline); p = prepared(env)
            c, ctx, _, _, journal, jctx, owners, custody, commission = env
            result = c.admit(p, journal.head(reference(commission.account_id, 'account'), jctx).value, ctx, identity())
            self.assertEqual(result.issues[0].code, 's3.comparable_clock_bound_unestablished')
            self.assertEqual(holds(owners[0].owner), 0)

    @covers('F17', 'T01')
    def test_clock_becomes_uncertain_after_D_commit_retains_same_D_and_reason(self):
        class ScriptClock:
            def __init__(self): self.calls = 0
            def now(self, context):
                self.calls += 1
                value = {'time_type': 'utc_instant', 'value': '2026-11-04T00:00:00Z', 'precision': 'second',
                    'clock': unknown(), 'uncertainty_seconds': known(number('0')) if self.calls <= 2 else unknown('s3.fixture.clock_bound_lost')}
                return api.CallResult('completed', api.ClockReading(known(value), unknown(), api.RecordDelta()))
        with scratch() as root:
            deadline = known({'time_type': 'utc_instant', 'value': '2026-11-05T00:00:00Z', 'precision': 'second',
                'clock': unknown(), 'uncertainty_seconds': known(number('0'))})
            env = setup(root, deadline=deadline); c, ctx, _, _, journal, jctx, _, custody, commission = env
            clock = ScriptClock(); ctx = replace(ctx, clock=clock); env = (c, ctx, *env[2:])
            plan = prepared(env); admission = admitted(env, plan); d = identity()
            out = c.issue(admission, ctx, d)
            self.assertEqual(out.state, 'rejected'); self.assertEqual(out.effects[0].boundary, 'not_crossed')
            self.assertEqual(out.issues[0].code, 's3.comparable_clock_bound_unestablished')
            head = journal.head(reference(commission.account_id, 'account'), jctx).value
            self.assertTrue(any(r['record_type'] == 's3.diagnostic' and r['payload']['code'] == out.issues[0].code for r in head.snapshot.records))
            self.assertEqual(consumed(custody), 0)
            replay = c.issue(admission, ctx, d)
            self.assertEqual(replay.state, 'partial'); self.assertIsNone(replay.value.token.runtime_permit)
            self.assertEqual(replay.value.transmission['target'], d); self.assertEqual(consumed(custody), 0)
            triplet('F17','clock_unknown_after_intent',{'custody_consumed':consumed(custody),'clock_reads':clock.calls},
                {'intent_cutoff':retained_snapshot(head.snapshot),'D':d,'issue_reason':out.issues[0].code},
                {'current':retained_snapshot(journal.head(reference(commission.account_id,'account'),jctx).value.snapshot),
                 'same_D':replay.value.transmission,'runtime_permit':False,'state':replay.state})


    @covers('T01')
    def test_changed_prepared_binding_and_unavailable_rule_or_preparer_hold(self):
        with scratch() as root:
            env = setup(root); c, ctx, view, req, journal, jctx, _, custody, commission = env
            p = prepared(env)
            mutated = copy.deepcopy(p.source_view.digest); mutated['value'] = '0' * 64
            bad = replace(p, source_view=replace(p.source_view, digest=mutated))
            result = c.admit(bad, journal.head(reference(commission.account_id, 'account'), jctx).value, ctx, identity())
            self.assertEqual(result.state, 'rejected'); self.assertEqual(consumed(custody), 0)
            self.assertEqual(Coordinator().plan(view, req, ctx.read).state, 'rejected')
            ctx.read.registry.drivers._preparers.clear()
            self.assertEqual(c.plan(view, req, ctx.read).issues[0].code, 's3.pure_preparer_unavailable')
