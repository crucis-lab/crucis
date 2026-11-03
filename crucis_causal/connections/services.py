"""Injected local services, no implicit native execution grants (DLV-08/09)."""
import copy
import uuid

from .codec import WireError
from .model import Builder, contract, scope, source
from dataclasses import dataclass


class IdentityService:
    def __init__(self, store=None): self.store=store
    def allocate(self): return str(uuid.uuid4())
    def import_once(self, occurrence, bound_inputs, create):
        if self.store is None: raise WireError('persistent import identity requires an explicit store')
        return self.store.import_once(occurrence,bound_inputs,create)


class RecordBuffer:
    def __init__(self, builder=None): self.builder=builder or Builder()
    def add(self, kind, payload, record_id=None): return self.builder.add(kind,payload,record_id)
    def get(self, ref): return self.builder.get(ref)
    def snapshot(self): return tuple(self.builder.package([self.builder.producer])['records'])
    def ingest(self, records):
        from .codec import dumps
        staged=copy.deepcopy(list(records))
        for record in staged:
            old=self.builder._records.get(record['id'])
            if old is not None and dumps(old)!=dumps(record): raise WireError('record identity conflict during evidence ingestion')
        for record in staged:self.builder._records[record['id']]=record
    def gap(self, subjects, reason, evidence=()):
        return self.add('gap',{'subjects':list(subjects),'reasons':[reason],'scope':scope(*subjects),
            'source':source('observed',evidence,self.builder.producer)})


class CaptureSink:
    """Staging only: no publication or native occurrence allocation method."""
    def __init__(self, records, identities): self.records=records;self.identities=identities
    def capture(self, data, **kwargs):
        from .evidence import capture_bytes
        return capture_bytes(self.records.builder,data,**kwargs)


class ContractRegistry:
    """Offline, exact versions. A declaration does not install/load a dependency."""
    def __init__(self): self._routes={};self._rules={}
    @staticmethod
    def key(c): return c['name'],c['version']
    def register_route(self, operation, route_kind, *, dependencies=(), presentations=(), request_routes=()):
        key=self.key(operation),route_kind
        if key in self._routes: raise WireError('route contract already registered')
        self._routes[key]={'dependencies':copy.deepcopy(tuple(dependencies)), 'presentations':tuple(presentations),
            'request_routes':tuple(request_routes) or ('s1.'+route_kind,)}
    def route(self, operation, route_kind): return copy.deepcopy(self._routes.get((self.key(operation),route_kind)))
    def register_rule(self, rule, checker):
        key=self.key(rule)
        if key in self._rules: raise WireError('assessment rule already registered')
        self._rules[key]=checker
    def rule(self, rule): return self._rules.get(self.key(rule))


class MappingRegistry:
    def __init__(self, resolver): self.resolver=resolver
    def resolve(self, ref):
        record=self.resolver.record(ref)
        if record['record_type']!='s1.mapping': raise WireError('mapping reference required')
        return copy.deepcopy(record)


class HandleRegistry:
    def __init__(self): self._handles={};self._native={}
    def attach(self, handle):
        aid=handle.attempt['target']
        if aid in self._handles and self._handles[aid].transport_handle is not handle.transport_handle:
            raise WireError('another runtime handle already occupies attempt; preserve duplicate-launch doubt')
        identity=handle.native_identity
        if identity['state']=='known':
            n=identity['value'];key=(n['authority'],n['namespace'],n['native_id'])
            if key in self._native and self._native[key]!=aid: raise WireError('established native episode already bound to another attempt')
            self._native[key]=aid
        self._handles[aid]=handle
        return handle
    def reconnect(self, native_identity):
        n=native_identity;key=(n['authority'],n['namespace'],n['native_id'])
        if key not in self._native: raise WireError('native episode identity is unestablished; no inferred reconnect')
        return self._handles[self._native[key]]
    def get(self, attempt): return self._handles[attempt['target']]


class RuntimeAuthority:
    """Caller-owned authority; a JSON value or copied declaration cannot mint a capability.

    This checks supplied policy boundaries, not OS isolation against malicious
    Python callers. Only the execution owner should hold this issuing object.
    """
    def __init__(self): self._issued={};self._used=set()
    def issue(self, kind, binding):
        token=object();self._issued[token]=(kind,copy.deepcopy(binding));return token
    def check(self, token, kind, binding, *, consume=False):
        try: expected=self._issued.get(token)
        except TypeError: expected=None
        if expected != (kind,binding): raise WireError('runtime capability absent or does not match exact operation/effect scope')
        if consume:
            if token in self._used: raise WireError('execution/delivery capability already consumed; retry needs a new explicit grant')
            self._used.add(token)


def execution_binding(grant):
    return {'request':grant.request,'attempt':grant.attempt,'operations':grant.operations,'effects':grant.effects,
        'presentations':grant.presentations,'policies':grant.policies,'authority':grant.authority}


def delivery_binding(grant):
    return {'action':grant.action,'response':grant.response,'endpoint':grant.endpoint,'effects':grant.effects,
        'policies':grant.policies,'authority':grant.authority}


def cancellation_binding(grant):
    return {'attempt':grant.attempt,'policies':grant.policies,'authority':grant.authority}


@dataclass(frozen=True, slots=True)
class ActionChannel:
    endpoint: dict
    transmit: object
