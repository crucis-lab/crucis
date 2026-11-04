"""Pure fixed-candidate selection and durable pre-send choices (DLV-08/09).

Acquisition/computation are separate effects. Availability and exact correlation
are checked here; neither establishes scientific truth or delivery authority.
"""
import copy
from . import api, codec
from .coordinator import frozen, read_with, root_of
from .model import Builder, ExecutionError, canonical, contract, index, known, qualified, reference, scope
from .registry import _verify_implementation
from .schema import validate_value


def coordinates(ref, anchor):
    return qualified(ref, anchor)


def verify_input(entry, context):
    if not isinstance(entry, api.BoundInput): raise ExecutionError('s3.pinned_decision_input_required')
    resolver = codec.Resolver(context.views, limits=context.limits)
    actual, pid = resolver.record(entry.reference, entry.source_package)
    if pid != entry.source_package or resolver.view(pid).digest != entry.source_digest or canonical(actual) != canonical(entry.record):
        raise ExecutionError('s3.decision_input_pin_mismatch')
    return qualified(entry.reference, pid)


def candidate_spec(value):
    if not isinstance(value, dict) or set(value) != {'procedure','policy','bundle','fallback','entries'} or value['fallback'] != 'forbidden' or not isinstance(value['entries'], list) or not value['entries']:
        raise ExecutionError('s3.fixed_candidate_specification_required')
    validate_value(value['procedure'],'Contract');validate_value(value['policy'],'KnownRef(s1.policy)');validate_value(value['bundle'],'Contract')
    actions=set()
    for item in value['entries']:
        if not isinstance(item,dict) or set(item) != {'action','response','required','context','domain','permitted_states'}:
            raise ExecutionError('s3.fixed_candidate_entry_shape')
        for name,expr in [('action','KnownRef(s1.action_request)'),('response','K(KnownRef(s1.action_response))'),
            ('required','KnownRef[]'),('context','KnownRef(s1.artifact_snapshot)'),('domain','K(KnownRef(s1.domain))')]:
            validate_value(item[name],expr)
        if item['action']['binding'] != 'external' or item['action']['target'] in actions or item['permitted_states'] not in (['returned'],['abstained']):
            raise ExecutionError('s3.fixed_candidate_identity_or_state')
        actions.add(item['action']['target'])
    return copy.deepcopy(value)


