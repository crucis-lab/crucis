"""Trusted-interface input custody, explicit scope and diagnostic retention.

DLV-08/09. Local cooperative storage and issuer-held handles only. No claim of
OS isolation, global erasure, source authenticity or prevention of native copying.
"""
import copy
from contextlib import contextmanager
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import sqlite3
import threading
import weakref
from . import api
from .authority import Authority
from .model import ExecutionError,canonical,contract,digest,identity,known,unknown
from .registry import callable_value
from .schema import validate_value
from .store import ArtifactStore

@dataclass(frozen=True,slots=True)
class InputMember:
    name:str
    source:dict
    bytes:bytes
    digest:dict
    format:dict
    def __post_init__(self):
        validate_value(self.name,'Code');validate_value(self.source,'Ref');validate_value(self.format,'Contract')
        if not isinstance(self.bytes,bytes) or digest(self.bytes)!=self.digest:raise ExecutionError('s3.input_content_changed')

@dataclass(frozen=True,slots=True)
class StageReceipt:
    correlation:str
    recipient:dict
    state:str
    members:tuple
    consumed:str
    remaining:str
    epoch:str
    handle:api.OpaqueHandle|None
    scope:str='Trusted custodian interface only; actual native use and other copies unestablished'

class RuntimeSecrets:
    """Configured runtime values; no manifest/log/export or ambient lookup API.

    Exact already-supplied callable identities can be authorized to receive a
    configured slot. Holding this object never grants an operation permission.
    Redaction protects configured sentinels only, not unknown-secret detection.
    """
    __slots__=('_slots','_receivers')
    def __init__(self,slots,receivers=()):
        if any(not isinstance(k,str) or not isinstance(v,bytes) or not v for k,v in slots.items()):raise ExecutionError('s3.explicit_runtime_secret_slots_required')
        self._slots=dict(slots);self._receivers=tuple(receivers)
        for receiver in receivers:callable_value(receiver)
    def __repr__(self):return '<private runtime slots>'
    def __reduce__(self):raise TypeError('runtime slots cannot be serialized')
    def __copy__(self):raise TypeError('runtime slots cannot be copied')
    def __deepcopy__(self,memo):raise TypeError('runtime slots cannot be copied')
    def safe(self,raw):return isinstance(raw,bytes) and all(value not in raw for value in self._slots.values())
    def redact(self,raw):
        if not isinstance(raw,bytes):raise ExecutionError('s3.diagnostic_bytes_required')
        result=raw
        for value in sorted(self._slots.values(),key=len,reverse=True):result=result.replace(value,b'[redacted runtime value]')
        if not self.safe(result):raise ExecutionError('s3.redaction_not_established')
        return result
    def invoke(self,receiver,slots,arguments):
        if not any(receiver is allowed for allowed in self._receivers):raise ExecutionError('s3.secret_receiver_not_authorized')
        if not isinstance(slots,tuple) or any(slot not in self._slots for slot in slots):raise ExecutionError('s3.runtime_secret_slot_unavailable')
        return callable_value(receiver)(arguments,{slot:self._slots[slot] for slot in slots})

@dataclass(frozen=True,slots=True)
class DiagnosticView:
    bytes:bytes
    relation:str
    procedure:dict
    original:dict
    limitation:str

def restricted_diagnostic(raw,secrets):
    """A derived redaction is never labeled the original captured diagnostic."""
    if not isinstance(secrets,RuntimeSecrets):raise ExecutionError('s3.explicit_diagnostic_policy_required')
    return DiagnosticView(secrets.redact(raw),'derived_redaction',contract('s3.redaction.configured_runtime_slots'),
        unknown('s3.raw_diagnostic_not_retained_by_policy'),
        'Raw original unavailable under this retention policy; no original-byte verification claim')

