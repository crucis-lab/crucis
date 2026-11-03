"""Reusable declared-family checks; no native execution or S4 metrics (DLV-08/09)."""
from decimal import Decimal
from .api import PlanIssue,PlanOp,InterpretedValue,FamilyReader
from .errors import ServiceError
from .model import contract,qualified
from .operations import get,read_context,bound
from .contracts import DefinitionCheck
from .schema import catalog

REQUIRED={
 'population':('frame','selection','unit','extent'), 'access':('mode','source_version','operations','responses','scope'),
 'task':('target','question','response_groups','admissibility','abstention','selection'),
 'coverage':('domain','predicate','omission','applicability'), 'temporal':('subject','trajectory','frame','unit','coordinates','windows','lag','epoch','stationarity','boundary'),
 'relational':('perspective','entity_schema','paths','cardinality','identity_namespace','joins','population'),
 'distributed':('parties','contributions','access','aggregation','overlap','count_meaning','normalization','missing_parties'),
 'learned':('encoder','native_domain','source_domain','training','calibration','evaluation','fit_policy','initialization'),
 'alignment':('procedure','source_domain','target_domain','candidates','selection','calibration','losses','ambiguity','timing'),
 'collection':('members','member_contract','weight_meaning','normalization','dependence','derived_selection'),
 'quantity':('event','conditioning','meaning','unit','measure','normalization','uncertainty'),
 'intervention':('environments','target_domain','target_kind','target_disclosure','task_target'),
 'measurement':('underlying','observed','law','scale','noise_source','reference_rule','losses'),
 'randomization':('role','generator','parameters','realization','coupling','coupled_to','stream_key'),
 'transform':('operation','inputs','outputs','maps','preservation','losses','fitted_inputs','reference_rule','order'),
 'comparison':('estimand','direction','matching','cardinality','units','weights','dependence','missingness','output_selection','reference_selection','uncertainty','multiplicity','stopping'),
 'commitment':('fixed','later_bound','cutoff','assurance','exposure','actors','authority','admission','consumption','amendments'),
 'native_handoff':('recipient','operation','response','route','transport','configuration','support','completion','completion_parameters','presentation_policy'),
 'legacy':('battery','version','manifest','item','arm','status','coordinate','projection'),
 'state':('scope','reset','loaded','reuse','visibility','history','independence'),
 'selection':('pool','rule','count','replacement','ordering','stopping','randomization'),
 'resolution':('requirements','candidates','selected','rule','cardinality','compatibility'),
 'response_group':('roles','minimum','maximum_kind','fulfillment','alternatives','abstention'),
 'assessment_context':('boundary','cutoff','revises','conflicts','limits','claim_scope'),
 'action':('target','value','operation','state','source_input')}

def values(reference,context):
    read=read_context(context);found=read.resolver.record(reference,read.active_package,read.access,read.limits)
    if found.record['record_type']!='s2.parameter_set':raise ServiceError('s2.parameter_set_required')
    p=found.record['payload'];name=p['schema']['name'].removeprefix('s2.params.')
    expected=catalog()['parameter_schemas'].get(name)
    if expected is None or p['schema']!=expected['contract']:raise ServiceError('s2.parameter_reader_unavailable')
    from .codec import validate_parameter
    validate_parameter(p)
    # References inside bindings are local to the parameter record's package.
    def qualify(v):
        if isinstance(v,dict):
            if 'binding' in v and 'target_type' in v:return bound(v,found.package_id,context)
            return {k:qualify(x) for k,x in v.items()}
        if isinstance(v,list):return [qualify(x) for x in v]
        return v
    return name,{b['key']:qualify(b['value']) for b in p['bindings']}

