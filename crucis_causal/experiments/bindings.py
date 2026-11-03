"""Late materialization and run bindings; recording is not execution (DLV-08/09)."""
from .api import PlanIssue,RunBindingDraft
from .errors import ServiceError
from .model import source,scope,index,qualified,contract
from .operations import atomic,get,diagnostic,read_context,bound
from .families import values,inspect

def _located(ref,context):
    r=read_context(context);return r.resolver.record(ref,r.active_package,r.access,r.limits)
def _pass(ref,context,subjects=(),claim=None):
    located=_located(ref,context);p=located.record['payload'];kind=located.record['record_type']
    if kind not in ('s2.assessment','s1.check'):return False
    named=p['claim'] if kind=='s2.assessment' else p['contract_checked']
    if claim is not None and named!=claim:return False
    if subjects and not any(get(qualified(r,located.package_id),context)['id'] in {get(s,context)['id'] for s in subjects} for r in p['subjects']):return False
    return p['result']=='pass'

def record_materialization(spec,evidence,realized,context):
    def build(tx):
        found=_located(spec,context);p=get(spec,context,'s2.transform_spec')['payload'];schema,b=values(realized,context)
        if schema!='transform':raise ServiceError('s2.transform_realization_schema_required')
        issues=list(inspect(realized,context).issues)
        from .information import transform_dependencies
        dependency_check=transform_dependencies(spec,context)
        issues.extend(dependency_check.issues)
        if b['operation']['state']=='known' and b['operation']['value']!=p['operation']:raise ServiceError('s2.transform_operation_mismatch')
        outputs=[]
        if b['outputs']['state']=='known':
            for ref in b['outputs']['value']:
                if get(ref,context)['record_type'] not in {'s2.case_revision','s1.artifact_snapshot','s1.domain','s1.mapping','s1.output'}:issues.append(PlanIssue('s2.materialized_output_not_captured'));continue
                outputs.append(ref)
        if not outputs:issues.append(PlanIssue('s2.materialized_outputs_unestablished'))
        required=[bound(r,found.package_id,context) for r in p['preserves']]
        for req in required:
            rp=get(req,context,'s2.requirement')['payload']
            if not any(_pass(e,context,(req,spec),rp['predicate']) for e in evidence):issues.append(PlanIssue('s2.preservation_check_not_passed',evidence=(req,)))
        checks=[r for r in evidence if get(r,context)['record_type'] in {'s2.assessment','s1.check'}]
        randomness=[r for r in evidence if get(r,context)['record_type']=='s2.resolution_receipt']
        if p['randomness'] and not randomness:issues.append(PlanIssue('s2.transform_randomness_binding_unestablished'))
        gaps=[diagnostic(tx,context,(spec,),i.code) for i in issues]
        ref=tx.add('materialization_receipt',{'transform':spec,'sources':b['inputs']['value'] if b['inputs']['state']=='known' else [],
            'outputs':outputs,'randomness':randomness,'checks':checks,'gaps':gaps,'scope':scope(spec),
            'source':source(context.draft.author,basis='derived',inputs=[realized,*evidence])})
        return ref,issues,(ref,)
    return atomic(context,build)

def bind_run(plan,trial,resolution,materialization,assessments,context):
    def build(tx):
        pl=_located(plan,context);pp=get(plan,context,'s2.plan_snapshot')['payload']
        tr=_located(trial,context);tp=get(trial,context,'s2.trial_slot')['payload'];issues=[];outstanding=[]
        if get(qualified(tp['origin_plan'],tr.package_id),context)['id']!=get(plan,context)['id']:
            if not any(_pass(r,context,(plan,trial),contract('s2.carry_forward')) for r in assessments):issues.append(PlanIssue('s2.carry_forward_unestablished'))
        if trial['target'] not in {r['target'] for r in pp['trials']['members']}:raise ServiceError('s2.trial_not_in_plan')
        for field,allowed in [('task','tasks'),('condition','conditions'),('subject','subjects')]:
            if tp[field]['target'] not in {r['target'] for r in pp[allowed]}:raise ServiceError('s2.trial_intent_mismatch')
        case=bound(tp['case_requirement'],tr.package_id,context);cr=_located(case,context);cp=cr.record['payload']
        target=bound(cp['requirement'],cr.package_id,context) if cr.record['record_type']=='s2.case_slot' else case
        rp=_located(resolution,context);receipt=get(resolution,context,'s2.resolution_receipt')['payload']
        matches=[e for e in receipt['entries'] if e['requirement']['target']==target['target']]
        if len(matches)!=1 or matches[0]['selected']['extent']!='complete_for_scope' or len(matches[0]['selected']['members'])!=1:
            issues.append(PlanIssue('s2.required_resolution_unestablished'));outstanding.append(target)
        else:
            selected=qualified(matches[0]['selected']['members'][0],rp.package_id)
            case_found=_located(selected,context);case_payload=get(selected,context,'s2.case_revision')['payload']
            if cr.record['record_type']=='s2.case_slot':
                needed={get(qualified(r,cr.package_id),context)['id'] for r in cp['sources']}
                actual={get(qualified(r,case_found.package_id),context)['id'] for r in case_payload['definitions']}
                if not needed<=actual:raise ServiceError('s2.case_source_binding_mismatch')
            elif cr.record['record_type']=='s2.case_revision' and cr.record['id']!=case_found.record['id']:raise ServiceError('s2.case_revision_substitution')
        subject=bound(tp['subject'],tr.package_id,context);sp=get(subject,context,'s2.subject_binding')['payload']
        for k in ('native_subject','configuration','support'):
            if sp[k]['state']!='known':issues.append(PlanIssue('s2.native_'+k+'_unestablished'));outstanding.extend(bound(r,_located(subject,context).package_id,context) for r in sp['requirements'])
        condition=qualified(tp['condition'],tr.package_id);condition_found=_located(condition,context);cond=condition_found.record['payload']
        for transform in cond['transforms']:
            matching=[r for r in materialization if get(r,context,'s2.materialization_receipt')['payload']['transform']['target']==transform['target']]
            if not matching:issues.append(PlanIssue('s2.materialization_required'));continue
            for r in matching:
                mp=get(r,context,'s2.materialization_receipt')['payload']
                if mp['gaps'] or not mp['outputs'] or not mp['checks']:issues.append(PlanIssue('s2.materialization_not_established'))
        for ref in assessments:
            if not _pass(ref,context,(plan,trial,resolution)):issues.append(PlanIssue('s2.binding_assessment_not_passed'))
        if not assessments:issues.append(PlanIssue('s2.binding_assessments_required'))
        ref=tx.add('run_binding',{'plan':plan,'trial':trial,'resolutions':[resolution],
            'materialization':index(materialization),'subject':subject,'assessments':list(assessments),'source':source(context.draft.author,basis='derived')})
        # Outstanding contains actual requirement refs only, not an invented ready flag.
        return RunBindingDraft(ref,tuple({r['target']:r for r in outstanding}.values()),tuple(assessments)),issues,(ref,)
    return atomic(context,build)
