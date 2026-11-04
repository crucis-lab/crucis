"""B04 exact scientific/native handoff and preservation gates (DLV-08/09)."""
import base64
import copy
import hashlib
from dataclasses import replace
import json
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from test_audit_execution_wire import LIMITS,covers,fixture,implementation
from test_audit_execution_journal import scratch
from test_audit_experiments_handoff import ready
from crucis_causal.execution import api,codec
from crucis_causal.execution.bridge import compile_request,working_s1,freeze_owned,native_identity,s1_return
from crucis_causal.execution.scientific import match_run,require_scientific,require_recovery_intent,RecoveryIntentRegistry
from crucis_causal.execution.imports import import_supplied,read_import,OutputInterpreter
from crucis_causal.execution.journal import resolve_binding
from crucis_causal.execution.model import (Builder,ExecutionError,canonical,contract,digest,identity,index,
    known,not_applicable,qualified,reference,scope,unknown,unknown_ref)
from crucis_causal.experiments.api import ProjectionOccurrence
from crucis_causal.connections.services import RecordBuffer
from crucis_causal.connections.store import PackageStore

def projected():
    d,c,run,n,r,v=ready();occ=ProjectionOccurrence(identity(),identity())
    result=compile_request(run,occ,c)
    if result.state!='completed':raise AssertionError(result.issues)
    return d,c,run,occ,result.value

def refs(projection):
    return qualified(projection.projection.request,projection.request_view.package_id),qualified(projection.projection.attempt,projection.request_view.package_id)

def decoder_fixture():
    from crucis_causal.connections.model import Builder as B1,contract as c1
    from crucis_causal.connections.codec import dumps as s1bytes
    from crucis_causal.connections.evidence import capture_bytes
    b1=B1('Native fixture bytes, not a discovery execution')
    artifact=capture_bytes(b1,b'{"order":["v1","v2","v0"]}',format_contract=c1('json'))
    selection=capture_bytes(b1,b'{"mode":"whole"}',format_contract=c1('json'))
    v1=codec.parse_snapshot(s1bytes(b1.package([artifact,selection])),LIMITS)
    b=Builder('Exact fixture decoder binding')
    selectors=b.add('typed_payload',{'payload_contract':contract('s3.fixture.select_whole'),
        'content':{'artifact':qualified(selection,v1.package_id),'selector':not_applicable()},
        'reference_context':{'package_id':b.package_id,'format':contract('account_package')}})
    operation=b.add('operation_binding',{'operation':contract('s3.op.decode_output'),
        'roles':[{'role':'s3.role.artifacts','members':index([qualified(artifact,v1.package_id)])},
            {'role':'s3.role.mappings','members':index()},{'role':'s3.role.source_outputs','members':index()}],
        'parameters':[{'key':k,'value':known(value)} for k,value in [('decoder',contract('s3.fixture.order_json')),
            ('selectors',selectors),('target_contract',c1('order'))]]})
    audience=b.add('audience',{'purpose':contract('fixture_read'),'recipients':index(),'disclosure_policy':unknown_ref('s1.policy'),'authority':unknown()})
    root=b.add('projection_view',{'view_role':'audience_projection','audience':audience,'projection_contract':contract('fixture_decode'),
        'members':index([operation]),'claims':index(),'limits':index()})
    v=codec.parse_snapshot(codec.dumps(b.package(root,(v1,)),LIMITS),LIMITS)
    resolver=codec.Resolver((v1,v),limits=LIMITS)
    bound=resolve_binding(operation,v.package_id,resolver)
    read=api.PinnedReadContext((v1,v),api.supplied_read([v1.package_id,v.package_id]),None,LIMITS)
    pin=implementation(Path(__file__).read_bytes())
    descriptor=api.ExactDriverDescriptor(b.producer,contract('s3.op.decode_output'),contract('binding'),contract('evidence'),pin,(),None)
    return api.ExactOperationRequest(unknown_ref('effect_command'),bound,bound.inputs,descriptor,v),read

