"""Persistent local fixture owner: actual decisions, holds and live grants.

DLV-08/09. This cooperative local owner enforces its configured ledger and
receiver permission checks. It is not a universal monetary meter, operating-system
isolation mechanism or authorization for a third-party provider.
"""
import copy
from contextlib import contextmanager
import datetime
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import time
import weakref
from . import api,codec
from .authority import Authority
from .journal import binding_digest,resolve_binding
from .model import (Builder,ExecutionError,canonical,contract,digest,identity,index,known,
                    not_applicable,number,qualified,reference,scope,unknown,unknown_ref)
from .registry import PayloadRegistry
from .schema import operation,split,validate_value

METHODS={'reserve':'s3.op.owner_reserve','reconcile':'s3.op.owner_reconcile','renew':'s3.op.owner_renew',
         'settle':'s3.op.owner_settle','release':'s3.op.owner_release','authorize':'s3.op.owner_authorize'}
DDL='''
CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY,value BLOB NOT NULL);
CREATE TABLE IF NOT EXISTS allocations(id TEXT PRIMARY KEY, maximum INTEGER NOT NULL, consumed INTEGER NOT NULL, allowed BLOB NOT NULL);
CREATE TABLE IF NOT EXISTS subjects(correlation TEXT PRIMARY KEY,binding BLOB NOT NULL,amounts BLOB NOT NULL,status TEXT NOT NULL,expires TEXT NOT NULL,epoch TEXT NOT NULL,receipt BLOB NOT NULL);
CREATE TABLE IF NOT EXISTS requests(id TEXT PRIMARY KEY,fingerprint BLOB NOT NULL,correlation TEXT NOT NULL,receipt BLOB NOT NULL,view_id TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS views(id TEXT PRIMARY KEY,data BLOB NOT NULL);
CREATE TABLE IF NOT EXISTS charges(correlation TEXT NOT NULL,resource TEXT NOT NULL,quantity TEXT NOT NULL,PRIMARY KEY(correlation,resource));
CREATE TABLE IF NOT EXISTS calls(id TEXT PRIMARY KEY,allocation TEXT NOT NULL,request_id TEXT NOT NULL,operation TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS control_records(call_id TEXT PRIMARY KEY,records BLOB NOT NULL);
'''

def _time():
    return {'time_type':'utc_instant','value':datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='microseconds').replace('+00:00','Z'),
        'precision':'fractional_second','clock':unknown(),'uncertainty_seconds':unknown()}

def _native_time(value):
    return {'time_type':'native_report','text':str(value),'timezone':known('owner_control_clock'),'precision':known('reported_nanoseconds')}

def _quantity(value):
    validate_value(value,'Number')
    if value['number_type']=='nonfinite' or Decimal(value['text'])<0:raise ExecutionError('s3.finite_nonnegative_amount_required')
    return Decimal(value['text'])

def native_binding_ref(binding):
    return reference(binding.record['id'],'operation_binding',binding.context['package_id'])

def owner_request_body(request):
    return {'operation':request.operation,'owner':request.owner,'correlation':request.correlation,
        'target_binding':native_binding_ref(request.binding),'binding_digest':binding_digest(request.binding),
        'parameters':list(request.parameters),'request_occurrence':request.request_occurrence,
        'admission_occurrence':request.admission_occurrence,
        'evidence':[qualified(e.reference,e.source_package) for e in request.evidence.entries]}

