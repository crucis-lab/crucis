"""Fixed-source native interaction fixture; no expert/LLM service (DLV-08/09)."""
import base64
from dataclasses import replace
import json
import dispatch_case as case
from crucis_causal.execution import api,codec
from crucis_causal.execution.authority import DriverBoundary
from crucis_causal.execution.coordinator import typed_document,read_with
from crucis_causal.execution.decisions import FixedCandidates,persist_selection
from crucis_causal.execution.drivers import _capture
from crucis_causal.execution.effects import EffectDriver,EffectMethod,capture_reply_problem
from crucis_causal.execution.interaction import validate_delivery,delivery_evidence
from crucis_causal.execution.model import (Builder,ExecutionError,canonical,contract,digest,identity,index,known,
    not_applicable,number,qualified,reference,scope,unknown,unknown_ref)
from crucis_causal.execution.registry import supplied_callable
from crucis_causal.connections.model import Builder as B1,contract as c1,source as s1source,unknown_ref as u1,unresolved as un1
from crucis_causal.connections.evidence import capture_bytes
from crucis_causal.connections.validation import content_bytes

OPS=tuple(contract('s3.op.'+n) for n in ('acquire_information','compute_response','deliver','lookup_delivery'))
PROCEDURE=contract('s3.fixture.fixed_sources')
BUNDLE=contract('s3.fixture.answer_bundle')


def bound(ref,role,read):
    resolver=codec.Resolver(read.views,limits=read.limits);record,pid=resolver.record(ref,ref['package_id'])
    return api.BoundInput(role,qualified(ref,pid),record,pid,resolver.view(pid).digest)


def bytes_of(ref,read):
    record,_=codec.Resolver(read.views,limits=read.limits).record(ref,ref['package_id'])
    return content_bytes(record['payload']['content'])


def action_context(entry,read):
    p=entry.record['payload']
    if p['native_action_identity']['state']!='known' or len(p['arguments'])!=1:raise ExecutionError('s3.fixture_action_identity_required')
    context=qualified(p['arguments'][0],entry.source_package)
    value=json.loads(bytes_of(context,read))
    native=p['native_action_identity']['value']
    if native['authority']!='S3_owned_fixture_provider' or native['namespace']!=value['session'] or native['native_id']!=value['id']:
        raise ExecutionError('s3.fixture_action_context_mismatch')
    return value


