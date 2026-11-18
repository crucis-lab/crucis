"""A single research-program overview; deeper investigations retain their routes.

All scientific statuses are bounded editorial accounts of selected source records.
No user interaction adopts policy, issues a scientific finding or runs a study.
"""
import html
import math

E = lambda s: html.escape(str(s), quote=True)


def p(copy, *evidence, cls=''):
    return '<p'+(' class="'+E(cls)+'"' if cls else '')+(' data-evidence="'+E(' '.join(evidence))+'"' if evidence else '')+'>'+E(copy)+'</p>'


REGIONS = [
    dict(id='reference', title='Can we trust the answer key?', short=['Trust the', 'answer key'],
         example='An answer looks wrong only if our answer key is justified for this exact question.',
         known='Beyond the apartment, a separate controlled example uses five quantities. We know the links used to construct that simulation, so we can derive whether a proposed link agrees with those rules.',
         check='For an actual audit, show that it used the matching source edition, quantities and question. Tracking a version is necessary; it does not prove the reference is appropriate.',
         question='Where would a new task or a stronger claim exceed the controlled reference we already know how to justify?',
         why='An answer can match the source even when the evidence shown to the system leaves other explanations possible. Those are different achievements.',
         next='Take one claimed arrow. Write the allowed explanations and what evidence would exclude each alternative. If alternatives still disagree, preserve that limit.',
         human='A causal-methodology reviewer can challenge the allowed explanations or an assumption that excludes one.',
         routes=[('reference-key','Start with the answer key'),('reference-evidence','Try two competing explanations'),('reference-boundary','Examine the remaining choice')],
         sources=['copilot-card','diverse-reference','reference-choice','teaching-only']),
    dict(id='answers', title='Which answer did we check?', short=['Select and read', 'the actual answer'],
         example='An early diagram, a revised diagram and a report can disagree. A correct calculation on the wrong one still misleads.',
         known='Beyond the apartment, a separate controlled example uses five quantities. Its saved revised diagram proposes no links, although the simulation was built with a direct link between two of them. Interpreting the saved output as the proposed diagram gives an expected disagreement.',
         check='The expected disagreement is a worked result. The exact software route still needs its own records of selection, quantity mapping, interpretation and reporting; a different fixture cannot substitute.',
         question='How should an extension handle a system that returns probabilities instead of the graph used in the current study?',
         why='Changing probabilities into a hard answer can add a decision the system never made. Leaving that choice hidden can change the comparison.',
         next='Trace the actual returned product before choosing a shared task. Preserve code-supplied defaults, unavailable results and any later selection separately.',
         human='A reviewer can challenge the mapping or show that the proposed task misreads what a system actually offers.',
         routes=[('answer-selected','Follow the selected output'),('answer-meaning','Work through its meaning'),('answer-boundary','Check what counts as a return')],
         sources=['copilot-card','causaliq-card','native-policy','native-stage','study-design']),
    dict(id='comparison', title='What makes a comparison fair?', short=['Make the comparison', 'answer a useful question'],
         example='A diagram and a probability forecast need not answer the same question. Putting their scores side by side does not make them comparable.',
         known='The study plan chooses controlled information comparisons within a workflow, with Copilot’s automatic graph workflow primary. Delivery, source accuracy and evidential support remain distinct; a missing capture differs from an explicit refusal.',
         check='The actual products and information available to each system must fit the chosen task. Then the same declared outcome and missing-result rules must be applied to every intended attempt.',
         question='Do the proposed outcomes distinguish useful use of information from misleading overreach, without hiding failures or missing results?',
         why='An outcome rule can reward an unhelpful answer or conceal an important failure. Extra runs cannot repair a rule that measures the wrong achievement.',
         next='Propose one study claim, eligible case mixture and outcome policy. Challenge it with an error, a partial answer, a refusal and an unavailable result before freezing it.',
         human='A methods or statistics reviewer can identify a difference that defeats the claim, or a policy that rewards the wrong behavior.',
         routes=[('comparison-task','Choose the scientific question'),('comparison-outcome','Work through outcome rules'),('comparison-population','Decide what cases can tell us')],
         sources=['native-policy','copilot-card','causaliq-card','study-path','study-design','eligibility']),
    dict(id='reconstruction', title='Can a reader retrace the finding?', short=['Retrace and', 'correct the finding'],
         example='“The system missed a link” should lead to the selected answer, the applicable reference and the calculation—not just another summary.',
         known='The view separates selected sources, derived expectations and software accounts. The update design preserves disagreement and no-new-finding outcomes.',
         check='A released finding needs its actual report and connected evidence. Public excerpts can support a bounded argument while missing raw artifacts still limit reproduction.',
         question='What public evidence is enough for the level of checking we promise, and what must reopen when a premise changes?',
         why='A changed input may invalidate one result without invalidating every other result. Private feedback must not silently become public endorsement.',
         next='Ask a fresh reader to recover one conclusion and its limits. Then change one decisive premise and check affected and unaffected conclusions separately.',
         human='A fresh reader can expose a missing step, inaccessible basis or unintended stronger claim. The research owner decides adoption and attribution.',
         routes=[('retrace-finding','Retrace one result'),('retrace-change','Follow a correction'),('retrace-boundary','Inspect the public boundary')],
         sources=['framework','framework-map','apartment','teaching-only']),
    dict(id='validation', title='Could the checker still mislead us?', short=['Challenge', 'Crucis itself'],
         example='A checker that rejects everything avoids some false claims while recognizing no useful answers. We must test both kinds of mistake.',
         known='Committed source accounts report controlled checks of supported answers, errors and weaker evidence. A newer joined path connects measurement, decisions, reports and auditor checks in a narrow fixed-source scope.',
         check='A pass belongs to its named inputs, assumptions and software version. Individual saved outputs and new uses need their own qualification; fixed controls are not an overall correctness rate.',
         question='Which important misleading behavior could still pass the duties and controls we have chosen?',
         why='A complete check of a declared finite space can still omit an important kind of system, question or interaction. The boundary itself needs challenge.',
         next='Try to construct an auditor that passes our controls but makes one important wrong judgment. Add the missing duty or test only after deriving its expected answer independently.',
         human='Reviewers can propose escaping cases, challenge an expected answer or identify an unsupported new kind of system.',
         routes=[('validate-cases','Challenge four kinds of result'),('validate-coverage','Inspect the coverage boundary'),('validate-extension','Consider an unfamiliar system')],
         sources=['s7','diverse-reference','diverse-build','joined-checks','framework-map']),
]

