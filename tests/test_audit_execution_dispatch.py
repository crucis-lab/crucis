"""B07 independent native receiver and guarded dispatch cases (DLV-08/09)."""
import base64
from dataclasses import replace
import json
import subprocess
from concurrent.futures import ThreadPoolExecutor
import queue
import threading
from pathlib import Path
import sys
import unittest
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT/'tests/audit_fixtures/sc3_runtime'))
from test_audit_execution_wire import covers
from test_audit_execution_journal import scratch
import dispatch_case as case
from audit_fixtures.sc3_runtime.receipt_case import snapshot as retained_snapshot, triplet
from crucis_causal.execution import api, codec
from crucis_causal.execution.identity import NativeConnections, coordinate
from crucis_causal.execution.model import ExecutionError, canonical, contract, digest, identity, known, unknown
from crucis_causal.connections.validation import content_bytes


def native_request(*, command=None, transmission=None, epoch='0', native_id=None, pause=False, drop_reply=False):
    return {'command': command or identity(), 'transmission': transmission or identity(), 'binding_digest': digest(b'independent-fixture-request'),
        'epoch': epoch, 'mode': 'remote', 'data': base64.b64encode(case.input_case.SOURCE).decode(),
        'pause': pause, 'drop_reply': drop_reply, 'native_id': native_id}


def lookup_documents(result):
    values = []
    for view in result.records.dependencies:
        for record in view.records:
            if record['record_type'] != 's3.typed_payload' or record['payload']['payload_contract'] != contract('s3.native.lookup_evidence'): continue
            ref = record['payload']['content']['artifact']
            origin = next(v for v in result.records.dependencies if v.package_id == ref['package_id'])
            artifact = next(r for r in origin.records if r['id'] == ref['target'])
            values.append(json.loads(content_bytes(artifact['payload']['content'])))
    return values


