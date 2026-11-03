"""Fixed-byte, chronology, decision and exposure accounts (DLV-08/09)."""
from decimal import Decimal
from .api import PlanIssue
from .contracts import DefinitionCheck
from .errors import ServiceError
from .model import contract,source,scope,index,known,unknown,qualified,walk
from .operations import atomic,get,bound,assessment
from .families import values

def located(ref,context):
    r=context.read;return r.resolver.record(ref,r.active_package,r.access,r.limits)

def event_order(events,context):
    seen=set();active=set();issues=[]
    def visit(ref,depth):
        if depth>int(context.read.limits.max_reference_depth):raise ServiceError('s2.reference_depth_limit')
        f=located(ref,context);rid=f.record['id']
        if rid in active:issues.append(PlanIssue('s2.event_precedence_cycle',evidence=(ref,)));return
        if rid in seen:return
        if f.record['record_type'] not in ('s2.lifecycle_event','s1.event'):raise ServiceError('s2.event_required')
        active.add(rid);seen.add(rid)
        for p in f.record['payload']['predecessors']:visit(bound(p,f.package_id,context),depth+1)
        active.remove(rid)
    for event in events:visit(event,0)
    return DefinitionCheck(contract('s2.event_precedence'),tuple(events),'fail' if issues else 'pass',tuple(issues))

def prospective_dependencies(plan,future_evidence,context):
    """Supplied future classification is evidence, never inferred from file names."""
    f=located(plan,context);get(plan,context,'s2.plan_snapshot')
    future=[located(r,context) for r in future_evidence]
    packages={r.package_id for r in future};ids={r.record['id'] for r in future}
    closure=context.read.resolver.closure(f.package_id,context.read.access,context.read.limits)
    bad=[v for v in closure if v.package_id in packages or any(r['id'] in ids for r in v.records)]
    return DefinitionCheck(contract('s2.prospective_dependency_closure'),(plan,),
        'fail' if bad else 'pass',(PlanIssue('s2.future_evidence_in_definition_package',evidence=tuple(future_evidence)),) if bad else ())

def record_commitment(plan,evidence,context):
    def build(tx):
        f=located(plan,context);get(plan,context,'s2.plan_snapshot');content=evidence.subject
        if content['package_id']==context.records.package_id or content['package_id']!=f.package_id:raise ServiceError('s2.distinct_frozen_commitment_subject_required')
        view=context.read.resolver.lookup(content['package_id'],context.read.access,context.read.limits)
        if view is None or view.snapshot_digest!=content['digest']:raise ServiceError('s2.commitment_bytes_mismatch')
        if f.record['id'] not in content['selected_records'] or any(r not in {x['id'] for x in view.records} for r in content['selected_records']):raise ServiceError('s2.commitment_selected_record_mismatch')
        ev=located(evidence.event,context);event=ev.record
        if event['record_type'] not in ('s2.lifecycle_event','s1.event'):raise ServiceError('s2.commitment_event_required')
        subjects=event['payload']['subjects'] if event['record_type']=='s2.lifecycle_event' else [event['payload']['subject']]
        if f.record['id'] not in {get(bound(r,ev.package_id,context),context)['id'] for r in subjects}:raise ServiceError('s2.commitment_event_scope_mismatch')
        ordering=event_order((evidence.event,),context)
        if ordering.result=='fail':raise ServiceError('s2.event_precedence_cycle')
        name,params=values(evidence.assurance,context)
        if name!='commitment':raise ServiceError('s2.commitment_assurance_schema_required')
        issues=[]
        if params['assurance']['state']=='known' and params['assurance']['value']=='external_attestation':issues.append(PlanIssue('s2.external_assurance_not_established_by_local_record'))
        for ref in evidence.exposure:get(ref,context,'s2.exposure_receipt')
        receipt=tx.add('commitment_receipt',{'plan':plan,'content':content,'event':evidence.event,'assurance':evidence.assurance,
            'exposure':index(evidence.exposure),'source':source(context.author,basis='observed',inputs=[evidence.event,evidence.assurance])})
        return receipt,issues,(receipt,)
    return atomic(context,build)

def record_amendment(previous,revised,evidence,context):
    def build(tx):
        old=get(previous,context,'s2.plan_snapshot');new=get(revised,context,'s2.plan_snapshot')
        if old['id']==new['id']:raise ServiceError('s2.new_plan_identity_required_for_amendment')
        ef=located(evidence.event,context);event=get(evidence.event,context,('s2.lifecycle_event','s1.event'));get(evidence.explanation,context,('s2.parameter_set','s1.artifact_snapshot'))
        subjects=event['payload']['subjects'] if event['record_type']=='s2.lifecycle_event' else [event['payload']['subject']]
        if new['id'] not in {get(bound(r,ef.package_id,context),context)['id'] for r in subjects}:raise ServiceError('s2.amendment_event_scope_mismatch')
        if not evidence.affected['subjects']:raise ServiceError('s2.amendment_scope_required')
        for ref in evidence.affected['subjects']:get(ref,context)
        for ref in evidence.prior_observed['members']:get(ref,context)
        if event_order((evidence.event,),context).result=='fail':raise ServiceError('s2.event_precedence_cycle')
        ref=tx.add('amendment',{'previous':previous,'revised':revised,'affected':evidence.affected,'reason':evidence.reason,
            'explanation':evidence.explanation,'event':evidence.event,'prior_observed':evidence.prior_observed,
            'source':source(context.author,basis='observed',inputs=[previous,revised,evidence.event])})
        return ref,(),(ref,)
    return atomic(context,build)

