"""Optional ports and reusable route boundaries, system agnostic (DLV-08/09)."""
from dataclasses import replace
import copy

from .api import (AdapterPorts, BoundConnection, EvidenceDelta, InvocationSpec, NativeHandle, Op,
    SupportClaim, SupportDeclaration)
from .codec import WireError
from .evidence import capture_bytes
from .model import contract, known, scope, source, unresolved
from .services import execution_binding, delivery_binding, cancellation_binding


def _reject(records, subjects, reason): return Op('rejected',diagnostics=(records.gap(subjects,reason),))


def bind_request(component, services, request, presented, route, inventory, context, *, allowed_routes):
    records=context.services.records
    try:
        req=records.get(request)
        if req['record_type']!='s1.request': raise WireError('request reference required')
        descriptor=services.registry.route(route.operation,route.route_kind)
        if (descriptor is None or req['payload']['operation']!=route.operation or route.route_kind not in allowed_routes
            or req['payload']['route'] not in descriptor['request_routes'] or context.services is not services):
            return _reject(records,[request],'s1.unsupported_route')
        if presented.permitted_policy != req['payload']['presentation_policy']:
            return _reject(records,[request],'s1.information_policy_mismatch')
        readiness='ready';gaps=[];inventory_by_id={x.component.get('target'):x for x in inventory.entries}
        for dependency in descriptor['dependencies']:
            if dependency.get('binding')!='internal':
                if readiness!='not_ready':readiness='unresolved'
                continue
            entry=inventory_by_id.get(dependency.get('target'))
            if entry and entry.available.get('value') is False: readiness='not_ready'
            elif not entry or entry.available['state']!='known' or entry.version['state']!='known':
                if readiness!='not_ready':readiness='unresolved'
        for ref in presented.presentations:
            p=records.get(ref)['payload']
            if p['recipient']!=component or p['state'] not in ('permitted','delivered','access_observed','use_claimed'):
                return _reject(records,[request,ref],'s1.information_not_permitted')
            if descriptor['presentations'] and p['information_contract'] not in descriptor['presentations']:
                return _reject(records,[request,ref],'s1.unsupported_presentation')
        if readiness!='ready':gaps.append(records.gap([request],'s1.dependency_not_established'))
        binding=records.add('binding',{'request':request,'adapter':component,'route':'s1.'+route.route_kind,
            'presented':list(presented.presentations),'resolved_configuration':[],'prerequisites':[],
            'state':readiness,'gaps':gaps})
        value=BoundConnection(binding,request,component,route,tuple(presented.presentations),readiness,tuple(gaps))
        return Op('completed' if readiness=='ready' else 'partial',value,tuple(gaps))
    except (KeyError,ValueError,TypeError) as exc:
        return _reject(records,[request],'s1.invalid_binding')


def make_connection(component, services):
    """Minimal describable connection; optional ports are added by route factories."""
    return AdapterPorts(describe=lambda:SupportDeclaration(component,(),('describe',)))


def recorded_connection(component, services):
    """Read exact supplied snapshots; no fake invoke/prepare/cancel port."""
    def read(source, context, sink):
        spec=source
        before={r['id'] for r in sink.records.snapshot()};artifacts=[];gaps=[]
        if not spec.sources:return _reject(services.records,[component],'s1.no_source_selected')
        for ref in spec.sources:
            try:
                record=context.resolver.record(ref)
                if record['record_type']!='s1.artifact_snapshot': raise WireError('captured source bytes required')
                if spec.expected_contracts and record['payload']['format'].get('value') not in spec.expected_contracts:
                    raise WireError('source format not established')
                artifacts.append(sink.capture(context.resolver.bytes(ref),origin=[ref],basis='observed'))
            except (OSError,KeyError,ValueError,WireError): gaps.append(sink.records.gap([ref],'s1.source_not_retrieved'))
        delta=EvidenceDelta(tuple(r for r in sink.records.snapshot() if r['id'] not in before),tuple(artifacts),spec.sources,tuple(gaps),unresolved())
        return Op('partial' if gaps else 'completed',delta,tuple(gaps))
    ports=AdapterPorts(describe=lambda:SupportDeclaration(component,(),('describe','bind','read')),
        bind=lambda request,presented,route,inventory,context:bind_request(component,services,request,presented,route,inventory,context,allowed_routes=('recorded',)),read=read)
    return ports


