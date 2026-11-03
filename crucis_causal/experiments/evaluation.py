"""Exact populations/evaluation intent; no scientific metric code (DLV-08/09)."""
import copy
from .api import PlanIssue,EvaluationBindingDraft,FamilyReader,PlanOp,InterpretedValue
from .errors import ServiceError
from .model import contract,qualified,source,scope,index,unknown
from .operations import atomic,get,read_context,bound,diagnostic
from .families import values
from .bindings import _pass

RETAIN=contract('s2.retain_all_intended_units')

def _found(ref,context):
    r=read_context(context);return r.resolver.record(ref,r.active_package,r.access,r.limits)
def _foreign(value,owner,context):
    if isinstance(value,dict):
        if 'binding' in value and 'target_type' in value:return bound(value,owner,context)
        return {k:_foreign(v,owner,context) for k,v in value.items()}
    if isinstance(value,list):return [_foreign(v,owner,context) for v in value]
    return value

def _trial_association(unit,output,basis,context):
    """A fresh scientific trial needs an actual sourced request/output bridge."""
    receipts=[];observations=[]
    for ref in basis:
        found=_found(ref,context);kind=found.record['record_type'];p=_foreign(found.record['payload'],found.package_id,context)
        if kind=='s2.request_binding_receipt':receipts.append(p)
        if kind=='s2.evidence_link':
            for r in p['native_evidence']['members']:
                if r['target_type']=='s1.connection_observation':
                    f=_found(r,context);observations.append(_foreign(f.record['payload'],f.package_id,context))
    for r in receipts:
        rf=_found(r['run'],context);run=_foreign(rf.record['payload'],rf.package_id,context)
        if run['trial']['target']!=unit['target']:continue
        for obs in observations:
            if obs['request']['target']==r['request']['target'] and r['attempt']['target'] in {s['target'] for s in obs['subjects']} and output['target'] in {o['target'] for o in obs['outputs']['members']} and obs['outputs']['extent']=='complete_for_scope':return True
    return False

