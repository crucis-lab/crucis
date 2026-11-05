"""Exact caller-supplied bindings; names never load code (DLV-08/09)."""
import copy
import inspect
import weakref
from dataclasses import dataclass
from decimal import Decimal
from jsonschema import Draft202012Validator
from . import api
from .model import ExecutionError, VERSION, digest,contract
from .schema import _catalog, _schema, fields, operation

_CALLABLES = weakref.WeakSet()

def supplied_callable(function):
    """Bind an already supplied callable, without calling or importing it."""
    if not callable(function): raise ExecutionError('s3.supplied_callable_required')
    handle = api.SuppliedCallable(api._OPAQUE_KEY, _CALLABLES)
    handle._function = function
    _CALLABLES.add(handle)
    return handle

def callable_value(handle):
    if not isinstance(handle, api.SuppliedCallable) or handle not in _CALLABLES:
        raise ExecutionError('s3.callable_binding_unavailable')
    return handle._function

def native_invocation(receiver,channel,selected,native):
    """Pure routing envelope for explicitly installed native invocation grammars.

    Native arguments remain under their own exact contract. Neither a contract
    string nor this envelope loads a callable, creates a handle or grants rights.
    """
    from .schema import validate_value
    validate_value(receiver,'KnownRef');validate_value(channel,'Contract');validate_value(selected,'Contract')
    if not isinstance(native,dict):raise ExecutionError('s3.native_invocation_body_required')
    return {'kind':'s3.native_invocation','recipient':copy.deepcopy(receiver),'channel':copy.deepcopy(channel),
        'native_contract':copy.deepcopy(selected),'native':copy.deepcopy(native)}

def invocation_route(value,selected,registry):
    """Validate the installed grammar before using a driver-provided route."""
    from .schema import validate_value
    if not isinstance(value,dict) or set(value)!={'kind','recipient','channel','native_contract','native'} or value['kind']!='s3.native_invocation' or value['native_contract']!=selected:
        raise ExecutionError('s3.native_invocation_envelope')
    validate_value(value['recipient'],'KnownRef');validate_value(value['channel'],'Contract')
    registry.decode(selected,value)
    return copy.deepcopy(value['recipient']),copy.deepcopy(value['channel'])

def key(selected):
    if not isinstance(selected, dict) or set(selected) != {'name','version'}:
        raise ExecutionError('s3.exact_contract_required')
    if not all(isinstance(selected[k], str) and selected[k] for k in selected):
        raise ExecutionError('s3.exact_contract_required')
    return selected['name'], selected['version']

def _signature(function, selected_port):
    row = next(p for p in _catalog()['ports'] if p['port'] == selected_port)
    try: actual = inspect.signature(function)
    except (ValueError, TypeError) as exc: raise ExecutionError('s3.method_signature_unavailable') from exc
    if list(actual.parameters) != list(row['arguments']) or any(p.kind in (p.VAR_POSITIONAL,p.VAR_KEYWORD) for p in actual.parameters.values()):
        raise ExecutionError('s3.method_signature_mismatch', selected_port)

def _copy_descriptor(descriptor):
    pin = descriptor.implementation
    if not isinstance(pin, api.PinnedArtifactIdentity): raise ExecutionError('s3.pinned_implementation_required')
    return api.ExactDriverDescriptor(copy.deepcopy(descriptor.component), copy.deepcopy(descriptor.operation),
        copy.deepcopy(descriptor.input_contract), copy.deepcopy(descriptor.output_contract),
        api.PinnedArtifactIdentity(copy.deepcopy(pin.reference), copy.deepcopy(pin.content_digest), copy.deepcopy(pin.selector),
            api.PinnedView(pin.source_view.package_id, copy.deepcopy(pin.source_view.format), copy.deepcopy(pin.source_view.digest), pin.source_view.source_bytes, pin.source_view.read_scope)),
        tuple(copy.deepcopy(descriptor.guarantees)), descriptor.method)

