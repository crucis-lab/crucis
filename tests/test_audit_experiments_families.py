from crucis.core.paths import ROOT as DATA_ROOT
"""S2-D cross-family/materialization contracts and scientific limits (DLV-08/09)."""
import copy
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'tests'))
from test_audit_experiments_definitions import q
from test_audit_experiments_services import draft,ac
from crucis.experiments import core,ServiceError
from crucis.experiments.model import source,scope,contract,known,unknown,number,reference
from crucis.experiments.operations import get,parameter,assessment
from crucis.experiments.families import inspect,values,entity_key,install

def with_payload(d,format_name,value):
    from crucis.connections.model import Builder,contract as c1,known as k1,unresolved
    from crucis.connections.evidence import capture_bytes
    from crucis.connections.codec import dumps as s1bytes
    from crucis.experiments.model import walk,digest,qualified,not_applicable
    from crucis.experiments.resolver import parse_snapshot,ReadAccess
    from crucis.experiments.writer import S2RecordWriter
    import json
    b=Builder('synthetic typed payload source');blob=capture_bytes(b,json.dumps(value).encode(),format_contract=c1('s2.payload.'+format_name))
    dependencies={}
    for _,r,_ in walk(value):
        if isinstance(r,dict) and r.get('binding')=='external':
            view=d.read.resolver.lookup(r['package_id'],d.read.access,d.read.limits)
            dependencies[view.package_id]={'package_id':view.package_id,'locator':unresolved(),'expected_digest':k1(view.snapshot_digest),'access':'s1.supplied'}
    view=parse_snapshot(s1bytes(b.package([blob],external_packages=list(dependencies.values()))),d.read.limits)
    base=d.records.base.with_view(view);access=ReadAccess(frozenset(base._views))
    other=S2RecordWriter(base,access,d.read.limits).context()
    return other,{'artifact':qualified(blob,view.package_id),'selector':not_applicable()}

def modified(d,original,updates):
    name,b=values(original,d);b.update(updates)
    with d.records.begin(d.author,d.clock) as tx:ref=parameter(tx,d,name,b);tx.commit()
    return ref

