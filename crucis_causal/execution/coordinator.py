"""Pinned planning, durable admission and conservative forwarding (DLV-08/09).

Rules, owners, controls and native mechanics are explicitly supplied objects.
No receipt recreates authority. Cooperative single-host control is not a provider
exactly-once guarantee, a distributed transaction, or hostile-code isolation.
"""
import copy
from dataclasses import dataclass, replace
import hashlib
import uuid
import weakref
from . import api, codec
from .clock import require_before
from .journal import binding_digest, resolve_binding
from .model import (Builder, ExecutionError, canonical, contract, digest, identity,
    index, known, not_applicable, qualified, reference, scope, unknown, unknown_ref)
from .owners import persist_owner_requests, owner_request_body
from .registry import callable_value, invocation_route, key, _verify_implementation
from .schema import validate_binding, validate_value, operation


def correlation_id(domain, occurrence):
    """Local content correlation, NOT a provider idempotency key.

    Version-4 lexical UUID with deterministic domain-separated bytes. Journal
    immutable-content collision checks remain mandatory; IDs alone prove nothing.
    """
    return str(uuid.UUID(bytes=hashlib.sha256(canonical([domain, occurrence])).digest()[:16], version=4))


def read_with(read, *views):
    if not isinstance(read, api.PinnedReadContext) or any(not read.access.permits(v.package_id) for v in read.views):
        raise ExecutionError('s3.read_denied')
    selected = {}
    for view in (*read.views, *views):
        previous = selected.get(view.package_id)
        if previous is not None and previous.source_bytes != view.source_bytes:
            raise ExecutionError('s3.package_identity_conflict')
        selected[view.package_id] = view
    resolver = codec.Resolver(selected.values(), limits=read.limits)
    return replace(read, views=tuple(resolver._views.values()), access=api.supplied_read(resolver._views))


def relocate(value, package_id):
    from .model import walk
    value = copy.deepcopy(value)
    for _, item, _ in walk(value):
        if isinstance(item, dict) and item.get('binding') == 'internal' and 'target_type' in item:
            item.update(binding='external', package_id=package_id)
    return value


def root_of(view, resolver):
    record, _ = resolver.record(view.package['roots'][0], view.package_id)
    if record['record_type'] != 's3.account_view':
        raise ExecutionError('s3.full_account_view_required')
    return record['payload']


def frozen(builder, root, read):
    view = codec.parse_snapshot(codec.dumps(builder.package(root, read.views), read.limits), read.limits)
    codec.Resolver((*read.views, view), limits=read.limits).closure(view.package_id)
    return view


def typed_document(builder, selected, value):
    from crucis_causal.connections.model import Builder as S1Builder, contract as c1
    from crucis_causal.connections.evidence import capture_bytes
    from crucis_causal.connections.codec import dumps
    native = S1Builder('Exact coordinator protocol bytes')
    artifact = capture_bytes(native, canonical(value), format_contract=c1('json'))
    storage = codec.parse_snapshot(dumps(native.package([artifact])), api.Limits())
    ref = builder.add('typed_payload', {'payload_contract': selected,
        'content': {'artifact': qualified(artifact, storage.package_id), 'selector': not_applicable()},
        'reference_context': {'package_id': builder.package_id, 'format': contract('account_package')}})
    return ref, storage


@dataclass(frozen=True, slots=True)
class AdmissionRule:
    catalog: dict
    operations: tuple
    implementation: api.PinnedArtifactIdentity
    evaluate: api.SuppliedCallable


@dataclass(frozen=True, slots=True)
class OwnerAllocation:
    role: str
    owner: object
    context: api.RuntimeContext
    amounts: tuple
    replay_contract: dict
    expected_revision: str


@dataclass(frozen=True, slots=True)
class _Services:
    journal: object
    journal_context: api.RuntimeContext
    storage: object
    owners: tuple
    required_owners: tuple
    driver_context: api.RuntimeContext
    clock_context: api.RuntimeContext
    deadline: dict
    sink: object
    fault: object


