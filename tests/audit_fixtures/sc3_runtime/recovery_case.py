"""Explicit synthetic partial-continuity bootstrap (DLV-08/09)."""
import base64
from dataclasses import replace
import json
from pathlib import Path
import dispatch_case as case
from crucis_causal.execution import api,codec
from crucis_causal.execution.authority import DriverBoundary
from crucis_causal.execution.coordinator import typed_document,root_of
from crucis_causal.execution.effects import EffectDriver,EffectMethod,capture_reply_problem
from crucis_causal.execution.journal import binding_digest
from crucis_causal.execution.model import (Builder,ExecutionError,canonical,contract,identity,index,
    known,not_applicable,qualified,reference,scope,unknown,unknown_ref)
from crucis_causal.execution.registry import supplied_callable
from crucis_causal.execution.scientific import RecoveryIntentRegistry
from crucis_causal.execution.stopping import require_observed_stop,state_components
from crucis_causal.connections.model import Builder as B1,contract as c1,source as s1source
from crucis_causal.connections.evidence import capture_bytes
from crucis_causal.connections.validation import content_bytes

OPS=tuple(contract(n) for n in ('s3.op.request_stop','s3.op.native_restart','s3.op.restore_state'))
MODE=contract('s3.fixture.restore_model_optimizer')
REQUIRED=[contract('s3.fixture.model'),contract('s3.fixture.optimizer')]
STOP=contract('s3.fixture.observed_component_stop')
SERVICE=Path(__file__).with_name('recovery_service.py')


def partial_mode(settings):
    return settings['loaded']['state']=='unresolved' and settings['history']['state']=='unresolved' and settings['independence']['state']=='not_applicable'