def record_decision(policy,information,chosen,rule,event,context):
    """Record even a nonconforming observed choice; never execute/repair it."""
    def build(tx):
        f=located(policy,context);p=get(policy,context,'s2.selection_rule')['payload'];issues=[];failed=False;parameters=[];recipe=None
        for ref in p['parameters']:
            name,b=values(bound(ref,f.package_id,context),context)
            if name=='selection' and b['adaptive_rule']['state']=='known':
                recipe=context.read.resolver.payload(b['adaptive_rule']['value'],context.read.active_package,context.read.access,context.read.limits)
                parameters.append(bound(ref,f.package_id,context))
        if rule!=contract('s2.threshold_action_selection') or recipe is None:issues.append(PlanIssue('s2.adaptive_rule_unavailable'))
        if recipe and int(recipe['max_rounds'])<2:issues.append(PlanIssue('s2.adaptive_action_limit_reached'));failed=True
        means=[]
        for ref in information:
            r=get(ref,context)
            if r['record_type']=='s1.output' and r['payload']['output_type']=='quantity':
                b=r['payload']['body'];v=b['value']
                if b['quantity_kind']=='s1.mean' and v.get('state')=='known' and v['value']['number_type']!='nonfinite' and recipe:
                    owner=located(ref,context).package_id
                    prop=get(bound(b['subject'],owner,context),context,'s1.proposition')
                    args={a['role']:a['value'] for a in prop['payload']['arguments']}
                    action=args.get('s1.target');value=args.get('s1.value');first=recipe['first']
                    if prop['payload']['predicate'] in (contract('s2.mean_z_after_action'),contract('s2.native_source_mean_after_action')) and isinstance(action,dict) and action.get('key')==first['target'] and isinstance(value,dict) and value.get('number_type')!='nonfinite' and 'text' in value and Decimal(value['text'])==Decimal(first['value']['text']):means.append(Decimal(v['value']['text']))
        expected=None
        if recipe and len(means)==1:expected=recipe['nonnegative'] if means[0]>=Decimal(recipe['threshold']['text']) else recipe['negative']
        else:issues.append(PlanIssue('s2.adaptive_input_unestablished'))
        domains=[]
        for ref in p['inputs']:
            sf=located(bound(ref,f.package_id,context),context)
            if sf.record['record_type']=='s2.source_definition' and sf.record['payload']['domain']['state']=='known':
                domain_ref=bound(sf.record['payload']['domain']['value'],sf.package_id,context);df=located(domain_ref,context)
                domains.append((df.package_id,get(domain_ref,context,'s1.domain')))
        if len(chosen)!=1:issues.append(PlanIssue('s2.adaptive_choice_cardinality_unestablished'))
        for ref in chosen:
            name,b=values(ref,context)
            if name!='action':raise ServiceError('s2.action_parameters_required')
            if b['state']['state']=='known' and b['state']['value']!='selected':issues.append(PlanIssue('s2.selection_not_delivery_evidence'));failed=True
            target=b['target'];actual_key=None
            if target['state']=='known':
                rid=get(target['value'],context)['id']
                for owner,domain in domains:
                    for member in domain['payload']['members']:
                        if get(bound(member['variable'],owner,context),context)['id']==rid:actual_key=member['key']
            if expected and actual_key is not None and b['value']['state']=='known':
                value=b['value']['value']
                if value['number_type']=='nonfinite' or actual_key!=expected['target'] or Decimal(value['text'])!=Decimal(expected['value']['text']):issues.append(PlanIssue('s2.adaptive_choice_nonconforming'));failed=True
            else:issues.append(PlanIssue('s2.adaptive_target_binding_unestablished'))
            if b['source_input']['state']!='known' or {r['target'] for r in b['source_input']['value']}!={r['target'] for r in information}:issues.append(PlanIssue('s2.adaptive_input_lineage_unestablished'))
        get(event,context,('s2.lifecycle_event','s1.event'))
        checked=assessment(tx,context,contract('s2.adaptive_policy_conformance'),(policy,*chosen),information,'fail' if failed else 'unknown' if issues else 'pass',issues)
        ref=tx.add('decision_receipt',{'policy':policy,'information':index(information),'chosen':index(chosen),'rule':rule,'event':event,
            'parameters':parameters,'source':source(context.author,basis='observed',inputs=[checked])})
        return ref,issues,(ref,checked)
    return atomic(context,build)

def exposure_information(receipts,context):
    """Reported/observed exposure persists independently of grant/consumption policy."""
    info=[];seen=set();issues=[]
    for ref in receipts:
        f=located(ref,context);p=get(ref,context,'s2.exposure_receipt')['payload']
        for item in p['information']['members']:
            r=bound(item,f.package_id,context);rid=get(r,context)['id']
            if rid not in seen:info.append(r);seen.add(rid)
        if p['information']['extent']!='complete_for_scope':issues.append(PlanIssue('s2.exposure_extent_unestablished'))
        if p['assessment']['state']!='known' or get(bound(p['assessment']['value'],f.package_id,context),context,'s2.assessment')['payload']['result']!='pass':issues.append(PlanIssue('s2.exposure_assessment_unestablished'))
    return tuple(info),tuple(issues)
