"""Exact S1/S2 staging and reference bridges (DLV-08/09).

No package lookup, invocation or native authority is manufactured here. Mutable
S1 working buffers are process-local; their bindings must be checked again before
use. The immutable source snapshots remain the reference authority.
"""
import base64
import copy
import json
import threading
import weakref
from . import api,codec
from .model import Builder,ExecutionError,canonical,contract,index,known,qualified,reference,unknown,unknown_ref
Projection=api.S1Projection

class WorkingS1(api.PinnedWorkingS1Context):
    __slots__=()
    def verify(self):
        resolver=codec.Resolver(self.source_views,limits=self.limits)
        for original,local,pin in self.mappings:
            record,pid=resolver.record(original,original['package_id'])
            if resolver.view(pid).digest!=pin or canonical(record)!=canonical(self.buffer.get(local)):
                raise ExecutionError('s3.working_s1_record_changed')
        return self

_locks=weakref.WeakKeyDictionary();_guard=threading.Lock()

def _lock(buffer):
    with _guard:return _locks.setdefault(buffer,threading.RLock())

def _projection_copy(value,limits):
    views=tuple(codec.parse_snapshot(v.source_bytes,limits,access=v.read_scope) for v in value.dependencies)
    by_id={v.package_id:v for v in views}
    return Projection(copy.deepcopy(value.projection),by_id[value.request_view.package_id],copy.deepcopy(value.handoff),
        by_id[value.scientific_view.package_id],copy.deepcopy(value.bridge),views)

def compile_request(run,occurrence,context):
    """Coordinator.compile implementation over the actual supplied S2 compiler.

    Exact repeated calls in this working compiler return the same frozen R.
    Fresh-process recovery uses that pinned R/handoff, never refreezes the old
    publication or fabricates a new native occurrence to recover a lost reply.
    """
    from crucis_causal.experiments import core as s2
    from crucis_causal.experiments.handoff import freeze_s1,_run,_import_ref
    from crucis_causal.experiments.operations import bound
    from crucis_causal.experiments.resolver import ReadAccess
    from crucis_causal.connections.api import RouteSpec
    if not isinstance(context,api.PinnedProjectionContext) or not isinstance(occurrence,api.S1ProjectionOccurrence):
        return api.rejected('s3.exact_projection_context_required')
    b=context.s1_records.builder;draft=context.draft
    context_limits=api.Limits(max_manifest_bytes=draft.read.limits.max_manifest_bytes,
        max_records=draft.read.limits.max_records,max_external_packages=draft.read.limits.max_packages,
        max_external_bytes=draft.read.limits.max_external_bytes,max_reference_depth=draft.read.limits.max_reference_depth,
        max_depth=draft.read.limits.max_parameter_depth)
    with _lock(b):
        before=copy.deepcopy(b._records);external=copy.deepcopy(getattr(b,'_s2_external',{}))
        scientific_before=copy.deepcopy(draft.records._records);declared_before=copy.deepcopy(draft.records._external)
        base_before=draft.records.base;access_before=draft.records.access
        try:
            if run.get('binding')!='external' or run.get('target_type')!='s2.run_binding':
                raise ExecutionError('s3.exact_scientific_run_required')
            found=draft.read.resolver.record(run,run['package_id'],draft.read.access,draft.read.limits)
            source=draft.read.resolver.lookup(found.package_id,draft.read.access,draft.read.limits)
            _,_,subject,sf,spec,*_=_run(run,context)
            # Existing S2 scope validation imports the exact qualified native
            # definition. Never strip package_id and trust target-only lookup.
            native=bound(subject['native_subject']['value'],sf.package_id,draft)
            recipient=_import_ref(native,context)
            route=RouteSpec(spec['route']['value'],spec['transport']['value'],spec['operation']['value'],())
            key=(occurrence.request_id,occurrence.attempt_id)
            binding=canonical({'run':run,'source_digest':source.snapshot_digest,'record':found.record,
                'recipient':recipient,'route':{'kind':route.route_kind,'transport':route.transport,'operation':route.operation,'parameters':list(route.parameters)}})
            cached=getattr(b,'_s3_projections',{}).get(key)
            if cached:
                if cached[0]!=binding:raise ExecutionError('s3.projection_occurrence_conflict')
                # Rechecking S2 detects changed request/presentation content.
                replay=s2.project_request(run,occurrence,recipient,route,context)
                if replay.state!='completed':raise ExecutionError(replay.diagnostics[0].code)
                returned=_projection_copy(cached[1],context_limits)
                return api.CallResult('completed',returned,records=api.RecordDelta(dependencies=returned.dependencies))
            result=s2.project_request(run,occurrence,recipient,route,context)
            if result.state!='completed':raise ExecutionError(result.diagnostics[0].code)
            frozen=freeze_s1(b.package([result.value.request,result.value.attempt],external_packages=list(getattr(b,'_s2_external',{}).values())),draft.read.limits)
            handoff=s2.record_handoff(run,occurrence,frozen,draft)
            if handoff.state!='completed':raise ExecutionError(handoff.diagnostics[0].code)
            evidence=draft.records.frozen([handoff.value])
            supplied=draft.records.base.with_view(frozen).with_view(evidence)
            access=ReadAccess(frozenset(set(draft.records.access.packages)|{frozen.package_id,evidence.package_id}))
            dependencies=tuple(codec.parse_snapshot(v.source_bytes,context_limits) for v in supplied.closure(evidence.package_id,access,draft.read.limits))
            resolver=codec.Resolver(dependencies,limits=context_limits);resolver.closure(evidence.package_id)
            native_view=resolver.view(frozen.package_id);scientific=resolver.view(evidence.package_id)
            bridge_builder=Builder('Exact S2 compiler to S1 request bridge')
            receipt=bridge_builder.add('bridge_receipt',{'rule':contract('s3.bridge.scientific_request'),
                'inputs':index([run,qualified(handoff.value,evidence.package_id)]),
                'outputs':index([qualified(result.value.request,frozen.package_id),qualified(result.value.attempt,frozen.package_id)]),
                'context':{'package_id':frozen.package_id,'format':native_view.format},'losses':index(),'checks':index([qualified(handoff.value,evidence.package_id)])},basis='derived',
                evidence=[run,qualified(handoff.value,evidence.package_id)],procedure=contract('s3.bridge.scientific_request'))
            audience=bridge_builder.add('audience',{'purpose':contract('private_compilation_evidence'),'recipients':index(),
                'disclosure_policy':unknown_ref('s1.policy'),'authority':unknown()})
            root=bridge_builder.add('projection_view',{'view_role':'audience_projection','audience':audience,
                'projection_contract':contract('scientific_request_bridge'),'members':index([receipt]),'claims':index(),'limits':index()})
            bridge_view=codec.parse_snapshot(codec.dumps(bridge_builder.package(root,dependencies),context_limits),context_limits)
            dependencies=(*dependencies,bridge_view)
            codec.Resolver(dependencies,limits=context_limits).closure(bridge_view.package_id)
            projection=Projection(result.value,native_view,qualified(handoff.value,evidence.package_id),scientific,qualified(receipt,bridge_view.package_id),dependencies)
            cache=getattr(b,'_s3_projections',{});cache[key]=(binding,projection);b._s3_projections=cache
            returned=_projection_copy(projection,context_limits)
            return api.CallResult('completed',returned,records=api.RecordDelta(dependencies=returned.dependencies))
        except ExecutionError as exc:
            b._records=before;b._s2_external=external
            draft.records._records=scientific_before;draft.records._external=declared_before
            draft.records.base=base_before;draft.records.access=access_before
            return api.rejected(exc.code)
        except (ValueError,TypeError,KeyError,AttributeError):
            b._records=before;b._s2_external=external
            draft.records._records=scientific_before;draft.records._external=declared_before
            draft.records.base=base_before;draft.records.access=access_before
            return api.rejected('s3.scientific_projection_unestablished')

