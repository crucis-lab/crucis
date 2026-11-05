"""B05 input custody and guarded realization (DLV-08/09)."""
import copy
from dataclasses import asdict,replace
import json
from pathlib import Path
import pickle
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from test_audit_execution_wire import LIMITS,covers
from test_audit_execution_journal import scratch
from crucis_causal.execution import api,codec
from crucis_causal.execution.model import ExecutionError,contract,digest,identity,known,reference,unknown
from crucis_causal.execution.registry import (supplied_callable,invocation_route,ExactDriverRegistry,
    ExactDecisionRegistry,PayloadRegistry,SuppliedRegistryContext)
from crucis_causal.execution.staging import InputMember,LocalCustodian,EndpointOwner,RuntimeSecrets,restricted_diagnostic
sys.path.insert(0,str(ROOT/'tests/audit_fixtures/sc3_runtime'))
import input_case as case
from crucis_causal.execution.inputs import InputDriver,Realizer
from crucis_causal.execution.model import qualified,index,scope,not_applicable

def member(name='s3.member.data',raw=b'A,B\n0,1\n'):
    return InputMember(name,reference(identity(),'s1.artifact_snapshot',identity()),raw,digest(raw),{'name':'s1.csv','version':'0.1.0-proposal.1'})

class InputCustodyCases(unittest.TestCase):
    @covers('X01','OP01H')
    def test_unknown_fitting_is_not_zero_and_provider_cannot_change_declared_reference_rule(self):
        from crucis_causal.experiments.api import PlanAssessmentContext
        from crucis_causal.connections.validation import content_bytes
        for variant in ['unknown_fit','changed_rule']:
            with self.subTest(variant=variant),scratch() as root:
                _,data,mapping,spec,requirement,draft,views=case.metadata();count=[]
                implementation=case.pin();component,actor_view=case.actor(implementation)
                original=case.provider(spec,requirement,mapping,views,count,implementation=implementation)
                def observed(inputs):
                    product=original(inputs)
                    if variant=='unknown_fit':return replace(product,fitted_inputs=unknown('s3.native_fitting_scope_unreported'))
                    alternate={'name':'s2.fixture.changed_reference_policy','version':'0.1.0-proposal.1'}
                    inputs.specification['payload']['reference_rule']=alternate
                    return replace(product,reference_rule=alternate)
                selected=Realizer(contract('s3.fixture.csv_permutation'),{'name':'s2.fixture.fixed_permutation','version':'0.1.0-proposal.1'},implementation,supplied_callable(observed))
                initial,account,binding,command,transmission=case.skeleton(component,(*views,actor_view,implementation.source_view),
                    operation='s3.op.realize_input',roles=[{'role':'s3.role.specification','members':index([spec])},
                        {'role':'s3.role.sources','members':index([data])},{'role':'s3.role.provider','members':index([component])}],
                    parameters={'procedure':known(contract('s3.fixture.csv_permutation')),'randomness':known([]),
                        'fitted_state':not_applicable(),'source_window':not_applicable()})
                def factory(boundary):return InputDriver(component,implementation,boundary,realizers=(selected,),scientific_context=PlanAssessmentContext(draft.read,draft,None))
                driver,request,context,grants,token,*_=case.manual_admission(root,(*views,actor_view,implementation.source_view,initial),account,binding,command,transmission,factory)
                out=driver.realize(request,context,grants,token,None)
                self.assertEqual(out.state,'partial' if variant=='unknown_fit' else 'rejected',out.issues)
                self.assertEqual(out.effects[0].boundary,'crossed');self.assertEqual(count,['actual_provider_entry'])
                self.assertTrue(any(r['record_type']=='s1.artifact_snapshot' and content_bytes(r['payload']['content'])==case.EXPECTED for v in out.records.dependencies for r in v.records if r['record_type']=='s1.artifact_snapshot'))
                if variant=='unknown_fit':
                    fit=[p['value'] for v in out.records.dependencies for r in v.records if r['record_type']=='s2.parameter_set' and r['payload']['schema']['name']=='s2.params.transform' for p in r['payload']['bindings'] if p['key']=='fitted_inputs']
                    self.assertTrue(fit);self.assertTrue(all(value['state']=='unresolved' for value in fit))
                else:self.assertEqual(out.issues[0].code,'s3.realization_reference_rule_mismatch')

    @covers('OP02P','OP02H')
    def test_endpoint_reference_stages_without_materializing_answers_or_restoring_grants_from_metadata(self):
        implementation=case.pin();component,actor_view=case.actor(implementation);count=[]
        views,account,binding,command,transmission,owner,source_grant=case.endpoint_metadata(component,(actor_view,implementation.source_view),implementation,count)
        with scratch() as root:
            def factory(boundary):return InputDriver(component,implementation,boundary,endpoints=((owner,source_grant),))
            driver,request,context,grants,token,*_=case.manual_admission(root,views,account,binding,command,transmission,factory)
            prepared=driver.prepare(request.binding,request.inputs,context.read)
            self.assertEqual(prepared.state,'completed',prepared.issues);self.assertEqual(count,[])
            registry=SuppliedRegistryContext(ExactDriverRegistry(),ExactDecisionRegistry(),PayloadRegistry())
            driver.install(registry)
            receiver,channel=invocation_route(prepared.value.invocation,request.descriptor.input_contract,registry.payloads)
            self.assertEqual(receiver,owner.component);self.assertEqual(channel,contract('s3.trusted_local_call'))
            actual=driver.endpoints;driver.endpoints=((owner,object.__new__(api.OpaqueGrant)),)
            held=driver.stage(request,context,grants,token,None)
            self.assertEqual(held.state,'rejected');self.assertEqual(held.effects[0].boundary,'not_crossed')
            driver.endpoints=actual
            out=driver.stage(request,context,grants,token,None)
            self.assertEqual(out.state,'completed',out.issues);self.assertEqual(count,[])
            proxy=out.value.live_handles[0]
            self.assertEqual(owner.query(proxy,b'question'),b'bounded-answer:question')
            self.assertEqual(count,['actual_endpoint_query']);self.assertEqual(owner.consumed,1)
            with self.assertRaises(ExecutionError):owner.query(proxy,b'question')
            self.assertEqual(count,['actual_endpoint_query']);self.assertEqual(len(owner.events()),1)
            self.assertEqual(owner.events()[0]['outcome'],'returned')
            self.assertEqual(driver.prepare(request.binding,request.inputs,context.read).state,'rejected')
            with self.assertRaises(AttributeError):owner.consumed=0
            owner.revoke(source_grant)
            with self.assertRaises(ExecutionError):owner.query(proxy,b'question')
            self.assertEqual(owner.consumed,1)

    @covers('X01','OP01P','OP01H')
    def test_actual_fitting_uses_declared_calibration_and_missing_subset_does_not_default_to_target(self):
        implementation=case.pin();component,actor_view=case.actor(implementation);count=[]
        spec,calibration,data,draft,views,selected=case.fitted_case(implementation,count)
        from crucis_causal.experiments.api import PlanAssessmentContext
        for supplied,permitted in [([data],False),([calibration,data],True)]:
            with self.subTest(permitted=permitted),scratch() as root:
                initial,account,binding,command,transmission=case.skeleton(component,(*views,actor_view,implementation.source_view),
                    operation='s3.op.realize_input',roles=[{'role':'s3.role.specification','members':index([spec])},
                        {'role':'s3.role.sources','members':index(supplied)},{'role':'s3.role.provider','members':index([component])}],
                    parameters={'procedure':known(contract('s3.fixture.fit_and_permute')),'randomness':known([]),
                        'fitted_state':not_applicable(),'source_window':not_applicable()})
                def factory(boundary):return InputDriver(component,implementation,boundary,realizers=(selected,),scientific_context=PlanAssessmentContext(draft.read,draft,None))
                driver,request,context,grants,token,*_=case.manual_admission(root,(*views,actor_view,implementation.source_view,initial),account,binding,command,transmission,factory)
                prepared=driver.prepare(request.binding,request.inputs,context.read)
                self.assertEqual(prepared.state,'completed' if permitted else 'rejected',prepared.issues)
                self.assertEqual(count,[])
                out=driver.realize(request,context,grants,token,None)
                if not permitted:
                    self.assertEqual(out.state,'rejected');self.assertEqual(out.effects[0].boundary,'not_crossed');self.assertEqual(count,[])
                else:
                    self.assertEqual(out.state,'completed',out.issues);self.assertEqual(count,['actual_fitting_entry'])
                    from crucis_causal.connections.validation import content_bytes
                    resolver=codec.Resolver(out.records.dependencies,limits=LIMITS)
                    refs=out.value.subjects['members'];products=[resolver.record(r,r['package_id'])[0] for r in refs]
                    self.assertEqual(content_bytes(products[0]['payload']['content']),case.FIT_EXPECTED)
                    fitted=json.loads(content_bytes(products[1]['payload']['content']))
                    self.assertEqual(fitted,{'centering_mean':'1','fitted_sources':[calibration]})
                    parameters=[r for v in out.records.dependencies for r in v.records if r['record_type']=='s2.parameter_set' and r['payload']['schema']['name']=='s2.params.transform']
                    self.assertTrue(any(p['value'].get('value')==[calibration] for r in parameters for p in r['payload']['bindings'] if p['key']=='fitted_inputs'))

    @covers('OP02P','OP02H')
    def test_guarded_stage_only_exposes_selected_archive_members_and_spends_permit_once(self):
        implementation=case.pin();component,actor_view=case.actor(implementation)
        with scratch() as root:
            custodian=LocalCustodian(root/'custody',max_stages='1');cap=custodian.control()
            views,account,binding,command,transmission=case.staging_metadata(component,(actor_view,implementation.source_view),namespace=custodian.namespace)
            def factory(boundary):return InputDriver(component,implementation,boundary,custodian=custodian,custody_control=cap)
            driver,request,context,grants,token,*_=case.manual_admission(root,views,account,binding,command,transmission,factory)
            prepared=driver.prepare(request.binding,request.inputs,context.read)
            self.assertEqual(prepared.state,'completed',prepared.issues)
            registry=SuppliedRegistryContext(ExactDriverRegistry(),ExactDecisionRegistry(),PayloadRegistry());driver.install(registry)
            self.assertEqual(invocation_route(prepared.value.invocation,request.descriptor.input_contract,registry.payloads),(component,contract('s3.trusted_local_call')))
            with self.assertRaises(ExecutionError):custodian.inspect(command['target'],cap)
            held=driver.stage(request,context,(),token,None)
            self.assertEqual(held.state,'rejected');self.assertEqual(held.effects[0].boundary,'not_crossed')
            altered=replace(request,descriptor=replace(request.descriptor,guarantees=({'unsupported':'s3.host_isolation'},)))
            metadata_only=driver.stage(altered,context,grants,token,None)
            self.assertEqual(metadata_only.state,'rejected');self.assertEqual(metadata_only.effects[0].boundary,'not_crossed')
            wrong_receiver=next(qualified(e.reference,e.source_package) for e in request.inputs.entries if e.role=='s3.role.recipient')
            with self.assertRaisesRegex(ExecutionError,'receiver_mismatch'):
                driver.boundary.enter(request,context,grants,token,request.descriptor,wrong_receiver,contract('s3.trusted_local_call'))
            with self.assertRaisesRegex(ExecutionError,'channel_mismatch'):
                driver.boundary.enter(request,context,grants,token,request.descriptor,component,contract('s3.unimplemented_rpc'))
            other=LocalCustodian(root/'other-custody');other_cap=other.control()
            driver.custodian=other;driver.custody_control=other_cap
            wrong_namespace=driver.stage(request,context,grants,token,None)
            self.assertEqual(wrong_namespace.state,'rejected');self.assertEqual(wrong_namespace.effects[0].boundary,'not_crossed')
            with self.assertRaises(ExecutionError):other.inspect(command['target'],other_cap)
            driver.custodian=custodian;driver.custody_control=cap
            out=driver.stage(request,context,grants,token,None)
            self.assertEqual(out.state,'completed',out.issues)
            handle=out.value.live_handles[0]
            self.assertEqual(custodian.read(handle,'s3.member.data'),case.SOURCE)
            self.assertEqual(custodian.read(handle,'s3.member.mask'),b'1,0,1\n')
            self.assertNotIn(b'evaluator-only',custodian.read(handle,'s3.member.data'))
            exposure=[r['payload'] for r in out.records.records if r['record_type']=='s3.exposure_entry']
            self.assertEqual({r['facet'] for r in exposure},{'transmitted','reachable','policy_consumed'})
            self.assertEqual(custodian.inspect(command['target'],cap).consumed,'1')
            self.assertEqual(driver.stage(request,context,grants,token,None).state,'rejected')
            self.assertEqual(custodian.inspect(command['target'],cap).consumed,'1')

    @covers('OP02H')
    def test_guarded_partial_stage_retains_possible_effect_and_no_coherent_handle(self):
        implementation=case.pin();component,actor_view=case.actor(implementation)
        with scratch() as root:
            custodian=LocalCustodian(root/'custody',max_stages='2');cap=custodian.control()
            views,account,binding,command,transmission=case.staging_metadata(component,(actor_view,implementation.source_view),namespace=custodian.namespace)
            def factory(boundary):return InputDriver(component,implementation,boundary,custodian=custodian,custody_control=cap)
            driver,request,context,grants,token,*_=case.manual_admission(root,views,account,binding,command,transmission,factory)
            def lost(label):
                if label=='after_stage_member_0':raise OSError('lost stage acknowledgement')
            out=driver.stage(request,replace(context,fault=lost),grants,token,None)
            self.assertEqual(out.state,'rejected');self.assertEqual(out.effects[0].boundary,'may_have_crossed',out.issues)
            uncertainty=[r['payload']['extent']['state'] for r in out.records.records if r['record_type']=='s3.exposure_entry']
            self.assertEqual(uncertainty,['unresolved','unresolved','unresolved'])
            observed=custodian.inspect(command['target'],cap)
            self.assertEqual((observed.state,len(observed.members),observed.consumed),('partial',1,'1'))
            with self.assertRaises(ExecutionError):custodian.activate(command['target'],observed.recipient,cap,expected_epoch='0')

    @covers('OP02H')
    def test_unsupported_stability_is_held_by_pure_prepare_and_before_any_transfer(self):
        implementation=case.pin();component,actor_view=case.actor(implementation)
        with scratch() as root:
            custodian=LocalCustodian(root/'custody');cap=custodian.control()
            views,account,binding,command,transmission=case.staging_metadata(component,(actor_view,implementation.source_view),namespace=custodian.namespace,stability='version_checked')
            def factory(boundary):return InputDriver(component,implementation,boundary,custodian=custodian,custody_control=cap)
            driver,request,context,grants,token,*_=case.manual_admission(root,views,account,binding,command,transmission,factory)
            self.assertEqual(driver.prepare(request.binding,request.inputs,context.read).state,'rejected')
            out=driver.stage(request,context,grants,token,None)
            self.assertEqual(out.state,'rejected');self.assertEqual(out.effects[0].boundary,'not_crossed')
            with self.assertRaises(ExecutionError):custodian.inspect(command['target'],cap)

    @covers('X01','OP01P','OP01H')
    def test_realization_uses_actual_owner_and_durable_permit_then_returns_S2_materialization(self):
        source,data,mapping,spec,requirement,draft,views=case.metadata();count=[];implementation=case.pin();component,actor_view=case.actor(implementation)
        with scratch() as root:
            initial,account,binding,command,transmission=case.skeleton(component,(*views,actor_view,implementation.source_view),
                operation='s3.op.realize_input',roles=[{'role':'s3.role.specification','members':index([spec])},
                    {'role':'s3.role.sources','members':index([data])},{'role':'s3.role.provider','members':index([component])}],
                parameters={'procedure':known(contract('s3.fixture.csv_permutation')),'randomness':known([]),
                    'fitted_state':not_applicable(),'source_window':not_applicable()})
            from crucis_causal.experiments.api import PlanAssessmentContext
            selected=Realizer(contract('s3.fixture.csv_permutation'),{'name':'s2.fixture.fixed_permutation','version':'0.1.0-proposal.1'},
                implementation,supplied_callable(case.provider(spec,requirement,mapping,views,count,implementation=implementation)))
            def factory(boundary):return InputDriver(component,implementation,boundary,realizers=(selected,),scientific_context=PlanAssessmentContext(draft.read,draft,None))
            driver,request,context,grants,token,*_=case.manual_admission(root,(*views,actor_view,implementation.source_view,initial),account,binding,command,transmission,factory)
            self.assertEqual(count,[])
            before=len(draft.records.snapshot().records)
            prepared=driver.prepare(request.binding,request.inputs,context.read)
            self.assertEqual(prepared.state,'completed',prepared.issues);self.assertEqual(count,[])
            self.assertEqual(len(draft.records.snapshot().records),before)
            missing=driver.realize(request,context,(),token,None)
            self.assertEqual(missing.state,'rejected');self.assertEqual(missing.effects[0].boundary,'not_crossed');self.assertEqual(count,[])
            out=driver.realize(request,context,grants,token,None)
            self.assertEqual(out.state,'completed',out.issues);self.assertEqual(count,['actual_provider_entry'])
            from crucis_causal.connections.validation import content_bytes
            resolver=codec.Resolver(out.records.dependencies,limits=LIMITS)
            result_ref=out.value.subjects['members'][0];artifact,_=resolver.record(result_ref,result_ref['package_id'])
            self.assertEqual(content_bytes(artifact['payload']['content']),case.EXPECTED)
            receipt_ref=out.value.receipts['members'][0];receipt,_=resolver.record(receipt_ref,receipt_ref['package_id'])
            self.assertEqual(receipt['record_type'],'s2.materialization_receipt');self.assertFalse(receipt['payload']['gaps'])
            self.assertTrue(receipt['payload']['checks'])
            again=driver.realize(request,context,grants,token,None)
            self.assertEqual(again.state,'rejected');self.assertEqual(count,['actual_provider_entry'])
            self.assertFalse(any(r['record_type'] in ('s1.request','s1.attempt','s2.run_binding') for r in draft.records.snapshot().records))

    @covers('OP01H','X01')
    def test_failed_preservation_is_partial_materialization_not_repaired_or_redrawn(self):
        source,data,mapping,spec,requirement,draft,views=case.metadata();count=[];implementation=case.pin();component,actor_view=case.actor(implementation)
        initial,account,binding,command,transmission=case.skeleton(component,(*views,actor_view,implementation.source_view),
            operation='s3.op.realize_input',roles=[{'role':'s3.role.specification','members':index([spec])},
                {'role':'s3.role.sources','members':index([data])},{'role':'s3.role.provider','members':index([component])}],
            parameters={'procedure':known(contract('s3.fixture.csv_permutation')),'randomness':known([]),
                'fitted_state':not_applicable(),'source_window':not_applicable()})
        from crucis_causal.experiments.api import PlanAssessmentContext
        selected=Realizer(contract('s3.fixture.csv_permutation'),{'name':'s2.fixture.fixed_permutation','version':'0.1.0-proposal.1'},implementation,
            supplied_callable(case.provider(spec,requirement,mapping,views,count,implementation=implementation,bad=True)))
        with scratch() as root:
            def factory(boundary):return InputDriver(component,implementation,boundary,realizers=(selected,),scientific_context=PlanAssessmentContext(draft.read,draft,None))
            driver,request,context,grants,token,*_=case.manual_admission(root,(*views,actor_view,implementation.source_view,initial),account,binding,command,transmission,factory)
            out=driver.realize(request,context,grants,token,None)
            self.assertEqual(out.state,'partial',out.issues);self.assertEqual(count,['actual_provider_entry'])
            self.assertIn('s2.preservation_check_not_passed',[i.code for i in out.issues])
            from crucis_causal.connections.validation import content_bytes
            resolver=codec.Resolver(out.records.dependencies,limits=LIMITS);ref=out.value.subjects['members'][0]
            record,_=resolver.record(ref,ref['package_id']);self.assertIn(b'different',content_bytes(record['payload']['content']))

    def test_coherent_interface_activation_preserves_exact_bytes_and_replay_budget(self):
        with scratch() as root:
            custodian=LocalCustodian(root,max_stages='1');control=custodian.control();epoch=custodian.epoch(control)
            recipient=reference(identity(),'s1.component',identity());key=identity()
            members=(member(),member('s3.member.mask',b'1,0\n'))
            receipt=custodian.transfer(key,digest(b'exact-binding'),recipient,members,control,expected_epoch=epoch)
            self.assertEqual(receipt.state,'complete');self.assertIsNone(receipt.handle)
            active=custodian.activate(key,recipient,control,expected_epoch=epoch)
            self.assertEqual(custodian.read(active.handle,'s3.member.data'),b'A,B\n0,1\n')
            self.assertEqual(custodian.read(active.handle,'s3.member.mask'),b'1,0\n')
            self.assertEqual(custodian.transfer(key,digest(b'exact-binding'),recipient,members,control,expected_epoch=epoch).remaining,'0')
            with self.assertRaisesRegex(ExecutionError,'correlation_conflict'):
                custodian.transfer(key,digest(b'changed-binding'),recipient,members,control,expected_epoch=epoch)
            with self.assertRaisesRegex(ExecutionError,'allowance_exhausted'):
                custodian.transfer(identity(),digest(b'exact-binding'),recipient,members,control,expected_epoch=epoch)
            with self.assertRaises(ExecutionError):custodian.read(object.__new__(api.OpaqueHandle),'s3.member.data')

    def test_partial_transfer_reopening_keeps_allowance_and_cannot_activate_or_implicitly_resume(self):
        with scratch() as root:
            custodian=LocalCustodian(root,max_stages='2');control=custodian.control();key=identity()
            recipient=reference(identity(),'s1.component',identity());members=(member(),member('s3.member.mask',b'1,0\n'))
            def interrupted(label):
                if label=='after_stage_member_0':raise OSError('injected lost transfer acknowledgement')
            with self.assertRaises(OSError):custodian.transfer(key,digest(b'exact-binding'),recipient,members,control,expected_epoch='0',fault=interrupted)
            fresh=LocalCustodian(root,max_stages='2');fresh_control=fresh.control()
            partial=fresh.inspect(key,fresh_control)
            self.assertEqual((partial.state,len(partial.members),partial.consumed,partial.remaining),('partial',1,'1','1'))
            replay=fresh.transfer(key,digest(b'exact-binding'),recipient,members,fresh_control,expected_epoch='0')
            self.assertEqual((replay.state,len(replay.members),replay.consumed),('partial',1,'1'))
            with self.assertRaisesRegex(ExecutionError,'coherent_activation_unestablished'):fresh.activate(key,recipient,fresh_control,expected_epoch='0')

    def test_revoke_does_not_erase_past_native_copy_or_restore_exposure_allowance(self):
        with scratch() as root:
            custodian=LocalCustodian(root,max_stages='1');control=custodian.control();key=identity()
            recipient=reference(identity(),'s1.component',identity());item=member()
            custodian.transfer(key,digest(b'exact-binding'),recipient,(item,),control,expected_epoch='0')
            active=custodian.activate(key,recipient,control,expected_epoch='0');native_copy=custodian.read(active.handle,item.name)
            revoked=custodian.revoke(key,control,expected_epoch='0')
            self.assertEqual(revoked['allowance'],'0');self.assertEqual(revoked['local_bytes'],'retained')
            self.assertEqual(native_copy,item.bytes)
            self.assertEqual(custodian.artifacts.read(item.digest),item.bytes)
            with self.assertRaises(ExecutionError):custodian.read(active.handle,item.name)

    def test_takeover_fences_actual_interface_and_old_sender_not_native_memory(self):
        with scratch() as root:
            custodian=LocalCustodian(root);control=custodian.control();key=identity()
            recipient=reference(identity(),'s1.component',identity());item=member()
            custodian.transfer(key,digest(b'exact-binding'),recipient,(item,),control,expected_epoch='0')
            active=custodian.activate(key,recipient,control,expected_epoch='0')
            self.assertEqual(custodian.takeover(control,expected_epoch='0'),'1')
            with self.assertRaises(ExecutionError):custodian.read(active.handle,item.name)
            with self.assertRaises(ExecutionError):custodian.revoke(key,control,expected_epoch='0')
            self.assertEqual(custodian.inspect(key,control).consumed,'1')

    @covers('X12')
    def test_runtime_slots_are_not_serialized_and_redaction_never_claims_original_bytes(self):
        sentinel=b'synthetic-private-'+identity().encode();calls=[]
        def receiver(arguments,values):
            calls.append('authorized_receiver');return values['s3.slot.credential']==sentinel
        allowed=supplied_callable(receiver);secrets=RuntimeSecrets({'s3.slot.credential':sentinel},(allowed,))
        self.assertTrue(secrets.invoke(allowed,('s3.slot.credential',),{}))
        with self.assertRaises(ExecutionError):secrets.invoke(supplied_callable(receiver),('s3.slot.credential',),{})
        with self.assertRaises(TypeError):pickle.dumps(secrets)
        with self.assertRaises(TypeError):copy.deepcopy(secrets)
        with self.assertRaises(TypeError):json.dumps(secrets)
        raw=b'Native diagnostic: credential='+sentinel+b' failed'
        redacted=restricted_diagnostic(raw,secrets)
        self.assertNotIn(sentinel,redacted.bytes)
        self.assertEqual(redacted.relation,'derived_redaction');self.assertEqual(redacted.original['state'],'unresolved')
        self.assertNotEqual(redacted.bytes,raw);self.assertEqual(calls,['authorized_receiver'])
        metadata=json.dumps({k:v for k,v in asdict(redacted).items() if k!='bytes'}).encode()
        self.assertNotIn(sentinel,metadata)

    def test_mutable_alias_and_wrong_digest_never_become_stable_input_member(self):
        value=bytearray(b'checked')
        with self.assertRaises(ExecutionError):member(raw=value)
        with self.assertRaises(ExecutionError):replace(member(),bytes=b'changed-after-planning')

    @covers('OP02H')
    def test_changed_staged_file_holds_activation_without_repinning_or_resetting_consumption(self):
        with scratch() as root:
            custodian=LocalCustodian(root,max_stages='1');control=custodian.control();key=identity()
            recipient=reference(identity(),'s1.component',identity());item=member()
            custodian.transfer(key,digest(b'exact-binding'),recipient,(item,),control,expected_epoch='0')
            target=custodian.artifacts._path(item.digest['value']).resolve()
            self.assertTrue(target.is_relative_to(custodian.artifacts.root));target.write_bytes(b'fault-injected changed bytes')
            with self.assertRaisesRegex(ExecutionError,'artifact_integrity_mismatch'):
                custodian.activate(key,recipient,control,expected_epoch='0')
            observed=custodian.inspect(key,control)
            self.assertEqual(observed.state,'complete');self.assertIsNone(observed.handle)
            self.assertEqual(observed.members[0]['digest'],item.digest)
            self.assertEqual((observed.consumed,observed.remaining),('1','0'))

if __name__=='__main__':unittest.main()
