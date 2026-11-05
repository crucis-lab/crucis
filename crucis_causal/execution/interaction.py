"""Common action/response/bundle checks and evidence projection (DLV-08/09).

Native mechanics still establish actual acceptance, current action validity and
bundle atomicity. No transport result implies native use or scientific truth.
"""
from dataclasses import dataclass
from . import api, codec
from .coordinator import frozen, root_of
from .decisions import verify_input
from .model import Builder, ExecutionError, canonical, contract, index, qualified, reference, scope, unknown


@dataclass(frozen=True, slots=True)
class DeliverySelection:
    decision: api.BoundInput
    actions: tuple
    responses: tuple
    endpoint: api.BoundInput
    correlation: dict
    validity: dict


def validate_delivery(binding, inputs, context):
    """Pure exact validation including replay of the original selection basis."""
    roles={}
    for entry in inputs.entries:
        verify_input(entry,context);roles.setdefault(entry.role,[]).append(entry)
    decision=roles['s3.role.decision'][0];actions=tuple(roles['s3.role.actions']);responses=tuple(roles['s3.role.responses']);endpoint=roles['s3.role.endpoint'][0]
    if not actions or len(actions)!=len(responses):raise ExecutionError('s3.delivery_action_response_cardinality')
    if decision.record['record_type']!='s3.action_decision' or endpoint.record['record_type']!='s1.endpoint':raise ExecutionError('s3.delivery_input_types')
    p=decision.record['payload']
    declaration,procedure=context.registry.decisions.lookup(p['rule'])
    if not callable(getattr(procedure,'replay',None)):raise ExecutionError('s3.decision_revalidation_unavailable')
    replay=procedure.replay(decision,context)
    if replay.state!='completed':raise ExecutionError(replay.issues[0].code)
    arefs=[qualified(e.reference,e.source_package) for e in actions];rrefs=[qualified(e.reference,e.source_package) for e in responses]
    selected=[qualified(r,decision.source_package) for r in p['selected']['members']]
    expected_actions=[qualified(r,decision.source_package) for r in p['actions']['members']]
    if arefs!=expected_actions or rrefs!=selected or p['selected']['extent']!='complete_for_scope':raise ExecutionError('s3.delivery_differs_from_frozen_selection')
    if len({canonical(r) for r in arefs})!=len(arefs):raise ExecutionError('s3.duplicate_action_occurrence')
    endpoint_ref=qualified(endpoint.reference,endpoint.source_package)
    for action,response in zip(actions,responses):
        if action.record['record_type']!='s1.action_request' or response.record['record_type']!='s1.action_response':raise ExecutionError('s3.delivery_input_types')
        if qualified(response.record['payload']['request'],response.source_package)!=qualified(action.reference,action.source_package) or qualified(action.record['payload']['endpoint'],action.source_package)!=endpoint_ref:
            raise ExecutionError('s3.delivery_correlation_mismatch')
    resolver=codec.Resolver(context.views,limits=context.limits);params={p['key']:p['value'] for p in binding.record['payload']['parameters']};pid=binding.context['package_id']
    correlation=resolver.payload(params['correlation']['value'],pid,context.registry.payloads)
    if correlation['contract']!=params['bundle']['value']:raise ExecutionError('s3.delivery_bundle_contract_mismatch')
    if not callable(getattr(procedure,'delivery_contract',None)) or procedure.delivery_contract(context)!=params['bundle']['value']:
        raise ExecutionError('s3.delivery_differs_from_fixed_bundle_policy')
    expected=[{'action':a,'response':r,'endpoint':endpoint_ref} for a,r in zip(arefs,rrefs)]
    if correlation['entries']!=expected:raise ExecutionError('s3.delivery_bundle_correlation_mismatch')
    validity=resolver.payload(params['validity']['value'],pid,context.registry.payloads)
    if {canonical(r) for r in validity['scope']['subjects']}!={canonical(r) for r in arefs}:raise ExecutionError('s3.delivery_validity_scope_mismatch')
    return DeliverySelection(decision,actions,responses,endpoint,correlation,validity)


def delivery_evidence(request, selection, receipts, read, *, accepted, transmission, transmitted=None, policy_consumed=None,
                      transmission_policy=None, consumption_policy=None):
    """Project supplied observations; requested/delivered/used stay distinct."""
    b=Builder('Observed delivery evidence, not native use')
    params={p['key']:p['value'] for p in request.binding.record['payload']['parameters']}
    delivery=b.add('delivery',{'command':request.command,'decision':qualified(selection.decision.reference,selection.decision.source_package),
        'actions':index([qualified(a.reference,a.source_package) for a in selection.actions]),
        'responses':index([qualified(r.reference,r.source_package) for r in selection.responses]),
        'recipient':qualified(selection.endpoint.record['payload']['owner'],selection.endpoint.source_package),
        'validity':params['validity']['value'],'receipts':index(receipts,extent='partial_for_scope')})
    exposure=[]
    for facet,extent,policy in [('transmitted',transmitted,transmission_policy),('policy_consumed',policy_consumed,consumption_policy)]:
        if extent is None:continue
        from .schema import validate_value
        validate_value(policy,'Contract');validate_value(extent,'K(Number|KnownRef(typed_payload))')
        exposure.append(b.add('exposure_entry',{'scope':scope(request.command),'owner':selection.validity['owner'],
            'recipient':qualified(selection.endpoint.record['payload']['owner'],selection.endpoint.source_package),
            'information':index([qualified(r.reference,r.source_package) for r in selection.responses]),'facet':facet,'extent':extent,
            'policy':policy,'basis':list(receipts),'revises':[]}))
    root=root_of(request.source_view,codec.Resolver(read.views,limits=read.limits))
    projection=b.add('projection_view',{'view_role':'audience_projection','audience':qualified(root['audience'],request.source_view.package_id),
        'projection_contract':contract('s3.delivery_observation'),'members':index([delivery,*receipts,*exposure]),'claims':index(),'limits':index()})
    view=frozen(b,projection,read)
    evidence=api.DriverEvidence(reference(request.binding.record['id'],'operation_binding',request.binding.context['package_id']),
        api.RecordDelta(view.records,(),(*read.views,view)),index([qualified(delivery,view.package_id)]),index(receipts),index(),())
    return api.CallResult('completed',evidence,records=evidence.records,
        effects=(api.EffectBoundary(request.command,'crossed',accepted,tuple(receipts),transmission),))
