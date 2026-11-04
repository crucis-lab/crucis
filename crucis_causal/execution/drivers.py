"""Explicit supplied native mechanics over the common guarded boundary.

DLV-08/09. This module loads no callable, executable, credential or endpoint from
metadata. Real execution and transport objects are installed by their owners.
"""
import copy
from dataclasses import dataclass, field
import inspect
from . import api, codec
from .identity import NativeConnections, coordinate, validate_descriptor
from .imports import _exact_request
from .journal import binding_digest, resolve_binding
from .model import (Builder, ExecutionError, canonical, contract, index, known,
    not_applicable, qualified, reference, scope, unknown, unknown_ref)
from .registry import (DeclaredDriver, callable_value, native_invocation,
    supplied_callable, _verify_implementation)
from .schema import validate_binding, validate_value
from .coordinator import read_with, root_of

NATIVE_OPS = {'s3.op.launch': 'invoke', 's3.op.lookup_launch': 'lookup', 's3.op.attach': 'attach'}


@dataclass(frozen=True, slots=True)
class NativeCall:
    request: api.ExactOperationRequest
    context: api.RuntimeContext
    parameters: dict
    transmission: dict
    invocation: dict


@dataclass(frozen=True, slots=True)
class NativeReply:
    raw: bytes | None
    format: dict
    acceptance: dict
    descriptor: dict | None = None
    runtime: object | None = None
    epoch: str | None = None
    classification: str | None = None
    matches: tuple = ()
    coverage: api.QueryCoverage | None = None
    facts: api.RecordDelta = field(default_factory=api.RecordDelta)
    origin_attempt: dict | None = None


@dataclass(frozen=True, slots=True)
class NativeMechanics:
    receiver: dict
    channel: dict
    prepare: api.SuppliedCallable
    methods: tuple


def guarded_native_invocation(value):
    if not isinstance(value, dict) or set(value) != {'kind','recipient','channel','native_contract','native'} or value['kind'] != 's3.native_invocation' or value['native_contract'] != contract('s3.invocation.guarded_native'):
        raise ExecutionError('s3.guarded_native_invocation_shape')
    validate_value(value['recipient'], 'KnownRef'); validate_value(value['channel'], 'Contract')
    body = value['native']
    if not isinstance(body, dict) or set(body) != {'operation','binding_digest','arguments'} or body['operation']['name'] not in NATIVE_OPS:
        raise ExecutionError('s3.guarded_native_invocation_body')
    validate_value(body['operation'], 'Contract'); validate_value(body['binding_digest'], 'Digest')
    if not isinstance(body['arguments'], dict): raise ExecutionError('s3.explicit_native_arguments_required')
    # JSON data only, bounded by the enclosing snapshot/request checks. This
    # native extension cannot contain a callable/handle or install code.
    canonical(body['arguments'])
    return copy.deepcopy(value)


def lookup_evidence(value):
    keys = {'classification','query_binding','matches','scope','paths','interval','retention','complete','no_late_acceptance'}
    if not isinstance(value, dict) or set(value) != keys or value['classification'] not in ('positive','negative','unknown','disputed'):
        raise ExecutionError('s3.closed_lookup_evidence_required')
    for name, expression in [('query_binding','Digest'),('scope','Scope'),('paths','Contract[]'),('interval','K(TimeInterval)'),
                             ('retention','Contract'),('complete','K(Boolean)'),('no_late_acceptance','K(Boolean)')]:
        validate_value(value[name], expression)
    if not isinstance(value['matches'], list): raise ExecutionError('s3.lookup_match_list_required')
    for descriptor in value['matches']: validate_descriptor(descriptor)
    return copy.deepcopy(value)


def _capture(raw, selected, dependencies, *, basis='observed', origins=()):
    from crucis_causal.connections.model import Builder as B1
    from crucis_causal.connections.evidence import capture_bytes
    from crucis_causal.connections.codec import dumps
    b = B1('Native transport/body capture')
    ref = capture_bytes(b, raw, format_contract=selected, basis=basis, origin=list(origins))
    # S3 does not enter a prior subsystem's reader. Only explicit S1 snapshots
    # can be prior-format capture dependencies.
    resolver = codec.Resolver(dependencies, limits=api.Limits())
    prior = {}
    for origin in origins:
        if origin.get('binding') != 'external': raise ExecutionError('s3.qualified_native_capture_origin_required')
        for view in resolver.closure(origin['package_id']):
            if view.format['name'] != 's1.connection_package': raise ExecutionError('s3.prior_capture_namespace_required')
            prior[view.package_id] = view
    package = b.package([ref], external_packages=[{'package_id': v.package_id, 'locator': unknown(),
        'expected_digest': known(v.digest), 'access': 's1.supplied_metadata'} for v in prior.values()])
    view = codec.parse_snapshot(dumps(package), api.Limits())
    return qualified(ref, view.package_id), view