# Proposed next work is classified by what could actually decide it. These links
# open the relevant investigation; they neither adopt policy nor dispatch a run.
ACTIONS = {
 'reference':dict(check_kind='Check the existing evidence',check_action='Verify which reference, quantity names and question the actual audit consumed. Recover existing records first; repeat an execution only if the needed record cannot be recovered.',check_link=('reference-key','Trace the reference actually used'),
   research_kind='Methodological analysis for a stronger or new claim',research_action='Controlled references are already the chosen starting point for this study. Examine a new assumption or competing explanation when extending the claim beyond that scope; more repeats do not justify an unsupported assumption.',research_link=('reference-boundary','Work through the reference boundary'),
   done='Move on when the exact-use check is evidenced and the chosen claim states its reference assumptions. Reopen if the source, quantities, task or assumptions change.'),
 'answers':dict(check_kind='Qualify the saved-output route',check_action='Use the saved answer and execution records to test selection, names, meaning and reporting together. This check usually needs the existing evidence, not another paid model answer.',check_link=('answer-selected','Inspect the selected-output check'),
   research_kind='Methodological extension, separate from the current comparison',research_action='The current study plan uses Copilot’s automatic graph workflow as primary. A shared comparison with a probability-returning system needs a separately justified task; it is not a prerequisite for the first matched Copilot comparison.',research_link=('answer-meaning','Examine a different answer format'),
   done='Close the named output check when the connected records demonstrate the expected result. Reopen the interpretation for a changed output format, selected field, quantity map or claim.'),
 'comparison':dict(check_kind='A bounded pilot, then study runs',check_action='After fixing the task and outcome rules, use a small, bounded pilot with the actual system. Learn which attempts finish, which answers can be judged, what they cost and how much outcomes vary. Review study size and freeze the design before seeing main-study outcomes.',check_link=('comparison-population','Follow the pilot-to-study decision'),
   research_kind='Design review before execution',research_action='The current direction compares controlled information conditions within a workflow. Challenge whether the chosen outcomes detect useful improvement and misleading overreach. Set failure, missing-result and dependence rules before using the pilot to size the study.',research_link=('comparison-outcome','Work through the outcome rules'),
   done='Proceed from reviewed rules to the bounded pilot, then review size and uncertainty before the main study. Revise the method if pilot evidence exposes an inapplicable outcome or unresolved ambiguity; do not merely add runs.'),
 'reconstruction':dict(check_kind='A reporting and correction rehearsal',check_action='Take an actual report, recover its exact supporting records, then change one decisive premise. Check that affected conclusions reopen and unrelated conclusions remain intact. Model calls are not needed for this rehearsal.',check_link=('retrace-change','Inspect the correction rehearsal'),
   research_kind='Fresh-reader and disclosure review',research_action='State what a public reader should be able to reconstruct. Have a fresh reader try it with the proposed public evidence, then repair missing steps or narrow the claim. Review attribution separately from scientific adoption.',research_link=('retrace-boundary','Check the public evidence boundary'),
   done='The release is ready at its promised level when a reader can retrace the claim and correction, with access limits explicit. Reopen when the basis, report or released evidence changes.'),
 'validation':dict(check_kind='Execute independently specified controls',check_action='Compare this auditor version with the independently derived positive, error, unsettled and wrong-field expectations, including the connected report. Preserve failures and retest fixes; no new native-system answer is required for fixed controls.',check_link=('validate-cases','Inspect the decisive auditor controls'),
   research_kind='Adversarial analysis, then targeted iteration',research_action='Construct an important misleading auditor that could still pass the current checks. If it succeeds, add a justified duty or separating control and rerun it. Real pilot or study outputs can reveal a new format or failure that calls for the same analysis.',research_link=('validate-coverage','Search for an escaping failure'),
   done='A pass closes only the declared duties and versions supported by those controls. Extend the scope when a counterexample or new use exposes a gap; ordinary development need not wait for an expert to endorse it.')
}


