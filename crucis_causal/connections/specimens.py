"""Exact-wire transcriptions of nine design scenarios, synthetic only (DLV-08/09).

Generated once as golden specimens. Fixed fixture IDs/times are fictional, never
identities or timestamps claimed for historical native runs. Native byte samples
remain unchanged; the old logical design specimens remain separate documents.
"""
import copy
import hashlib
import uuid

from .domains import directed_link, finite_domain, graph_body, mapped_graph, member, permutation
from .evidence import capture_bytes, evidence_record
from .model import Builder, contract, index, known, not_applicable, number, reference, scope, source, unknown_ref, unresolved


def quantity(b, subject, value, kind='probability', evidence=()):
    return b.output('quantity',{'quantity_kind':'s1.'+kind,'subject':subject,'value':known(number(value),evidence),
        'units':known({'name':'dimensionless','convention':contract('dimensionless')}),'conditioning':[],
        'basis':unresolved(),'procedure':b.producer,'associated_rule':unresolved()},evidence=evidence)


def prop(b,subject,name,value):
    return b.add('proposition',{'predicate':contract('native_property'),'arguments':[
        {'role':'s1.subject','value':subject},{'role':'s1.property','value':name},{'role':'s1.value','value':value}],
        'conditioning':[],'scope':scope(subject)})


def observation(b,subject,name,value,evidence=()):
    return b.add('observation',{'subject':subject,'proposition':prop(b,subject,name,value),'value':value,'scope':scope(subject),
        'source_time':unresolved(),'capture_time':unresolved(),'source':source('reported',evidence,b.producer),'event':unresolved()})


def _freeze(case):
    package=case['package'];ids=[package['package_id']]+[r['id'] for r in package['records']]
    mapping={old:str(uuid.UUID(bytes=hashlib.sha256((case['id']+':'+str(i)).encode()).digest()[:16],version=4)) for i,old in enumerate(ids)}
    def replace(value):
        if isinstance(value,dict):return {k:replace(v) for k,v in value.items()}
        if isinstance(value,list):return [replace(v) for v in value]
        if isinstance(value,str):return mapping.get(value,value)
        return value
    case=replace(case)
    for record in case['package']['records']:
        record['created_at']['value']['value']='2026-11-01T12:00:00.000000Z'
    return case