def _document(builder, selected, value, dependencies, *, origins=()):
    artifact, storage = _capture(canonical(value), {'name': 's1.json', 'version': '0.1.0-proposal.1'}, dependencies,
        basis='derived', origins=origins)
    ref = builder.add('typed_payload', {'payload_contract': selected,
        'content': {'artifact': artifact, 'selector': not_applicable()},
        'reference_context': {'package_id': builder.package_id, 'format': contract('account_package')}},
        basis='derived', evidence=origins, procedure=contract('s3.explicit_native_reply_projection'))
    return ref, storage


class NativeDriver(DeclaredDriver):
    def __init__(self, component, implementation, boundary, mechanics):
        if not isinstance(mechanics, NativeMechanics): raise ExecutionError('s3.explicit_native_mechanics_required')
        _verify_implementation(implementation)
        validate_value(component, 'KnownRef(component)'); validate_value(mechanics.receiver, 'KnownRef')
        validate_value(mechanics.channel, 'Contract')
        if list(inspect.signature(callable_value(mechanics.prepare)).parameters) != ['binding','inputs','context']:
            raise ExecutionError('s3.native_pure_preparer_signature')
        methods = {}
        for selected, method in mechanics.methods:
            if selected != contract(selected['name']) or selected['name'] not in NATIVE_OPS or selected['name'] in methods:
                raise ExecutionError('s3.exact_native_method_binding_required')
            if list(inspect.signature(callable_value(method)).parameters) != ['call']:
                raise ExecutionError('s3.native_runtime_method_signature')
            methods[selected['name']] = method
        if not methods: raise ExecutionError('s3.native_method_set_required')
        self.component = copy.deepcopy(component); self.implementation = implementation
        self.boundary = boundary
        self.mechanics = NativeMechanics(copy.deepcopy(mechanics.receiver), copy.deepcopy(mechanics.channel), mechanics.prepare, tuple(mechanics.methods))
        self.methods = methods
        self.connections = NativeConnections()
        descriptors = tuple(api.ExactDriverDescriptor(self.component, contract(op), contract('s3.invocation.guarded_native'),
            contract('s3.native_port_result'), implementation, (), supplied_callable(getattr(self, NATIVE_OPS[op]))) for op in methods)
        self.descriptors = {d.operation['name']: d for d in descriptors}
        super().__init__(api.DriverDeclaration(self.component, descriptors, ()), self._prepare)

    def install(self, registry):
        registry.payloads.register(contract('s3.invocation.guarded_native'), guarded_native_invocation)
        registry.payloads.register(contract('s3.native.lookup_evidence'), lookup_evidence)
        registry.drivers.install(self, registry)

    def _prepare(self, binding, inputs, context):
        validate_binding(binding.record['payload'], admission=True)
        op = binding.record['payload']['operation']['name']
        if op not in self.methods: raise ExecutionError('s3.native_method_unavailable')
        resolver = codec.Resolver(context.views, limits=context.limits)
        actual = resolve_binding(reference(binding.record['id'], 'operation_binding', binding.context['package_id']), binding.context['package_id'], resolver)
        def entries(value):
            return [{'role': e.role, 'reference': e.reference, 'record': e.record,
                'source_package': e.source_package, 'source_digest': e.source_digest} for e in value.entries]
        if binding_digest(actual) != binding_digest(binding) or canonical(entries(actual.inputs)) != canonical(entries(inputs)):
            raise ExecutionError('s3.native_preparation_binding_mismatch')
        for source in inputs.source_views:
            checked = resolver.view(source.package_id)
            if checked.digest != source.digest or checked.source_bytes != source.source_bytes:
                raise ExecutionError('s3.native_preparation_source_mismatch')
        arguments = callable_value(self.mechanics.prepare)(actual, inputs, context)
        return guarded_native_invocation(native_invocation(self.mechanics.receiver, self.mechanics.channel,
            contract('s3.invocation.guarded_native'), {'operation': actual.record['payload']['operation'],
                'binding_digest': binding_digest(actual), 'arguments': arguments}))

    def _frame(self, request, context, reply, *, attempt, code):
        read = read_with(context.read, *reply.facts.dependencies, self.implementation.source_view)
        if reply.facts.native_additions or reply.facts.scientific_additions:
            raise ExecutionError('s3.native_additions_require_owned_freeze')
        b = Builder('Native dispatch evidence', implementation=known({'artifact': self.implementation.reference, 'selector': self.implementation.selector}))
        origins = []
        if reply.raw is not None:
            if not isinstance(reply.raw, bytes): raise ExecutionError('s3.exact_native_response_bytes_required')
            raw, snapshot = _capture(reply.raw, reply.format, read.views)
            read = read_with(read, snapshot); origins.append(raw)
        diagnostic = b.add('diagnostic', {'code': code, 'scope': scope(request.command),
            'details': 'Scoped native response observation; native assertions are not universal truth or permission.', 'evidence': origins})
        subjects, associations = [], []
        descriptors = ((reply.descriptor,) if reply.descriptor is not None else ()) + reply.matches
        for value in descriptors:
            descriptor = validate_descriptor(value)
            if request.binding.record['payload']['operation'] == contract('s3.op.attach'):
                supplied = next(e for e in request.inputs.entries if e.role == 's3.role.subject')
                original = codec.Resolver(read.views, limits=read.limits)
                prior = original.payload(supplied.record['payload']['descriptor'], supplied.source_package, read.registry.payloads)
                if coordinate(prior) != coordinate(descriptor): raise ExecutionError('s3.native_attachment_subject_mismatch')
                subjects.append(qualified(supplied.reference, supplied.source_package))
                continue
            document, storage = _document(b, contract('s3.payload.native_descriptor'), descriptor, read.views, origins=origins)
            read = read_with(read, storage)
            origin = reply.origin_attempt or unknown_ref('s1.attempt', 's3.native_origin_not_established_by_reply')
            validate_value(origin, 'Ref(s1.attempt)')
            subject = b.add('native_subject', {'descriptor': document, 'origin_attempt': origin, 'scope': scope(request.command), 'basis': origins}, basis='reported', evidence=origins)
            subjects.append(subject)
            if attempt.get('binding') != 'unresolved':
                associations.append(b.add('native_association', {'attempt': attempt, 'native_subject': subject,
                    'relation': 'reported', 'basis': origins, 'assessment': unknown('s3.association_not_independently_assessed')}, basis='reported', evidence=origins))
        if reply.coverage is not None:
            coverage = reply.coverage
            data = {'classification': reply.classification, 'query_binding': binding_digest(request.binding),
                'matches': list(reply.matches), 'scope': coverage.scope, 'paths': list(coverage.paths),
                'interval': coverage.interval, 'retention': coverage.retention, 'complete': coverage.complete,
                'no_late_acceptance': coverage.no_late_acceptance}
            document, storage = _document(b, contract('s3.native.lookup_evidence'), data, read.views, origins=origins)
            read = read_with(read, storage); origins.append(document)
        audience = b.add('audience', {'purpose': contract('s3.private_native_evidence'), 'recipients': index(),
            'disclosure_policy': unknown_ref('s1.policy'), 'authority': unknown()})
        root = b.add('projection_view', {'view_role': 'audience_projection', 'audience': audience,
            'projection_contract': contract('s3.native_dispatch'), 'members': index([diagnostic, *subjects, *associations, *origins]), 'claims': index(), 'limits': index()})
        view = codec.parse_snapshot(codec.dumps(b.package(root, read.views), read.limits), read.limits)
        codec.Resolver((*read.views, view), limits=read.limits).closure(view.package_id)
        delta = api.RecordDelta((*reply.facts.records, *view.records), (), (*read.views, view))
        evidence = api.DriverEvidence(request.binding and reference(request.binding.record['id'], 'operation_binding', request.binding.context['package_id']),
            delta, index([qualified(r, view.package_id) for r in subjects], extent='complete_for_scope' if reply.descriptor is not None or reply.classification == 'positive' else 'unresolved'),
            index([qualified(diagnostic, view.package_id)]), index(), ())
        return evidence, tuple(qualified(r, view.package_id) for r in subjects)

    def _run(self, op, request, context, grants, issue_token, sink):
        effect = api.EffectBoundary(request.command, 'not_crossed', unknown('s3.not_forwarded'), (), issue_token.transmission)
        attempt = unknown_ref('s1.attempt', 's3.native_origin_unestablished')
        observed = None; retained = api.RecordDelta()
        try:
            actual, resolver = _exact_request(request, context.read, op)
            prepared = self.prepare(actual, request.inputs, context.read)
            if prepared.state != 'completed': return api.rejected(prepared.issues[0].code, effects=(effect,))
            invocation = prepared.value.invocation['native']['arguments']
            parameters = {p['key']: copy.deepcopy(p['value']) for p in actual.record['payload']['parameters']}
            if op == 's3.op.launch': attempt = next(qualified(e.reference, e.source_package) for e in actual.inputs.entries if e.role == 's3.role.attempt')
            if op == 's3.op.attach':
                association = next(e for e in actual.inputs.entries if e.role == 's3.role.association')
                attempt = qualified(association.record['payload']['attempt'], association.source_package)
            entered = self.boundary.enter(request, context, grants, issue_token, self.descriptors[op], self.mechanics.receiver, self.mechanics.channel)
            effect = entered.effect
            reply = callable_value(self.methods[op])(NativeCall(request, context, parameters, issue_token.transmission, invocation))
            if not isinstance(reply, NativeReply): raise ExecutionError('s3.typed_native_reply_required')
            observed = reply
            validate_value(reply.acceptance, 'K(Boolean)')
            if reply.descriptor is not None: validate_descriptor(reply.descriptor)
            evidence, subjects = self._frame(request, context, reply, attempt=attempt, code='s3.native_response_received')
            retained = evidence.records
            handles = ()
            if reply.runtime is not None:
                if reply.descriptor is None or reply.epoch is None: raise ExecutionError('s3.native_runtime_identity_unestablished')
                role = 's3.connection.' + (parameters['connection_role']['value'] if op == 's3.op.attach' else 'controller')
                handles = (self.connections.bind(reply.descriptor, reply.runtime, role, reply.epoch, request.command),)
                from dataclasses import replace
                evidence = replace(evidence, live_handles=handles)
            boundary = 'crossed' if reply.acceptance.get('state') == 'known' and reply.acceptance['value'] else 'not_crossed' if reply.acceptance.get('state') == 'known' else 'may_have_crossed'
            effect = api.EffectBoundary(request.command, boundary, reply.acceptance, tuple(evidence.receipts['members']), issue_token.transmission)
            if reply.acceptance.get('state') == 'known' and not reply.acceptance['value']:
                return api.rejected('s3.native_operation_not_accepted', records=evidence.records, effects=(effect,))
            if op == 's3.op.launch':
                value = api.NativeStart(attempt, known(subjects[0]) if subjects else unknown('s3.native_identity_unestablished'), handles[0] if handles else None, evidence)
            elif op == 's3.op.lookup_launch':
                if reply.classification not in ('positive','negative','unknown','disputed') or not isinstance(reply.coverage, api.QueryCoverage):
                    raise ExecutionError('s3.native_lookup_coverage_unestablished')
                for match in reply.matches: validate_descriptor(match)
                value = api.LookupResult(reply.classification, tuple(copy.deepcopy(reply.matches)), binding_digest(actual), reply.coverage, evidence.records)
            else:
                if not handles or len(subjects) != 1: raise ExecutionError('s3.native_attachment_handle_unestablished')
                # The connection names the requested native subject, not a new
                # subject identity invented by reconnecting to it.
                subject = next(qualified(e.reference, e.source_package) for e in actual.inputs.entries if e.role == 's3.role.subject')
                value = api.NativeConnection(subject, attempt, role, reply.epoch, handles[0], evidence)
            if reply.acceptance['state'] != 'known':
                return api.CallResult('partial', value, records=evidence.records, effects=(effect,),
                    issues=(api.Issue('s3.native_acceptance_unestablished', scope(request.command), ()),))
            return api.CallResult('completed', value, records=evidence.records, effects=(effect,))
        except Exception as exc:
            code = exc.code if isinstance(exc, ExecutionError) else 's3.native_call_unconfirmed'
            # Exception text may contain transport/auth details. Preserve scoped
            # uncertainty without copying arbitrary native exception strings.
            if observed is not None and not retained.records:
                try:
                    safe = NativeReply(observed.raw, {'name': 's1.octets', 'version': '0.1.0-proposal.1'}, unknown('s3.native_metadata_uninterpreted'))
                    evidence, _ = self._frame(request, context, safe, attempt=attempt, code=code)
                    retained = evidence.records
                except Exception:
                    pass  # Return the actual boundary even if storage also fails.
            return api.rejected(code, records=retained, effects=(effect,))

    def invoke(self, request, context, grants, issue_token, sink):
        return self._run('s3.op.launch', request, context, grants, issue_token, sink)

    def lookup(self, request, context, grants, issue_token, sink):
        return self._run('s3.op.lookup_launch', request, context, grants, issue_token, sink)

    def attach(self, request, context, grants, issue_token, sink):
        return self._run('s3.op.attach', request, context, grants, issue_token, sink)
