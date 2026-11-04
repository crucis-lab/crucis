"""Exact audience closure for supplied immutable evidence (DLV-08/09).

Policy code and readable bytes are explicit inputs. An audience label alone is
never permission, and opaque-byte permission is never interpreted-content proof.
"""
from dataclasses import dataclass
import copy
import inspect
from . import api,codec
from .model import ExecutionError,canonical,contract,digest,qualified,reference,walk
from .registry import callable_value,key,_verify_implementation
from .schema import validate_value
from .recovery import copied_pin


@dataclass(frozen=True,slots=True)
class AudienceRule:
    policy: dict
    implementation: api.PinnedArtifactIdentity
    evaluate: api.SuppliedCallable


class AudiencePolicies:
    def __init__(self,rules=()):
        self._rules={}
        for rule in rules:
            if not isinstance(rule,AudienceRule):raise ExecutionError('s3.supplied_audience_rule_required')
            validate_value(rule.policy,'Contract');_verify_implementation(rule.implementation)
            if list(inspect.signature(callable_value(rule.evaluate)).parameters)!=['view','audience','claims','context']:raise ExecutionError('s3.audience_rule_signature')
            selected=key(rule.policy)
            if selected in self._rules:raise ExecutionError('s3.duplicate_audience_rule')
            self._rules[selected]=AudienceRule(copy.deepcopy(rule.policy),copied_pin(rule.implementation),rule.evaluate)

    def freeze(self,view,audience,claims,context):
        try:
            resolver=codec.Resolver(context.views,limits=context.limits)
            if any(not context.access.permits(v.package_id) for v in context.views):raise ExecutionError('s3.read_denied')
            actual=resolver.view(view.package_id)
            if actual.source_bytes!=view.source_bytes:raise ExecutionError('s3.package_identity_conflict')
            closure=resolver.closure(view.package_id)
            record,apid=resolver.record(audience,audience.get('package_id',view.package_id))
            if record['record_type']!='s3.audience':raise ExecutionError('s3.exact_audience_required')
            policy_ref=record['payload']['disclosure_policy'];policy,ppid=resolver.record(policy_ref,apid)
            if policy['record_type']!='s1.policy':raise ExecutionError('s3.audience_policy_uninterpreted')
            rule=self._rules.get(key(policy['payload']['policy_contract']))
            if rule is None:raise ExecutionError('s3.audience_policy_unavailable')
            _verify_implementation(rule.implementation)
            result=callable_value(rule.evaluate)(view,qualified(audience,apid),claims,context)
            if not isinstance(result,api.CallResult) or not isinstance(result.value,api.AudienceClosure):raise ExecutionError('s3.audience_closure_contract')
            allowed=result.value
            if allowed.audience!=qualified(audience,apid) or allowed.policy!=rule.policy:raise ExecutionError('s3.audience_policy_binding_mismatch')
            validate_audience(view,allowed,resolver,context.registry.payloads)
            withheld=result.issues if result.state!='completed' else ()
            if claims and any(r['record_type']=='s3.typed_payload' and not context.registry.payloads.supports(r['payload']['payload_contract']) for v in closure for r in v.records):
                withheld=(*withheld,api.Issue('s3.opaque_content_assurance_unestablished',{'subjects':[qualified(audience,apid)],'qualifiers':[]},()))
            draft=api.PackageDraft(view.package_id,view.format,view.source_bytes,view.digest,allowed,withheld)
            return api.CallResult('partial' if withheld else 'completed',draft,issues=withheld)
        except ExecutionError as exc:return api.rejected(exc.code)


def validate_audience(view,audience,resolver,payloads):
    if not isinstance(audience,api.AudienceClosure):raise ExecutionError('s3.actual_audience_closure_required')
    closure=resolver.closure(view.package_id)
    root,rpid=resolver.record(view.package['roots'][0],view.package_id)
    actual,_=resolver.record(root['payload']['audience'],rpid)
    selected,_=resolver.record(audience.audience,audience.audience.get('package_id',view.package_id))
    if canonical(actual)!=canonical(selected):raise ExecutionError('s3.audience_projection_required')
    permissions={}
    for ref in audience.allowed_records:
        record,pid=resolver.record(ref,view.package_id)
        permissions[(pid,record['id'])]=canonical(record)
    deps={v.package_id:v for v in audience.allowed_dependencies}
    required_deps={v.package_id for v in closure if v.package_id!=view.package_id}
    if set(deps)!=required_deps or len(deps)!=len(audience.allowed_dependencies):raise ExecutionError('s3.audience_dependency_not_allowed')
    required_records={(v.package_id,r['id']) for v in closure for r in v.records}
    if set(permissions)!=required_records or len(permissions)!=len(audience.allowed_records):raise ExecutionError('s3.audience_record_not_allowed')
    for dependency in closure:
        if dependency.package_id!=view.package_id:
            allowed=deps.get(dependency.package_id)
            if allowed is None or allowed.source_bytes!=dependency.source_bytes or allowed.digest!=dependency.digest:raise ExecutionError('s3.audience_dependency_not_allowed')
        for record in dependency.records:
            if permissions.get((dependency.package_id,record['id']))!=canonical(record):raise ExecutionError('s3.audience_record_not_allowed')
            # This includes record producers, diagnostics and provenance, not
            # merely the root's nominal members. Resolver closure checks pins.
            if record['record_type']=='s3.typed_payload':
                selected=record['payload']['payload_contract']
                if payloads.supports(selected):
                    resolver.payload(reference(record['id'],'typed_payload',dependency.package_id),dependency.package_id,payloads)
                else:
                    # Exact opaque bytes are allowed only when their owning
                    # record AND artifact/dependency bytes are in the closure.
                    # Any stronger claim is withheld by the supplied rule.
                    artifact,_=resolver.record(record['payload']['content']['artifact'],dependency.package_id)
                    if artifact['record_type']!='s1.artifact_snapshot':raise ExecutionError('s3.opaque_payload_bytes_unavailable')
    return audience


def exact_native_projection(raw,expected_digest,permission,*,audience):
    """Preserve an already authorized native artifact exactly; add no S3 root.

    The supplied pure permission function establishes only this byte audience.
    It cannot confer grant/control authority or authorize additional metadata.
    """
    if not isinstance(raw,bytes) or digest(raw)!=expected_digest:raise ExecutionError('s3.native_projection_integrity')
    if not callable(permission) or permission(raw,audience) is not True:raise ExecutionError('s3.native_bytes_audience_unestablished')
    return raw