class Mechanics:
    def __init__(self,env):self.env=env
    def prepare(self,binding,inputs,context):
        env=self.env;resolver=codec.Resolver(context.views,limits=context.limits)
        op=binding.record['payload']['operation']['name'];pid=binding.context['package_id']
        p={p['key']:p['value'] for p in binding.record['payload']['parameters']}
        roles={r['role']:r['members']['members'] for r in binding.record['payload']['roles']}
        def one(role):
            refs=roles['s3.role.'+role]
            if len(refs)!=1:raise ExecutionError('s3.fixture_recovery_identity')
            return refs[0]
        if op=='s3.op.request_stop':
            if p['scope']!=known('component') or p['method']!=known(contract('s3.fixture.cooperative_stop')) or p['escalation']['state']!='not_applicable':raise ExecutionError('s3.fixture_stop_scope_unqualified')
            job=env.job(one('subject'),resolver)
            if one('policy')!=env.policy:raise ExecutionError('s3.fixture_recovery_policy')
            return {'job':job,'scope':'component','epoch':env.client.epoch}
        if one('policy')!=env.policy:raise ExecutionError('s3.fixture_recovery_policy')
        if p['required_components']!=known(REQUIRED):raise ExecutionError('s3.fixture_components_unqualified')
        checkpoint,cpid=resolver.record(one('checkpoint'),pid)
        if checkpoint['record_type']!='s1.output' or checkpoint['id']!=env.checkpoint['target']:raise ExecutionError('s3.fixture_checkpoint_identity')
        data=case.content(resolver,env.state_metadata,env.state_metadata['package_id'],contract('s3.fixture.partial_state'))
        state_record,spid=resolver.record(env.state_metadata,env.state_metadata['package_id'])
        context_pid=state_record['payload']['reference_context']['package_id']
        state_components(data['components'],REQUIRED)
        source=data['components'][0]['restore_source']['value']
        args={'checkpoint':env.native_checkpoint['id'],'source_type':source['source_type'],'bytes':None,'epoch':env.client.epoch}
        if source['source_type']=='captured_payload':
            artifact,apid=resolver.record(source['payload']['artifact'],context_pid)
            if source['payload']['selector']['state']!='not_applicable':raise ExecutionError('s3.fixture_whole_checkpoint_required')
            args['bytes']=base64.b64encode(content_bytes(artifact['payload']['content'])).decode()
        else:
            locator_record,lpid=resolver.record(source['reference'],context_pid)
            locator=case.content(resolver,source['reference'],context_pid,contract('s3.payload.native_state_locator'))
            if locator['owner']!=env.component or locator['loader_contract']!=contract('s3.fixture.partial_loader') or locator['identity']['native_id']!=env.native_checkpoint['id'] or locator['identity']['namespace']!=env.client.namespace:
                raise ExecutionError('s3.fixture_state_loader_mismatch')
            validity=case.content(resolver,locator['validity'],locator_record['payload']['reference_context']['package_id'],contract('s3.fixture.state_validity'))
            if validity!={'epoch':env.client.epoch,'available':True}:raise ExecutionError('s3.fixture_state_unavailable')
        if op=='s3.op.native_restart':
            if p['overlap_rule']!=known(contract('s3.fixture.strict_nonoverlap')):raise ExecutionError('s3.fixture_overlap_unqualified')
            if env.stop_assessment is None:raise ExecutionError('s3.observed_stop_unestablished')
            require_observed_stop(env.stop_assessment,one('predecessor'),resolver,procedure=STOP,question=STOP)
            args['predecessor']=env.predecessor_job
            supplied=case.content(resolver,p['invocation']['value'],pid,contract('s3.fixture.restart_arguments'))
            if supplied!={'drop_reply':False}:raise ExecutionError('s3.fixture_restart_arguments')
        else:
            if p['quiescence_rule']!=known(contract('s3.fixture.quiescent_before_load')):raise ExecutionError('s3.fixture_quiescence_unqualified')
            args['job']=env.job(one('subject'),resolver)
        return args

    def execute(self,call):
        env=self.env;op=call.request.binding.record['payload']['operation']['name']
        method={'s3.op.request_stop':'request_stop','s3.op.native_restart':'restart','s3.op.restore_state':'restore'}[op]
        args={**call.invocation,'command':call.request.command['target'],'transmission':call.transmission['target']}
        try:raw,data=env.client.raw(method,**args)
        except case.ReplyError as exc:return capture_reply_problem(call,exc.raw,exc.code)
        if env.native_fault:env.native_fault('after_'+method+'_reply',data)
        return self.record(call,method,raw,data)

    def record(self,call,method,raw,data):
        env=self.env;b=Builder('Actual scoped native recovery reply')
        b1=B1('Exact recovery receiver bytes');a=capture_bytes(b1,raw,format_contract=c1('json'))
        raw_view=case.input_case.snapshot1(b1,[a]);raw_ref=qualified(a,raw_view.package_id)
        basis=[raw_ref];members=[];subjects=[];assessments=[]
        if method=='restart':
            successor=next(qualified(e.reference,e.source_package) for e in call.request.inputs.entries if e.role=='s3.role.successor')
            descriptor,storage=typed_document(b,contract('s3.payload.native_descriptor'),data['descriptor']);basis.append(descriptor)
            subject=b.add('native_subject',{'descriptor':descriptor,'origin_attempt':successor,'scope':scope(successor),'basis':[raw_ref]})
            subjects.append(subject);members.append(subject);env.successor_subject=None;env.successor_job=data['job']
            components=[{**c,'loaded':unknown('s3.native_loading_unobserved'),'evidence':[raw_ref]} for c in env.components]
        elif method=='restore':
            storage=None;components=[{**c,'loaded':known(True,basis=[raw_ref]) if c['component'] in REQUIRED else unknown('s3.native_loading_unobserved'),'evidence':[raw_ref]} for c in env.components]
            state_components(components,REQUIRED,loaded=True)
        else:
            storage=None;components=[]
        if method in ('restart','restore'):
            recovery=b.add('recovery',{'kind':'native_restart' if method=='restart' else 'state_restore','subjects':scope(env.predecessor,env.successor),
                'policy':MODE,'predecessors':index([env.predecessor]),'successors':index([env.successor]),'components':components,
                'overlap':known(env.stop_assessment) if env.stop_assessment else unknown(),'basis':[raw_ref]})
            members.append(recovery)
        root=root_of(call.request.source_view,codec.Resolver(call.context.read.views,limits=case.L))
        projection=b.add('projection_view',{'view_role':'audience_projection','audience':qualified(root['audience'],call.request.source_view.package_id),
            'projection_contract':contract('s3.fixture.recovery_reply'),'members':index(members),'claims':index(),'limits':index()})
        views=(*call.context.read.views,raw_view,*([storage] if storage else []));view=case.frame(b,projection,views)
        refs=[qualified(r,view.package_id) for r in subjects]
        if method=='restart':env.successor_subject=refs[0]
        delta=api.RecordDelta(view.records,(),(*views,view))
        evidence=api.DriverEvidence(reference(call.request.binding.record['id'],'operation_binding',call.request.binding.context['package_id']),delta,index(refs),index([raw_ref]),index(assessments),())
        value=api.NativeStart(successor,known(refs[0]),None,evidence) if method=='restart' else evidence
        return api.CallResult('completed',value,records=delta,effects=(api.EffectBoundary(call.request.command,'crossed',known(data['accepted']),tuple(basis),call.transmission),))


