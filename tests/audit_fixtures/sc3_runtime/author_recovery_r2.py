"""One-shot metadata authoring: a NEW checkpoint-condition revision (DLV-08/09).

The frozen B00 request says recovery/state policy NA. It stays an appropriate
held example. This addendum explicitly permits the accepted model/optimizer-only
fixture mode before any S3 native execution; no prior source/expected value is
edited and no model/optimizer/RNG/history load is claimed by metadata.
"""
import copy
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3];sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
from crucis_causal.connections import model as s1
from crucis_causal.connections.services import RecordBuffer,ContractRegistry,IdentityService
from crucis_causal.connections.codec import dumps as s1bytes
from crucis_causal.experiments import api,core
from crucis_causal.experiments.model import (qualified,reference,identity,index,known,unknown,not_applicable,source,contract,walk)
from crucis_causal.experiments.resolver import PlanResolver,ReadAccess,parse_snapshot
from crucis_causal.experiments.writer import S2RecordWriter
from crucis_causal.experiments.operations import parameter,assessment
from crucis_causal.experiments.families import values
from crucis_causal.experiments.handoff import compiler_context,install_projection
from crucis_causal.experiments.completion import install as install_completion
from crucis_causal.experiments.services import ProjectionRegistry
from crucis_causal.execution.bridge import compile_request

MODE={'name':'s3.fixture.restore_model_optimizer','version':'0.1.0-proposal.3'}