class FamilyCases(unittest.TestCase):
    def test_all_twenty_five_parameter_readers_register_exactly_without_native_imports(self):
        d=draft();install(d.read.registry,d.author)
        from crucis.experiments.schema import catalog
        self.assertEqual(len(d.read.registry._entries),25)
        for name in catalog()['parameter_schemas']:
            self.assertIsNotNone(d.read.registry.lookup(contract('s2.params.'+name)))
            self.assertEqual(inspect(q('schema-preservation-examples','schema.'+name),d).result,'unknown')

    def test_temporal_boundaries_units_and_unknown_epoch(self):
        d=draft();base=q('D-s2-plan','temporal')
        self.assertEqual(inspect(base,d).result,'unknown')
        bad=modified(d,base,{'lag':known(number(-1000))})
        self.assertEqual(inspect(bad,d).result,'fail')
        unit=modified(d,base,{'unit':known({'name':'millisecond','convention':contract('s2.milliseconds')})})
        self.assertIn('s2.temporal_unit_mapping_required',{i.code for i in inspect(unit,d).issues})

    def test_temporal_large_window_does_not_allocate_unbounded_range(self):
        # Exact coordinate/window identity remains supplied metadata, no row synthesis.
        d=draft();ref=q('D-s2-plan','temporal');name,b=values(ref,d)
        self.assertEqual(name,'temporal');self.assertEqual(b['lag']['value']['text'],'-1')
        read=d.read;payload=read.resolver.payload(b['windows']['value'],read.active_package,read.access,read.limits)
        self.assertEqual([w['eligible_children'][0] for w in payload['windows']],['1','4'])
        payload['windows'][0]['end_exclusive']='1000000000000000'
        other,blob=with_payload(d,'windows',payload)
        changed=modified(other,ref,{'windows':known(blob)})
        self.assertIn('s2.window_outside_source_coordinates',{i.code for i in inspect(changed,other).issues})

    def test_relational_perspective_and_site_identity_are_not_column_aliases(self):
        d=draft();bad=modified(d,q('E-s2-plan','relational'),{'perspective':known('Firm')})
        self.assertEqual(inspect(bad,d).result,'fail')
        self.assertNotEqual(entity_key('site-A','v1','Employee',('worksFor','Firm'),'17'),entity_key('site-B','v1','Employee',('worksFor','Firm'),'17'))
        with self.assertRaises(ServiceError):entity_key('','v1','Employee',(),'17')

    def test_distributed_unknown_contributions_do_not_create_central_rows_or_two_site_claim(self):
        d=draft();ref=q('E-s2-plan','distributed');result=inspect(ref,d)
        self.assertEqual(result.result,'unknown')
        self.assertIn('s2.required_contributions_unestablished',{i.code for i in result.issues})
        _,b=values(ref,d);self.assertEqual(len(b['parties']['value']),2)

    def test_alignment_keeps_two_mappings_and_rejects_unique_or_best_score_claim(self):
        d=draft();ref=q('F-s2-receipts','alignment')
        _,b=values(ref,d);self.assertEqual(len(b['candidates']['value']),2)
        self.assertEqual(inspect(modified(d,ref,{'ambiguity':known('unique')}),d).result,'fail')
        self.assertEqual(inspect(modified(d,ref,{'selection':known(contract('s2.best_reference_score'))}),d).result,'fail')

    def test_native_weighted_collection_preserves_equal_graph_particles_and_missing_parameters(self):
        d=draft();ref=q('G-s2-receipts','weights');_,b=values(ref,d)
        r=d.read;payload=r.resolver.payload(b['members']['value'],r.active_package,r.access,r.limits)
        self.assertEqual([m['weight']['text'] for m in payload['members']],['2','1','1','2'])
        self.assertNotEqual(payload['members'][0]['object'],payload['members'][1]['object'])
        self.assertNotEqual(payload['members'][0]['parameter'],payload['members'][1]['parameter'])
        self.assertEqual(inspect(ref,d,require_known=False).result,'pass')
        self.assertFalse(any(x['record_type']=='s2.trial_slot' for x in d.records.snapshot().records))

    def test_zero_negative_and_nonfinite_native_mass_withholds_normalization(self):
        for invalid in ['zero','negative','nonfinite']:
            d=draft();ref=q('G-s2-receipts','weights');_,b=values(ref,d);r=d.read
            payload=r.resolver.payload(b['members']['value'],r.active_package,r.access,r.limits)
            for m in payload['members']:m['weight']=number(0)
            if invalid=='negative':payload['members'][0]['weight']=number(-1)
            if invalid=='nonfinite':payload['members'][0]['weight']=number('NaN')
            other,blob=with_payload(d,'weighted_members',payload)
            changed=modified(other,ref,{'members':known(blob),'normalization':known(contract('s2.divide_positive_finite_total'))})
            self.assertEqual(inspect(changed,other,require_known=False).result,'fail')

    def test_complete_supplied_identity_realization_records_checks_without_transform_execution(self):
        d=draft();ctx=ac(d);domain=q('A-s1-definitions','domain')
        with d.records.begin(d.author,d.clock) as tx:
            req=tx.add('requirement',{'predicate':contract('test.same_domain_identity'),'subjects':[domain],'parameters':[],'scope':scope(domain),'source':source(d.author)})
            spec=tx.add('transform_spec',{'operation':contract('s2.identity_binding'),'inputs':[req],'parameters':[],'preserves':[req],'produces':[req],'randomness':[],'predecessors':[],'reference_rule':contract('s2.same_domain'),'source':source(d.author)})
            realized=parameter(tx,d,'transform',{'operation':known(contract('s2.identity_binding')),'inputs':known([domain]),'outputs':known([domain]),'maps':known([]),'preservation':known([req]),'losses':known([]),'fitted_inputs':known([]),'reference_rule':known(contract('s2.same_domain')),'order':known([])})
            checked=assessment(tx,ctx,contract('test.same_domain_identity'),(req,spec),(domain,),'pass');tx.commit()
        result=core.record_materialization(spec,(checked,),realized,ctx)
        self.assertEqual(result.state,'completed',result.diagnostics)
        self.assertEqual(get(result.value,d)['payload']['outputs'],[domain])

    def test_unknown_intervention_targets_not_empty_or_known(self):
        d=draft();ref=q('H-s2-plan','intervention');_,b=values(ref,d);r=d.read
        payload=r.resolver.payload(b['environments']['value'],r.active_package,r.access,r.limits)
        self.assertEqual(payload['environments'][0]['targets'],known([]));self.assertEqual(payload['environments'][2]['targets']['state'],'unresolved')
        bad=modified(d,ref,{'target_disclosure':known('known')});self.assertEqual(inspect(bad,d).result,'fail')

    def test_proxy_domain_not_reused_as_underlying_identity(self):
        d=draft();ref=q('H-s2-plan','measurement');_,b=values(ref,d)
        bad=modified(d,ref,{'observed':b['underlying']});self.assertEqual(inspect(bad,d).result,'fail')

    def test_random_repeat_key_does_not_establish_shared_native_randomness(self):
        d=draft()
        with d.records.begin(d.author,d.clock) as tx:
            ref=parameter(tx,d,'randomization',{'role':known('native'),'coupling':known('shared_realization'),'coupled_to':known([])})
            tx.commit()
        self.assertIn('s2.coupling_binding_required',{i.code for i in inspect(ref,d).issues})

    def test_missing_materialization_and_subject_support_remain_partial_without_execution(self):
        d=draft();ctx=ac(d)
        resolved=core.resolve_slots((q('A-s2-plan','case_slot'),),(q('A-s2-receipts','case'),),d)
        bound=core.bind_run(q('A-s2-plan','plan'),q('A-s2-plan','trial.real1'),resolved.value.receipt,(),(),ctx)
        self.assertEqual(bound.state,'partial');codes={i.code for i in bound.diagnostics}
        self.assertIn('s2.materialization_required',codes);self.assertIn('s2.native_support_unestablished',codes)
        self.assertFalse(any(r['record_type'].startswith('s1.') for r in bound.additions.records))

    def test_partial_transform_receipt_preserves_gaps_and_does_not_generate_sources(self):
        d=draft();ctx=ac(d)
        with d.records.begin(d.author,d.clock) as tx:
            ref=parameter(tx,d,'transform',{'operation':known(contract('s2.checked_presentation')),'inputs':known([q('A-s2-plan','source')]),'outputs':unknown()});tx.commit()
        result=core.record_materialization(q('A-s2-plan','transform'),(),ref,ctx)
        self.assertEqual(result.state,'partial');p=get(result.value,d)['payload']
        self.assertEqual(p['outputs'],[]);self.assertTrue(p['gaps']);self.assertEqual(p['checks'],[])

    def test_recipe_predecessor_cycle_does_not_become_executable_order(self):
        from crucis.experiments.information import transform_dependencies
        d=draft();ref=reference(d.identities.allocate(),'transform_spec')
        with d.records.begin(d.author,d.clock) as tx:
            tx.add('transform_spec',{'operation':contract('s2.identity_binding'),'inputs':[],'parameters':[],
                'preserves':[],'produces':[],'randomness':[],'predecessors':[ref],
                'reference_rule':contract('s2.same_domain'),'source':source(d.author)},ref['target']);tx.commit()
        self.assertEqual(transform_dependencies(ref,d).result,'fail')

    def test_evaluator_channel_cannot_become_native_permission_by_presentation_label(self):
        from crucis.connections.model import Builder,contract as c1,unknown_ref,unresolved
        from crucis.connections.codec import dumps as s1bytes
        from crucis.experiments.resolver import parse_snapshot,ReadAccess
        from crucis.experiments.writer import S2RecordWriter
        from crucis.experiments.information import check_information
        from crucis.experiments.model import index,qualified
        d=draft();b=Builder('synthetic native metadata');policy=b.add('policy',{'policy_contract':c1('test_policy'),'parameters':[],'scope':scope(b.producer),'authority':unresolved(),'source':{'basis':'intrinsic','evidence':[],'procedure':unresolved(),'inputs':[]}})
        req=b.add('request',{'operation':c1('test_discovery'),'task_scope':scope(b.producer),'deliverables':[],'completion':c1('test_completion'),'completion_parameters':[],'presentation_policy':policy,'resource_policy':unresolved(),'recovery_policy':unresolved(),'route':'s1.recorded','source':{'basis':'intrinsic','evidence':[],'procedure':unresolved(),'inputs':[]}})
        attempt=b.add('attempt',{'request':req,'native_identity':unresolved(),'initial_state':unresolved(),'binding':unresolved(),'source':{'basis':'intrinsic','evidence':[],'procedure':unresolved(),'inputs':[]}})
        presented=b.add('presentation',{'information_contract':contract('s2.private_reference'),'payload':unresolved(),'endpoint':unresolved(),'domain':unresolved(),'schema':unresolved(),'recipient':b.producer,'state':'permitted','attempt':attempt,'source':{'basis':'intrinsic','evidence':[],'procedure':unresolved(),'inputs':[]}})
        view=parse_snapshot(s1bytes(b.package([presented])),d.read.limits);base=d.records.base.with_view(view)
        other=S2RecordWriter(base,ReadAccess(frozenset(base._views)),d.read.limits).context()
        with other.records.begin(other.author,other.clock) as tx:
            channel=tx.add('channel_binding',{'information':contract('s2.private_reference'),'recipient':known(qualified(b.producer,view.package_id)),
                'domain':unknown(),'payload_requirement':unknown(),'disposition':'forbidden','parameters':[],'scope':scope(other.author),'source':source(other.author)})
            ip=tx.add('information_policy',{'channels':index([channel]),'state_policy':unknown(),'constraints':[],'scope':scope(other.author),'source':source(other.author)});tx.commit()
        result=check_information(ip,(qualified(presented,view.package_id),),other)
        self.assertEqual(result.result,'fail');self.assertIn('s2.forbidden_information',{i.code for i in result.issues})

if __name__=='__main__':unittest.main()
