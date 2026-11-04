"""Explicit supplied mechanics behind the common one-use boundary (DLV-08/09).

This is routing and control, not a default backend. Native preparation, transport
and semantics must be supplied as actual objects under exact operation contracts.
"""
import copy
from dataclasses import dataclass, replace
import inspect
from . import api, codec
from .drivers import NativeCall
from .imports import _exact_request
from .journal import binding_digest, resolve_binding
from .model import ExecutionError, canonical, contract, scope, unknown
from .registry import DeclaredDriver, callable_value, native_invocation, supplied_callable, _verify_implementation
from .schema import operation, validate_value


@dataclass(frozen=True, slots=True)
class EffectMethod:
    operation: dict
    prepare: api.SuppliedCallable
    execute: api.SuppliedCallable
    output_contract: dict
    guarantees: tuple = ()


def invocation(value):
    if not isinstance(value, dict) or set(value) != {'kind','recipient','channel','native_contract','native'} or value['kind'] != 's3.native_invocation' or value['native_contract'] != contract('s3.invocation.supplied_effect'):
        raise ExecutionError('s3.supplied_effect_invocation_shape')
    validate_value(value['recipient'], 'KnownRef'); validate_value(value['channel'], 'Contract')
    body = value['native']
    if not isinstance(body, dict) or set(body) != {'operation','binding_digest','arguments'} or not isinstance(body['arguments'], dict):
        raise ExecutionError('s3.supplied_effect_invocation_body')
    row = operation(body['operation'])
    if row is None or row['pure'] or not row['port'].startswith('Driver.'):
        raise ExecutionError('s3.exact_effect_operation_required')
    validate_value(body['binding_digest'], 'Digest'); canonical(body['arguments'])
    return copy.deepcopy(value)