def import_binding(sources,views,occurrence):
    b=Builder('Exact supplied-evidence import binding')
    operation=b.add('operation_binding',{'operation':contract('s3.op.import_evidence'),
        'roles':[{'role':'s3.role.sources','members':index(sources)}],
        'parameters':[{'key':'occurrence','value':known(occurrence)},
            {'key':'reader','value':known(contract('s3.reader.supplied_evidence'))},
            {'key':'prior_import','value':not_applicable()}]})
    audience=b.add('audience',{'purpose':contract('fixture_import'),'recipients':index(),
        'disclosure_policy':unknown_ref('s1.policy'),'authority':unknown()})
    root=b.add('projection_view',{'view_role':'audience_projection','audience':audience,
        'projection_contract':contract('fixture_import_binding'),'members':index([operation]),'claims':index(),'limits':index()})
    view=codec.parse_snapshot(codec.dumps(b.package(root,views),LIMITS),LIMITS)
    resolver=codec.Resolver((*views,view),limits=LIMITS)
    binding=resolve_binding(operation,view.package_id,resolver)
    context=api.PinnedReadContext((*views,view),api.supplied_read(v.package_id for v in (*views,view)),None,LIMITS)
    return api.ExactOperationRequest(unknown_ref('effect_command'),binding,binding.inputs,None,view),context