def build_case(name):
    b=Builder('synthetic SC-1 composition observer');raw=capture_bytes(b,b'{"native":"synthetic fixture"}')
    outputs=[];context=[];observations=[];gaps=[];expect=[]
    def expects(ref,check,result):expect.append({'subject':ref['target'],'contract':'s1.'+check,'result':result})
    if name=='c1':
        title='Reordered graph and failed optional probability'
        d=finite_domain(b,['X','Y'],[raw]);p=b.get(d)['payload'];p['members']=list(reversed(p['members']));native=b.add('domain',p)
        m=permutation(b,native,d,[('1','1'),('0','0')],[raw]);g=b.output('graph',graph_body(native,[directed_link(native,1,0)],'dag'),evidence=[raw])
        view=mapped_graph(b,b.package([g]),g,m);q=quantity(b,prop(b,view,'s1.optional_score',True),'1.2',evidence=[raw])
        outputs=[g,view,q];context=[d,native,m];expects(view,'dag','pass');expects(q,'quantity_value','fail')
    elif name=='c2':
        title='Historical graph with unknown execution and later evidence availability'
        d=finite_domain(b,['A','B'],[raw]);g=b.output('graph',graph_body(d,[directed_link(d,0,1)]),evidence=[raw]);outputs=[g]
        original=capture_bytes(b,b'original file');changed=capture_bytes(b,b'changed file')
        context=[d,original,changed];observations=[observation(b,original,'s1.availability','captured',[original]),
            observation(b,original,'s1.availability','not_found_at_location',[raw]),observation(b,changed,'s1.availability','captured_different_content',[changed])]
        expects(g,'graph_encoding','pass')
    elif name=='c3':
        title='Three distinct paired graph/parameter draws and unselected candidate probability'
        d=finite_domain(b,['A','B'],[raw]);draws=[]
        for i in range(3):
            g=b.output('graph',graph_body(d,[directed_link(d,0,1)] if i<2 else []),evidence=[raw]);parameter=quantity(b,g,str(i+1),'coefficient',[raw])
            draws.append({'key':'sample'+str(i),'object':g,'multiplicity':'1','associated':[{'role':'s1.parameters','target':parameter}]})
        c=b.output('collection',{'collection_kind':'sample_bank','member_contracts':[contract('graph')],'members':draws,
            'extent':scope(d),'ordering':'native_sequence','generation':unresolved(),'weights':[]},evidence=[raw])
        candidate=b.add('proposition',{'predicate':contract('direct_relation'),'arguments':[{'role':'s1.cause','value':member(d,1)},
            {'role':'s1.effect','value':member(d,0)}],'conditioning':[],'scope':scope(d)})
        outputs=[c,quantity(b,candidate,'0.3',evidence=[raw])];context=[d];expects(c,'collection_members','pass')
    elif name=='c4':
        title='Temporal coordinates and narrow query coverage'
        d=finite_domain(b,['X'],[raw]);p=b.get(d)['payload'];variable=p['members'][0]['variable']
        p.update(domain_kind='relative_temporal',coordinate_contract=known(contract('relative_steps')),
            members=[{'key':key,'variable':variable,'coordinates':[{'dimension':contract('relative_step'),'value':number(lag),'reference':unresolved()}]} for key,lag in [('past',-1),('now',0)]])
        temporal=b.add('domain',p);coverage={'pairing':'ordered','domain':temporal,'include_same_node':False,
            'pairs':[{'left':member(temporal,'past'),'right':member(temporal,'now')}],'extent':'listed_only'}
        g=b.output('graph',graph_body(temporal,[directed_link(temporal,'past','now')],'dag',coverage),evidence=[raw])
        outputs=[g];context=[temporal];expects(temporal,'temporal_domain','pass');expects(g,'dag','pass')
    elif name=='c5':
        title='Learned-domain output and separate derived reference alignment'
        native=finite_domain(b,['factor0','factor1'],[raw]);p=b.get(native)['payload'];p['domain_kind']='learned';native=b.add('domain',p)
        target=finite_domain(b,['truthA','truthB'],[raw]);g=b.output('graph',graph_body(native,[directed_link(native,0,1)]),evidence=[raw])
        m=b.add('mapping',{'mapping_kind':'semantic_alignment','from':native,'to':target,
            'entries':[{'from':[member(native,i)],'to':[member(target,i)],'source':source('derived',[raw],b.producer)} for i in range(2)],
            'procedure':b.producer,'purpose':'s1.evaluation_alignment','coverage':scope(native,target),'properties':[],'checks':[],'source':source('derived',[raw])})
        view=mapped_graph(b,b.package([g]),g,m,declared_alignment=True)
        model=b.output('model_reference',{'model_role':'s1.encoder','artifacts':[{'artifact':raw,'selector':known({'selector_type':'json_pointer','pointer':''})}],
            'input_domains':[],'output_domains':[native],'dependencies':[],'associated':[g],'reader':unresolved(),'state_coverage':index(extent='not_examined')},evidence=[raw])
        outputs=[g,view,model];context=[native,target,m];expects(view,'graph_encoding','pass');expects(model,'model_internals','unknown')
    elif name=='c6':
        title='Conflicting terminal evidence with immutable assessments'
        a=observation(b,raw,'s1.outcome.termination','normal',[raw]);z=observation(b,raw,'s1.outcome.termination','failed',[raw])
        def assessment(basis,value,supporting,disputed,revises):
            return b.add('assessment',{'subjects':[raw],'rule':contract('outcome_observations'),'parameters':[],'basis':basis,
                'conclusions':[{'facet':'s1.outcome.termination','value':value,'supporting':supporting,'disputed':disputed}], 'cutoff':basis,'revises':revises})
        old=assessment([a],known('normal',[a]),[a],[],[]);new=assessment([a,z],unresolved('s1.conflicting_evidence',[a,z]),[],[a,z],[old])
        current=b.add('selection',{'purpose':'s1.current_assessment','selected':[new],'rule':contract('explicit_selection'),'basis':[a,z],'source':source()})
        observations=[a,z];context=[old,new,current]
    elif name=='c7':
        title='Parser correction on unchanged native evidence'
        d=finite_domain(b,['A','B'],[raw]);old=b.output('graph',graph_body(d,[directed_link(d,1,0)]),evidence=[raw]);new=b.output('graph',graph_body(d,[directed_link(d,0,1)]),evidence=[raw])
        correction=b.add('relation',{'relation_contract':contract('interpretation_correction'),
            'endpoints':[{'role':'s1.previous','target':old},{'role':'s1.corrected','target':new}], 'parameters':[raw],
            'scope':scope(old,new),'source':source('reconstructed',[raw],b.producer)})
        outputs=[old,new];context=[d,correction];expects(old,'graph_encoding','pass');expects(new,'graph_encoding','pass')
    elif name=='c8':
        title='Complete publication of deliberately partial native evidence'
        partial=capture_bytes(b,b'{"edges":[',source_span={'kind':'byte_range','start':'0','end_exclusive':'10'},native_extent='s1.partial_for_interface')
        declaration=b.add('artifact_declaration',{'native_identity':unresolved(),'reported_format':known(contract('native_checkpoint')),
            'locations':[],'claims':[],'source':source('reported',[raw])})
        gap=b.add('gap',{'subjects':[partial,declaration],'reasons':['s1.incomplete_capture','s1.not_retrieved'],
            'scope':scope(partial,declaration),'source':source('observed',[partial],b.producer)})
        gaps=[gap];context=[partial,declaration];expects(partial,'snapshot_integrity','pass')
    elif name=='c9':
        title='Local result, explicit abstention and separate tied ranking'
        d=finite_domain(b,['A','B','Y'],[raw]);query=prop(b,d,'s1.local_query','parents')
        local=b.output('set',{'predicate':contract('parents'),'targets':[member(d,2)],'candidates':d,'members':[member(d,0)],
            'decisions':[{'proposition':query,'decision':'abstain','reason':known('s1.insufficient_evidence'),'source':source('reported',[raw])}], 'coverage':scope(d),'omission':'s1.unreported'},evidence=[raw])
        abstain=b.output('abstention',{'query':query,'reason':known('s1.insufficient_evidence'),'scope':scope(d)},evidence=[raw])
        rank=b.output('ranking',{'predicate':contract('predictive_rank'),'domain':d,'groups':[[member(d,0),member(d,1)]],
            'direction':'earlier_higher','unranked':[member(d,2)],'excluded':[],'quantities':[]},evidence=[raw])
        outputs=[local,abstain,rank];context=[d];expects(local,'local_set','pass');expects(rank,'ranking','pass')
    else:raise ValueError('unknown composition case')
    root=evidence_record(b,[raw],outputs,subjects=[raw],gaps=gaps,observations=observations,context=context)
    expects(root,'connection_minimum','pass')
    return _freeze({'tickets':['DLV-08','DLV-09'],'id':name,'title':title,'synthetic':True,
        'fixture_identity_and_times':'fictional fixed values, not native occurrences','package':b.package([root]),
        'expectations':expect,'scientific_correctness':'not_assessed'})


