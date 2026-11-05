"""Explicit four-path fixture composition; never a real causal evaluation."""
import base64
from contextlib import contextmanager
from dataclasses import replace
from decimal import Decimal
import json
from pathlib import Path
import sqlite3
import sys
from types import SimpleNamespace
import dispatch_case as case
from crucis_causal.execution import api,codec
from crucis_causal.execution.drivers import NativeReply
from crucis_causal.execution.model import (Builder,ExecutionError,canonical,contract,digest,identity,index,
    known,not_applicable,number,qualified,reference,scope,unknown,unknown_ref)
sys.path.insert(0,str(case.FIX))
from native_program import discover


class LocalReceiver:
    """Owned synchronous native function with an independent durable call meter."""
    def __init__(self,root):
        self.root=Path(root);self.root.mkdir(parents=True,exist_ok=True);self.path=self.root/'native.sqlite3'
        self.epoch='0'
        with self.db() as db:
            db.executescript('CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY,value TEXT NOT NULL); CREATE TABLE IF NOT EXISTS calls(transmission TEXT PRIMARY KEY,command TEXT NOT NULL,input_digest TEXT NOT NULL,result BLOB NOT NULL,charge TEXT NOT NULL);')
            db.execute('INSERT OR IGNORE INTO meta VALUES(?,?)',('namespace',identity()))
            self.namespace=db.execute('SELECT value FROM meta WHERE key=?',('namespace',)).fetchone()[0]

    @contextmanager
    def db(self):
        db=sqlite3.connect(self.path,isolation_level=None)
        try:
            db.row_factory=sqlite3.Row
            if db.execute('PRAGMA journal_mode=DELETE').fetchone()[0].lower()!='delete':raise AssertionError('local fixture profile')
            db.execute('PRAGMA synchronous=FULL');yield db
        finally:db.close()

    def invoke(self,data,command,transmission):
        with self.db() as db:
            db.execute('BEGIN IMMEDIATE')
            old=db.execute('SELECT * FROM calls WHERE transmission=?',(transmission,)).fetchone()
            if old:
                if old['command']!=command or old['input_digest']!=digest(data)['value']:raise ExecutionError('s3.fixture_transmission_conflict')
                db.execute('COMMIT');return bytes(old['result'])
            total=sum((Decimal(r[0]) for r in db.execute('SELECT charge FROM calls')),Decimal('0'))
            if total+Decimal('0.7')>Decimal('1'):raise ExecutionError('s3.fixture_local_capacity')
            raw=discover(data) # Actual synchronous native call, not stored oracle playback.
            db.execute('INSERT INTO calls VALUES(?,?,?,?,?)',(transmission,command,digest(data)['value'],raw,'0.7'));db.execute('COMMIT')
            return raw

    def oracle(self):
        with self.db() as db:
            rows=[dict(r)|{'result':base64.b64encode(bytes(r['result'])).decode()} for r in db.execute('SELECT * FROM calls')]
        return {'calls':rows,'charge':str(sum((Decimal(r['charge']) for r in rows),Decimal('0'))),'cap':'1'}


