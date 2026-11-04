"""Scoped exact accounting: revisions, unknowns and facets stay distinct.

DLV-08/09. No automatic unit conversion, native use inference, or unknown-to-zero.
Inputs are already resolved BoundInputs; original records are never rewritten.
"""
from dataclasses import dataclass
from decimal import Decimal
from . import api
from .model import ExecutionError,canonical,known,number,qualified,unknown

@dataclass(frozen=True,slots=True)
class Total:
    quantity:dict
    contributors:tuple
    issues:tuple
    claim_scope:str='Arithmetic on recorded quantities under the declared rule; not independent native-world verification'

def _ref(ref,anchor):
    return qualified(ref,anchor) if ref.get('binding')=='internal' else ref

def _scope(scope,anchor):
    return {k:[_ref(r,anchor) for r in v] for k,v in scope.items()}

def _key(entry,*,member=True):
    p=entry.record['payload'];anchor=entry.source_package
    values={'owner':_ref(p['owner'],anchor),'resource':p['resource'],'unit':_ref(p['unit'],anchor)}
    if member:values.update(scope=_scope(p['scope'],anchor),interval=p['interval'])
    return canonical(values)

def _pending(code,refs):
    return Total(unknown(code,refs),tuple(refs),(api.Issue(code,{'subjects':list(refs),'qualifiers':[]},tuple(refs)),))

def resource_total(entries,*,entry_kind='bill',rule='s3.aggregation.replace_then_disjoint_members'):
    if rule!='s3.aggregation.replace_then_disjoint_members':return _pending('s3.aggregation_uninterpreted',())
    if any(not isinstance(e,api.BoundInput) or e.record['record_type']!='s3.resource_entry' for e in entries):
        raise ExecutionError('s3.resolved_resource_entries_required')
    selected=[e for e in entries if e.record['payload']['entry_kind']==entry_kind]
    refs=[_ref(e.reference,e.source_package) for e in selected]
    if not selected:return _pending('s3.no_established_resource_population',refs)
    records={e.record['id']:e for e in selected}
    if len(records)!=len(selected):return _pending('s3.duplicate_accounting_occurrence',refs)
    if len({_key(e,member=False) for e in selected})!=1:return _pending('s3.incompatible_resource_units_or_owners',refs)
    replaced=set();children={}
    for e in selected:
        p=e.record['payload']
        if p['aggregation']!={'name':rule,'version':'0.1.0-proposal.3'}:return _pending('s3.aggregation_uninterpreted',refs)
        for prior in p['revises']:
            old=records.get(prior['target'])
            if old is None or _key(old)!=_key(e):return _pending('s3.resource_revision_scope_mismatch',refs)
            if prior['target']==e.record['id']:return _pending('s3.resource_revision_cycle',refs)
            replaced.add(prior['target']);children.setdefault(prior['target'],set()).add(e.record['id'])
    incoming={rid:0 for rid in records}
    for source,targets in children.items():
        for target in targets:incoming[target]+=1
    ready=[rid for rid,n in incoming.items() if n==0];visited=0
    while ready:
        rid=ready.pop();visited+=1
        for target in children.get(rid,()):
            incoming[target]-=1
            if incoming[target]==0:ready.append(target)
    if visited!=len(records):return _pending('s3.resource_revision_cycle',refs)
    # A replacement chain must have one terminal fact, not two competing finals.
    active=[e for e in selected if e.record['id'] not in replaced]
    if not active:return _pending('s3.resource_revision_cycle',refs)
    scopes={}
    for e in active:
        p=e.record['payload'];key=_key(e)
        if key in scopes:return _pending('s3.resource_revision_conflict',refs)
        scopes[key]=e
        if p['quantity']['state']!='known' or p['finality']!='final':return _pending('s3.resource_quantity_or_finality_unresolved',refs)
        val=p['quantity']['value']
        if val['number_type']=='nonfinite' or Decimal(val['text'])<0:return _pending('s3.invalid_resource_amount',refs)
        if not p['scope']['subjects'] or any(r.get('binding')=='unresolved' for r in p['scope']['subjects']):
            return _pending('s3.resource_member_scope_unresolved',refs)
    # A shared member across active entries is overlapping, never automatically additive.
    seen=set()
    for e in active:
        members={canonical(_ref(r,e.source_package)) for r in e.record['payload']['scope']['subjects']}
        if seen.intersection(members):return _pending('s3.resource_member_overlap',refs)
        seen.update(members)
    total=sum((Decimal(e.record['payload']['quantity']['value']['text']) for e in active),Decimal('0'))
    return Total(known(number(total)),tuple(_ref(e.reference,e.source_package) for e in active),())

def exposure_totals(entries):
    """Report each owner/recipient/facet separately; cleanup never subtracts history."""
    groups={}
    for e in entries:
        if not isinstance(e,api.BoundInput) or e.record['record_type']!='s3.exposure_entry':raise ExecutionError('s3.resolved_exposure_entries_required')
        p=e.record['payload'];key=canonical({'owner':_ref(p['owner'],e.source_package),'recipient':_ref(p['recipient'],e.source_package),
            'facet':p['facet'],'policy':p['policy']})
        groups.setdefault(key,[]).append(e)
    result={}
    for key,values in groups.items():
        local={e.record['id']:e for e in values}
        refs=tuple(_ref(e.reference,e.source_package) for e in values)
        if len(local)!=len(values):
            result[key]=_pending('s3.duplicate_accounting_occurrence',refs);continue
        if any(r['target'] not in local or _scope(local[r['target']].record['payload']['scope'],local[r['target']].source_package)!=
            _scope(e.record['payload']['scope'],e.source_package) for e in values for r in e.record['payload']['revises']):
            result[key]=_pending('s3.exposure_revision_scope_mismatch',());continue
        replaced={r['target'] for e in values for r in e.record['payload']['revises']}
        incoming={rid:0 for rid in local};children={}
        for e in values:
            for prior in e.record['payload']['revises']:
                children.setdefault(prior['target'],set()).add(e.record['id'])
        for targets in children.values():
            for target in targets:incoming[target]+=1
        ready=[rid for rid,n in incoming.items() if n==0];visited=0
        while ready:
            rid=ready.pop();visited+=1
            for target in children.get(rid,()):
                incoming[target]-=1
                if incoming[target]==0:ready.append(target)
        if visited!=len(local):
            result[key]=_pending('s3.exposure_revision_cycle',refs);continue
        active=[e for e in values if e.record['id'] not in replaced]
        refs=tuple(_ref(e.reference,e.source_package) for e in active)
        amounts=[e.record['payload']['extent'] for e in active]
        # Policy identifiers alone do not prove additivity of two disclosures.
        # Preserve separate facts until an explicit composition rule is supplied.
        if len(active)>1:
            result[key]=_pending('s3.exposure_composition_unestablished',refs);continue
        if not active or any(q['state']!='known' or 'number_type' not in q['value'] or q['value']['number_type']=='nonfinite' or Decimal(q['value']['text'])<0 for q in amounts):
            result[key]=_pending('s3.exposure_extent_unresolved',refs)
        else:
            result[key]=Total(known(number(sum((Decimal(q['value']['text']) for q in amounts),Decimal('0')))),refs,())
    return result
