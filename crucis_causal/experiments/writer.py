"""Atomic staged S2 metadata, with actual implementation provenance (DLV-08/09)."""
import copy
import hashlib
import json
from pathlib import Path
from .api import RecordDelta,PlanReadContext,DraftContext,PackageView,ResolvedPlanRecord
from .codec import dumps,validate_package,record_bytes
from .errors import ServiceError
from .model import contract,known,unknown,source,reference,scope,index,identity,digest,walk
from .resolver import ReadAccess,parse_snapshot
from .services import ClockService,IdentityService,FamilyRegistry

def implementation():
    root=Path(__file__).parent
    return {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.iterdir()) if p.suffix in ('.py','.json','.txt')}

class S2RecordWriter:
    def __init__(self,base,access,limits,*,identities=None,clock=None,name='S2 metadata recorder'):
        self.identities=identities or IdentityService();self.clock=clock or ClockService()
        self.base,self.access,self.limits=base,access,limits
        self.package_id=self.identities.allocate();self._records={};self._external={};self._active=False
        self.producer=reference(self.identities.allocate(),'component')
        # S1 captures the bytes; the new S2 component explicitly identifies S2's
        # own implementation, rather than borrowing S1 Builder's default manifest.
        from crucis_causal.connections.model import Builder,contract as c1
        from crucis_causal.connections.evidence import capture_bytes
        from crucis_causal.connections.codec import dumps as s1dumps
        b=Builder('S1 byte capture for S2 provenance')
        artifact=capture_bytes(b,record_bytes(implementation()),format_contract=c1('s2.code_identity_manifest'),basis='observed')
        view=parse_snapshot(s1dumps(b.package([artifact])),limits)
        self.base=self.base.with_view(view)
        self.access=ReadAccess(frozenset(set(access.packages)|{view.package_id,self.package_id}))
        ref=reference(artifact['target'],'s1.artifact_snapshot',view.package_id)
        self._declare(ref)
        payload={'name':name,'role':'s2.observer','version':known(contract('s2.experiment_package')['version']),
            'implementation':known({'artifact':ref,'selector':known({'selector_type':'json_pointer','pointer':''})}),
            'configuration':unknown(),'source':source(self.producer,basis='intrinsic')}
        self._records[self.producer['target']]=self._envelope('s2.component',payload,self.producer['target'])
    def _declare(self,ref):
        if ref.get('binding')!='external' or ref['package_id']==self.package_id:return
        view=self.base.lookup(ref['package_id'],self.access,self.limits)
        if view is None:raise ServiceError('s2.explicit_dependency_snapshot_required')
        self._external[view.package_id]={'package_id':view.package_id,'format':view.format,'locator':unknown(),
            'expected_digest':known(view.snapshot_digest),'access':'s2.supplied_metadata'}
    def _envelope(self,kind,payload,rid):
        return {'id':rid,'record_type':kind,'contract':contract(kind),'producer':copy.deepcopy(self.producer),
            'created_at':known(self.clock.now()),'payload':copy.deepcopy(payload),'extensions':[]}
    def _package(self,roots=()):
        return {'format':contract('s2.experiment_package'),'package_id':self.package_id,
            'roots':list(roots) or [self.producer],'records':list(copy.deepcopy(self._records).values()),
            'external_packages':copy.deepcopy(list(self._external.values())),'extensions':[]}
    def view(self):
        p=self._package();raw=dumps(p,self.limits);return parse_snapshot(raw,self.limits)
    def frozen(self,roots=()):
        p=self._package(roots);p['package_id']=self.identities.allocate();raw=dumps(p,self.limits)
        return parse_snapshot(raw,self.limits)
    def begin(self,author,clock):
        if self._active or author!=self.producer or clock is not self.clock:raise ServiceError('s2.transaction_scope_mismatch')
        self._active=True;self._transaction=Transaction(self);return self._transaction
    def add(self,kind,payload,record_id=None):
        if not self._active:raise ServiceError('s2.transaction_required')
        return self._transaction.add(kind,payload,record_id)
    def get(self,ref):
        if ref.get('binding')!='internal' or ref.get('target') not in self._records:raise ServiceError('s2.staging_record_unavailable')
        r=self._records[ref['target']]
        if r['record_type']!=ref['target_type']:raise ServiceError('s2.reference_target')
        return copy.deepcopy(r)
    def ingest(self,records):
        if not self._active:raise ServiceError('s2.transaction_required')
        for r in records:
            old=self._records.get(r['id'])
            if old is not None and record_bytes(old)!=record_bytes(r):raise ServiceError('s2.record_identity_conflict')
            baseline=self.base._records.get(r['id'])
            if baseline is not None and record_bytes(baseline)!=record_bytes(r):raise ServiceError('s2.record_identity_conflict')
        for r in records:
            for _,ref,_ in walk(r):
                if isinstance(ref,dict) and 'binding' in ref:self._declare(ref)
            self._records[r['id']]=copy.deepcopy(r)
    def snapshot(self):return RecordDelta(tuple(copy.deepcopy(list(self._records.values()))),())
    def context(self,registry=None):
        overlay=OverlayResolver(self)
        read=PlanReadContext(self.limits,overlay,registry or FamilyRegistry(),WriterReadAccess(self),self.package_id)
        return DraftContext(read,self.identities,self,self.producer,self.clock)

