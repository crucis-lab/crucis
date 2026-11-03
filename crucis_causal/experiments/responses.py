"""Scoped response meaning/admissibility; no score or reference choice (DLV-08/09)."""
from .model import VERSION,qualified
from .operations import get,read_context

def _output(ref,context):
    read=read_context(context);found=read.resolver.record(ref,read.active_package,read.access,read.limits)
    return found.record['payload'],found.package_id

def graph_adjacency(output,left,right,context):
    """assert/deny/unreported/abstain/unknown for a native scoped graph answer."""
    p,owner=_output(output,context)
    # This API has no explicit abstention-question binding argument. Retain the
    # native abstention, but do not assert it answers an arbitrary queried pair.
    if p.get('output_type')=='abstention':return 'unknown'
    if p.get('output_type')!='graph':return 'unknown'
    b=p['body'];coverage=b['coverage'];domain=get(qualified(b['domain'],owner),context,'s1.domain')
    keys={m['key'] for m in domain['payload']['members']}
    if get(qualified(coverage['domain'],owner),context)['id']!=domain['id']:return 'unknown'
    if domain['payload']['extent']!='s1.full_for_interface':return 'unknown'
    if coverage['extent'] not in ('all_in_domain','listed_only'):return 'unknown'
    for pair in [*coverage['pairs'],*b['links']]:
        if any(get(qualified(pair[side]['domain'],owner),context)['id']!=domain['id'] or pair[side]['key'] not in keys for side in ('left','right')):return 'unknown'
    if left not in keys or right not in keys or (left==right and not coverage['include_same_node']):return 'unreported'
    if b['family']['version']!=VERSION:return 'unknown'
    if b['family']['name'] not in {'s1.dag','s1.cpdag','s1.pag','s1.legacy_graph'}:return 'unknown'
    if coverage['extent']=='listed_only':
        pairs=[(x['left']['key'],x['right']['key']) for x in coverage['pairs']]
        if (left,right) not in pairs and (coverage['pairing']=='ordered' or (right,left) not in pairs):return 'unreported'
    supported={'s1.direct_relation','s1.unresolved_adjacency','s1.bidirected_relation','s1.endpoint_relation','s1.association'}
    for link in b['links']:
        if {link['left']['key'],link['right']['key']}=={left,right}:
            return 'assert' if link['relation']['name'] in supported and link['relation']['version']==VERSION else 'unknown'
    if any(x['relation']['name'] not in supported or x['relation']['version']!=VERSION for x in b['links']):return 'unknown'
    omission=b['omission']['within_coverage']
    return 'deny' if omission=='asserted_absence' else 'unknown' if omission=='unresolved' else 'unreported'

def order_admissible(output,domain,precedences,context):
    """Sequence admissibility versus compatibility of a partial relation."""
    p,owner=_output(output,context)
    if p.get('output_type')!='order':return 'unestablished'
    b=p['body'];d=get(qualified(b['domain'],owner),context,'s1.domain')
    if b['predicate']!={'name':'s1.precedes','version':VERSION}:return 'unestablished'
    if any(get(qualified(m['domain'],owner),context)['id']!=d['id'] for m in b['sequence']):return 'unestablished'
    if any(get(qualified(pair[side]['domain'],owner),context)['id']!=d['id'] for pair in b['pairs'] for side in ('left','right')):return 'unestablished'
    if get(domain,context,'s1.domain')['id']!=d['id']:return 'unestablished'
    keys={m['key'] for m in d['payload']['members']}
    if any(pair[side]['key'] not in keys for pair in b['pairs'] for side in ('left','right')):return 'unestablished'
    if any(a not in keys or c not in keys for a,c in precedences):return 'unestablished'
    if b['representation']=='sequence':
        values=[m['key'] for m in b['sequence']]
        if len(values)!=len(set(values)) or set(values)!=keys:return 'invalid'
        positions={v:i for i,v in enumerate(values)}
        return 'valid' if all(positions[a]<positions[c] for a,c in precedences) else 'invalid'
    adjacency={}
    for pair in b['pairs']:adjacency.setdefault(pair['left']['key'],set()).add(pair['right']['key'])
    def reaches(a,c):
        seen=set();pending=list(adjacency.get(a,()))
        while pending:
            x=pending.pop()
            if x==c:return True
            if x not in seen:seen.add(x);pending.extend(adjacency.get(x,()))
        return False
    if any(reaches(c,a) for a,c in precedences):return 'invalid'
    return 'valid' if all(reaches(a,c) for a,c in precedences) else 'unestablished'