class BridgeCases(unittest.TestCase):
    @covers('OP27P','OP27H')
    def test_OP27_exact_typed_backend_holds_missingness_before_any_import_write(self):
        _,resolver=fixture()
        view=next(v for v in resolver._views.values() if v.format['name']=='s1.connection_package')
        artifact=next(reference(r['id'],'s1.artifact_snapshot',view.package_id) for r in view.records if r['record_type']=='s1.artifact_snapshot')
        request,context=import_binding([artifact],resolver.closure(view.package_id),identity())
        with scratch() as root:
            store=PackageStore(root)
            wrong=replace(request,inputs=api.PinnedInputs((),request.inputs.source_views))
            self.assertEqual(read_import(wrong,context,store).state,'rejected')
            self.assertFalse(list((root/'imports').glob('*.json')))
            first=read_import(request,context,store);self.assertEqual(first.state,'completed',first.issues)
            again=read_import(request,context,store)
            self.assertEqual(first.value.receipt,again.value.receipt)
            self.assertEqual(len(list((root/'imports').glob('*.json'))),1)
            self.assertEqual(read_import(request,replace(context,access=api.supplied_read(())),store).state,'rejected')
            another,other_context=import_binding([artifact],resolver.closure(view.package_id),identity())
            class LostReply:
                def import_once(self,key,binding,create):
                    store.import_once(key,binding,create)
                    raise OSError('injected lost reply after actual import commit')
            lost=read_import(another,other_context,LostReply())
            self.assertEqual(lost.issues[0].code,'s3.import_commit_unconfirmed')
            recovered=read_import(another,other_context,PackageStore(root))
            self.assertEqual(recovered.state,'completed',recovered.issues)
            self.assertEqual(len(list((root/'imports').glob('*.json'))),2)

    @covers('OP30P','OP30H')
    def test_new_checkpoint_revision_explicitly_permits_narrow_mode_without_claiming_loading(self):
        root=ROOT/'tests/audit_fixtures/sc3_recovery_r2';manifest=json.loads((root/'manifest.json').read_bytes())
        for item in manifest['files']:self.assertEqual(hashlib.sha256((root/item['path']).read_bytes()).hexdigest(),item['sha256'])
        views=tuple(codec.parse_snapshot((root/item['path']).read_bytes(),LIMITS) for item in manifest['files'])
        resolver=codec.Resolver(views,limits=LIMITS)
        match=match_run(manifest['run_binding'],manifest['request'],manifest['attempt'],manifest['handoff'],resolver)
        self.assertEqual(manifest['native_calls'],'0');self.assertEqual(manifest['expected']['total'],'9')
        with self.assertRaisesRegex(ExecutionError,'mode_uninterpreted'):require_recovery_intent(match,resolver,manifest['mode'])
        rules=RecoveryIntentRegistry()
        def partial_mode(settings):
            return settings['loaded']['state']=='unresolved' and settings['history']['state']=='unresolved' and settings['independence']['state']=='not_applicable'
        rules.register(manifest['mode'],contract('s3.fixture.checkpoint_restart'),partial_mode,implementation(Path(__file__).read_bytes()))
        record,_=require_recovery_intent(match,resolver,manifest['mode'],policies=rules)
        values={p['key']:p['value'] for p in record['payload']['bindings']}
        self.assertEqual(values['loaded']['state'],'unresolved');self.assertEqual(values['history']['state'],'unresolved')
        self.assertEqual(manifest['prior_fixture']['trial_count'],'1')

    @covers('OP30P')
    def test_OP30_actual_S2_compiler_freezes_R_and_replay_reuses_exact_R_and_handoff(self):
        d,c,run,occ,p=projected();old=p.request_view.source_bytes
        again=compile_request(run,occ,c)
        self.assertEqual(again.state,'completed',again.issues)
        self.assertEqual(again.value.request_view.source_bytes,old)
        self.assertEqual(again.value.handoff,p.handoff)
        stable=copy.deepcopy(p.projection.request)
        again.value.projection.request['target']=identity()
        self.assertEqual(compile_request(run,occ,c).value.projection.request,stable)
        self.assertEqual(len([r for r in d.records.snapshot().records if r['record_type']=='s2.request_binding_receipt']),1)
        resolver=codec.Resolver(p.dependencies,limits=LIMITS)
        request,attempt=refs(p);matched=match_run(run,request,attempt,p.handoff,resolver)
        self.assertEqual(matched.run,run)
        # Actual observation O is a new frozen identity; copied R stays exact.
        c.s1_records.gap([p.projection.attempt],'s1.fixture_observation_missing')
        from crucis_causal.experiments.handoff import freeze_s1
        observed=freeze_s1(c.s1_records.builder.package([p.projection.request]),d.read.limits)
        self.assertNotEqual(observed.package_id,p.request_view.package_id)
        for record in p.request_view.records:
            self.assertEqual(next(r for r in observed.records if r['id']==record['id']),record)
        self.assertEqual(p.request_view.source_bytes,old)

    @covers('OP30H')
    def test_OP30_changed_occurrence_or_request_holds_without_new_native_or_scientific_record(self):
        d,c,run,occ,p=projected()
        before=len(d.records.snapshot().records)
        request=p.projection.request
        c.s1_records.builder._records[request['target']]['payload']['route']='s1.direct'
        out=compile_request(run,occ,c)
        self.assertEqual(out.state,'rejected')
        self.assertEqual(len(d.records.snapshot().records),before)
        self.assertEqual(compile_request({**run,'target_type':'s2.trial_slot'},ProjectionOccurrence(identity(),identity()),c).state,'rejected')

    @covers('OP30P','OP30H')
    def test_scientific_match_requires_exact_run_and_NA_never_authorizes_checkpoint_restart(self):
        _,_,run,_,p=projected();resolver=codec.Resolver(p.dependencies,limits=LIMITS)
        request,attempt=refs(p);matched=match_run(run,request,attempt,p.handoff,resolver)
        self.assertIs(require_scientific(purpose='scientific_run',visible_scientific_intent=True,matches=(matched,)),matched)
        with self.assertRaises(ExecutionError):require_scientific(purpose='preparation_probe',visible_scientific_intent=True,matches=(),na_rule=contract('s3.fixed_nonscientific_probe'),fixed_before_effect=True)
        with self.assertRaises(ExecutionError):require_scientific(purpose='preparation_probe',visible_scientific_intent=False,matches=(),fixed_before_effect=False)
        self.assertIsNone(require_scientific(purpose='historical_observation',visible_scientific_intent=False,matches=()))
        with self.assertRaisesRegex(ExecutionError,'recovery_policy_unestablished'):require_recovery_intent(matched,resolver,contract('fixture_restore'))
        with self.assertRaises(ExecutionError):match_run(run,request,{**attempt,'target':identity()},p.handoff,resolver)

    @covers('OP30P','OP30H')
    def test_working_scope_preserves_all_records_and_detects_subsequent_changes(self):
        _,_,_,_,p=projected();resolver=codec.Resolver(p.dependencies,limits=LIMITS)
        request,attempt=refs(p);buffer=RecordBuffer();working=working_s1(request,attempt,resolver,buffer)
        for record in p.request_view.records:self.assertEqual(buffer.get(reference(record['id'],record['record_type'])),record)
        buffer.builder._records[request['target']]['payload']['route']='s1.direct'
        with self.assertRaisesRegex(ExecutionError,'working_s1_record_changed'):working.verify()
        with self.assertRaises(ExecutionError):working_s1(request,attempt,resolver,buffer)
        with self.assertRaises(ExecutionError):working_s1(p.projection.request,attempt,resolver,RecordBuffer())

    @covers('OP27P','OP27H')
    def test_OP27_actual_store_replay_preserves_unknown_origin_and_changed_key_conflicts(self):
        _,resolver=fixture()
        view=next(v for v in resolver._views.values() if v.format['name']=='s1.connection_package')
        artifacts=[reference(r['id'],'s1.artifact_snapshot',view.package_id) for r in view.records if r['record_type']=='s1.artifact_snapshot']
        with scratch() as root:
            store=PackageStore(root);occ=identity()
            imported=import_supplied(occ,artifacts[:1],resolver,store)
            replay=import_supplied(occ,artifacts[:1],resolver,PackageStore(root))
            self.assertEqual(imported.snapshot.source_bytes,replay.snapshot.source_bytes)
            self.assertEqual(imported.native_occurrence['state'],'unresolved')
            self.assertFalse(any(r['record_type'] in ('s1.request','s1.attempt') for r in imported.snapshot.records))
            with self.assertRaises(ExecutionError):import_supplied(occ,artifacts[1:2] or [],resolver,store)
            another=import_supplied(identity(),artifacts[:1],resolver,store)
            self.assertNotEqual(another.receipt,imported.receipt)
            self.assertEqual(len(list((root/'imports').glob('*.json'))),2)

    @covers('OP28P','OP28H')
    def test_OP28_actual_pure_reader_preserves_native_order_and_failed_decode_retains_bytes(self):
        request,context=decoder_fixture();calls=[]
        def selector(value):
            if value!={'mode':'whole'}:raise ExecutionError('s3.fixture_selector')
            return value
        def reader(inputs,selectors,target,context):
            from crucis_causal.connections.validation import content_bytes
            from crucis_causal.connections.model import Builder as B1,source
            from crucis_causal.connections.codec import dumps as s1bytes
            from crucis_causal.connections.domains import finite_domain,member
            from crucis_causal.connections.services import RecordBuffer
            from crucis_causal.connections.evidence import capture_bytes
            calls.append('pure_read')
            entry=inputs.entries[0];native=json.loads(content_bytes(entry.record['payload']['content']))['order']
            self.assertEqual(native,['v1','v2','v0'])
            from crucis_causal.connections.model import contract as c1,scope as scope1
            b=B1('Explicit fixture order interpreter');domain=finite_domain(b,['v0','v1','v2'])
            coordinates={'v0':'0','v1':'1','v2':'2'}
            out=b.output('order',{'predicate':c1('causal_precedence'),'domain':domain,'representation':'sequence',
                'sequence':[member(domain,coordinates[k]) for k in native],'pairs':[],'coverage':scope1(domain),
                'omission':'s1.unreported'},evidence=[qualified(entry.reference,entry.source_package)])
            b._records[out['target']]['payload']['source']=source('derived',[qualified(entry.reference,entry.source_package)],b.producer)
            dependencies=[{'package_id':v.package_id,'locator':unknown(),'expected_digest':known(v.digest),'access':'s1.supplied_metadata'} for v in inputs.source_views if v.format['name']=='s1.connection_package']
            frozen=codec.parse_snapshot(s1bytes(b.package([out],external_packages=dependencies)),LIMITS)
            delta=api.RecordDelta(dependencies=(*inputs.source_views,frozen))
            return api.DriverEvidence(reference(request.binding.record['id'],'operation_binding',request.source_view.package_id),delta,index([qualified(out,frozen.package_id)]),index(),index(),())
        target=next(v['value']['value'] for v in request.binding.record['payload']['parameters'] if v['key']=='target_contract')
        interpreter=OutputInterpreter(contract('s3.fixture.order_json'),target,contract('s3.fixture.select_whole'),selector,reader,request.descriptor.implementation)
        out=interpreter.decode(request,context)
        self.assertEqual(out.state,'completed',out.issues);self.assertEqual(calls,['pure_read'])
        derived=next(r for v in out.records.dependencies for r in v.records if r['record_type']=='s1.output')
        self.assertEqual([m['key'] for m in derived['payload']['body']['sequence']],['1','2','0'])
        wrong=replace(request,inputs=api.PinnedInputs((),request.inputs.source_views))
        held=interpreter.decode(wrong,context)
        self.assertEqual(held.state,'rejected');self.assertEqual(calls,['pure_read'])
        self.assertEqual(held.records.dependencies,context.views)
        self.assertEqual(interpreter.decode(request,replace(context,access=api.supplied_read(()))).state,'rejected')
        def broken(inputs,selectors,target,context):raise ValueError('fixture native bytes uninterpretable')
        rejected=OutputInterpreter(contract('s3.fixture.order_json'),target,contract('s3.fixture.select_whole'),selector,broken,request.descriptor.implementation).decode(request,context)
        self.assertEqual(rejected.state,'rejected');self.assertEqual(rejected.records.dependencies,context.views)

    @covers('OP30P','OP30H')
    def test_owned_deltas_require_exact_frozen_namespace_and_content(self):
        _,_,_,_,projection=projected();native=projection.request_view
        request,attempt=refs(projection)
        working=working_s1(request,attempt,codec.Resolver(projection.dependencies,limits=LIMITS),RecordBuffer())
        owned=api.OwnedS1Delta(working,native.records,scope())
        with self.assertRaises(ExecutionError):freeze_owned(api.RecordDelta(native_additions=(owned,)))
        dependencies=tuple(v for v in projection.dependencies if v.package_id!=native.package_id)
        delta=freeze_owned(api.RecordDelta(native_additions=(owned,),dependencies=dependencies),native_snapshots=(native,))
        self.assertIn(native.source_bytes,[v.source_bytes for v in delta.dependencies])
        changed=copy.deepcopy(native.records[0]);changed['payload']['name']='changed'
        with self.assertRaises(ExecutionError):freeze_owned(api.RecordDelta(native_additions=(replace(owned,value=(changed,)),)),native_snapshots=(native,))
        with self.assertRaises(ExecutionError):freeze_owned(api.RecordDelta(native_additions=(replace(owned,context=None),)),native_snapshots=(native,))
        with self.assertRaises(ExecutionError):freeze_owned(api.RecordDelta(records=native.records))

    @covers('OP27P','OP27H')
    def test_incarnation_bridge_raw_coordinates_and_rejected_S1_return_remain_honest(self):
        raw={'authority':'fixture-owner','namespace':'jobs','native_id':'7','incarnation':known('generation-α'),
            'identity_rule':contract('fixture_incarnation'),'validity':unknown_ref('typed_payload'),'basis':[]}
        # Descriptor validity is a required ref; this pure encoding does not resolve it or establish rights.
        raw['validity']=reference(identity(),'typed_payload')
        bridged=native_identity(raw,mode='incarnation_key',driver_bridge_aware=True)
        encoded=bridged['s1_identity']['native_id'].removeprefix('s3-incarnation-key-v1:')
        self.assertEqual(json.loads(base64.b64decode(encoded)),['fixture-owner','jobs','7','generation-α'])
        self.assertEqual(bridged['raw_descriptor'],raw)
        with self.assertRaises(ExecutionError):native_identity({**raw,'incarnation':unknown()},mode='incarnation_key',driver_bridge_aware=True)
        with self.assertRaises(ExecutionError):native_identity(raw,mode='literal_unique')
        self.assertEqual(native_identity(raw,mode='literal_unique',literal_unique=True)['s1_identity']['native_id'],'7')
        from crucis_causal.connections.api import Op
        result=s1_return(Op('rejected',diagnostics=(reference(identity(),'s1.gap'),)),reference(identity(),'effect_command'),{'occurrence':identity()},entered=True)
        self.assertEqual(result.effects[0].boundary,'may_have_crossed')

if __name__=='__main__':unittest.main()