def record_population(comparison,evidence,context):
    def build(tx):
        cf=_found(comparison,context);cp=get(comparison,context,'s2.comparison')['payload'];issues=[];proposals=[];plans=[];observed=[];seen=set()
        def examine(ref,depth=0):
            if depth>int(context.read.limits.max_reference_depth):raise ServiceError('s2.reference_depth_limit')
            found=_found(ref,context);rid=found.record['id']
            if rid in seen:return
            seen.add(rid);kind=found.record['record_type'];p=_foreign(found.record['payload'],found.package_id,context)
            if kind=='s2.analysis_population_receipt':
                if get(p['comparison'],context)['id']!=get(comparison,context)['id']:raise ServiceError('s2.population_comparison_mismatch')
                proposals.append((ref,p))
            elif kind=='s2.plan_snapshot':plans.append((ref,p))
            elif kind=='s2.evidence_link':
                for subject in p['subjects']:examine(subject,depth+1)
            elif kind in ('s2.case_revision','s2.membership'):observed.append(ref)
        for ref in evidence:examine(ref)
        if cp['population_rule']!=RETAIN:issues.append(PlanIssue('s2.population_rule_unavailable'))
        if len(proposals)>1:raise ServiceError('s2.explicit_population_selection_required')
        intended=[];extent='complete_for_scope'
        for ref,p in plans:
            if comparison['target'] not in {r['target'] for r in p['comparisons']}:continue
            if p['trials']['extent']!='complete_for_scope':extent='partial_for_scope'
            for trial in p['trials']['members']:
                tp=get(trial,context,'s2.trial_slot')['payload']
                if tp['task']['target'] in {x['target'] for x in cp['tasks']} and tp['condition']['target'] in {x['target'] for x in cp['conditions']}:intended.append(trial)
        if not intended and proposals:
            intended=proposals[0][1]['intended']['members'];extent=proposals[0][1]['intended']['extent']
        if not intended and observed:intended=observed
        if not intended:extent='unresolved';issues.append(PlanIssue('s2.intended_population_unestablished'))
        ids=[get(r,context)['id'] for r in intended]
        if any(get(r,context)['record_type'] not in ('s2.case_revision','s2.membership','s2.trial_slot') for r in intended):
            raise ServiceError('s2.scientific_unit_identity_required')
        if len(ids)!=len(set(ids)):raise ServiceError('s2.explicit_multiplicity_unit_required')
        entries=copy.deepcopy(proposals[0][1]['entries']) if proposals else []
        keys=[x['key'] for x in entries]
        if len(keys)!=len(set(keys)):raise ServiceError('s2.duplicate_population_entry_key')
        unit_ids=[get(x['unit'],context)['id'] for x in entries]
        if len(unit_ids)!=len(set(unit_ids)):raise ServiceError('s2.repeated_unit_requires_distinct_membership_or_trial')
        for unit,rid in zip(intended,ids):
            if rid not in unit_ids:
                entries.append({'key':rid,'unit':unit,'members':[],'disposition':'unresolved',
                    'reasons':['s2.intended_unit_not_observed'],'basis':[],'weight':unknown()})
                issues.append(PlanIssue('s2.intended_unit_not_observed',evidence=(unit,)))
        schema,params=values(bound(cp['target'],cf.package_id,context),context)
        if schema!='comparison':raise ServiceError('s2.comparison_parameters_required')
        final_only=params['output_selection']['state']=='known' and params['output_selection']['value']==contract('s2.first_attempt_final_only')
        if not final_only and not (params['output_selection']['state']=='known' and params['output_selection']['value']==contract('s2.declared_population') and cp['measures']==[contract('s2.metadata_binding')]):issues.append(PlanIssue('s2.output_selection_rule_unavailable'))
        for e in entries:
            rid=get(e['unit'],context)['id']
            if rid not in ids:
                e['disposition']='unmatched';e['reasons'].append('s2.outside_intended_frame');issues.append(PlanIssue('s2.outside_intended_frame'))
            if e['disposition'] in ('unresolved','unmatched'):issues.append(PlanIssue('s2.analysis_unit_unresolved',evidence=(e['unit'],)))
            if e['disposition']!='included' and not e['reasons']:raise ServiceError('s2.population_disposition_reason_required')
            if e['disposition']=='excluded' and any(r in ('s2.poor_quality_is_not_exclusion','s2.low_accuracy') for r in e['reasons']):raise ServiceError('s2.outcome_quality_not_exclusion_rule')
            if e['weight']['state']=='known':
                if params['weights']['state']!='known' or not params['weights']['value']:
                    raise ServiceError('s2.population_weight_without_declared_rule')
                issues.append(PlanIssue('s2.population_weight_procedure_required',evidence=(e['unit'],)))
            for member in e['members']:get(member['target'],context)
            for ref in e['basis']:get(ref,context)
            if e['disposition']!='included' or not final_only:continue
            outputs=[m['target'] for m in e['members'] if m['target']['target_type']=='s1.output']
            if not outputs:
                e['disposition']='unresolved';e['reasons'].append('s2.selected_output_unestablished');issues.append(PlanIssue('s2.selected_output_unestablished'));continue
            if len(outputs)!=1:
                e['disposition']='unresolved';e['reasons'].append('s2.output_selection_ambiguous');issues.append(PlanIssue('s2.output_selection_ambiguous'));continue
            output=get(outputs[0],context,'s1.output')['payload']
            if output['output_type']!='graph':raise ServiceError('s2.graph_quality_requires_graph_not_abstention')
            role=output['role']
            if role['state']!='known' or role['value'] not in ('s1.final_graph','s1.final_answer','s1.final_response'):raise ServiceError('s2.stage_is_not_final_output')
            conforms=any(_pass(r,context,(e['unit'],),contract('s2.condition_conformance')) for r in e['basis'])
            if not conforms:
                for ref in e['basis']:
                    found=_found(ref,context);p=found.record['payload']
                    scoped={r['target'] for r in p.get('subjects',[])}
                    if found.record['record_type']=='s2.assessment' and e['unit']['target'] in scoped and p['claim']==contract('s2.condition_conformance') and p['result']=='fail':raise ServiceError('s2.nonconforming_unit_cannot_enter_intended_contrast')
                e['disposition']='unresolved';e['reasons'].append('s2.condition_conformance_unestablished');issues.append(PlanIssue('s2.condition_conformance_unestablished'))
            if get(e['unit'],context)['record_type']=='s2.trial_slot':
                if not _trial_association(e['unit'],outputs[0],e['basis'],context):
                    e['disposition']='unresolved';e['reasons'].append('s2.trial_output_association_unestablished');issues.append(PlanIssue('s2.trial_output_association_unestablished'))
                if not any(_pass(r,context,(e['unit'],),contract('s2.first_attempt_selection')) for r in e['basis']):
                    e['disposition']='unresolved';e['reasons'].append('s2.first_attempt_selection_unestablished');issues.append(PlanIssue('s2.first_attempt_selection_unestablished'))
        gaps=[diagnostic(tx,context,(comparison,),i.code) for i in issues]
        ref=tx.add('analysis_population_receipt',{'comparison':comparison,'intended':index(intended,extent,subjects=(comparison,),gaps=gaps),
            'entries':entries,'rule':cp['population_rule'],'parameters':[bound(cp['target'],_found(comparison,context).package_id,context)],
            'source':source(context.draft.author,basis='derived',inputs=evidence)})
        return ref,issues,(ref,)
    return atomic(context,build)

def _target_signature(refs,context):
    result=[]
    for ref in refs:
        name,b=values(ref,context)
        if name=='intervention' and b['task_target']['state']=='known':result.append(('intervention',b['task_target']['value']))
        if name=='measurement' and b['observed']['state']=='known':result.append(('measurement',get(b['observed']['value'],context)['id']))
    return tuple(sorted(result))

