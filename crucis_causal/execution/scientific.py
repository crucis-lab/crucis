"""Scoped scientific eligibility, separate from readiness and authority (DLV-08/09)."""
import copy
from dataclasses import dataclass
from . import api
from .model import ExecutionError,canonical,contract,qualified

@dataclass(frozen=True,slots=True)
class ScientificMatch:
    run:dict
    trial:dict
    request:dict
    attempt:dict
    handoff:dict
    source_views:tuple
    claim_scope:str='Exact recorded scientific/native metadata match; not scientific truth or permission'

def match_run(run,request,attempt,handoff,resolver):
    """Validate actual S2 receipt and compiler metadata, with exact contexts/pins."""
    from crucis_causal.experiments.model import digest as d2
    from crucis_causal.experiments.codec import record_bytes
    from crucis_causal.experiments.handoff import _metadata
    for ref,kind in [(run,'s2.run_binding'),(request,'s1.request'),(attempt,'s1.attempt'),(handoff,'s2.request_binding_receipt')]:
        if ref.get('binding')!='external' or ref.get('target_type')!=kind:raise ExecutionError('s3.exact_scientific_binding_required')
    sources={}
    for ref in [run,request,attempt,handoff]:
        for v in resolver.closure(ref['package_id']):sources[v.package_id]=v
    # Reuse the S2 compiler's actual condition/resolution/materialization checks,
    # using its own reader. S3 snapshots never enter the S2 reader.
    from types import SimpleNamespace
    from crucis_causal.experiments.api import PlanReadContext,ReaderLimits
    from crucis_causal.experiments.resolver import PlanResolver,ReadAccess
    from crucis_causal.experiments.handoff import _run
    native_views=[v for v in sources.values() if v.format['name'] in ('s1.connection_package','s2.experiment_package')]
    limits=ReaderLimits(resolver.limits.max_manifest_bytes,resolver.limits.max_records,resolver.limits.max_external_packages,
        resolver.limits.max_external_bytes,resolver.limits.max_reference_depth,resolver.limits.max_depth)
    s2resolver=PlanResolver([v.source_bytes for v in native_views],limits=limits)
    s2read=PlanReadContext(limits,s2resolver,None,ReadAccess(frozenset(v.package_id for v in native_views)),run['package_id'])
    _,_,subject,subjectf,spec,task,response,responsef,policy_ref=_run(run,SimpleNamespace(draft=SimpleNamespace(read=s2read)))
    rf,rpid=resolver.record(run,run['package_id']);req,qpid=resolver.record(request,request['package_id'])
    att,apid=resolver.record(attempt,attempt['package_id']);receipt,hpid=resolver.record(handoff,handoff['package_id'])
    def exact(ref,anchor,expected):
        value,pid=resolver.record(ref,anchor)
        if pid!=expected['package_id'] or value['id']!=expected['target']:raise ExecutionError('s3.scientific_occurrence_mismatch')
    for field,ref in [('run',run),('request',request),('attempt',attempt)]:exact(receipt['payload'][field],hpid,ref)
    exact(att['payload']['request'],apid,request)
    trial,tpid=resolver.record(rf['payload']['trial'],rpid)
    plan,ppid=resolver.record(rf['payload']['plan'],rpid)
    if not any(resolver.record(ref,ppid)[0]['id']==trial['id'] for ref in plan['payload']['trials']['members']):
        raise ExecutionError('s3.scientific_trial_not_in_plan')
    if not rf['payload']['assessments'] or not rf['payload']['resolutions']:raise ExecutionError('s3.scientific_prerequisites_unestablished')
    for ref in [*rf['payload']['assessments'],*receipt['payload']['checks']]:
        check,_=resolver.record(ref,rpid if ref in rf['payload']['assessments'] else hpid)
        if check['payload'].get('result')!='pass':raise ExecutionError('s3.scientific_check_not_passed')
    if not receipt['payload']['checks']:raise ExecutionError('s3.scientific_handoff_check_missing')
    class FrozenBuffer:
        _records={r['id']:r for r in resolver.view(qpid).records}
        def get(self,ref):
            record,_=resolver.record(ref,qpid)
            return record
    meta=_metadata(FrozenBuffer(),request)
    if meta['run_id']!=rf['id'] or meta['run_digest']!=d2(record_bytes(rf)):
        raise ExecutionError('s3.scientific_run_digest_mismatch')
    if meta['request_id']!=req['id'] or meta['attempt_id']!=att['id'] or qpid!=apid:
        raise ExecutionError('s3.scientific_occurrence_mismatch')
    expected_meta={'scientific_operation':task['operation'],'native_operation':spec['operation']['value'],
        'response':response['fulfillment_rule'],'route':spec['route']['value'],'transport':spec['transport']['value'],
        'recipient':spec['recipient']['value']['target'],'configuration':spec['configuration']['value']['target']}
    if any(meta.get(k)!=v for k,v in expected_meta.items()) or req['payload']['operation']!=spec['operation']['value'] or req['payload']['route']!='s1.'+spec['route']['value'] or req['payload']['completion']!=spec['completion']['value']:
        raise ExecutionError('s3.scientific_native_projection_mismatch')
    def coordinates(refs,anchor):
        return [(r['record_type'],r['id'],canonical(r)) for ref in refs for r,_ in [resolver.record(ref,anchor)]]
    def scope_equal(native,scientific):
        return all(coordinates(native[k],qpid)==coordinates(scientific[k],responsef.package_id) for k in ('subjects','qualifiers'))
    if not scope_equal(req['payload']['task_scope'],task['scope']):raise ExecutionError('s3.scientific_scope_mismatch')
    if response['parameters'] or len(req['payload']['deliverables'])!=len(response['deliverables']):raise ExecutionError('s3.scientific_response_projection_unestablished')
    for native,scientific in zip(req['payload']['deliverables'],response['deliverables']):
        if scientific['parameters'] or any(native[k]!=scientific[k] for k in ('role','contract','required','abstention')) or not scope_equal(native['scope'],scientific['scope']):
            raise ExecutionError('s3.scientific_deliverable_mismatch')
    for key in ('resource_policy','recovery_policy'):
        native=req['payload'][key];expected=spec[key]
        if native['state']!=expected['state']:raise ExecutionError('s3.scientific_policy_mismatch')
        if native['state']=='known' and coordinates([native['value']],qpid)!=coordinates([expected['value']],subjectf.package_id):
            raise ExecutionError('s3.scientific_policy_mismatch')
    if meta['request_payload_digest']!=d2(record_bytes({k:v for k,v in req['payload'].items() if k!='source'})):
        raise ExecutionError('s3.scientific_request_changed')
    if meta['presentations_digest']!=d2(record_bytes([resolver.record(r,qpid)[0]['payload'] for r in meta['presentations']])):
        raise ExecutionError('s3.scientific_presentation_changed')
    policy,_=resolver.record(req['payload']['presentation_policy'],qpid)
    allowed={r['target'] for r in meta['presentations']}
    if allowed!={r['target'] for r in policy['payload']['parameters']}:
        raise ExecutionError('s3.scientific_information_policy_mismatch')
    scientific_policy,policy_pid=resolver.record(policy_ref,run['package_id'])
    channels=scientific_policy['payload']['channels']
    if channels['extent']!='complete_for_scope':raise ExecutionError('s3.scientific_information_coverage_unestablished')
    expected_presentations=[]
    for ref in channels['members']:
        channel,channel_pid=resolver.record(ref,policy_pid);value=channel['payload']
        if value['recipient']['state']!='known':raise ExecutionError('s3.scientific_recipient_unestablished')
        if value['recipient']['value']['target']!=meta['recipient'] or value['disposition']=='forbidden':continue
        if value['disposition'] not in ('permitted','required') or value['payload_requirement']['state']!='known':raise ExecutionError('s3.scientific_information_unestablished')
        requirement,required_pid=resolver.record(value['payload_requirement']['value'],channel_pid)
        payloads=[r for r in requirement['payload']['subjects'] if r['target_type'] in ('s1.artifact_snapshot','s1.endpoint')]
        if len(payloads)!=1:raise ExecutionError('s3.scientific_information_payload_ambiguous')
        expected_presentations.append((value,channel_pid,payloads[0],required_pid))
    if len(expected_presentations)!=len(meta['presentations']):raise ExecutionError('s3.scientific_information_cardinality')
    for presentation,(channel,channel_pid,payload_ref,payload_pid) in zip(meta['presentations'],expected_presentations):
        native,_=resolver.record(presentation,qpid);value=native['payload']
        if value['information_contract']!=channel['information'] or value['state']!='permitted' or value['recipient']['target']!=meta['recipient'] or value['attempt']['target']!=att['id']:
            raise ExecutionError('s3.scientific_presentation_mismatch')
        selected=value['endpoint'] if payload_ref['target_type']=='s1.endpoint' else value['payload']
        if selected['state']!='known':raise ExecutionError('s3.scientific_presentation_payload_unestablished')
        ref=selected['value'] if payload_ref['target_type']=='s1.endpoint' else selected['value']['artifact']
        if coordinates([ref],qpid)!=coordinates([payload_ref],payload_pid):raise ExecutionError('s3.scientific_presentation_payload_mismatch')
        if payload_ref['target_type']=='s1.artifact_snapshot' and selected['value']['selector']['state']!='not_applicable':raise ExecutionError('s3.scientific_presentation_selector_unsupported')
        if value['domain']['state']!=channel['domain']['state']:raise ExecutionError('s3.scientific_domain_knowledge_mismatch')
        if value['domain']['state']=='known' and coordinates([value['domain']['value']],qpid)!=coordinates([channel['domain']['value']],channel_pid):
            raise ExecutionError('s3.scientific_domain_mismatch')
    for record in resolver.view(qpid).records:
        p=record['payload']
        if record['record_type']=='s1.presentation' and p['attempt']['target']==att['id'] and p['state'] in ('permitted','delivered','access_observed','use_claimed') and record['id'] not in allowed:
            raise ExecutionError('s3.scientific_extra_information')
    return ScientificMatch(copy.deepcopy(run),qualified(rf['payload']['trial'],rpid),copy.deepcopy(request),copy.deepcopy(attempt),copy.deepcopy(handoff),tuple(sources.values()))