def task_detail(registry):
    source=registry['apartment-task'];data=source['data_excerpt']
    rows=data['values'];columns=data['columns']
    expected=['D3_time_to_first_window_open_min','D4_mean_window_open_fraction','D5_ventilation_ach_open','O3_heat_exposure_degmin']
    if [c['native_name'] for c in columns]!=expected or [c['column_index'] for c in columns]!=[9,10,11,15]:raise ValueError('Changed task-column meaning needs a revised explanation')
    if data['member']!='x.npy' or data['value_channel']!=0 or data['row_indices_zero_based']!=list(range(5)):raise ValueError('Changed task selection needs a revised explanation')
    if len(rows)!=5 or len(columns)!=4 or any(len(row)!=4 for row in rows):raise ValueError('Unexpected released table selection')
    if any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) for row in rows for v in row):raise ValueError('Non-finite released table value')
    graph_url=source['source_files']['graph.json']['url'];data_url=source['source_files']['observations.npz']['url']
    body='<details class="task-grounding" id="apartment-task"><summary>Open the actual CausalArena task, its structure and saved data</summary><div class="task-grounding-body"><p class="eyebrow">CausalArena · Apartment heat exposure, shading and AC use</p><h3>A released simulation and its stated reference.</h3>'
    body+=p('The original scenario asks how exterior shading changes heat exposure and air-conditioning electricity use. Window opening and airflow are part of that larger system. We use that part to introduce the audit; opening at 8 AM versus 10 AM is our follow-on question, not a completed benchmark experiment.','apartment-task')
    roles=[('The available table','The released observation-only file contains 1,000 simulated rows and 17 named quantities. They include weather, shading, opening behavior, airflow and heat exposure.'),
           ('The discovery task','Recover the causal relationships. In the archived method, a numerical procedure used prepared data; a language model received names and domain context. This original table was not shown directly to the language model.'),
           ('The independent comparison','The same archive stores a reference graph and quantity names. To judge the program’s answer, we must check that this reference applies and that the selected output is interpreted correctly.')]
    body+='<ol class="task-structure">'+''.join('<li><span>'+str(i+1)+'</span><div><h4>'+E(title)+'</h4>'+p(copy,'apartment-task','apartment')+'</div></li>' for i,(title,copy) in enumerate(roles))+'</ol>'
    body+='<h4>Read the four quantities before reading their values.</h4><dl class="task-columns">'
    definitions=[('Opening delay','Time to the first window opening, originally in minutes after sunrise. It is not a clock time.'),('Window opening','The mean fraction of the window that is open in the late morning.'),('Airflow','Ventilation while the window is open, originally expressed as air changes per hour.'),('Heat exposure','How far and how long temperature exceeds 27°C, accumulated from 6 AM until 2 PM. It is not average room temperature from 8 AM until 12 PM.')]
    body+=''.join('<div><dt>'+E(label)+'</dt><dd>'+E(copy)+'</dd></div>' for label,copy in definitions)+'</dl>'
    body+=p('The exported columns were rescaled to a common numerical scale. Zero is near a column’s average; negative values are below it and positive values above it. These displayed values are therefore not minutes, percentages or temperatures.','apartment-task',cls='task-scale')
    body+='<div class="task-table-scroll" tabindex="0" role="region" aria-label="First five released rows; scroll horizontally on a narrow screen"><table class="record-table task-table"><caption>First five released simulated rows · four of 17 columns · values rounded to three decimals</caption><thead><tr><th scope="col">Stored row</th>'+''.join('<th scope="col">'+E(c['label'])+'</th>' for c in columns)+'</tr></thead><tbody>'
    for i,row in enumerate(rows):body+='<tr><th scope="row">'+str(i+1)+'</th>'+''.join('<td>'+format(v,'.3f')+'</td>' for v in row)+'</tr>'
    body+='</tbody></table></div><p class="task-scroll-note">On a narrow screen, scroll the table sideways to see every column.</p>'
    body+=p('These are the first five stored rows in order, not selected successes or paired 8 AM/10 AM interventions. The task drawing is an explanatory view; the table excerpt comes from the released file, whose digest matches the retained benchmark file.','apartment-task')
    body+='<div class="task-next"><h4>What would answer the opening-time question?</h4>'+p('First define the intervention and temperature outcome, and establish that the available simulator or measurements can represent them. A separately justified analysis or experiment would then be needed. That work is not required merely to check an arrow in the already saved answer.','apartment-task','teaching-only')+'<a href="./index.html">Follow the saved answer and the separate decision question →</a></div>'
    body+='<nav class="route-links"><a href="'+E(graph_url)+'">Original task specification ↗</a><a href="'+E(data_url)+'">Released observation file ↗</a><a href="./evidence.html#apartment-task">Exact selection and source record ↗</a><a href="https://arxiv.org/abs/2609.11897">CausalArena paper ↗</a></nav>'
    body+=p('CausalArena: Zi-Rong Li, Si-Yang Liu, Tian-Zuo Wang and Han-Jia Ye. Dataset release declares CC BY 4.0. This view selects five rows and four columns, shortens labels and rounds displayed values; exact selections and source versions remain in the evidence record.','apartment-task',cls='task-attribution')
    return body+'</div></details>'


