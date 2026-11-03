"""Explicit scientific/native translation and immutable S1 snapshots (DLV-08/09)."""
import copy
import json
import threading
import weakref
from . import api
from .errors import ServiceError
from .model import contract,source,scope,known,unknown,identity,digest,reference,qualified,walk
from .codec import record_bytes
from .operations import atomic,get,bound,parameter,assessment
from .families import values
from .writer import implementation
from .resolver import parse_snapshot

_locks=weakref.WeakKeyDictionary();_lock_guard=threading.Lock()
def _lock(builder):
    with _lock_guard:return _locks.setdefault(builder,threading.RLock())
def _locate(ref,context):
    read=context.draft.read if hasattr(context,'draft') else context.read
    return read.resolver.record(ref,read.active_package,read.access,read.limits)
def _import_ref(ref,context):
    """Copy exact supplied S1 dependency records; no S2 kinds enter SC-1."""
    builder=context.s1_records.builder;read=context.draft.read
    found=read.resolver.record(ref,read.active_package,read.access,read.limits)
    view=read.resolver.lookup(found.package_id,read.access,read.limits)
    if view.format['name']!='s1.connection_package':raise ServiceError('s2.native_reference_requires_s1_snapshot')
    local={r['id']:r for r in view.records};selected={};pending=[found.record['id']]
    while pending:
        rid=pending.pop()
        if rid in selected:continue
        r=local.get(rid)
        if r is None:raise ServiceError('s2.s1_dependency_unavailable')
        selected[rid]=r
        for _,item,_ in walk(r):
            if isinstance(item,dict) and item.get('binding')=='internal':pending.append(item['target'])
    context.s1_records.ingest(tuple(selected.values()))
    # Copy the needed local record closure only, preserving all record contents.
    # External contexts stay explicitly pinned rather than being silently merged.
    for external in view.package['external_packages']:
        other=read.resolver.lookup(external['package_id'],read.access,read.limits)
        if other is None or other.format['name']!='s1.connection_package':raise ServiceError('s2.s1_dependency_unavailable')
        if external['expected_digest']['state']=='known' and external['expected_digest']['value']!=other.snapshot_digest:raise ServiceError('s2.integrity_mismatch')
        # Keep package qualification; descriptors are supplied when freezing.
        descriptors=getattr(builder,'_s2_external',{})
        descriptors[other.package_id]={'package_id':other.package_id,'locator':unknown(),'expected_digest':known(other.snapshot_digest),'access':'s1.supplied_metadata'}
        builder._s2_external=descriptors
    if any(r['record_type']=='s1.artifact_snapshot' and r['payload']['format']['state']=='known' and r['payload']['format']['value']['name'].startswith('s2.payload.') for r in selected.values()):
        descriptors=getattr(builder,'_s2_external',{})
        descriptors[view.package_id]={'package_id':view.package_id,'locator':unknown(),'expected_digest':known(view.snapshot_digest),'access':'s1.supplied_metadata'}
        builder._s2_external=descriptors
    return reference(found.record['id'],found.record['record_type'])

def compiler_context(draft,s1_records,s1_identities,s1_registry,s1_view,projections):
    from crucis_causal.connections.evidence import capture_bytes
    from crucis_causal.connections.model import contract as c1
    b=s1_records.builder;cid=identity();compiler=reference(cid,'s1.component')
    artifact=capture_bytes(b,record_bytes(implementation()),format_contract=c1('s2.code_identity_manifest'),basis='observed')
    b.add('component',{'name':'S2 scientific/native metadata compiler','role':'s1.compiler','version':known(contract('s2.experiment_package')['version']),
        'implementation':known({'artifact':artifact,'selector':known({'selector_type':'json_pointer','pointer':''})}),
        'configuration':unknown(),'source':source(compiler,basis='intrinsic')},record_id=cid,producer=compiler)
    return api.S1ProjectionContext(draft,s1_records,s1_identities,s1_registry,b.producer,compiler,s1_view,projections)