class EndpointOwner:
    """Explicit bounded local endpoint authority; no raw dataset is invented.

    Process-local native fixture profile. A new instance has a new namespace;
    old grants/proxies cannot be recreated from descriptors. Query consumption
    survives proxy duplication/revocation within this actual owner instance.
    There is no durable/global exposure-budget or cross-process handle claim.
    """
    def __init__(self,component,endpoint,operation,method,*,generation='initial',max_queries='1'):
        validate_value(component,'KnownRef');validate_value(endpoint,'KnownRef(s1.endpoint)')
        validate_value(operation,'Contract');validate_value(max_queries,'PositiveIndex')
        if not isinstance(generation,str) or not generation:raise ExecutionError('s3.endpoint_generation_required')
        import inspect
        if list(inspect.signature(callable_value(method)).parameters)!=['arguments']:raise ExecutionError('s3.endpoint_signature')
        self._component=copy.deepcopy(component);self._endpoint=copy.deepcopy(endpoint);self._operation=copy.deepcopy(operation)
        self._namespace=identity();self._generation=generation;self._method=method;self._maximum=int(max_queries);self._consumed=0
        self._authority=Authority();self._grants=weakref.WeakKeyDictionary();self._proxies=weakref.WeakKeyDictionary()
        self._delegations={};self._events=[];self._lock=threading.RLock()
    @property
    def component(self):return copy.deepcopy(self._component)
    @property
    def endpoint(self):return copy.deepcopy(self._endpoint)
    @property
    def operation(self):return copy.deepcopy(self._operation)
    @property
    def namespace(self):return self._namespace
    @property
    def generation(self):return self._generation
    @property
    def maximum(self):return self._maximum
    @property
    def consumed(self):return self._consumed
    def grant(self,recipient):
        """Actual source-owner bootstrap, never a coordinator metadata conversion."""
        validate_value(recipient,'KnownRef')
        body={'namespace':self._namespace,'generation':self._generation,'endpoint':self._endpoint,'recipient':recipient,'maximum_queries':str(self._maximum)}
        cap=self._authority.issue(body);self._grants[cap]=body;return cap
    def describe(self,grant):
        # Supplied runtime binding description; no endpoint call or budget debit.
        with self._lock:
            body=self._grants.get(grant) if isinstance(grant,api.OpaqueGrant) else None
            if body is None:raise ExecutionError('s3.actual_endpoint_grant_required')
            return copy.deepcopy(body)
    def current(self,grant):
        """Pure local issuer check; no endpoint query, new right or quota debit."""
        with self._lock:
            body=self.describe(grant);self._authority.check(grant,body)
            if body['generation']!=self._generation:raise ExecutionError('s3.endpoint_binding_not_current')
            if self._consumed>=min(self._maximum,int(body['maximum_queries'])):raise ExecutionError('s3.endpoint_allowance_exhausted')
            return body
    def delegate(self,correlation,grant,recipient,*,namespace,generation):
        validate_value(correlation,'ID')
        with self._lock:
            body=self._grants.get(grant) if isinstance(grant,api.OpaqueGrant) else None
            if body is None:raise ExecutionError('s3.actual_endpoint_grant_required')
            self._authority.check(grant,body)
            if namespace!=self._namespace or generation!=self._generation or body['generation']!=self._generation or body['recipient']!=recipient:
                raise ExecutionError('s3.endpoint_binding_not_current')
            if self._consumed>=min(self._maximum,int(body['maximum_queries'])):raise ExecutionError('s3.endpoint_allowance_exhausted')
            bound=canonical({'endpoint':self._endpoint,'namespace':namespace,'generation':generation,'recipient':recipient})
            prior=self._delegations.get(correlation)
            if prior is not None and prior!=bound:raise ExecutionError('s3.endpoint_delegation_conflict')
            self._delegations[correlation]=bound
            proxy=api.OpaqueHandle(api._OPAQUE_KEY,self);self._proxies[proxy]=(correlation,grant,generation)
            return proxy
    def query(self,proxy,arguments):
        if not isinstance(arguments,bytes):raise ExecutionError('s3.endpoint_argument_bytes_required')
        with self._lock:
            bound=self._proxies.get(proxy) if isinstance(proxy,api.OpaqueHandle) else None
            if bound is None or bound[2]!=self._generation:raise ExecutionError('s3.actual_current_endpoint_proxy_required')
            body=self._grants.get(bound[1]);self._authority.check(bound[1],body)
            if self._consumed>=min(self._maximum,int(body['maximum_queries'])):raise ExecutionError('s3.endpoint_allowance_exhausted')
            self._consumed+=1;event={'occurrence':identity(),'delegation':bound[0],'namespace':self._namespace,
                'generation':self._generation,'ordinal':str(self._consumed),'outcome':'unconfirmed'}
            self._events.append(event)
        # Do not log arguments, bearer values or a raw diagnostic on exception.
        result=callable_value(self._method)(arguments)
        if not isinstance(result,bytes):raise ExecutionError('s3.endpoint_response_bytes_unestablished')
        with self._lock:event['outcome']='returned'
        return result
    def revoke(self,grant):
        with self._lock:self._authority.revoke(grant);self._grants.pop(grant,None)
    def events(self):
        with self._lock:return tuple(copy.deepcopy(self._events))

