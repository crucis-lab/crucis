"""Explicit supplied bytes only: no locator handlers or filesystem search (DLV-08/09)."""
import copy
from dataclasses import dataclass
from functools import lru_cache
from .api import PackageView, ResolvedPlanRecord
from .codec import loads, validate_package, record_bytes
from .errors import ServiceError
from .model import contract, digest, walk

@dataclass(frozen=True,slots=True)
class ReadAccess:
    packages:frozenset
    def permits(self,package_id,purpose):return package_id in self.packages

def _parse_snapshot(data,limits):
    # S1 owns its own schema/codec. Raw JSON numeric fields are allowed only in its
    # embedded native byte payloads, never promoted into an S2 semantic value.
    if len(data)>int(limits.max_manifest_bytes):raise ServiceError('s2.manifest_limit')
    from crucis_causal.connections.codec import loads as s1loads
    try:p=s1loads(data)
    except ValueError as exc:raise ServiceError('s2.invalid_snapshot') from exc
    if p.get('format',{}).get('name')=='s2.experiment_package':p=validate_package(loads(data,limits),limits)
    elif p.get('format',{}).get('name')=='s1.connection_package':
        from crucis_causal.connections.validation import validate_wire
        if len(p.get('records',[]))>int(limits.max_records):raise ServiceError('s2.record_limit')
        report=validate_wire(p)
        if not report.ok:raise ServiceError('s2.invalid_s1_snapshot',message=str(report.issues[:2]))
    else:raise ServiceError('s2.unsupported_package_format')
    return PackageView(p,data,digest(data))

@lru_cache(maxsize=64)
def _cached_snapshot(data,limits):return _parse_snapshot(data,limits)

def parse_snapshot(data,limits):
    if not isinstance(data,bytes):raise ServiceError('s2.immutable_snapshot_bytes_required')
    # Cache only exact immutable bytes and limits, never paths/mtime or access.
    # Bound retained raw bytes to 16 MiB; returned views are independent copies.
    view=_cached_snapshot(data,limits) if isinstance(data,bytes) and len(data)<=262144 else _parse_snapshot(data,limits)
    return PackageView(view.package,view.source_bytes,copy.deepcopy(view.snapshot_digest),view.resolved_packages)