def require_scientific(*,purpose,visible_scientific_intent,matches,na_rule=None,fixed_before_effect=False):
    """No probe label can waive visible intent, including historical effects."""
    if purpose not in ('scientific_run','preparation_probe','historical_observation'):
        raise ExecutionError('s3.fixed_execution_purpose_required')
    if purpose=='scientific_run' or visible_scientific_intent:
        if len(matches)!=1 or not isinstance(matches[0],ScientificMatch):raise ExecutionError('s3.matching_scientific_run_unestablished')
        return matches[0]
    if matches:
        if len(matches)!=1:raise ExecutionError('s3.scientific_binding_ambiguous')
        return matches[0]
    if purpose=='historical_observation':return None # preservation only; not permission to launch
    if not fixed_before_effect or na_rule!=contract('s3.fixed_nonscientific_probe'):
        raise ExecutionError('s3.scientific_nonapplicability_unestablished')
    return None

class RecoveryIntentRegistry:
    """Explicit pure scientific state interpretations; never native permission."""
    def __init__(self):self._rules={}
    def register(self,mode,reset,validate,implementation):
        import inspect
        from .registry import key,_verify_implementation
        from .schema import validate_value
        validate_value(mode,'Contract');validate_value(reset,'Contract')
        if list(inspect.signature(validate).parameters)!=['settings']:raise ExecutionError('s3.recovery_intent_signature')
        _verify_implementation(implementation)
        selected=key(mode)
        if selected in self._rules:raise ExecutionError('s3.duplicate_recovery_interpretation')
        self._rules[selected]=(copy.deepcopy(reset),validate,implementation)
    def check(self,mode,settings):
        from .registry import key,_verify_implementation
        entry=self._rules.get(key(mode))
        if entry is None:raise ExecutionError('s3.scientific_recovery_mode_uninterpreted')
        reset,validate,implementation=entry;_verify_implementation(implementation)
        if settings['reuse']['state']!='known' or settings['reuse']['value']!=mode or settings['reset']['state']!='known' or settings['reset']['value']!=reset:
            raise ExecutionError('s3.scientific_state_mode_unestablished')
        if validate(copy.deepcopy(settings)) is not True:raise ExecutionError('s3.scientific_state_condition_not_established')

