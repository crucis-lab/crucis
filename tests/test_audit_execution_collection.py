"""B08 actual capture/source/ACK gates over an independent receiver (DLV-08/09)."""
import base64
import copy
from dataclasses import replace
import json
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'tests/audit_fixtures/sc3_runtime'))
from test_audit_execution_wire import covers, fixture
from test_audit_execution_journal import scratch
from test_audit_execution_dispatch import native_request
from test_audit_execution_coordinator import fault_receipt
import dispatch_case as case
import observation_case as obs
from crucis_causal.execution import api, codec
from crucis_causal.execution.model import Builder, ExecutionError, canonical, contract, digest, identity, index, known, qualified, reference, scope, unknown


def native_events(env):
    result=env.journal.head(env.account,env.jctx);read=case.read_with(env.context.read,*result.records.dependencies,result.value.snapshot)
    resolver=codec.Resolver(read.views,limits=case.L);values=[]
    for record in result.value.snapshot.records:
        if record['record_type']=='s3.typed_payload' and record['payload']['payload_contract']==contract('s3.fixture.native_event'):
            values.append(case.content(resolver,reference(record['id'],'typed_payload',result.value.snapshot.package_id),result.value.snapshot.package_id,contract('s3.fixture.native_event')))
    return values


def capture_source(env, source=None):
    request=env.observe(source=source)
    plan=env.plan(request);assert plan.state=='completed',plan.issues
    binding,_,_=env.coordinator._actual(plan.value,env.context.read)
    return obs.source_identity(binding,binding.inputs,env.context.read)


def receipts(case_id,variant,env,client,**facts):
    head=env.journal.head(env.account,env.jctx).value
    fault_receipt(case_id,variant,'history-prefix',{'package':head.snapshot.package_id,'digest':head.snapshot.digest,'bytes':base64.b64encode(head.snapshot.source_bytes).decode()})
    fault_receipt(case_id,variant,'receiver-oracle',client.call('oracle')|{'ack':env.oracle_ack()})
    fault_receipt(case_id,variant,'recovered-view',facts)