def inspect(reference,context,*,require_known=True):
    name,bindings=values(reference,context);read=read_context(context);issues=[];failed=False
    def issue(code,fail=False):
        nonlocal failed
        issues.append(PlanIssue(code,evidence=(reference,)));failed|=fail
    def value(key):
        state=bindings[key]
        return state['value'] if state['state']=='known' else None
    if require_known:
        for key in REQUIRED[name]:
            if bindings[key]['state']=='unresolved':issue('s2.required_'+key+'_unestablished')
    def payload(key):
        v=value(key)
        if v is None:return None
        return read.resolver.payload(v,read.active_package,read.access,read.limits)
    if name=='temporal':
        coordinates=payload('coordinates');windows=payload('windows');lag=value('lag');unit=value('unit')
        if coordinates and unit and coordinates['unit']!=unit:issue('s2.temporal_unit_mapping_required',True)
        if coordinates and len(coordinates['indices'])!=len(set(coordinates['indices'])):issue('s2.duplicate_time_coordinate',True)
        if windows and lag:
            if lag['number_type']!='integer':issue('s2.integer_sample_lag_required')
            else:
                lag=int(lag['text'])
                for w in windows['windows']:
                    start,end=int(w['start']),int(w['end_exclusive']);eligible={int(x) for x in w['eligible_children']}
                    if start>=end or any(c<start or c>=end or c+lag<start or c+lag>=end for c in eligible):issue('s2.invalid_temporal_boundary_eligibility',True)
                    if coordinates:
                        available={int(x) for x in coordinates['indices']}
                        if end-start>len(available) or any(i not in available for i in range(start,end)):issue('s2.window_outside_source_coordinates',True)
    elif name=='relational':
        paths=payload('paths')
        if paths and value('perspective') and paths['perspective']!=value('perspective'):issue('s2.relational_perspective_mismatch',True)
        if paths and any(not p['segments'] or p['segments'][0]!=paths['perspective'] for p in paths['paths']):issue('s2.relational_path_mismatch',True)
        if value('identity_namespace')=='':issue('s2.entity_namespace_required',True)
    elif name=='distributed':
        parties=value('parties');missing=value('missing_parties');contributions=value('contributions')
        if parties is not None and len({get(r,context)['id'] for r in parties})!=len(parties):issue('s2.duplicate_party_identity',True)
        if missing is not None and parties is not None and any(get(r,context)['id'] not in {get(p,context)['id'] for p in parties} for r in missing):issue('s2.unplanned_missing_party',True)
        if parties and contributions is not None and len(contributions)<len(parties):issue('s2.incomplete_party_contributions')
    elif name=='learned':
        if value('native_domain') is not None and get(value('native_domain'),context,'s1.domain')['payload']['domain_kind']!='learned':issue('s2.learned_domain_required',True)
        if value('encoder') is not None and value('native_domain') is not None and get(value('encoder'),context)['id']==get(value('native_domain'),context)['id']:issue('s2.model_and_variable_domain_are_distinct',True)
    elif name=='alignment':
        candidates=value('candidates');ambiguity=value('ambiguity');selection=value('selection')
        if selection==contract('s2.best_reference_score'):issue('s2.outcome_selected_alignment_forbidden',True)
        if candidates is not None:
            if ambiguity=='unique' and len(candidates)!=1:issue('s2.ambiguous_alignment_not_unique',True)
            for ref in candidates:
                found=read.resolver.record(ref,read.active_package,read.access,read.limits);p=found.record['payload']
                if found.record['record_type']!='s1.mapping' or p['mapping_kind']!='semantic_alignment':issue('s2.semantic_alignment_mapping_required',True);continue
                for k,m in [('source_domain','from'),('target_domain','to')]:
                    if value(k) is not None and get(value(k),context)['id']!=get(qualified(p[m],found.package_id),context)['id']:issue('s2.alignment_domain_mismatch',True)
    elif name=='collection':
        data=payload('members')
        if data:
            keys=[m['key'] for m in data['members']]
            if len(keys)!=len(set(keys)):issue('s2.duplicate_native_member_key',True)
            weights=[]
            for m in data['members']:
                n=m['weight']
                if n['number_type']=='nonfinite':issue('s2.invalid_finite_mass',True);continue
                weight=Decimal(n['text']);weights.append(weight)
                if weight<0:issue('s2.negative_mass',True)
                get(m['object'],context,'s1.output')
                try:get(m['parameter'],context)
                except ServiceError as exc:
                    if exc.code not in ('s2.unresolved_reference','s2.package_unavailable','s2.access_denied','s2.reference_target'):raise
                    issue('s2.member_parameter_unestablished')
            if value('normalization')==contract('s2.divide_positive_finite_total') and not any(w>0 for w in weights):issue('s2.nonpositive_normalization_mass',True)
            if value('weight_meaning') is not None and data['weight_meaning']!=value('weight_meaning'):issue('s2.weight_meaning_mismatch',True)
    elif name=='intervention':
        data=payload('environments')
        if data:
            keys=[e['key'] for e in data['environments']]
            if len(keys)!=len(set(keys)):issue('s2.duplicate_environment_key',True)
            for env in data['environments']:
                if env['kind']==contract('s2.observational') and (env['targets']['state']!='known' or env['targets']['value']):issue('s2.observational_target_contradiction',True)
                if value('target_disclosure')=='known' and env['targets']['state']!='known':issue('s2.unknown_targets_not_known_mask',True)
                if env['targets']['state']=='unresolved':issue('s2.environment_targets_unestablished')
    elif name=='measurement':
        a,b=value('underlying'),value('observed')
        if a is not None and b is not None and get(a,context)['id']==get(b,context)['id'] and value('law')==contract('s2.additive_measurement'):
            issue('s2.proxy_is_not_underlying_identity',True)
    elif name=='randomization':
        if value('coupling')=='shared_realization' and not value('coupled_to'):issue('s2.coupling_binding_required')
        if value('coupling')=='independent_by_design' and bindings['realization']['state']!='known':issue('s2.native_independence_not_observed')
    elif name=='response_group':
        minimum,maximum=value('minimum'),value('maximum')
        if value('maximum_kind')=='finite':
            if maximum is None or minimum is None:issue('s2.response_cardinality_unestablished')
            elif Decimal(maximum['text'])<Decimal(minimum['text']):issue('s2.invalid_response_cardinality',True)
    elif name=='transform':
        if value('operation') is not None and value('operation')==contract('s2.best_reference_score'):issue('s2.outcome_selected_transform_forbidden',True)
    result='fail' if failed else 'unknown' if issues else 'pass'
    return DefinitionCheck(contract('s2.family_binding_invariants'),(reference,),result,tuple(issues))

def entity_key(site,schema,perspective,path,local_id):
    if not all(isinstance(x,str) and x for x in (site,schema,perspective,local_id)):raise ServiceError('s2.scoped_entity_identity_required')
    return site,schema,perspective,tuple(path),local_id

def install(registry,implementation):
    def make(name):
        def read(ref,context):
            actual,_=values(ref,context)
            if actual!=name:raise ServiceError('s2.family_schema_mismatch')
            result=inspect(ref,context)
            limits=tuple(PlanIssue('s2.constraint_failed' if result.result=='fail' else i.code,evidence=i.evidence) for i in result.issues)
            value=InterpretedValue(contract('s2.parameter_interpretation'),(ref,),(ref,),(),limits)
            return PlanOp('partial' if limits else 'completed',value,diagnostics=limits)
        return read
    for name in catalog()['parameter_schemas']:
        registry.register(FamilyReader(contract('s2.params.'+name),implementation,contract('s2.parameter_set'),contract('s2.parameter_interpretation'),make(name)))