def freeze_s1(package,limits,*,source_view=None):
    """Fresh snapshot identity; copied records never get silently relabeled."""
    from crucis_causal.connections.validation import validate_wire
    from crucis_causal.connections.codec import dumps as s1bytes
    p=copy.deepcopy(package);old=p['package_id']
    old_descriptors=[r for r in p['external_packages'] if r['package_id']==old]
    if any(isinstance(r,dict) and r.get('binding')=='external' and r.get('package_id')==old for _,r,_ in walk(p)) or old_descriptors:
        if source_view is None or source_view.package_id!=old or any(r['expected_digest'].get('value')!=source_view.snapshot_digest for r in old_descriptors):raise ServiceError('s2.self_qualified_s1_reference_requires_explicit_relocation')
    # Typed captured payloads have their own reference context. Preserve an old
    # supplied context explicitly; do not rewrite captured bytes or record IDs.
    needs_source=False
    for r in p['records']:
        if r['record_type']!='s1.artifact_snapshot':continue
        payload=r['payload'];fmt=payload['format'];content=payload['content']
        if fmt['state']=='known' and fmt['value']['name'].startswith('s2.payload.') and content['content_form']=='inline_utf8':
            for _,ref,_ in walk(json.loads(content['text'])):
                if isinstance(ref,dict) and ref.get('binding')=='external' and ref.get('package_id')==old:needs_source=True
    if needs_source:
        if source_view is None or source_view.package_id!=old:raise ServiceError('s2.captured_payload_source_snapshot_required')
        p['external_packages'].append({'package_id':old,'locator':unknown(),'expected_digest':known(source_view.snapshot_digest),'access':'s1.supplied_metadata'})
    p['package_id']=identity()
    if not validate_wire(p).ok:raise ServiceError('s2.invalid_s1_staging_snapshot')
    return parse_snapshot(s1bytes(p),limits)

def _run(binding,context):
    d=context.draft;read=d.read;rf=_locate(binding,context);run=get(binding,d,'s2.run_binding')['payload']
    trial_ref=bound(run['trial'],rf.package_id,d);tf=_locate(trial_ref,context);trial=tf.record['payload']
    plan_ref=bound(run['plan'],rf.package_id,d);pf=_locate(plan_ref,context);plan=pf.record['payload']
    if trial_ref['target'] not in {r['target'] for r in plan['trials']['members']}:raise ServiceError('s2.trial_not_in_plan')
    if run['subject']['target']!=trial['subject']['target']:raise ServiceError('s2.trial_subject_substitution')
    for field,allowed in [('task','tasks'),('condition','conditions'),('subject','subjects')]:
        if trial[field]['target'] not in {r['target'] for r in plan[allowed]}:raise ServiceError('s2.trial_intent_mismatch')
    subject_ref=bound(run['subject'],rf.package_id,d);sf=_locate(subject_ref,context);subject=sf.record['payload']
    if any(subject[k]['state']!='known' for k in ('native_subject','configuration','support')):raise ServiceError('s2.native_support_unestablished')
    support=bound(subject['support']['value'],sf.package_id,d);name,spec=values(support,d)
    if name!='native_handoff':raise ServiceError('s2.native_support_contract_uninterpreted')
    for field in ('recipient','operation','response','route','transport','configuration','completion','presentation_policy'):
        if spec[field]['state']!='known':raise ServiceError('s2.native_projection_parameter_unestablished',field)
    task_ref=bound(trial['task'],tf.package_id,d);taskf=_locate(task_ref,context);task_binding=taskf.record['payload']
    definition_ref=bound(task_binding['definition'],taskf.package_id,d);df=_locate(definition_ref,context);definition=df.record['payload']
    response_ref=bound(definition['response'],df.package_id,d);responsef=_locate(response_ref,context);response=responsef.record['payload']
    condition_ref=bound(trial['condition'],tf.package_id,d);conditionf=_locate(condition_ref,context);condition=conditionf.record['payload']
    policy_ref=bound(condition['information'],conditionf.package_id,d)
    if not run['resolutions']:raise ServiceError('s2.required_resolution_unestablished')
    case_ref=bound(trial['case_requirement'],tf.package_id,d);casef=_locate(case_ref,context);cp=casef.record['payload']
    expected=cp['requirement']['target'] if casef.record['record_type']=='s2.case_slot' else casef.record['id']
    selected=[]
    for ref in run['resolutions']:
        resf=_locate(bound(ref,rf.package_id,d),context);res=resf.record['payload']
        for e in res['entries']:
            if e['selected']['extent']!='complete_for_scope' or len(e['selected']['members'])!=1:raise ServiceError('s2.required_resolution_unestablished')
            if e['requirement']['target']==expected:selected.append((e['selected']['members'][0],resf.package_id))
    if len(selected)!=1:raise ServiceError('s2.required_resolution_unestablished')
    chosen=_locate(bound(*selected[0],d),context)
    if chosen.record['record_type']!='s2.case_revision':raise ServiceError('s2.case_revision_required')
    if casef.record['record_type']=='s2.case_slot':
        needed={r['target'] for r in cp['sources']};actual={r['target'] for r in chosen.record['payload']['definitions']}
        if not needed<=actual:raise ServiceError('s2.case_source_binding_mismatch')
    transforms={r['target'] for r in condition['transforms']};materialized=set()
    for ref in run['materialization']['members']:
        mf=_locate(bound(ref,rf.package_id,d),context);mp=mf.record['payload']
        if mp['gaps'] or not mp['outputs'] or not mp['checks']:raise ServiceError('s2.materialization_not_established')
        for check in mp['checks']:
            if get(bound(check,mf.package_id,d),d)['payload'].get('result')!='pass':raise ServiceError('s2.materialization_check_not_passed')
        materialized.add(mp['transform']['target'])
    if not transforms<=materialized:raise ServiceError('s2.materialization_required')
    if not run['assessments']:raise ServiceError('s2.binding_assessments_required')
    covered=False
    for ref in run['assessments']:
        af=_locate(bound(ref,rf.package_id,d),context);ap=af.record['payload']
        if ap.get('result')!='pass':raise ServiceError('s2.binding_assessment_not_passed')
        if ap.get('claim')==contract('s2.bind_inputs_sources') and {plan_ref['target'],trial_ref['target']}<={r['target'] for r in ap['subjects']}:covered=True
    if not covered:raise ServiceError('s2.scoped_input_binding_check_required')
    return rf,run,subject,sf,spec,definition,response,responsef,policy_ref