class LocalMechanics(case.Mechanics):
    def prepare(self,binding,inputs,context):
        value=super().prepare(binding,inputs,context)
        if value['mode']!='local' or value['pause'] or value['drop_reply'] or value['native_id'] is not None or value['epoch']!='0':raise ExecutionError('s3.fixture_local_options_unqualified')
        return value
    def invoke(self,call):
        raw=self.client.invoke(base64.b64decode(call.invocation['data']),call.request.command['target'],call.transmission['target'])
        descriptor={'authority':'S3_owned_local_function','namespace':self.client.namespace,'native_id':call.transmission['target'],
            'incarnation':known(call.transmission['target']),'identity_rule':contract('s3.fixture.local_call_occurrence'),'validity':unknown_ref('typed_payload'),'basis':[]}
        attempt=next(qualified(e.reference,e.source_package) for e in call.request.inputs.entries if e.role=='s3.role.attempt')
        b=Builder('Measured local native fixture bill')
        meter=self.client.oracle();native_bill=next(row for row in meter['calls'] if row['transmission']==call.transmission['target'])
        proof,storage=case.typed_document(b,contract('s3.fixture.native_bill'),{'command':native_bill['command'],'transmission':native_bill['transmission'],'charge':native_bill['charge'],'cap':meter['cap']})
        bill=b.add('resource_entry',{'scope':scope(reference(call.request.binding.record['id'],'operation_binding',call.request.binding.context['package_id'])),
            'owner':self.client.owner.owner,'resource':contract('s3.fixture_work'),'unit':self.client.owner.units['s3.fixture_work'],
            'entry_kind':'bill','quantity':known(number(native_bill['charge'])),'interval':not_applicable('s3.fixture.atomic_local_call'),
            'finality':'final','revises':[],'aggregation':contract('s3.aggregation.replace_then_disjoint_members'),'basis':[proof]})
        audience=b.add('audience',{'purpose':contract('s3.private_fixture'),'recipients':index(),'disclosure_policy':unknown_ref('s1.policy'),'authority':unknown()})
        root=b.add('projection_view',{'view_role':'audience_projection','audience':audience,'projection_contract':contract('s3.fixture.local_bill'),'members':index([bill]),'claims':index(),'limits':index()})
        v=case.frame(b,root,(*call.context.read.views,storage));delta=api.RecordDelta(v.records,(),(*call.context.read.views,storage,v))
        return NativeReply(raw,{'name':'s1.json','version':'0.1.0-proposal.1'},known(True),descriptor=descriptor,epoch='0',origin_attempt=attempt,facts=delta)


class LocalEnvironment(case.Environment):
    def __init__(self,root,receiver):
        super().__init__(root,receiver,scientific_path='local',native_operations=(case.OPS[0],),
            resources={'s3.fixture_work':{'unit':contract('fixture_unit'),'capacity':number('1')}},mechanics_factory=LocalMechanics,native_channel=contract('s3.fixture.local_function'))
        receiver.owner=self.owner
    def operation_amounts(self,actual):return self.amounts('0.7')