class Mechanics:
    def __init__(self,env):self.env=env

    def prepare(self,binding,inputs,context):
        op=binding.record['payload']['operation'];params={p['key']:p['value'] for p in binding.record['payload']['parameters']}
        resolver=codec.Resolver(context.views,limits=context.limits);pid=binding.context['package_id']
        if op==OPS[0]:
            if params['provider']!=known(contract('s3.fixture.permitted_source')) or params['expected_response']!=known(contract('s3.fixture.source_result')):
                raise ExecutionError('s3.fixture_information_provider_unsupported')
            query=case.content(resolver,params['query']['value'],pid,contract('s3.fixture.information_query'))
            if set(query)!={'action','context'} or query['action'] not in {a['id'] for a in self.env.native['actions']}:raise ExecutionError('s3.fixture_information_query_scope')
            return query
        if op==OPS[1]:
            if params['provider']!=known(contract('s3.fixture.fixed_compute')) or params['expected_response']!=known(contract('s3.fixture.source_result')):
                raise ExecutionError('s3.fixture_compute_provider_unsupported')
            actions=[e for e in inputs.entries if e.role=='s3.role.actions']
            if len(actions)!=1:raise ExecutionError('s3.fixture_one_compute_action')
            native=action_context(actions[0],context)
            given=[e for e in inputs.entries if e.role=='s3.role.inputs']
            if len(given)!=1 or given[0].record['record_type']!='s1.artifact_snapshot':raise ExecutionError('s3.fixture_computation_source_missing')
            data=content_bytes(given[0].record['payload']['content']);source=json.loads(data)
            if source.get('action')!=native['id'] or source.get('context')!=native['context']:raise ExecutionError('s3.fixture_computation_source_context_mismatch')
            native_parameters=case.content(resolver,params['native_parameters']['value'],pid,contract('s3.fixture.compute_parameters'))
            if native_parameters!={'rule':'fixed_source_echo'}:raise ExecutionError('s3.fixture_computation_rule_unsupported')
            return {'action':native['id'],'context':native['context'],'source':base64.b64encode(data).decode()}
        if op==OPS[2]:
            selected=validate_delivery(binding,inputs,context)
            if selected.correlation['receiver_atomicity']!='all_or_none' or selected.correlation['physical_operation']!=BUNDLE or selected.validity['receiver_check']!=contract('s3.fixture.current_action_epoch') or selected.validity['owner']!=self.env.component:
                raise ExecutionError('s3.fixture_native_bundle_or_validity_unsupported')
            if params['idempotency']['state']!='not_applicable':raise ExecutionError('s3.fixture_no_delivery_resend_contract')
            entries=[]
            for action,response in zip(selected.actions,selected.responses):
                native=action_context(action,context);body=response.record['payload']
                if body['response_state']!='returned' or len(body['content'])!=1:raise ExecutionError('s3.fixture_native_response_type')
                raw=bytes_of(qualified(body['content'][0],response.source_package),context)
                value=json.loads(raw)
                if value.get('action')!=native['id'] or value.get('context')!=native['context']:raise ExecutionError('s3.fixture_response_context_mismatch')
                entries.append({'action':native['id'],'context':native['context'],'bytes':base64.b64encode(raw).decode()})
            return {'session':self.env.native['session'],'epoch':selected.validity['epoch'],'atomicity':'all_or_none','entries':entries}
        if op==OPS[3]:
            command=next(e for e in inputs.entries if e.role=='s3.role.delivery_command')
            if command.record['payload']['operation']!=OPS[2]:raise ExecutionError('s3.fixture_delivery_command_required')
            query=case.content(resolver,params['query']['value'],pid,contract('s3.fixture.delivery_query'))
            if query!={'command':command.record['id']} or params['receipt_contract']!=known(contract('s3.fixture.answer_receipt')):raise ExecutionError('s3.fixture_delivery_lookup_scope')
            return query
        raise ExecutionError('s3.fixture_interaction_unavailable')

    def _source_result(self,call,method):
        arguments=dict(call.invocation)
        if method=='compute':arguments['transmission']=call.transmission['target']
        try:raw,data=self.env.client.raw(method,**arguments)
        except case.ReplyError as exc:return capture_reply_problem(call,exc.raw,exc.code)
        b=B1('Actually acquired/computed fixture information')
        envelope=capture_bytes(b,raw,format_contract=c1('json'))
        refs=[envelope]
        if data['state']=='available':
            snapshot=capture_bytes(b,base64.b64decode(data['bytes'],validate=True),format_contract=c1('json'),origin=[envelope]);refs.append(snapshot)
        view=case.input_case.snapshot1(b,refs)
        binding=reference(call.request.binding.record['id'],'operation_binding',call.request.binding.context['package_id'])
        datarefs=[qualified(r,view.package_id) for r in refs[1:]]
        evidence=api.DriverEvidence(binding,api.RecordDelta(dependencies=(view,)),index(datarefs,extent='complete_for_scope' if datarefs else 'unresolved'),index([qualified(envelope,view.package_id)]),index(),())
        if datarefs:self.env.data[method][data['action']]=datarefs[0]
        issues=() if datarefs else (api.Issue('s3.required_information_unavailable',scope(call.request.command),(qualified(envelope,view.package_id),)),)
        return api.CallResult('completed' if datarefs else 'partial',evidence,records=evidence.records,issues=issues,
            effects=(api.EffectBoundary(call.request.command,'crossed',known(True),(qualified(envelope,view.package_id),),call.transmission),))

    def acquire(self,call):return self._source_result(call,'information')
    def compute(self,call):return self._source_result(call,'compute')

    def deliver(self,call):
        try:raw,data=self.env.client.raw('answer_bundle',**call.invocation,command=call.request.command['target'],transmission=call.transmission['target'])
        except case.ReplyError as exc:return capture_reply_problem(call,exc.raw,exc.code)
        ref,view=_capture(raw,{'name':'s1.json','version':'0.1.0-proposal.1'},call.context.read.views)
        read=read_with(call.context.read,view)
        selection=validate_delivery(call.request.binding,call.request.inputs,read)
        if data['accepted'] and (data['command']!=call.request.command['target'] or data['transmission']!=call.transmission['target'] or data['entries']!=call.invocation['entries'] or data['atomicity']!='all_or_none' or data['consumed']!=str(len(selection.actions))):
            return capture_reply_problem(call,raw,'s3.delivery_receipt_correlation_unestablished')
        return delivery_evidence(call.request,selection,(ref,),read,accepted=known(data['accepted']),transmission=call.transmission,
            transmitted=known(number(len(selection.responses))),policy_consumed=known(number(data['consumed'])),
            transmission_policy=contract('s3.fixture.gateway_received_response_payloads'),consumption_policy=contract('s3.fixture.native_response_slots'))

    def lookup_delivery(self,call):
        try:raw,data=self.env.client.raw('lookup_answer',**call.invocation)
        except case.ReplyError as exc:return capture_reply_problem(call,exc.raw,exc.code)
        ref,view=_capture(raw,{'name':'s1.json','version':'0.1.0-proposal.1'},call.context.read.views)
        # All native matches and their exact content/context are retained. No
        # empty result permits a new delivery or turns unknown native use into0.
        resolver=codec.Resolver(call.context.read.views,limits=call.context.read.limits)
        original=next(e for e in call.request.inputs.entries if e.role=='s3.role.delivery_command')
        from crucis_causal.execution.journal import resolve_binding
        old=resolve_binding(original.record['payload']['binding'],original.source_package,resolver)
        expected=self.prepare(old,old.inputs,call.context.read)
        for match in data['matches']:
            if match['command']!=call.invocation['command'] or match['entries']!=expected['entries']:
                return capture_reply_problem(call,raw,'s3.fixture_delivery_receipt_command_mismatch')
        evidence=api.DriverEvidence(reference(call.request.binding.record['id'],'operation_binding',call.request.binding.context['package_id']),
            api.RecordDelta(dependencies=(view,)),index(),index([ref]),index(),())
        return api.CallResult('completed',evidence,records=evidence.records,
            effects=(api.EffectBoundary(call.request.command,'crossed',known(True),(ref,),call.transmission),))


