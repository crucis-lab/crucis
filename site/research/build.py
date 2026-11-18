"""Build the public research view from explicitly selected editorial inputs.

No runtime evidence collection, scientific approval or publication occurs here.
"""
import hashlib
import html
import json
import re
import shutil
import textwrap
from pathlib import Path
from .projection import project, prepare
from .home import homepage

HERE = Path(__file__).resolve().parent
EDITION = '17 November 2026'
E = lambda x: html.escape(str(x), quote=True)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def link(slug, label):
    return f'<a href="./{E(slug)}.html">{E(label)} →</a>'


def shell(title, body, *, active='', description='', extra=''):
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="{E(description or title)}"><title>{E(title)} · Crucis</title>
<link rel="stylesheet" href="./atlas.css"><script defer src="./atlas.js"></script>{extra}</head>
<body><a class="skip" href="#main">Skip to content</a><header class="mast"><div class="shell">
<a class="brand" href="../index.html"><span aria-hidden="true">✳</span>CRUCIS</a>
<nav aria-label="Main"><a href="./index.html" {'aria-current="page"' if active=='opening' else ''}>Apartment walkthrough</a><a href="./atlas.html#study">The study</a><a href="./evidence.html" {'aria-current="page"' if active=='evidence' else ''}>Evidence record</a></nav></div></header>
<main class="shell" id="main">{body}</main><footer class="footer"><div class="shell"><p>Crucis · Research edition · {EDITION}</p><nav aria-label="Research record"><a href="./history.html">What changed</a><a href="./research-record.html">How the record works</a><a href="./review.html">Questions for review</a></nav></div></footer></body></html>'''


def intro(title, lead, crumb='Research atlas', kicker='A question worth following', atlas_target=''):
    target='./atlas.html'+('#'+atlas_target if atlas_target else '')
    return f'<nav class="breadcrumbs" aria-label="Breadcrumb"><a href="{E(target)}">{E(crumb)}</a><span>{E(title)}</span></nav><div class="intro"><p class="eyebrow">{E(kicker)}</p><h1>{E(title)}</h1><p class="lead">{E(lead)}</p></div>'


def svg(inner, title, *, w=360, h=240):
    return f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="{E(title)}">{inner}</svg>'


def text(x, y, content, cls=''):
    return f'<text x="{x}" y="{y}" text-anchor="middle" class="{cls}">{E(content)}</text>'


def graph(nodes, edges, title, caption='Only the named relationships are shown.'):
    # Node labels may be names or a short label dict. Edges use node indices/names.
    names=[str(n.get('label',n.get('id',''))) if isinstance(n,dict) else str(n) for n in nodes]
    if not names or len(set(names))!=len(names):raise ValueError('Graph requires explicit distinct node labels')
    count=len(names);h=((count+1)//2)*75+25 if count>3 else 200;points=[]
    for i,n in enumerate(names):
        if count<=3:points.append((60+i*240/max(1,count-1),95))
        else:points.append((70+(i%2)*220,50+(i//2)*75))
    marker='arrow-'+digest((title+repr(names)+repr(edges)).encode())[:12]
    marks=f'<defs><marker id="{marker}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0L10 5L0 10" fill="var(--ink)"/></marker></defs>'
    def idx(v):
        if isinstance(v,int) and not isinstance(v,bool) and 0<=v<count:return v
        if str(v) in names:return names.index(str(v))
        raise ValueError('Unknown graph endpoint')
    for edge in edges:
        if isinstance(edge,dict):a,b=edge.get('from',edge.get('source')),edge.get('to',edge.get('target'));style=edge.get('style','')
        else:a,b=edge[:2];style=''
        ai,bi=idx(a),idx(b)
        if ai==bi:raise ValueError('Self-loop needs an explicitly supported teaching view')
        x1,y1=points[ai];x2,y2=points[bi];length=((x2-x1)**2+(y2-y1)**2)**.5;ux=(x2-x1)/length;uy=(y2-y1)/length
        start=55 if len(names[ai])>5 else 30;end=58 if len(names[bi])>5 else 33
        dash='stroke-dasharray="4 4"' if style=='dashed' else ''
        marks+=f'<line x1="{x1+start*ux}" y1="{y1+start*uy}" x2="{x2-end*ux}" y2="{y2-end*uy}" stroke="var(--ink)" stroke-width="1.7" marker-end="url(#{marker})" {dash}/>'
    for (x,y),name in zip(points,names):
        if len(name)>5:
            lines=textwrap.wrap(name,width=12,break_long_words=False)
            marks+=f'<rect x="{x-52}" y="{y-35}" width="104" height="70" rx="8" fill="var(--land)" stroke="var(--line)"/>'
            for i,line in enumerate(lines):marks+=text(x,y+5-(len(lines)-1)*10+i*20,line)
        else:marks+=f'<circle cx="{x}" cy="{y}" r="27" fill="var(--land)" stroke="var(--line)"/>'+text(x,y+5,name)
    return svg(marks,title,h=h)+f'<p class="figure-note">{E(caption)}</p>'


def table_visual(headers, rows, highlight=None, cells=()):
    parts=['<table class="record-table"><thead><tr>']+[f'<th scope="col">{E(h)}</th>' for h in headers]+['</tr></thead><tbody>']
    for i,row in enumerate(rows):
        values=row.get('cells',row.get('values',list(row.values()))) if isinstance(row,dict) else row
        if len(values)!=len(headers):raise ValueError('Table row/header mismatch')
        selected=i in highlight if isinstance(highlight,list) else i==highlight
        parts.append(f'<tr data-highlight="{str(selected).lower()}">'+''.join('<td '+('data-highlight="true"' if [i,j] in cells else '')+'>'+E(v)+'</td>' for j,v in enumerate(values))+'</tr>')
    return ''.join(parts)+'</tbody></table>'


def visual(v):
    kind=v.get('type','states');title=v.get('title',v.get('label','Follow the distinction'));caption=v.get('caption',v.get('note',''))
    if kind not in {'graph','table','record','matrix','worlds','distribution','bars','probabilities','bounds','coverage','split','comparison','mapping','exercise','sequence'}:raise ValueError('Unqualified visual type: '+kind)
    if kind=='graph':
        art=graph(v.get('nodes',[]),v.get('edges',[]),title,caption or 'Arrows run from the proposed cause to what it directly changes.')
    elif kind in ('table','record'):
        art=table_visual(v.get('headers',v.get('columns',['Item','Meaning'])),v.get('rows',[]),v.get('highlight',v.get('highlight_rows',[])))
    elif kind=='matrix':
        labels=v.get('labels',[]);values=v.get('values',[])
        if len(values)!=len(labels) or any(len(row)!=len(labels) for row in values):raise ValueError('Matrix shape does not match labels')
        art=table_visual(['From / to',*labels],[[labels[i],*row] for i,row in enumerate(values)],cells=[[r,c+1] for r,c in v.get('highlight_cells',[])])
        art+='<p class="figure-note">Read the row as the starting variable and the column as the ending variable. A zero means this selected matrix contains no arrow there.</p>'
    elif kind=='worlds':
        worlds=v.get('worlds',[]);art=''
        for i,world in enumerate(worlds):
            art+=f'<p class="figure-label">{E(world.get("title",world.get("label","Possible world "+str(i+1))))}</p>'+graph(world.get('nodes',['A','B','C']),world.get('edges',[]),title,world.get('caption',world.get('note','')))
    elif kind in ('distribution','bars','probabilities'):
        items=v.get('items',v.get('bars',[]));marks=''
        if 'labels' in v:
            if not v['labels'] or len(v['labels'])!=len(v['values']) or ('fractions' in v and len(v['fractions'])!=len(v['values'])):raise ValueError('Probability label/value cardinality mismatch')
            items=[{'label':n,'value':val,'display':str(v.get('fractions',v['values'])[i])} for i,(n,val) in enumerate(zip(v['labels'],v['values']))]
        for i,item in enumerate(items):
            if isinstance(item,dict):label=item.get('label',str(i+1));val=item.get('value',0);value_label=item.get('display',item.get('value_label',str(val)))
            else:label,val=item;value_label=str(val)
            if not isinstance(val,(int,float)) or isinstance(val,bool) or not 0<=val<=1:raise ValueError('Probability view requires a finite value from zero to one')
            x=65+i*230/max(1,len(items)-1);height=val*110
            marks+=f'<rect x="{x-22}" y="{160-height}" width="44" height="{height}" rx="3" fill="var(--known)"/>'+text(x,30,value_label)+text(x,190,label)
        art=svg(marks,title,h=215)
        if v.get('derivation'):art+='<p class="figure-note">'+E('; '.join(v['derivation']) if isinstance(v['derivation'],list) else v['derivation'])+'</p>'
        if v.get('formula'):art+='<p class="figure-note">'+E(v['formula'])+'</p>'
    elif kind=='bounds':
        marks=''
        for i,slot in enumerate(v['slots']):
            x=20+i*84
            marks+=f'<rect x="{x}" y="25" width="65" height="55" rx="6" fill="var(--pending)" stroke="var(--line)"/>'+text(x+32.5,59,slot)
        marks+=text(180,115,'Four intended slots; two values unknown')
        marks+='<line x1="30" x2="330" y1="165" y2="165" stroke="var(--line)"/>'
        lo=30+300*v['lower'];hi=30+300*v['upper']
        marks+=f'<line x1="{lo}" x2="{hi}" y1="165" y2="165" stroke="var(--ink)" stroke-width="5"/>'+text(lo,151,'1/4')+text(hi,151,'3/4')+text(30,194,'0')+text(330,194,'1')
        art=svg(marks,'Four binary outcome slots: one success, one failure, two unknown. Mean lies between one quarter and three quarters.',h=215)
        art+=table_visual(['Completion','Four values','Mean'],[['Lowest possible',', '.join(map(str,v['lower_completion'])),'1/4'],['Highest possible',', '.join(map(str,v['upper_completion'])),'3/4']])
    elif kind=='coverage':
        marks='<path d="M20 115C10 25 115 6 194 30C300 2 350 65 334 153C343 230 185 235 97 205C42 212 12 171 20 115Z" fill="var(--land)" stroke="var(--line)"/>'
        marks+='<rect x="65" y="65" width="226" height="105" rx="12" fill="var(--paper)" stroke="var(--ink)" stroke-dasharray="4 4"/>'+text(178,103,'The declared duty roster')+text(178,131,'Evidence decides each duty')+text(178,198,'The surrounding space needs challenge')
        art=svg(marks,'A bounded declared duty roster inside a larger unmeasured problem space. No area represents coverage.',h=245)
        art+='<ul>'+''.join('<li>'+E(x['title'])+': '+E(x['detail'])+'</li>' for x in v['dimensions'])+'</ul>'
    elif kind in ('split','comparison'):
        art=''
        for side in ('left','right'):
            part=v[side];art+='<p class="figure-label">'+E(part['title'])+'</p>'
            if kind=='comparison' and 'nodes' in part:art+=graph(part['nodes'],part['edges'],part['title'],'')
            elif 'labels' in part and 'values' in part:art+=visual({'type':'probabilities',**part})
            else:art+='<ul>'+''.join('<li>'+E(x)+'</li>' for x in part.get('items',[]))+'</ul>'
    elif kind=='mapping':
        before=v['before'];after=v['after'];h=max(len(before),len(after))*55+45;marks=text(90,20,'Saved names')+text(270,20,'Source names')
        for i,n in enumerate(before):marks+=text(90,65+i*55,n)
        for i,n in enumerate(after):marks+=text(270,65+i*55,n)
        for a,b in v['pairs']:
            i=before.index(a);j=after.index(b);marks+=f'<line x1="130" x2="230" y1="{60+i*55}" y2="{60+j*55}" stroke="var(--line)" stroke-width="1.4"/>'
        art=svg(marks,title,h=h)
    elif kind=='exercise':
        art=f'<div data-exercise><p>{E(v["prompt"])}</p><div class="exercise">'
        for i,option in enumerate(v['options']):
            result=('This choice works. ' if i==v['answer'] else 'This choice does not work. ')+v['explanation']
            art+=f'<button type="button" data-result="{E(result)}" aria-pressed="false">{E(option)}</button>'
        art+='</div><button type="button" data-reveal>Reveal the explanation</button><p class="exercise-result" data-exercise-result aria-live="polite">The explanation is hidden until you choose or reveal it.</p><noscript><p>'+E(v['explanation'])+'</p></noscript></div>'
    else:
        items=v.get('items',v.get('stages',v.get('states',v.get('steps',[]))))
        if not items:items=[{'label':title,'detail':caption}]
        art='<ol class="duty-list">'
        for i,item in enumerate(items):
            if isinstance(item,dict):name=item.get('label',item.get('title',item.get('name','')));detail=item.get('detail',item.get('text',item.get('meaning',item.get('value',''))))
            else:name=str(item);detail=''
            art+=f'<li><span class="number">{i+1}</span><div><h3>{E(name)}</h3><p>{E(detail)}</p></div></li>'
        art+='</ol>'
    return f'<div class="visual"><p class="figure-label">{E(title)}</p>{art}'+(f'<p class="figure-note">{E(caption)}</p>' if caption and kind!='graph' else '')+'</div>'


def source_links(keys, registry):
    for key in keys:
        if key not in registry:raise ValueError('Unbound public source: '+key)
    if not keys:return ''
    return '<div class="route-links">'+''.join(f'<a class="evidence-link" href="./evidence.html#{E(k)}">{E(registry[k]["title"])} ↗</a>' for k in keys)+'</div>'


def chapter(page, registry):
    steps=page['steps'];nav='<nav class="step-nav" aria-label="Page steps">'
    for i,s in enumerate(steps):
        current='aria-current="step"' if i==0 else ''
        nav+=f'<button type="button" data-step-jump="{i}" {current}><span class="step-num">{i+1:02d}</span>{E(s["title"])}</button>'
    nav+='</nav><label class="mobile-step-nav" for="step-select">In this page<select id="step-select">'+''.join(f'<option value="{i}">{i+1}. {E(s["title"])}</option>' for i,s in enumerate(steps))+'</select></label><div class="canvas">';body=''
    for i,s in enumerate(steps):
        sid=s['id'];v=dict(s['visual']);v.setdefault('title',s['title'])
        exercise=v['type']=='exercise'
        body+=f'<section class="scene" data-step="{i}" data-next-label="{E(s.get("next_label","Continue →"))}" id="{E(sid)}"><p class="paper-stamp">{E(s.get("case_label",page["case_label"]))}</p><h2 tabindex="-1">{E(s["title"])}</h2><p class="question">{E(s["question"])}</p><div class="scene-grid">{visual(v)}<div class="scene-copy">'
        if exercise:body+='<div data-before-attempt><h3>Keep the two rules in view.</h3><p>Machine one: X follows the switch; Y copies X.</p><p>Machine two: Y follows the switch; X copies Y.</p></div><div data-after-attempt hidden>'
        body+=''.join(f'<p>{E(p)}</p>' for p in s['body'])+('</div>' if exercise else '')+'</div></div>'+f'<p class="takeaway" {"data-after-attempt hidden" if exercise else ""}><strong>What follows.</strong> {E(s["takeaway"])}</p>'+source_links(s.get('evidence',[]),registry)
        if i==len(steps)-1 and page.get('next_work'):
            work=page['next_work'];body+='<section class="principle"><p class="eyebrow">The remaining work · '+E(work['kind'].replace('-',' '))+'</p><h3>'+E(work['question'])+'</h3><p>'+E(work['already_known'])+'</p>'
            for path in work.get('paths',[]):body+='<details class="record"><summary>'+E(path['label'])+'</summary><p>'+E(path['test'])+'</p><p>'+E(path['yield'])+'</p></details>'
            body+='<p><strong>What would move it forward.</strong> '+E(work['needed'])+'</p><p><strong>Where a person can help.</strong> '+E(work['human_use'])+'</p></section>'
        body+='</section>'
    body+='<div class="canvas-controls"><button type="button" id="back">← Back</button><span class="count" id="step-count" aria-live="polite"></span><button class="next" type="button" id="next">Continue →</button></div><button class="view-all" id="view-all" type="button" aria-pressed="false">Read every step together</button>'
    nxt=page.get('next',{});body+='<nav class="page-handoff" id="page-handoff" aria-label="Continue this investigation"><p>Keep the result of this page in view as you take the next step.</p>'+link(nxt.get('slug','atlas'),nxt.get('label','Return to the research atlas'))+'</nav>'
    if page.get('crosslinks'):body+='<nav class="route-links" aria-label="Connected questions">'+''.join(link(x['slug'],x['label']) for x in page['crosslinks'])+'</nav>'
    head=intro(page['title'],page['lead'],kicker='Follow the '+page['journey']+' question',atlas_target=page['journey'])
    if 'S7' in json.dumps([s['body'] for s in steps]):head+='<p class="note">The auditor is tested too: <strong>S7</strong> is Crucis’s subsystem for checking its own results against separately derived expectations. Its passes apply to named tasks and versions.</p>'
    content=head+'<div class="chapter">'+nav+body+'</div></div>'
    return shell(page['title'],content,extra='<noscript><style>.step-nav,.mobile-step-nav,.canvas-controls,.view-all{display:none}.scene{border-top:1px solid var(--line)}[data-after-attempt]{display:block!important}[data-before-attempt]{display:none}</style></noscript>')


def evidence(registry, bindings):
    body=intro('Follow a statement to its evidence.','Start with the explanation, then inspect the exact source and its limits. A source account, an independently derived expectation and a reproduced software result are different kinds of support.',kicker='The public evidence view')
    body+='''<section class="principle" id="requirements"><h2>What this record gives you</h2><p>In the retained graph accounts, “complete” means a matrix has an entry for every variable pair. It does not mean every pair has an arrow. A matrix filled with zeros can therefore be fully specified.</p><p>A visible statement links here to the source edition it uses. The bundled excerpts let you inspect that basis even if a repository commit has not yet been published. Hashes identify exact bytes; they do not prove that the source is true or that this build reproduced the reported tests.</p><p>Some retained raw research artifacts have not been cleared for redistribution. Their absence limits independent reproduction. A bounded summary does not silently replace them.</p></section>'''
    for key,s in registry.items():
        body+=f'<section class="record" id="{E(key)}"><span class="source-state">{E(s.get("kind",s.get("source_state","editorial derivation")))}</span><h2>{E(s["title"])}</h2><p>{E(s.get("supports",s.get("summary","")))}</p><p class="note">Limit: {E(s.get("limits","No empirical result is claimed by this illustration."))}</p>'
        for excerpt in s.get('excerpts',[]):body+=f'<blockquote>{E(excerpt["text"])}</blockquote>'
        if s.get('derivation'):body+='<div class="principle">'+''.join(f'<p>{E(p)}</p>' for p in s['derivation'])+'</div>'
        if key=='apartment':
            body+='''<section class="principle" id="saved-case"><h3>The saved case</h3><p>This is the earlier simulated 17-variable apartment case. The retained summary identifies the archived result and reference by digest. It does not provide public raw reproduction or substitute the separate five-variable controlled source.</p></section><section class="principle" id="method"><h3>The method behind the proposed diagram</h3><p>The borrowed ordering approach asks a language model about which quantities can affect others, adding a third quantity to help avoid inconsistent directions. Those answers inform an ordering. The paper explains the method; what this particular saved implementation returned is a separate question.</p><p>The local experiment also uses a measurement-based procedure called PC. It checks which associations remain after accounting for other measured quantities, under its own assumptions. The local combination rule keeps the links supplied by that procedure; where their direction is unresolved, it looks for an ordering in the language-model proposal.</p><p>In the archived code, the measurement procedure runs before the model queries. The teaching sequence shows their proposed diagrams separately to distinguish their evidence; “earlier proposal” means before the combined final answer, not before measurements were analyzed.</p><p>The retained local implementation account binds <code>harness/agents/vashishtha.py</code> at research revision <code>27a6394accf473dccedd46d4162743d4e283af3e</code>, SHA-256 <code>3b533967fc280ffa88bbaed3721af21bf378e557f0c0ac1b6fb9ae71b9cb4865</code>. This summary does not reproduce the raw archived run.</p><p><a href="https://arxiv.org/html/2310.15117v2#S4">Read the borrowed method’s derivation in §4</a></p></section><section class="principle" id="intermediate"><h3>The earlier proposal</h3><p>The first view isolates heat exposure → first opening time. The later view also includes first opening time → window-open fraction. The extra arrow was already in the earlier proposal; the first view had deliberately omitted it.</p></section><section class="principle" id="final"><h3>The saved final diagram</h3><p>Of those two selected relationships, the final view no longer contains heat exposure → first opening time. It contains window-open fraction → first opening time, opposite to the pictured source link. This is a specific structural conflict, not a cooling-effect estimate.</p></section>'''
        body+='<details><summary>Exact source and version</summary>'
        meta={k:s[k] for k in ('repository','commit','path','sha256','source_digest','source_state','remote_publication_verified','evidence_level','binding') if k in s}
        body+='<pre>'+E(json.dumps(meta,indent=2,ensure_ascii=False))+'</pre>'
        if s.get('optional_repository_url'):body+=f'<p><a href="{E(s["optional_repository_url"])}">Repository source at the recorded revision</a> · Remote availability was not verified for this edition; the excerpt above is the primary access.</p>'
        for p in s.get('papers',[]):body+=f'<p><a href="{E(p["url"])}">{E(p["title"])}</a></p>'
        body+='</details></section>'
    body+='<nav class="route-links"><a href="./evidence-record.json">Machine-readable evidence view</a><a href="./scope.json">Question-to-responsibility crosswalk</a><a href="./atlas.html">Return to the atlas →</a></nav>'
    return shell('Evidence record',body,active='evidence')


def history_page():
    return shell('What changed, and why?',intro('What changed, and why?','A new explanation should show what changed in its basis. It should not rewrite the old evidence or invent a meeting that caused the improvement.',kicker='Dated research history')+'''<ol class="timeline"><li><time>Earlier local investigations</time><h3>Separate questions were worked through</h3><p>The apartment, source-warrant, output-identity and controlled-case walkthroughs developed different parts of the argument. Their private snapshots are preserved. They are not represented as earlier public releases here.</p></li><li><time>16 November 2026 · retained committed source edition</time><h3>Controlled references and implementation checks broadened</h3><p>The selected source accounts cover three fixed mechanisms, scoped proofs and controlled measurement paths. Their stated limits remain part of this record.</p><a href="./evidence.html#diverse-build">Read the retained source account</a></li><li><time>17 November 2026 · this candidate</time><h3>A connected research homepage</h3><p>The main homepage now connects the apartment decision, five audit questions, inline investigations and the study rationale. It separates known reasoning, exact-path qualification and research choices. Auditor coverage guides the case space; it does not determine statistical sample size. Old pending labels are not generalized to all current work. No human endorsement or new empirical result is created by this editorial update.</p></li></ol><section class="principle"><h2>After the next contribution</h2><p>A future approved public entry will identify the previous conclusion, the new contribution, the changed reasoning and any remaining disagreement. Private notes can support an investigation without being published. Until an actual contribution and its public use are recorded, there is no invented session progress to display.</p><nav class="route-links"><a href="./research-record.html">See the update rules →</a><a href="./retrace-change.html">Try a concrete correction →</a></nav></section>''')


def review_page(pages, projected):
    body=intro('Where could a conversation change the research?','Start from a decision that survives our own source reading and tests. Bring the alternatives and the best counterexample we have, so the discussion can improve the answer.',kicker='Focused human investigation')
    by_slug={p['slug']:p for p in pages}
    for slug in ('comparison-task','validate-coverage','reference-boundary'):
        page=by_slug[slug];work=page['next_work']
        body+='<section class="record"><p class="eyebrow">'+E(work['kind'].replace('-',' '))+'</p><h2>'+E(work['question'])+'</h2><p><strong>Where we are.</strong> '+E(work['already_known'])+'</p><p><strong>What would move it forward.</strong> '+E(work['needed'])+'</p><p><strong>Useful contribution.</strong> '+E(work['human_use'])+'</p>'
        for path in work.get('paths',[]):body+='<details><summary>'+E(path['label'])+'</summary><p>'+E(path['test'])+'</p><p>'+E(path['yield'])+'</p></details>'
        if projected[slug]['state']!='same-bound-basis':body+='<p class="note">This question’s source basis has changed. Reassess it before relying on the earlier explanation.</p>'
        body+=link(slug,'Work through the question first')+'</section>'
    body+='<section class="principle"><h2>Use the available time well.</h2><p>For ten minutes, choose one decisive counterexample or premise. For twenty-five, compare two live alternatives and agree the next evidence. With a full hour, reconstruct the argument, test several branches and assign a bounded follow-up. Introduce only the context that the selected question needs.</p><p>A return session starts with what changed since that person last saw the question. TA roles and specialist fit depend on actual expertise and agreement; no roles or appointments are assigned by this page.</p><p class="note">These entries are generated from the same current question records as the journeys. They are selected review focuses, not a claim that every other question is resolved.</p><nav class="route-links"><a href="./research-record.html">How contributions enter the record →</a><a href="./review-questions.json">All current review questions</a><a href="./atlas.html">Choose another territory →</a></nav></section>'
    return shell('Questions for review',body)


def record_page():
    body=intro('How does new work change the record?','A conversation can suggest a better explanation. The explanation still needs evidence, a decision and—where relevant—a demonstrated fix.',kicker='From a private note to a public improvement')
    states=[('Keep the observation','Record what was actually said or found, what the person saw and any promise or follow-up. Private correspondence stays private.'),('Turn it into a checkable question','Separate advice from evidence. Identify which claim or obligation it challenges, alternatives and the work that could decide it.'),('Resolve or retain the disagreement','Source reading, proof, an experiment or owner judgment may be needed. Agreement and a long meeting are not proof; no-finding outcomes are preserved.'),('Verify the change','An implementation suggestion goes to its owner. A claimed fix needs the actual changed version and appropriate recheck, not just its author’s assurance.'),('Release the permitted improvement','Generate an updated public explanation from approved findings. Attribute private feedback only with agreement; public scientific adoption and disclosure are separate decisions.')]
    body+='<ol class="duty-list">'+''.join(f'<li><span class="number">{i+1}</span><div><h3>{E(t)}</h3><p>{E(p)}</p></div></li>' for i,(t,p) in enumerate(states))+'</ol>'
    body+='''<section class="principle"><h2>What updates automatically?</h2><p>The private preparation process can refresh the current question, evidence delta and proposed agenda after a recorded update. It must retain previous exposure, promises, disagreement and open actions. It cannot invent attendance, consent, agreement, scientific acceptance or a completed fix.</p><p>The public site is an edition generated from selected records, not a window into private activity. New private feedback does not automatically change public scientific status. An accepted correction reopens conclusions that depend on it; unaffected conclusions need a reason for remaining applicable.</p><nav class="route-links"><a href="./retrace-change.html">Follow an affected conclusion →</a><a href="./history.html">Inspect the dated history →</a></nav></section>'''
    return shell('How the research record works',body)


def operations_page(registry):
    body=intro('Did the attempt stop—or did we lose sight of it?','Suppose we ask a causal-discovery system for a graph. Our collector stops waiting. That tells us about the collector; by itself it does not tell us whether the system finished.',kicker='A worked recovery contrast')
    items=[('Before the request','If custody establishes that no native effect occurred, local preparation may resume under its original authority. A plan is not a dispatched request.'),('After a request, before a known answer','An unknown remote effect is not safe to treat as “nothing happened.” Reconcile what was issued, observed and settled before considering another native attempt.'),('Recover the same returned bytes','Authenticated recovery of an answer already returned at the declared boundary can restore the original occurrence. Keep the earlier hold and later recovery linked.'),('Generate a new answer','Asking the system again creates a new attempt, with new exposure and resource effects. It must not silently replace the earlier missing result or become another independent scientific case.')]
    body+='<ol class="duty-list">'+''.join(f'<li><span class="number">{i+1}</span><div><h3>{E(t)}</h3><p>{E(p)}</p></div></li>' for i,(t,p) in enumerate(items))+'</ol>'
    body+='''<section class="principle"><h2>Why this changes the comparison</h2><p>If difficult attempts disappear whenever collection fails, the remaining score can look better for the wrong reason. Retain intended cases and their actual dispositions. A deadline outcome, a verified native failure, a missing capture and an explicit abstention need different evidence.</p><p>This is an authored recovery example, not a report of a newly executed native run. Actual retries, cutoffs and resource limits belong to the applicable execution contract; this site adopts no new study policy.</p><nav class="route-links"><a href="./comparison-outcome.html">See how missing outcomes enter a comparison →</a><a href="./retrace-change.html">Follow the recovery history →</a></nav></section>'''+source_links(['framework','native-policy'],registry)
    return shell('Execution and recovery',body)


def build_research(out, *, source_revision):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    data=json.loads((HERE/'journeys.json').read_text(encoding='utf-8'))
    pages=data['pages'];sources=json.loads((HERE/'evidence-sources.json').read_text(encoding='utf-8'))
    registry={s['id']:s for s in sources['sources']}
    if len(registry)!=len(sources['sources']):raise ValueError('Duplicate source keys')
    for s in registry.values():
        for excerpt in s.get('excerpts',[]):
            if digest(excerpt['text'].encode())!=excerpt['sha256']:raise ValueError('Changed bound excerpt: '+s['id'])
    for name in ('atlas.css','atlas.js','opening.css','opening.js'):shutil.copyfile(HERE/name,out/name)
    opening=(HERE/'opening.html').read_text(encoding='utf-8')
    home=shell('Can we trust an answer about cause and effect?',homepage(registry,pages),active='atlas',description='From a hot apartment to a bounded research program: what Crucis must check, what the evidence establishes, what remains open and how we design the study.')
    outputs={'index':opening,'atlas':home,'evidence':evidence(registry,sources),'history':history_page(),'research-record':record_page(),'operations':operations_page(registry)}
    view_bindings=json.loads((HERE/'view-bindings.json').read_text(encoding='utf-8'))
    projected=project(sources['sources'],view_bindings)
    outputs['review']=review_page(pages,projected)
    proposal=prepare(pages,projected)
    (out/'review-questions.json').write_text(json.dumps({'kind':'public review-entry projection; no private session context','questions':proposal['proposed_work']},indent=2,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')
    for page in pages:
        if page['slug'] in outputs:raise ValueError('Duplicate route')
        content=chapter(page,registry)
        outputs[page['slug']]=content
    public_statements=[];node_map={n['page']:n for n in view_bindings['pages']}
    for slug,content in outputs.items():
        if projected[slug]['state']=='needs-reassessment':
            content=re.sub(r'(<main\b[^>]*>)',r'\1<p class="takeaway" role="alert">The evidence behind this earlier explanation has changed. Its conclusion needs reassessment; do not treat it as a current finding.</p>',content,count=1)
        ordinal=[0]
        def bind_paragraph(match):
            attrs,inner=match.groups();ordinal[0]+=1
            found=re.search(r'\bid="([^"]+)"',attrs);anchor=found.group(1) if found else 'statement-'+str(ordinal[0])
            selected=re.search(r'\bdata-evidence="([^"]*)"',attrs)
            keys=selected.group(1).split() if selected else list(node_map[slug]['sources'])
            if any(k not in node_map[slug]['sources'] for k in keys):raise ValueError('Unbound paragraph evidence: '+slug)
            plain=html.unescape(re.sub(r'<[^>]*>','',inner));public_statements.append({'page':slug+'.html','anchor':anchor,'text':plain,'text_sha256':digest(plain.encode()),'evidence':keys,'kind':'paragraph-level editorial binding; source selection is not entailment proof'})
            return '<p'+attrs+('' if found else ' id="'+anchor+'"')+'>'+inner+'</p>'
        content=re.sub(r'<p\b([^>]*)>(.*?)</p>',bind_paragraph,content,flags=re.S)
        (out/(slug+'.html')).write_text(content,encoding='utf-8',newline='\n')
    (out/'evidence-record.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    shutil.copyfile(HERE/'scope.json',out/'scope.json')
    (out/'view-status.json').write_text(json.dumps(projected,indent=2)+'\n',encoding='utf-8',newline='\n')
    bindings=[]
    for p in pages:
        for step in p['steps']:
            for i,statement in enumerate([*step['body'],step['takeaway']]):
                bindings.append({'page':p['slug']+'.html','anchor':step['id'],'statement_index':i,'text':statement,'text_sha256':digest(statement.encode()),'evidence':step['evidence'],'case_kind':step.get('case_kind',p['case_kind']),'kind':'editorial statement binding, not an issued scientific finding'})
    (out/'statement-bindings.json').write_text(json.dumps({'statements':bindings,'public_paragraphs':public_statements,'route_aliases':{'../index.html':'atlas.html'},'limits':'Bindings expose source selection; review is still needed to judge entailment and sufficiency.'},indent=2,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')
    content_bindings={p.name:digest(p.read_bytes()) for p in sorted(out.iterdir()) if p.is_file() and p.name!='edition.json'}
    (out/'edition.json').write_text(json.dumps({'edition':'2026-11-17','source_commit':source_revision,'kind':'public_research_projection_not_a_scientific_certificate','evidence_cutoff':'See individual source records; not a live monitor','files':content_bindings},indent=2)+'\n',encoding='utf-8',newline='\n')
    return len(outputs)
