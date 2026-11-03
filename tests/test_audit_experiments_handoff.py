from crucis.core.paths import ROOT as DATA_ROOT
"""S2-G exact projections, occurrence identity and snapshot chains (DLV-08/09)."""
import copy
import json
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'tests'))
from test_audit_experiments_wire import resolver,LIMITS
from test_audit_experiments_services import draft,ac
from test_audit_experiments_definitions import q
from crucis.experiments import api,core,ServiceError
from crucis.experiments.model import contract,source,scope,index,known,unknown,not_applicable,qualified,reference,identity
from crucis.experiments.operations import parameter,assessment,get
from crucis.experiments.writer import S2RecordWriter
from crucis.experiments.services import ProjectionRegistry
from crucis.experiments.resolver import ReadAccess,parse_snapshot
from crucis.experiments.handoff import compiler_context,install_projection,freeze_s1

def ready(cardinality=None):
    """Explicit synthetic metadata fixture; never launches a native method."""
    from crucis.connections.model import Builder,contract as c1,source as src1
    from crucis.connections.evidence import capture_bytes
    from crucis.connections.domains import finite_domain
    from crucis.connections.codec import dumps as s1bytes
    from crucis.connections.services import RecordBuffer,IdentityService,ContractRegistry
    from crucis.connections.api import RouteSpec
    from crucis.experiments.completion import install as completion
    b=Builder('S1 observer for synthetic no-execution fixture');native=reference(identity(),'s1.component');conf=reference(identity(),'s1.configuration')
    code=capture_bytes(b,b'Synthetic native metadata descriptor; not executed.',format_contract=c1('source_text'))
    settings=capture_bytes(b,b'{}',format_contract=c1('json'))
    data=capture_bytes(b,b'X,Y\n0,1\n1,0\n',format_contract=c1('csv'))
    dom=finite_domain(b,['X','Y'])
    b.add('component',{'name':'synthetic no-execution method','role':'s1.native_system','version':known('fixture-1'),
        'implementation':known({'artifact':code,'selector':not_applicable()}),'configuration':known(conf),'source':src1('intrinsic')},record_id=native['target'])
    b.add('configuration',{'component':native,'explicit_settings':settings,'resolved_defaults':not_applicable(),
        'scope':scope(native),'source':src1('intrinsic')},record_id=conf['target'])
    np=b.add('policy',{'policy_contract':contract('s2.explicit_native_policy'),'parameters':[],'scope':scope(native),'authority':unknown(),'source':src1('intrinsic')})
    initial=parse_snapshot(s1bytes(b.package([native])),LIMITS)
    base=resolver().with_view(initial);d=S2RecordWriter(base,ReadAccess(frozenset(base._views)),LIMITS).context()
    def n(ref):return qualified(ref,initial.package_id)
    plan=reference(identity(),'plan_snapshot');trial=reference(identity(),'trial_slot')
    scientific=contract('s2.discover_structure');native_op=contract('native.demo.learn');response_rule=contract('s2.roles_or_abstention')
    with d.records.begin(d.author,d.clock) as tx:
        req=tx.add('requirement',{'predicate':contract('s2.supplied_payload'),'subjects':[n(data)],'parameters':[],'scope':scope(n(data)),'source':source(d.author)})
        population=parameter(tx,d,'population',{'frame':known([n(data)]),'unit':known('source_case'),'extent':known('complete_for_scope')})
        src=tx.add('source_definition',{'source_kind':contract('s2.static_snapshot'),'domain':known(n(dom)),
            'evidence':index([n(data)]),'access':unknown(),'population':population,'assumptions':[],'lineage':[],'source':source(d.author)})
        slot=tx.add('case_slot',{'requirement':req,'sources':[src],'domain_requirements':[],'resolution_rule':contract('s2.explicit_single_selection'),
            'parameters':[],'scope':scope(n(dom)),'source':source(d.author)})
        case=tx.add('case_revision',{'case_key':{'namespace':'synthetic','key':'input-1'},'prior':not_applicable(),'origin_time':unknown(),
            'aliases':[],'scope':scope(n(dom)),'domains':index([n(dom)]),'evidence':index([n(data)]),'definitions':[src],
            'relations':[],'exposure':index([], 'not_examined'),'limitations':[],'source':source(d.author)})
        cv=tx.add('coverage_spec',{'domain':known(n(dom)),'predicate':contract('s2.adjacency'),'parameters':[],
            'extent':'complete_for_scope','omission':contract('s2.asserted_absence'),'scope':scope(n(dom)),'source':source(d.author)})
        resp=tx.add('response_contract',{'deliverables':[{'role':'s2.final','contract':c1('graph'),'scope':scope(n(dom)),
            'cardinality':cardinality or {'minimum':'1','maximum':{'kind':'finite','value':'1'}},'required':True,'abstention':'allowed','parameters':[]}],
            'coverage':cv,'fulfillment_rule':response_rule,'parameters':[],'source':source(d.author)})
        task=tx.add('task_definition',{'operation':scientific,'scope':scope(n(dom)),'response':resp,'completion':response_rule,'completion_parameters':[],'assumptions':[],'source':source(d.author)})
        tb=tx.add('task_binding',{'definition':task,'cases':[slot],'domains':[n(dom)],'targets':[],'scope':scope(n(dom)),'source':source(d.author)})
        channel=tx.add('channel_binding',{'information':contract('s2.table_input'),'recipient':known(n(native)),'domain':known(n(dom)),
            'payload_requirement':known(req),'disposition':'required','parameters':[],'scope':scope(n(dom)),'source':source(d.author)})
        info=tx.add('information_policy',{'channels':index([channel]),'state_policy':not_applicable(),'constraints':[],'scope':scope(n(dom)),'source':source(d.author)})
        condition=tx.add('condition',{'condition_key':{'namespace':'synthetic','key':'baseline'},'applies_to':scope(n(dom)),
            'varies':[],'preserves':[],'information':info,'transforms':[],'parameters':[],'source':source(d.author)})
        support=parameter(tx,d,'native_handoff',{'recipient':known(n(native)),'operation':known(native_op),'response':known(response_rule),
            'route':known('recorded'),'transport':known(c1('recorded')),'configuration':known(n(conf)),
            'support':known([n(native)]),'completion':known(contract('s2.completion_roles')),'completion_parameters':known([]),
            'presentation_policy':known(n(np)),'resource_policy':not_applicable(),'recovery_policy':not_applicable()})
        subject=tx.add('subject_binding',{'native_subject':known(n(native)),'configuration':known(n(conf)),'support':known(support),
            'requirements':[],'parameters':[],'scope':scope(n(dom)),'source':source(d.author)})
        tx.add('trial_slot',{'origin_plan':plan,'case_requirement':slot,'task':tb,'condition':condition,'subject':subject,
            'repeat_key':{'namespace':'synthetic.trial','key':'one'},'randomness':[],'source':source(d.author)},trial['target'])
        tx.add('plan_snapshot',{'purpose':contract('s2.synthetic_projection'),'definitions':[src,case,resp,info],
            'collections':[slot],'tasks':[tb],'conditions':[condition],'subjects':[subject],'comparisons':[],
            'trials':index([trial]),'resolution_requirements':[req],'commitment_requirements':[],'prior_evidence':index([]),
            'limitations':[],'source':source(d.author)},plan['target'])
        resolution=tx.add('resolution_receipt',{'entries':[{'role':'s2.case','requirement':req,'selected':index([case]),
            'rule':contract('s2.explicit_single_selection'),'basis':[case]}],'candidates':index([case]),'scope':scope(req),'source':source(d.author)})
        checked=assessment(tx,ac(d),contract('s2.bind_inputs_sources'),(plan,trial,resolution),(n(data),),'pass');tx.commit()
    bound=core.bind_run(plan,trial,resolution,(),(checked,),ac(d))
    if bound.state!='completed':raise AssertionError(bound.diagnostics)
    m=d.records.frozen([bound.value.binding]);d.records.base=d.records.base.with_view(m)
    d.records.access=ReadAccess(frozenset(set(d.records.access.packages)|{m.package_id}))
    binding=qualified(bound.value.binding,m.package_id)
    registry=ContractRegistry();registry.register_route(native_op,'recorded',presentations=(contract('s2.table_input'),));completion(registry)
    projections=ProjectionRegistry();s1=RecordBuffer(b)
    ctx=compiler_context(d,s1,IdentityService(),registry,initial,projections)
    install_projection(projections,scientific,native_op,response_rule,'recorded',d.author)
    route=RouteSpec('recorded',c1('recorded'),native_op,())
    return d,ctx,binding,native,route,initial

