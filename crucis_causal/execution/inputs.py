"""Admitted realization/staging; native procedures remain explicitly supplied.

DLV-08/09. Preparation is pure. Realization can precede final scientific binding;
it returns actual captured products and existing S2 materialization results.
"""
import copy
from dataclasses import dataclass,replace
import io
import json
import zipfile
from . import api,codec
from .authority import DriverBoundary
from .journal import binding_digest,resolve_binding
from .imports import _exact_request
from .model import (Builder,ExecutionError,canonical,contract,digest,index,known,qualified,reference,
    scope,unknown,unknown_ref)
from .registry import DeclaredDriver,PayloadRegistry,callable_value,supplied_callable,_verify_implementation,native_invocation
from .schema import validate_binding,validate_value
from .staging import InputMember,LocalCustodian,EndpointOwner

@dataclass(frozen=True,slots=True)
class Realizer:
    procedure:dict
    operation:dict
    implementation:api.PinnedArtifactIdentity
    method:api.SuppliedCallable
    validate:api.SuppliedCallable|None=None

@dataclass(frozen=True,slots=True)
class SourceValue:
    reference:dict
    kind:str
    bytes:bytes|None
    format:dict

@dataclass(frozen=True,slots=True)
class RealizationInput:
    specification:dict
    sources:tuple[SourceValue,...]
    parameters:tuple[api.BoundInput,...]
    randomness:tuple[api.BoundInput,...]
    fitted_state:SourceValue|None
    source_window:dict

@dataclass(frozen=True,slots=True)
class RealizationProduct:
    snapshots:tuple[api.PinnedView,...]
    outputs:tuple[dict,...]
    mappings:tuple[dict,...]
    checks:tuple[dict,...]
    fitted_inputs:dict
    losses:tuple[dict,...]
    reference_rule:dict

@dataclass(frozen=True,slots=True)
class EndpointInput:
    owner:EndpointOwner
    grant:api.OpaqueGrant
    presentation:dict
    namespace:str
    generation:str

def _bound(ref,anchor,resolver,role):
    record,pid=resolver.record(ref,anchor)
    return api.BoundInput(role,qualified(ref,pid),record,pid,resolver.view(pid).digest)

def _value(ref,anchor,resolver):
    from crucis_causal.connections.validation import content_bytes
    record,pid=resolver.record(ref,anchor);kind=record['record_type']
    if kind=='s1.artifact_snapshot':
        raw=content_bytes(record['payload']['content']);fmt=record['payload']['format']
        return SourceValue(qualified(ref,pid),kind,bytes(raw),copy.deepcopy(fmt))
    # Case/output identities are not flattened into a table or an evaluator view.
    # Explicit providers can use configured owner-managed sources for these.
    return SourceValue(qualified(ref,pid),kind,None,unknown('s3.source_not_a_raw_snapshot'))

def _parameters(binding):return {p['key']:p['value'] for p in binding.record['payload']['parameters']}

def _stage_parameters(value):
    if not isinstance(value,dict) or set(value)!={'members','custody_namespace','custody_epoch','activation'} or value['activation']!='coherent_bundle':
        raise ExecutionError('s3.trusted_stage_parameter_shape')
    validate_value(value['custody_epoch'],'Index')
    validate_value(value['custody_namespace'],'ID')
    if not isinstance(value['members'],list) or not value['members']:raise ExecutionError('s3.staged_members_required')
    for item in value['members']:
        if not isinstance(item,dict) or set(item)!={'presentation','name'}:raise ExecutionError('s3.staged_member_shape')
        validate_value(item['presentation'],'KnownRef(s1.presentation)');validate_value(item['name'],'Code')
    if len({v['name'] for v in value['members']})!=len(value['members']):raise ExecutionError('s3.duplicate_staged_member')
    return value

def _endpoint_parameters(value):
    if not isinstance(value,dict) or set(value)!={'presentation','endpoint_namespace','generation','maximum_queries'}:raise ExecutionError('s3.endpoint_staging_parameter_shape')
    validate_value(value['presentation'],'KnownRef(s1.presentation)');validate_value(value['endpoint_namespace'],'ID')
    validate_value(value['maximum_queries'],'PositiveIndex')
    if not isinstance(value['generation'],str) or not value['generation']:raise ExecutionError('s3.endpoint_generation_required')
    return value