def author(destination):
    destination=Path(destination)
    if destination.exists():raise RuntimeError('Preserve old revision; author into a new directory')
    fixed=ROOT/'tests/audit_fixtures/sc3'
    old=json.loads((fixed/'checkpoint-binding.json').read_bytes());limits=api.ReaderLimits.standard()
    base=PlanResolver([(fixed/p).read_bytes() for p in old['dependencies']],limits=limits)
    access=ReadAccess(frozenset(base._views));run=old['run_binding']
    def located(ref,anchor):return base.record(ref,anchor,access,limits)
    rf=located(run,run['package_id']);trial=located(rf.record['payload']['trial'],rf.package_id)
    old_plan=located(rf.record['payload']['plan'],rf.package_id)
    condition=located(trial.record['payload']['condition'],trial.package_id)
    info=located(condition.record['payload']['information'],condition.package_id)
    subject=located(trial.record['payload']['subject'],trial.package_id)
    support_ref=qualified(subject.record['payload']['support']['value'],subject.package_id)
    oldread=api.PlanReadContext(limits,base,None,access,subject.package_id)
    _,support=values(support_ref,oldread)
    native=support['recipient']['value'];native_view=base.lookup(native['package_id'],access,limits)
    b=s1.Builder('Explicit pre-execution checkpoint fixture policies')
    resource=b.add('policy',{'policy_contract':s1.contract('s3.fixture.resource_cap_twenty','0.1.0-proposal.3'),
        'parameters':[],'scope':s1.scope(native),'authority':s1.unresolved(),'source':s1.source('intrinsic')})
    recovery=b.add('policy',{'policy_contract':MODE,'parameters':[],'scope':s1.scope(native),
        'authority':s1.unresolved(),'source':s1.source('intrinsic')})
    policies=parse_snapshot(s1bytes(b.package([resource,recovery],external_packages=[{'package_id':native_view.package_id,
        'locator':unknown(),'expected_digest':known(native_view.snapshot_digest),'access':'s1.supplied_metadata'}])),limits)
    base=base.with_view(policies);access=ReadAccess(frozenset(base._views))
    writer=S2RecordWriter(base,access,limits,name='Explicit checkpoint-condition revision, not a native run');draft=writer.context()
    def relocated(found):
        payload=copy.deepcopy(found.record['payload'])
        for _,ref,_ in walk(payload):
            if isinstance(ref,dict) and ref.get('binding')=='internal':ref.update(binding='external',package_id=found.package_id)
        payload['source']=source(draft.author,basis='derived',inputs=[reference(found.record['id'],found.record['record_type'],found.package_id)])
        return payload
    planned=reference(identity(),'plan_snapshot');trial_ref=reference(identity(),'trial_slot')
    with writer.begin(draft.author,draft.clock) as tx:
        state=parameter(tx,draft,'state',{'scope':known([native]),'reset':known(contract('s3.fixture.checkpoint_restart','0.1.0-proposal.3')),
            'reuse':known(MODE),'loaded':unknown(),'visibility':known([qualified(recovery,policies.package_id)]),
            'history':unknown(),'independence':not_applicable()})
        new_info=tx.add('information_policy',{**relocated(info),'state_policy':known(state)})
        new_condition=tx.add('condition',{**relocated(condition),'information':new_info,
            'condition_key':{'namespace':'synthetic.checkpoint','key':'explicit-model-optimizer-r2'}})
        updated={**support,'resource_policy':known(qualified(resource,policies.package_id)),
            'recovery_policy':known(qualified(recovery,policies.package_id))}
        new_support=parameter(tx,draft,'native_handoff',updated)
        new_subject=tx.add('subject_binding',{**relocated(subject),'support':known(new_support)})
        tx.add('trial_slot',{**relocated(trial),'origin_plan':planned,'condition':new_condition,'subject':new_subject},trial_ref['target'])
        plan_payload=relocated(old_plan)
        plan_payload.update(conditions=[new_condition],subjects=[new_subject],trials=index([trial_ref]),
            definitions=[new_info if ref['target']==info.record['id'] else ref for ref in plan_payload['definitions']])
        tx.add('plan_snapshot',plan_payload,planned['target'])
        resolution=qualified(rf.record['payload']['resolutions'][0],rf.package_id)
        check=assessment(tx,draft,contract('s2.bind_inputs_sources'),(planned,trial_ref,resolution),(), 'pass')
        tx.commit()
    checked=api.PlanAssessmentContext(draft.read,draft,None)
    bound=core.bind_run(planned,trial_ref,resolution,(),(check,),checked)
    if bound.state!='completed':raise AssertionError(bound.diagnostics)
    frozen=writer.frozen([bound.value.binding]);writer.base=writer.base.with_view(frozen)
    writer.access=ReadAccess(frozenset(set(writer.access.packages)|{frozen.package_id}))
    new_run=qualified(bound.value.binding,frozen.package_id)
    native_builder=s1.Builder('Checkpoint r2 native request recorder');registry=ContractRegistry()
    registry.register_route(support['operation']['value'],support['route']['value'],presentations=(contract('s2.table_input'),))
    install_completion(registry);projections=ProjectionRegistry()
    compiler=compiler_context(draft,RecordBuffer(native_builder),IdentityService(),registry,native_view,projections)
    task=located(trial.record['payload']['task'],trial.package_id)
    definition=located(task.record['payload']['definition'],task.package_id)
    response=located(definition.record['payload']['response'],definition.package_id)
    install_projection(projections,definition.record['payload']['operation'],support['operation']['value'],response.record['payload']['fulfillment_rule'],support['route']['value'],draft.author)
    occurrence=api.ProjectionOccurrence(identity(),identity())
    result=compile_request(new_run,occurrence,compiler)
    if result.state!='completed':raise AssertionError(result.issues)
    projection=result.value
    destination.mkdir(parents=True)
    files=[]
    for n,view in enumerate(sorted(projection.dependencies,key=lambda v:v.package_id)):
        path=destination/f'dependency-{n:02}.json';path.write_bytes(view.source_bytes)
        files.append({'path':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'package_id':view.package_id})
    binding={'revision':'r2','prior_fixture':old,'run_binding':new_run,
        'request':qualified(projection.projection.request,projection.request_view.package_id),
        'attempt':qualified(projection.projection.attempt,projection.request_view.package_id),'handoff':projection.handoff,'bridge':projection.bridge,
        'mode':MODE,'trial_count':'1','native_calls':'0','owner_calls':'0',
        'expected':json.loads((fixed/'oracles.json').read_bytes())['checkpoint'],'files':files}
    (destination/'manifest.json').write_text(json.dumps(binding,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'authored':str(destination),'snapshots':len(files),'native_calls':'0','owner_calls':'0'}))

if __name__=='__main__':author(ROOT/'tests/audit_fixtures/sc3_recovery_r2')