def working_s1(request,attempt,resolver,buffer):
    """Establish exact qualified-to-working bindings without rewriting records."""
    if request.get('binding')!='external' or attempt.get('binding')!='external':raise ExecutionError('s3.qualified_s1_source_required')
    req,pid=resolver.record(request,request['package_id']);att,apid=resolver.record(attempt,attempt['package_id'])
    if req['record_type']!='s1.request' or att['record_type']!='s1.attempt' or pid!=apid:
        raise ExecutionError('s3.request_attempt_scope_mismatch')
    target,_=resolver.record(att['payload']['request'],apid)
    if target['id']!=req['id']:raise ExecutionError('s3.request_attempt_scope_mismatch')
    views=resolver.closure(pid)
    if any(v.format['name']!='s1.connection_package' for v in views):raise ExecutionError('s3.s1_only_working_scope_required')
    source=resolver.view(pid);records=source.records
    # Preflight every collision before RecordBuffer ingestion.
    for record in records:
        old=buffer.builder._records.get(record['id'])
        if old is not None and canonical(old)!=canonical(record):raise ExecutionError('s3.working_s1_identity_conflict')
    descriptors=copy.deepcopy(getattr(buffer.builder,'_s2_external',{}))
    for v in views:
        if v.package_id==buffer.builder.package_id:raise ExecutionError('s3.working_source_identity_collision')
        descriptor={'package_id':v.package_id,'locator':unknown(),'expected_digest':known(v.digest),'access':'s1.supplied_metadata'}
        if v.package_id in descriptors and descriptors[v.package_id]!=descriptor:raise ExecutionError('s3.working_dependency_conflict')
        descriptors[v.package_id]=descriptor
    buffer.ingest(records)
    buffer.builder._s2_external=descriptors
    maps=tuple((reference(r['id'],r['record_type'],pid),reference(r['id'],r['record_type']),source.digest) for r in records)
    return WorkingS1(buffer,views,maps,reference(req['id'],'s1.request'),reference(att['id'],'s1.attempt'),resolver.limits).verify()