def _metadata(builder,request):
    matches=[]
    for r in builder._records.values():
        if r['record_type']!='s1.relation' or r['payload']['relation_contract']!=contract('s2.request_projection_metadata'):continue
        ends={e['role']:e['target'] for e in r['payload']['endpoints']}
        if ends.get('s1.request',{}).get('target')==request['target']:
            snap=builder.get(ends['s1.metadata'])
            if snap['payload']['format']['value']!=contract('s2.handoff_metadata'):raise ServiceError('s2.handoff_metadata_contract')
            matches.append(json.loads(snap['payload']['content']['text']))
    if len(matches)!=1:raise ServiceError('s2.unique_handoff_metadata_required')
    return matches[0]

def _compile(binding,occurrence,recipient,route,context):
    from crucis_causal.connections.api import PresentedBundle
    from crucis_causal.connections.evidence import capture_bytes
    from crucis_causal.connections.model import contract as c1
    rf,run,subject,sf,spec,task,response,responsef,policy_ref=_run(binding,context)
    d=context.draft;b=context.s1_records.builder
    compiler=b.get(context.compiler)['payload'];impl=compiler['implementation']
    if impl['state']!='known':raise ServiceError('s2.compiler_identity_unestablished')
    captured=b.get(impl['value']['artifact'])['payload']['content']
    if captured['content_form']!='inline_utf8' or json.loads(captured['text'])!=implementation():raise ServiceError('s2.compiler_implementation_changed')
    native=bound(subject['native_subject']['value'],sf.package_id,d)
    if native['target']!=recipient['target'] or spec['recipient']['value']['target']!=recipient['target']:raise ServiceError('s2.native_recipient_mismatch')
    if spec['operation']['value']!=route.operation or spec['route']['value']!=route.route_kind or spec['transport']['value']!=route.transport or spec['response']['value']!=response['fulfillment_rule']:raise ServiceError('s2.native_route_projection_mismatch')
    descriptor=context.s1_registry.route(route.operation,route.route_kind)
    if descriptor is None:raise ServiceError('s2.s1_native_route_unregistered')
    completion=spec['completion']['value']
    if context.s1_registry.rule(completion) is None:raise ServiceError('s2.completion_contract_unregistered')
    if context.s1_view.format['name']!='s1.connection_package':raise ServiceError('s2.explicit_s1_view_required')
    if response['fulfillment_rule'] not in (contract('s2.roles_or_abstention'),contract('s2.exact_roles'),contract('s2.exact_final_or_abstention')):raise ServiceError('s2.fulfillment_projection_rule_unavailable')
    b.get(recipient);_import_ref(native,context)
    conf=bound(subject['configuration']['value'],sf.package_id,d);configuration=get(conf,d,'s1.configuration')
    if configuration['payload']['component']['target']!=recipient['target']:raise ServiceError('s2.native_configuration_scope_mismatch')
    _import_ref(conf,context)
    expected={'run_id':rf.record['id'],'run_digest':digest(record_bytes(rf.record)),
        'scientific_operation':task['operation'],'native_operation':route.operation,'response':response['fulfillment_rule'],
        'route':route.route_kind,'transport':route.transport,'recipient':recipient['target'],
        'configuration':conf['target'],'request_id':occurrence.request_id,'attempt_id':occurrence.attempt_id}
    request=reference(occurrence.request_id,'s1.request');attempt=reference(occurrence.attempt_id,'s1.attempt')
    if occurrence.request_id in b._records or occurrence.attempt_id in b._records:
        if occurrence.request_id not in b._records or occurrence.attempt_id not in b._records:raise ServiceError('s2.partial_occurrence_identity_conflict')
        metadata=_metadata(b,request)
        if any(metadata.get(k)!=v for k,v in expected.items()):raise ServiceError('s2.occurrence_intent_conflict')
        if b.get(attempt)['payload']['request']!=request:raise ServiceError('s2.request_attempt_mismatch')
        if metadata['request_payload_digest']!=digest(record_bytes({k:v for k,v in b.get(request)['payload'].items() if k!='source'})):raise ServiceError('s2.request_content_changed')
        if metadata['presentations_digest']!=digest(record_bytes([b.get(r)['payload'] for r in metadata['presentations']])):raise ServiceError('s2.presentation_content_changed')
        return request,attempt,PresentedBundle(tuple(metadata['presentations']),b.get(request)['payload']['presentation_policy'])
    policyf=_locate(policy_ref,context);policy=policyf.record['payload']
    if policy['channels']['extent']!='complete_for_scope':raise ServiceError('s2.complete_native_information_policy_required')
    presentations=[];native_domains=set()
    provenance=source(context.compiler,basis='derived')
    native_policy=reference(identity(),'s1.policy')
    b.add('attempt',{'request':request,'native_identity':unknown(),'initial_state':unknown(),'binding':unknown(),'source':provenance},record_id=attempt['target'],producer=context.compiler)
    for channel_ref in policy['channels']['members']:
        channel_f=_locate(bound(channel_ref,policyf.package_id,d),context);channel=channel_f.record['payload']
        if channel['recipient']['state']!='known':raise ServiceError('s2.information_recipient_unestablished')
        if channel['recipient']['value']['target']!=recipient['target']:continue
        if channel['disposition']=='forbidden':continue
        if channel['disposition'] not in ('permitted','required'):raise ServiceError('s2.information_policy_unestablished')
        if descriptor['presentations'] and channel['information'] not in descriptor['presentations']:raise ServiceError('s2.native_information_contract_unsupported')
        if channel['payload_requirement']['state']!='known':raise ServiceError('s2.native_payload_requirement_unestablished')
        reqf=_locate(bound(channel['payload_requirement']['value'],channel_f.package_id,d),context);req=reqf.record['payload']
        artifacts=[bound(r,reqf.package_id,d) for r in req['subjects'] if r['target_type'] in ('s1.artifact_snapshot','s1.endpoint')]
        if len(artifacts)!=1:raise ServiceError('s2.explicit_single_native_payload_required')
        item=_import_ref(artifacts[0],context)
        domain=unknown()
        if channel['domain']['state']=='known':
            dr=_import_ref(bound(channel['domain']['value'],channel_f.package_id,d),context);domain=known(dr);native_domains.add(dr['target'])
        p=b.add('presentation',{'information_contract':channel['information'],
            'payload':known({'artifact':item,'selector':{'state':'not_applicable','rule':contract('s2.full_native_payload'),'scope':[]}}) if item['target_type']=='s1.artifact_snapshot' else unknown(),
            'endpoint':known(item) if item['target_type']=='s1.endpoint' else unknown(),'domain':domain,'schema':unknown(),
            'recipient':recipient,'state':'permitted','attempt':attempt,'source':provenance},producer=context.compiler)
        presentations.append(p)
    b.add('policy',{'policy_contract':contract('s2.compiled_information_policy'),'parameters':presentations,
        'scope':scope(recipient,*presentations),'authority':unknown(),'source':provenance},record_id=native_policy['target'],producer=context.compiler)
    def scope1(value):
        result={'subjects':[],'qualifiers':[]}
        for part in result:
            for ref in value[part]:
                actual=bound(ref,responsef.package_id,d)
                if actual['target_type'] not in ('s1.domain','s1.proposition'):raise ServiceError('s2.native_scope_projection_unavailable')
                if actual['target_type']=='s1.domain' and actual['target'] not in native_domains:raise ServiceError('s2.native_domain_mapping_required')
                result[part].append(_import_ref(actual,context))
        return result
    deliverables=[]
    if response['parameters']:raise ServiceError('s2.response_group_projection_requires_explicit_rule')
    for item in response['deliverables']:
        if item['parameters']:raise ServiceError('s2.deliverable_parameters_require_explicit_projection')
        cardinality=item['cardinality']
        if item['required']!=(int(cardinality['minimum'])>0):raise ServiceError('s2.conditional_role_projection_requires_explicit_rule')
        if completion!=contract('s2.completion_roles') and cardinality!={'minimum':'1','maximum':{'kind':'finite','value':'1'}}:raise ServiceError('s2.native_cardinality_rule_unavailable')
        deliverables.append({'role':item['role'],'contract':item['contract'],'scope':scope1(item['scope']),'required':item['required'],'abstention':item['abstention']})
    extended=capture_bytes(b,record_bytes({'deliverables':response['deliverables'],'fulfillment_rule':response['fulfillment_rule']}),format_contract=contract('s2.response_projection'),basis='derived')
    def policy1(key):
        value=spec[key]
        if value['state']=='known':return known(_import_ref(value['value'],context))
        return copy.deepcopy(value)
    b.add('request',{'operation':route.operation,'task_scope':scope1(task['scope']),'deliverables':deliverables,
        'completion':completion,'completion_parameters':[extended],'presentation_policy':native_policy,
        'resource_policy':policy1('resource_policy'),'recovery_policy':policy1('recovery_policy'),'route':'s1.'+route.route_kind,'source':provenance},record_id=request['target'],producer=context.compiler)
    expected.update(request_payload_digest=digest(record_bytes({k:v for k,v in b.get(request)['payload'].items() if k!='source'})),presentations=presentations,
        presentations_digest=digest(record_bytes([b.get(r)['payload'] for r in presentations])))
    meta=capture_bytes(b,record_bytes(expected),format_contract=contract('s2.handoff_metadata'),basis='derived')
    b.add('relation',{'relation_contract':contract('s2.request_projection_metadata'),
        'endpoints':[{'role':'s1.request','target':request},{'role':'s1.metadata','target':meta}],'parameters':[],
        'scope':scope(request,attempt),'source':provenance},producer=context.compiler)
    return request,attempt,PresentedBundle(tuple(presentations),native_policy)