def cases():return [build_case('c'+str(i)) for i in range(1,10)]


def history_case():
    """Additional composition covers every optional history record and body family."""
    b=Builder('synthetic history observer');raw=capture_bytes(b,b'{"fixture":"offline history"}')
    d=finite_domain(b,['A','B'],[raw]);configuration=b.add('configuration',{'component':b.producer,'explicit_settings':raw,
        'resolved_defaults':unresolved(),'scope':scope(b.producer),'source':source('reported',[raw])})
    policy=b.add('policy',{'policy_contract':contract('fixture_policy'),'parameters':[raw],'scope':scope(b.producer),
        'authority':known(b.producer),'source':source('reported',[raw])})
    def req(route):
        return b.add('request',{'operation':contract('fixture_discovery'),'task_scope':scope(d),'deliverables':[],
            'completion':contract('fixture_completion'),'completion_parameters':[],'presentation_policy':policy,
            'resource_policy':known(policy),'recovery_policy':known(policy),'route':route,'source':source('reported',[raw])})
    request=req('s1.direct')
    binding=b.add('binding',{'request':request,'adapter':b.producer,'route':'s1.direct','presented':[],
        'resolved_configuration':[configuration],'prerequisites':[],'state':'ready','gaps':[]})
    def attempt(request,initial=None):
        return b.add('attempt',{'request':request,'native_identity':unresolved(),'initial_state':known(initial) if initial else unresolved(),
            'binding':known(binding) if request==b.get(binding)['payload']['request'] else unresolved(),'source':source('reported',[raw])})
    first=attempt(request)
    def session(request,attempt):
        return b.add('session',{'request':request,'native_identity':unresolved(),'parent':not_applicable('no_parent'),
            'membership':index([attempt]),'completion_rule':contract('fixture_completion'),'source':source('reported',[raw])})
    first_session=session(request,first)
    endpoint=b.add('endpoint',{'owner':b.producer,'operation':contract('expert'),'request_contract':contract('expert_request'),
        'response_contract':contract('expert_response'),'input_domains':[d],'allowed_information':policy,
        'transport':contract('fixture_transport'),'source':source('reported',[raw])})
    query=prop(b,d,'s1.synthetic_question','direction?')
    def action_pair(session,attempt):
        authority=b.add('authority_evidence',{'actor':b.producer,'policy':policy,'operation':contract('expert'),
            'subjects':[attempt],'permitted_effects':['s1.deliver'],'decision':'permitted','validity':scope(attempt),'source':source('reported',[raw])})
        action=b.add('action_request',{'session':session,'attempt':attempt,'requester':b.producer,'endpoint':endpoint,
            'arguments':[raw],'question':known(query),'authority':authority,'native_action_identity':unresolved(),'source':source('reported',[raw])})
        response=b.add('action_response',{'request':action,'responder':b.producer,'content':[raw],'response_state':'returned',
            'delivery':[],'source':source('reported',[raw])})
        return action,response
    action,response=action_pair(first_session,first)
    def event(subject,name,predecessors=(),position=None):
        return b.add('event',{'subject':subject,'actor':b.producer,'event_contract':contract(name),'content':raw,'native_time':unresolved(),
            'local_sequence':known({'stream':'fixture','position':str(position),'producer':b.producer}) if position is not None else unresolved(),
            'predecessors':list(predecessors),'correlation':unresolved(),'source':source('reported',[raw])})
    original_event=event(response,'response_recorded',position=0)
    receipt={'authority':'synthetic fixture','namespace':'action receipts','native_id':'one','source':source('reported',[raw])}
    transmission=b.add('transmission',{'message':action,'sender':b.producer,'recipient':b.producer,
        'transport':contract('idempotent_receipt'),'native_receipt':known(receipt),'outcome':'acknowledged','source':source('reported',[raw])})
    axes=b.add('schema',{'payload':{'artifact':raw,'selector':known({'selector_type':'json_pointer','pointer':''})},
        'axes':[],'labels':[],'encoding':contract('json'),'domain':d,'source':source('reported',[raw])})
    presentation=b.add('presentation',{'information_contract':contract('fixture_context'),'payload':known({'artifact':raw,
        'selector':known({'selector_type':'json_pointer','pointer':''})}),'endpoint':known(endpoint),'domain':known(d),'schema':known(axes),
        'recipient':b.producer,'state':'delivered','attempt':first,'source':source('reported',[raw])})
    checkpoint=b.output('model_reference',{'model_role':'s1.checkpoint','artifacts':[{'artifact':raw,'selector':known({'selector_type':'json_pointer','pointer':''})}],
        'input_domains':[d],'output_domains':[d],'dependencies':[configuration],'associated':[],
        'reader':unresolved(),'state_coverage':index([raw],'partial_for_scope')},evidence=[raw])
    second=attempt(request,checkpoint)
    load=b.add('state_load',{'attempt':second,'snapshot':checkpoint,'requested_components':['s1.optimizer','s1.rng'],
        'observed_components':[{'component':'s1.optimizer','identity':known('fixture-v1'),'availability':known(raw),'loaded':known(True),'evidence':[raw]},
            {'component':'s1.rng','identity':unresolved(),'availability':unresolved(),'loaded':unresolved(),'evidence':[]}],
        'configuration_before':[configuration],'configuration_after':[configuration],'continuity':'partial','scope':scope(second),'source':source('reported',[raw])})
    recovery=b.add('recovery',{'successor':second,'predecessor':first,'recovery_kind':'checkpoint_continuation','request_relation':'same_request',
        'state':known(checkpoint),'load':known(load),'reason':known('s1.interrupted'),'policy':policy,'source':source('reported',[raw])})
    replay_request=req('s1.recorded_response_replay');third=attempt(replay_request);replay_session=session(replay_request,third)
    replay_action,replay_response=action_pair(replay_session,third)
    match=b.add('check',{'procedure':b.producer,'contract_checked':contract('exact_replay_match'),'subjects':[replay_action],
        'inputs':[raw],'scope':scope(replay_action),'result':'pass','diagnostics':[],'source':source('reported',[raw])})
    replay=b.add('replay',{'request':replay_request,'attempt':third,'source_attempt':first,'transcript':raw,
        'match_rule':contract('exact_replay_match'),'match_parameters':[],
        'consumed':[{'action':replay_action,'source_event':original_event,'response':replay_response,'match_scope':scope(third),
            'occurrence_key':'first-request','checks':[match]}],'unmatched':[],'exhaustion':'stop','fresh_fallback':'forbidden','source':source('reported',[raw])})
    asked=event(second,'cancel_requested',[original_event],1);ack=event(second,'cancel_acknowledged',[asked],2)
    cancellation=b.add('cancellation',{'subject':second,'requester':b.producer,'policy':policy,'requested':asked,
        'acknowledgment':known(ack),'observed_stop':unresolved(),'source':source('reported',[raw])})
    usage=quantity(b,first,1,'count',[raw]);accounting=b.add('accounting',{'scope':scope(request),'quantities':[usage],
        'members':[first],'aggregation':contract('disjoint_sum'),'coverage':'disjoint_members','revised':[],'source':source('reported',[raw])})
    message=b.output('message',{'message_kind':'action_response','content':response,'correlation':action,'operation':contract('expert'),
        'participants':[{'role':'s1.responder','target':b.producer}]},evidence=[raw])
    claims=b.output('claims',{'propositions':[query],'decisions':[{'proposition':query,'decision':'assert',
        'reason':unresolved(),'source':source('reported',[raw])}],'coverage':scope(d),'omission':'s1.no_assertion'},evidence=[raw])
    diagnostic=b.output('diagnostic',{'code':'s1.synthetic_observer_note','phase':'s1.capture','subjects':[second],
        'attribution':unresolved(),'details':[raw],'source_error':unresolved()},evidence=[raw])
    location=b.add('location',{'locator':'synthetic://reported-only/checkpoint','access_contract':contract('descriptor_only'),
        'expected_snapshot':raw,'retrievals':[],'automatic_access':False})
    root=evidence_record(b,[raw],[checkpoint,usage,message,claims,diagnostic],context=[configuration,policy,binding,presentation,
        first_session,transmission,recovery,replay,cancellation,accounting,location])
    receipt=b.add('import_receipt',{'import_occurrence':str(uuid.uuid4()),'sources':[raw],'reader':b.producer,
        'configuration':known(configuration),'operation_policy':contract('fixture_import'),'result_roots':[root],
        'native_occurrence':unresolved(),'source':source('reported',[raw])})
    # Import occurrence is a separate fictional identity, frozen with this specimen.
    case={'tickets':['DLV-08','DLV-09'],'id':'h1','title':'Optional histories and messages, synthetic only','synthetic':True,
        'fixture_identity_and_times':'fictional fixed values, not native occurrences','package':b.package([root,receipt]),
        'expectations':[{'subject':recovery['target'],'contract':'s1.checkpoint_binding','result':'pass'},
            {'subject':load['target'],'contract':'s1.state_continuity','result':'pass'},
            {'subject':replay['target'],'contract':'s1.replay_occurrences','result':'pass'},
            {'subject':cancellation['target'],'contract':'s1.cancellation_stop','result':'unknown'}], 'scientific_correctness':'not_assessed'}
    return _freeze(case)