def freeze_owned(delta,*,native_snapshots=(),scientific_snapshots=(),limits=None):
    """Only immutable owned-format snapshots can cross the journal boundary."""
    limits=limits or api.Limits()
    if not isinstance(delta,api.RecordDelta):raise ExecutionError('s3.record_delta_required')
    dependencies={v.package_id:v for v in delta.dependencies}
    for additions,snapshots,fmt in [(delta.native_additions,native_snapshots,'s1.connection_package'),
                                    (delta.scientific_additions,scientific_snapshots,'s2.experiment_package')]:
        if additions and not snapshots:raise ExecutionError('s3.owned_additions_require_frozen_snapshots')
        for view in snapshots:
            actual=codec.parse_snapshot(view.source_bytes,limits)
            if actual.format['name']!=fmt or actual.package_id!=view.package_id or actual.digest!=view.digest:
                raise ExecutionError('s3.owned_snapshot_format_or_pin')
            old=dependencies.get(actual.package_id)
            if old and old.source_bytes!=actual.source_bytes:raise ExecutionError('s3.package_identity_conflict')
            dependencies[actual.package_id]=actual
        # No claimed mutable addition may disappear during freezing.
        pool={r['id']:r for v in snapshots for r in v.records}
        for addition in additions:
            if fmt=='s1.connection_package':
                if not isinstance(addition.context,WorkingS1):raise ExecutionError('s3.verified_working_s1_context_required')
                addition.context.verify()
            else:
                from crucis_causal.experiments.api import DraftContext
                if not isinstance(addition.context,DraftContext):raise ExecutionError('s3.owned_scientific_context_required')
            records=getattr(addition.value,'records',addition.value)
            if not isinstance(records,(tuple,list)):raise ExecutionError('s3.explicit_owned_records_required')
            for record in records:
                if canonical(pool.get(record['id']))!=canonical(record):raise ExecutionError('s3.owned_addition_not_frozen')
    for record in delta.records:
        if not record['record_type'].startswith('s3.'):raise ExecutionError('s3.namespace_partition_required')
    resolver=codec.Resolver(tuple(dependencies.values()),limits=limits)
    for pid in dependencies:resolver.closure(pid)
    return api.CommitDelta(delta.records,delta.roots,tuple(dependencies.values()))

def native_identity(descriptor,*,mode,driver_bridge_aware=False,literal_unique=False):
    """Derived registry key retains the exact raw coordinate tuple separately."""
    from .registry import PayloadRegistry
    PayloadRegistry().decode(contract('s3.payload.native_descriptor'),descriptor)
    raw=copy.deepcopy(descriptor)
    if mode=='literal_unique':
        if literal_unique is not True:raise ExecutionError('s3.native_incarnation_adequacy_unestablished')
        key=raw['native_id'];basis='observed'
    elif mode=='incarnation_key':
        if driver_bridge_aware is not True or raw['incarnation']['state']!='known':raise ExecutionError('s3.native_incarnation_adequacy_unestablished')
        values=[raw['authority'],raw['namespace'],raw['native_id'],raw['incarnation']['value']]
        key='s3-incarnation-key-v1:'+base64.b64encode(json.dumps(values,ensure_ascii=False,separators=(',',':')).encode('utf-8')).decode('ascii');basis='derived'
    else:raise ExecutionError('s3.native_identity_bridge_unsupported')
    from crucis_causal.connections.model import source as source1
    return {'s1_identity':{'authority':raw['authority'],'namespace':raw['namespace'],'native_id':key,
            'source':source1('derived',raw['basis'])},
        'raw_descriptor':raw,'basis':basis,'rule':contract('s3.bridge.'+mode,'0.1.0-proposal.2'),
        'limits':['s3.s1_process_local_handle_registry','s3.registry_key_not_provider_deduplication']}

def s1_return(result,command,transmission,*,entered):
    """S1 rejection after entry is not atomic proof of no native effect."""
    state='not_crossed' if not entered else 'may_have_crossed'
    boundary=api.EffectBoundary(command,state,unknown('s3.native_acceptance_unestablished'),(),transmission)
    if result.state=='rejected':return api.rejected('s3.s1_invocation_rejected_effect_unresolved',effects=(boundary,))
    return api.CallResult('completed',result, effects=(boundary,))
