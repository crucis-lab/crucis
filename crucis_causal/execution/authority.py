"""Actual issuer-owned process capabilities, never receipt deserialization.

DLV-08/09. Cooperative Python capability boundaries; not hostile-code isolation.
"""
import threading
import weakref
from dataclasses import dataclass
from . import api
from .model import ExecutionError,canonical,reference,unknown

class Authority:
    def __init__(self):
        self._issued=weakref.WeakKeyDictionary();self._lock=threading.RLock()

    def issue(self, binding, *, control=False):
        cls=api.OpaqueControlCapability if control else api.OpaqueGrant
        cap=cls(api._OPAQUE_KEY,self)
        with self._lock:self._issued[cap]=canonical(binding)
        return cap

    def check(self,cap,binding):
        if not isinstance(cap,(api.OpaqueControlCapability,api.OpaqueGrant)):
            raise ExecutionError('s3.actual_owner_capability_required')
        with self._lock:
            if self._issued.get(cap)!=canonical(binding):raise ExecutionError('s3.owner_capability_binding_mismatch')

    def revoke(self,cap):
        with self._lock:
            if isinstance(cap,(api.OpaqueControlCapability,api.OpaqueGrant)):self._issued.pop(cap,None)

def require_owner_grants(entries,binding,boundary):
    """Current per-owner checks; no distributed atomicity/receiver fence inferred.

    Each entry is (supplied owner port, its actual result, owner control context).
    Pure missingness checks precede any further admitted owner query. Existing
    partial holds remain untouched if another owner is unavailable or denies.
    """
    if not entries:raise ExecutionError('s3.required_owner_set_unestablished')
    for owner,result,context in entries:
        if not isinstance(result,api.CallResult) or result.state!='completed' or not isinstance(result.value,api.OwnerReceiptAndOptionalLiveGrant) or not isinstance(result.value.grant,api.OpaqueGrant):
            raise ExecutionError('s3.owner_group_incomplete')
        ref=result.value.receipt
        view=next((v for v in result.records.dependencies if v.package_id==ref.get('package_id')),None)
        record=next((r for r in view.records if r['id']==ref['target']),None) if view else None
        if record is None or record['record_type']!='s3.owner_receipt' or record['payload']['decision']!='permitted':
            raise ExecutionError('s3.owner_decision_unestablished')
    for owner,result,context in entries:
        checked=owner.check(result.value.grant,binding,boundary,context)
        if checked.state!='completed' or checked.value.decision!='permitted':raise ExecutionError('s3.owner_group_not_current')
    return tuple(result.value.grant for owner,result,context in entries)

@dataclass(frozen=True,slots=True)
class BoundaryEntry:
    binding:api.ResolvedOperationBinding
    resolver:object
    effect:api.EffectBoundary
    owner_evidence:tuple