def landscape():
    # Geometry is explicitly schematic. Selection is ink-outline emphasis, not success.
    positions=[(151,105,123,70),(433,105,130,70),(299,268,232,75),(147,435,126,75),(437,435,130,75)]
    shapes=''
    for region,(x,y,rx,ry) in zip(REGIONS,positions):
        key=region['id'];a,b=region['short']
        d=f'M{x-rx},{y}C{x-rx},{y-ry} {x+rx*.7},{y-ry*1.1} {x+rx},{y-ry*.1}C{x+rx*1.1},{y+ry*.8} {x-rx*.8},{y+ry*1.1} {x-rx},{y}Z'
        shapes+=f'<a href="#{key}" data-home-select="{key}" aria-label="{E(region["title"])}"><g data-home-land="{key}"><path d="{d}"/><text x="{x}" y="{y-4}">{E(a)}</text><text x="{x}" y="{y+20}">{E(b)}</text></g></a>'
    return '<svg viewBox="0 0 600 550" role="group" aria-label="Five connected audit questions. Select a region to explore it here. Areas are schematic."><path class="land-outer" d="M18 245C0 20 145 0 293 18C515-10 601 80 578 265C613 472 485 551 294 525C92 550 0 439 18 245Z"/>'+shapes+'</svg>'