def install_projection(registry,scientific_operation,native_operation,response,route_kind,implementation_ref):
    def project(binding,occurrence,recipient,route,context):
        before=set(context.s1_records.builder._records)
        request,attempt,presented=_compile(binding,occurrence,recipient,route,context)
        records=tuple(copy.deepcopy(r) for rid,r in context.s1_records.builder._records.items() if rid not in before)
        return api.PlanOp('completed',api.S1RequestProjection(request,attempt,presented,route,records,(binding,),()))
    registry.register(api.ProjectionProcedure(scientific_operation,native_operation,response,route_kind,implementation_ref,project))

def project_request(binding,occurrence,recipient,route,context):
    b=context.s1_records.builder
    with _lock(b):
        before=copy.deepcopy(b._records);external=copy.deepcopy(getattr(b,'_s2_external',{}))
        def build(tx):
            from jsonschema import Draft202012Validator
            from .schema import _schema,expression
            if occurrence.request_id==occurrence.attempt_id or any(not Draft202012Validator({'$defs':_schema()['$defs'],**expression('ID')}).is_valid(x) for x in (occurrence.request_id,occurrence.attempt_id)):raise ServiceError('s2.distinct_occurrence_ids_required')
            if recipient.get('binding')!='internal':raise ServiceError('s2.local_s1_recipient_required')
            _,_,_,_,_,task,response,_,_=_run(binding,context)
            procedure=context.projections.lookup(task['operation'],route.operation,response['fulfillment_rule'],route.route_kind)
            if procedure is None:raise ServiceError('s2.projection_procedure_unavailable')
            result=procedure.project(binding,occurrence,recipient,route,context)
            if not isinstance(result,api.PlanOp) or result.state!='completed' or not isinstance(result.value,api.S1RequestProjection):raise ServiceError('s2.projection_result_contract')
            if result.value.request['target']!=occurrence.request_id or result.value.attempt['target']!=occurrence.attempt_id:raise ServiceError('s2.projection_occurrence_mismatch')
            from crucis_causal.connections.validation import validate_wire
            p=b.package([result.value.request],external_packages=list(getattr(b,'_s2_external',{}).values()))
            if not validate_wire(p).ok:raise ServiceError('s2.projected_s1_shape_invalid')
            return result.value,(),()
        result=atomic(context.draft,build)
        if result.state=='rejected':b._records=before;b._s2_external=external
        return result