def _verify_implementation(pin):
    if not isinstance(pin, api.PinnedArtifactIdentity): raise ExecutionError('s3.pinned_implementation_required')
    from .codec import Resolver
    from crucis_causal.connections.validation import content_bytes
    resolver = Resolver((pin.source_view,), limits=api.Limits())
    record, _ = resolver.record(pin.reference, pin.source_view.package_id)
    if record['record_type'] != 's1.artifact_snapshot': raise ExecutionError('s3.implementation_snapshot_required')
    selector = pin.selector
    if selector['state'] != 'not_applicable' and not (selector['state'] == 'known' and selector['value'] == {'selector_type': 'json_pointer', 'pointer': ''}):
        raise ExecutionError('s3.whole_implementation_snapshot_required')
    raw = content_bytes(record['payload']['content'])
    if digest(raw) != pin.content_digest: raise ExecutionError('s3.implementation_digest_mismatch')

class PayloadRegistry:
    """Closed pure decoders over already supplied values; no URI resolution."""
    def __init__(self):
        self._decoders = {}
        for name in _catalog()['parameter_grammars']:
            if name[0].islower():
                self.register({'name': 's3.payload.'+name, 'version': VERSION}, self._grammar(name))

    @staticmethod
    def _grammar(name):
        spec = {'$defs': _schema()['$defs'], **fields(_catalog()['parameter_grammars'][name])}
        validator = Draft202012Validator(spec)
        def decode(value):
            error = next(validator.iter_errors(value), None)
            if error: raise ExecutionError('s3.parameter_grammar', '/'+'/'.join(map(str,error.absolute_path)))
            if name == 'reservation_amounts' or name == 'control_allocation':
                for amount in value.get('entries', value.get('limits', [])):
                    n = amount['quantity']
                    if n['number_type'] == 'nonfinite' or Decimal(n['text']) < 0:
                        raise ExecutionError('s3.finite_nonnegative_amount_required')
            if name == 'collection_bounds':
                if not any(value[k]['state'] == 'known' for k in ['max_events','max_bytes','deadline']):
                    raise ExecutionError('s3.collection_requires_established_bound')
            # Value-level calendar/base64/range semantics are the same on payloads.
            from .codec import _semantics
            _semantics({'records': [], 'payload': value})
            return copy.deepcopy(value)
        return decode

    def register(self, selected, decoder):
        selected_key = key(selected)
        if selected_key in self._decoders: raise ExecutionError('s3.duplicate_contract_binding')
        if not callable(decoder): raise ExecutionError('s3.pure_decoder_required')
        self._decoders[selected_key] = decoder

    def decode(self, selected, value):
        decoder = self._decoders.get(key(selected))
        if decoder is None: raise ExecutionError('s3.unsupported_payload_contract')
        return decoder(copy.deepcopy(value))

    def supports(self, selected):
        return key(selected) in self._decoders

def require_critical_semantics(view, claims, payloads, limits):
    """Withhold only affected claims; keep unknown extension bytes untouched."""
    from .codec import loads
    from crucis_causal.connections.validation import content_bytes
    extensions = list(view.package['extensions'])
    for record in view.records:
        extensions.extend(record['extensions'])
    for extension in extensions:
        if not set(extension['critical_for']).intersection(claims): continue
        if not payloads.supports(extension['contract']): raise ExecutionError('s3.critical_extension_uninterpreted')
        try: raw = content_bytes(extension['payload'])
        except (ValueError, OSError) as exc: raise ExecutionError('s3.critical_extension_bytes_unavailable') from exc
        payloads.decode(extension['contract'], loads(raw, limits))

