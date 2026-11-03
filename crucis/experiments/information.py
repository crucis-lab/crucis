"""Explicit information and recipe boundaries; no delivery/reset effects (DLV-08/09)."""
from .api import PlanIssue
from .contracts import DefinitionCheck
from .errors import ServiceError
from .model import contract,qualified
from .operations import get,read_context,bound

def transform_dependencies(spec,context):
    read=read_context(context);active=set();seen=set();issues=[]
    def visit(ref,depth):
        if depth>int(read.limits.max_reference_depth):raise ServiceError('s2.reference_depth_limit')
        found=read.resolver.record(ref,read.active_package,read.access,read.limits);rid=found.record['id']
        if rid in active:issues.append(PlanIssue('s2.transform_predecessor_cycle',evidence=(ref,)));return
        if rid in seen:return
        p=get(ref,context,'s2.transform_spec')['payload'];active.add(rid);seen.add(rid)
        for parent in p['predecessors']:visit(bound(parent,found.package_id,context),depth+1)
        active.remove(rid)
    visit(spec,0)
    return DefinitionCheck(contract('s2.transform_dependency_order'),(spec,),'fail' if issues else 'pass',tuple(issues))

def check_information(policy,presentations,context):
    read=read_context(context);located=read.resolver.record(policy,read.active_package,read.access,read.limits)
    p=get(policy,context,'s2.information_policy')['payload'];issues=[];failed=False;matched=set()
    channels=[]
    for ref in p['channels']['members']:
        found=read.resolver.record(bound(ref,located.package_id,context),read.active_package,read.access,read.limits)
        channels.append((found.record['id'],found.record['payload'],found.package_id))
    for presentation in presentations:
        found=read.resolver.record(presentation,read.active_package,read.access,read.limits)
        presented=get(presentation,context,'s1.presentation')['payload'];native=get(qualified(presented['recipient'],found.package_id),context)['id']
        matches=[]
        for cid,c,owner in channels:
            if c['information']!=presented['information_contract']:continue
            if c['recipient']['state']!='known':
                issues.append(PlanIssue('s2.information_recipient_unestablished'));continue
            if get(qualified(c['recipient']['value'],owner),context)['id']==native:matches.append((cid,c))
        if not matches:
            issues.append(PlanIssue('s2.information_not_permitted',evidence=(presentation,)));failed|=p['channels']['extent']=='complete_for_scope'
        for cid,c in matches:
            matched.add(cid)
            if c['disposition']=='forbidden':issues.append(PlanIssue('s2.forbidden_information',evidence=(presentation,)));failed=True
            elif c['disposition']=='unresolved':issues.append(PlanIssue('s2.information_policy_unestablished'))
    for cid,c,owner in channels:
        if c['disposition']=='required' and cid not in matched:issues.append(PlanIssue('s2.required_information_not_presented'))
    if p['channels']['extent']!='complete_for_scope':issues.append(PlanIssue('s2.information_channel_extent_unestablished'))
    return DefinitionCheck(contract('s2.information_boundary'),(policy,*presentations),'fail' if failed else 'unknown' if issues else 'pass',tuple(issues))