def prepared_connection(component, services, invocation, outputs_expected=(), *, _routes=('prepared_command',)):
    """Pure command/function/service descriptor; preparing cannot execute it."""
    def prepare(bound, context, sink):
        if bound.readiness!='ready':return _reject(services.records,[bound.binding],'s1.route_not_ready')
        try:
            kind=invocation['kind']
            fields={'function':{'kind','entrypoint','arguments'},'process':{'kind','executable','argv','cwd','environment_policy'},
                    'service':{'kind','endpoint','request'}}[kind]
            if set(invocation)!=fields:raise WireError('closed invocation fields required')
            if kind=='process' and (not isinstance(invocation['argv'],list) or any(not isinstance(x,str) for x in invocation['argv'])):
                raise WireError('process invocation requires argument vector')
        except (KeyError,TypeError,WireError):return _reject(services.records,[bound.binding],'s1.invalid_invocation')
        spec=InvocationSpec(bound.binding,bound.route,copy.deepcopy(invocation),bound.permitted_presentations,
            tuple(outputs_expected),unresolved(),(context.write_scope,))
        return Op('completed',spec)
    return AdapterPorts(describe=lambda:SupportDeclaration(component,(),('describe','bind','prepare')),
        bind=lambda request,presented,route,inventory,context:bind_request(component,services,request,presented,route,inventory,context,allowed_routes=_routes),prepare=prepare)


def supplied_connection(component, services, invocation, *, authority, executor,
                        effects=('s1.cpu',), observer=None, delivery=None, canceller=None, delivery_effects=('s1.deliver',)):
    """Caller-supplied execution/observation drivers, never entrypoint eval or shell strings.

    The owner supplies each driver and runtime capability. A CPU fixture can use
    this route; provider adapters must retain their own spend/cap guards as well.
    No installation or dependency probe occurs during describe/bind/prepare.
    """
    if not callable(executor):raise WireError('an explicit execution driver is required')
    base=prepared_connection(component,services,invocation,_routes=('direct','prepared_command','recorded_response_replay'))
    def invoke(spec, context, sink):
        try:
            grant=context.grant;binding=services.records.get(spec.binding)['payload'];attempt=services.records.get(context.attempt)['payload']
            if (grant.attempt!=context.attempt or grant.request!=attempt['request'] or binding['request']!=grant.request
                or spec.route.operation not in grant.operations or tuple(spec.inputs)!=grant.presentations
                or tuple(grant.effects)!=tuple(effects) or not set_ref_subset(spec.authority_required,grant.policies)
                or binding['state']!='ready' or spec.invocation!=invocation or binding['adapter']!=component
                or binding['route']!='s1.'+spec.route.route_kind or binding['presented']!=list(spec.inputs)):
                raise WireError('grant/spec scope mismatch')
            auth=services.records.get(grant.authority)['payload']
            if (auth['decision']!='permitted' or auth['operation']!=spec.route.operation or context.attempt not in auth['subjects']
                or auth['policy'] not in grant.policies
                or any(effect not in auth['permitted_effects'] for effect in grant.effects)):raise WireError('authority evidence mismatch')
            authority.check(grant.runtime_capability,'execute',execution_binding(grant),consume=True)
        except (KeyError,TypeError,ValueError,WireError):return _reject(services.records,[context.attempt],'s1.execution_not_authorized')
        try:
            # Executor owns the explicit function/process/service binding. No implicit imports.
            result=executor(copy.deepcopy(spec.invocation),context,sink)
            if not isinstance(result,NativeHandle) or result.attempt!=context.attempt:raise WireError('driver must return the granted attempt handle')
            context.handle_registry.attach(result)
            return Op('completed',result)
        except Exception as exc:
            # Capture recoverable evidence even when the call/ack failed. Attribution stays scoped.
            detail=sink.capture(str(exc).encode('utf-8',errors='backslashreplace'),basis='observed')
            return Op('rejected',diagnostics=(services.records.gap([context.attempt],'s1.invocation_or_ack_failed',[detail]),))
    def observe(handle,cursor,limit,context,sink):
        if observer is None:raise WireError('observe is unsupported')
        result=observer(handle,cursor,limit,context,sink)
        # Bounded batches are checked independently of any native completion claim.
        if result.state!='rejected':
            from .codec import dumps
            batch=result.value
            if len(batch.records)>int(limit.max_events) or len(dumps(list(batch.records)))>int(limit.max_bytes):
                return _reject(services.records,[handle.attempt],'s1.observation_batch_exceeded')
        return result
    def deliver(response,channel,context,sink):
        grant=context.grant
        try:
            response_payload=services.records.get(response)['payload'];action=services.records.get(grant.action)['payload']
            endpoint=services.records.get(grant.endpoint)['payload'];auth=services.records.get(grant.authority)['payload']
            if (grant.response!=response or response_payload['request']!=grant.action or action['endpoint']!=grant.endpoint
                or channel.endpoint!=grant.endpoint or tuple(grant.effects)!=tuple(delivery_effects)
                or auth['decision']!='permitted' or auth['operation']!=endpoint['operation']
                or auth['policy'] not in grant.policies or grant.action not in auth['subjects']
                or any(e not in auth['permitted_effects'] for e in grant.effects)):
                raise WireError('delivery response/action/endpoint authority mismatch')
            for ref in response_payload['delivery']:
                p=services.records.get(ref)['payload']
                if (p['endpoint'].get('value')!=grant.endpoint or p['recipient']!=endpoint['owner']
                    or p['attempt']!=action['attempt'] or p['state'] not in ('permitted','delivered')):
                    raise WireError('delivery presentation outside selected native audience')
            authority.check(grant.runtime_capability,'deliver',delivery_binding(grant),consume=True)
        except (KeyError,TypeError,ValueError,WireError):return _reject(services.records,[response],'s1.delivery_not_authorized')
        return delivery(response,channel,context,sink)
    def cancel(handle,context,sink):
        grant=context.grant
        try:
            auth=services.records.get(grant.authority)['payload']
            if (grant.attempt!=handle.attempt or auth['decision']!='permitted' or auth['operation']!=contract('cancel')
                or auth['policy'] not in grant.policies or grant.attempt not in auth['subjects']):raise WireError('cancellation target/authority mismatch')
            authority.check(grant.runtime_capability,'cancel',cancellation_binding(grant),consume=True)
        except (KeyError,TypeError,ValueError,WireError):return _reject(services.records,[handle.attempt],'s1.cancellation_not_authorized')
        return canceller(handle,context,sink)
    names=('describe','bind','prepare','invoke')+ (('observe',) if observer else ())+ (('deliver',) if delivery else ())+ (('cancel',) if canceller else ())
    return AdapterPorts(describe=lambda:SupportDeclaration(component,(),names),bind=base.bind,prepare=base.prepare,invoke=invoke,
        observe=observe if observer else None,deliver=deliver if delivery else None,cancel=cancel if canceller else None)