class FixedCandidates:
    """One explicitly configured pure procedure; no default oracle or fallback."""
    def __init__(self, component, implementation, specification, procedure):
        _verify_implementation(implementation);_verify_implementation(specification)
        validate_value(component,'KnownRef(component)');validate_value(procedure,'Contract')
        self.component,self.implementation,self.specification,self.procedure=copy.deepcopy(component),implementation,specification,copy.deepcopy(procedure)

    def describe(self, context):
        return api.DecisionDeclaration(self.component,self.procedure,contract('s3.fixed_candidate_inputs'),contract('s3.fixed_candidate_selection'),
            contract('s3.fixed_candidate_sources'),{'state':'not_applicable','rule':contract('s3.fallback_forbidden'),'scope':[]},self.implementation)

    def install(self, registry): registry.decisions.register(self.describe(registry),self)

    def _spec(self, context):
        _verify_implementation(self.specification)
        resolver=codec.Resolver(context.views,limits=context.limits)
        artifact,pid=resolver.record(self.specification.reference,self.specification.source_view.package_id)
        from crucis_causal.connections.validation import content_bytes
        raw=content_bytes(artifact['payload']['content'])
        from .model import digest
        if digest(raw)!=self.specification.content_digest:raise ExecutionError('s3.fixed_specification_changed')
        value=candidate_spec(codec.loads(raw,context.limits))
        if value['procedure']!=self.procedure:raise ExecutionError('s3.fixed_procedure_mismatch')
        for item in value['entries']:
            for ref in [item['action'],item['context'],*item['required']]:resolver.record(ref,pid)
            if item['response']['state']=='known':resolver.record(item['response']['value'],pid)
        resolver.record(value['policy'],pid)
        return value,resolver

    def _actions(self, actions, policy, context):
        if not isinstance(actions,tuple) or not actions:raise ExecutionError('s3.nonempty_action_occurrences_required')
        refs=tuple(verify_input(a,context) for a in actions);pref=verify_input(policy,context)
        if any(a.record['record_type']!='s1.action_request' for a in actions) or policy.record['record_type']!='s1.policy':
            raise ExecutionError('s3.fixed_action_policy_types')
        spec,resolver=self._spec(context)
        if pref!=spec['policy'] or policy.record['payload']['policy_contract']!=self.procedure:raise ExecutionError('s3.fixed_policy_mismatch')
        allowed={canonical(qualified(r,policy.source_package)) for r in policy.record['payload']['scope']['subjects']}
        if len(set(map(canonical,refs)))!=len(refs) or any(canonical(r) not in allowed for r in refs):raise ExecutionError('s3.fixed_policy_action_scope')
        entries={e['action']['target']:e for e in spec['entries']}
        if any(r['target'] not in entries or entries[r['target']]['action']!=r for r in refs):raise ExecutionError('s3.fixed_action_not_configured')
        return refs,spec,resolver

    def requirements(self, actions, policy, context):
        try:
            refs,spec,resolver=self._actions(actions,policy,context)
            sources=[]
            for ref in refs:
                item=next(e for e in spec['entries'] if e['action']==ref);parameters=[policy]
                for source in [self.specification.reference,item['context'],*item['required']]:
                    record,pid=resolver.record(source,self.specification.source_view.package_id)
                    parameters.append(api.BoundInput('s3.role.required_information',qualified(source,pid),record,pid,resolver.view(pid).digest))
                sources.append(api.ClaimRequest(contract('s3.fixed_candidate_source'),scope(ref),api.PinnedInputs(tuple(parameters),tuple(context.views))))
            return api.CallResult('completed',api.InformationRequirements(actions,tuple(sources),policy,{'package_id':self.specification.source_view.package_id,'format':self.specification.source_view.format}))
        except ExecutionError as exc:return api.rejected(exc.code)

    def delivery_contract(self, context):return self._spec(context)[0]['bundle']

    def select(self, actions, policy, inputs, frontier, context):
        try:
            refs,spec,resolver=self._actions(actions,policy,context)
            if not isinstance(inputs,api.PinnedInputs):raise ExecutionError('s3.pinned_decision_information_required')
            given={canonical(verify_input(e,context)) for e in inputs.entries}
            if canonical(self.specification.reference) not in given:raise ExecutionError('s3.fixed_specification_not_supplied')
            view=next((v for v in context.views if v.package_id==frontier.get('package_id')),None)
            if view is None:raise ExecutionError('s3.decision_frontier_unavailable')
            f,pid=resolver.record(frontier,view.package_id)
            if f['record_type']!='s3.frontier' or f['payload']['local_records']['extent']!='complete_for_scope':raise ExecutionError('s3.decision_frontier_coverage_unestablished')
            permitted={canonical(qualified(r,pid)) for r in f['payload']['local_records']['members']}
            needed=[self.specification.reference,*refs,qualified(policy.reference,policy.source_package)]
            selected=[];issues=[]
            for action in actions:
                item=next(e for e in spec['entries'] if e['action']['target']==action.record['id'])
                args=[qualified(r,action.source_package) for r in action.record['payload']['arguments']]
                if item['context'] not in args:raise ExecutionError('s3.decision_action_context_mismatch')
                if item['domain']['state']=='known' and item['domain']['value'] not in args:raise ExecutionError('s3.decision_action_domain_mismatch')
                if item['domain']['state']=='unresolved':raise ExecutionError('s3.decision_domain_unestablished')
                needed.append(item['context']);needed.extend(item['required'])
                missing=[]
                from crucis_causal.connections.validation import content_bytes
                for ref in item['required']:
                    record,_=resolver.record(ref,self.specification.source_view.package_id)
                    if canonical(ref) not in given or record['record_type']!='s1.artifact_snapshot':
                        missing.append(ref);continue
                    try:content_bytes(record['payload']['content'])
                    except (ValueError,OSError):missing.append(ref)
                if missing or item['response']['state']!='known':
                    issues.append(api.Issue('s3.required_response_source_unavailable',scope(item['action']),tuple(missing)))
                    continue
                response=item['response']['value'];record,rpid=resolver.record(response,self.specification.source_view.package_id)
                if qualified(record['payload']['request'],rpid)!=item['action'] or record['payload']['response_state'] not in item['permitted_states']:
                    raise ExecutionError('s3.fixed_response_correlation_or_state')
                needed.append(response);selected.append(response)
            if any(canonical(r) not in permitted for r in needed):raise ExecutionError('s3.decision_information_outside_frontier')
            if issues:
                value=api.DecisionResult(refs,index(extent='unresolved'),frontier,self.procedure,tuple(issues))
                return api.CallResult('partial',value,issues=tuple(issues))
            return api.CallResult('completed',api.DecisionResult(refs,index(selected),frontier,self.procedure,()))
        except ExecutionError as exc:return api.rejected(exc.code)

    def replay(self, decision, context):
        """Recompute from the frozen basis, never from later ambient material."""
        try:
            verify_input(decision,context)
            if decision.record['record_type']!='s3.action_decision':raise ExecutionError('s3.action_decision_required')
            resolver=codec.Resolver(context.views,limits=context.limits);p=decision.record['payload']
            spec,_=self._spec(context)
            def bound(ref,anchor,role):
                record,pid=resolver.record(ref,anchor)
                return api.BoundInput(role,qualified(ref,pid),record,pid,resolver.view(pid).digest)
            actions=tuple(bound(r,decision.source_package,'s3.role.actions') for r in p['actions']['members'])
            policy=bound(spec['policy'],self.specification.source_view.package_id,'s3.role.policy')
            information=api.PinnedInputs(tuple(bound(r,decision.source_package,'s3.role.information') for r in p['information']['members']),tuple(context.views))
            result=self.select(actions,policy,information,qualified(p['frontier'],decision.source_package),context)
            selected=[qualified(r,decision.source_package) for r in p['selected']['members']]
            if result.state!='completed' or result.value.selected['members']!=selected or p['rule']!=self.procedure:
                raise ExecutionError('s3.frozen_decision_not_reproduced')
            return result
        except ExecutionError as exc:return api.rejected(exc.code)


