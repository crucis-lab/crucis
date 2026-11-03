"""Definition invariants, not causal truth or metric evaluation (DLV-08/09)."""
from dataclasses import dataclass
from .api import PlanIssue,PlanOp,InterpretedValue,FamilyReader
from .errors import ServiceError
from .model import contract,qualified
from .operations import get,read_context

@dataclass(frozen=True,slots=True)
class DefinitionCheck:
    contract:dict; subjects:tuple; result:str; issues:tuple=()

def canonical_id(ref,context):return get(ref,context)['id']
def equivalent(a,b,context):return get(a,context)['id']==get(b,context)['id'] and a['target_type']==b['target_type']
def nested(ref,record,context):
    read=read_context(context);owner=read.resolver.record(ref,read.active_package,read.access,read.limits).package_id
    return qualified(record,owner)

def inspect(reference,context):
    read=read_context(context);found=read.resolver.record(reference,read.active_package,read.access,read.limits)
    record=found.record;p=record['payload'];kind=record['record_type'];issues=[];failed=False
    def issue(code,fail=False):
        nonlocal failed
        issues.append(PlanIssue(code,evidence=(reference,)));failed|=fail
    def scoped(ref):return qualified(ref,found.package_id)
    def resolve(ref,expected=None):return get(scoped(ref),context,expected)
    if kind=='s2.case_revision':
        if p['prior']['state']=='known' and resolve(p['prior']['value'])['id']==record['id']:issue('s2.self_case_revision',True)
        if p['domains']['extent']!='complete_for_scope':issue('s2.case_domain_extent_unestablished')
        if not p['case_key']['namespace'] or not p['case_key']['key']:issue('s2.scoped_case_identity_required',True)
    elif kind=='s2.collection_release':
        if p['membership']['extent']!='complete_for_scope':issue('s2.collection_extent_unestablished')
        cases=[];slots=[]
        for ref in p['membership']['members']:
            member=resolve(ref,'s2.membership');mp=member['payload']
            owner=read.resolver.record(scoped(ref),read.active_package,read.access,read.limits).package_id
            if get(qualified(mp['collection'],owner),context)['id']!=record['id']:issue('s2.membership_wrong_collection',True)
            case=get(qualified(mp['case'],owner),context,'s2.case_revision')['id'];cases.append(case)
            selected=mp['selection_slot']
            slots.append(get(qualified(selected['value'],owner),context)['id'] if selected['state']=='known' else None)
        if len(cases)!=len(set(cases)):
            if p['multiplicity']=='unique_case_revisions':issue('s2.duplicate_case_membership',True)
            elif any(s is None for s in slots) or len(slots)!=len(set(slots)):issue('s2.explicit_distinct_selection_slots_required',True)
    elif kind=='s2.membership':
        resolve(p['case'],'s2.case_revision');collection=resolve(p['collection'],'s2.collection_release')
        if collection['payload']['membership']['extent']=='complete_for_scope' and record['id'] not in {r['target'] for r in collection['payload']['membership']['members']}:
            issue('s2.member_not_in_declared_complete_release',True)
    elif kind=='s2.task_definition':
        resolve(p['response'],'s2.response_contract')
        if not p['scope']['subjects']:issue('s2.task_scope_required',True)
    elif kind=='s2.response_contract':
        roles=[d['role'] for d in p['deliverables']]
        if len(roles)!=len(set(roles)):issue('s2.duplicate_deliverable_role',True)
        if not roles:issue('s2.response_requirement_unestablished')
        resolve(p['coverage'],'s2.coverage_spec')
        for d in p['deliverables']:
            if not d['scope']['subjects']:issue('s2.deliverable_scope_unestablished')
    elif kind=='s2.coverage_spec':
        if p['extent']!='complete_for_scope':issue('s2.partial_reference_coverage')
        if not p['scope']['subjects']:issue('s2.coverage_scope_unestablished')
        if p['domain']['state']=='known':resolve(p['domain']['value'],'s1.domain')
        else:issue('s2.coverage_domain_unestablished')
    elif kind=='s2.reference_definition':
        resolve(p['coverage'],'s2.coverage_spec')
        if p['assertions']['state']!='known':issue('s2.reference_assertions_unavailable')
        else:resolve(p['assertions']['value'])
        # Tiers label the existing claim class; no graph shape proves applicability.
        if not p['applicability']:issue('s2.reference_applicability_unestablished')
    elif kind=='s2.plan_snapshot':
        if p['trials']['extent']!='complete_for_scope':issue('s2.trial_enumeration_unestablished')
        for ref in p['trials']['members']:
            trial=resolve(ref,'s2.trial_slot');owner=read.resolver.record(scoped(ref),read.active_package,read.access,read.limits).package_id
            if get(qualified(trial['payload']['origin_plan'],owner),context)['id']!=record['id']:issue('s2.amended_trial_requires_carry_forward')
    else:issue('s2.definition_family_unregistered')
    return DefinitionCheck(contract('s2.definition_invariants'),(reference,),'fail' if failed else 'unknown' if issues else 'pass',tuple(issues))

def install(registry,implementation):
    kinds=['case_revision','collection_release','membership','task_definition','response_contract','coverage_spec','reference_definition','plan_snapshot']
    def read(ref,context):
        result=inspect(ref,context)
        limits=tuple(PlanIssue('s2.constraint_failed' if result.result=='fail' else i.code,evidence=i.evidence) for i in result.issues)
        value=InterpretedValue(contract('s2.definition_interpretation'),(ref,),(),(),limits)
        return PlanOp('partial' if limits else 'completed',value,diagnostics=limits)
    for kind in kinds:registry.register(FamilyReader(contract('s2.'+kind),implementation,contract('s2.'+kind),contract('s2.definition_interpretation'),read))
