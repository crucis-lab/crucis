"""Explicit source-scoped compatibility, reusing S1's safe codec (DLV-08/09/10)."""
import base64
import copy
from dataclasses import dataclass
from . import api
from .codec import record_bytes,validate_package
from .errors import ServiceError
from .model import contract,reference,qualified,known,unknown,source,digest,walk
from .operations import atomic,get,parameter,diagnostic,bound
from .families import values

@dataclass(frozen=True,slots=True)
class CompatibilityView:
    """Caller-provided runtime S1 selection; never loaded as code from a package."""
    view:api.PackageView
    selection:object

def target(kind):return contract('s2.legacy.'+kind)

def _snapshot(ref,context):
    d=context.draft;read=d.read
    if ref.get('binding')!='external':raise ServiceError('s2.qualified_legacy_source_required')
    found=read.resolver.record(ref,read.active_package,read.access,read.limits)
    if found.record['record_type']!='s1.artifact_snapshot':raise ServiceError('s2.legacy_source_bytes_unavailable')
    view=read.resolver.lookup(found.package_id,read.access,read.limits)
    if view.format['name']!='s1.connection_package':raise ServiceError('s2.legacy_requires_s1_snapshot')
    # S1 Resolver has no filesystem root or path grant here. Inline captured
    # content works; descriptors/locations alone cannot trigger file discovery.
    from crucis.connections.evidence import Resolver
    from crucis.connections.legacy import echo,encode
    from crucis.connections.codec import dumps as s1bytes,loads as s1loads
    local=reference(ref['target'],'s1.artifact_snapshot')
    fmt=found.record['payload']['format']
    if fmt['state']!='known':raise ServiceError('s2.legacy_source_contract_unestablished')
    raw=Resolver(view.package).bytes(local)
    value=echo(view.package,local)
    if s1bytes(encode(value))!=s1bytes(s1loads(raw)):
        raise ServiceError('s2.legacy_value_roundtrip_loss')
    return value,fmt['value'],raw

def _closure(records,roots):
    mapping={r['id']:r for r in records};selected={};pending=[r['target'] for r in roots]
    while pending:
        rid=pending.pop()
        if rid in selected:continue
        r=mapping.get(rid)
        if r is None:raise ServiceError('s2.legacy_staged_closure_missing')
        selected[rid]=r
        pending.extend(x['target'] for _,x,_ in walk(r) if isinstance(x,dict) and x.get('binding')=='internal')
    return list(selected.values())