def persist_selection(result, information, policy, journal, head, context, occurrence):
    """Freeze a nonempty selected choice once, before any delivery effect."""
    try:
        validate_value(occurrence,'ID')
        if not isinstance(result,api.DecisionResult) or result.issues or not result.selected['members'] or result.selected['extent']!='complete_for_scope':
            raise ExecutionError('s3.held_choice_cannot_be_delivered')
        resolver=codec.Resolver(context.read.views,limits=context.read.limits)
        for ref in (*result.actions,*result.selected['members']):resolver.record(ref,ref['package_id'])
        def possible_occurrences(refs,anchor):
            keys=set()
            for ref in refs:
                action,pid=resolver.record(ref,ref['package_id'] if ref['binding']=='external' else anchor)
                native=action['payload']['native_action_identity']
                if native['state']=='known':
                    n=native['value'];keys.add(canonical([n['authority'],n['namespace'],n['native_id']]))
            return keys
        possible=possible_occurrences(result.actions,result.actions[0]['package_id'])
        payload={'actions':index(result.actions),'rule':result.rule,'information':index([qualified(e.reference,e.source_package) for e in information.entries]),
            'frontier':result.input_frontier,'selected':result.selected,'assessment':{'state':'unresolved','reasons':['s3.selection_is_not_scientific_truth'],'evidence':[]}}
        for old in head.snapshot.records:
            if old['record_type']!='s3.action_decision':continue
            old_actions={r['target'] for r in old['payload']['actions']['members']}
            same_native=possible & possible_occurrences(old['payload']['actions']['members'],head.snapshot.package_id)
            if old_actions & {r['target'] for r in result.actions} or same_native:
                if canonical(old['payload'])!=canonical(payload):raise ExecutionError('s3.action_choice_already_frozen')
                return api.CallResult('completed',reference(old['id'],'action_decision',head.snapshot.package_id))
        b=Builder('Pre-send frozen response selection')
        selected=b.add('action_decision',payload,record_id=occurrence)
        root=root_of(head.snapshot,resolver)
        projection=b.add('projection_view',{'view_role':'audience_projection','audience':qualified(root['audience'],head.snapshot.package_id),
            'projection_contract':contract('s3.pre_send_selection'),'members':index([selected]),'claims':index(),'limits':index()})
        view=frozen(b,projection,context.read)
        committed=journal.append(head.account,head.revision,occurrence,api.CommitDelta(view.records,(),(*context.read.views,view)),context)
        if committed.state!='completed':return committed
        return api.CallResult('completed',qualified(selected,view.package_id),records=api.RecordDelta(view.records,(),(*context.read.views,view,committed.value.head.snapshot)))
    except ExecutionError as exc:return api.rejected(exc.code)