class Environment(case.Environment):
    def __init__(self,root,client,*,source_type='captured_payload'):
        super().__init__(root,client,scientific_path='checkpoint_r2',native_operations=(*case.OPS,*OPS))
        self.native_fault=None;self.stop_assessment=None;self.successor_subject=None;self.successor_job=None
        manifest=json.loads((case.ROOT/'tests/audit_fixtures/sc3_recovery_r2/manifest.json').read_bytes())
        self.predecessor=manifest['attempt'];self.request_ref=manifest['request'];self.run_ref=manifest['run_binding']
        resolver=codec.Resolver(self.context.read.views,limits=case.L);req,pid=resolver.record(self.request_ref,self.request_ref['package_id'])
        self.policy=qualified(req['payload']['recovery_policy']['value'],pid)
        self.recovery_intents=RecoveryIntentRegistry();self.recovery_intents.register(MODE,contract('s3.fixture.checkpoint_restart'),partial_mode,self.pin)
        self.coordinator.recovery_intents=self.recovery_intents
        boundary=DriverBoundary(self.journal,self.jctx,((self.owner,self.octx),));self.recovery_mechanics=Mechanics(self)
        self.recovery_driver=EffectDriver(self.component,self.pin,boundary,self.component,contract('s3.fixture.http'),
            tuple(EffectMethod(op,supplied_callable(self.recovery_mechanics.prepare),supplied_callable(self.recovery_mechanics.execute),contract('s3.fixture.recovery_evidence')) for op in OPS))
        self.recovery_driver.install(self.registry)
        launched=self.run(self.launch(mode='checkpoint'))
        if launched.state!='completed':raise AssertionError(launched.issues)
        self.predecessor_job=client.call('oracle')['jobs'][0]['id']
        self.native_checkpoint=client.call('checkpoint',job=self.predecessor_job)
        self.state(source_type)

    def state(self,source_type):
        b1=B1('Captured checkpoint and distinct successor occurrence')
        raw=base64.b64decode(self.native_checkpoint['bytes']);a=capture_bytes(b1,raw,format_contract=c1('native_checkpoint'))
        output=b1.add('output',{'output_type':'native_report','native_producer':b1.producer,'subjects':[self.predecessor],
            'role':known('s1.checkpoint'),'designation':known('s1.partial_state'),
            'body':{'type_claim':known(c1('partial_model_optimizer')),'payload':{'artifact':a,'selector':not_applicable()},'interpretation_gap':[]},
            'source':s1source('reported',[a]),'relations':[],'checks':[]})
        successor=b1.add('attempt',{'request':self.request_ref,'native_identity':unknown(),'initial_state':known(output),'binding':unknown(),
            'source':s1source('derived',[self.predecessor,output])})
        prior=tuple(v for v in self.context.read.views if v.format['name']=='s1.connection_package')
        v=case.input_case.snapshot1(b1,[output,successor],prior);self.include(v)
        self.checkpoint=qualified(output,v.package_id);self.successor=qualified(successor,v.package_id)
        source={'source_type':'captured_payload','payload':{'artifact':qualified(a,v.package_id),'selector':not_applicable()}}
        if source_type=='native_reference':
            validity,views=case.document(contract('s3.fixture.state_validity'),{'epoch':self.client.epoch,'available':True},self.context.read.views);self.include(*views)
            native={'authority':'S3_owned_fixture_provider','namespace':self.client.namespace,'native_id':self.native_checkpoint['id'],
                'incarnation':known(self.native_checkpoint['id']),'identity_rule':contract('s3.fixture.checkpoint_identity'),'validity':validity,'basis':[]}
            locator,views=case.document(contract('s3.payload.native_state_locator'),{'owner':self.component,'identity':native,
                'state_contract':MODE,'validity':validity,'loader_contract':contract('s3.fixture.partial_loader'),'basis':[self.checkpoint]},self.context.read.views);self.include(*views)
            source={'source_type':'native_reference','reference':locator}
        self.components=[{'component':c,'identity':known(self.native_checkpoint['id']+':'+c['name']),
            'restore_source':known(source),'availability':known(True),'loaded':unknown(),'evidence':[self.checkpoint]} for c in REQUIRED]
        self.components += [{'component':contract('s3.fixture.'+name),'identity':unknown(),'restore_source':unknown(),
            'availability':unknown(),'loaded':unknown(),'evidence':[self.checkpoint]} for name in ('rng','history')]
        self.state_metadata,views=case.document(contract('s3.fixture.partial_state'),{'components':self.components},self.context.read.views);self.include(*views)

    def job(self,ref,resolver):
        record,pid=resolver.record(ref,ref.get('package_id'))
        if record['id']==self.predecessor['target']:return self.predecessor_job
        if record['record_type']!='s3.native_subject':raise ExecutionError('s3.fixture_job_identity')
        descriptor=case.content(resolver,record['payload']['descriptor'],pid,contract('s3.payload.native_descriptor'))
        if descriptor['namespace']!=self.client.namespace or descriptor['incarnation']['state']!='known':raise ExecutionError('s3.fixture_job_identity')
        return descriptor['native_id']

    def observe_stop(self):
        raw,data=self.client.raw('inspect_stop',job=self.predecessor_job)
        b=Builder('Observed stop scoped to exact predecessor component');receipt,storage=typed_document(b,contract('s3.fixture.native_stop_observation'),data)
        f=b.add('frontier',{'local_records':index([self.predecessor,receipt]),'source_positions':index(),'selection_rule':STOP})
        assessment=b.add('assessment',{'question':STOP,'scope':scope(self.predecessor),'result':known(data['observed_stopped']),
            'basis':index([receipt]),'frontier':f,'procedure':STOP,'revises':[],'conflicts_with':[]})
        r=b.add('projection_view',{'view_role':'audience_projection','audience':qualified(root_of(self.view,codec.Resolver(self.context.read.views,limits=case.L))['audience'],self.view.package_id),
            'projection_contract':STOP,'members':index([assessment]),'claims':index(),'limits':index()})
        view=case.frame(b,r,(*self.context.read.views,storage));self.include(storage,view);self.stop_assessment=qualified(assessment,view.package_id)
        return data

    def stop_request(self):
        roles=tuple({'role':'s3.role.'+k,'members':index([v])} for k,v in [('subject',self.predecessor),('policy',self.policy)])
        params={'scope':known('component'),'method':known(contract('s3.fixture.cooperative_stop')),'escalation':not_applicable()}
        return api.OperationRequest(OPS[0],roles,tuple({'key':k,'value':v} for k,v in params.items()),identity())

    def restart_request(self):
        invocation,views=case.document(contract('s3.fixture.restart_arguments'),{'drop_reply':False},self.context.read.views);self.include(*views)
        roles=tuple({'role':'s3.role.'+k,'members':index([v])} for k,v in [('request',self.request_ref),('predecessor',self.predecessor),('successor',self.successor),('scientific_binding',self.run_ref),('checkpoint',self.checkpoint),('policy',self.policy)])
        p={'mode':known('checkpoint_continuation'),'request_relation':known('same_request'),'required_components':known(REQUIRED),
            'overlap_rule':known(contract('s3.fixture.strict_nonoverlap')),'invocation':known(invocation),'purpose':known('scientific_run'),'scientific_rule':known(MODE)}
        return api.OperationRequest(OPS[1],roles,tuple({'key':k,'value':v} for k,v in p.items()),identity())

    def restore_request(self):
        roles=tuple({'role':'s3.role.'+k,'members':index([v])} for k,v in [('subject',self.successor_subject),('checkpoint',self.checkpoint),('policy',self.policy)])
        p={'required_components':known(REQUIRED),'quiescence_rule':known(contract('s3.fixture.quiescent_before_load'))}
        return api.OperationRequest(OPS[2],roles,tuple({'key':k,'value':v} for k,v in p.items()),identity())

    def operation_amounts(self,actual):
        return self.amounts('4' if actual.record['payload']['operation'] in (case.OPS[0],OPS[1]) else '0')