def record_handoff(binding,occurrence,s1_snapshot,context):
    def build(tx):
        view=parse_snapshot(s1_snapshot.source_bytes,context.read.limits)
        if view.format['name']!='s1.connection_package' or view.package!=s1_snapshot.package or view.snapshot_digest!=s1_snapshot.snapshot_digest:raise ServiceError('s2.s1_snapshot_mismatch')
        # The caller explicitly supplies the immutable snapshot; it becomes a
        # declared dependency only through this operation's successful commit.
        context.records.base=context.records.base.with_view(view)
        from .resolver import ReadAccess
        allowed=set(context.records.access.packages)|{view.package_id}
        context.records.access=ReadAccess(frozenset(allowed))
        records={r['id']:r for r in view.records}
        req=records.get(occurrence.request_id);attempt=records.get(occurrence.attempt_id)
        if not req or not attempt or req['record_type']!='s1.request' or attempt['record_type']!='s1.attempt' or attempt['payload']['request']['target']!=req['id']:raise ServiceError('s2.request_attempt_mismatch')
        class Buffer:
            _records=records
            def get(self,ref):return copy.deepcopy(self._records[ref['target']])
        meta=_metadata(Buffer(),reference(req['id'],'s1.request'))
        f=context.read.resolver.record(binding,context.read.active_package,context.read.access,context.read.limits)
        if meta['run_id']!=f.record['id'] or meta['run_digest']!=digest(record_bytes(f.record)):raise ServiceError('s2.handoff_run_binding_mismatch')
        if meta['request_payload_digest']!=digest(record_bytes({k:v for k,v in req['payload'].items() if k!='source'})):raise ServiceError('s2.handoff_request_mismatch')
        if meta['presentations_digest']!=digest(record_bytes([records[r['target']]['payload'] for r in meta['presentations']])):raise ServiceError('s2.handoff_presentations_mismatch')
        allowed={r['target'] for r in meta['presentations']}
        policy=records[req['payload']['presentation_policy']['target']]['payload']
        if allowed!={r['target'] for r in policy['parameters']}:raise ServiceError('s2.handoff_policy_scope_mismatch')
        if any(r['record_type']=='s1.presentation' and r['payload']['attempt']['target']==attempt['id'] and r['payload']['state'] in ('permitted','delivered','access_observed','use_claimed') and r['id'] not in allowed for r in records.values()):raise ServiceError('s2.handoff_extra_native_information')
        projection=parameter(tx,context,'native_handoff',{'operation':known(req['payload']['operation']),
            'response':known(meta['response']),'route':known(meta['route']),'transport':known(meta['transport'])})
        check=assessment(tx,context,contract('s2.handoff_binding'),(binding,),(),'pass')
        ref=tx.add('request_binding_receipt',{'run':binding,'request':reference(req['id'],'s1.request',view.package_id),
            'attempt':reference(attempt['id'],'s1.attempt',view.package_id),'projection':projection,'checks':[check],
            'source':source(context.author,basis='observed')})
        return ref,(),(ref,)
    return atomic(context,build)

def link_evidence(subjects,s1_evidence,context):
    def build(tx):
        from .schema import catalog
        allowed=set(catalog()['core_payloads']['s2.evidence_link']['native_evidence'].removeprefix('IndexList(Ref(').removesuffix('))').split('|'))
        for ref in subjects:get(ref,context)
        for ref in s1_evidence:
            if ref.get('binding')!='external' or ref['target_type'] not in allowed:raise ServiceError('s2.qualified_native_evidence_required')
            get(ref,context)
        from .model import index
        ref=tx.add('evidence_link',{'subjects':list(subjects),'native_evidence':index(s1_evidence),
            'source':source(context.author,basis='observed',inputs=s1_evidence)})
        return ref,(),(ref,)
    return atomic(context,build)