def project():
    d,c,b,n,r,v=ready();occ=api.ProjectionOccurrence(identity(),identity());out=core.project_request(b,occ,n,r,c)
    return d,c,b,n,r,v,occ,out

class HandoffCases(unittest.TestCase):
    def test_supported_differently_named_operation_projects_only_native_fields_and_allowed_bytes(self):
        d,c,b,n,r,v,occ,result=project();self.assertEqual(result.state,'completed',result.diagnostics)
        request=c.s1_records.get(result.value.request)['payload'];self.assertEqual(request['operation'],r.operation)
        self.assertNotEqual(r.operation,contract('s2.discover_structure'));self.assertEqual(len(result.value.presented.presentations),1)
        self.assertEqual(request['resource_policy']['state'],'not_applicable')
        presentation=c.s1_records.get(result.value.presented.presentations[0])['payload']
        snapshot=c.s1_records.get(presentation['payload']['value']['artifact'])['payload']
        self.assertEqual(snapshot['content']['text'],'X,Y\n0,1\n1,0\n')
        self.assertEqual(c.s1_records.get(result.value.attempt)['payload']['native_identity']['state'],'unresolved')

    def test_projection_same_occurrence_is_idempotent_without_refreshing_timestamps(self):
        d,c,b,n,r,v,occ,first=project();self.assertEqual(first.state,'completed',first.diagnostics)
        before=copy.deepcopy(c.s1_records.builder._records)
        second=core.project_request(b,occ,n,r,c)
        self.assertEqual(second.state,'completed',second.diagnostics);self.assertFalse(second.value.s1_records)
        self.assertEqual(before,c.s1_records.builder._records)

    def test_missing_native_support_or_exact_projection_registry_never_invokes(self):
        d,c,b,n,r,v=ready();c.projections._entries.clear()
        result=core.project_request(b,api.ProjectionOccurrence(identity(),identity()),n,r,c)
        self.assertEqual(result.state,'rejected');self.assertEqual(result.diagnostics[0].code,'s2.projection_procedure_unavailable')
        bad=core.project_request(q('bridge-M-input-binding','run'),api.ProjectionOccurrence(identity(),identity()),n,r,c)
        self.assertEqual(bad.state,'rejected');self.assertEqual(bad.diagnostics[0].code,'s2.native_support_unestablished')

    def test_s1_writer_and_s2_transaction_rollback_on_completion_contract_failure(self):
        d,c,b,n,r,v=ready();c.s1_registry._rules.clear();before=copy.deepcopy(c.s1_records.builder._records);before2=d.records.snapshot()
        result=core.project_request(b,api.ProjectionOccurrence(identity(),identity()),n,r,c)
        self.assertEqual(result.state,'rejected');self.assertEqual(before,c.s1_records.builder._records);self.assertEqual(before2,d.records.snapshot())

    def test_frozen_R_and_later_O_have_distinct_package_id_and_unchanged_copied_records(self):
        d,c,b,n,r,v,occ,result=project();self.assertEqual(result.state,'completed',result.diagnostics)
        builder=c.s1_records.builder
        first=freeze_s1(builder.package([result.value.request]),LIMITS)
        builder.add('gap',{'subjects':[result.value.attempt],'reasons':['s1.later_observation_unknown'],
            'scope':scope(result.value.attempt),'source':{'basis':'observed','evidence':[],'procedure':unknown(),'inputs':[]}})
        second=freeze_s1(builder.package([result.value.request]),LIMITS)
        self.assertNotEqual(first.package_id,second.package_id)
        later={x['id']:x for x in second.records}
        self.assertTrue(all(later[x['id']]==x for x in first.records));self.assertNotEqual(first.snapshot_digest,second.snapshot_digest)

    def test_handoff_pins_exact_R_request_attempt_and_run_identity(self):
        d,c,b,n,r,v,occ,result=project();self.assertEqual(result.state,'completed',result.diagnostics)
        frozen=freeze_s1(c.s1_records.builder.package([result.value.request]),LIMITS)
        handoff=core.record_handoff(b,occ,frozen,d);self.assertEqual(handoff.state,'completed',handoff.diagnostics)
        p=get(handoff.value,d)['payload'];self.assertEqual(p['request']['package_id'],frozen.package_id)
        self.assertEqual(get(p['request'],d)['id'],occ.request_id)
        bad=core.record_handoff(q('bridge-M-input-binding','run'),occ,frozen,d)
        self.assertEqual(bad.state,'rejected');self.assertEqual(bad.diagnostics[0].code,'s2.handoff_run_binding_mismatch')

    def test_changed_request_or_presentation_cannot_reuse_the_occurrence_or_handoff(self):
        for field in ['request','presentation']:
            d,c,b,n,r,v,occ,result=project();self.assertEqual(result.state,'completed',result.diagnostics)
            builder=c.s1_records.builder
            if field=='request':builder._records[occ.request_id]['payload']['completion']=contract('s2.other_completion')
            else:builder._records[result.value.presented.presentations[0]['target']]['payload']['information_contract']=contract('s2.private_reference')
            second=core.project_request(b,occ,n,r,c);self.assertEqual(second.state,'rejected')
            frozen=freeze_s1(builder.package([result.value.request]),LIMITS)
            self.assertEqual(core.record_handoff(b,occ,frozen,d).state,'rejected')

    def test_complex_cardinality_retained_in_explicit_completion_parameters(self):
        d,c,b,n,r,v=ready({'minimum':'2','maximum':{'kind':'finite','value':'3'}})
        result=core.project_request(b,api.ProjectionOccurrence(identity(),identity()),n,r,c)
        self.assertEqual(result.state,'completed',result.diagnostics)
        params=c.s1_records.get(result.value.request)['payload']['completion_parameters']
        actual=json.loads(c.s1_records.get(params[0])['payload']['content']['text'])
        self.assertEqual(actual['deliverables'][0]['cardinality']['minimum'],'2')

    def test_compiler_code_identity_and_no_native_execution_capability(self):
        d,c,b,n,r,v=ready();component=c.s1_records.get(c.compiler)['payload']
        blob=c.s1_records.get(component['implementation']['value']['artifact'])['payload']['content']
        self.assertIn('handoff.py',json.loads(blob['text']))
        self.assertFalse(hasattr(c,'grant'));self.assertFalse(hasattr(c,'executor'))
        bad=core.project_request(b,api.ProjectionOccurrence(identity(),identity()),reference(identity(),'s1.component'),r,c)
        self.assertEqual(bad.state,'rejected')

    def test_external_evidence_links_are_qualified_and_historical_imports_do_not_gain_attempts(self):
        d=draft();result=core.link_evidence((q('B-s2-receipts','case'),),(q('B-s1-trace','recovered_graph'),),d)
        self.assertEqual(result.state,'completed');self.assertFalse(any(r['record_type']=='s1.attempt' for r in result.additions.records))
        self.assertEqual(core.link_evidence((q('B-s2-receipts','case'),),({'binding':'internal','target':identity(),'target_type':'s1.output'},),d).state,'rejected')

if __name__=='__main__':unittest.main()