DDL='''
CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY,value BLOB NOT NULL);
CREATE TABLE IF NOT EXISTS stages(id TEXT PRIMARY KEY,fingerprint BLOB NOT NULL,recipient BLOB NOT NULL,expected INTEGER NOT NULL,status TEXT NOT NULL,epoch TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS members(stage TEXT NOT NULL REFERENCES stages(id),name TEXT NOT NULL,descriptor BLOB NOT NULL,PRIMARY KEY(stage,name));
'''

class LocalCustodian:
    """Explicit namespace-owner service; its handles enforce this read interface.

    Partial transfer reaches the custodian. Activation is coherent for the named
    recipient at this interface. A receipt does not prove native access/use.
    Namespace-admin methods are not a replacement for DriverBoundary admission.
    """
    def __init__(self,root,*,max_stages='100',max_bytes='67108864'):
        validate_value(max_stages,'PositiveIndex')
        self.root=Path(root).resolve()
        if str(self.root).startswith('\\\\'):raise ExecutionError('s3.network_custody_not_qualified')
        self.root.mkdir(parents=True,exist_ok=True);self.path=self.root/'custody.sqlite3'
        self.artifacts=ArtifactStore(self.root/'objects',max_bytes=max_bytes)
        self.authority=Authority();self._controls=weakref.WeakKeyDictionary();self._handles=weakref.WeakKeyDictionary();self._lock=threading.RLock()
        config={'max_stages':max_stages,'max_bytes':max_bytes,'code':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'consumption_rule':contract('s3.custody.per_accepted_stage')}
        with self._db() as db:
            db.executescript(DDL);db.execute('BEGIN IMMEDIATE')
            old=db.execute('SELECT value FROM meta WHERE key=?',('config',)).fetchone()
            if old and json.loads(old[0])!=config:raise ExecutionError('s3.custody_configuration_or_code_drift')
            if old is None:
                for key,value in [('config',canonical(config)),('epoch',b'0'),('consumed',b'0'),('identity',identity().encode())]:
                    db.execute('INSERT INTO meta VALUES(?,?)',(key,value))
            self._namespace=bytes(db.execute('SELECT value FROM meta WHERE key=?',('identity',)).fetchone()[0]).decode()
            db.execute('COMMIT')
        self._maximum=int(max_stages)

    @property
    def namespace(self):return self._namespace
    @property
    def maximum(self):return self._maximum

    @contextmanager
    def _db(self):
        db=sqlite3.connect(self.path,timeout=5,isolation_level=None);db.row_factory=sqlite3.Row
        try:
            if db.execute('PRAGMA journal_mode=DELETE').fetchone()[0].lower()!='delete':raise ExecutionError('s3.custody_storage_profile')
            db.execute('PRAGMA synchronous=FULL');db.execute('PRAGMA foreign_keys=ON')
            if db.execute('PRAGMA synchronous').fetchone()[0]!=2 or db.execute('PRAGMA foreign_keys').fetchone()[0]!=1:
                raise ExecutionError('s3.custody_storage_profile')
            yield db
        finally:db.close()

    def control(self,rights=('transfer','inspect','activate','revoke','takeover')):
        if not rights or any(r not in ('transfer','inspect','activate','revoke','takeover') for r in rights):raise ExecutionError('s3.custody_right_unavailable')
        body={'namespace':self.namespace,'rights':list(rights)}
        cap=self.authority.issue(body,control=True);self._controls[cap]=body;return cap

    def _check(self,control,right):
        body=self._controls.get(control) if isinstance(control,api.OpaqueControlCapability) else None
        if body is None or right not in body['rights']:raise ExecutionError('s3.custody_control_denied')
        self.authority.check(control,body)

    def epoch(self,control):
        self._check(control,'inspect')
        with self._db() as db:return bytes(db.execute('SELECT value FROM meta WHERE key=?',('epoch',)).fetchone()[0]).decode()

    def transfer(self,correlation,binding,recipient,members,control,*,expected_epoch,fault=None):
        self._check(control,'transfer');validate_value(correlation,'ID');validate_value(recipient,'KnownRef')
        validate_value(binding,'Digest')
        if not isinstance(members,tuple) or not members or len({m.name for m in members})!=len(members) or any(not isinstance(m,InputMember) for m in members):raise ExecutionError('s3.complete_input_member_set_required')
        if sum(len(m.bytes) for m in members)>self.artifacts.max_bytes:raise ExecutionError('s3.staging_byte_limit')
        descriptions=copy.deepcopy([{'name':m.name,'source':m.source,'digest':m.digest,'format':m.format} for m in members])
        fingerprint=canonical({'binding':binding,'recipient':recipient,'members':descriptions,'epoch':expected_epoch})
        with self._db() as db:
            db.execute('BEGIN IMMEDIATE');epoch=bytes(db.execute('SELECT value FROM meta WHERE key=?',('epoch',)).fetchone()[0]).decode()
            if epoch!=expected_epoch:raise ExecutionError('s3.custody_epoch_conflict')
            old=db.execute('SELECT * FROM stages WHERE id=?',(correlation,)).fetchone()
            if old:
                if bytes(old['fingerprint'])!=fingerprint:raise ExecutionError('s3.staging_correlation_conflict')
                # Receiver replay returns the existing partial/complete result;
                # it never implicitly resumes an uncertain prior transfer.
                db.execute('COMMIT');return self.inspect(correlation,control)
            consumed=int(bytes(db.execute('SELECT value FROM meta WHERE key=?',('consumed',)).fetchone()[0]))
            if consumed>=self.maximum:raise ExecutionError('s3.local_exposure_allowance_exhausted')
            db.execute('INSERT INTO stages VALUES(?,?,?,?,?,?)',(correlation,fingerprint,canonical(recipient),len(members),'partial',epoch))
            db.execute('UPDATE meta SET value=? WHERE key=?',(str(consumed+1).encode(),'consumed'));db.execute('COMMIT')
        if fault:fault('after_stage_acceptance')
        for pos,member in enumerate(members):
            installed=self.artifacts.stage(member.bytes)
            if installed!=descriptions[pos]['digest']:raise ExecutionError('s3.staged_input_digest_mismatch')
            with self._db() as db:
                db.execute('BEGIN IMMEDIATE')
                epoch=bytes(db.execute('SELECT value FROM meta WHERE key=?',('epoch',)).fetchone()[0]).decode()
                if epoch!=expected_epoch:raise ExecutionError('s3.custody_epoch_conflict')
                row=db.execute('SELECT status FROM stages WHERE id=?',(correlation,)).fetchone()
                if row['status']!='partial':raise ExecutionError('s3.staging_no_longer_writable')
                db.execute('INSERT INTO members VALUES(?,?,?)',(correlation,member.name,canonical(descriptions[pos])));db.execute('COMMIT')
            if fault:fault('after_stage_member_'+str(pos))
        with self._db() as db:
            db.execute('BEGIN IMMEDIATE')
            if bytes(db.execute('SELECT value FROM meta WHERE key=?',('epoch',)).fetchone()[0]).decode()!=expected_epoch:raise ExecutionError('s3.custody_epoch_conflict')
            db.execute('UPDATE stages SET status=? WHERE id=?',('complete',correlation));db.execute('COMMIT')
        if fault:fault('after_stage_complete')
        return self.inspect(correlation,control)

    def inspect(self,correlation,control):
        self._check(control,'inspect')
        with self._db() as db:
            row=db.execute('SELECT * FROM stages WHERE id=?',(correlation,)).fetchone()
            if row is None:raise ExecutionError('s3.staging_occurrence_unestablished')
            members=tuple(json.loads(r[0]) for r in db.execute('SELECT descriptor FROM members WHERE stage=? ORDER BY name',(correlation,)))
            consumed=int(bytes(db.execute('SELECT value FROM meta WHERE key=?',('consumed',)).fetchone()[0]))
            return StageReceipt(correlation,json.loads(row['recipient']),row['status'],members,str(consumed),str(self.maximum-consumed),row['epoch'],None)

    def activate(self,correlation,recipient,control,*,expected_epoch,fault=None):
        self._check(control,'activate')
        with self._db() as db:
            db.execute('BEGIN IMMEDIATE')
            row=db.execute('SELECT * FROM stages WHERE id=?',(correlation,)).fetchone()
            epoch=bytes(db.execute('SELECT value FROM meta WHERE key=?',('epoch',)).fetchone()[0]).decode()
            if row is None or row['status'] not in ('complete','active') or row['epoch']!=epoch or epoch!=expected_epoch or json.loads(row['recipient'])!=recipient:
                raise ExecutionError('s3.coherent_activation_unestablished')
            members=tuple(json.loads(r[0]) for r in db.execute('SELECT descriptor FROM members WHERE stage=?',(correlation,)))
            if len(members)!=row['expected']:raise ExecutionError('s3.coherent_activation_unestablished')
            for member in members:self.artifacts.read(member['digest'])
            db.execute('UPDATE stages SET status=? WHERE id=?',('active',correlation));db.execute('COMMIT')
        if fault:fault('after_stage_activation')
        handle=api.OpaqueHandle(api._OPAQUE_KEY,self)
        with self._lock:self._handles[handle]=(correlation,canonical(recipient),expected_epoch)
        receipt=self.inspect(correlation,control)
        return StageReceipt(receipt.correlation,receipt.recipient,receipt.state,receipt.members,receipt.consumed,receipt.remaining,receipt.epoch,handle)

    def read(self,handle,name):
        with self._lock:binding=self._handles.get(handle) if isinstance(handle,api.OpaqueHandle) else None
        if binding is None:raise ExecutionError('s3.actual_custody_handle_required')
        correlation,recipient,epoch=binding
        with self._db() as db:
            db.execute('BEGIN')
            current=bytes(db.execute('SELECT value FROM meta WHERE key=?',('epoch',)).fetchone()[0]).decode()
            row=db.execute('SELECT * FROM stages WHERE id=?',(correlation,)).fetchone()
            member=db.execute('SELECT descriptor FROM members WHERE stage=? AND name=?',(correlation,name)).fetchone()
            if row is None or row['status']!='active' or current!=epoch or row['epoch']!=epoch or bytes(row['recipient'])!=recipient or member is None:
                raise ExecutionError('s3.custody_access_not_current')
            raw=self.artifacts.read(json.loads(member[0])['digest']);db.execute('COMMIT')
            return raw

    def revoke(self,correlation,control,*,expected_epoch):
        self._check(control,'revoke')
        with self._db() as db:
            db.execute('BEGIN IMMEDIATE')
            epoch=bytes(db.execute('SELECT value FROM meta WHERE key=?',('epoch',)).fetchone()[0]).decode()
            row=db.execute('SELECT * FROM stages WHERE id=?',(correlation,)).fetchone()
            if epoch!=expected_epoch or row is None or row['epoch']!=epoch:raise ExecutionError('s3.custody_epoch_conflict')
            db.execute('UPDATE stages SET status=? WHERE id=?',('revoked',correlation));db.execute('COMMIT')
        return {'future_interface_access':'revoked','local_bytes':'retained','prior_disclosure':'unchanged',
            'other_copies':unknown('s3.other_copies_not_observed'),'allowance':self.inspect(correlation,control).remaining}

    def takeover(self,control,*,expected_epoch):
        self._check(control,'takeover')
        with self._db() as db:
            db.execute('BEGIN IMMEDIATE')
            epoch=bytes(db.execute('SELECT value FROM meta WHERE key=?',('epoch',)).fetchone()[0]).decode()
            if epoch!=expected_epoch:raise ExecutionError('s3.custody_epoch_conflict')
            value=str(int(epoch)+1);db.execute('UPDATE meta SET value=? WHERE key=?',(value.encode(),'epoch'));db.execute('COMMIT')
            return value