class CollectionCases(unittest.TestCase):
    @covers('OP06P','OP07P','X02')
    def test_capture_three_occurrences_two_native_events_then_separate_ack(self):
        with scratch() as root, case.service(root/'provider') as (client,_):
            descriptor=client.call('launch',**native_request())['descriptor']
            env=obs.Environment(root/'coordinator',client,descriptor,max_events='3')
            first=env.run(env.observe(max_events='2'))
            self.assertEqual(first.state,'completed',first.issues)
            a=env.capture();self.assertEqual(len(a.artifacts),2)
            resolver=codec.Resolver(env.context.read.views,limits=case.L)
            fragment,_=resolver.record(a.artifacts[0],a.artifacts[0]['package_id'])
            from crucis_causal.connections.validation import content_bytes
            self.assertEqual(content_bytes(fragment['payload']['content']),b'{"graph":')
            self.assertEqual(env.oracle_ack()['updates'],'0')
            second=env.run(env.observe(cursor_value=a.durable_cursor,max_events='1'))
            self.assertEqual(second.state,'completed',second.issues)
            b=env.capture();self.assertEqual(len(b.artifacts),1)
            events=native_events(env)
            self.assertEqual(len(events),3);self.assertEqual(len({x['native_event'] for x in events}),2)
            self.assertEqual([x['native_sequence'] for x in sorted(events,key=lambda x:int(x['transport_offset']))],['2','1','1'])
            self.assertEqual(len({x['capture'] for x in events}),3)
            self.assertEqual(env.oracle_ack()['position'],None)
            acknowledged=env.run(env.acknowledge(b))
            self.assertEqual(acknowledged.state,'completed',acknowledged.issues)
            self.assertEqual(env.oracle_ack()['position'],'3');self.assertEqual(env.oracle_ack()['updates'],'1')
            self.assertEqual(len(client.call('oracle')['jobs']),1)
            head=env.journal.head(env.account,env.jctx).value.snapshot
            progress=[r['payload'] for r in head.records if r['record_type']=='s3.source_frontier' and r['payload']['durably_captured']['state']=='known']
            self.assertTrue(progress);self.assertTrue(all(p['interpreted']['state']=='unresolved' for p in progress))
            self.assertTrue(any(p['acknowledged']['state']=='unresolved' for p in progress))
            self.assertTrue(any(p['acknowledged']==b.durable_cursor for p in progress))

    @covers('F08','F19','OP06H','OP07H')
    def test_raw_write_flush_and_space_faults_preserve_bytes_without_cursor_or_ack(self):
        for case_id,barrier in [('F08','artifact_before_flush'),('F19','artifact_after_flush')]:
            with self.subTest(barrier=barrier),scratch() as root,case.service(root/'provider') as (client,_):
                descriptor=client.call('launch',**native_request())['descriptor'];env=obs.Environment(root/'coordinator',client,descriptor)
                prepared=env.plan(env.observe());self.assertEqual(prepared.state,'completed',prepared.issues)
                admitted=env.admit(prepared.value);self.assertEqual(admitted.state,'completed',admitted.issues)
                original=env.mechanics_stream.observe
                def observed(call):
                    result=original(call)
                    def fail(label):
                        if label==barrier:
                            env.journal.artifacts.fault=None
                            raise OSError(28,'injected bounded I/O failure')
                    env.journal.artifacts.fault=fail
                    return result
                method=env.stream_driver.methods[obs.OPS[0]['name']]
                from crucis_causal.execution.registry import supplied_callable
                env.stream_driver.methods[obs.OPS[0]['name']]=replace(method,execute=supplied_callable(observed))
                failed=env.issue(admitted.value)
                self.assertEqual(failed.state,'partial',failed.issues);self.assertTrue(failed.value.result.records.dependencies)
                self.assertEqual(env.captures(),[]);self.assertEqual(env.oracle_ack()['updates'],'0')
                fresh=obs.reopen(env);source=capture_source(fresh)
                self.assertEqual(fresh.journal.checkpoint(fresh.account,source,fresh.jctx)['state'],'unresolved')
                retried=fresh.run(fresh.observe());self.assertEqual(retried.state,'completed',retried.issues)
                self.assertEqual(len(fresh.capture().artifacts),3);self.assertEqual(fresh.oracle_ack()['updates'],'0')
                self.assertEqual(len(client.call('oracle')['stream_reads']),2)
                self.assertLess(int(fresh.owner.remaining_control(fresh.allocation)),1000)
                receipts(case_id,barrier,fresh,client,captures=len(fresh.captures()),ack=fresh.oracle_ack(),native_jobs='1',original_cursor_advanced=False)

    @covers('F09','OP06P','OP07P')
    def test_capture_committed_before_reply_recovers_original_batch_before_ack(self):
        with scratch() as root,case.service(root/'provider') as (client,_):
            descriptor=client.call('launch',**native_request())['descriptor']
            def fail(label):
                if label=='after_capture_commit':raise ExecutionError('s3.fixture.capture_reply_lost')
            env=obs.Environment(root/'coordinator',client,descriptor,fault=fail)
            failed=env.run(env.observe());self.assertEqual(failed.state,'partial',failed.issues)
            original=env.capture();self.assertEqual(env.oracle_ack()['updates'],'0')
            prefix_head=env.journal.head(env.account,env.jctx).value;prefix=prefix_head.snapshot
            fresh=obs.reopen(env);recovered=fresh.capture(original.occurrence)
            self.assertEqual(recovered.artifacts,original.artifacts);self.assertEqual(recovered.durable_cursor,original.durable_cursor)
            self.assertEqual(fresh.run(fresh.acknowledge(recovered)).state,'completed')
            self.assertEqual(fresh.oracle_ack()['updates'],'1')
            self.assertEqual(prefix.source_bytes,fresh.journal.snapshot(fresh.account,prefix_head.revision,fresh.jctx).value.source_bytes)
            receipts('F09','capture_commit_before_ack',fresh,client,same_batch=original.occurrence,same_artifacts=original.artifacts,ack=fresh.oracle_ack())

    @covers('X02','OP06H','OP07H')
    def test_source_alias_filter_generation_and_consumer_cannot_inherit_cursor(self):
        with scratch() as root,case.service(root/'provider') as (client,_):
            descriptor=client.call('launch',**native_request())['descriptor'];env=obs.Environment(root/'coordinator',client,descriptor)
            self.assertEqual(env.run(env.observe(max_events='1')).state,'completed');first=env.capture()
            alias,_=env.add_source(generation=known(descriptor['incarnation']['value'],basis=[env.native_subject]))
            aliased,_=codec.Resolver(env.context.read.views,limits=case.L).record(alias,alias['package_id'])
            self.assertEqual(aliased['payload']['generation']['basis'],[env.native_subject])
            held=env.run(env.observe(source=alias,max_events='1'))
            self.assertEqual(held.state,'rejected',held.issues)
            self.assertEqual(held.effects[0].boundary,'not_crossed')
            self.assertEqual(len(env.captures()),1)
            partition,_=env.add_source(partition='p1')
            wrong=env.run(env.observe(source=partition,cursor_value=first.durable_cursor,max_events='1'))
            self.assertEqual(wrong.state,'rejected',wrong.issues)
            self.assertEqual(wrong.effects,())
            self.assertEqual(len(client.call('oracle')['stream_reads']),1)
            missing,_=env.add_source(generation=unknown('s3.fixture.generation_unknown'))
            self.assertEqual(env.plan(env.observe(source=missing,max_events='1')).state,'rejected')
            wrong_ack=env.run(env.acknowledge(first,source=partition))
            self.assertEqual(wrong_ack.state,'rejected',wrong_ack.issues);self.assertEqual(env.oracle_ack()['updates'],'0')
            self.assertEqual(env.run(env.observe(source=partition,max_events='1')).state,'completed')
            other=env.capture();self.assertNotEqual(other.source.filter_digest,first.source.filter_digest)

    @covers('F09','OP07P','OP07H')
    def test_unknown_capture_commit_requires_actual_reconciliation_before_ack(self):
        from crucis_causal.execution.registry import supplied_callable
        with scratch() as root,case.service(root/'provider') as (client,_):
            descriptor=client.call('launch',**native_request())['descriptor'];env=obs.Environment(root/'coordinator',client,descriptor)
            armed=[False]
            def io_fault(label):
                if armed[0] and label=='after_journal_commit':
                    armed[0]=False
                    raise OSError('injected capture commit reply loss')
            env.jctx=replace(env.jctx,fault=io_fault)
            original=env.mechanics_stream.observe
            def fetched(call):
                result=original(call);armed[0]=True;return result
            method=env.stream_driver.methods[obs.OPS[0]['name']]
            env.stream_driver.methods[obs.OPS[0]['name']]=replace(method,execute=supplied_callable(fetched))
            interrupted=env.run(env.observe())
            self.assertEqual(interrupted.state,'partial',interrupted.issues)
            self.assertEqual(interrupted.issues[0].code,'s3.capture_commit_unconfirmed')
            self.assertEqual(env.oracle_ack()['updates'],'0')
            fresh=obs.reopen(env);capture=fresh.capture()
            self.assertEqual(len(capture.artifacts),3)
            self.assertEqual(fresh.run(fresh.acknowledge(capture)).state,'completed')
            self.assertEqual(fresh.oracle_ack()['updates'],'1')
            self.assertEqual(len(client.call('oracle')['stream_reads']),1)
            receipts('F09','unknown_capture_commit_reconciled',fresh,client,capture=capture.occurrence,artifacts=capture.artifacts,ack=fresh.oracle_ack(),source_reads='1')

    @covers('F09','OP06H','OP07P')
    def test_lost_ack_reply_replays_original_D_without_another_source_ack(self):
        with scratch() as root,case.service(root/'provider') as (client,_):
            descriptor=client.call('launch',**native_request())['descriptor'];env=obs.Environment(root/'coordinator',client,descriptor)
            self.assertEqual(env.run(env.observe()).state,'completed');capture=env.capture()
            prepared=env.plan(env.acknowledge(capture));self.assertEqual(prepared.state,'completed',prepared.issues)
            group,d=identity(),identity();admitted=env.admit(prepared.value,group=group)
            self.assertEqual(admitted.state,'completed',admitted.issues)
            client.call('arm_ack_loss')
            lost=env.issue(admitted.value,transmission=d)
            self.assertEqual(lost.state,'partial',lost.issues)
            self.assertEqual(lost.effects[0].acceptance['state'],'unresolved')
            self.assertEqual(env.oracle_ack()['updates'],'1')
            fresh=obs.reopen(env)
            restored=fresh.coordinator.restore_prepared(prepared.value.command,prepared.value.source_view,fresh.context.read)
            self.assertEqual(restored.state,'completed',restored.issues)
            again=fresh.admit(restored.value,group=group);self.assertEqual(again.state,'completed',again.issues)
            replay=fresh.issue(again.value,transmission=d)
            self.assertEqual(replay.state,'partial',replay.issues);self.assertIsNone(replay.value.token.runtime_permit)
            self.assertEqual(fresh.oracle_ack()['updates'],'1')
            # The native source owns this virtual deadline. Advancing it does
            # not terminate the job, reset the auditor's budget or advance data.
            client.call('advance_tick',amount='10')
            expired=fresh.run(fresh.observe(cursor_value=capture.durable_cursor,max_events='1'))
            self.assertEqual(expired.state,'partial',expired.issues)
            self.assertTrue(expired.value.result.receipts['members'])
            self.assertEqual(len(client.call('oracle')['stream_reads']),1)
            self.assertEqual(len(client.call('oracle')['jobs']),1)
            self.assertEqual(len(fresh.captures()),1)
            receipts('F09','ack_reply_loss_same_D_recovery',fresh,client,transmission=d,no_replay_permit=True,ack=fresh.oracle_ack(),captures='1',expired_source_reads='0')

    @covers('OP06H','OP07H')
    def test_unsupported_consuming_profile_bounds_and_forged_capture_receipt_hold(self):
        with scratch() as root,case.service(root/'provider') as (client,_):
            descriptor=client.call('launch',**native_request())['descriptor'];env=obs.Environment(root/'coordinator',client,descriptor,max_events='1')
            self.assertEqual(env.plan(env.observe(ack_mode='combined')).state,'rejected')
            over=env.run(env.observe(max_events='2'));self.assertEqual(over.state,'rejected',over.issues)
            self.assertEqual(client.call('oracle')['stream_reads'],[])
            self.assertEqual(env.captures(),[]);self.assertEqual(env.oracle_ack()['updates'],'0')
            self.assertEqual(env.run(env.observe(max_events='1')).state,'completed');captured=env.capture()
            b=Builder('Negative-control forged receipt metadata')
            fake=b.add('journal_receipt',{'account':qualified(env.account,env.view.package_id),'transaction':identity(),'previous_revision':'0','committed_revision':'1',
                'records':index(),'durability':contract('durability.local_process_crash')})
            audience=b.add('audience',{'purpose':contract('s3.private_fixture'),'recipients':index(),'disclosure_policy':obs.unknown_ref('s1.policy'),'authority':unknown()})
            r=b.add('projection_view',{'view_role':'audience_projection','audience':audience,'projection_contract':contract('s3.fixture.forged_receipt'),'members':index([fake]),'claims':index(),'limits':index()})
            v=case.frame(b,r,env.context.read.views);env.include(v)
            request=env.acknowledge(captured)
            changed=replace(request,roles=tuple({'role':x['role'],'members':index([qualified(fake,v.package_id)])} if x['role']=='s3.role.capture_receipt' else x for x in request.roles))
            rejected=env.run(changed);self.assertEqual(rejected.state,'rejected',rejected.issues);self.assertEqual(env.oracle_ack()['updates'],'0')

    @covers('OP06P','W02')
    def test_private_resolver_indexes_never_accept_mutated_return_or_denied_access(self):
        view,resolver=fixture();root=view.package['roots'][0]
        original,_=resolver.record(root,view.package_id);mutated,_=resolver.record(root,view.package_id)
        mutated['payload'].clear()
        self.assertEqual(resolver.record(root,view.package_id)[0],original)
        source=view.package;source['records'].clear();self.assertTrue(resolver.closure(view.package_id))
        duplicate=resolver.add(view);duplicate.format['name']='s3.caller_mutation'
        self.assertEqual(resolver.view(view.package_id).format,view.format)
        read=api.PinnedReadContext((view,),api.supplied_read((view.package_id,)),case.SuppliedRegistryContext(case.ExactDriverRegistry(),case.ExactDecisionRegistry(),case.PayloadRegistry()),case.L)
        changed_bytes=codec.parse_snapshot(view.source_bytes+b' ',case.L)
        with self.assertRaisesRegex(ExecutionError,'package_identity_conflict'):case.read_with(read,changed_bytes)
        # Cached structural success never masks changed fields or tighter
        # transport limits, and does not replace value-level semantic checks.
        bad=view.package;bad['records'][0]['unexpected']=True
        with self.assertRaises(ExecutionError):codec.dumps(bad,case.L)
        with self.assertRaises(ExecutionError):codec.parse_snapshot(view.source_bytes,replace(case.L,max_manifest_bytes='16'))
        invalid_date=view.package
        invalid_date['records'][0]['created_at']=known({'time_type':'utc_instant','value':'2026-02-30T00:00:00Z',
            'precision':'second','clock':unknown(),'uncertainty_seconds':unknown()})
        for _ in range(2):
            with self.assertRaisesRegex(ExecutionError,'invalid_utc_time_or_uncertainty'):codec.dumps(invalid_date,case.L)
        denied=replace(view,read_scope=api.supplied_read(()))
        with self.assertRaises(ExecutionError):resolver.add(denied)
        changed=replace(view,source_bytes=view.source_bytes+b' ')
        with self.assertRaises(ExecutionError):resolver.add(changed)


if __name__=='__main__':unittest.main()