class DispatchCases(unittest.TestCase):
    @covers('F06')
    def test_killed_coordinator_cold_recovery_keeps_provider_job_and_original_unknown_D(self):
        from test_audit_execution_coordinator import fault_receipt
        with scratch() as root, case.service(root/'provider') as (client, provider):
            env = case.Environment(root/'coordinator', client)
            result = env.plan(env.launch(drop_reply=True)); self.assertEqual(result.state, 'completed', result.issues)
            group, d = identity(), identity(); packet = case.packet(env, result.value, group, d)
            path = root/'dispatch-packet.json'; path.write_bytes(canonical(packet))
            child = subprocess.Popen([sys.executable, '-B', str(ROOT/'tests/audit_fixtures/sc3_runtime/dispatch_worker.py'), str(path)],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0)
            messages = queue.Queue(); reader = threading.Thread(target=lambda: messages.put(child.stdout.readline()), daemon=True); reader.start()
            try:
                child.stdin.write(json.dumps({'token': client._token})+'\n'); child.stdin.flush()
                line = messages.get(timeout=60)
                if line.strip() != 'READY:before_issue_reply':
                    if child.poll() is None: child.terminate(); child.wait(timeout=10)
                    raise AssertionError('owned recovery barrier absent: '+line+child.stderr.read())
                child.kill(); child.wait(timeout=15)
            finally:
                if child.poll() is None: child.kill(); child.wait(timeout=15)
                reader.join(timeout=5)
                for stream in (child.stdin, child.stdout, child.stderr): stream.close()
            self.assertFalse(reader.is_alive()); self.assertIsNone(provider.poll())
            oracle = client.call('oracle'); self.assertEqual(len(oracle['jobs']), 1)
            head = env.journal.head(env.account, env.jctx).value
            fault_receipt('F06', 'coordinator_death_after_lost_native_ack', 'receiver-oracle', oracle)
            fault_receipt('F06', 'coordinator_death_after_lost_native_ack', 'history-prefix', {'package_id': head.snapshot.package_id,
                'digest': head.snapshot.digest, 'bytes': base64.b64encode(head.snapshot.source_bytes).decode()})
            cold, original = case.reopen(packet, client._token)
            current = cold.journal.head(cold.account, cold.jctx)
            admitted = cold.coordinator.admit(original, current.value, cold.context, group)
            self.assertEqual(admitted.state, 'completed', admitted.issues)
            replay = cold.issue(admitted.value, transmission=d)
            self.assertEqual(replay.state, 'partial', replay.issues); self.assertIsNone(replay.value.token.runtime_permit)
            self.assertEqual(replay.effects[0].acceptance['state'], 'unresolved')
            found = cold.run(cold.lookup(original.command))
            self.assertEqual(found.state, 'completed', found.issues)
            self.assertTrue(any(v['classification'] == 'positive' for v in lookup_documents(found)))
            self.assertEqual(len(client.call('oracle')['jobs']), 1)
            restored = cold.journal.head(cold.account, cold.jctx).value
            fault_receipt('F06', 'coordinator_death_after_lost_native_ack', 'recovered-view', {'package_id': restored.snapshot.package_id,
                'digest': restored.snapshot.digest, 'same_group': group, 'same_D': d, 'native_jobs': 1,
                'bytes': base64.b64encode(restored.snapshot.source_bytes).decode()})

    @covers('OP03H', 'OP04H', 'OP05H')
    def test_missing_or_wrong_native_prerequisites_do_not_forward_and_unknown_lookup_stays_unknown(self):
        with scratch() as root, case.service(root/'provider') as (client, _):
            env = case.Environment(root/'coordinator', client)
            wrong = env.launch(); parameters = json.loads(json.dumps(wrong.parameters))
            next(p for p in parameters if p['key'] == 'invocation')['value'] = unknown('s3.fixture.missing_invocation')
            rejected = env.plan(replace(wrong, parameters=tuple(parameters)))
            self.assertEqual(rejected.state, 'rejected'); self.assertEqual(client.call('oracle')['jobs'], [])
            launched = env.run(env.launch()); self.assertEqual(launched.state, 'completed', launched.issues)
            missing = env.run(env.lookup(launched.value.command, unavailable=True))
            self.assertEqual(missing.state, 'completed', missing.issues)
            self.assertTrue(any(v['classification'] == 'unknown' and v['complete']['value'] is False for v in lookup_documents(missing)))
            descriptor = client.call('query', command=launched.value.command['target'])['matches'][0]
            bad = json.loads(json.dumps(descriptor)); bad['incarnation'] = unknown('s3.fixture.incarnation_missing')
            held = env.plan(env.existing(bad))
            self.assertEqual(held.state, 'rejected'); self.assertEqual(client.call('oracle')['attachments'], [])

    @covers('F07', 'OP03H', 'OP04P')
    def test_receiver_fences_delayed_old_epoch_and_preserves_previously_accepted_work(self):
        from test_audit_execution_coordinator import fault_receipt
        with scratch() as root, case.service(root/'provider') as (client, _):
            old = native_request(); client.call('launch', **old)
            delayed = native_request(pause=True)
            with ThreadPoolExecutor(max_workers=1) as executor:
                pending = executor.submit(client.call, 'launch', **delayed)
                client.call('await_pending', transmission=delayed['transmission'])
                empty = client.call('query', command=delayed['command'])
                self.assertEqual(empty['classification'], 'negative'); self.assertFalse(empty['no_late_acceptance'])
                fault_receipt('F07', 'delayed_request_epoch_takeover', 'history-prefix', {'delayed': delayed, 'query': empty})
                changed = client.call('rotate_epoch'); self.assertEqual(changed['epoch'], '1')
                client.call('release', transmission=delayed['transmission'])
                rejected = pending.result(timeout=20)
                self.assertFalse(rejected['acceptance']['value'])
            oracle = client.call('oracle')
            self.assertEqual(len(oracle['jobs']), 1); self.assertEqual(oracle['jobs'][0]['command'], old['command'])
            self.assertEqual(oracle['jobs'][0]['charge'], '4')
            fault_receipt('F07', 'delayed_request_epoch_takeover', 'receiver-oracle', oracle)
            fault_receipt('F07', 'delayed_request_epoch_takeover', 'recovered-view',
                {'epoch': changed['epoch'], 'delayed_response': rejected, 'accepted_predecessor': old['command']})

    @covers('F06', 'OP04P', 'OP04H')
    def test_negative_before_delayed_acceptance_is_not_closure_and_duplicates_are_retained(self):
        with scratch() as root, case.service(root/'provider') as (client, _):
            original = native_request(pause=True)
            with ThreadPoolExecutor(max_workers=1) as executor:
                delayed = executor.submit(client.call, 'launch', **original)
                client.call('await_pending', transmission=original['transmission'])
                before = client.call('query', command=original['command'])
                self.assertEqual(before['classification'], 'negative'); self.assertFalse(before['no_late_acceptance'])
                # Explicit supervisor negative control, not auditor resubmission.
                duplicate = native_request(command=original['command'])
                client.call('launch', **duplicate)
                client.call('release', transmission=original['transmission']); delayed.result(timeout=20)
            found = client.call('query', command=original['command'])
            self.assertEqual(len(found['matches']), 2); self.assertEqual(found['charges'], ['4', '4'])
            self.assertNotEqual(coordinate(found['matches'][0]), coordinate(found['matches'][1]))
            empty_command = identity(); client.call('close_command', command=empty_command)
            closed = client.call('query', command=empty_command)
            self.assertEqual(closed['classification'], 'negative'); self.assertTrue(closed['no_late_acceptance'])
            later = client.call('launch', **native_request(command=empty_command))
            self.assertFalse(later['acceptance']['value'])
            triplet('F06','negative_lookup_before_delayed_original_arrives',client.call('oracle'),
                {'original_request':original,'negative_before_arrival':before,'supervisor_duplicate_request':duplicate,
                 'scope':'Native receiver negative control; deliberate supervisor duplicate, not auditor resubmission'},
                {'retained_matches':found,'separately_closed_ingress':closed,'late_closed_command_response':later})

    @covers('X06', 'OP05P')
    def test_unknown_origin_attach_has_no_fabricated_R_A_or_trial(self):
        with scratch() as root, case.service(root/'provider') as (client, _):
            descriptor = client.call('launch', **native_request())['descriptor']
            env = case.Environment(root/'coordinator', client, scientific_path=None)
            before = {r['id'] for v in env.context.read.views for r in v.records if r['record_type'] in ('s1.request','s1.attempt','s2.trial_slot')}
            self.assertEqual(before, set())
            result = env.run(env.existing(descriptor))
            self.assertEqual(result.state, 'completed', result.issues)
            self.assertEqual(len(result.value.result.live_handles), 1)
            after = {r['id'] for v in result.records.dependencies for r in v.records if r['record_type'] in ('s1.request','s1.attempt','s2.trial_slot')}
            self.assertEqual(after, set()); self.assertEqual(len(client.call('oracle')['jobs']), 1)

    @covers('OP03P', 'OP03H')
    def test_actual_S1_function_and_shell_false_process_keep_native_guards_and_frozen_R(self):
        from dataclasses import replace
        from crucis_causal.connections import api as a1
        from crucis_causal.connections.model import contract as c1, known as k1, source as source1, unknown_ref as u1, unresolved
        from crucis_causal.connections.ports import supplied_connection
        from crucis_causal.connections.services import RuntimeAuthority, execution_binding, HandleRegistry
        from crucis_causal.experiments.handoff import freeze_s1
        from crucis_causal.experiments.api import ReaderLimits
        from crucis_causal.execution.bridge import working_s1
        from crucis_causal.execution.s1_native import S1Invocation
        from test_audit_connections_ports import setup, bind
        from test_audit_connections_history import attempt
        for mode in ('function', 'process'):
            with self.subTest(mode=mode), scratch() as root:
                b, services, sink = setup(); authority = RuntimeAuthority(); calls = []
                script = ROOT/'tests/audit_fixtures/sc3_runtime/process_echo.py'
                arguments = ['literal&not_a_shell', '$(literal)', str(root/'must-not-be-created')]
                invocation = ({'kind': 'function', 'entrypoint': c1('fixture_function'), 'arguments': []} if mode == 'function' else
                    {'kind': 'process', 'executable': sys.executable, 'argv': [str(script), *arguments],
                     'cwd': u1('location'), 'environment_policy': u1('policy')})
                def execute(descriptor, context, capture):
                    calls.append(mode)
                    if mode == 'function': raw = b'actual local function result'; runtime = raw
                    else:
                        completed = subprocess.run([descriptor['executable'], '-B', *descriptor['argv']], cwd=root,
                            env={'PYTHONUTF8': '1', 'PYTHONDONTWRITEBYTECODE': '1'}, capture_output=True, timeout=10, shell=False,
                            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0)
                        self.assertEqual(completed.returncode, 0, completed.stderr)
                        raw = completed.stdout; runtime = completed
                        self.assertEqual(json.loads(raw)['argv'], arguments)
                        self.assertEqual(Path(json.loads(raw)['cwd']).resolve(), root.resolve())
                        self.assertFalse((root/'must-not-be-created').exists())
                    captured = capture.capture(raw)
                    return a1.NativeHandle(context.attempt, unresolved(), runtime, (captured,), ())
                ports = supplied_connection(b.producer, services, invocation, authority=authority, executor=execute)
                request, policy, bound = bind(b, services, ports, 'direct')
                a = attempt(b, request)
                spec = ports.prepare(bound.value, a1.PrepareContext(policy, services.identities), sink).value
                auth = b.add('authority_evidence', {'actor': b.producer, 'policy': policy, 'operation': spec.route.operation,
                    'subjects': [a], 'permitted_effects': ['s1.cpu'], 'decision': 'permitted', 'validity': case.scope(a), 'source': source1()})
                grant = a1.ExecutionGrant(request, a, (spec.route.operation,), ('s1.cpu',), (), (policy,), auth, object())
                context = a1.ExecutionContext(grant, a, HandleRegistry())
                frozen = freeze_s1(b.package([request, a, bound.value.binding]), ReaderLimits.standard())
                snapshot = codec.parse_snapshot(frozen.source_bytes, case.L)
                resolver = codec.Resolver((snapshot,), limits=case.L)
                working = working_s1(case.qualified(request, snapshot.package_id), case.qualified(a, snapshot.package_id), resolver, services.records)
                wrong = S1Invocation(working, ports, spec, context, sink)
                denied = wrong.invoke(None)
                self.assertEqual(denied.acceptance['state'], 'unresolved'); self.assertEqual(calls, [])
                token = authority.issue('execute', execution_binding(grant))
                granted = replace(context, grant=replace(grant, runtime_capability=token))
                actual = S1Invocation(working, ports, spec, granted, sink)
                accepted = actual.invoke(None)
                self.assertTrue(accepted.acceptance['value']); self.assertEqual(calls, [mode])
                self.assertTrue(any(r['record_type'] == 's1.artifact_snapshot' for v in accepted.facts.dependencies for r in v.records))
                self.assertNotEqual(denied.facts.dependencies[-1].package_id, accepted.facts.dependencies[-1].package_id)
                self.assertEqual(snapshot.source_bytes, frozen.source_bytes)
                actual.invoke(None); self.assertEqual(calls, [mode])

    @covers('F06')
    def test_independent_receiver_lost_reply_keeps_one_job_and_exact_D_replay(self):
        with scratch() as root, case.service(root/'provider') as (client, process):
            request = native_request(drop_reply=True)
            with self.assertRaises(ExecutionError): client.call('launch', **request)
            oracle = client.call('oracle')
            self.assertEqual(len(oracle['jobs']), 1)
            self.assertEqual(oracle['jobs'][0]['charge'], '4')
            with self.assertRaises(ExecutionError): client.call('launch', **request)
            self.assertEqual(len(client.call('oracle')['jobs']), 1)
            query = client.call('query', command=request['command'])
            self.assertEqual(query['classification'], 'positive'); self.assertEqual(len(query['matches']), 1)
            self.assertFalse(query['no_late_acceptance'])
            self.assertIsNone(process.poll())

    @covers('OP03P', 'OP04P', 'OP05P')
    def test_real_coordinator_launch_lookup_and_attach_never_relaunch(self):
        with scratch() as root, case.service(root/'provider') as (client, process):
            env = case.Environment(root/'coordinator', client)
            launched = env.run(env.launch())
            self.assertEqual(launched.state, 'completed', launched.issues)
            self.assertEqual(len(client.call('oracle')['jobs']), 1)
            command = launched.value.command
            found = env.run(env.lookup(command))
            self.assertEqual(found.state, 'completed', found.issues)
            payloads = lookup_documents(found)
            self.assertTrue(payloads)
            self.assertTrue(all(v['classification'] == 'positive' and v['no_late_acceptance']['value'] is False for v in payloads))
            descriptor = client.call('query', command=command['target'])['matches'][0]
            attempt = next(r['members']['members'][0] for r in env.launch_roles if r['role'] == 's3.role.attempt')
            attached = env.run(env.existing(descriptor, attempt=attempt))
            self.assertEqual(attached.state, 'completed', attached.issues)
            self.assertEqual(len(attached.value.result.live_handles), 1)
            oracle = client.call('oracle')
            self.assertEqual(len(oracle['jobs']), 1); self.assertEqual(len(oracle['attachments']), 1)
            self.assertIsNone(process.poll())

    @covers('F06', 'OP04P')
    def test_common_pipeline_lost_ack_preserves_unknown_then_exact_lookup(self):
        with scratch() as root, case.service(root/'provider') as (client, _):
            env = case.Environment(root/'coordinator', client)
            planned = env.plan(env.launch(drop_reply=True)); self.assertEqual(planned.state, 'completed', planned.issues)
            admitted = env.admit(planned.value); self.assertEqual(admitted.state, 'completed', admitted.issues)
            d = identity(); out = env.issue(admitted.value, transmission=d)
            uncertain_prefix=retained_snapshot(env.journal.head(env.account,env.jctx).value.snapshot)
            self.assertEqual(out.state, 'partial', out.issues)
            self.assertEqual(out.effects[0].boundary, 'may_have_crossed')
            self.assertEqual(out.effects[0].acceptance['state'], 'unresolved')
            self.assertEqual(len(client.call('oracle')['jobs']), 1)
            replay = env.issue(admitted.value, transmission=d)
            self.assertEqual(replay.state, 'partial', replay.issues); self.assertIsNone(replay.value.token.runtime_permit)
            self.assertEqual(len(client.call('oracle')['jobs']), 1)
            result = env.run(env.lookup(planned.value.command))
            self.assertEqual(result.state, 'completed', result.issues)
            self.assertTrue(any(v['classification'] == 'positive' for v in lookup_documents(result)))
            self.assertEqual(len(client.call('oracle')['jobs']), 1)
            triplet('F06','provider_accepted_reply_lost',client.call('oracle'),
                {'uncertain_account':uncertain_prefix,'C':planned.value.command,'D':d,'acceptance':out.effects[0].acceptance},
                {'current':retained_snapshot(env.journal.head(env.account,env.jctx).value.snapshot),
                 'lookup':lookup_documents(result),'same_D_replay_has_permit':False})


    @covers('X08', 'OP05H')
    def test_actual_connection_registry_never_uses_only_literal_reused_ID(self):
        with scratch() as root, case.service(root/'provider') as (client, _):
            first = client.call('launch', **native_request(native_id='reused'))['descriptor']
            second = client.call('launch', **native_request(native_id='reused'))['descriptor']
            self.assertNotEqual(coordinate(first), coordinate(second))
            with self.assertRaises(ExecutionError): client.call('attach', descriptor=first, epoch='0', role='controller')
            successful = client.call('attach', descriptor=second, epoch='0', role='observer')
            self.assertEqual(successful['descriptor'], second)
            registry = NativeConnections(); live = case.Connection(client, first, 'original')
            handle = registry.bind(first, live, 's3.connection.observer', '0', {})
            with self.assertRaises(ExecutionError): registry.get(handle, descriptor=second)
            with self.assertRaises(ExecutionError): registry.get(object.__new__(api.OpaqueHandle))
            changed_basis = json.loads(json.dumps(first)); changed_basis['incarnation']['basis'] = []
            self.assertEqual(coordinate(changed_basis), coordinate(first))