class Environment(case.Environment):
    def __init__(self,root,client,job,*,all_sources=False,fault=None):
        resources={'s3.fixture_work':{'unit':contract('fixture_unit'),'capacity':number('20')},
            's3.fixture_policy_slots':{'unit':contract('fixture_response'),'capacity':number('2')},
            's3.fixture_compute':{'unit':contract('fixture_request'),'capacity':number('2')}}
        super().__init__(root,client,scientific_path=None,fault=fault,native_operations=(*case.OPS,*OPS),resources=resources)
        raw,self.native=client.raw('setup_actions',job=job,all_sources=all_sources)
        self.data={'information':{},'compute':{}};self.choices={};self.procedure=None
        b=B1('Observed native actions and fixed permitted information policy')
        envelope=capture_bytes(b,raw,format_contract=c1('json'))
        gateway=b.add('component',{'name':'Owned fixture interaction receiver','role':'s1.fixture_receiver','version':known('1'),
            'implementation':known({'artifact':self.pin.reference,'selector':not_applicable()}),'configuration':un1(),'source':s1source('observed',[envelope])})
        action_ids=[identity(),identity()]
        policy=b.add('policy',{'policy_contract':PROCEDURE,'parameters':[], 'scope':scope(*(reference(i,'s1.action_request') for i in action_ids)),
            'authority':known(gateway),'source':s1source('observed',[envelope])})
        session=b.add('session',{'request':u1('request'),'native_identity':known({'authority':'S3_owned_fixture_provider','namespace':client.namespace,'native_id':self.native['session'],'source':s1source('reported',[envelope])}),
            'parent':not_applicable(),'membership':index(extent='partial_for_scope'),'completion_rule':c1('fixture_unknown_completion'),'source':s1source('reported',[envelope])})
        endpoint=b.add('endpoint',{'owner':gateway,'operation':BUNDLE,'request_contract':c1('fixture_question'),'response_contract':c1('fixture_answer'),
            'input_domains':[],'allowed_information':policy,'transport':c1('fixture_http'),'source':s1source('reported',[envelope])})
        local={}
        for aid,native in zip(action_ids,self.native['actions']):
            value={**native,'session':self.native['session']}
            context=capture_bytes(b,canonical(value),format_contract=c1('json'),origin=[envelope])
            action=b.add('action_request',{'session':session,'attempt':u1('attempt'),'requester':gateway,'endpoint':endpoint,'arguments':[context],
                'question':not_applicable('s3.native_text_prompt_without_formal_proposition'),'authority':u1('authority_evidence'),
                'native_action_identity':known({'authority':'S3_owned_fixture_provider','namespace':self.native['session'],'native_id':native['id'],'source':s1source('reported',[envelope])}),
                'source':s1source('reported',[envelope])},record_id=aid)
            missing=b.add('artifact_declaration',{'native_identity':un1(),'reported_format':known(c1('json')),'locations':[],'claims':[],'source':s1source('reported',[envelope])})
            local[native['label']]={'action':action,'context':context,'missing':missing,'native':native}
        view=case.input_case.snapshot1(b,[policy,session,endpoint,*[v['action'] for v in local.values()]],(self.pin.source_view,));self.include(view)
        self.policy,self.endpoint,self.gateway=(qualified(x,view.package_id) for x in (policy,endpoint,gateway))
        self.actions={label:{**v,'action':qualified(v['action'],view.package_id),'context':qualified(v['context'],view.package_id),'missing':qualified(v['missing'],view.package_id)} for label,v in local.items()}
        self.mechanics_interaction=Mechanics(self)
        boundary=DriverBoundary(self.journal,self.jctx,((self.owner,self.octx),))
        methods=(self.mechanics_interaction.acquire,self.mechanics_interaction.compute,self.mechanics_interaction.deliver,self.mechanics_interaction.lookup_delivery)
        self.interaction_driver=EffectDriver(self.component,self.pin,boundary,self.component,contract('s3.fixture.http'),
            tuple(EffectMethod(op,supplied_callable(self.mechanics_interaction.prepare),supplied_callable(m),contract('s3.fixture.interaction_evidence')) for op,m in zip(OPS,methods)))
        self.interaction_driver.install(self.registry)

    def operation_amounts(self,actual):
        result=list(super().operation_amounts(actual));op=actual.record['payload']['operation']
        count=sum(e.role=='s3.role.responses' for e in actual.inputs.entries) if op==OPS[2] else 0
        for name,unit,value in [('s3.fixture_policy_slots','fixture_response',count),('s3.fixture_compute','fixture_request',int(op==OPS[1]))]:
            result.append({'resource':contract(name),'unit':contract(unit),'quantity':number(value),'aggregation':contract('s3.aggregation.replace_then_disjoint_members')})
        return tuple(result)

    def information(self,label='Q1',*,provider=None):
        item=self.actions[label];native=item['native']
        query,views=case.document(contract('s3.fixture.information_query'),{'action':native['id'],'context':native['context']},self.context.read.views);self.include(*views)
        roles=tuple({'role':'s3.role.'+k,'members':index(v)} for k,v in [('source',[item['context']]),('recipient',[self.component]),('policy',[self.policy])])
        params={'provider':known(provider or contract('s3.fixture.permitted_source')),'query':known(query),'expected_response':known(contract('s3.fixture.source_result'))}
        return api.OperationRequest(OPS[0],roles,tuple({'key':k,'value':v} for k,v in params.items()),identity())

    def compute(self,label='Q1',*,source=None):
        item=self.actions[label];given=source or self.data['information'].get(item['native']['id']) or item['missing']
        params,views=case.document(contract('s3.fixture.compute_parameters'),{'rule':'fixed_source_echo'},self.context.read.views);self.include(*views)
        roles=tuple({'role':'s3.role.'+k,'members':index(v)} for k,v in [('actions',[item['action']]),('inputs',[given]),('policy',[self.policy])])
        values={'provider':known(contract('s3.fixture.fixed_compute')),'native_parameters':known(params),'expected_response':known(contract('s3.fixture.source_result'))}
        return api.OperationRequest(OPS[1],roles,tuple({'key':k,'value':v} for k,v in values.items()),identity())

    def prepare_decisions(self):
        b=B1('Explicit fixed response candidates from actual computation evidence');entries=[];information=[]
        for label,item in self.actions.items():
            native=item['native'];computed=self.data['compute'].get(native['id']);acquired=self.data['information'].get(native['id'])
            if computed:
                response=b.add('action_response',{'request':item['action'],'responder':self.gateway,'content':[computed],'response_state':'returned','delivery':[], 'source':s1source('reported',[computed])})
            else:response=None
            entries.append({'action':item['action'],'response':known(response) if response else unknown('s3.required_source_missing'),
                'required':[acquired or item['missing'],*([computed] if computed else [])],'context':item['context'],
                'domain':not_applicable('s3.native_action_no_variable_domain',subjects=[item['action']]),'permitted_states':['returned']})
            information.extend([item['context'],acquired or item['missing'],*([computed] if computed else [])])
        prior=tuple(v for v in self.context.read.views if v.format['name']=='s1.connection_package')
        responses=case.input_case.snapshot1(b,[b.producer],prior);self.include(responses)
        for entry in entries:
            if entry['response']['state']=='known':entry['response']['value']=qualified(entry['response']['value'],responses.package_id)
        specification={'procedure':PROCEDURE,'policy':self.policy,'bundle':BUNDLE,'fallback':'forbidden','entries':entries}
        raw=canonical(specification);b=B1('Fixed candidate specification, no executable content');ref=capture_bytes(b,raw,format_contract=c1('json'))
        view=case.input_case.snapshot1(b,[ref],tuple(v for v in self.context.read.views if v.format['name']=='s1.connection_package'));self.include(view)
        self.specification=api.PinnedArtifactIdentity(qualified(ref,view.package_id),digest(raw),not_applicable(),view)
        self.procedure=FixedCandidates(self.component,self.pin,self.specification,PROCEDURE);self.procedure.install(self.registry)
        self.information_refs=[self.specification.reference,*information]
        self.candidate_spec=specification
        b3=Builder('Exact information available before response selection')
        refs=[reference(r['id'],r['record_type'],v.package_id) for v in self.context.read.views for r in v.records]
        frontier=b3.add('frontier',{'local_records':index(refs),'source_positions':index(),'selection_rule':contract('s3.fixture.pre_send_inputs')})
        audience=b3.add('audience',{'purpose':contract('s3.private_fixture'),'recipients':index(),'disclosure_policy':unknown_ref('s1.policy'),'authority':unknown()})
        root=b3.add('projection_view',{'view_role':'audience_projection','audience':audience,'projection_contract':contract('s3.fixture.pre_send_frontier'),'members':index([frontier]),'claims':index(),'limits':index()})
        f=case.frame(b3,root,self.context.read.views);self.include(f);self.frontier=qualified(frontier,f.package_id)
        self.information_inputs=api.PinnedInputs(tuple(bound(r,'s3.role.information',self.context.read) for r in self.information_refs),tuple(self.context.read.views))

    def select(self,labels=('Q1',)):
        actions=tuple(bound(self.actions[label]['action'],'s3.role.actions',self.context.read) for label in labels)
        policy=bound(self.policy,'s3.role.policy',self.context.read)
        req=self.procedure.requirements(actions,policy,self.context.read)
        if req.state!='completed':return req
        return self.procedure.select(actions,policy,self.information_inputs,self.frontier,self.context.read)

    def freeze_choice(self,selected,*,occurrence=None):
        head=self.journal.head(self.account,self.jctx);self.include(*head.records.dependencies,head.value.snapshot)
        result=persist_selection(selected.value,self.information_inputs,bound(self.policy,'s3.role.policy',self.context.read),self.journal,head.value,
            replace(self.jctx,read=self.context.read),occurrence or identity())
        if result.state=='completed':self.include(*result.records.dependencies)
        return result

    def deliver(self,decision,labels=('Q1',)):
        resolver=codec.Resolver(self.context.read.views,limits=case.L);record,pid=resolver.record(decision,decision['package_id'])
        actions=[self.actions[label]['action'] for label in labels];responses=[qualified(r,pid) for r in record['payload']['selected']['members']]
        correlation={'contract':BUNDLE,'entries':[{'action':a,'response':r,'endpoint':self.endpoint} for a,r in zip(actions,responses)],'physical_operation':BUNDLE,'receiver_atomicity':'all_or_none'}
        c,views=case.document(contract('s3.payload.bundle_correlation'),correlation,self.context.read.views);self.include(*views)
        validity={'owner':self.component,'scope':scope(*actions),'epoch':self.client.epoch,'valid_from':unknown(),'valid_until':unknown(),
            'receiver_check':contract('s3.fixture.current_action_epoch'),'revocation':contract('s3.fixture.native_close')}
        v,views=case.document(contract('s3.payload.validity'),validity,self.context.read.views);self.include(*views)
        roles=tuple({'role':'s3.role.'+k,'members':index(refs)} for k,refs in [('decision',[decision]),('actions',actions),('responses',responses),('endpoint',[self.endpoint]),('presentations',[])])
        params={'bundle':known(BUNDLE),'correlation':known(c),'validity':known(v),'idempotency':not_applicable('s3.no_implicit_delivery_retry')}
        return api.OperationRequest(OPS[2],roles,tuple({'key':k,'value':value} for k,value in params.items()),identity())

    def lookup_answer(self,command,labels=('Q1',)):
        q,views=case.document(contract('s3.fixture.delivery_query'),{'command':command['target']},self.context.read.views);self.include(*views)
        roles=tuple({'role':'s3.role.'+k,'members':index(refs)} for k,refs in [('delivery_command',[command]),('actions',[self.actions[l]['action'] for l in labels]),('endpoint',[self.endpoint])])
        return api.OperationRequest(OPS[3],roles,({'key':'query','value':known(q)},{'key':'receipt_contract','value':known(contract('s3.fixture.answer_receipt'))}),identity())