SAVED=('predecessor','request_ref','run_ref','policy','predecessor_job','native_checkpoint','checkpoint','successor',
    'components','state_metadata','stop_assessment','successor_subject','successor_job')

def packet(env,plan,group,transmission):
    value=case.packet(env,plan,group,transmission)
    value['recovery']={name:getattr(env,name) for name in SAVED}
    value['view']=env.view.package_id
    return value


def reopen(value,token,*,native_fault=None):
    from crucis_causal.execution.clock import WallClock
    from crucis_causal.execution.coordinator import Coordinator,AdmissionRule,OwnerAllocation,read_with
    from crucis_causal.execution.journal import Journal
    from crucis_causal.execution.owners import LocalOwner
    from crucis_causal.execution.registry import SuppliedRegistryContext,ExactDriverRegistry,ExactDecisionRegistry,PayloadRegistry
    env=object.__new__(Environment);env.root=Path(value['root']);env.fault=None;env.native_fault=native_fault
    env.client=case.Client(value['address'],token,value['namespace'],value['epoch'])
    env.mechanics=case.Mechanics(value['component'],env.client,'checkpoint')
    env.component=value['component'];env.account=value['account'];env.allocation=value['allocation']
    for name,item in value['recovery'].items():setattr(env,name,item)
    env.launch_roles=None
    views=tuple(codec.parse_snapshot(base64.b64decode(raw),case.L) for raw in value['views'])
    resolver=codec.Resolver(views,limits=case.L);p=value['pin']
    env.pin=api.PinnedArtifactIdentity(p['reference'],p['content_digest'],p['selector'],resolver.view(p['source']))
    env.view=resolver.view(value['view'])
    env.registry=SuppliedRegistryContext(ExactDriverRegistry(),ExactDecisionRegistry(),PayloadRegistry())
    read=api.PinnedReadContext(views,api.supplied_read(v.package_id for v in views),env.registry,case.L)
    env.journal=Journal(env.root/'journal');env.jctx=api.RuntimeContext(read,env.journal.control(env.account))
    h=env.journal.head(env.account,env.jctx);read=read_with(read,*h.records.dependencies,h.value.snapshot)
    env.owner=LocalOwner(env.root/'owner',{'s3.fixture_work':{'unit':contract('fixture_unit'),'capacity':case.number('20')}},native_operations=(*case.OPS,*OPS),ttl_ns='300000000000')
    env.octx=api.RuntimeContext(read,env.owner.control(env.allocation,max_calls='1000'))
    boundary=DriverBoundary(env.journal,env.jctx,((env.owner,env.octx),));env.recovery_mechanics=Mechanics(env)
    env.recovery_driver=EffectDriver(env.component,env.pin,boundary,env.component,contract('s3.fixture.http'),
        tuple(EffectMethod(op,supplied_callable(env.recovery_mechanics.prepare),supplied_callable(env.recovery_mechanics.execute),contract('s3.fixture.recovery_evidence')) for op in OPS))
    env.recovery_driver.install(env.registry)
    env.recovery_intents=RecoveryIntentRegistry();env.recovery_intents.register(MODE,contract('s3.fixture.checkpoint_restart'),partial_mode,env.pin)
    env.coordinator=Coordinator((AdmissionRule(contract('s3.fixture.native_profile'),(*case.OPS,*OPS),env.pin,supplied_callable(case.eligible)),),recovery_intents=env.recovery_intents)
    runtime=api.RuntimeContext(read,None);allocation=OwnerAllocation('native_owner',env.owner,env.octx,env.amounts('0'),contract('s3.owner.same_request_exact_replay'),'0')
    cap=env.coordinator.bind(env.journal,env.jctx,env.journal,(allocation,),('native_owner',),runtime,runtime,not_applicable('s3.no_absolute_deadline'),None)
    env.context=api.CoordinatorContext(read,env.journal,env.journal,{'native_owner':env.owner},env.registry.drivers,env.registry.decisions,cap,WallClock(),case.L)
    original=env.coordinator.restore_prepared(value['command'],resolver.view(value['source']),read)
    if original.state!='completed':raise AssertionError(original.issues)
    return env,original.value
