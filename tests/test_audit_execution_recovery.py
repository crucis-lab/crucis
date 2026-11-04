"""B10 actual stop/load/owner interruptions and pure recovery gates (DLV-08/09)."""
import base64
from dataclasses import replace
from decimal import Decimal
import json
import os
from pathlib import Path
import queue
import subprocess
import sys
import threading
import unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'tests/audit_fixtures/sc3_runtime'))
from test_audit_execution_wire import covers,implementation
from test_audit_execution_journal import scratch
from test_audit_execution_coordinator import fault_receipt
import dispatch_case as case
import recovery_case as recovery
from crucis_causal.execution import api,codec
from crucis_causal.execution.coordinator import read_with
from crucis_causal.execution.model import (Builder,ExecutionError,canonical,contract,identity,index,known,
    not_applicable,number,qualified,reference,scope,unknown,unknown_ref)
from crucis_causal.execution.recovery import RecoveryPolicies,RecoveryRule
from crucis_causal.execution.registry import supplied_callable
from crucis_causal.execution.stopping import close_collection,state_components


def fault(case_id,variant,env,**details):
    native=env.client.call('recovery_oracle')
    head=env.journal.head(env.account,env.jctx)
    fault_receipt(case_id,variant,'receiver-oracle',native)
    fault_receipt(case_id,variant,'history-prefix',{'revision':head.value.revision,'snapshot':head.value.snapshot.package_id,
        'source_digest':head.value.snapshot.digest,'records':str(len(head.value.snapshot.records))})
    fault_receipt(case_id,variant,'recovered-view',details)