def reopen(previous):
    """Fresh actual issuers/registries; no native handle or grant resurrection."""
    from crucis_causal.execution.clock import WallClock
    from crucis_causal.execution.coordinator import AdmissionRule,Coordinator,OwnerAllocation
    from crucis_causal.execution.journal import Journal
    from crucis_causal.execution.owners import LocalOwner
    from crucis_causal.execution.registry import SuppliedRegistryContext,ExactDriverRegistry,ExactDecisionRegistry,PayloadRegistry
    env=object.__new__(Environment)
    for name in ('root','client','pin','component','account','allocation','view','native','data','actions','policy','endpoint','gateway','choices','specification','information_refs','information_inputs','candidate_spec','frontier'):
        setattr(env,name,getattr(previous,name))
    env.fault=None;env.launch_roles=None
    env.registry=SuppliedRegistryContext(ExactDriverRegistry(),ExactDecisionRegistry(),PayloadRegistry())
    read=replace(previous.context.read,registry=env.registry)
    env.journal=Journal(env.root/'journal');env.jctx=api.RuntimeContext(read,env.journal.control(env.account))
    current=env.journal.head(env.account,env.jctx);read=read_with(read,*current.records.dependencies,current.value.snapshot)
    env.owner=LocalOwner(env.root/'owner',previous.owner.resources,native_operations=previous.owner.native_operations,ttl_ns='300000000000')
    env.octx=api.RuntimeContext(read,env.owner.control(env.allocation,max_calls='1000'))
    env.procedure=FixedCandidates(env.component,env.pin,env.specification,PROCEDURE);env.procedure.install(env.registry)
    env.mechanics_interaction=Mechanics(env);boundary=DriverBoundary(env.journal,env.jctx,((env.owner,env.octx),))
    methods=(env.mechanics_interaction.acquire,env.mechanics_interaction.compute,env.mechanics_interaction.deliver,env.mechanics_interaction.lookup_delivery)
    env.interaction_driver=EffectDriver(env.component,env.pin,boundary,env.component,contract('s3.fixture.http'),
        tuple(EffectMethod(op,supplied_callable(env.mechanics_interaction.prepare),supplied_callable(m),contract('s3.fixture.interaction_evidence')) for op,m in zip(OPS,methods)))
    env.interaction_driver.install(env.registry)
    env.coordinator=Coordinator((AdmissionRule(contract('s3.fixture.native_profile'),(*case.OPS,*OPS),env.pin,supplied_callable(case.eligible)),))
    runtime=api.RuntimeContext(read,None);allocation=OwnerAllocation('native_owner',env.owner,env.octx,env.amounts('0'),contract('s3.owner.same_request_exact_replay'),'0')
    cap=env.coordinator.bind(env.journal,env.jctx,env.journal,(allocation,),('native_owner',),runtime,runtime,not_applicable('s3.no_absolute_deadline'),None)
    env.context=api.CoordinatorContext(read,env.journal,env.journal,{'native_owner':env.owner},env.registry.drivers,env.registry.decisions,cap,WallClock(),case.L)
    return env