class PlanResolver:
    def __init__(self,snapshots=(),*,limits):
        self.limits=limits;self._views={};self._records={};self._bounds_checked=set()
        for data in snapshots:self.add(parse_snapshot(data,limits))
    def add(self,view):
        if not isinstance(view,PackageView):raise ServiceError('s2.verified_snapshot_required')
        # Reparse, rather than trusting a caller-constructed view/digest.
        actual=parse_snapshot(view.source_bytes,self.limits)
        if actual.package!=view.package or actual.snapshot_digest!=view.snapshot_digest:raise ServiceError('s2.snapshot_view_mismatch')
        old=self._views.get(actual.package_id)
        if old and old.source_bytes!=actual.source_bytes:raise ServiceError('s2.package_identity_conflict')
        if not old and len(self._views)>=int(self.limits.max_packages):raise ServiceError('s2.package_count_limit')
        if not old and sum(len(v.source_bytes) for v in self._views.values())+len(actual.source_bytes)>int(self.limits.max_external_bytes):raise ServiceError('s2.external_byte_limit')
        for r in actual.records:
            old_record=self._records.get(r['id'])
            if old_record is not None and record_bytes(old_record)!=record_bytes(r):raise ServiceError('s2.record_identity_conflict')
        self._views[actual.package_id]=actual
        for r in actual.records:self._records[r['id']]=r
    def with_view(self,view):
        result=object.__new__(type(self));result.limits=self.limits;result._views=dict(self._views);result._records=copy.deepcopy(self._records);result._bounds_checked=set(self._bounds_checked)
        result.add(view);return result
    def _lookup(self,package_id,access,limits):
        if not access.permits(package_id,contract('s2.metadata_read')):raise ServiceError('s2.access_denied')
        view=self._views.get(package_id)
        if view and (package_id,limits) not in self._bounds_checked:
            if len(view.source_bytes)>int(limits.max_manifest_bytes):raise ServiceError('s2.manifest_limit')
            if len(view.records)>int(limits.max_records):raise ServiceError('s2.record_limit')
            if len(view.source_bytes)>int(limits.max_external_bytes):raise ServiceError('s2.external_byte_limit')
            if any(depth>int(limits.max_parameter_depth) for _,_,depth in walk(view.package)):raise ServiceError('s2.parameter_depth_limit')
            self._bounds_checked.add((package_id,limits))
        return view
    def lookup(self,package_id,access,limits):
        view=self._lookup(package_id,access,limits)
        return PackageView(view.package,view.source_bytes,copy.deepcopy(view.snapshot_digest),view.resolved_packages) if view else None
    def record(self,reference,anchor,access,limits):
        if reference.get('binding')=='unresolved':raise ServiceError('s2.unresolved_reference',evidence=reference.get('evidence',()))
        if not anchor:raise ServiceError('s2.reference_anchor_required')
        origin=self._lookup(anchor,access,limits)
        if origin is None:raise ServiceError('s2.package_unavailable')
        pid=anchor if reference['binding']=='internal' else reference['package_id']
        target=self._lookup(pid,access,limits)
        if target is None:raise ServiceError('s2.package_unavailable')
        if pid!=anchor:
            declared=next((d for d in origin._package['external_packages'] if d['package_id']==pid),None)
            if declared is None:raise ServiceError('s2.undeclared_external_package')
            expected=declared['expected_digest']
            if expected['state']=='known' and expected['value']!=target.snapshot_digest:raise ServiceError('s2.integrity_mismatch')
            if 'format' in declared and declared['format']!=target.format:raise ServiceError('s2.package_format_mismatch')
        record=next((r for r in target._package['records'] if r['id']==reference['target']),None)
        if record is None or record['record_type']!=reference['target_type']:raise ServiceError('s2.reference_target')
        return ResolvedPlanRecord(copy.deepcopy(record),pid,(),())
    def closure(self,pid,access,limits):
        seen=set();stack=set();result=[];total=0
        def visit(current,depth):
            nonlocal total
            if depth>int(limits.max_reference_depth):raise ServiceError('s2.reference_depth_limit')
            if current in stack:raise ServiceError('s2.package_dependency_cycle')
            if current in seen:return
            if len(seen)>=int(limits.max_packages):raise ServiceError('s2.package_count_limit')
            view=self._lookup(current,access,limits)
            if view is None:raise ServiceError('s2.package_unavailable')
            total+=len(view.source_bytes)
            if total>int(limits.max_external_bytes):raise ServiceError('s2.external_byte_limit')
            seen.add(current);stack.add(current);result.append(view)
            p=view._package
            for desc in p['external_packages']:
                other=self._lookup(desc['package_id'],access,limits)
                if other is None:raise ServiceError('s2.package_unavailable')
                if desc['expected_digest']['state']=='known' and desc['expected_digest']['value']!=other.snapshot_digest:raise ServiceError('s2.integrity_mismatch')
                if 'format' in desc and desc['format']!=other.format:raise ServiceError('s2.package_format_mismatch')
                visit(desc['package_id'],depth+1)
            for path,r,_ in walk(p):
                if isinstance(r,dict) and r.get('binding') in ('internal','external') and 'target_type' in r:self.record(r,current,access,limits)
            stack.remove(current)
        visit(pid,0);return tuple(PackageView(v.package,v.source_bytes,copy.deepcopy(v.snapshot_digest),v.resolved_packages) for v in result)

    def payload(self,payload_ref,anchor,access,limits):
        from .payloads import read
        return read(payload_ref,anchor,self,access,limits)