class DriverBoundary:
    """Common guarded forwarding, reused by supplied native mechanics.

    The configured actual owners and journal are supplied services, not names
    from a manifest. This gate controls one local forwarding opportunity; actual
    receiver idempotency/fencing/isolation still require their own mechanisms.
    """
    def __init__(self,journal,journal_context,owners):
        if not owners:raise ExecutionError('s3.required_owner_set_unestablished')
        self.journal=journal;self.journal_context=journal_context;self.owners=tuple(owners)

    def enter(self,request,context,grants,issue_token,descriptor,receiver,channel):
        from . import codec
        from .imports import _exact_request
        from .journal import binding_digest,resolve_binding
        from .registry import _verify_implementation
        from .schema import operation
        if not isinstance(context,api.RuntimeContext) or not isinstance(issue_token,api.IssueToken):
            raise ExecutionError('s3.live_driver_boundary_required')
        row=operation(descriptor.operation)
        if row is None or row['pure'] or not row['port'].startswith('Driver.'):
            raise ExecutionError('s3.effect_driver_operation_required')
        actual,_=_exact_request(request,context.read,descriptor.operation['name'])
        expected=binding_digest(actual)
        if not isinstance(request.descriptor,api.ExactDriverDescriptor) or request.descriptor.operation!=descriptor.operation or request.descriptor.component!=descriptor.component or request.descriptor.method is not descriptor.method:
            raise ExecutionError('s3.exact_runtime_driver_binding_required')
        if request.descriptor.input_contract!=descriptor.input_contract or request.descriptor.output_contract!=descriptor.output_contract or request.descriptor.guarantees!=descriptor.guarantees:
            raise ExecutionError('s3.runtime_driver_declaration_mismatch')
        _verify_implementation(descriptor.implementation)
        if request.descriptor.implementation.reference!=descriptor.implementation.reference or request.descriptor.implementation.content_digest!=descriptor.implementation.content_digest or request.descriptor.implementation.selector!=descriptor.implementation.selector or request.descriptor.implementation.source_view.source_bytes!=descriptor.implementation.source_view.source_bytes:
            raise ExecutionError('s3.runtime_driver_implementation_mismatch')
        if issue_token.binding_digest!=expected or issue_token.command!=request.command:
            raise ExecutionError('s3.issue_request_binding_mismatch')
        source=request.source_view
        if source.package_id!=actual.context['package_id'] or source.digest!=next(v.digest for v in actual.inputs.source_views if v.package_id==source.package_id):
            raise ExecutionError('s3.request_source_view_mismatch')
        resolver=codec.Resolver((*context.read.views,*actual.inputs.source_views,issue_token.intent_commit.head.snapshot),limits=context.read.limits)
        head=issue_token.intent_commit.head
        command,pid=resolver.record(request.command,head.snapshot.package_id)
        if command['record_type']!='s3.effect_command' or command['payload']['operation']!=descriptor.operation or command['payload']['account']['target']!=head.account['target']:
            raise ExecutionError('s3.effect_command_scope_mismatch')
        bound=resolve_binding(command['payload']['binding'],pid,resolver)
        if binding_digest(bound)!=expected:raise ExecutionError('s3.command_binding_mismatch')
        component,component_pid=resolver.record(descriptor.component,source.package_id)
        declared=[resolver.record(ref,pid)[0] for ref in command['payload']['dependencies']['members']]
        if component['record_type'] not in ('s1.component','s3.component') or not any(canonical(r)==canonical(component) for r in declared):
            raise ExecutionError('s3.command_driver_dependency_unestablished')
        implementation=component['payload']['implementation']
        if implementation['state']!='known':raise ExecutionError('s3.driver_implementation_unestablished')
        artifact,_=resolver.record(implementation['value']['artifact'],component_pid)
        expected_artifact,_=resolver.record(descriptor.implementation.reference,descriptor.implementation.source_view.package_id)
        if canonical(artifact)!=canonical(expected_artifact) or implementation['value']['selector']!=descriptor.implementation.selector:
            raise ExecutionError('s3.driver_component_implementation_mismatch')
        transmission,transmission_pid=resolver.record(issue_token.transmission,head.snapshot.package_id)
        if transmission['record_type']!='s3.transmission' or transmission['payload']['command']['target']!=command['id']:
            raise ExecutionError('s3.transmission_scope_mismatch')
        if transmission['payload']['channel']!=channel:raise ExecutionError('s3.transmission_channel_mismatch')
        expected_receiver,_=resolver.record(receiver,source.package_id)
        recorded_receiver,_=resolver.record(transmission['payload']['recipient'],transmission_pid)
        if canonical(recorded_receiver)!=canonical(expected_receiver):raise ExecutionError('s3.transmission_receiver_mismatch')
        if len(grants)!=len(self.owners):raise ExecutionError('s3.owner_group_incomplete')
        evidence=[]
        for (owner,owner_context),grant in zip(self.owners,grants):
            checked=owner.check(grant,actual,descriptor.operation,owner_context)
            if checked.state!='completed' or not isinstance(checked.value,api.ValidityReceipt) or checked.value.decision!='permitted' or checked.value.binding_digest!=expected:
                raise ExecutionError('s3.owner_group_not_current')
            evidence.append(checked.value.evidence)
        # No callback/transfer is invoked before the actual issuer consumes it.
        # A crash after consumption conservatively leaves possible effects.
        self.journal.consume(issue_token,self.journal_context)
        return BoundaryEntry(actual,resolver,api.EffectBoundary(request.command,'may_have_crossed',
            unknown('s3.receiver_acceptance_unestablished'),(),issue_token.transmission),tuple(evidence))
