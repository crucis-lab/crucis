"""Scoped stop/state assessments and immutable collection closure (DLV-08/09)."""
from . import api, codec
from .coordinator import frozen, read_with
from .model import (Builder, ExecutionError, canonical, contract, identity, index,
    known, qualified, reference, scope, unknown)
from .schema import validate_binding, validate_value


def require_observed_stop(assessment, subject, resolver, *, procedure, question):
    record,pid = resolver.record(assessment,assessment.get('package_id'))
    p = record['payload']
    if record['record_type']!='s3.assessment' or p['question']!=question or p['procedure']!=procedure or p['result']['state']!='known' or p['result']['value'] is not True or p['conflicts_with']:
        raise ExecutionError('s3.observed_stop_unestablished')
    actual=[resolver.record(r,pid)[0] for r in p['scope']['subjects']]
    expected,_=resolver.record(subject,subject.get('package_id'))
    if len(actual)!=1 or canonical(actual[0])!=canonical(expected) or p['scope']['qualifiers'] or p['basis']['extent']!='complete_for_scope' or not p['basis']['members']:
        raise ExecutionError('s3.stop_scope_unestablished')
    # An explicit later conflict cannot silently be ignored as an earlier pass.
    for view in resolver._views.values():
        for other in view.records:
            if other['record_type']!='s3.assessment':continue
            if any(r['target']==record['id'] for r in other['payload']['conflicts_with']):raise ExecutionError('s3.stop_evidence_disputed')
    return qualified(assessment,pid)


def state_components(components,required,*,loaded=False):
    """Separate source identity, availability and load; no inferred RNG/history."""
    from .schema import validate_value
    if not isinstance(components,list) or len({canonical(c['component']) for c in components})!=len(components):
        raise ExecutionError('s3.unique_state_components_required')
    for item in components: validate_value(item,'StateComponent')
    selected={canonical(c['component']):c for c in components}
    for wanted in required:
        item=selected.get(canonical(wanted))
        if item is None or item['identity']['state']!='known' or item['restore_source']['state']!='known' or item['availability']['state']!='known' or item['availability']['value'] is not True:
            raise ExecutionError('s3.required_state_unavailable')
        if loaded and (item['loaded']['state']!='known' or item['loaded']['value'] is not True):raise ExecutionError('s3.required_state_load_unestablished')
    return tuple(selected[canonical(wanted)] for wanted in required)


def close_collection(request, account, journal, context, *, captured=None, basis=()):
    """Own journal action only. Never stops jobs, releases holds or resets quotas."""
    try:
        if not isinstance(request,api.OperationRequest) or request.operation!=contract('s3.op.close_collection'):
            raise ExecutionError('s3.close_collection_request_required')
        validate_value(request.request_occurrence,'ID')
        validate_binding({'operation':request.operation,'roles':list(request.roles),'parameters':list(request.parameters)},admission=True)
        roles={r['role']:r['members']['members'] for r in request.roles};p={p['key']:p['value']['value'] for p in request.parameters}
        read=context.read;resolver=codec.Resolver(read.views,limits=read.limits)
        for v in read.views:
            if not read.access.permits(v.package_id):raise ExecutionError('s3.read_denied')
        period=roles['s3.role.period'][0];frontier=roles['s3.role.frontier'][0];outstanding=roles['s3.role.obligations']
        for ref in [period,frontier,*outstanding,*basis]:resolver.record(ref,ref.get('package_id'))
        # Every unresolved obligation already in this account remains named. A
        # later discharged fact does not erase the earlier obligation/cutoff.
        head=journal.head(account,context)
        if head.state!='completed':return head
        pending={r['id'] for r in head.value.snapshot.records if r['record_type']=='s3.obligation' and r['payload']['disposition'] in ('pending','unresolved','handed_off')}
        if not pending<={r['target'] for r in outstanding}:raise ExecutionError('s3.closure_omits_unresolved_obligations')
        captured=index(extent='unresolved',gaps=[]) if captured is None else captured
        validate_value(captured,'IndexList(Ref)')
        payload={'period':period,'frontier':frontier,'stopping_rule':p['stopping_rule'],'reason':p['reason'],
            'captured':captured,'outstanding':index(outstanding),'basis':list(basis)}
        prior=[r for r in head.value.snapshot.records if r['id']==request.request_occurrence]
        if prior:
            if prior[0]['record_type']!='s3.collection_closure' or prior[0]['payload']!=payload:raise ExecutionError('s3.collection_closure_identity_conflict')
            return api.CallResult('completed',reference(prior[0]['id'],'collection_closure',head.value.snapshot.package_id),records=api.RecordDelta(dependencies=(*head.records.dependencies,head.value.snapshot)))
        b=Builder('Immutable closure of observation, not native termination')
        ref=b.add('collection_closure',payload,record_id=request.request_occurrence)
        from .coordinator import root_of
        r=root_of(head.value.snapshot,codec.Resolver((*read.views,*head.records.dependencies,head.value.snapshot),limits=read.limits))
        projection=b.add('projection_view',{'view_role':'audience_projection','audience':qualified(r['audience'],head.value.snapshot.package_id),
            'projection_contract':contract('s3.collection_closure_view'),'members':index([ref]),'claims':index(),'limits':index()})
        read=read_with(read,*head.records.dependencies,head.value.snapshot);view=frozen(b,projection,read)
        result=journal.append(account,p['expected_journal_revision'],request.request_occurrence,api.CommitDelta(view.records,(),(*read.views,view)),context)
        if result.state!='completed':return result
        return api.CallResult('completed',qualified(ref,view.package_id),records=api.RecordDelta(view.records,(),(*read.views,view,result.value.head.snapshot)))
    except ExecutionError as exc:return api.rejected(exc.code)