def decode_graph(env,issued):
    """Explicit fixture decoder: native `order` supplies input-column alignment.

    It is not a topological order, a true graph, or a general label-matching rule.
    Missing edges remain unreported. Both native and derived objects survive.
    """
    from crucis_causal.connections.model import Builder as B1,contract as c1,source as s1source
    from crucis_causal.connections.domains import finite_domain,member,graph_body,directed_link
    from crucis_causal.connections.validation import content_bytes
    from crucis_causal.execution.imports import OutputInterpreter
    from crucis_causal.execution.journal import resolve_binding
    resolver=codec.Resolver(env.context.read.views,limits=case.L)
    raw=[]
    for v in issued.records.dependencies:
        for r in v.records:
            if r['record_type']=='s1.artifact_snapshot':
                try:value=json.loads(content_bytes(r['payload']['content']))
                except (ValueError,KeyError,TypeError):continue
                if isinstance(value,dict) and set(value)=={'order','edges'}:raw.append(reference(r['id'],r['record_type'],v.package_id))
    unique={canonical(r):r for r in raw}
    if len(unique)!=1:raise ExecutionError('s3.fixture_exact_native_graph_required')
    artifact=next(iter(unique.values()))
    shown=next(r['members']['members'][0] for r in env.launch_roles if r['role']=='s3.role.presentations')
    presentation,ppid=resolver.record(shown,shown['package_id']);canonical_domain=qualified(presentation['payload']['domain']['value'],ppid)
    record,dpid=resolver.record(canonical_domain,canonical_domain['package_id'])
    names=[]
    for m in record['payload']['members']:
        variable,vpid=resolver.record(m['variable'],dpid)
        if variable['payload']['meaning']['state']!='known':raise ExecutionError('s3.fixture_input_domain_unknown')
        names.append(variable['payload']['meaning']['value'])
    params,views=case.document(contract('s3.fixture.graph_selectors'),{'mode':'whole'},env.context.read.views);env.include(*views)
    b=Builder('Pure native graph interpretation binding')
    op=b.add('operation_binding',{'operation':contract('s3.op.decode_output'),'roles':[
        {'role':'s3.role.artifacts','members':index([artifact])},{'role':'s3.role.mappings','members':index()},{'role':'s3.role.source_outputs','members':index()}],
        'parameters':[{'key':k,'value':known(v)} for k,v in [('decoder',contract('s3.fixture.column_order_graph')),('selectors',params),('target_contract',c1('graph'))]]})
    audience=b.add('audience',{'purpose':contract('s3.private_fixture'),'recipients':index(),'disclosure_policy':unknown_ref('s1.policy'),'authority':unknown()})
    r=b.add('projection_view',{'view_role':'audience_projection','audience':audience,'projection_contract':contract('s3.fixture.graph_decode'),'members':index([op]),'claims':index(),'limits':index()})
    view=case.frame(b,r,env.context.read.views);env.include(view);resolver=codec.Resolver(env.context.read.views,limits=case.L)
    binding=resolve_binding(op,view.package_id,resolver)
    descriptor=api.ExactDriverDescriptor(env.component,contract('s3.op.decode_output'),contract('binding'),contract('evidence'),env.pin,(),None)
    request=api.ExactOperationRequest(unknown_ref('effect_command'),binding,binding.inputs,descriptor,view)
    observed={}
    def selectors(value):
        if value!={'mode':'whole'}:raise ExecutionError('s3.fixture_graph_selector')
        return value
    def reader(inputs,selectors,target,context):
        entry=inputs.entries[0];native=json.loads(content_bytes(entry.record['payload']['content']))
        order=native['order']
        if not isinstance(order,list) or len(order)!=len(names) or len(set(order))!=len(order):raise ExecutionError('s3.fixture_column_alignment_unestablished')
        positions={label:str(i) for i,label in enumerate(order)}
        if any(len(edge)!=2 or any(n not in positions for n in edge) for edge in native['edges']):raise ExecutionError('s3.fixture_graph_edge_unmapped')
        native_builder=B1('Native graph and explicit column-alignment view')
        domain=finite_domain(native_builder,order,evidence=[artifact])
        links=[directed_link(domain,positions[a],positions[b]) for a,b in native['edges']]
        graph=native_builder.output('graph',graph_body(domain,links,omission='unreported'),evidence=[artifact])
        entries=[{'from':[member(domain,str(i))],'to':[member(canonical_domain,m['key'])],'source':s1source('derived',[artifact],native_builder.producer)} for i,m in enumerate(record['payload']['members'])]
        mapping=native_builder.add('mapping',{'mapping_kind':'native_decode','from':domain,'to':canonical_domain,'entries':entries,
            'procedure':native_builder.producer,'purpose':'s1.coordinate_interpretation','coverage':scope(domain,canonical_domain),'properties':[],'checks':[],
            'source':s1source('derived',[artifact,canonical_domain],native_builder.producer)})
        derived=native_builder.output('graph',graph_body(canonical_domain,[directed_link(canonical_domain,positions[a],positions[b]) for a,b in native['edges']],omission='unreported'),
            role='s1.derived_view',evidence=[graph,mapping])
        native_builder.add('relation',{'relation_contract':c1('representation_of'),'endpoints':[{'role':'s1.source','target':graph},{'role':'s1.view','target':derived}],
            'parameters':[mapping],'scope':scope(graph,derived),'source':s1source('derived',[graph,mapping],native_builder.producer)})
        dependencies=tuple(v for v in context.views if v.format['name']=='s1.connection_package')
        frozen=case.input_case.snapshot1(native_builder,[graph,derived,mapping],dependencies)
        observed.update(order=order,canonical_order=names,mapping=dict(zip(order,names)),native=qualified(graph,frozen.package_id),derived=qualified(derived,frozen.package_id))
        delta=api.RecordDelta(dependencies=(*context.views,frozen))
        return api.DriverEvidence(reference(binding.record['id'],'operation_binding',view.package_id),delta,index([observed['native'],observed['derived']]),index(),index(),())
    interpreter=OutputInterpreter(contract('s3.fixture.column_order_graph'),c1('graph'),contract('s3.fixture.graph_selectors'),selectors,reader,env.pin)
    result=interpreter.decode(request,env.context.read)
    if result.state!='completed':raise AssertionError(result.issues)
    env.include(*result.records.dependencies)
    return observed,result


from observation_case import Environment as ObservationEnvironment,OPS as STREAM_OPS