def persist_owner_requests(journal,head,requests,journal_context,read_context):
    """Persist the complete initial group and exact request bodies before any RPC.

    Returns only a journal commit, never sends a request or returns native authority.
    Subsequent recovery requests receive their own identities and explicit plans.
    """
    if not requests or len({r.admission_occurrence for r in requests})!=1:raise ExecutionError('s3.one_complete_admission_group_required')
    from crucis_causal.connections.model import Builder as S1Builder,contract as c1
    from crucis_causal.connections.evidence import capture_bytes
    from crucis_causal.connections.codec import dumps as s1dumps
    resolver=codec.Resolver((*read_context.views,head.snapshot),limits=read_context.limits)
    target=requests[0].binding
    if any(binding_digest(r.binding)!=binding_digest(target) for r in requests):raise ExecutionError('s3.admission_group_binding_conflict')
    source_view=resolver.view(target.context['package_id'])
    command=next((r for r in source_view.records if r['record_type']=='s3.effect_command' and r['payload']['binding']['target']==target.record['id']),None)
    if command is None:raise ExecutionError('s3.owner_plan_command_unestablished')
    view_root=next(r for r in head.snapshot.records if r['id']==head.snapshot.package['roots'][0]['target'])['payload']
    group=requests[0].admission_occurrence
    b=Builder('Durable owner admission plan',created_at=known(_time()));native=S1Builder('Exact owner request/plan bytes')
    plan={'admission_occurrence':group,'command':reference(command['id'],'effect_command',source_view.package_id),
        'binding_digest':binding_digest(target),'basis_frontier':qualified(view_root['frontier'],head.snapshot.package_id),
        'requirements':qualified(view_root['requirements'],head.snapshot.package_id),
        'owner_requests':[{'owner':r.owner,'correlation':r.correlation,'request_occurrence':r.request_occurrence,
            'operation':r.operation,'expected_revision':next((p['value'] for p in r.parameters if p['key']=='expected_revision'),unknown())} for r in requests]}
    specifications=[(r.request_occurrence,contract('s3.owner.exact_request'),owner_request_body(r)) for r in requests]
    specifications.append((group,contract('s3.payload.admission_plan'),plan))
    artifacts=[(rid,selected,capture_bytes(native,canonical(value),format_contract=c1('json'))) for rid,selected,value in specifications]
    storage=codec.parse_snapshot(s1dumps(native.package([native.producer])),read_context.limits)
    for rid,selected,artifact in artifacts:
        b.add('typed_payload',{'payload_contract':selected,'content':{'artifact':qualified(artifact,storage.package_id),'selector':not_applicable()},
            'reference_context':{'package_id':b.package_id,'format':contract('account_package')}},record_id=rid)
    # The existing root keeps its exact old cutoff. These newly appended facts are
    # selected into a new coordinator view later; nothing mutates the old frontier.
    b.ingest(head.snapshot.records)
    dependencies={v.package_id:v for v in (*resolver._views.values(),storage)}
    staged=codec.parse_snapshot(codec.dumps(b.package(head.snapshot.package['roots'][0],tuple(dependencies.values())),read_context.limits),read_context.limits)
    dependencies[staged.package_id]=staged
    delta=api.CommitDelta(tuple(b._records.values()),(),tuple(dependencies.values()))
    return journal.append(head.account,head.revision,group,delta,journal_context)

