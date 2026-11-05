"""Pure, explicitly supplied recovery policies and scoped continuation (DLV-08/09).

A plan is advice from frozen evidence, never a grant, retry or provider call.
Unknown-origin work remains unprojected; scientific continuations reuse the
predecessor's verified trial, not a fabricated successor handoff.
"""
import copy
from dataclasses import dataclass
import inspect
from . import api, codec
from .model import ExecutionError, canonical, contract, qualified, scope
from .registry import callable_value, key, _verify_implementation
from .schema import validate_binding, validate_value


@dataclass(frozen=True, slots=True)
class RecoveryRule:
    policy: dict
    implementation: api.PinnedArtifactIdentity
    evaluate: api.SuppliedCallable


def copied_pin(pin):
    """Copy metadata while preserving the actual supplied read capability."""
    _verify_implementation(pin)
    view=pin.source_view
    return api.PinnedArtifactIdentity(copy.deepcopy(pin.reference),copy.deepcopy(pin.content_digest),copy.deepcopy(pin.selector),
        api.PinnedView(view.package_id,copy.deepcopy(view.format),copy.deepcopy(view.digest),view.source_bytes,view.read_scope))


class RecoveryPolicies:
    def __init__(self, rules=()):
        self._rules = {}
        for rule in rules:
            if not isinstance(rule, RecoveryRule): raise ExecutionError('s3.supplied_recovery_rule_required')
            validate_value(rule.policy, 'Contract'); _verify_implementation(rule.implementation)
            if list(inspect.signature(callable_value(rule.evaluate)).parameters) != ['view','goal','context']:
                raise ExecutionError('s3.recovery_policy_signature')
            selected = key(rule.policy)
            if selected in self._rules: raise ExecutionError('s3.duplicate_recovery_policy')
            self._rules[selected] = RecoveryRule(copy.deepcopy(rule.policy),copied_pin(rule.implementation),rule.evaluate)

    def plan(self, view, goal, context):
        try:
            if not isinstance(goal, api.RecoveryGoal) or goal.kind not in ('wait','reconcile','reconnect','retransmit','restart','stop','close'):
                raise ExecutionError('s3.exact_recovery_goal_required')
            validate_value(goal.scope, 'Scope'); validate_value(goal.policy, 'Contract')
            resolver = codec.Resolver(context.views, limits=context.limits)
            if not context.access.permits(view.package_id): raise ExecutionError('s3.read_denied')
            resolver.closure(view.package_id)
            root,rpid=resolver.record(view.package['roots'][0],view.package_id)
            declared=root['payload'].get('obligations',root['payload'].get('members',{'members':[]}))['members']
            retained=[]
            for ref in declared:
                if ref['target_type']!='s3.obligation' or ref.get('binding')=='unresolved':continue
                record,pid=resolver.record(ref,rpid)
                if record['payload']['disposition'] in ('pending','unresolved','handed_off'):retained.append(qualified(ref,pid))
            rule = self._rules.get(key(goal.policy))
            if rule is None:
                issue = api.Issue('s3.recovery_policy_unavailable', goal.scope, ())
                return api.CallResult('partial', api.RecoveryPlan(goal, (), (issue,), tuple(retained)), issues=(issue,))
            _verify_implementation(rule.implementation)
            result = callable_value(rule.evaluate)(view, copy.deepcopy(goal), context)
            if not isinstance(result, api.RecoveryPlan) or result.goal != goal or not isinstance(result.operations, tuple) or not isinstance(result.obligations, tuple):
                raise ExecutionError('s3.recovery_plan_contract')
            for request in result.operations:
                if not isinstance(request, api.OperationRequest): raise ExecutionError('s3.recovery_operation_required')
                validate_binding({'operation': request.operation, 'roles': list(request.roles), 'parameters': list(request.parameters)}, admission=True)
            for ref in result.obligations:
                record, _ = resolver.record(ref, view.package_id)
                if record['record_type'] != 's3.obligation': raise ExecutionError('s3.recovery_obligation_required')
            if not {r['target'] for r in retained}<={r['target'] for r in result.obligations}:raise ExecutionError('s3.recovery_omits_unresolved_obligations')
            if any(not isinstance(i, api.Issue) for i in result.held_requirements): raise ExecutionError('s3.recovery_issue_required')
            if result.held_requirements:
                return api.CallResult('partial', result, issues=result.held_requirements)
            return api.CallResult('completed', result)
        except ExecutionError as exc: return api.rejected(exc.code)