def set_ref_subset(left,right):return all(x in right for x in left)


def attached_connection(component,services,observer):
    """Observe a caller-established handle; never launch or fabricate an attempt."""
    from .codec import dumps
    def observe(handle,cursor,limit,context,sink):
        result=observer(handle,cursor,limit,context,sink)
        if result.state!='rejected' and (len(result.value.records)>int(limit.max_events)
            or len(dumps(list(result.value.records)))>int(limit.max_bytes)):
            return _reject(services.records,[handle.attempt],'s1.observation_batch_exceeded')
        return result
    return AdapterPorts(describe=lambda:SupportDeclaration(component,(),('describe','bind','observe')),
        bind=lambda request,presented,route,inventory,context:bind_request(component,services,request,presented,route,inventory,context,allowed_routes=('attached_job',)),
        observe=observe)


def with_decoder(base, component, services, *, reader, targets, decoder):
    """Bind one explicit pure decoder; parse failure leaves captured source intact."""
    from .api import InterpretationDelta
    def decode(source, request, context):
        view=source
        try:
            if view.reader!=reader or request.target_contract not in targets or request.requested_guarantee not in ('preserve','interpret'):
                return _reject(services.records,[view.snapshot],'s1.unsupported_decoder')
            if tuple(request.selectors)!=tuple(view.selectors):raise WireError('decoder selector binding differs')
            for ref in request.mappings:context.mappings.resolve(ref)
            raw=context.resolver.bytes(view.snapshot)
            if view.selectors:raw=[context.resolver.select({'artifact':view.snapshot,'selector':known(s)}) for s in view.selectors]
            value=decoder(raw,request,context)
            if not isinstance(value,InterpretationDelta):raise WireError('decoder result type mismatch')
            return Op('partial' if value.gaps else 'completed',value,tuple(value.gaps))
        except (KeyError,OSError,ValueError,TypeError,WireError):
            gap=services.records.gap([view.snapshot],'s1.decode_not_established',[view.snapshot])
            return Op('partial',InterpretationDelta((services.records.get(gap),),(),(),(),(gap,)),(gap,))
    declaration=base.describe()
    names=tuple(n for n in base.supported() if n!='decode')+('decode',)
    return replace(base,describe=lambda:SupportDeclaration(component,declaration.claims,names),decode=decode)