def output_family_case():
    b=Builder('synthetic output-family observer');raw=capture_bytes(b,b'[0.4,0.6]');d=finite_domain(b,['A','B'],[raw])
    graph=b.output('graph',graph_body(d,[directed_link(d,0,1)],'dag'),evidence=[raw])
    cid=str(uuid.uuid4());collection=reference(cid,'output');members=[];weights=[]
    for i,mass in enumerate(['0.4','0.6']):
        p=prop(b,collection,'s1.collection_member','atom'+str(i));q=quantity(b,p,mass,evidence=[raw]);weights.append(q)
        members.append({'key':'atom'+str(i),'object':graph,'multiplicity':'1','associated':[{'role':'s1.weight','target':q}]})
    b.add('output',{'output_type':'collection','native_producer':unknown_ref('component'),'subjects':[],
        'role':known('s1.native_answer'),'designation':unresolved(),'body':{'collection_kind':'finite_measure',
            'member_contracts':[contract('graph')],'members':members,'extent':scope(d),'ordering':'unordered',
            'generation':unresolved(),'weights':weights},'source':source('reported',[raw]),'relations':[],'checks':[]},record_id=cid)
    axes=b.add('schema',{'payload':{'artifact':raw,'selector':known({'selector_type':'json_pointer','pointer':''})},
        'axes':[{'name':'s1.sample','axis_kind':'sample','length':'2','coordinates':[{'key':str(i),'member':unresolved(),
            'value':known(str(i))} for i in range(2)],'index_base':'zero'}], 'labels':[],'encoding':contract('json'),'domain':d,'source':source('reported',[raw])})
    def qvalue(value):return b.output('quantity',{'quantity_kind':'s1.probability','subject':d,'value':value,
        'units':known({'name':'dimensionless','convention':contract('dimensionless')}),'conditioning':[],
        'basis':known(raw),'procedure':b.producer,'associated_rule':unresolved()},evidence=[raw])
    tensor=qvalue({'value_type':'tensor','payload':{'artifact':raw,'selector':known({'selector_type':'json_pointer','pointer':''})},
        'axes':axes,'entry_contract':contract('json_probability_tensor'),'missing':contract('no_missing')})
    interval=qvalue({'value_type':'interval','lower':known(number('0.1')),'upper':known(number('0.9')),
        'lower_inclusive':True,'upper_inclusive':True,'construction':contract('native_interval'),'level':known(number('0.95')),'target':graph})
    order=b.output('order',{'predicate':contract('precedes'),'domain':d,'representation':'sequence','sequence':[member(d,0),member(d,1)],
        'pairs':[],'coverage':scope(d),'omission':'s1.no_assertion'},evidence=[raw])
    gap=b.add('gap',{'subjects':[raw],'reasons':['s1.unsupported_semantics'],'scope':scope(raw),'source':source('reported',[raw])})
    opaque=b.output('native_report',{'type_claim':known({'name':'foreign.symbolic_response','version':'fixture-1'}),
        'payload':{'artifact':raw,'selector':known({'selector_type':'json_pointer','pointer':''})},'interpretation_gap':[gap]},evidence=[raw])
    root=evidence_record(b,[raw],[graph,collection,tensor,interval,order,opaque],context=[d,axes],gaps=[gap])
    return _freeze({'tickets':['DLV-08','DLV-09'],'id':'o1','title':'Finite measure, tensor, interval, order and opaque extension',
        'synthetic':True,'fixture_identity_and_times':'fictional fixed values, not native occurrences','package':b.package([root]),
        'expectations':[{'subject':collection['target'],'contract':'s1.finite_measure','result':'pass'},
            {'subject':tensor['target'],'contract':'s1.tensor_encoding','result':'pass'},
            {'subject':interval['target'],'contract':'s1.interval','result':'pass'},
            {'subject':order['target'],'contract':'s1.order_constraints','result':'pass'},
            {'subject':opaque['target'],'contract':'s1.native_interpretation','result':'unknown'}],'scientific_correctness':'not_assessed'})


if __name__=='__main__':
    import argparse
    from pathlib import Path
    from .codec import dumps
    from .semantics import validate
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',required=True);args=parser.parse_args()
    directory=Path(args.out);directory.mkdir(parents=True,exist_ok=True)
    for case in cases()+[history_case(),output_family_case()]:
        report=validate(case['package']);report.require()
        for expected in case['expectations']:
            if not any(c.subject==expected['subject'] and c.contract==expected['contract'] and c.result==expected['result'] for c in report.checks):
                raise ValueError('composition expectation not met: '+str(expected))
        path=directory/(case['id']+'.json')
        if path.exists():continue # Frozen cases are never silently regenerated in place.
        with path.open('xb') as stream:stream.write(dumps(case))