def guarded_input_invocation(value):
    if not isinstance(value,dict) or set(value)!={'kind','recipient','channel','native_contract','native'} or value['kind']!='s3.native_invocation' or value['native_contract']!=contract('s3.invocation.guarded_input'):
        raise ExecutionError('s3.guarded_input_invocation_shape')
    validate_value(value['recipient'],'KnownRef');validate_value(value['channel'],'Contract')
    native=value['native']
    if not isinstance(native,dict) or set(native)!={'operation','binding_digest','prepared_only'} or native['prepared_only'] is not True:
        raise ExecutionError('s3.guarded_input_invocation_body')
    validate_value(native['operation'],'Contract');validate_value(native['binding_digest'],'Digest')
    if native['operation'] not in (contract('s3.op.stage_input'),contract('s3.op.realize_input')) or value['channel']!=contract('s3.trusted_local_call'):
        raise ExecutionError('s3.guarded_input_invocation_contract')
    return value

def _select(presentation,anchor,resolver,limit):
    from crucis_causal.connections.validation import content_bytes
    payload=presentation['payload']['payload']
    if payload['state']!='known':raise ExecutionError('s3.staging_endpoint_requires_installed_custody_driver')
    source=payload['value'];artifact,pid=resolver.record(source['artifact'],anchor)
    raw=content_bytes(artifact['payload']['content'])
    if len(raw)>limit:raise ExecutionError('s3.input_byte_limit')
    selector=source['selector'];fmt=artifact['payload']['format']
    selected_format=fmt['value'] if fmt['state']=='known' else contract('s3.uninterpreted_bytes')
    if selector['state']=='not_applicable':return raw,selected_format
    if selector['state']!='known':raise ExecutionError('s3.input_selector_unestablished')
    value=selector['value'];kind=value['selector_type']
    if kind=='byte_range':
        start,end=int(value['start']),int(value['end_exclusive'])
        if not 0<=start<=end<=len(raw):raise ExecutionError('s3.input_byte_range')
        return raw[start:end],contract('s3.uninterpreted_selected_bytes')
    if kind=='archive_member':
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            candidates=[v for v in archive.infolist() if v.filename==value['name']]
            if len(candidates)!=1 or candidates[0].is_dir() or candidates[0].file_size>limit:raise ExecutionError('s3.archive_selection_unestablished')
            with archive.open(candidates[0]) as stream:selected=stream.read(limit+1)
        if len(selected)>limit:raise ExecutionError('s3.input_byte_limit')
        if value['member_digest']['state']=='known' and value['member_digest']['value']!=digest(selected):raise ExecutionError('s3.archive_member_digest_mismatch')
        return selected,contract('s3.uninterpreted_selected_bytes')
    raise ExecutionError('s3.input_selector_encoding_unimplemented')