class RemoteEnvironment(ObservationEnvironment):
    def __init__(self,root,client):
        resources={'s3.fixture_work':{'unit':contract('fixture_unit'),'capacity':number('10')},
            's3.fixture_fetch_events':{'unit':contract('fixture_event'),'capacity':number('12')}}
        case.Environment.__init__(self,root,client,scientific_path='remote',native_operations=(*case.OPS,*STREAM_OPS),resources=resources)


def cold_packet(env,kind,**extra):
    p=env.pin
    value={'kind':kind,'root':str(env.root),'account':env.account,'component':env.component,'allocation':env.allocation,'view':env.view.package_id,
        'pin':{'reference':p.reference,'content_digest':p.content_digest,'selector':p.selector,'source':p.source_view.package_id},
        'views':[base64.b64encode(v.source_bytes).decode() for v in env.context.read.views],**extra}
    if kind=='remote':
        value['saved']={name:getattr(env,name) for name in ('descriptor','sources','source','period','max_events','max_bytes','native_subject')}
    elif kind=='interactive':
        value['saved']={name:getattr(env,name) for name in ('native','data','actions','policy','endpoint','gateway','choices','information_refs','candidate_spec','frontier')}
        p=env.specification;value['specification']={'reference':p.reference,'content_digest':p.content_digest,'selector':p.selector,'source':p.source_view.package_id}
    return value


def cold_reopen(value,bootstrap):
    """Trusted test-supervisor bootstrap; saved JSON alone has no authority."""
    from crucis_causal.execution.registry import SuppliedRegistryContext,ExactDriverRegistry,ExactDecisionRegistry,PayloadRegistry,supplied_callable
    for field in ('kind','root','account','allocation'):
        if value[field]!=bootstrap[field]:raise ExecutionError('s3.fixture_bootstrap_scope_mismatch')
    views=tuple(codec.parse_snapshot(base64.b64decode(raw),case.L) for raw in value['views']);resolver=codec.Resolver(views,limits=case.L)
    p=value['pin'];pin=api.PinnedArtifactIdentity(p['reference'],p['content_digest'],p['selector'],resolver.view(p['source']))
    registry=SuppliedRegistryContext(ExactDriverRegistry(),ExactDecisionRegistry(),PayloadRegistry())
    read=api.PinnedReadContext(views,api.supplied_read(v.package_id for v in views),registry,case.L)
    prior=SimpleNamespace(root=Path(bootstrap['root']),pin=pin,component=value['component'],account=bootstrap['account'],allocation=bootstrap['allocation'],view=resolver.view(value['view']),context=SimpleNamespace(read=read))
    if value['kind']=='local':return prior
    prior.client=case.Client(bootstrap['address'],bootstrap['token'],bootstrap['namespace'],bootstrap['epoch'])
    for name,item in value['saved'].items():setattr(prior,name,item)
    if value['kind']=='remote':
        import observation_case as obs
        from crucis_causal.execution.collection import ObservationProfile
        prior.profile=ObservationProfile(obs.PROTOCOL,supplied_callable(obs.source_identity),supplied_callable(obs.measure),supplied_callable(obs.resume),supplied_callable(obs.advance),pin)
        prior.owner=SimpleNamespace(resources={'s3.fixture_work':{'unit':contract('fixture_unit'),'capacity':number('10')},'s3.fixture_fetch_events':{'unit':contract('fixture_event'),'capacity':number('12')}},native_operations=(*case.OPS,*obs.OPS))
        return obs.reopen(prior)
    if value['kind']=='interactive':
        import interaction_case as inter
        p=value['specification'];prior.specification=api.PinnedArtifactIdentity(p['reference'],p['content_digest'],p['selector'],resolver.view(p['source']))
        prior.information_inputs=api.PinnedInputs(tuple(inter.bound(r,'s3.role.information',read) for r in prior.information_refs),views)
        prior.owner=SimpleNamespace(resources={'s3.fixture_work':{'unit':contract('fixture_unit'),'capacity':number('20')},
            's3.fixture_policy_slots':{'unit':contract('fixture_response'),'capacity':number('2')},'s3.fixture_compute':{'unit':contract('fixture_request'),'capacity':number('2')}},native_operations=(*case.OPS,*inter.OPS))
        return inter.reopen(prior)
    raise ExecutionError('s3.fixture_cold_profile_unavailable')