class Coordinator:
    def __init__(self, rules=(), *, collector=None):
        self.collector = collector
        self._rules = {}
        self._controls = weakref.WeakKeyDictionary()
        self._admissions = {}
        for rule in rules:
            if not isinstance(rule, AdmissionRule): raise ExecutionError('s3.supplied_admission_rule_required')
            _verify_implementation(rule.implementation)
            callable_value(rule.evaluate)
            selected = key(rule.catalog)
            if selected in self._rules: raise ExecutionError('s3.duplicate_admission_rule')
            self._rules[selected] = rule

    def bind(self, journal, journal_context, storage, owners, required_owners,
             driver_context, clock_context, deadline, sink, fault=None):
        """Caller supplies actual independently issued controls; no self-grants."""
        validate_value(deadline, 'K(Time)')
        if not isinstance(owners, tuple) or not isinstance(required_owners, tuple) or not required_owners or len(set(required_owners)) != len(required_owners):
            raise ExecutionError('s3.explicit_required_owner_roles')
        if any(not isinstance(o, OwnerAllocation) for o in owners) or len({o.role for o in owners}) != len(owners):
            raise ExecutionError('s3.unique_supplied_owner_allocations')
        cap = api.OpaqueControlCapability(api._OPAQUE_KEY, self)
        self._controls[cap] = _Services(journal, journal_context, storage, owners, required_owners,
            driver_context, clock_context, copy.deepcopy(deadline), sink, fault)
        return cap

    def _services(self, context):
        cap = getattr(context, 'control_capability', None)
        services = self._controls.get(cap) if isinstance(cap, api.OpaqueControlCapability) else None
        if services is None or services.journal is not context.journal or services.storage is not context.storage:
            raise ExecutionError('s3.actual_coordinator_control_required')
        if set(context.owners) != {o.role for o in services.owners} or any(context.owners[o.role] is not o.owner for o in services.owners):
            raise ExecutionError('s3.coordinator_owner_binding_mismatch')
        if context.drivers is not context.read.registry.drivers or context.decisions is not context.read.registry.decisions:
            raise ExecutionError('s3.coordinator_registry_binding_mismatch')
        return services

    @staticmethod
    def _fault(services, label):
        if services.fault: services.fault(label)

    def open(self, commission, context):
        try:
            services = self._services(context)
            read_with(context.read)
            if not isinstance(commission, api.CommissionSpec): raise ExecutionError('s3.commission_required')
            validate_value(commission.account_id, 'ID')
            resolver = codec.Resolver(context.read.views, limits=context.limits)
            account = reference(commission.account_id, 'account')
            existing = context.journal.head(account, services.journal_context)
            if existing.state == 'completed':
                snapshot = context.journal.snapshot(account, '1', services.journal_context)
                view = snapshot.value
                r = codec.Resolver((*context.read.views, *snapshot.records.dependencies, view), limits=context.limits)
                root = root_of(view, r)
                actual, _ = r.record(root['account'], view.package_id)
                target, _ = r.record(actual['payload']['target'], view.package_id)
                if actual['payload']['purpose'] != commission.purpose or target['payload'] != commission.target or root['audience'] != commission.audience or root['requirements'] != commission.requirements:
                    raise ExecutionError('s3.commission_identity_conflict')
                return api.CallResult('completed', view, records=snapshot.records)
            if existing.issues[0].code != 's3.account_not_open': return existing
            for ref, kind in [(commission.audience, 's3.audience'), (commission.requirements, 's3.requirement_context')]:
                if ref.get('binding') != 'external' or resolver.record(ref, ref['package_id'])[0]['record_type'] != kind:
                    raise ExecutionError('s3.qualified_commission_context_required')
            b = Builder('Execution account commission')
            target = b.add('target', commission.target)
            account = b.add('account', {'purpose': commission.purpose, 'target': target, 'related_accounts': index()}, record_id=commission.account_id)
            frontier = b.add('frontier', {'local_records': index([account, target]), 'source_positions': index(), 'selection_rule': contract('s3.fixed_commission_cutoff')})
            disposition = b.add('disposition', {'kind': 'no_effect_selected', 'operations': index(), 'requirements': commission.requirements, 'frontier': frontier, 'basis': []})
            root = b.add('account_view', {'account': account, 'view_role': 'full_account', 'audience': commission.audience,
                'frontier': frontier, 'requirements': commission.requirements, 'activities': index(), 'evidence': index(), 'assessments': index(),
                'disposition': disposition, 'obligations': index(), 'collections': index()})
            view = frozen(b, root, context.read)
            result = context.journal.append(account, '0', commission.account_id,
                api.CommitDelta(view.records, tuple(view.package['roots']), (*context.read.views, view)), services.journal_context)
            if result.state != 'completed': return result
            self._fault(services, 'after_open_commit')
            return api.CallResult('completed', result.value.head.snapshot,
                records=api.RecordDelta(dependencies=(*context.read.views, view)))
        except ExecutionError as exc: return api.rejected(exc.code)
        except Exception: return api.rejected('s3.open_result_unconfirmed')

    def _evaluate(self, binding, view, read):
        resolver = codec.Resolver((*read.views, view), limits=read.limits)
        root = root_of(view, resolver)
        req, pid = resolver.record(root['requirements'], view.package_id)
        payload = req['payload']
        # Preserving opaque bytes is not interpreting an admission-critical
        # condition. Apply the shared B01 guard to the exact supplied closure,
        # including earlier owned-format snapshots, before any executable grant.
        from .registry import require_critical_semantics
        claims = {'s3.operational_admission', binding.record['payload']['operation']['name']}
        for requested in payload['requested_claims']['members']:
            claim, _ = resolver.record(requested, pid)
            claims.add(claim['payload']['claim']['name'])
        for dependency in resolver.closure(view.package_id):
            require_critical_semantics(dependency, claims, read.registry.payloads, read.limits)
        if payload['coverage']['extent'] != 'complete_for_scope' or payload['requested_claims']['extent'] != 'complete_for_scope':
            raise ExecutionError('s3.requirement_coverage_unestablished')
        rule = self._rules.get(key(payload['catalog']))
        if rule is None or binding.record['payload']['operation'] not in rule.operations:
            raise ExecutionError('s3.requirement_evaluator_unavailable')
        # Every advertised conditional family must have known applicability and
        # semantics. The installed rule evaluates its actual scoped evidence.
        from .schema import validate_family
        for ref in payload['coverage']['members']:
            case, _ = resolver.record(ref, pid)
            if not validate_family(case['payload']) or case['payload']['applicability'] not in ('applies', 'not_applicable') or case['payload']['gaps']:
                raise ExecutionError('s3.required_family_unestablished')
        _verify_implementation(rule.implementation)
        frontier = qualified(root['frontier'], view.package_id)
        result = callable_value(rule.evaluate)(binding, qualified(root['requirements'], view.package_id), frontier, read)
        if not isinstance(result, api.RequirementEvaluation) or result.frontier != frontier or result.requirements != qualified(root['requirements'], view.package_id):
            raise ExecutionError('s3.requirement_evaluation_binding_mismatch')
        if result.withheld or result.issues: raise ExecutionError('s3.required_prerequisites_unestablished')
        for requested in payload['requested_claims']['members']:
            claim, claim_pid = resolver.record(requested, pid)
            expected = claim['payload']
            matches = [c for c in result.established if isinstance(c, api.ClaimRequest) and c.contract == expected['claim'] and c.scope == expected['scope']]
            if len(matches) != 1 or expected['parameters']['extent'] != 'complete_for_scope':
                raise ExecutionError('s3.requested_claim_unestablished')
            actual = matches[0].parameters
            if not isinstance(actual, api.PinnedInputs) or [resolver.record(e.reference, e.source_package)[0] for e in actual.entries] != [resolver.record(r, claim_pid)[0] for r in expected['parameters']['members']]:
                raise ExecutionError('s3.claim_parameter_binding_mismatch')
        self._scientific(binding, view, resolver)
        return result, rule

    @staticmethod
    def _scientific(binding, view, resolver):
        if binding.record['payload']['operation']['name'] != 's3.op.launch': return
        from .scientific import match_run, require_scientific
        params = {p['key']: p['value'] for p in binding.record['payload']['parameters']}
        roles = {r['role']: r['members']['members'] for r in binding.record['payload']['roles']}
        request = roles['s3.role.request'][0]; attempt = roles['s3.role.attempt'][0]
        request_record, qpid = resolver.record(request, view.package_id)
        request = qualified(request, qpid)
        _, apid = resolver.record(attempt, view.package_id); attempt = qualified(attempt, apid)
        # Positive compiler metadata cannot be hidden by a probe enum.
        metadata = [r for r in resolver.view(qpid).records if r['record_type'] == 's1.relation' and
            r['payload']['relation_contract']['name'] == 's2.request_projection_metadata' and
            any(e['target']['target'] == request['target'] for e in r['payload']['endpoints'])]
        run_refs = roles['s3.role.scientific_binding']
        matches = []
        for run in run_refs:
            run_record, rpid = resolver.record(run, view.package_id); run = qualified(run, rpid)
            candidates = [(r, v.package_id) for v in binding.inputs.source_views for r in v.records if r['record_type'] == 's2.request_binding_receipt' and
                r['payload']['run']['target'] == run_record['id'] and r['payload']['request']['target'] == request['target'] and r['payload']['attempt']['target'] == attempt['target']]
            if len(candidates) != 1: raise ExecutionError('s3.scientific_handoff_unestablished')
            record, hpid = candidates[0]
            matches.append(match_run(run, request, attempt, reference(record['id'], record['record_type'], hpid), resolver))
        purpose = params['purpose']['value']
        require_scientific(purpose='scientific_run' if purpose == 'scientific_run' else 'preparation_probe',
            visible_scientific_intent=bool(metadata or run_refs), matches=matches,
            na_rule=params['scientific_rule']['value'], fixed_before_effect=True)

    def plan(self, view, request, context):
        try:
            if not isinstance(request, api.OperationRequest): raise ExecutionError('s3.operation_request_required')
            validate_value(request.request_occurrence, 'ID')
            resolver = codec.Resolver((*context.views, view), limits=context.limits)
            if any(not context.access.permits(v.package_id) for v in context.views): raise ExecutionError('s3.read_denied')
            resolver.closure(view.package_id)
            root = root_of(view, resolver)
            payload = relocate({'operation': request.operation, 'roles': list(request.roles), 'parameters': list(request.parameters)}, view.package_id)
            validate_binding(payload, admission=True)
            row = operation(request.operation)
            if row['pure'] or not row['port'].startswith('Driver.'):
                raise ExecutionError('s3.operation_requires_own_pure_or_service_port')
            descriptor = context.registry.drivers.lookup(request.operation)
            requirement_record, _ = resolver.record(root['requirements'], view.package_id)
            rule = self._rules.get(key(requirement_record['payload']['catalog']))
            if rule is None: raise ExecutionError('s3.requirement_evaluator_unavailable')
            b = Builder('Pure operation plan')
            capture_pins = ()
            if request.operation['name'] in ('s3.op.observe', 's3.op.acknowledge'):
                if self.collector is None: raise ExecutionError('s3.capture_handler_unavailable')
                self.collector.install(context.registry)
                capture_pins = self.collector.dependencies(payload, view.package_id, resolver)
            binding_ref = b.add('operation_binding', payload)
            command = b.add('effect_command', {'account': qualified(root['account'], view.package_id), 'operation': request.operation,
                'binding': binding_ref, 'targets': scope(qualified(root['account'], view.package_id)),
                'dependencies': index([descriptor.component, descriptor.implementation.reference, rule.implementation.reference,
                    *(p.reference for p in capture_pins if p.reference not in (descriptor.implementation.reference, rule.implementation.reference))]), 'admission': unknown('s3.not_admitted'),
                'frontier': qualified(root['frontier'], view.package_id)}, record_id=request.request_occurrence)
            # Keep the exact original frontier and scientific context immutable.
            relocated = relocate(root, view.package_id)
            relocated['activities'] = index([command])
            plan_root = b.add('account_view', relocated)
            staged = frozen(b, plan_root, read_with(context, view, descriptor.implementation.source_view, *(p.source_view for p in capture_pins)))
            read = read_with(context, view, staged, descriptor.implementation.source_view, *(p.source_view for p in capture_pins))
            r = codec.Resolver(read.views, limits=read.limits)
            binding = resolve_binding(qualified(binding_ref, staged.package_id), staged.package_id, r)
            requirements, rule = self._evaluate(binding, staged, read)
            if not any(v.package_id == rule.implementation.source_view.package_id for v in read.views):
                raise ExecutionError('s3.admission_rule_source_not_pinned')
            native = read.registry.drivers.prepare(binding, binding.inputs, read)
            if native.state != 'completed': return native
            invocation_route(native.value.invocation, descriptor.input_contract, read.registry.payloads)
            return api.CallResult('completed', api.PreparedOperation(qualified(binding_ref, staged.package_id), staged,
                requirements, descriptor, api.PinnedClosure(r.closure(staged.package_id), binding.inputs.entries), qualified(command, staged.package_id)))
        except ExecutionError as exc: return api.rejected(exc.code)
        except Exception: return api.rejected('s3.plan_evaluation_failed')

    @staticmethod
    def _actual(prepared, read):
        if not isinstance(prepared, api.PreparedOperation): raise ExecutionError('s3.prepared_operation_required')
        resolver = codec.Resolver((*read.views, *prepared.dependencies.views, prepared.source_view), limits=read.limits)
        resolver.closure(prepared.source_view.package_id)
        binding = resolve_binding(prepared.binding, prepared.source_view.package_id, resolver)
        command, pid = resolver.record(prepared.command, prepared.source_view.package_id)
        if command['payload']['operation'] != binding.record['payload']['operation'] or binding_digest(resolve_binding(command['payload']['binding'], pid, resolver)) != binding_digest(binding):
            raise ExecutionError('s3.prepared_command_binding_mismatch')
        actual = read.registry.drivers.lookup(binding.record['payload']['operation'])
        from .registry import _copy_descriptor
        if _copy_descriptor(actual) != _copy_descriptor(prepared.driver): raise ExecutionError('s3.prepared_driver_mismatch')
        return binding, resolver, command

    def restore_prepared(self, command, source_view, context):
        """Pure reconstruction from exact persisted C bytes and supplied code.

        Restores a plan, never an admission/grant/permit or a new command identity.
        The caller must separately obtain actual current owner admission.
        """
        try:
            read_with(context)
            resolver = codec.Resolver((*context.views, source_view), limits=context.limits)
            record, pid = resolver.record(command, source_view.package_id)
            if record['record_type'] != 's3.effect_command' or pid != source_view.package_id:
                raise ExecutionError('s3.original_command_source_required')
            binding = resolve_binding(record['payload']['binding'], pid, resolver)
            validate_binding(binding.record['payload'], admission=True)
            descriptor = context.registry.drivers.lookup(record['payload']['operation'])
            component, _ = resolver.record(descriptor.component, pid)
            declared = [resolver.record(r, pid)[0] for r in record['payload']['dependencies']['members']]
            if component not in declared: raise ExecutionError('s3.restored_driver_dependency_mismatch')
            original_read = replace(context, views=resolver.closure(pid), access=api.supplied_read(v.package_id for v in resolver.closure(pid)))
            requirements, _ = self._evaluate(binding, source_view, original_read)
            native = context.registry.drivers.prepare(binding, binding.inputs, original_read)
            if native.state != 'completed': return native
            invocation_route(native.value.invocation, descriptor.input_contract, context.registry.payloads)
            return api.CallResult('completed', api.PreparedOperation(qualified(record['payload']['binding'], pid), source_view,
                requirements, descriptor, api.PinnedClosure(resolver.closure(pid), binding.inputs.entries), qualified(command, pid)))
        except ExecutionError as exc: return api.rejected(exc.code)

    @staticmethod
    def _timely(services, context):
        if services.deadline['state'] == 'not_applicable': require_before(services.deadline, None); return
        reading = context.clock.now(services.clock_context)
        if reading.state != 'completed': raise ExecutionError('s3.clock_observation_unestablished')
        require_before(services.deadline, reading.value)

    def compile(self, run, occurrence, context):
        from .bridge import compile_request
        return compile_request(run, occurrence, context)

    def _owner_requests(self, binding, group, services, read):
        b = Builder('Exact admission allocations'); refs = []; stores = []
        for allocation in services.owners:
            if allocation.replay_contract != contract('s3.owner.same_request_exact_replay'):
                raise ExecutionError('s3.owner_replay_protocol_unestablished')
            amounts = []
            for template in allocation.amounts:
                if set(template) != {'resource', 'unit', 'quantity', 'aggregation'}:
                    raise ExecutionError('s3.explicit_allocation_template_required')
                amounts.append({**copy.deepcopy(template), 'scope': scope(qualified(reference(binding.record['id'], 'operation_binding'), binding.context['package_id']))})
            ref, store = typed_document(b, contract('s3.payload.reservation_amounts'), {'entries': amounts})
            refs.append(ref); stores.append(store)
        # A private packet is metadata; it cannot mint an owner capability.
        root = root_of(next(v for v in read.views if v.package_id == binding.context['package_id']), codec.Resolver(read.views, limits=read.limits))
        projection = b.add('projection_view', {'view_role': 'audience_projection', 'audience': qualified(root['audience'], binding.context['package_id']),
            'projection_contract': contract('s3.exact_allocations'), 'members': index(refs), 'claims': index(), 'limits': index()})
        view = frozen(b, projection, read_with(read, *stores))
        read = read_with(read, *stores, view)
        requests = []
        for allocation, ref in zip(services.owners, refs):
            # An explicit expected revision is a conditional request, not proof
            # that an owner is currently at that revision. Do not perform an
            # unrecorded owner query just to construct its first durable R.
            validate_value(allocation.expected_revision, 'Index')
            occurrence, correlation = identity(), identity()
            params = {'correlation': correlation, 'request_occurrence': occurrence, 'admission_occurrence': group,
                'amounts': qualified(ref, view.package_id), 'expected_revision': allocation.expected_revision}
            requests.append(api.ExactOwnerRequest(contract('s3.op.owner_reserve'), allocation.owner.owner, correlation, binding,
                tuple({'key': k, 'value': known(v)} for k, v in params.items()), api.PinnedInputs((), binding.inputs.source_views), occurrence, group))
        return tuple(requests), read

    @staticmethod
    def _load_requests(head, group, binding, read, services):
        resolver = codec.Resolver((*read.views, head.snapshot), limits=read.limits)
        plans = [r for r in head.snapshot.records if r['id'] == group]
        if not plans: return None
        if plans[0]['record_type'] != 's3.typed_payload': raise ExecutionError('s3.admission_occurrence_conflict')
        registry = read.registry.payloads
        selected = contract('s3.owner.exact_request')
        if not registry.supports(selected):
            def decode(value):
                if not isinstance(value, dict) or set(value) != {'operation','owner','correlation','target_binding','binding_digest','parameters','request_occurrence','admission_occurrence','evidence'}:
                    raise ExecutionError('s3.exact_owner_body_shape')
                return value
            registry.register(selected, decode)
        plan = resolver.payload(reference(group, 'typed_payload', head.snapshot.package_id), head.snapshot.package_id, registry)
        if plan['binding_digest'] != binding_digest(binding) or len(plan['owner_requests']) != len(services.owners):
            raise ExecutionError('s3.admission_occurrence_binding_conflict')
        requests = []
        for original, allocation in zip(plan['owner_requests'], services.owners):
            if original['owner'] != allocation.owner.owner: raise ExecutionError('s3.admission_owner_set_conflict')
            body = resolver.payload(reference(original['request_occurrence'], 'typed_payload', head.snapshot.package_id), head.snapshot.package_id, registry)
            if body['binding_digest'] != binding_digest(binding) or body['evidence']:
                raise ExecutionError('s3.admission_owner_request_conflict')
            restored = api.ExactOwnerRequest(body['operation'], body['owner'], body['correlation'], binding, tuple(body['parameters']),
                api.PinnedInputs((), binding.inputs.source_views), body['request_occurrence'], body['admission_occurrence'])
            if owner_request_body(restored) != body: raise ExecutionError('s3.admission_owner_request_conflict')
            requests.append(restored)
        return tuple(requests), read_with(read, *resolver._views.values())

    def admit(self, prepared, expected_head, context, admission_occurrence):
        results = []
        try:
            services = self._services(context); validate_value(admission_occurrence, 'ID')
            if set(services.required_owners) != {o.role for o in services.owners}: raise ExecutionError('s3.required_owner_missing')
            binding, resolver, command = self._actual(prepared, context.read)
            account = command['payload']['account']
            if account['target'] != expected_head.account['target']: raise ExecutionError('s3.admission_account_mismatch')
            # Evaluate against the ORIGINAL pinned plan, not later ambient views.
            original = replace(context.read, views=prepared.dependencies.views, access=api.supplied_read(v.package_id for v in prepared.dependencies.views))
            evaluation, _ = self._evaluate(binding, prepared.source_view, original)
            if evaluation != prepared.requirements: raise ExecutionError('s3.prepared_requirements_changed')
            self._timely(services, context)
            read = read_with(context.read, *resolver._views.values())
            jctx = replace(services.journal_context, read=read)
            head_result = context.journal.head(account, jctx)
            if head_result.state != 'completed': return head_result
            head = head_result.value
            read = read_with(read, *head_result.records.dependencies, head.snapshot)
            loaded = self._load_requests(head, admission_occurrence, binding, read, services)
            if loaded is None:
                if head.revision != expected_head.revision: raise ExecutionError('s3.stale_journal_revision')
                # Pin C before any admission RPC; this is metadata only.
                persisted = context.journal.append(account, head.revision, correlation_id('s3.plan', admission_occurrence),
                    api.CommitDelta(prepared.source_view.records, (), (*read.views, prepared.source_view)), jctx)
                if persisted.state != 'completed': return persisted
                requests, read = self._owner_requests(binding, admission_occurrence, services, read)
                jctx = replace(jctx, read=read)
                planned = persist_owner_requests(context.journal, persisted.value.head, requests, jctx, read)
                if planned.state != 'completed': return planned
                retained = context.journal.head(account, jctx)
                if retained.state != 'completed': return retained
                head = retained.value
                read = read_with(read, *retained.records.dependencies, head.snapshot)
            else: requests, read = loaded
            self._fault(services, 'after_admission_plan')
            for position, (allocation, request) in enumerate(zip(services.owners, requests)):
                octx = replace(allocation.context, read=read_with(allocation.context.read, *read.views))
                result = allocation.owner.reserve(request, octx)
                results.append((allocation.owner, result, octx))
                # Retain each actual response before advancing the next owner.
                if result.records.dependencies or result.records.records:
                    head = context.journal.head(account, jctx).value
                    transaction = correlation_id('s3.owner.response', request.request_occurrence)
                    if not any(r['record_type'] == 's3.journal_receipt' and r['payload']['transaction'] == transaction for r in head.snapshot.records):
                        retained = context.journal.append(account, head.revision, transaction,
                            api.CommitDelta(result.records.records, (), result.records.dependencies), jctx)
                        if retained.state != 'completed': return api.rejected('s3.owner_response_commit_unconfirmed', records=result.records)
                        head = retained.value.head
                    read = read_with(read, head.snapshot, *result.records.dependencies)
                self._fault(services, 'after_owner_' + str(position))
            from .authority import require_owner_grants
            grants = require_owner_grants(tuple(results), binding, binding.record['payload']['operation'])
            head = context.journal.head(account, jctx).value
            validity = api.ValidityContext((), copy.deepcopy(services.deadline), (), api.RecordDelta())
            assessment, head = self._assessment(head, prepared, context, services, read, admission_occurrence)
            admission = api.LiveAdmission(prepared, tuple(copy.deepcopy(r.value.receipt) for _, r, _ in results), grants, head,
                validity, admission_occurrence, reference(admission_occurrence, 'typed_payload', head.snapshot.package_id),
                assessment)
            # Exact actual admission instance: dataclass replacement cannot mint it.
            self._admissions[id(admission)] = (admission, services, tuple(results), binding_digest(binding))
            self._fault(services, 'before_admit_reply')
            return api.CallResult('completed', admission, records=api.RecordDelta(dependencies=(head.snapshot,)))
        except ExecutionError as exc:
            return api.rejected(exc.code, records=api.RecordDelta(dependencies=tuple(v for _, r, _ in results for v in r.records.dependencies)))
        except Exception:
            return api.rejected('s3.admission_result_unconfirmed', records=api.RecordDelta(dependencies=tuple(v for _, r, _ in results for v in r.records.dependencies)))

    @staticmethod
    def _assessment(head, prepared, context, services, read, occurrence):
        rid = correlation_id('s3.admission.assessment', occurrence)
        if any(r['id'] == rid for r in head.snapshot.records):
            return reference(rid, 'assessment', head.snapshot.package_id), head
        b = Builder('Scoped current admission decision')
        ref = b.add('assessment', {'question': contract('s3.operational_admission'), 'scope': scope(prepared.command), 'result': known(True),
            'basis': index([prepared.binding]), 'frontier': prepared.requirements.frontier, 'procedure': contract('s3.current_all_owner_checks'),
            'revises': [], 'conflicts_with': []}, record_id=rid)
        root = root_of(prepared.source_view, codec.Resolver(read.views, limits=read.limits))
        projection = b.add('projection_view', {'view_role': 'audience_projection', 'audience': qualified(root['audience'], prepared.source_view.package_id),
            'projection_contract': contract('s3.admission_evidence'), 'members': index([ref]), 'claims': index([ref]), 'limits': index()})
        view = frozen(b, projection, read)
        result = context.journal.append(head.account, head.revision, correlation_id('s3.admission.assessment.commit', occurrence),
            api.CommitDelta(view.records, (), (*read.views, view)), replace(services.journal_context, read=read))
        if result.state != 'completed': raise ExecutionError('s3.admission_assessment_unconfirmed')
        return qualified(ref, view.package_id), result.value.head

    def issue(self, admission, context, transmission_occurrence):
        intent = None; forwarded = False; observed = None; evidence = None
        try:
            services = self._services(context); validate_value(transmission_occurrence, 'ID')
            # Runtime dataclass contains dict fields: use identity bindings, not
            # equality or reconstructable fields, for the live admission proof.
            issued = self._admissions.get(id(admission))
            if issued is None or issued[0] is not admission or issued[1] is not services: raise ExecutionError('s3.actual_live_admission_required')
            if admission.owner_receipts != tuple(r.value.receipt for _, r, _ in issued[2]) or admission.live_grants != tuple(r.value.grant for _, r, _ in issued[2]):
                raise ExecutionError('s3.live_admission_owner_binding_changed')
            if admission.validity != api.ValidityContext((), services.deadline, (), api.RecordDelta()):
                raise ExecutionError('s3.live_admission_validity_changed')
            prepared = admission.prepared
            binding, resolver, command = self._actual(prepared, context.read)
            if issued[3] != binding_digest(binding): raise ExecutionError('s3.admission_binding_changed')
            original = replace(context.read, views=prepared.dependencies.views, access=api.supplied_read(v.package_id for v in prepared.dependencies.views))
            evaluation, _ = self._evaluate(binding, prepared.source_view, original)
            if evaluation != prepared.requirements: raise ExecutionError('s3.prepared_requirements_changed')
            read = read_with(context.read, *resolver._views.values())
            jctx = replace(services.journal_context, read=read)
            current = context.journal.head(command['payload']['account'], jctx)
            if current.state != 'completed': return current
            head = current.value
            read = read_with(read, *current.records.dependencies, head.snapshot)
            source = prepared.source_view
            # Never mint a second transmission for an unresolved prior command.
            transmissions = [r for r in head.snapshot.records if r['record_type'] == 's3.transmission' and r['payload']['command']['target'] == command['id']]
            if transmissions and transmission_occurrence not in {r['id'] for r in transmissions}:
                raise ExecutionError('s3.prior_transmission_requires_reconciliation')
            prepared_call = context.drivers.prepare(binding, binding.inputs, replace(read, views=prepared.dependencies.views,
                access=api.supplied_read(v.package_id for v in prepared.dependencies.views)))
            if prepared_call.state != 'completed': return prepared_call
            receiver, channel = invocation_route(prepared_call.value.invocation, prepared.driver.input_contract, context.read.registry.payloads)
            b = Builder('Single transmission intent')
            d = b.add('transmission', {'command': prepared.command, 'channel': channel, 'recipient': receiver,
                'ownership': unknown(), 'sent_at': unknown(), 'receipts': index()}, record_id=transmission_occurrence)
            root = root_of(source, resolver)
            projection = b.add('projection_view', {'view_role': 'audience_projection', 'audience': qualified(root['audience'], source.package_id),
                'projection_contract': contract('s3.transmission_intent'), 'members': index([d]), 'claims': index(), 'limits': index()})
            if transmissions:
                # Reuse original bytes, producer, package and IDs, not refreeze D.
                existing = transmissions[0]
                dref = reference(existing['id'], 'transmission', head.snapshot.package_id)
                return self._replay_issue(admission, context, services, head, read, dref)
            staged = frozen(b, projection, read)
            dref = qualified(d, staged.package_id)
            read = read_with(read, staged)
            self._timely(services, context)
            from .authority import require_owner_grants
            require_owner_grants(issued[2], binding, binding.record['payload']['operation'])
            token = context.journal.prepare_issue(prepared.command, head,
                api.OwnerBindingReceipts(admission.owner_receipts, binding_digest(binding), admission.validity), replace(jctx, read=read), dref)
            if token.state != 'completed': return token
            intent = token.value
            self._fault(services, 'after_issue_intent')
            if token.value.runtime_permit is None:
                return self._unresolved_issue(admission, token.value, 's3.intent_replayed_without_forwarding')
            # Recheck after durable intent and immediately before entering driver.
            self._timely(services, context)
            require_owner_grants(issued[2], binding, binding.record['payload']['operation'])
            exact = api.ExactOperationRequest(prepared.command, binding, binding.inputs, prepared.driver, source)
            native_context = replace(services.driver_context, read=read)
            if binding.record['payload']['operation']['name'] == 's3.op.observe':
                if self.collector is None: raise ExecutionError('s3.capture_handler_unavailable')
                self.collector.before(exact, token.value, context.journal, services.journal_context, read)
            elif binding.record['payload']['operation']['name'] == 's3.op.acknowledge':
                if self.collector is None: raise ExecutionError('s3.capture_handler_unavailable')
                self.collector.acknowledgement(exact, token.value, context.journal, services.journal_context, read)
            forwarded = True
            result = callable_value(prepared.driver.method)(exact, native_context, admission.live_grants, token.value, services.sink)
            if not isinstance(result, api.CallResult): raise ExecutionError('s3.driver_return_contract')
            observed = result
            from .native_results import result_evidence
            captured = None
            if isinstance(result.value, api.NativeBatch):
                if self.collector is None: raise ExecutionError('s3.capture_handler_unavailable')
                try:
                    captured = self.collector.collect(result.value, result, exact, token.value, context.journal, services.journal_context, read)
                except Exception as exc:
                    code = exc.code if isinstance(exc, ExecutionError) else 's3.native_capture_unconfirmed'
                    evidence = self.collector.salvage(result.value, result, exact, read, code)
                    raise ExecutionError(code) from None
                evidence = captured
                self._fault(services, 'after_capture_commit')
            evidence = result_evidence(result, prepared.binding, read, captured=captured)
            retained = self._save_issue(admission, context, services, token.value, result, evidence, read)
            self._fault(services, 'before_issue_reply')
            return retained
        except ExecutionError as exc:
            retained = self._issue_problem(admission, context, services, intent, read, exc.code) if intent is not None else api.RecordDelta()
            return self._issue_interruption(admission, intent, forwarded, observed, evidence, exc.code, retained)
        except Exception:
            retained = self._issue_problem(admission, context, services, intent, read, 's3.issue_result_unconfirmed') if intent is not None else api.RecordDelta()
            return self._issue_interruption(admission, intent, forwarded, observed, evidence, 's3.issue_result_unconfirmed', retained)

    @staticmethod
    def _issue_problem(admission, context, services, token, read, code):
        """Retain scoped diagnostics/liability without inventing native outcome."""
        try:
            rid = correlation_id('s3.issue.problem', token.transmission['target'] + ':' + code)
            current = context.journal.head(token.intent_commit.head.account, services.journal_context)
            if current.state != 'completed': return api.RecordDelta()
            if any(r['id'] == rid for r in current.value.snapshot.records):
                return api.RecordDelta(dependencies=(*current.records.dependencies, current.value.snapshot))
            read = read_with(read, *current.records.dependencies, current.value.snapshot)
            b = Builder('Unconfirmed issue obligation')
            diagnostic = b.add('diagnostic', {'code': code, 'scope': scope(token.command, token.transmission),
                'details': 'Local operation interrupted; receiver acceptance and outstanding liabilities remain separately scoped.',
                'evidence': [token.transmission]}, record_id=rid)
            obligation = b.add('obligation', {'question': contract('s3.reconcile_issue_effects'), 'scope': scope(token.command, token.transmission),
                'owner': unknown_ref('component', 's3.follow_up_owner_unassigned'), 'disposition': 'unresolved', 'basis': [diagnostic, token.transmission], 'follow_up': index()})
            root = root_of(admission.prepared.source_view, codec.Resolver(read.views, limits=read.limits))
            projection = b.add('projection_view', {'view_role': 'audience_projection', 'audience': qualified(root['audience'], admission.prepared.source_view.package_id),
                'projection_contract': contract('s3.issue_problem'), 'members': index([diagnostic, obligation]), 'claims': index(), 'limits': index()})
            view = frozen(b, projection, read)
            delta = api.RecordDelta(view.records, (), (*read.views, view))
            context.journal.append(current.value.account, current.value.revision, correlation_id('s3.issue.problem.commit', rid),
                api.CommitDelta(delta.records, (), delta.dependencies), replace(services.journal_context, read=read))
            return delta
        except Exception:
            return api.RecordDelta()  # Original issue evidence/result still returned.

    @staticmethod
    def _issue_interruption(admission, token, forwarded, observed, evidence, code, retained):
        if token is None: return api.rejected(code)
        effects = observed.effects if observed is not None else (api.EffectBoundary(token.command,
            'may_have_crossed' if forwarded else 'not_crossed', unknown('s3.receiver_acceptance_unestablished'), (), token.transmission),)
        if evidence is None and observed is not None and isinstance(observed.records, api.RecordDelta):
            evidence = api.DriverEvidence(admission.prepared.binding, observed.records, index(extent='unresolved'), index(extent='unresolved'), index(), ())
        if evidence is not None:
            return api.CallResult('partial', api.IssueReceipt(token.command, token, evidence, effects, token.transmission, admission.admission_occurrence),
                records=evidence.records, issues=(api.Issue(code, scope(token.command), ()),), effects=effects)
        return api.rejected(code, records=retained, effects=effects)

    def _save_issue(self, admission, context, services, token, result, evidence, read):
        if evidence.records.native_additions or evidence.records.scientific_additions:
            return api.CallResult('partial', api.IssueReceipt(admission.prepared.command, token, evidence, result.effects, token.transmission, admission.admission_occurrence),
                records=evidence.records, issues=(api.Issue('s3.owned_additions_require_freeze', scope(token.command), ()),), effects=result.effects)
        b = Builder('Durable driver return, not native success inference')
        body = {'state': result.state, 'issues': [{'code': i.code, 'scope': i.scope, 'evidence': list(i.evidence)} for i in result.issues],
            'effects': [{'command': e.command, 'boundary': e.boundary, 'acceptance': e.acceptance, 'evidence': list(e.evidence), 'transmission': e.transmission} for e in result.effects],
            'binding': evidence.binding, 'subjects': evidence.subjects, 'receipts': evidence.receipts, 'assessments': evidence.assessments,
            'transmission': token.transmission, 'admission_occurrence': admission.admission_occurrence}
        ref, store = typed_document(b, contract('s3.payload.driver_return'), body)
        root = root_of(admission.prepared.source_view, codec.Resolver(read.views, limits=read.limits))
        projection = b.add('projection_view', {'view_role': 'audience_projection', 'audience': qualified(root['audience'], admission.prepared.source_view.package_id),
            'projection_contract': contract('s3.driver_return'), 'members': index([ref]), 'claims': index(), 'limits': index()},
            record_id=correlation_id('s3.driver.return.record', token.transmission['target']))
        read = read_with(read, store, *evidence.records.dependencies)
        view = frozen(b, projection, read)
        head = context.journal.head(token.intent_commit.head.account, services.journal_context).value
        committed = context.journal.append(head.account, head.revision, correlation_id('s3.driver.return.commit', token.transmission['target']),
            api.CommitDelta((*evidence.records.records, *view.records), (), (*read.views, view)), replace(services.journal_context, read=read))
        receipt = api.IssueReceipt(admission.prepared.command, token, evidence, result.effects, token.transmission, admission.admission_occurrence)
        if committed.state != 'completed':
            return api.CallResult('partial', receipt, records=evidence.records, effects=result.effects,
                issues=(*result.issues, api.Issue('s3.driver_result_commit_unconfirmed', scope(token.command), ())))
        return api.CallResult(result.state if result.state != 'rejected' else 'partial', receipt, records=evidence.records,
            effects=result.effects, issues=result.issues)

    @staticmethod
    def _unresolved_issue(admission, token, code):
        evidence = api.DriverEvidence(admission.prepared.binding, api.RecordDelta(), index(extent='unresolved'), index(extent='unresolved'), index(), ())
        effect = api.EffectBoundary(token.command, 'may_have_crossed', unknown('s3.receiver_acceptance_unestablished'), (), token.transmission)
        return api.CallResult('partial', api.IssueReceipt(token.command, token, evidence, (effect,), token.transmission, admission.admission_occurrence),
            issues=(api.Issue(code, scope(token.command), ()),), effects=(effect,))

    def _replay_issue(self, admission, context, services, head, read, transmission):
        read = read_with(read, head.snapshot)
        token = context.journal.prepare_issue(admission.prepared.command, head,
            api.OwnerBindingReceipts(admission.owner_receipts, binding_digest(resolve_binding(admission.prepared.binding,
                admission.prepared.source_view.package_id, codec.Resolver(read.views, limits=read.limits))), admission.validity),
            replace(services.journal_context, read=read), transmission)
        if token.state != 'completed': return token
        rid = correlation_id('s3.driver.return.record', transmission['target'])
        records = [r for r in head.snapshot.records if r['id'] == rid]
        if not records: return self._unresolved_issue(admission, token.value, 's3.intent_replayed_without_forwarding')
        payload_ref = records[0]['payload']['members']['members'][0]
        registry = read.registry.payloads
        selected = contract('s3.payload.driver_return')
        if not registry.supports(selected):
            def decode(value):
                if not isinstance(value, dict) or set(value) != {'state','issues','effects','binding','subjects','receipts','assessments','transmission','admission_occurrence'}:
                    raise ExecutionError('s3.driver_return_payload_shape')
                return value
            registry.register(selected, decode)
        resolver = codec.Resolver(read.views, limits=read.limits)
        body = resolver.payload(payload_ref, head.snapshot.package_id, registry)
        if body['admission_occurrence'] != admission.admission_occurrence or body['transmission']['target'] != transmission['target']:
            raise ExecutionError('s3.driver_return_binding_conflict')
        effects = tuple(api.EffectBoundary(**e) for e in body['effects'])
        evidence = api.DriverEvidence(body['binding'], api.RecordDelta(dependencies=(head.snapshot,)), body['subjects'], body['receipts'], body['assessments'], ())
        receipt = api.IssueReceipt(admission.prepared.command, token.value, evidence, effects, transmission, admission.admission_occurrence)
        issues = tuple(api.Issue(i['code'], i['scope'], tuple(i['evidence'])) for i in body['issues'])
        return api.CallResult(body['state'] if body['state'] != 'rejected' else 'partial', receipt, records=evidence.records, issues=issues, effects=effects)