class EffectDriver(DeclaredDriver):
    def __init__(self, component, implementation, boundary, receiver, channel, methods):
        _verify_implementation(implementation)
        validate_value(component, 'KnownRef(component)'); validate_value(receiver, 'KnownRef'); validate_value(channel, 'Contract')
        self.component, self.receiver, self.channel = copy.deepcopy(component), copy.deepcopy(receiver), copy.deepcopy(channel)
        self.boundary, self.implementation, self.methods = boundary, implementation, {}
        descriptors = []
        for method in methods:
            if not isinstance(method, EffectMethod): raise ExecutionError('s3.supplied_effect_method_required')
            row = operation(method.operation)
            if row is None or row['pure'] or not row['port'].startswith('Driver.') or method.operation['name'] in self.methods:
                raise ExecutionError('s3.exact_effect_operation_required')
            if list(inspect.signature(callable_value(method.prepare)).parameters) != ['binding','inputs','context'] or list(inspect.signature(callable_value(method.execute)).parameters) != ['call']:
                raise ExecutionError('s3.effect_mechanic_signature')
            validate_value(method.output_contract, 'Contract')
            self.methods[method.operation['name']] = method
            descriptors.append(api.ExactDriverDescriptor(component, copy.deepcopy(method.operation), contract('s3.invocation.supplied_effect'),
                copy.deepcopy(method.output_contract), implementation, method.guarantees, supplied_callable(getattr(self, row['port'].split('.')[1]))))
        if not descriptors: raise ExecutionError('s3.effect_method_set_required')
        self.descriptors = {d.operation['name']: d for d in descriptors}
        super().__init__(api.DriverDeclaration(component, tuple(descriptors), ()), self._prepare)

    def install(self, registry):
        if not registry.payloads.supports(contract('s3.invocation.supplied_effect')):
            registry.payloads.register(contract('s3.invocation.supplied_effect'), invocation)
        registry.drivers.install(self, registry)

    def _prepare(self, binding, inputs, context):
        selected = binding.record['payload']['operation']
        method = self.methods.get(selected['name'])
        if method is None or method.operation != selected: raise ExecutionError('s3.effect_method_unavailable')
        resolver = codec.Resolver(context.views, limits=context.limits)
        ref = {'binding': 'external', 'package_id': binding.context['package_id'], 'target_type': 's3.operation_binding', 'target': binding.record['id']}
        actual = resolve_binding(ref, binding.context['package_id'], resolver)
        def entries(value):
            return [{'role': e.role, 'reference': e.reference, 'record': e.record, 'source_package': e.source_package, 'source_digest': e.source_digest} for e in value.entries]
        if binding_digest(actual) != binding_digest(binding) or canonical(entries(actual.inputs)) != canonical(entries(inputs)):
            raise ExecutionError('s3.effect_preparation_binding_mismatch')
        for view in inputs.source_views:
            checked = resolver.view(view.package_id)
            if checked.source_bytes != view.source_bytes or checked.digest != view.digest: raise ExecutionError('s3.effect_preparation_source_mismatch')
        arguments = callable_value(method.prepare)(actual, inputs, context)
        return invocation(native_invocation(self.receiver, self.channel, contract('s3.invocation.supplied_effect'),
            {'operation': selected, 'binding_digest': binding_digest(actual), 'arguments': arguments}))

    def _execute(self, port, request, context, grants, issue_token, sink):
        effect = api.EffectBoundary(request.command, 'not_crossed', unknown('s3.not_forwarded'), (), issue_token.transmission)
        observed = None
        try:
            selected = request.binding.record['payload']['operation']
            row = operation(selected)
            if row is None or row['port'] != 'Driver.' + port: raise ExecutionError('s3.effect_port_mismatch')
            actual, _ = _exact_request(request, context.read, selected['name'])
            method = self.methods.get(selected['name'])
            if method is None or method.operation != selected: raise ExecutionError('s3.effect_method_unavailable')
            prepared = self.prepare(actual, request.inputs, context.read)
            if prepared.state != 'completed': return api.rejected(prepared.issues[0].code, effects=(effect,))
            entered = self.boundary.enter(request, context, grants, issue_token, self.descriptors[selected['name']], self.receiver, self.channel)
            effect = entered.effect
            params = {p['key']: copy.deepcopy(p['value']) for p in actual.record['payload']['parameters']}
            result = callable_value(method.execute)(NativeCall(request, context, params, issue_token.transmission, prepared.value.invocation['native']['arguments']))
            observed = result
            if not isinstance(result, api.CallResult) or result.state not in ('completed','partial','rejected') or not isinstance(result.records, api.RecordDelta):
                raise ExecutionError('s3.effect_result_contract')
            if result.state in ('partial','rejected') and not result.issues or result.state == 'partial' and result.value is None:
                raise ExecutionError('s3.effect_result_law')
            for observed in result.effects:
                if not isinstance(observed, api.EffectBoundary) or observed.command != request.command or observed.transmission != issue_token.transmission:
                    raise ExecutionError('s3.effect_result_scope_mismatch')
                validate_value(observed.acceptance, 'K(Boolean)')
            return replace(result, effects=result.effects or (effect,))
        except Exception as exc:
            code = exc.code if isinstance(exc, ExecutionError) else 's3.supplied_effect_unconfirmed'
            retained = observed.records if isinstance(observed, api.CallResult) and isinstance(observed.records, api.RecordDelta) else api.RecordDelta()
            batch = observed.value if isinstance(observed, api.CallResult) and isinstance(observed.value, api.NativeBatch) else None
            return api.CallResult('rejected', batch, records=retained, issues=(api.Issue(code, scope(request.command), ()),), effects=(effect,))

    def realize(self, request, context, grants, issue_token, sink):
        return self._execute('realize', request, context, grants, issue_token, sink)
    def stage(self, request, context, grants, issue_token, sink):
        return self._execute('stage', request, context, grants, issue_token, sink)
    def invoke(self, request, context, grants, issue_token, sink):
        return self._execute('invoke', request, context, grants, issue_token, sink)
    def lookup(self, request, context, grants, issue_token, sink):
        return self._execute('lookup', request, context, grants, issue_token, sink)
    def attach(self, request, context, grants, issue_token, sink):
        return self._execute('attach', request, context, grants, issue_token, sink)
    def observe(self, request, context, grants, issue_token, sink):
        return self._execute('observe', request, context, grants, issue_token, sink)
    def ack(self, request, context, grants, issue_token, sink):
        return self._execute('ack', request, context, grants, issue_token, sink)
    def acquire(self, request, context, grants, issue_token, sink):
        return self._execute('acquire', request, context, grants, issue_token, sink)
    def compute(self, request, context, grants, issue_token, sink):
        return self._execute('compute', request, context, grants, issue_token, sink)
    def deliver(self, request, context, grants, issue_token, sink):
        return self._execute('deliver', request, context, grants, issue_token, sink)
    def lookup_delivery(self, request, context, grants, issue_token, sink):
        return self._execute('lookup_delivery', request, context, grants, issue_token, sink)
    def stop(self, request, context, grants, issue_token, sink):
        return self._execute('stop', request, context, grants, issue_token, sink)
    def restore(self, request, context, grants, issue_token, sink):
        return self._execute('restore', request, context, grants, issue_token, sink)
    def read(self, request, context, grants, issue_token, sink):
        return self._execute('read', request, context, grants, issue_token, sink)