class LocalOwner:
    def __init__(self,root,resources,*,native_operations=(),clock=None,ttl_ns='60000000000',limits=None):
        self.root=Path(root).resolve();self.root.mkdir(parents=True,exist_ok=True)
        if str(self.root).startswith('\\\\'):raise ExecutionError('s3.network_owner_store_not_qualified')
        self.path=self.root/'owner.sqlite3';self.limits=limits or api.Limits();self.clock=clock or time.time_ns
        if not isinstance(ttl_ns,str) or not re.fullmatch(r'[1-9][0-9]*',ttl_ns):raise ExecutionError('s3.positive_owner_ttl_required')
        self.ttl=int(ttl_ns);self.resources=copy.deepcopy(resources);self.native_operations=tuple(copy.deepcopy(native_operations))
        for name,spec in self.resources.items():
            validate_value(name,'QName');validate_value(spec['unit'],'Contract');_quantity(spec['capacity'])
            if set(spec)!={'unit','capacity'}:raise ExecutionError('s3.closed_owner_resource_config')
        for selected in self.native_operations:validate_value(selected,'Contract')
        self.authority=Authority();self._controls=weakref.WeakKeyDictionary();self._grants=weakref.WeakKeyDictionary()
        self.payloads=PayloadRegistry()
        def request_key(value):
            if not isinstance(value,dict) or set(value)!={'request_occurrence'}:raise ExecutionError('s3.owner_query_key_shape')
            validate_value(value['request_occurrence'],'ID');return value
        self.payloads.register(contract('s3.payload.owner_request_key'),request_key)
        implementation={name:hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() for name in ['owners.py','authority.py','accounting.py']}
        config={'resources':self.resources,'native_operations':list(self.native_operations),'ttl_ns':ttl_ns,'implementation':implementation}
        with self._db() as db:
            db.executescript(DDL);db.execute('BEGIN IMMEDIATE')
            old=db.execute('SELECT value FROM meta WHERE key=?',('config',)).fetchone()
            if old and json.loads(old[0])!=config:raise ExecutionError('s3.owner_configuration_or_code_drift')
            if old is None:
                view,units,requirement,frontier,audience=self._make_meta(implementation)
                db.execute('INSERT INTO meta VALUES(?,?)',('config',canonical(config)))
                db.execute('INSERT INTO meta VALUES(?,?)',('epoch',b'0'))
                db.execute('INSERT INTO meta VALUES(?,?)',('revision',b'0'))
                db.execute('INSERT INTO meta VALUES(?,?)',('identity',canonical({'view':view.package_id,'units':units,'requirements':requirement,'frontier':frontier,'audience':audience})))
                for v in self._meta_views:
                    db.execute('INSERT OR IGNORE INTO views VALUES(?,?)',(v.package_id,v.source_bytes))
            descriptor=json.loads(db.execute('SELECT value FROM meta WHERE key=?',('identity',)).fetchone()[0])
            db.execute('COMMIT')
            self.meta=codec.parse_snapshot(bytes(db.execute('SELECT data FROM views WHERE id=?',(descriptor['view'],)).fetchone()[0]),self.limits)
        self.units=descriptor['units'];self.requirements=descriptor['requirements'];self.frontier=descriptor['frontier'];self.audience=descriptor['audience']
        self.owner=reference(next(r['id'] for r in self.meta.records if r['record_type']=='s3.component'),'component',self.meta.package_id)

    @contextmanager
    def _db(self):
        db=sqlite3.connect(self.path,timeout=5,isolation_level=None);db.row_factory=sqlite3.Row
        try:
            if db.execute('PRAGMA journal_mode=DELETE').fetchone()[0].lower()!='delete':raise ExecutionError('s3.owner_storage_profile')
            db.execute('PRAGMA synchronous=FULL');db.execute('PRAGMA foreign_keys=ON');yield db
        finally:db.close()

    def _make_meta(self,implementation):
        from crucis_causal.connections.model import Builder as S1Builder,contract as c1
        from crucis_causal.connections.evidence import capture_bytes
        from crucis_causal.connections.codec import dumps as s1dumps
        pid,owner_id=identity(),identity();b1=S1Builder('Owner supplied code and unit definitions')
        code=capture_bytes(b1,canonical(implementation),format_contract=c1('code_identity_manifest'))
        definitions={}
        for name,spec in self.resources.items():
            value={'contract':spec['unit'],'resource':contract(name),'owner_scope':scope(reference(owner_id,'component'))}
            definitions[name]=capture_bytes(b1,canonical(value),format_contract=c1('json'))
        definitions['s3.control_call']=capture_bytes(b1,canonical({'contract':contract('owner_control_call_unit'),
            'resource':contract('control_call'),'owner_scope':scope(reference(owner_id,'component'))}),format_contract=c1('json'))
        source_view=codec.parse_snapshot(s1dumps(b1.package([code])),self.limits)
        b=Builder('Local ledger owner',package_id=pid,producer_id=owner_id,created_at=known(_time()),
            implementation=known({'artifact':qualified(code,source_view.package_id),'selector':not_applicable()}))
        audience=b.add('audience',{'purpose':contract('private_owner_evidence'),'recipients':index(),
            'disclosure_policy':unknown_ref('s1.policy'),'authority':unknown()})
        frontier=b.add('frontier',{'local_records':index(),'source_positions':index(),'selection_rule':contract('owner_local_snapshot')})
        requirements=b.add('requirement_context',{'catalog':contract('owner_requirements'),'requested_claims':index(),'coverage':index()})
        units={}
        for name,artifact in definitions.items():
            units[name]=b.add('typed_payload',{'payload_contract':contract('s3.payload.unit'),
                'content':{'artifact':qualified(artifact,source_view.package_id),'selector':not_applicable()},
                'reference_context':{'package_id':pid,'format':contract('account_package')}})
        root=b.add('projection_view',{'view_role':'audience_projection','audience':audience,'projection_contract':contract('owner_metadata'),
            'members':index([b.producer,*units.values(),frontier,requirements]),'claims':index(),'limits':index()})
        view=codec.parse_snapshot(codec.dumps(b.package(root,(source_view,)),self.limits),self.limits)
        self._meta_views=(source_view,view)
        return view,{k:qualified(v,pid) for k,v in units.items()},qualified(requirements,pid),qualified(frontier,pid),qualified(audience,pid)

    def _epoch(self,db):return bytes(db.execute('SELECT value FROM meta WHERE key=?',('epoch',)).fetchone()[0]).decode()
    def _revision(self,db):return bytes(db.execute('SELECT value FROM meta WHERE key=?',('revision',)).fetchone()[0]).decode()
    def _now(self):
        value=self.clock()
        if isinstance(value,bool) or not isinstance(value,int):raise ExecutionError('s3.owner_clock_unestablished')
        return value

    def control(self,allocation_id,*,max_calls='100',allowed_operations=None):
        """Explicit namespace-admin allocation; same ID never resets its counter."""
        validate_value(allocation_id,'ID');validate_value(max_calls,'PositiveIndex')
        allowed=tuple(allowed_operations or [*METHODS.values(),'s3.owner.inspect','s3.owner.check'])
        body={'kind':'owner_control','allocation':allocation_id,'maximum':max_calls,'allowed':list(allowed)}
        with self._db() as db:
            db.execute('BEGIN IMMEDIATE');old=db.execute('SELECT * FROM allocations WHERE id=?',(allocation_id,)).fetchone()
            if old and (old['maximum']!=int(max_calls) or json.loads(old['allowed'])!=list(allowed)):raise ExecutionError('s3.control_allocation_identity_conflict')
            db.execute('INSERT OR IGNORE INTO allocations VALUES(?,?,?,?)',(allocation_id,int(max_calls),0,canonical(list(allowed))));db.execute('COMMIT')
        cap=self.authority.issue(body,control=True);self._controls[cap]=body
        return cap

    def _control(self,context,operation_name,request_id):
        cap=getattr(context,'control',None)
        body=self._controls.get(cap) if isinstance(cap,api.OpaqueControlCapability) else None
        if body is None:raise ExecutionError('s3.owner_control_denied')
        self.authority.check(cap,body)
        if operation_name not in body['allowed']:raise ExecutionError('s3.owner_control_operation_denied')
        with self._db() as db:
            db.execute('BEGIN IMMEDIATE');row=db.execute('SELECT * FROM allocations WHERE id=?',(body['allocation'],)).fetchone()
            if row is None or row['consumed']>=row['maximum']:raise ExecutionError('s3.owner_control_allowance_exhausted')
            db.execute('UPDATE allocations SET consumed=consumed+1 WHERE id=?',(body['allocation'],))
            call_id=identity();db.execute('INSERT INTO calls VALUES(?,?,?,?)',(call_id,body['allocation'],request_id,operation_name))
            created=known(_time());event=reference(call_id,'diagnostic')
            envelope={'producer':self.owner,'created_at':created,'provenance':{'basis':'observed','evidence':[],
                'procedure':known(contract('owner_authorized_reception')),'inputs':[]},'extensions':[]}
            diagnostic={**envelope,'id':call_id,'record_type':'s3.diagnostic','contract':contract('diagnostic'),
                'payload':{'code':'s3.authorized_owner_reception','scope':scope(self.owner),'details':canonical({
                    'receiver_occurrence':call_id,'allocation':body['allocation'],'subject_label':request_id,'operation':operation_name}).decode(),'evidence':[]}}
            resource={**envelope,'id':identity(),'record_type':'s3.resource_entry','contract':contract('resource_entry'),
                'payload':{'scope':scope(event),'owner':self.owner,'resource':contract('control_call'),'unit':self.units['s3.control_call'],
                    'entry_kind':'control_overhead','quantity':known(number('1')),'interval':not_applicable('s3.owner_receiver_observation_interval'),
                    'finality':'final','revises':[],'aggregation':contract('s3.aggregation.replace_then_disjoint_members'),'basis':[event]}}
            db.execute('INSERT INTO control_records VALUES(?,?)',(call_id,canonical([diagnostic,resource])));db.execute('COMMIT')
        return call_id

    def remaining_control(self,allocation_id):
        with self._db() as db:
            r=db.execute('SELECT maximum,consumed FROM allocations WHERE id=?',(allocation_id,)).fetchone()
            return str(r['maximum']-r['consumed'])

    def _control_frame(self,context):
        """Observed authorized receptions, not CPU, money or native-policy use."""
        body=self._controls.get(context.control)
        with self._db() as db:
            rows=list(db.execute('SELECT r.records FROM control_records r JOIN calls c ON r.call_id=c.id WHERE c.allocation=?',(body['allocation'],)))
            data=list(db.execute('SELECT data FROM views'))
        b=Builder('Owner control reception recorder',created_at=known(_time()))
        members=[]
        # Repeated snapshots copy the original observation IDs/content unchanged.
        for row in rows:
            records=json.loads(row['records']);b.ingest(records)
            members.extend(reference(r['id'],r['record_type']) for r in records)
        root=b.add('projection_view',{'view_role':'audience_projection','audience':self.audience,'projection_contract':contract('owner_control_receptions'),
            'members':index(members),'claims':index(),'limits':index()})
        dependencies=tuple(codec.parse_snapshot(bytes(r[0]),self.limits) for r in data if json.loads(r[0])['package_id'] in
            {self.meta.package_id,*[d['package_id'] for d in self.meta.package['external_packages']]})
        view=codec.parse_snapshot(codec.dumps(b.package(root,dependencies),self.limits),self.limits)
        return (*dependencies,view)

    def _resolver(self,request,context):
        views={v.package_id:v for v in (*context.read.views,*request.binding.inputs.source_views,*request.evidence.source_views,self.meta)}
        with self._db() as db:
            # Only source dependencies required by the fixed owner metadata here.
            for descriptor in self.meta.package['external_packages']:
                row=db.execute('SELECT data FROM views WHERE id=?',(descriptor['package_id'],)).fetchone()
                views[descriptor['package_id']]=codec.parse_snapshot(bytes(row['data']),self.limits)
        return codec.Resolver(views.values(),limits=self.limits)

    def _parameters(self,method,request,context):
        if not isinstance(request,api.ExactOwnerRequest) or request.operation!=contract(METHODS[method]) or request.owner!=self.owner:
            raise ExecutionError('s3.exact_owner_request_required')
        for value in [request.correlation,request.request_occurrence,request.admission_occurrence]:validate_value(value,'ID')
        values={p['key']:p['value'] for p in request.parameters};spec=operation(request.operation)['parameters']
        if len(values)!=len(request.parameters) or set(values)!=set(spec):raise ExecutionError('s3.owner_parameter_keys')
        for name,expr in spec.items():
            validate_value(values[name],'K('+expr+')')
            if values[name]['state']!='known':raise ExecutionError('s3.owner_parameter_unestablished',name)
        params={k:v['value'] for k,v in values.items()}
        for name in ['correlation','request_occurrence','admission_occurrence']:
            if params[name]!=getattr(request,name):raise ExecutionError('s3.owner_request_identity_mismatch',name)
        resolver=self._resolver(request,context)
        actual=resolve_binding(native_binding_ref(request.binding),request.binding.context['package_id'],resolver)
        if binding_digest(actual)!=binding_digest(request.binding):raise ExecutionError('s3.owner_subject_binding_mismatch')
        for entry in request.evidence.entries:
            if not isinstance(entry,api.BoundInput):raise ExecutionError('s3.pinned_owner_evidence_required')
            found,pid=resolver.record(entry.reference,entry.source_package)
            if pid!=entry.source_package or canonical(found)!=canonical(entry.record) or resolver.view(pid).digest!=entry.source_digest:
                raise ExecutionError('s3.owner_evidence_pin_mismatch')
        return params,resolver

    def _payload(self,ref,request,resolver,expected):
        anchor=ref['package_id'] if ref.get('binding')=='external' else request.binding.context['package_id']
        record,pid=resolver.record(ref,anchor)
        if record['payload']['payload_contract']!=contract('s3.payload.'+expected):raise ExecutionError('s3.owner_payload_contract')
        return resolver.payload(ref,anchor,self.payloads)

    def _available(self,db,name):
        cap=_quantity(self.resources[name]['capacity'])
        used=sum((Decimal(r[0]) for r in db.execute('SELECT quantity FROM charges WHERE resource=?',(name,))),Decimal('0'))
        held=Decimal('0')
        for row in db.execute('SELECT amounts FROM subjects WHERE status=?',('active',)):
            held+=sum((Decimal(a['quantity']['text']) for a in json.loads(row[0]) if a['resource']['name']==name),Decimal('0'))
        return cap-used-held

    def _live_grant(self,row,request):
        if row is None or row['status']!='active' or self._now()>=int(row['expires']):return None
        with self._db() as db:epoch=self._epoch(db)
        if row['epoch']!=epoch or json.loads(row['binding'])!=binding_digest(request.binding):return None
        if request.binding.record['payload']['operation'] not in self.native_operations:return None
        if self.resources and not json.loads(row['amounts']):return None
        body={'kind':'native_owner_grant','correlation':request.correlation,'binding':binding_digest(request.binding),
            'epoch':epoch,'expires':row['expires'],'operation':request.binding.record['payload']['operation']}
        cap=self.authority.issue(body);self._grants[cap]=body;return cap

    def _emit(self,request,resolver,decision,revision,epoch,expires,entries,prior=()):
        from crucis_causal.connections.model import Builder as S1Builder,contract as c1
        from crucis_causal.connections.evidence import capture_bytes
        from crucis_causal.connections.codec import dumps as s1dumps
        b=Builder('Local owner evidence recorder',created_at=known(_time()))
        validity={'owner':self.owner,'scope':scope(native_binding_ref(request.binding)),'epoch':epoch,
            'valid_from':known(_native_time(self._now())),'valid_until':known(_native_time(expires)),
            'receiver_check':contract('owner_exact_live_grant'),'revocation':contract('owner_persisted_epoch')}
        b1=S1Builder('Owner validity bytes');artifact=capture_bytes(b1,canonical(validity),format_contract=c1('json'))
        content=codec.parse_snapshot(s1dumps(b1.package([artifact])),self.limits)
        valid=b.add('typed_payload',{'payload_contract':contract('s3.payload.validity'),
            'content':{'artifact':qualified(artifact,content.package_id),'selector':not_applicable()},
            'reference_context':{'package_id':b.package_id,'format':contract('account_package')}})
        resource_refs=[]
        for kind,amount,finality in entries:
            name=amount['resource']['name']
            resource_refs.append(b.add('resource_entry',{'scope':scope(native_binding_ref(request.binding)), 'owner':self.owner,
                'resource':amount['resource'],'unit':self.units[name],'entry_kind':kind,'quantity':known(amount['quantity']),
                'interval':not_applicable('s3.owner_atomic_subject_interval'), 'finality':finality,'revises':[],
                'aggregation':contract('s3.aggregation.replace_then_disjoint_members'),'basis':list(prior)}))
        receipt=b.add('owner_receipt',{'owner':self.owner,'correlation':request.correlation,'binding':native_binding_ref(request.binding),
            'revision':known(revision),'decision':decision,'holds':index(resource_refs),'validity':valid,'evidence':list(prior),
            'request_occurrence':request.request_occurrence,'admission_occurrence':request.admission_occurrence})
        root=b.add('projection_view',{'view_role':'audience_projection','audience':self.audience,'projection_contract':contract('owner_receipt_view'),
            'members':index([receipt,*resource_refs]),'claims':index(),'limits':index()})
        dependencies={v.package_id:v for v in (*resolver._views.values(),content)}
        value=codec.parse_snapshot(codec.dumps(b.package(root,tuple(dependencies.values())),self.limits),self.limits)
        check=codec.Resolver((*dependencies.values(),value),limits=self.limits);check.closure(value.package_id)
        return qualified(receipt,value.package_id),value,tuple(dependencies.values())

    def _request(self,method,request,context):
        try:
            params,resolver=self._parameters(method,request,context)
            self._control(context,METHODS[method],request.request_occurrence)
            if getattr(context,'fault',None):context.fault('before_owner_request')
            fingerprint=digest(canonical({'operation':request.operation,'owner':request.owner,'correlation':request.correlation,
                'binding':binding_digest(request.binding),'parameters':list(request.parameters),'request_occurrence':request.request_occurrence,
                'admission_occurrence':request.admission_occurrence,
                'evidence':[{'reference':qualified(e.reference,e.source_package),'source_digest':e.source_digest,
                    'record_digest':digest(canonical(e.record))} for e in request.evidence.entries]}))
            with self._db() as db:
                db.execute('BEGIN IMMEDIATE')
                cached=db.execute('SELECT * FROM requests WHERE id=?',(request.request_occurrence,)).fetchone()
                if cached:
                    if json.loads(cached['fingerprint'])!=fingerprint:raise ExecutionError('s3.owner_request_identity_conflict')
                    receipt=json.loads(cached['receipt']);view=codec.parse_snapshot(bytes(db.execute('SELECT data FROM views WHERE id=?',(cached['view_id'],)).fetchone()[0]),self.limits)
                    row=db.execute('SELECT * FROM subjects WHERE correlation=?',(request.correlation,)).fetchone()
                    revision=self._revision(db);db.execute('COMMIT')
                    old_record=next(r for r in view.records if r['id']==receipt['target'])
                    grant=self._live_grant(row,request) if old_record['payload']['decision']=='permitted' else None
                    return api.CallResult('completed',api.OwnerReceiptAndOptionalLiveGrant(receipt,revision,grant,()),
                        records=api.RecordDelta(dependencies=(view,*self._control_frame(context))))
                revision=self._revision(db);epoch=self._epoch(db)
                if 'expected_revision' in params and params['expected_revision']!=revision:raise ExecutionError('s3.owner_revision_conflict')
                row=db.execute('SELECT * FROM subjects WHERE correlation=?',(request.correlation,)).fetchone()
                bound=binding_digest(request.binding)
                if row and json.loads(row['binding'])!=bound:raise ExecutionError('s3.owner_correlation_binding_conflict')
                amounts=json.loads(row['amounts']) if row else [];expires=int(row['expires']) if row else self._now()+self.ttl
                status=row['status'] if row else 'active';decision='permitted';entries=[]
                prior=[qualified(e.reference,e.source_package) for e in request.evidence.entries]
                if row and row['receipt']:
                    previous=json.loads(row['receipt']);prior.append(previous)
                    old_view=codec.parse_snapshot(bytes(db.execute('SELECT data FROM views WHERE id=?',(previous['package_id'],)).fetchone()[0]),self.limits)
                    resolver.add(old_view)
                    for desc in old_view.package['external_packages']:
                        data=db.execute('SELECT data FROM views WHERE id=?',(desc['package_id'],)).fetchone()
                        if data:resolver.add(codec.parse_snapshot(bytes(data[0]),self.limits))
                if method=='reserve':
                    if row is not None:raise ExecutionError('s3.owner_reservation_already_exists')
                    amounts=self._payload(params['amounts'],request,resolver,'reservation_amounts')['entries']
                    totals={}
                    for amount in amounts:
                        name=amount['resource']['name'];spec=self.resources.get(name)
                        if spec is None or amount['resource']!=contract(name) or amount['unit']!=spec['unit']:raise ExecutionError('s3.owner_resource_or_unit_uninterpreted')
                        if amount['scope']!=scope(native_binding_ref(request.binding)):raise ExecutionError('s3.owner_amount_scope_mismatch')
                        totals[name]=totals.get(name,Decimal('0'))+_quantity(amount['quantity'])
                    if any(total>self._available(db,name) for name,total in totals.items()):decision='held';status='held';amounts=[]
                    entries=[('reservation',a,'interim') for a in amounts]
                elif method=='reconcile':
                    query=self._payload(params['query'],request,resolver,'query')
                    if query['subject']!=native_binding_ref(request.binding):raise ExecutionError('s3.owner_query_scope_mismatch')
                    query_anchor=params['query']['package_id'] if params['query'].get('binding')=='external' else request.binding.context['package_id']
                    query_record,_=resolver.record(params['query'],query_anchor)
                    keys=resolver.payload(query['keys'],query_record['payload']['reference_context']['package_id'],self.payloads)
                    if keys!={'request_occurrence':params['request_to_reconcile']}:raise ExecutionError('s3.owner_query_identity_mismatch')
                    if query['retention']!=contract('owner_retained_requests') or query['negative_coverage']!=contract('owner_exact_request_history'):raise ExecutionError('s3.owner_query_coverage_uninterpreted')
                    lost=db.execute('SELECT * FROM requests WHERE id=?',(params['request_to_reconcile'],)).fetchone()
                    if lost is None:decision='unresolved'
                    elif lost['correlation']!=request.correlation:raise ExecutionError('s3.owner_query_identity_mismatch')
                    else:
                        prior.append(json.loads(lost['receipt']))
                        lost_view=codec.parse_snapshot(bytes(db.execute('SELECT data FROM views WHERE id=?',(lost['view_id'],)).fetchone()[0]),self.limits)
                        lost_receipt=next(r for r in lost_view.records if r['id']==prior[-1]['target'])
                        decision=lost_receipt['payload']['decision']
                elif method=='renew':
                    if row is None or status!='active':raise ExecutionError('s3.owner_hold_not_active')
                    validity=self._payload(params['extension'],request,resolver,'validity')
                    if validity['owner']!=self.owner or validity['epoch']!=epoch or validity['scope']!=scope(native_binding_ref(request.binding)):raise ExecutionError('s3.owner_validity_scope_mismatch')
                    until=validity['valid_until']
                    if until['state']!='known' or until['value']['time_type']!='native_report':raise ExecutionError('s3.owner_clock_domain_unestablished')
                    if until['value']['timezone']!=known('owner_control_clock'):raise ExecutionError('s3.owner_clock_domain_unestablished')
                    expires=int(until['value']['text'])
                    if expires<=self._now():raise ExecutionError('s3.owner_extension_expired')
                elif method=='settle':
                    if row is None:raise ExecutionError('s3.owner_subject_not_established')
                    if params['aggregation']!=contract('s3.aggregation.replace_then_disjoint_members'):raise ExecutionError('s3.aggregation_uninterpreted')
                    facts=[e for e in request.evidence.entries if e.record['record_type']=='s3.resource_entry' and e.record['payload']['entry_kind']=='bill']
                    if not facts:decision='held'
                    else:
                        from .accounting import resource_total
                        by_resource={}
                        for e in facts:by_resource.setdefault(e.record['payload']['resource']['name'],[]).append(e)
                        for name,values in by_resource.items():
                            if name not in self.resources:raise ExecutionError('s3.owner_resource_or_unit_uninterpreted')
                            if any(e.record['payload']['owner']!=self.owner or e.record['payload']['unit']!=self.units[name] or e.record['payload']['scope']!=scope(native_binding_ref(request.binding)) for e in values):raise ExecutionError('s3.owner_bill_scope_mismatch')
                            total=resource_total(tuple(values))
                            if total.issues:decision='held';break
                            db.execute('INSERT INTO charges VALUES(?,?,?) ON CONFLICT(correlation,resource) DO UPDATE SET quantity=excluded.quantity',
                                (request.correlation,name,total.quantity['value']['text']))
                            entries.append(('settlement',{'resource':contract(name),'quantity':total.quantity['value']},'final'))
                        if decision=='permitted':status='settled'
                elif method=='release':
                    if row is None:raise ExecutionError('s3.owner_subject_not_established')
                    if params['release_rule']!=contract('owner_release_capacity_only'):raise ExecutionError('s3.owner_release_rule_uninterpreted')
                    status='released';entries=[('release',a,'final') for a in amounts]
                elif method=='authorize':
                    validity=self._payload(params['validity'],request,resolver,'validity')
                    if any(effect not in self.native_operations for effect in params['effects']) or request.binding.record['payload']['operation'] not in params['effects']:decision='denied'
                    if validity['owner']!=self.owner or validity['epoch']!=epoch or validity['scope']!=scope(native_binding_ref(request.binding)):decision='denied'
                    until=validity['valid_until']
                    if until['state']!='known' or until['value']['time_type']!='native_report' or until['value']['timezone']!=known('owner_control_clock'):
                        decision='held'
                    else:
                        selected_expiry=min(expires,int(until['value']['text']))
                        if selected_expiry<=self._now():decision='denied'
                        if decision=='permitted':expires=selected_expiry
                    if self.resources and not amounts:decision='held'
                new_revision=str(int(revision)+1)
                receipt,view,dependencies=self._emit(request,resolver,decision,new_revision,epoch,expires,entries,prior)
                for v in (*dependencies,view):
                    old=db.execute('SELECT data FROM views WHERE id=?',(v.package_id,)).fetchone()
                    if old and bytes(old[0])!=v.source_bytes:raise ExecutionError('s3.owner_evidence_identity_conflict')
                    db.execute('INSERT OR IGNORE INTO views VALUES(?,?)',(v.package_id,v.source_bytes))
                if method!='reconcile' or row is not None:
                    db.execute('INSERT INTO subjects VALUES(?,?,?,?,?,?,?) ON CONFLICT(correlation) DO UPDATE SET amounts=excluded.amounts,status=excluded.status,expires=excluded.expires,epoch=excluded.epoch,receipt=excluded.receipt',
                        (request.correlation,canonical(bound),canonical(amounts),status,str(expires),epoch,canonical(receipt)))
                db.execute('INSERT INTO requests VALUES(?,?,?,?,?)',(request.request_occurrence,canonical(fingerprint),request.correlation,canonical(receipt),view.package_id))
                db.execute('UPDATE meta SET value=? WHERE key=?',(new_revision.encode(),'revision'))
                if getattr(context,'fault',None):context.fault('before_owner_commit')
                db.execute('COMMIT')
                if getattr(context,'fault',None):context.fault('after_owner_commit')
                current=db.execute('SELECT * FROM subjects WHERE correlation=?',(request.correlation,)).fetchone()
            grant=self._live_grant(current,request) if decision=='permitted' else None
            return api.CallResult('completed',api.OwnerReceiptAndOptionalLiveGrant(receipt,new_revision,grant,()),records=api.RecordDelta(dependencies=(*dependencies,view,*self._control_frame(context))))
        except ExecutionError as exc:return api.rejected(exc.code)
        except Exception:return api.rejected('s3.owner_reply_unconfirmed')

    def reserve(self,request,context):return self._request('reserve',request,context)
    def reconcile(self,request,context):return self._request('reconcile',request,context)
    def renew(self,request,context):return self._request('renew',request,context)
    def settle(self,request,context):return self._request('settle',request,context)
    def release(self,request,context):return self._request('release',request,context)
    def authorize(self,request,context):return self._request('authorize',request,context)

    def inspect(self,binding,context):
        try:
            self._control(context,'s3.owner.inspect',binding.record['id'])
            with self._db() as db:revision=self._revision(db)
            availability=api.RequirementEvaluation(self.requirements,(),(),(),self.frontier)
            return api.CallResult('completed',api.OwnerSnapshot(self.owner,known(revision),availability,api.RecordDelta(dependencies=self._control_frame(context))))
        except ExecutionError as exc:return api.rejected(exc.code)

    def check(self,grant,binding,boundary,context):
        try:
            validate_value(boundary,'Contract')
            self._control(context,'s3.owner.check',binding.record['id'])
            body=self._grants.get(grant) if isinstance(grant,api.OpaqueGrant) else None
            if body is None:raise ExecutionError('s3.actual_live_owner_grant_required')
            self.authority.check(grant,body)
            with self._db() as db:
                row=db.execute('SELECT * FROM subjects WHERE correlation=?',(body['correlation'],)).fetchone()
                epoch=self._epoch(db)
            if body['binding']!=binding_digest(binding) or body['operation']!=boundary or body['epoch']!=epoch or row is None or self._now()>=min(int(body['expires']),int(row['expires'])) or row['status']!='active' or row['epoch']!=epoch:
                raise ExecutionError('s3.owner_grant_not_current')
            return api.CallResult('completed',api.ValidityReceipt(binding_digest(binding),self.owner,'permitted',api.RecordDelta()))
        except ExecutionError as exc:return api.rejected(exc.code)

    def rotate_epoch(self,context):
        self._control(context,'s3.owner.check','epoch_transition')
        with self._db() as db:
            db.execute('BEGIN IMMEDIATE');epoch=str(int(self._epoch(db))+1)
            db.execute('UPDATE meta SET value=? WHERE key=?',(epoch.encode(),'epoch'));db.execute('COMMIT')
        return epoch