def apartment_art(kind):
    if kind=='room':
        return '''<svg viewBox="0 0 540 310" role="img" aria-label="Apartment with an open window. Compare opening at 8 AM or 10 AM; the benchmark does not supply a measured result for this decision.">
<path d="M42 252V49H462V252Z" class="room-wall"/><path d="M42 252L109 207H462M109 207V49" class="line"/>
<path d="M136 75H257V177H136Z" class="window"/><path d="M196 76V176L235 157V90Z" class="window-open"/>
<path d="M219 111C270 86 278 123 309 102M219 138C264 112 286 156 322 131" class="air"/>
<path d="M334 205V167Q334 159 342 159H414Q423 159 423 169V206M327 207H430M341 207V220M415 207V220" class="line"/>
<circle cx="390" cy="85" r="19" class="sun"/><path d="M390 54V48M390 116V122M359 85H353M421 85H427" class="line"/>
<text x="135" y="285">A hot apartment</text><text x="393" y="285">8 AM or 10 AM?</text></svg>'''
    if kind=='arrows':
        return '''<svg viewBox="0 0 540 310" role="img" aria-label="Simplified source path: opening time affects opening fraction, which affects airflow, which affects heat exposure. Other relationships omitted.">
<defs><marker id="home-cause" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0L10 5L0 10Z" fill="currentColor"/></marker></defs>
<rect x="20" y="45" width="210" height="75" rx="12"/><rect x="310" y="45" width="210" height="75" rx="12"/>
<rect x="310" y="195" width="210" height="75" rx="12"/><rect x="20" y="195" width="210" height="75" rx="12"/>
<path d="M235 83H301M415 125V185M305 233H239" class="causal-arrow" marker-end="url(#home-cause)"/>
<text x="125" y="88">Opening time</text><text x="415" y="77">How much the</text><text x="415" y="101">window is open</text>
<text x="415" y="240">Airflow</text><text x="125" y="240">Heat exposure</text></svg>'''
    return '''<svg viewBox="0 0 540 310" role="img" aria-label="Two separate checks: does the explanation match the source, and does opening earlier actually improve the desired temperature outcome? Neither result substitutes for the other.">
<path d="M270 40V77M270 77H134V110M270 77H406V110" class="line"/>
<text x="270" y="27">One practical question</text>
<rect x="23" y="112" width="222" height="135" rx="12"/><rect x="295" y="112" width="222" height="135" rx="12"/>
<text x="134" y="140">Check</text><text x="134" y="166">the explanation</text><text x="134" y="201">Does this arrow</text><text x="134" y="227">match the source?</text>
<text x="406" y="145">Test the decision</text><text x="406" y="179">Is the room cooler</text><text x="406" y="206">from 8 AM</text><text x="406" y="233">until 12 PM?</text>
<text x="270" y="286">One result does not answer both.</text></svg>'''