def require_recovery_intent(match,resolver,mode,*,policies=None):
    """A captured checkpoint/NA policy is never permission to restart a trial."""
    if not isinstance(match,ScientificMatch):raise ExecutionError('s3.matching_scientific_run_unestablished')
    req,pid=resolver.record(match.request,match.request['package_id'])
    policy=req['payload']['recovery_policy']
    if policy['state']!='known':raise ExecutionError('s3.scientific_recovery_policy_unestablished')
    record,ppid=resolver.record(policy['value'],pid)
    if record['record_type']!='s1.policy' or record['payload']['policy_contract']!=mode:
        raise ExecutionError('s3.scientific_recovery_mode_unestablished')
    trial,tpid=resolver.record(match.trial,match.trial['package_id'])
    condition,cpid=resolver.record(trial['payload']['condition'],tpid)
    information,ipid=resolver.record(condition['payload']['information'],cpid)
    state=information['payload']['state_policy']
    if state['state']!='known':raise ExecutionError('s3.scientific_state_condition_unestablished')
    from crucis_causal.experiments.api import PlanReadContext,ReaderLimits
    from crucis_causal.experiments.resolver import PlanResolver,ReadAccess
    from crucis_causal.experiments.families import values
    sources=resolver.closure(match.handoff['package_id'])
    native_views=[v for v in sources if v.format['name'] in ('s1.connection_package','s2.experiment_package')]
    limits=ReaderLimits(resolver.limits.max_manifest_bytes,resolver.limits.max_records,resolver.limits.max_external_packages,
        resolver.limits.max_external_bytes,resolver.limits.max_reference_depth,resolver.limits.max_depth)
    reader=PlanResolver([v.source_bytes for v in native_views],limits=limits)
    context=PlanReadContext(limits,reader,None,ReadAccess(frozenset(v.package_id for v in native_views)),ipid)
    name,settings=values(state['value'],context)
    if name!='state':
        raise ExecutionError('s3.scientific_state_mode_unestablished')
    permitted_scope=[qualified(ref,ppid) for ref in record['payload']['scope']['subjects']]
    if settings['scope']['state']!='known' or not permitted_scope or canonical(settings['scope']['value'])!=canonical(permitted_scope):
        raise ExecutionError('s3.scientific_state_scope_unestablished')
    if not isinstance(policies,RecoveryIntentRegistry):raise ExecutionError('s3.scientific_recovery_mode_uninterpreted')
    policies.check(mode,settings)
    return resolver.record(state['value'],ipid)