class InputDriver(DeclaredDriver):
    def __init__(self,component,implementation,boundary,*,realizers=(),scientific_context=None,custodian=None,custody_control=None,endpoints=()):
        if not isinstance(boundary,DriverBoundary):raise ExecutionError('s3.actual_driver_boundary_required')
        _verify_implementation(implementation)
        self.component=copy.deepcopy(component);self.implementation=implementation;self.boundary=boundary
        self.scientific_context=scientific_context;self.custodian=custodian;self.custody_control=custody_control
        self.payloads=PayloadRegistry();self.payloads.register(contract('s3.payload.trusted_stage'),_stage_parameters)
        self.payloads.register(contract('s3.payload.trusted_endpoint_stage'),_endpoint_parameters)
        self.endpoints=tuple(endpoints)
        if any(not isinstance(owner,EndpointOwner) for owner,grant in self.endpoints):raise ExecutionError('s3.actual_endpoint_owner_required')
        self.realizers={}
        for realizer in realizers:
            if not isinstance(realizer,Realizer):raise ExecutionError('s3.explicit_realizer_required')
            validate_value(realizer.procedure,'Contract');validate_value(realizer.operation,'Contract')
            _verify_implementation(realizer.implementation)
            import inspect
            if list(inspect.signature(callable_value(realizer.method)).parameters)!=['inputs']:raise ExecutionError('s3.realizer_signature')
            if realizer.validate is not None and list(inspect.signature(callable_value(realizer.validate)).parameters)!=['inputs']:raise ExecutionError('s3.realizer_validator_signature')
            key=canonical(realizer.procedure)
            if key in self.realizers:raise ExecutionError('s3.duplicate_realizer')
            self.realizers[key]=realizer
        methods=tuple(api.ExactDriverDescriptor(self.component,contract(op),contract('s3.invocation.guarded_input'),contract('s3.driver_evidence'),implementation,(),supplied_callable(method))
            for op,method in [('s3.op.realize_input',self.realize),('s3.op.stage_input',self.stage)])
        self.descriptors={d.operation['name']:d for d in methods}
        super().__init__(api.DriverDeclaration(self.component,methods,()),self._prepare)

    def install(self,registry):
        """Explicit supplied-plugin installation, with its exact pure grammar."""
        registry.payloads.register(contract('s3.invocation.guarded_input'),guarded_input_invocation)
        registry.drivers.install(self,registry)

    def _realization(self,binding,resolver):
        params=_parameters(binding);specs=[e for e in binding.inputs.entries if e.role=='s3.role.specification']
        spec=specs[0];p=spec.record['payload'];selected=self.realizers.get(canonical(params['procedure']['value']))
        if selected is None or selected.operation!=p['operation']:raise ExecutionError('s3.realization_procedure_unavailable')
        provider=next(e for e in binding.inputs.entries if e.role=='s3.role.provider')
        if qualified(provider.reference,provider.source_package)!=self.component:raise ExecutionError('s3.realization_provider_mismatch')
        _verify_implementation(selected.implementation)
        random=tuple(_bound(r,binding.context['package_id'],resolver,'s3.role.randomness') for r in params['randomness']['value'])
        if p['randomness'] and not random:raise ExecutionError('s3.realization_randomness_unestablished')
        if p['predecessors']:raise ExecutionError('s3.realization_predecessor_evidence_requires_installed_procedure')
        parameters=tuple(_bound(r,spec.source_package,resolver,'s3.role.parameters') for r in p['parameters'])
        source_entries=tuple(e for e in binding.inputs.entries if e.role=='s3.role.sources')
        permitted=[]
        for req in p['inputs']:
            requirement,rpid=resolver.record(req,spec.source_package)
            permitted.extend(resolver.record(ref,rpid)[0] for ref in requirement['payload']['subjects'])
        if not permitted or any(not any(canonical(e.record)==canonical(r) for r in permitted) for e in source_entries):
            raise ExecutionError('s3.realization_input_scope_unestablished')
        sources=tuple(_value(e.reference,e.source_package,resolver) for e in source_entries)
        fitted=params['fitted_state'];fitted_value=None if fitted['state']=='not_applicable' else _value(fitted['value'],binding.context['package_id'],resolver)
        window=params['source_window']
        if window['state']!='not_applicable':raise ExecutionError('s3.realization_source_window_requires_installed_procedure')
        supplied=RealizationInput(copy.deepcopy(spec.record),sources,parameters,random,fitted_value,copy.deepcopy(window))
        if selected.validate is None:
            if fitted_value is not None or random:raise ExecutionError('s3.realization_state_or_randomness_interpretation_unestablished')
        elif callable_value(selected.validate)(supplied) is not True:raise ExecutionError('s3.realization_procedure_requirements_unestablished')
        return selected,supplied

    def _staging(self,binding,resolver):
        params=_parameters(binding)
        if params['transfer_contract']['value']==contract('s3.transfer.trusted_endpoint'):return self._endpoint_staging(binding,resolver)
        if params['transfer_contract']['value']!=contract('s3.transfer.trusted_snapshot') or params['stability']['value']!='snapshot' or params['cleanup_rule']['value']!=contract('s3.cleanup.revoke_trusted_interface'):
            raise ExecutionError('s3.staging_guarantee_unavailable')
        typed=params['native_parameters']['value'];record,_=resolver.record(typed,binding.context['package_id'])
        if record['payload']['payload_contract']!=contract('s3.payload.trusted_stage'):raise ExecutionError('s3.staging_parameter_contract')
        native=resolver.payload(typed,binding.context['package_id'],self.payloads)
        presentations=[e for e in binding.inputs.entries if e.role=='s3.role.presentations'];recipient=next(e for e in binding.inputs.entries if e.role=='s3.role.recipient')
        if len(native['members'])!=len(presentations):raise ExecutionError('s3.staged_presentation_cardinality')
        typed_context=record['payload']['reference_context']['package_id'];members=[];seen=set()
        for item in native['members']:
            current,pid=resolver.record(item['presentation'],typed_context)
            candidates=[e for e in presentations if e.record['id']==current['id'] and e.source_package==pid]
            if len(candidates)!=1 or (pid,current['id']) in seen:raise ExecutionError('s3.staged_presentation_substitution')
            seen.add((pid,current['id']));p=current['payload']
            if p['state']!='permitted':raise ExecutionError('s3.staged_presentation_not_permitted')
            destination,_=resolver.record(p['recipient'],pid)
            if destination['id']!=recipient.record['id']:raise ExecutionError('s3.staged_recipient_mismatch')
            raw,fmt=_select(current,pid,resolver,int(resolver.limits.max_external_bytes))
            members.append(InputMember(item['name'],qualified(item['presentation'],pid),raw,digest(raw),fmt))
        return native,qualified(recipient.reference,recipient.source_package),tuple(members)

    def _endpoint_staging(self,binding,resolver):
        params=_parameters(binding)
        if params['stability']['value']!='immutable_reference' or params['cleanup_rule']['value']!=contract('s3.cleanup.revoke_endpoint_proxy'):
            raise ExecutionError('s3.endpoint_snapshot_guarantee_unavailable')
        record,pid=resolver.record(params['native_parameters']['value'],binding.context['package_id'])
        if record['payload']['payload_contract']!=contract('s3.payload.trusted_endpoint_stage'):raise ExecutionError('s3.endpoint_parameter_contract')
        native=resolver.payload(params['native_parameters']['value'],binding.context['package_id'],self.payloads)
        presentations=[e for e in binding.inputs.entries if e.role=='s3.role.presentations']
        if len(presentations)!=1:raise ExecutionError('s3.coherent_multi_endpoint_delegation_unimplemented')
        presentation,ppid=resolver.record(native['presentation'],record['payload']['reference_context']['package_id'])
        selected=presentations[0]
        if selected.record!=presentation or selected.source_package!=ppid or presentation['payload']['state']!='permitted':raise ExecutionError('s3.endpoint_presentation_substitution')
        p=presentation['payload'];recipient=next(e for e in binding.inputs.entries if e.role=='s3.role.recipient')
        actual_recipient,rpid=resolver.record(p['recipient'],ppid)
        if canonical(actual_recipient)!=canonical(recipient.record) or p['endpoint']['state']!='known' or p['payload']['state']=='known':raise ExecutionError('s3.endpoint_presentation_unestablished')
        endpoint,epid=resolver.record(p['endpoint']['value'],ppid);endpoint_ref=reference(endpoint['id'],'s1.endpoint',epid)
        matches=[(owner,grant) for owner,grant in self.endpoints if owner.endpoint==endpoint_ref and owner.namespace==native['endpoint_namespace']]
        if len(matches)!=1:raise ExecutionError('s3.actual_endpoint_binding_unavailable')
        owner,grant=matches[0];description=owner.current(grant)
        declared_owner,opid=resolver.record(endpoint['payload']['owner'],epid)
        configured_owner,_=resolver.record(owner.component,binding.context['package_id'])
        recipient_ref=qualified(recipient.reference,recipient.source_package)
        if canonical(declared_owner)!=canonical(configured_owner) or endpoint['payload']['operation']!=owner.operation or description['recipient']!=recipient_ref or description['generation']!=native['generation'] or description['maximum_queries']!=native['maximum_queries']:
            raise ExecutionError('s3.endpoint_owner_or_scope_mismatch')
        return native,recipient_ref,(EndpointInput(owner,grant,qualified(native['presentation'],ppid),native['endpoint_namespace'],native['generation']),)

    def _prepare(self,binding,inputs,context):
        validate_binding(binding.record['payload'],admission=True)
        resolver=codec.Resolver(context.views,limits=context.limits)
        actual=resolve_binding(reference(binding.record['id'],'operation_binding',binding.context['package_id']),binding.context['package_id'],resolver)
        if binding_digest(actual)!=binding_digest(binding) or canonical([e.record for e in actual.inputs.entries])!=canonical([e.record for e in inputs.entries]):
            raise ExecutionError('s3.input_preparation_binding_mismatch')
        if any(not context.access.permits(v.package_id) for v in context.views):raise ExecutionError('s3.read_denied')
        binding=actual
        op=binding.record['payload']['operation']['name']
        receiver=self.component
        if op=='s3.op.realize_input':self._realization(binding,resolver)
        elif op=='s3.op.stage_input':
            _,_,members=self._staging(binding,resolver)
            if isinstance(members[0],EndpointInput):receiver=members[0].owner.component
        else:raise ExecutionError('s3.input_driver_operation_unavailable')
        value=native_invocation(receiver,contract('s3.trusted_local_call'),contract('s3.invocation.guarded_input'),
            {'operation':binding.record['payload']['operation'],'binding_digest':binding_digest(binding),'prepared_only':True})
        return guarded_input_invocation(value)

    def _evidence(self,request,context,dependencies,*,code,subjects=(),receipts=(),checks=(),exposure=()):
        b=Builder('Guarded input boundary recorder',implementation=known({'artifact':self.implementation.reference,'selector':self.implementation.selector}))
        diagnostic=b.add('diagnostic',{'code':code,'scope':scope(request.command),'details':'Scoped input-interface observation; no native-use or isolation inference','evidence':list(subjects)})
        members=[diagnostic]
        for observation in exposure:
            if isinstance(observation,dict):values=observation
            else:
                recipient,facet,extent,information=observation
                values={'owner':self.component,'recipient':recipient,'information':index(information),'facet':facet,'extent':extent,'policy':contract('s3.custody.per_accepted_stage')}
            members.append(b.add('exposure_entry',{'scope':scope(request.command),**values,'basis':[diagnostic],'revises':[]}))
        audience=b.add('audience',{'purpose':contract('s3.private_input_evidence'),'recipients':index(),'disclosure_policy':unknown_ref('s1.policy'),'authority':unknown()})
        root=b.add('projection_view',{'view_role':'audience_projection','audience':audience,'projection_contract':contract('s3.input_evidence'),
            'members':index(members),'claims':index(),'limits':index()})
        # Resolver rejects any same-ID/different-content view; no latest-wins merge.
        resolved=codec.Resolver((*context.read.views,*dependencies,self.implementation.source_view),limits=context.read.limits)
        views=tuple(resolved._views.values())
        frame=codec.parse_snapshot(codec.dumps(b.package(root,views),context.read.limits),context.read.limits)
        codec.Resolver((*views,frame),limits=context.read.limits).closure(frame.package_id)
        delta=api.RecordDelta(records=frame.records,dependencies=(*views,frame))
        return api.DriverEvidence(reference(request.binding.record['id'],'operation_binding',request.binding.context['package_id']),delta,index(subjects),index(receipts),index(checks),())

    def stage(self,request,context,grants,issue_token,sink):
        effect=api.EffectBoundary(request.command,'not_crossed',unknown('s3.not_forwarded'),(),issue_token.transmission);failure_exposure=None
        try:
            actual,resolver=_exact_request(request,context.read,'s3.op.stage_input')
            native,recipient,members=self._staging(actual,resolver)
            if isinstance(members[0],EndpointInput):
                source=members[0]
                failure_exposure=[{'owner':source.owner.component,'recipient':recipient,'information':index([source.presentation]),
                    'facet':'reachable','extent':unknown('s3.endpoint_delegation_unconfirmed'),'policy':contract('s3.endpoint.bounded_capability')}]
                entry=self.boundary.enter(request,context,grants,issue_token,self.descriptors['s3.op.stage_input'],source.owner.component,contract('s3.trusted_local_call'));effect=entry.effect
                proxy=source.owner.delegate(request.command['target'],source.grant,recipient,namespace=source.namespace,generation=source.generation)
                evidence=self._evidence(request,context,(),code='s3.trusted_endpoint_reference_delegated',subjects=(source.presentation,),
                    exposure=[{'owner':source.owner.component,'recipient':recipient,'information':index([source.presentation]),
                        'facet':'reachable','extent':known({'number_type':'integer','text':'1'}),'policy':contract('s3.endpoint.bounded_capability')}])
                evidence=replace(evidence,live_handles=(proxy,))
                return api.CallResult('completed',evidence,records=evidence.records,effects=(replace(effect,boundary='crossed',acceptance=known(True)),))
            custodian=self.custodian;control=self.custody_control
            if not isinstance(custodian,LocalCustodian) or native['custody_namespace']!=custodian.namespace:raise ExecutionError('s3.actual_custodian_namespace_required')
            entry=self.boundary.enter(request,context,grants,issue_token,self.descriptors['s3.op.stage_input'],self.component,contract('s3.trusted_local_call'));effect=entry.effect
            custodian.transfer(request.command['target'],binding_digest(entry.binding),recipient,members,control,
                expected_epoch=native['custody_epoch'],fault=context.fault)
            effect=replace(effect,boundary='crossed',acceptance=known(True))
            active=custodian.activate(request.command['target'],recipient,control,expected_epoch=native['custody_epoch'],fault=context.fault)
            refs=[m.source for m in members]
            evidence=self._evidence(request,context,(),code='s3.trusted_snapshot_activated',subjects=refs,
                exposure=[(self.component,'transmitted',known({'number_type':'integer','text':str(len(members))}),refs),
                    (recipient,'reachable',known({'number_type':'integer','text':str(len(members))}),refs),
                    (self.component,'policy_consumed',known({'number_type':'integer','text':'1'}),refs)])
            evidence=replace(evidence,live_handles=(active.handle,))
            return api.CallResult('completed',evidence,records=evidence.records,effects=(replace(effect,boundary='crossed',acceptance=known(True)),))
        except ExecutionError as exc:return self._stage_failure(request,context,effect,exc.code,failure_exposure)
        except Exception:return self._stage_failure(request,context,effect,'s3.staging_outcome_unconfirmed',failure_exposure)

    def _stage_failure(self,request,context,effect,code,observations=None):
        retained=api.RecordDelta(dependencies=context.read.views)
        if effect.boundary!='not_crossed':
            try:
                refs=[qualified(e.reference,e.source_package) for e in request.inputs.entries if e.role=='s3.role.presentations']
                recipient=next(qualified(e.reference,e.source_package) for e in request.inputs.entries if e.role=='s3.role.recipient')
                evidence=self._evidence(request,context,(),code=code,subjects=refs,exposure=observations if observations is not None else [
                    (self.component,'transmitted',unknown('s3.transfer_extent_unconfirmed'),refs),
                    (recipient,'reachable',unknown('s3.activation_extent_unconfirmed'),refs),
                    (self.component,'policy_consumed',unknown('s3.policy_consumption_unconfirmed'),refs)])
                retained=evidence.records
            except Exception:pass # original effects/source remain; no invented successful capture
        return api.rejected(code,records=retained,effects=(effect,))

    def realize(self,request,context,grants,issue_token,sink):
        effect=api.EffectBoundary(request.command,'not_crossed',unknown('s3.not_forwarded'),(),issue_token.transmission);retained=api.RecordDelta(dependencies=context.read.views)
        try:
            actual,resolver=_exact_request(request,context.read,'s3.op.realize_input')
            selected,inputs=self._realization(actual,resolver)
            from crucis_causal.experiments.api import PlanAssessmentContext
            if not isinstance(self.scientific_context,PlanAssessmentContext):raise ExecutionError('s3.actual_scientific_materialization_context_required')
            entry=self.boundary.enter(request,context,grants,issue_token,self.descriptors['s3.op.realize_input'],self.component,contract('s3.trusted_local_call'));effect=entry.effect
            product=callable_value(selected.method)(inputs)
            if not isinstance(product,RealizationProduct) or not product.outputs:raise ExecutionError('s3.realization_product_unestablished')
            effect=replace(effect,boundary='crossed',acceptance=known(True))
            resolved=codec.Resolver((*context.read.views,*product.snapshots),limits=context.read.limits)
            for view in product.snapshots:
                if view.format['name'] not in ('s1.connection_package','s2.experiment_package'):raise ExecutionError('s3.realization_native_namespace')
                resolved.closure(view.package_id)
            retained=api.RecordDelta(dependencies=tuple(resolved._views.values()))
            specification=next(e for e in entry.binding.inputs.entries if e.role=='s3.role.specification')
            if product.reference_rule!=specification.record['payload']['reference_rule']:raise ExecutionError('s3.realization_reference_rule_mismatch')
            validate_value(product.fitted_inputs,'K(Ref[])')
            fitting=product.fitted_inputs['value'] if product.fitted_inputs['state']=='known' else ()
            for ref in (*product.outputs,*product.mappings,*product.checks,*fitting):
                if ref.get('binding')!='external':raise ExecutionError('s3.realization_qualified_output_required')
                resolved.record(ref,ref['package_id'])
            receipt,scientific_views,issues=self._materialize(entry.binding,product,resolved)
            evidence=self._evidence(request,context,(*product.snapshots,*scientific_views),code='s3.realization_captured',subjects=product.outputs,receipts=(receipt,),checks=product.checks)
            state='partial' if issues else 'completed'
            return api.CallResult(state,evidence,records=evidence.records,issues=issues,effects=(replace(effect,boundary='crossed',acceptance=known(True)),))
        except ExecutionError as exc:return api.rejected(exc.code,records=retained,effects=(effect,))
        except Exception:return api.rejected('s3.materialization_evidence_unconfirmed' if effect.acceptance.get('state')=='known' else 's3.realization_outcome_unconfirmed',records=retained,effects=(effect,))

    def _materialize(self,binding,product,resolver):
        from crucis_causal.experiments import core as s2
        from crucis_causal.experiments.api import PlanAssessmentContext
        from crucis_causal.experiments.operations import parameter
        from crucis_causal.experiments.resolver import parse_snapshot,ReadAccess
        context=self.scientific_context
        if not isinstance(context,PlanAssessmentContext):raise ExecutionError('s3.actual_scientific_materialization_context_required')
        draft=context.draft;writer=draft.records
        for view in resolver._views.values():
            if view.format['name'] in ('s1.connection_package','s2.experiment_package'):
                writer.base=writer.base.with_view(parse_snapshot(view.source_bytes,draft.read.limits))
                writer.access=ReadAccess(frozenset(set(writer.access.packages)|{view.package_id}))
        spec=next(e for e in binding.inputs.entries if e.role=='s3.role.specification')
        sources=[qualified(e.reference,e.source_package) for e in binding.inputs.entries if e.role=='s3.role.sources']
        with writer.begin(draft.author,draft.clock) as tx:
            realized=parameter(tx,draft,'transform',{'operation':known(spec.record['payload']['operation']),'inputs':known(sources),
                'outputs':known(list(product.outputs)),'maps':known(list(product.mappings)),'preservation':known(list(product.checks)),'losses':known(list(product.losses)),
                'fitted_inputs':copy.deepcopy(product.fitted_inputs),'reference_rule':known(product.reference_rule),'order':known([])})
            tx.commit()
        random=tuple(_parameters(binding)['randomness']['value'])
        result=s2.record_materialization(qualified(spec.reference,spec.source_package),(*product.checks,*random),realized,context)
        if result.state=='rejected':raise ExecutionError(result.diagnostics[0].code)
        frozen=writer.frozen([result.value]);supplied=writer.base.with_view(frozen)
        access=ReadAccess(frozenset(set(writer.access.packages)|{frozen.package_id}))
        views=tuple(codec.parse_snapshot(v.source_bytes,resolver.limits) for v in supplied.closure(frozen.package_id,access,draft.read.limits))
        issues=tuple(api.Issue(i.code,scope(qualified(spec.reference,spec.source_package)),tuple(i.evidence)) for i in result.diagnostics)
        return qualified(result.value,frozen.package_id),views,issues