def require_continuation(binding, resolver, policies):
    """Exact same-request scientific continuation; other relations hold explicitly.

    Driver mechanics must additionally establish state availability, overlap and
    current loader/receiver validity before the one-use native boundary.
    """
    from .scientific import match_run, require_recovery_intent
    from .model import reference
    if binding.record['payload']['operation'] != contract('s3.op.native_restart'):
        raise ExecutionError('s3.restart_binding_required')
    roles = {r['role']:r['members']['members'] for r in binding.record['payload']['roles']}
    params = {p['key']:p['value'] for p in binding.record['payload']['parameters']}
    pid = binding.context['package_id']
    def one(role, kind):
        refs = roles['s3.role.'+role]
        if len(refs) != 1: raise ExecutionError('s3.restart_identity_unestablished')
        record, anchor = resolver.record(refs[0], pid)
        if record['record_type'] != kind: raise ExecutionError('s3.restart_identity_unestablished')
        return qualified(refs[0], anchor), record, anchor
    request, req, qpid = one('request','s1.request')
    predecessor, old, apid = one('predecessor','s1.attempt')
    successor, new, npid = one('successor','s1.attempt')
    if old['id'] == new['id']: raise ExecutionError('s3.distinct_successor_required')
    if params['request_relation']['state']!='known' or params['request_relation']['value']!='same_request':
        # Do not infer a scientific new-request relation without a supported S2
        # projection for that relation and the original trial.
        raise ExecutionError('s3.new_request_recovery_unqualified')
    for attempt, anchor in [(old,apid),(new,npid)]:
        actual, actual_pid = resolver.record(attempt['payload']['request'], anchor)
        if actual_pid != qpid or canonical(actual) != canonical(req): raise ExecutionError('s3.recovery_request_mismatch')
    policy, policy_record, ppid = one('policy','s1.policy')
    expected = req['payload']['recovery_policy']
    if expected['state'] != 'known': raise ExecutionError('s3.scientific_recovery_policy_unestablished')
    original_policy, original_pid = resolver.record(expected['value'], qpid)
    if original_pid != ppid or canonical(original_policy) != canonical(policy_record): raise ExecutionError('s3.recovery_policy_mismatch')
    run, run_record, rpid = one('scientific_binding','s2.run_binding')
    handoffs = [(r,v.package_id) for v in binding.inputs.source_views for r in v.records
        if r['record_type']=='s2.request_binding_receipt' and r['payload']['run']['target']==run_record['id']
        and r['payload']['request']['target']==req['id'] and r['payload']['attempt']['target']==old['id']]
    if len(handoffs) != 1: raise ExecutionError('s3.scientific_handoff_unestablished')
    h,hpid = handoffs[0]
    match = match_run(run,request,predecessor,reference(h['id'],h['record_type'],hpid),resolver)
    require_recovery_intent(match,resolver,policy_record['payload']['policy_contract'],policies=policies)
    if params['purpose']['value'] != 'scientific_run' or params['mode']['value'] != 'checkpoint_continuation':
        raise ExecutionError('s3.scientific_recovery_mode_unestablished')
    if params['scientific_rule']['value']!=policy_record['payload']['policy_contract']:
        raise ExecutionError('s3.scientific_recovery_rule_unestablished')
    return match


