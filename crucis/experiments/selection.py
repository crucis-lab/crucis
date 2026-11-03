"""Explicit bounded slot resolution, never latest/best selection (DLV-08/09)."""
from .api import PlanIssue,ResolutionDraft
from .errors import ServiceError
from .model import source,scope,index,contract,qualified
from .operations import atomic,get,read_context,bound

SINGLE=contract('s2.explicit_single_selection')

def resolve_slots(requirements,candidates,context):
    def build(tx):
        if not requirements:raise ServiceError('s2.resolution_requirement_required')
        entries=[];selected=[];outstanding=[];issues=[]
        read=read_context(context)
        candidate_records=[(r,get(r,context,'s2.case_revision')) for r in candidates]
        if len({r['id'] for _,r in candidate_records})!=len(candidate_records):raise ServiceError('s2.duplicate_resolution_candidate')
        for ref in requirements:
            found=read.resolver.record(ref,read.active_package,read.access,read.limits);r=found.record;p=r['payload']
            owner=found.package_id;slot_sources=[];target=ref;rule=None
            if r['record_type']=='s2.case_slot':
                rule=p['resolution_rule'];target=bound(p['requirement'],owner,context);slot_sources=[get(qualified(x,owner),context)['id'] for x in p['sources']]
            elif r['record_type']=='s2.requirement':
                for param in p['parameters']:
                    pp=get(qualified(param,owner),context,'s2.parameter_set')['payload']
                    if pp['schema']==contract('s2.params.resolution'):
                        rb=next(b['value'] for b in pp['bindings'] if b['key']=='rule')
                        if rb['state']=='known':rule=rb['value']
            elif r['record_type']=='s2.selection_rule':rule=p['rule']
            else:raise ServiceError('s2.slot_or_resolution_requirement_required')
            matches=[]
            if rule==SINGLE:
                for candidate,record in candidate_records:
                    located=read.resolver.record(candidate,read.active_package,read.access,read.limits)
                    definitions={get(qualified(x,located.package_id),context)['id'] for x in record['payload']['definitions']}
                    if not slot_sources or set(slot_sources)<=definitions:matches.append(candidate)
            if rule!=SINGLE or len(matches)!=1:
                code='s2.resolution_rule_unavailable' if rule!=SINGLE else 's2.ambiguous_resolution' if len(matches)>1 else 's2.required_realization_unavailable'
                issues.append(PlanIssue(code,evidence=tuple(candidates)));outstanding.append(target)
                entries.append({'role':'s2.case','requirement':target,'selected':index([], 'unresolved',subjects=(ref,)),
                    'rule':rule or contract('s2.unresolved_resolution_rule'),'basis':list(candidates)})
            else:
                selected.extend(matches);entries.append({'role':'s2.case','requirement':target,'selected':index(matches,subjects=(ref,)),
                    'rule':rule,'basis':list(candidates)})
        receipt=tx.add('resolution_receipt',{'entries':entries,'candidates':index(candidates,subjects=requirements),
            'scope':scope(*requirements),'source':source(context.author,basis='derived',inputs=candidates)})
        return ResolutionDraft(receipt,tuple(selected),tuple(outstanding)),issues,(receipt,)
    return atomic(context,build)