def _import_builtin(source_spec,scope_spec,context):
    d=context.draft
    if not source_spec.captured_sources:raise ServiceError('s2.legacy_source_required')
    bindings=get(scope_spec.bindings,d,'s2.parameter_set');name,v=values(scope_spec.bindings,d)
    if name!='legacy':raise ServiceError('s2.legacy_binding_required')
    declarations=False
    for ref in source_spec.captured_sources:
        if ref.get('binding')!='external':raise ServiceError('s2.qualified_legacy_source_required')
        declared=get(ref,d,('s1.artifact_snapshot','s1.artifact_declaration'))
        if declared['record_type']=='s1.artifact_declaration':
            declarations=True;continue
        value,fmt,raw=_snapshot(ref,context)
        if fmt!=source_spec.legacy_contract:raise ServiceError('s2.legacy_source_contract_mismatch')
        if scope_spec.kind=='run_record':
            from crucis.core.runs import RunRecord
            if not isinstance(value,RunRecord):raise ServiceError('s2.legacy_runrecord_required')
            for key,actual in [('item',value.item),('arm',value.arm),('status',value.status)]:
                if v[key]['state']=='known' and v[key]['value']!=actual:raise ServiceError('s2.legacy_binding_source_mismatch',key)
        elif scope_spec.kind in ('battery_manifest','audit_spec'):
            if not isinstance(value,dict):raise ServiceError('s2.legacy_manifest_mapping_required')
        else:raise ServiceError('s2.legacy_kind_unsupported')
    if scope_spec.interpretation_claims:raise ServiceError('s2.legacy_explicit_interpretation_procedure_required')
    fingerprint=digest(record_bytes({'source':{'captured_sources':source_spec.captured_sources,'contract':source_spec.legacy_contract,
        'identity':source_spec.source_identity},'scope':{'kind':scope_spec.kind,'bindings':scope_spec.bindings},
        'snapshots':[d.read.resolver.lookup(r['package_id'],d.read.access,d.read.limits).snapshot_digest for r in source_spec.captured_sources]}))
    issues=(api.PlanIssue('s2.legacy_original_history_unestablished'),api.PlanIssue('s2.legacy_source_scope_only'))
    if declarations:issues+=(api.PlanIssue('s2.legacy_source_bytes_unavailable'),)
    def build(tx):
        def create():
            gaps=[diagnostic(tx,d,source_spec.captured_sources,i.code) for i in issues]
            receipt=tx.add('import_receipt',{'import_occurrence':source_spec.occurrence_id,'sources':list(source_spec.captured_sources),
                'reader':d.author,'configuration':known(scope_spec.bindings),'original_identity':source_spec.source_identity,
                'interpretations':[],'gaps':gaps,'source':source(d.author,basis='reconstructed',inputs=source_spec.captured_sources)})
            validate_package(d.records._package(),d.read.limits)
            records=_closure(d.records.snapshot().records,[receipt])
            external={x['package_id'] for r in records for _,x,_ in walk(r) if isinstance(x,dict) and x.get('binding')=='external'}
            pending=list(external);snapshots={}
            while pending:
                pid=pending.pop()
                if pid in snapshots:continue
                view=d.records.base.lookup(pid,d.records.access,d.read.limits)
                if view is None:raise ServiceError('s2.legacy_dependency_unavailable')
                snapshots[pid]=base64.b64encode(view.source_bytes).decode('ascii')
                pending.extend(p['package_id'] for p in view.package['external_packages'])
            return {'receipt':receipt,'records':records,'snapshots':list(snapshots.values())}
        saved=d.identities.import_once(source_spec.occurrence_id,fingerprint,create)
        from .resolver import parse_snapshot,ReadAccess
        for encoded in saved['snapshots']:
            view=parse_snapshot(base64.b64decode(encoded,validate=True),d.read.limits)
            d.records.base=d.records.base.with_view(view)
            d.records.access=ReadAccess(frozenset(set(d.records.access.packages)|{view.package_id}))
        tx.ingest(tuple(saved['records']))
        return api.LegacyImportDelta(saved['receipt'],(saved['receipt'],),source_spec.captured_sources,issues),issues,(saved['receipt'],)
    return atomic(d,build)

def _echo(bindings,policy,context):
    if policy.rule!=contract('s2.legacy_echo'):raise ServiceError('s2.legacy_echo_rule_required')
    # A receipt is a source-scoped occurrence, not a narrow score-key record.
    selected=values(policy.selection,context.draft)
    if selected[0]!='legacy' or selected[1]['projection'].get('value')!=policy.rule:raise ServiceError('s2.legacy_projection_binding_required')
    from crucis.connections.api import LegacyProjection
    from crucis.connections.legacy import encode
    projections=[];keys=set();source_format=None
    for ref in bindings:
        p=get(ref,context.draft,'s2.import_receipt')['payload']
        for captured in p['sources']:
            value,fmt,raw=_snapshot(captured,context)
            if source_format is None:source_format=fmt
            elif fmt!=source_format:raise ServiceError('s2.legacy_mixed_source_contracts')
            key=(value.system,value.item,value.arm) if all(hasattr(value,k) for k in ('system','item','arm')) else None
            if key is not None and key in keys:raise ServiceError('s2.legacy_repeated_key_collision')
            keys.add(key)
            # Echo is exact at the encoded-value scope. It does not promise
            # native original-file bytes or original scientific history.
            encode(value)
            projections.append(LegacyProjection(value,(ref,captured),(),(),policy.rule))
    if not projections:raise ServiceError('s2.legacy_projection_subject_required')
    return api.PlanOp('completed',api.LegacyProjectionDelta(tuple(projections),tuple(bindings),()))