def require_scientific_restore(binding,resolver,policies):
    """A2's checkpoint and fixed S2 mode must agree before in-place loading."""
    from .scientific import match_run,require_recovery_intent
    from .model import reference
    pid=binding.context['package_id']
    roles={r['role']:r['members']['members'] for r in binding.record['payload']['roles']}
    subject,spid=resolver.record(roles['s3.role.subject'][0],pid)
    successor_ref=subject['payload']['origin_attempt']
    if successor_ref.get('binding')=='unresolved':raise ExecutionError('s3.scientific_restore_origin_unestablished')
    successor,apid=resolver.record(successor_ref,spid)
    request,qpid=resolver.record(successor['payload']['request'],apid)
    request_ref=reference(request['id'],'s1.request',qpid)
    candidates={}
    for view in binding.inputs.source_views:
        for record in view.records:
            if record['record_type']=='s2.request_binding_receipt' and record['payload']['request']['target']==request['id']:
                candidates.setdefault(record['id'],(record,view.package_id))
    if len(candidates)!=1:raise ExecutionError('s3.scientific_restore_handoff_unestablished')
    receipt,hpid=next(iter(candidates.values()));r=receipt['payload']
    run=qualified(r['run'],hpid);predecessor=qualified(r['attempt'],hpid)
    if predecessor['target']==successor['id']:raise ExecutionError('s3.distinct_successor_required')
    match=match_run(run,request_ref,predecessor,reference(receipt['id'],receipt['record_type'],hpid),resolver)
    policy,ppid=resolver.record(roles['s3.role.policy'][0],pid)
    expected=request['payload']['recovery_policy']
    if expected['state']!='known':raise ExecutionError('s3.scientific_recovery_policy_unestablished')
    original,opid=resolver.record(expected['value'],qpid)
    if canonical(original)!=canonical(policy) or opid!=ppid:raise ExecutionError('s3.recovery_policy_mismatch')
    require_recovery_intent(match,resolver,policy['payload']['policy_contract'],policies=policies)
    initial=successor['payload']['initial_state']
    if initial['state']!='known':raise ExecutionError('s3.scientific_restore_checkpoint_unestablished')
    planned,cpid=resolver.record(roles['s3.role.checkpoint'][0],pid)
    actual,ipid=resolver.record(initial['value'],apid)
    if canonical(planned)!=canonical(actual) or cpid!=ipid:raise ExecutionError('s3.scientific_restore_checkpoint_mismatch')
    return match


def visible_scientific_followup(binding,view,resolver):
    """Visible scoped intent cannot be waived by calling later actions probes."""
    from .coordinator import root_of
    root=root_of(view,resolver);account,apid=resolver.record(root['account'],view.package_id)
    target,tpid=resolver.record(account['payload']['target'],apid)
    if account['payload']['purpose']=='execute' and target['payload']['definition']==contract('s3.scientific_execution'):return True
    # Target labels are extensible. Existing scientific command intent in the
    # same account cannot be hidden behind another target definition string.
    seen=set()
    for source in binding.inputs.source_views:
        for record in source.records:
            if record['id'] in seen or record['record_type']!='s3.effect_command':continue
            seen.add(record['id'])
            if record['payload']['account']['target']!=account['id'] or record['payload']['operation']!=contract('s3.op.launch'):continue
            planned,ppid=resolver.record(record['payload']['binding'],source.package_id)
            values={p['key']:p['value'] for p in planned['payload']['parameters']}
            scientific=[r for r in planned['payload']['roles'] if r['role']=='s3.role.scientific_binding']
            if values.get('purpose',{}).get('value')=='scientific_run' or any(r['members']['members'] for r in scientific):return True
    requests=[]
    def attempt(ref,anchor):
        if ref.get('binding')=='unresolved':return
        record,pid=resolver.record(ref,anchor)
        if record['record_type']=='s1.attempt':requests.append((record['payload']['request'],pid))
    for entry in binding.inputs.entries:
        p=entry.record['payload'];kind=entry.record['record_type'];pid=entry.source_package
        if kind=='s1.attempt':attempt(qualified(entry.reference,pid),pid)
        elif kind=='s3.native_subject':attempt(p['origin_attempt'],pid)
        elif kind=='s1.action_request':attempt(p['attempt'],pid)
        elif kind=='s1.action_response':
            action,anchor=resolver.record(p['request'],pid);attempt(action['payload']['attempt'],anchor)
        elif kind=='s1.session' and p['request'].get('binding')!='unresolved':requests.append((p['request'],pid))
    for ref,anchor in requests:
        req,qpid=resolver.record(ref,anchor)
        if any(r['record_type']=='s1.relation' and r['payload']['relation_contract']['name']=='s2.request_projection_metadata' and
               any(e['target']['target']==req['id'] for e in r['payload']['endpoints']) for r in resolver.view(qpid).records):return True
    return False
