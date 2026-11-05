"""Reuse actual S1 invocation guards without minting native authority.

DLV-08/09. Owners supply the ports, exact prepared spec, actual execution
context/grant and owned working buffer. Manifest code/lease text is insufficient.
"""
from dataclasses import dataclass
from . import api, codec
from .bridge import WorkingS1, freeze_owned
from .drivers import NativeReply
from .model import ExecutionError, canonical, contract, digest, qualified, reference, known, unknown
from .registry import callable_value


@dataclass(frozen=True, slots=True)
class S1Invocation:
    working: WorkingS1
    ports: object
    specification: object
    execution_context: object
    sink: object
    identify: api.SuppliedCallable | None = None

    def __post_init__(self):
        from crucis_causal.connections.api import InvocationSpec, ExecutionContext
        if not isinstance(self.working, WorkingS1) or not isinstance(self.specification, InvocationSpec) or not isinstance(self.execution_context, ExecutionContext):
            raise ExecutionError('s3.actual_s1_invocation_binding_required')
        if not callable(getattr(self.ports, 'invoke', None)) or self.sink.records is not self.working.buffer:
            raise ExecutionError('s3.actual_s1_ports_and_owned_sink_required')
        self.working.verify()

    def prepare(self, binding, inputs, context):
        self.working.verify()
        if binding.record['payload']['operation'] != contract('s3.op.launch'):
            raise ExecutionError('s3.s1_invocation_operation_unavailable')
        roles = {e.role: e for e in inputs.entries if e.role in ('s3.role.request','s3.role.attempt','s3.role.binding')}
        originals = {'s3.role.request': self.working.request, 's3.role.attempt': self.working.attempt,
            's3.role.binding': self.specification.binding}
        for role, ref in originals.items():
            if role not in roles or canonical(roles[role].record) != canonical(self.working.buffer.get(ref)):
                raise ExecutionError('s3.s1_native_input_binding_mismatch')
        if self.execution_context.attempt != self.working.attempt:
            raise ExecutionError('s3.s1_native_execution_attempt_mismatch')
        resolver = codec.Resolver(context.views, limits=context.limits)
        params = {p['key']: p['value'] for p in binding.record['payload']['parameters']}
        typed, pid = resolver.record(params['invocation']['value'], binding.context['package_id'])
        if typed['payload']['payload_contract'] != contract('s3.native.s1_invocation'):
            raise ExecutionError('s3.s1_invocation_parameter_contract')
        from crucis_causal.connections.validation import content_bytes
        artifact, _ = resolver.record(typed['payload']['content']['artifact'], pid)
        expected = {'binding_id': self.specification.binding['target'], 'invocation_digest': digest(canonical(self.specification.invocation))}
        import json
        if typed['payload']['content']['selector']['state'] != 'not_applicable' or json.loads(content_bytes(artifact['payload']['content'])) != expected:
            raise ExecutionError('s3.s1_prepared_invocation_substituted')
        return expected

    def invoke(self, call):
        self.working.verify()
        result = self.ports.invoke(self.specification, self.execution_context, self.sink)
        self.working.verify()
        b = self.working.buffer.builder
        roots = [self.working.request, self.working.attempt]
        package = b.package(roots, external_packages=list(getattr(b, '_s2_external', {}).values()))
        from crucis_causal.experiments.api import ReaderLimits
        from crucis_causal.experiments.handoff import freeze_s1
        limits = self.working.limits
        prior_limits = ReaderLimits(limits.max_manifest_bytes, limits.max_records, limits.max_external_packages,
            limits.max_external_bytes, limits.max_reference_depth, limits.max_depth)
        immutable = freeze_s1(package, prior_limits)
        snapshot = codec.parse_snapshot(immutable.source_bytes, limits)
        dependencies = (*self.working.source_views, snapshot)
        # All additions are frozen in their real S1 namespace. The S3 journal
        # receives dependency bytes, not S1 records disguised as S3 records.
        facts = api.RecordDelta(dependencies=dependencies)
        freeze_owned(facts, native_snapshots=(snapshot,), limits=self.working.limits)
        if result.state == 'rejected':
            return NativeReply(None, {'name': 's1.octets', 'version': '0.1.0-proposal.1'},
                unknown('s3.s1_rejection_after_entry_effect_unresolved'), facts=facts)
        from crucis_causal.connections.api import NativeHandle
        if not isinstance(result.value, NativeHandle) or result.value.attempt != self.working.attempt:
            raise ExecutionError('s3.s1_native_handle_attempt_mismatch')
        descriptor = None
        if self.identify is not None: descriptor = callable_value(self.identify)(result.value)
        return NativeReply(None, {'name': 's1.octets', 'version': '0.1.0-proposal.1'}, known(True),
            descriptor=descriptor, facts=facts, origin_attempt=reference(self.working.attempt['target'], 's1.attempt', snapshot.package_id))