def kill_after_reply(env,request,expected):
    planned=env.plan(request)
    if planned.state!='completed':raise AssertionError(planned.issues)
    g,d=identity(),identity();value=recovery.packet(env,planned.value,g,d)
    path=env.root/(identity()+'.packet.json');path.write_bytes(canonical(value))
    child=subprocess.Popen([sys.executable,'-B',str(ROOT/'tests/audit_fixtures/sc3_runtime/recovery_worker.py'),str(path)],
        stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
    messages=queue.Queue();reader=threading.Thread(target=lambda:messages.put(child.stdout.readline()),daemon=True);reader.start()
    try:
        child.stdin.write(json.dumps({'token':env.client._token})+'\n');child.stdin.flush()
        line=messages.get(timeout=120)
        if line.strip()!='READY:after_'+expected+'_reply':
            if child.poll() is None:child.terminate();child.wait(timeout=10)
            raise AssertionError('Native reply barrier absent: '+line+child.stderr.read())
        child.kill();child.wait(timeout=15)
    finally:
        if child.poll() is None:child.kill();child.wait(timeout=15)
        reader.join(timeout=5)
        for stream in (child.stdin,child.stdout,child.stderr):stream.close()
    fresh,original=recovery.reopen(value,env.client._token)
    admitted=fresh.admit(original,group=g)
    if admitted.state!='completed':raise AssertionError(admitted.issues)
    replay=fresh.issue(admitted.value,transmission=d)
    if replay.state!='partial' or replay.value.token.runtime_permit is not None:raise AssertionError('A reopened intent must not forward again')
    return fresh,replay,value


class RecoveryCases(unittest.TestCase):
    @covers('F12','F13','OP12P','OP13P','OP14P','X04')
    def test_process_death_stop_ack_restart_acceptance_and_load_receipt_stay_separate(self):
        with scratch() as root,case.service(root/'provider',program=recovery.SERVICE) as (client,_):
            env=recovery.Environment(root/'coordinator',client)
            initial=env.context.read.views;original_R=next(v for v in initial if v.package_id==env.request_ref['package_id']).source_bytes
            fresh,_,_=kill_after_reply(env,env.stop_request(),'request_stop')
            self.assertFalse(fresh.observe_stop()['observed_stopped'])
            held=fresh.plan(fresh.restart_request());self.assertEqual(held.state,'rejected',held.issues)
            self.assertEqual(len(client.call('recovery_oracle')['jobs']),1)
            fault('F12','killed_after_stop_ack',fresh,strict_restart_held=True,no_descendant_termination_claim=True)
            client.call('finish_stop',job=fresh.predecessor_job);self.assertTrue(fresh.observe_stop()['observed_stopped'])
            next_env,_,_=kill_after_reply(fresh,fresh.restart_request(),'restart')
            native=client.call('recovery_oracle');self.assertEqual(len(native['jobs']),2);self.assertEqual(native['loads'],[])
            self.assertNotEqual(next_env.predecessor['target'],next_env.successor['target'])
            # Native query of the original command resolves acceptance without
            # launching again; raw state remains unproven until actual load.
            successor=native['jobs'][1];next_env.successor_job=successor['id']
            b=Builder('Reconciled accepted successor, not restored state')
            descriptor,storage=case.typed_document(b,contract('s3.payload.native_descriptor'),client.call('query',command=successor['command'])['matches'][0])
            subject=b.add('native_subject',{'descriptor':descriptor,'origin_attempt':next_env.successor,'scope':scope(next_env.successor),'basis':[descriptor]})
            from crucis_causal.execution.coordinator import root_of
            ar=root_of(next_env.view,codec.Resolver(next_env.context.read.views,limits=case.L))['audience']
            r=b.add('projection_view',{'view_role':'audience_projection','audience':qualified(ar,next_env.view.package_id),
                'projection_contract':contract('s3.fixture.reconciled_successor'),'members':index([subject]),'claims':index(),'limits':index()})
            v=case.frame(b,r,(*next_env.context.read.views,storage));next_env.include(storage,v);next_env.successor_subject=qualified(subject,v.package_id)
            fault('F13','killed_after_restart_acceptance',next_env,accepted=True,loaded='unresolved',jobs='2')
            final,_,_=kill_after_reply(next_env,next_env.restore_request(),'restore')
            observed=client.call('inspect_loaded',job=final.successor_job)
            self.assertEqual(observed['components'],['model','optimizer']);self.assertEqual(observed['rng']['state'],'unresolved');self.assertEqual(observed['history']['state'],'unresolved')
            self.assertEqual(base64.b64decode(observed['bytes']),b'{"model":[2,4],"optimizer":{"step":7}}')
            final_native=client.call('recovery_oracle');self.assertEqual(sum(Decimal(r['charge']) for r in final_native['jobs']),Decimal('9'))
            self.assertEqual(next(v for v in final.context.read.views if v.package_id==final.request_ref['package_id']).source_bytes,original_R)
            fault('F13','killed_after_load_before_local_receipt',final,model_loaded=True,optimizer_loaded=True,rng='unresolved',history='unresolved',total='9',trial_count='1',attempts='2')

    @covers('OP12H','OP13H','OP14H','X04')
    def test_native_handle_expiry_wrong_components_and_unknown_stop_hold_without_new_job(self):
        with scratch() as root,case.service(root/'provider',program=recovery.SERVICE) as (client,_):
            env=recovery.Environment(root/'coordinator',client,source_type='native_reference')
            self.assertEqual(env.plan(env.restart_request()).state,'rejected')
            client.call('finish_stop',job=env.predecessor_job);env.observe_stop()
            bad=replace(env.stop_request(),parameters=tuple({'key':p['key'],'value':known('declared_descendants')} if p['key']=='scope' else p for p in env.stop_request().parameters))
            self.assertEqual(env.plan(bad).state,'rejected')
            client.call('expire_checkpoint',id=env.native_checkpoint['id'])
            failed=env.run(env.restart_request());self.assertNotEqual(failed.state,'completed')
            self.assertEqual(len(client.call('recovery_oracle')['jobs']),1)
            for loaded in (False,True):
                bad=[{**c,'availability':unknown()} for c in env.components]
                with self.assertRaisesRegex(ExecutionError,'required_state_unavailable'):state_components(bad,recovery.REQUIRED,loaded=loaded)
            with self.assertRaisesRegex(ExecutionError,'load_unestablished'):state_components(env.components,recovery.REQUIRED,loaded=True)
            # No supported in-place subject/quiescence proof has been supplied.
            self.assertEqual(env.plan(env.restore_request()).state,'rejected')

    @covers('OP13P','OP14P')
    def test_native_reference_loader_actual_loading_and_wrong_quiescence(self):
        with scratch() as root,case.service(root/'provider',program=recovery.SERVICE) as (client,_):
            env=recovery.Environment(root/'coordinator',client,source_type='native_reference')
            client.call('finish_stop',job=env.predecessor_job);env.observe_stop()
            started=env.run(env.restart_request());self.assertEqual(started.state,'completed',started.issues)
            recoveries=[r['payload'] for r in started.records.records if r['record_type']=='s3.recovery']
            self.assertTrue(all(c['loaded']['state']=='unresolved' for c in recoveries[0]['components']))
            request=env.restore_request();bad=replace(request,parameters=tuple({'key':p['key'],'value':known(contract('s3.unsupported_quiescence'))} if p['key']=='quiescence_rule' else p for p in request.parameters))
            self.assertEqual(env.plan(bad).state,'rejected');self.assertEqual(client.call('recovery_oracle')['loads'],[])
            loaded=env.run(request);self.assertEqual(loaded.state,'completed',loaded.issues)
            components=next(r['payload']['components'] for r in loaded.records.records if r['record_type']=='s3.recovery')
            self.assertEqual({c['component']['name']:c['loaded']['state'] for c in components},
                {'s3.fixture.model':'known','s3.fixture.optimizer':'known','s3.fixture.rng':'unresolved','s3.fixture.history':'unresolved'})
            self.assertEqual(len(client.call('recovery_oracle')['loads']),1)
            self.assertEqual(len(client.call('recovery_oracle')['jobs']),2)

    @covers('F20')
    def test_owner_settlement_and_release_reply_loss_keep_same_request_and_total_nine(self):
        from test_audit_execution_owners import owner_setup,reserve,facts,request
        from crucis_causal.execution.accounting import resource_total
        from crucis_causal.execution.owners import LocalOwner
        with scratch() as root:
            owner,binding,ctx,allocation=owner_setup(root/'owner')
            reserved,ctx,_=reserve(owner,binding,ctx);entries,ctx=facts(owner,binding,ctx)
            self.assertEqual(resource_total(entries).quantity['value']['text'],'9')
            rev=owner.inspect(binding,ctx).value.revision['value']
            req=request(owner,binding,'settle',correlation=reserved.correlation,params={'expected_revision':rev,'aggregation':contract('s3.aggregation.replace_then_disjoint_members')},evidence=api.PinnedInputs(entries[:2],ctx.read.views))
            def lost(label):
                if label=='after_owner_commit':raise OSError('actual settlement commit reply lost')
            self.assertEqual(owner.settle(req,replace(ctx,fault=lost)).state,'rejected')
            fresh=LocalOwner(root/'owner',owner.resources,native_operations=owner.native_operations)
            fctx=api.RuntimeContext(ctx.read,fresh.control(allocation,max_calls='100'))
            settled=fresh.settle(req,fctx);self.assertEqual(settled.state,'completed',settled.issues)
            again=fresh.settle(req,fctx);self.assertEqual(settled.value.receipt,again.value.receipt)
            rel=request(fresh,binding,'release',correlation=reserved.correlation,params={'expected_revision':fresh.inspect(binding,fctx).value.revision['value'],'release_rule':contract('owner_release_capacity_only')})
            self.assertEqual(fresh.release(rel,replace(fctx,fault=lost)).state,'rejected');self.assertEqual(fresh.release(rel,fctx).state,'completed')
            with fresh._db() as db:
                charges=[dict(r) for r in db.execute('SELECT * FROM charges')];requests=str(db.execute('SELECT COUNT(*) FROM requests').fetchone()[0])
            self.assertEqual(charges[0]['quantity'],'5');self.assertLess(int(fresh.remaining_control(allocation)),100)
            for name,value in [('receiver-oracle',{'charges':charges,'request_count':requests}),('history-prefix',{'request':req.request_occurrence,'revision':settled.value.revision}),('recovered-view',{'same_receipt':True,'composed_evidence_total':'9','single_subject_charge':'5','release_not_charge_erasure':True})]:fault_receipt('F20','actual_owner_commit_reply_loss',name,value)

    @covers('OP31P','OP31H')
    def test_close_collection_preserves_obligations_and_does_not_stop_native(self):
        with scratch() as root,case.service(root/'provider',program=recovery.SERVICE) as (client,_):
            env=case.Environment(root/'coordinator',client,scientific_path=None)
            b=Builder('Explicit unresolved collection obligation')
            bounds,store=case.typed_document(b,contract('s3.payload.collection_bounds'),{'max_events':known('10'),'max_bytes':known('1000'),'deadline':not_applicable(),'stopping_rule':contract('s3.fixture.user_close')})
            period=b.add('collection_period',{'scope':scope(qualified(env.account,env.view.package_id)),'bounds':bounds,'predecessors':[],'policy':contract('s3.fixture.user_close')})
            frontier=b.add('frontier',{'local_records':index(),'source_positions':index(extent='unresolved'),'selection_rule':contract('s3.fixture.close_cutoff')})
            obligation=b.add('obligation',{'question':contract('s3.native_termination'),'scope':scope(qualified(env.account,env.view.package_id)),'owner':unknown_ref('component'),'disposition':'unresolved','basis':[],'follow_up':index(extent='unresolved')})
            from crucis_causal.execution.coordinator import root_of
            ar=root_of(env.view,codec.Resolver(env.context.read.views,limits=case.L))['audience']
            r=b.add('projection_view',{'view_role':'audience_projection','audience':qualified(ar,env.view.package_id),'projection_contract':contract('s3.fixture.close_context'),'members':index([period,frontier,obligation]),'claims':index(),'limits':index()})
            v=case.frame(b,r,(*env.context.read.views,store));env.include(store,v)
            h=env.journal.head(env.account,env.jctx).value
            added=env.journal.append(env.account,h.revision,identity(),api.CommitDelta(v.records,(),(*env.context.read.views,v)),env.jctx);self.assertEqual(added.state,'completed',added.issues)
            env.include(*added.records.dependencies,added.value.head.snapshot);ctx=replace(env.jctx,read=env.context.read)
            roles=tuple({'role':'s3.role.'+k,'members':index(refs)} for k,refs in [('period',[qualified(period,v.package_id)]),('frontier',[qualified(frontier,v.package_id)]),('obligations',[qualified(obligation,v.package_id)])])
            p={'stopping_rule':known(contract('s3.fixture.user_close')),'reason':known('s3.user_cutoff'),'expected_journal_revision':known(added.value.head.revision)}
            request=api.OperationRequest(contract('s3.op.close_collection'),roles,tuple({'key':k,'value':val} for k,val in p.items()),identity())
            bad=replace(request,roles=tuple({'role':r['role'],'members':index()} if r['role']=='s3.role.obligations' else r for r in roles))
            self.assertEqual(close_collection(bad,env.account,env.journal,ctx).state,'rejected')
            closed=close_collection(request,env.account,env.journal,ctx);self.assertEqual(closed.state,'completed',closed.issues)
            again=close_collection(request,env.account,env.journal,ctx);self.assertEqual(again.state,'completed',again.issues)
            h=env.journal.head(env.account,ctx).value
            self.assertEqual(len([r for r in h.snapshot.records if r['record_type']=='s3.collection_closure']),1)
            self.assertTrue(any(r['record_type']=='s3.obligation' and r['payload']['disposition']=='unresolved' for r in h.snapshot.records))
            self.assertEqual(client.call('recovery_oracle')['commands'],'0')

    def test_pure_recovery_uses_exact_registered_policy_and_never_calls_services(self):
        from test_audit_execution_wire import fixture
        view,resolver=fixture();ctx=api.PinnedReadContext(tuple(resolver._views.values()),api.supplied_read(resolver._views),None,case.L)
        goal=api.RecoveryGoal('reconcile',scope(),contract('s3.fixture.no_coverage'))
        held=RecoveryPolicies().plan(view,goal,ctx);self.assertEqual(held.state,'partial');self.assertEqual(held.value.operations,())
        def evaluate(view,goal,context):
            issue=api.Issue('s3.possible_predecessor_effects',goal.scope,())
            return api.RecoveryPlan(goal,(),(issue,),held.value.obligations)
        policies=RecoveryPolicies((RecoveryRule(goal.policy,implementation(),supplied_callable(evaluate)),))
        result=policies.plan(view,goal,ctx);self.assertEqual(result.state,'partial');self.assertEqual(result.value.operations,())
        from crucis_causal.execution.coordinator import Coordinator
        self.assertEqual(Coordinator(recovery_policies=policies).recover(view,goal,ctx),result)
        self.assertEqual(policies.plan(view,goal,replace(ctx,access=api.supplied_read(()))).state,'rejected')

    def test_shared_immutable_indexes_preserve_identity_access_limits_and_public_copy_rules(self):
        from test_audit_execution_wire import fixture,record_ref
        view,resolver=fixture();ref=record_ref(view,'component')
        first=codec.Resolver((view,),limits=case.L);second=codec.Resolver((view,),limits=case.L)
        public,_=first.record(ref,view.package_id);old=public['payload']['name'];public['payload']['name']='changed public copy'
        self.assertEqual(second.record(ref,view.package_id)[0]['payload']['name'],old)
        internal,_=first._locate(ref,view.package_id)
        with self.assertRaises(TypeError):internal['payload']['name']='accidental shared mutation'
        with self.assertRaises(ExecutionError):codec.Resolver((replace(view,read_scope=api.supplied_read(())),),limits=case.L)
        with self.assertRaises(ExecutionError):codec.Resolver((view,),limits=replace(case.L,max_records='1'))
        package=view.package;package['package_id']=identity()
        next(r for r in package['records'] if r['id']==ref['target'])['payload']['name']='conflicting identity bytes'
        mutated=codec.parse_snapshot(codec.dumps(package,case.L),case.L)
        with self.assertRaisesRegex(ExecutionError,'record_identity_conflict'):codec.Resolver((view,mutated),limits=case.L)

    def test_negative_native_acceptance_does_not_assert_zero_effects_after_forwarding(self):
        with scratch() as root,case.service(root/'provider') as (client,_):
            env=case.Environment(root/'coordinator',client)
            client.call('rotate_epoch') # Actual receiver fencing, local owner remains current.
            result=env.run(env.launch());self.assertEqual(result.state,'partial',result.issues)
            self.assertEqual(result.effects[0].acceptance,known(False))
            self.assertEqual(result.effects[0].boundary,'may_have_crossed')
            self.assertEqual(client.call('oracle')['jobs'],[])
            self.assertTrue(any(r['record_type']=='s1.artifact_snapshot' for v in result.records.dependencies for r in v.records))

    @covers('OP08H')
    def test_native_information_permission_does_not_waive_visible_S2_followup_condition(self):
        from crucis_causal.execution.authority import DriverBoundary
        from crucis_causal.execution.effects import EffectDriver,EffectMethod
        from crucis_causal.execution.registry import supplied_callable
        selected=contract('s3.op.acquire_information');calls=[]
        with scratch() as root,case.service(root/'provider') as (client,_):
            env=case.Environment(root/'coordinator',client,native_operations=(*case.OPS,selected))
            def prepare(binding,inputs,context):return {}
            def execute(call):calls.append(call);raise AssertionError('scientific followup must hold before forwarding')
            driver=EffectDriver(env.component,env.pin,DriverBoundary(env.journal,env.jctx,((env.owner,env.octx),)),env.component,contract('s3.fixture.http'),
                (EffectMethod(selected,supplied_callable(prepare),supplied_callable(execute),contract('s3.fixture.information_evidence')),))
            driver.install(env.registry)
            resolver=codec.Resolver(env.context.read.views,limits=case.L)
            shown=next(r['members']['members'][0] for r in env.launch_roles if r['role']=='s3.role.presentations')
            presentation,pid=resolver.record(shown,shown['package_id'])
            artifact=qualified(presentation['payload']['payload']['value']['artifact'],pid)
            request_ref=next(r['members']['members'][0] for r in env.launch_roles if r['role']=='s3.role.request')
            native,qpid=resolver.record(request_ref,request_ref['package_id']);policy=qualified(native['payload']['presentation_policy'],qpid)
            query,views=case.document(contract('s3.fixture.query'),{},env.context.read.views);env.include(*views)
            roles=tuple({'role':'s3.role.'+k,'members':index(refs)} for k,refs in [('source',[artifact]),('recipient',[env.component]),('policy',[policy])])
            parameters={'provider':known(contract('s3.fixture.explicit_information_source')),'query':known(query),'expected_response':known(contract('s3.fixture.reply'))}
            req=api.OperationRequest(selected,roles,tuple({'key':k,'value':v} for k,v in parameters.items()),identity())
            before=env.owner.remaining_control(env.allocation)
            out=env.run(req);self.assertEqual(out.state,'rejected',out.issues);self.assertEqual(out.issues[0].code,'s3.scientific_followup_policy_unqualified')
            self.assertEqual(calls,[]);self.assertEqual(env.owner.remaining_control(env.allocation),before);self.assertEqual(client.call('oracle')['jobs'],[])


if __name__=='__main__':unittest.main()