def _compatibility(bindings,policy,context):
    if policy.require_lossless:raise ServiceError('s2.legacy_narrow_view_is_lossy')
    if policy.rule!=contract('s2.legacy_explicit_view'):raise ServiceError('s2.legacy_projection_rule_unsupported')
    read=context.draft.read;found=read.resolver.record(policy.selection,read.active_package,read.access,read.limits)
    rule=get(policy.selection,context.draft,'s2.selection_rule')['payload']
    if rule['rule']!=policy.rule or not rule['inputs'] or any(bound(r,found.package_id,context.draft) not in bindings for r in rule['inputs']):raise ServiceError('s2.legacy_selection_scope_mismatch')
    views=getattr(context.s1_services,'legacy_views',{})
    selected=views.get(policy.selection['target'])
    if not isinstance(selected,CompatibilityView):raise ServiceError('s2.explicit_s1_legacy_selection_required')
    from .resolver import parse_snapshot
    actual=parse_snapshot(selected.view.source_bytes,context.draft.read.limits)
    if actual.package!=selected.view.package:raise ServiceError('s2.snapshot_view_mismatch')
    if not selected.selection.source_records or any(qualified(r,actual.package_id) not in bindings for r in selected.selection.source_records):raise ServiceError('s2.legacy_selection_source_mismatch')
    from crucis.connections.legacy import project
    value=project(actual.package,selected.selection)
    losses=tuple(api.PlanIssue('s2.'+x) for x in value.lost_guarantees)+(api.PlanIssue('s2.unselected_scientific_bindings_not_projected'),)
    return api.PlanOp('completed',api.LegacyProjectionDelta((value,),tuple(bindings)+(policy.selection,),losses))

def install(registry,implementation):
    from crucis.connections.model import contract as c1
    for kind,src in [('run_record',c1('legacy_runrecord_codec')),('battery_manifest',contract('s2.legacy_manifest_codec')),('audit_spec',contract('s2.legacy_audit_spec_codec'))]:
        registry.register(api.LegacyProcedure(src,target(kind),implementation,_import_builtin,_echo))
    registry.register(api.LegacyProcedure(contract('s2.legacy_explicit_view'),contract('s2.legacy_explicit_view'),implementation,
        lambda *args:api.reject(ServiceError('s2.direction_unsupported')),_compatibility))

def _guard(context,call,expected):
    """An injected procedure cannot leave committed staging behind on rejection."""
    w=context.draft.records
    if w._active:return api.reject(ServiceError('s2.transaction_scope_mismatch'))
    before=copy.deepcopy(w._records),copy.deepcopy(w._external),w.base,w.access
    def restore():
        if w._active:w._transaction.discard()
        w._records,w._external,w.base,w.access=before
    try:
        result=call()
        if w._active:raise ServiceError('s2.legacy_unclosed_transaction')
        if not isinstance(result,api.PlanOp) or (result.state!='rejected' and not isinstance(result.value,expected)):raise ServiceError('s2.legacy_result_contract')
        if result.state=='rejected':restore()
        elif expected is api.LegacyImportDelta:
            get(result.value.receipt,context.draft,'s2.import_receipt')
            for ref in result.value.roots:get(ref,context.draft)
        return result
    except Exception as exc:restore();return api.reject(exc)

def import_legacy(source,scope,context):
    try:
        procedure=context.legacy.lookup(source.legacy_contract,target(scope.kind))
        if procedure is None:raise ServiceError('s2.legacy_reader_unavailable')
        # Built-ins are atomic; injected procedures must use the same staged
        # contract. Refuse malformed results rather than inventing conversions.
        return _guard(context,lambda:procedure.import_value(source,scope,context),api.LegacyImportDelta)
    except Exception as exc:return api.reject(exc)

def project_legacy(bindings,policy,context):
    try:
        if policy.rule==contract('s2.legacy_explicit_view'):source_contract=policy.rule;kind=policy.rule
        else:
            if not bindings:raise ServiceError('s2.legacy_projection_subject_required')
            receipt=get(bindings[0],context.draft,'s2.import_receipt')['payload']
            value,source_contract,_=_snapshot(receipt['sources'][0],context)
            from crucis.core.runs import RunRecord
            kind=target('run_record' if isinstance(value,RunRecord) else 'audit_spec' if source_contract==contract('s2.legacy_audit_spec_codec') else 'battery_manifest')
        procedure=context.legacy.lookup(source_contract,kind)
        if procedure is None:raise ServiceError('s2.legacy_projection_unavailable')
        return _guard(context,lambda:procedure.project_value(bindings,policy,context),api.LegacyProjectionDelta)
    except Exception as exc:return api.reject(exc)