class WriterReadAccess:
    """Live explicit metadata-input scope; never a native execution capability."""
    def __init__(self,writer):self.writer=writer
    def permits(self,pid,purpose):return self.writer.access.permits(pid,purpose)
    @property
    def packages(self):return self.writer.access.packages

class Transaction:
    def __init__(self,writer):
        self.writer=writer;self.before=copy.deepcopy(writer._records);self.external=copy.deepcopy(writer._external);self.closed=False
        self.base,self.access=writer.base,writer.access
    def add(self,kind,payload,record_id=None):
        if self.closed:raise ServiceError('s2.closed_transaction')
        kind=kind if '.' in kind else 's2.'+kind;rid=record_id or self.writer.identities.allocate()
        if rid in self.writer._records:raise ServiceError('s2.record_identity_conflict')
        r=self.writer._envelope(kind,payload,rid)
        from jsonschema import Draft202012Validator
        from .schema import _schema
        spec={'$defs':_schema()['$defs'],'$ref':'#/$defs/Record'}
        if not Draft202012Validator(spec).is_valid(r):raise ServiceError('s2.record_schema')
        for _,ref,_ in walk(r):
            if isinstance(ref,dict) and 'binding' in ref:self.writer._declare(ref)
        self.writer._records[rid]=r
        return reference(rid,kind)
    def get(self,ref):return self.writer.get(ref)
    def ingest(self,records):return self.writer.ingest(records)
    def snapshot(self):return RecordDelta(tuple(copy.deepcopy(r) for rid,r in self.writer._records.items() if rid not in self.before),())
    def commit(self):
        if self.closed:raise ServiceError('s2.closed_transaction')
        try:validate_package(self.writer._package(),self.writer.limits)
        except Exception:self.discard();raise
        result=self.snapshot();self.closed=True;self.writer._active=False;return result
    def discard(self):
        if not self.closed:
            self.writer._records=self.before;self.writer._external=self.external;self.writer.base=self.base;self.writer.access=self.access;self.closed=True;self.writer._active=False
    def __enter__(self):return self
    def __exit__(self,typ,value,tb):
        if not self.closed:self.discard()

class OverlayResolver:
    """One explicit transaction scope over immutable supplied snapshots."""
    def __init__(self,writer):self.writer=writer
    def lookup(self,pid,access,limits):
        if pid==self.writer.package_id:
            if not access.permits(pid,contract('s2.metadata_read')):raise ServiceError('s2.access_denied')
            return self.writer.view()
        return self.writer.base.lookup(pid,access,limits)
    def record(self,ref,anchor,access,limits):
        if anchor==self.writer.package_id:
            if not access.permits(anchor,contract('s2.metadata_read')):raise ServiceError('s2.access_denied')
            if ref.get('binding')=='internal' or (ref.get('binding')=='external' and ref['package_id']==anchor):
                return ResolvedPlanRecord(self.writer.get({k:v for k,v in ref.items() if k!='package_id'}|{'binding':'internal'}),anchor)
            if ref.get('binding')=='external':
                view=self.writer.base.lookup(ref['package_id'],access,limits)
                if view is None:raise ServiceError('s2.package_unavailable')
                return self.writer.base.record(reference(ref['target'],ref['target_type']),view.package_id,access,limits)
            raise ServiceError('s2.unresolved_reference')
        return self.writer.base.record(ref,anchor,access,limits)
    def closure(self,pid,access,limits):
        if pid!=self.writer.package_id:return self.writer.base.closure(pid,access,limits)
        view=self.writer.view();temp=self.writer.base.with_view(view)
        return temp.closure(pid,access,limits)
    def with_view(self,view):
        # A new immutable read view does not mutate this writer or its base.
        return self.writer.base.with_view(view)
    def payload(self,ref,anchor,access,limits):
        from .payloads import read
        return read(ref,anchor,self,access,limits)