def bind_evaluation(plan,comparison,population,references,inputs,alignments,interpretations,parameters,context):
    def build(tx):
        pf=_found(plan,context);p=get(plan,context,'s2.plan_snapshot')['payload'];cf=_found(comparison,context);cp=get(comparison,context,'s2.comparison')['payload'];issues=[];outstanding=[]
        if comparison['target'] not in {r['target'] for r in p['comparisons']}:raise ServiceError('s2.comparison_not_in_plan')
        pop=get(population,context,'s2.analysis_population_receipt')['payload']
        if pop['comparison']['target']!=comparison['target']:raise ServiceError('s2.population_comparison_mismatch')
        if pop['rule']!=cp['population_rule']:raise ServiceError('s2.population_rule_mismatch')
        if pop['intended']['extent']!='complete_for_scope' or pop['intended']['gaps'] or any(e['disposition'] in ('unresolved','unmatched') for e in pop['entries']):issues.append(PlanIssue('s2.analysis_population_incomplete'))
        _,params=values(bound(cp['target'],cf.package_id,context),context)
        if any(m!=contract('s2.metadata_binding') for m in cp['measures']):
            from .families import inspect
            issues.extend(inspect(bound(cp['target'],cf.package_id,context),context).issues)
        if params['reference_selection']['state']!='known':issues.append(PlanIssue('s2.reference_selection_unestablished'))
        elif params['reference_selection']['value']==contract('s2.best_reference_score'):raise ServiceError('s2.best_reference_selection_forbidden')
        allowed={r['target'] for r in p['definitions'] if r['target_type']=='s2.reference_definition'}
        target=[]
        for task in cp['tasks']:
            tf=_found(bound(task,cf.package_id,context),context);tp=tf.record['payload']
            target.extend(bound(r,tf.package_id,context) for r in tp['targets'])
        signature=_target_signature(target,context)
        for ref in references:
            if ref['target'] not in allowed:raise ServiceError('s2.reference_not_declared_by_plan')
            rf=_found(ref,context);rp=get(ref,context,'s2.reference_definition')['payload']
            other=_target_signature([bound(r,rf.package_id,context) for r in rp['parameters']],context)
            if signature and other and signature!=other:raise ServiceError('s2.reference_target_mismatch')
            if signature and not other:issues.append(PlanIssue('s2.reference_target_binding_unestablished'))
            if rp['assertions']['state']!='known':issues.append(PlanIssue('s2.reference_assertions_unavailable'))
            for requirement in rp['applicability']:
                req=bound(requirement,rf.package_id,context);rqp=get(req,context,'s2.requirement')['payload']
                if not any(_pass(r,context,(req,ref),rqp['predicate']) for r in interpretations):issues.append(PlanIssue('s2.reference_applicability_unestablished',evidence=(req,)));outstanding.append(req)
        for ref in inputs:get(ref,context,('s2.evidence_link','s1.output','s1.connection_observation'))
        mappings=[r for r in alignments if get(r,context)['record_type']=='s1.mapping']
        pairs={}
        for ref in mappings:
            mf=_found(ref,context);mp=mf.record['payload'];k=mp['from']['target'],mp['to']['target'];pairs[k]=pairs.get(k,0)+1
        if any(count>1 for count in pairs.values()):
            selection=params['output_selection']
            if selection['state']!='known' or selection['value'] not in (contract('s2.invariant_alignment'),contract('s2.report_alignment_range')):issues.append(PlanIssue('s2.alignment_ambiguity_unresolved'))
        ref=tx.add('evaluation_binding',{'plan':plan,'comparison':comparison,'inputs':list(inputs),'references':list(references),
            'alignments':list(alignments),'interpretations':list(interpretations),'population':population,'parameters':list(parameters),
            'source':source(context.draft.author,basis='derived')})
        for measure in cp['measures']:
            reader=context.read.registry.lookup(measure)
            if reader is None:issues.append(PlanIssue('s2.measurement_descriptor_unavailable'));continue
            if reader.input_contract!=contract('s2.evaluation_binding'):issues.append(PlanIssue('s2.measurement_descriptor_input_mismatch'));continue
            checked=reader.read(ref,context)
            if not isinstance(checked,PlanOp) or checked.state!='completed' or not isinstance(checked.value,InterpretedValue) or checked.value.contract!=reader.output_contract or ref not in checked.value.subjects or checked.value.limits:
                issues.append(PlanIssue('s2.measurement_binding_unestablished'))
        if not cp['measures']:issues.append(PlanIssue('s2.measurement_contract_required'))
        return EvaluationBindingDraft(ref,population,tuple(outstanding)),issues,(ref,)
    return atomic(context,build)

def install_metadata_descriptor(registry,implementation):
    """Only a metadata contract; this never claims a scientific metric exists."""
    def read(ref,context):
        p=get(ref,context,'s2.evaluation_binding')['payload'];get(p['population'],context,'s2.analysis_population_receipt')
        return PlanOp('completed',InterpretedValue(contract('s2.metadata_binding_interpretation'),(ref,),(),()))
    registry.register(FamilyReader(contract('s2.metadata_binding'),implementation,contract('s2.evaluation_binding'),contract('s2.metadata_binding_interpretation'),read))
