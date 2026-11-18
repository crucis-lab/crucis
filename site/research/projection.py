"""Minimal build-time currentness view; not a scientific adjudication system.

The owning records supply the selected sources and dispositions. Feedback,
attendance and model summaries are not accepted decisions in this adapter.
"""
import hashlib
import json


def fingerprint(source):
    fields={k:source[k] for k in ('id','repository','commit','path','sha256','source_digest','source_state','evidence_level','binding','kind','excerpts','supports','limits','derivation','data_excerpt','source_files') if k in source}
    return hashlib.sha256(json.dumps(fields,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()


def project(sources, bindings):
    current={s['id']:fingerprint(s) for s in sources}
    nodes={n['page']:n for n in bindings['pages']}
    if len(nodes)!=len(bindings['pages']):raise ValueError('Duplicate projection page')
    result={};visiting=set()
    def visit(page):
        if page in result:return result[page]
        if page in visiting:raise ValueError('Cyclic decisive dependencies')
        if page not in nodes:raise ValueError('Unknown decisive dependency')
        visiting.add(page);node=nodes[page]
        changed=[key for key,expected in node['sources'].items() if current.get(key)!=expected]
        upstream=[p for p in node.get('depends_on',[]) if visit(p)['state']!='same-bound-basis']
        result[page]={'state':'needs-reassessment' if changed or upstream else 'same-bound-basis','changed_sources':changed,'affected_predecessors':upstream,'basis_level':node['basis_level'],'limits':'Source currentness only; this is not evidence of entailment, software correctness or scientific acceptance.'}
        visiting.remove(page);return result[page]
    for page in nodes:visit(page)
    return result


def prepare(pages, projected, private_context=None):
    """Refresh proposed work; public selection never consumes private notes."""
    private_context=private_context or {}
    return {'kind':'private proposed preparation; not human signoff or public adoption',
        'exposure':private_context.get('exposure',[]),'disagreement':private_context.get('disagreement',[]),
        'no_findings':private_context.get('no_findings',[]),'promises':private_context.get('promises',[]),
        'open_actions':private_context.get('open_actions',[]),'proposed_work':[
            {'page':p['slug'],'source_state':projected[p['slug']]['state'],'question':p['next_work']['question'],
             'needed':p['next_work']['needed'],'human_contribution':p['next_work']['human_use']}
            for p in pages]}