class ExactDriverRegistry:
    def __init__(self):
        self._entries = {}
        self._preparers = {}

    def install(self, driver, context):
        """Associate an explicitly supplied pure preparer; no method-name lookup."""
        _signature(driver.prepare, 'Driver.prepare')
        declaration = driver.describe(context)
        self.register(declaration)
        for descriptor in declaration.methods:
            self._preparers[key(descriptor.operation)] = (descriptor.method, driver.prepare)

    def prepare(self, binding, inputs, context):
        selected = binding.record['payload']['operation']
        descriptor = self.lookup(selected)
        entry = self._preparers.get(key(selected))
        if entry is None or entry[0] is not descriptor.method:
            return api.rejected('s3.pure_preparer_unavailable')
        result = entry[1](binding, inputs, context)
        if not isinstance(result, api.CallResult):
            raise ExecutionError('s3.typed_preparation_result_required')
        if result.state == 'completed':
            value = result.value
            if not isinstance(value, api.PreparedNativeCall) or value.descriptor.method is not descriptor.method or value.descriptor.component != descriptor.component or value.binding != binding or value.inputs != inputs:
                raise ExecutionError('s3.preparation_binding_mismatch')
        return result

    def register(self, declaration):
        if not isinstance(declaration, api.DriverDeclaration): raise ExecutionError('s3.driver_declaration_required')
        staged = {}
        for descriptor in declaration.methods:
            if not isinstance(descriptor, api.ExactDriverDescriptor) or descriptor.component != declaration.component:
                raise ExecutionError('s3.driver_component_mismatch')
            row = operation(descriptor.operation)
            if row is None: raise ExecutionError('s3.unsupported_operation_contract')
            function = callable_value(descriptor.method)
            _signature(function, row['port'])
            selected = key(descriptor.operation)
            if selected in self._entries or selected in staged: raise ExecutionError('s3.duplicate_driver_binding')
            key(descriptor.input_contract); key(descriptor.output_contract)
            _verify_implementation(descriptor.implementation)
            staged[selected] = _copy_descriptor(descriptor)
        self._entries.update(staged)

    def lookup(self, selected):
        descriptor = self._entries.get(key(selected))
        if descriptor is None: raise ExecutionError('s3.driver_unavailable')
        # Preserve the actual callable identity; copying a descriptor cannot mint it.
        return _copy_descriptor(descriptor)

class ExactDecisionRegistry:
    def __init__(self):
        self._entries = {}

    def register(self, declaration, decision):
        if not isinstance(declaration, api.DecisionDeclaration): raise ExecutionError('s3.decision_declaration_required')
        for name in ['describe','requirements','select']:
            method = getattr(decision, name, None)
            if not callable(method): raise ExecutionError('s3.declared_method_absent', name)
            _signature(method, 'Decision.'+name)
        selected = key(declaration.procedure)
        if selected in self._entries: raise ExecutionError('s3.duplicate_decision_binding')
        _verify_implementation(declaration.implementation)
        # Copy declarations while preserving only the explicitly supplied live callable.
        pin = declaration.implementation
        copied_pin = api.PinnedArtifactIdentity(copy.deepcopy(pin.reference), copy.deepcopy(pin.content_digest), copy.deepcopy(pin.selector),
            api.PinnedView(pin.source_view.package_id, copy.deepcopy(pin.source_view.format), copy.deepcopy(pin.source_view.digest), pin.source_view.source_bytes, pin.source_view.read_scope))
        copied = api.DecisionDeclaration(copy.deepcopy(declaration.component), copy.deepcopy(declaration.procedure),
            copy.deepcopy(declaration.input_contract), copy.deepcopy(declaration.output_contract), copy.deepcopy(declaration.information_requirements),
            copy.deepcopy(declaration.fallback_rule), copied_pin)
        self._entries[selected] = (copied, decision)

    def lookup(self, selected):
        result = self._entries.get(key(selected))
        if result is None: raise ExecutionError('s3.decision_unavailable')
        return result

@dataclass(frozen=True, slots=True)
class SuppliedRegistryContext:
    drivers: ExactDriverRegistry
    decisions: ExactDecisionRegistry
    payloads: PayloadRegistry

class DeclaredDriver:
    """Pure shared describe/prepare shell; actual effect methods are supplied."""
    def __init__(self, declaration, prepare_invocation):
        self._declaration = api.DriverDeclaration(copy.deepcopy(declaration.component), tuple(_copy_descriptor(d) for d in declaration.methods), tuple(copy.deepcopy(declaration.dependencies)))
        self._prepare_invocation = prepare_invocation

    def describe(self, context):
        return api.DriverDeclaration(copy.deepcopy(self._declaration.component), tuple(_copy_descriptor(d) for d in self._declaration.methods), tuple(copy.deepcopy(self._declaration.dependencies)))

    def prepare(self, binding, inputs, context):
        selected = binding.record['payload']['operation']
        descriptor = next((d for d in self._declaration.methods if d.operation == selected), None)
        if descriptor is None: return api.rejected('s3.driver_unavailable')
        # The supplied pure function receives no transport, owner write or I/O port.
        try:
            invocation = self._prepare_invocation(binding, inputs, context)
            return api.CallResult('completed', api.PreparedNativeCall(binding, descriptor, invocation, inputs))
        except ExecutionError as exc:
            return api.rejected(exc.code)