def homepage(registry, pages):
    for r in REGIONS:
        if any(s not in registry for s in r['sources']):raise ValueError('Unbound homepage region')
        if any(slug not in {pg['slug'] for pg in pages} for slug,_ in r['routes']):raise ValueError('Unbound homepage journey')
    body='''<nav class="home-page-nav" aria-label="On this page"><a href="#purpose">Why Crucis?</a><a href="#landscape">The research landscape</a><a href="#study">How we study it</a><a href="#next-work">What comes next</a></nav><div class="home-intro"><p class="eyebrow">Crucis · Checking answers about cause and effect</p><h1>Would opening the window earlier keep the room cooler?</h1><p class="home-lead">Start with a decision. Follow the explanation. Then ask what would make its answer trustworthy.</p></div>
<section class="home-case" aria-label="From the apartment decision to the need for an audit"><div class="home-case-tabs" role="group" aria-label="Explore the opening example"><button type="button" data-case-select="decision" aria-controls="case-decision">1 · The decision</button><button type="button" data-case-select="explanation" aria-controls="case-explanation">2 · The explanation</button><button type="button" data-case-select="check" aria-controls="case-check">3 · What must be checked</button></div>'''
    case=[('decision','room','A reason to open the window.',
           'The room gets hot. Opening the window might bring in cooler air—but opening at 8 AM rather than 10 AM is useful only if it improves the temperature we care about.',
           'To isolate that choice in a proposed experiment, compare equivalent morning conditions, including outdoor temperature and wind.'),
          ('explanation','arrows','We can check a proposed explanation.',
           'A causal-discovery program tries to infer what affects what. It can express its answer with arrows: an arrow starts at a proposed cause and ends at what it directly changes.',
           'Here the picture shows links stated by the apartment’s released reference—a proposed answer key, rather than a program’s answer. Other links are omitted. We must check that the reference applies before using it to judge the saved proposals.'),
          ('check','split','Checking an arrow and testing a decision are different jobs.',
           'We can check whether a proposed arrow matches an applicable source. That alone does not measure whether opening earlier keeps the room cooler.',
           'For that decision, the proposed experiment compares average room temperature from 8 AM until 12 PM under the two opening times. The saved diagrams do not establish that result.')]
    for key,kind,title,a,b in case:
        body+=f'<div class="home-case-scene" data-case-panel="{key}" id="case-{key}"><div class="home-illustration">{apartment_art(kind)}<p class="figure-note task-reference"><a href="#apartment-task">Based on CausalArena’s apartment task · source and saved data ↓</a></p></div><div><h2>{title}</h2>'+p(a,'apartment','teaching-only')+p(b,'apartment','teaching-only')+'</div></div>'
    body+=task_detail(registry)
    body+=p('Suppose a program tries to help by proposing how opening the window affects airflow and heat. We need to check that explanation before relying on it. We also need a separate test of whether opening at 8 AM rather than 10 AM improves the room temperature.','apartment','teaching-only',cls='home-case-bridge')
    body+='''<nav class="route-links"><a href="./index.html">Walk through the full apartment case →</a><a href="./evidence.html#apartment">Inspect the saved-case basis ↗</a></nav></section>
<section class="home-section" id="purpose"><p class="eyebrow">Why Crucis exists</p><h2>A plausible answer is the beginning of the check.</h2>'''
    body+=p('Crucis is an independent framework for auditing causal-discovery systems and their claims. Its job is to preserve what a system actually produced, test a well-defined question about it, and make the finding traceable to evidence.','framework')
    body+=p('Before trusting “this answer is wrong,” we need to know which answer was checked, what it meant, why the reference applies and how the conclusion was reached. We must challenge Crucis’s own checks too.','framework','framework-map')
    body+=p('Following an answer into a useful scientific comparison exposes five connected duties. Each becomes a question in the landscape below.','framework','framework-map')
    chain=[('Read the answer','Select the intended output and preserve what it means.','answers'),('Justify the key','Establish why this reference can judge this answer.','reference'),('Compare fairly','Declare the achievement and matching conditions.','comparison'),('Trace the finding','Connect the reported conclusion to its evidence.','reconstruction'),('Test Crucis','Check the auditor and the connections it relies on.','validation')]
    body+='<ol class="audit-chain" aria-label="What must hold along an audit">'+''.join(f'<li><a href="#{key}" data-home-select="{key}"><span class="chain-number">{i+1:02}</span><strong>{name}</strong><span>{detail}</span></a></li>' for i,(name,detail,key) in enumerate(chain))+'</ol>'
    body+=p('The connections matter: a valid reference and a correctly decoded answer can still concern different quantities or versions. The whole route needs evidence when separate component checks do not establish it.','framework-map')
    body+='''</section><section class="home-section" id="landscape"><p class="eyebrow">The bounded research landscape</p><h2>Five questions we have to earn answers to.</h2>'''
    body+=p('Choose a territory to see the current reasoning, the checks it still needs and the research choice a person could help challenge. These are connected questions, not five completion percentages.','framework-map')
    body+='<div class="home-explorer"><div class="home-map"><div class="home-landscape">'+landscape()+'</div><p class="figure-note">Areas and distances are schematic. An outline means selected, not passed. The declared scope can expand when a counterexample exposes a gap.</p><nav class="home-territory-list" aria-label="Choose an audit question">'+''.join(f'<a href="#{r["id"]}" data-home-select="{r["id"]}">{E(r["title"])}</a>' for r in REGIONS)+'</nav></div><div class="home-region-panels">'
    for r in REGIONS:
        action=ACTIONS[r['id']]
        body+=f'<article class="home-region" id="{r["id"]}" data-home-region="{r["id"]}" tabindex="-1"><p class="eyebrow">Explore this territory</p><h3>{E(r["title"])}</h3>'+p(r['example'],*r['sources'],cls='region-example')
        for label,key,state in [('What the retained evidence establishes','known','reasoned'),('What still needs an exact check','check','execution'),('The research choice to challenge','question','research')]:
            body+=f'<section class="region-duty {state}"><h4>{label}</h4>'+p(r[key],*r['sources'])
            if key in ('check','question'):
                lane='check' if key=='check' else 'research';slug,link_label=action[lane+'_link']
                body+='<div class="direction-action"><span class="action-kind">Next · '+E(action[lane+'_kind'])+'</span>'+p(action[lane+'_action'],*r['sources'],'study-design')+'<a href="./'+E(slug)+'.html">'+E(link_label)+' →</a></div>'
            body+='</section>'
        body+='<details class="region-more"><summary>Why the remaining choice matters</summary>'+p(r['why'],*r['sources'])+'</details>'
        body+='<div class="region-next"><p class="eyebrow">What lets us move on—and what would reopen it</p>'+p(action['done'],*r['sources'],'study-design')+'<details><summary>Where a person can help</summary>'+p(r['human'],*r['sources'])+'</details></div>'
        body+='<details class="region-more"><summary>All steps in this investigation</summary><nav class="region-routes" aria-label="Deeper '+E(r['id'])+' walkthroughs">'+''.join(f'<a href="./{slug}.html"><span>{i+1:02}</span>{E(label)} →</a>' for i,(slug,label) in enumerate(r['routes']))+'</nav></details>'
        body+='<details class="region-more"><summary>Evidence and scope behind this summary</summary><div class="route-links">'+''.join(f'<a href="./evidence.html#{s}">{E(registry[s]["title"])} ↗</a>' for s in r['sources'])+'</div></details><a class="home-map-return" href="#landscape">↑ Choose another question</a></article>'
    body+='</div></div></section>'
    body+='''<section class="home-section" id="study"><p class="eyebrow">How the study follows from this work</p><h2>Crucis is part of what we are testing.</h2>'''
    body+=p('We need to test whether Crucis produces reliable, useful audits—not assume that it does. That requires two connected kinds of evidence. Either can reveal failures or limits.','study-design','framework')
    body+=p('The current study plan asks how causal-discovery systems use added knowledge, accept or reject proposed edits, and seek information or withhold an answer. It also asks whether Crucis can audit those behaviors faithfully.','study-design')
    body+='''<div class="study-tracks"><article><span class="track-label">Check the measuring instrument</span><h3>Does Crucis make the right distinctions?</h3>'''+p('Use independently solved cases: a supported answer, an actual error, a correct answer not established by the available evidence, and an intact file containing the wrong field. Then inspect the connected audit path.','s7','diverse-build','joined-checks')+'''<a href="./validate-cases.html">Follow the auditor tests →</a></article><article><span class="track-label">Use it to learn about actual systems</span><h3>What scientific conclusion can an audit support?</h3>'''+p('Choose the intended task and information conditions. Preserve native outputs, failures and uncertainty. Use qualified references and comparisons to estimate what happened within a declared study scope.','study-design','study-path','native-policy')+'''<a href="./comparison-task.html">Follow the study-design question →</a></article></div>'''
    body+=p('Checking the instrument against known answers is calibration. Those controls help qualify Crucis, while the empirical study observes actual discovery systems. Controls cannot substitute for independent study observations or establish performance on unseen cases. Any case reuse must remain explicit.','study-design','study-path')
    body+='''<div class="study-sizing"><div><p class="eyebrow">Why this does not give us a sample size yet</p><h3>Coverage chooses what to challenge. Precision helps decide how much to observe.</h3>'''
    body+=p('The research map helps identify missing mechanisms, meanings, conditions and failure paths. The study plan then needs eligible independent cases, information about variation and a defensible uncertainty target. More calls on one case do not create more independent cases.','study-design','study-path')
    body+=p('The inspected plan has no adopted main-study sample size. Its later sizing gate uses completion and assessability, cost and time, variation within a case, differences between cases and dependence among related cases.','study-design','study-path')+'</div>'
    stages=[('Fix the claim','What would we estimate, for whom, and under which information?'),('Choose the cases','Which mechanisms and tasks belong, and which observations share a case or family?'),('Learn from a bounded pilot','Can we judge the paired attempts? What do failures, time, cost and variation look like?'),('Justify size and freeze','Review precision, case weights, dependence, missing outcomes and stopping rules before the main runs.')]
    body+='<ol class="sizing-path" aria-label="How the study size is justified">'+''.join(f'<li><span>{i+1:02}</span><div><h4>{title}</h4>{p(detail,"study-design","study-path")}</div></li>' for i,(title,detail) in enumerate(stages))+'</ol></div>'
    body+='''<details class="region-more"><summary>What is already demonstrated, and what is not?</summary>'''
    body+=p('The newer committed implementation account reports joined controlled measurement, finding, report and auditor-check paths. Its fixed three-source controls are implementation evidence. They are not new observations of discovery-system behavior, a population correctness estimate or the main study.','joined-checks')
    body+=p('This homepage retains that source account separately from earlier evidence. It does not qualify newer uncommitted work, the separately saved five-variable output or every possible system.','joined-checks','copilot-card')+'<div class="route-links"><a href="./evidence.html#joined-checks">Inspect the joined-path account ↗</a><a href="./evidence.html#study-design">Inspect the study and sizing plan ↗</a></div></details></section>'
    body+='''<section class="home-section" id="next-work"><p class="eyebrow">Where the work goes next</p><h2>Ask for the evidence—or challenge the choice.</h2>'''
    body+=p('For a known expected result, obtain the exact execution and reporting evidence. For a genuine research choice, compare live alternatives and seek the counterexample or expertise that could decide between them.','framework-map','study-design')
    body+='''<div class="frontier-grid"><article><span class="state-tag">Execution and qualification</span><h3>Demonstrate the actual path.</h3>'''+p('The implementation owner supplies records for the named case and version. A new control does not automatically qualify a different saved answer.','copilot-card','joined-checks')+'''<a href="./answer-selected.html">Trace one actual answer →</a></article><article><span class="state-tag">Human investigation</span><h3>Challenge a consequential choice.</h3>'''+p('Bring a bounded question, competing explanations, work already done and the evidence that would change our view. Preserve disagreement and no-finding outcomes.','framework-map','study-design')+'''<a href="./review.html">See focused questions for review →</a></article><article><span class="state-tag">Scope challenge</span><h3>Find an important escape.</h3>'''+p('Ask what a misleading auditor could still do while passing the current tests. Extend the duty roster when the example exposes a real missing promise or connection.','framework-map','s7')+'''<a href="./validate-coverage.html">Challenge the assessment boundary →</a></article></div></section>
<section class="home-section home-record" id="record"><div><p class="eyebrow">A continuing, inspectable research record</p><h2>What changed, and why should we believe it?</h2>'''
    body+=p('A session can contribute an objection, example or proposed change. It becomes public research progress only through reviewed reasoning or evidence. Attendance, silence and agreement are not proof. Private correspondence and attribution stay behind their own decisions.','framework-map')
    body+='''<nav class="route-links"><a href="./evidence.html">Read the evidence →</a><a href="./history.html">See the dated changes →</a><a href="./research-record.html">How contributions enter the record →</a></nav></div><aside><p class="eyebrow">Evidence edition · 17 November 2026</p>'''
    body+=p('A dated projection of selected sources, not a live monitor or a scientific certificate. Each source retains its own version and limits. Changed decisive evidence requires reassessment.','framework-map','joined-checks')
    body+='''<a href="./view-status.json">Inspect source-currentness details ↗</a></aside></section><section class="home-software" id="software"><div><p class="eyebrow">Use or extend Crucis</p><h2>The framework behind the research.</h2>'''+p('Inspect the software, installation instructions and declared support. The framework is broader than one adapter or study; each supported use still needs its own evidence.','framework')+'''</div><nav class="route-links"><a href="../software.html">Installation and software scope →</a><a href="https://github.com/crucis-lab/crucis">Source repository ↗</a></nav></section>'''
    return body
