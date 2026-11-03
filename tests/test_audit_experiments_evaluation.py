from crucis_causal.core.paths import ROOT as DATA_ROOT
"""S2-E explicit populations, missingness and evaluation selections (DLV-08/09)."""
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'tests'))
from test_audit_experiments_services import draft,ac
from test_audit_experiments_definitions import q
from crucis_causal.experiments import core
from crucis_causal.experiments.model import contract,source,scope,index,known,unknown
from crucis_causal.experiments.operations import get,parameter,assessment
from crucis_causal.experiments.evaluation import install_metadata_descriptor

def proposal(d,comparison,units,entries):
    with d.records.begin(d.author,d.clock) as tx:
        ref=tx.add('analysis_population_receipt',{'comparison':comparison,'intended':index(units),'entries':entries,
            'rule':contract('s2.retain_all_intended_units'),'parameters':[],'source':source(d.author)});tx.commit()
    return ref
def entry(unit,outputs=(),disposition='included',reasons=(),basis=(),key='unit'):
    return {'key':key,'unit':unit,'members':[{'role':'s2.selected_output','target':r} for r in outputs],
        'disposition':disposition,'reasons':list(reasons),'basis':list(basis),'weight':unknown()}
def metadata_scope(d,measure='s2.metadata_binding',tasks=(),references=()):
    with d.records.begin(d.author,d.clock) as tx:
        p=parameter(tx,d,'comparison',{'estimand':known(contract('s2.metadata_only')),'direction':known('none'),
            'matching':known(contract('s2.exact_source')),'units':known([q('A-s2-receipts','case')]),
            'weights':known([]),'dependence':known([]),'missingness':known(contract('s2.retain_all_intended_units')),
            'output_selection':known(contract('s2.declared_population')),'reference_selection':known(contract('s2.no_reference_required')),
            'uncertainty':known(contract('s2.no_inference')),'multiplicity':known(contract('s2.no_inference')),'stopping':known(contract('s2.fixed_bounded_design'))})
        comp=tx.add('comparison',{'tasks':list(tasks),'conditions':[],'target':p,'measures':[contract(measure)],
            'analysis_rule':contract('s2.metadata_only'),'population_rule':contract('s2.retain_all_intended_units'),
            'matching':p,'dependence':p,'missingness':p,'uncertainty':p,'parameters':[p],'source':source(d.author)})
        plan=tx.add('plan_snapshot',{'purpose':contract('s2.retrospective_metadata'),'definitions':[q('A-s2-receipts','case'),*references],
            'collections':[],'tasks':list(tasks),'conditions':[],'subjects':[],'comparisons':[comp],'trials':index([]),
            'resolution_requirements':[],'commitment_requirements':[],'prior_evidence':index([q('A-s2-receipts','case')]),
            'limitations':[],'source':source(d.author)});tx.commit()
    return plan,comp

class EvaluationCases(unittest.TestCase):
    def test_explicit_current_metadata_population_binds_without_invented_native_trial_or_metric(self):
        d=draft();ctx=ac(d);plan,comp=metadata_scope(d);unit=q('A-s2-receipts','case')
        proposed=proposal(d,comp,[unit],[entry(unit)])
        result=core.record_population(comp,(plan,proposed),ctx);self.assertEqual(result.state,'completed',result.diagnostics)
        install_metadata_descriptor(d.read.registry,d.author)
        bound=core.bind_evaluation(plan,comp,result.value,(),(),(),(),(),ctx)
        self.assertEqual(bound.state,'completed',bound.diagnostics)
        self.assertFalse(any(r['record_type']=='s2.trial_slot' for r in bound.additions.records))

    def test_missing_observations_retain_every_six_planned_slot_without_zero_score(self):
        d=draft();ctx=ac(d);comp=q('A-s2-plan','comparison')
        result=core.record_population(comp,(q('A-s2-plan','plan'),),ctx)
        self.assertEqual(result.state,'partial');p=get(result.value,d)['payload']
        self.assertEqual(len(p['intended']['members']),6);self.assertEqual(len(p['entries']),6)
        self.assertEqual({e['disposition'] for e in p['entries']},{'unresolved'})
        self.assertTrue(all(e['weight']['state']=='unresolved' for e in p['entries']))

    def test_no_unstated_denominator_from_comparison_label_or_local_files(self):
        d=draft();result=core.record_population(q('B-s2-plan','comparison'),(),ac(d))
        self.assertEqual(result.state,'partial');self.assertEqual(get(result.value,d)['payload']['intended']['extent'],'unresolved')

    def test_abstention_or_intermediate_stage_cannot_enter_final_graph_quality(self):
        for label in ['neutral1','real2_stage']:
            d=draft();unit=q('A-s2-plan','trial.real1');comp=q('A-s2-plan','comparison')
            p=proposal(d,comp,[unit],[entry(unit,[q('A-s1-trace',label)])])
            result=core.record_population(comp,(q('A-s2-plan','plan'),p),ac(d));self.assertEqual(result.state,'rejected',(label,result))
            self.assertFalse(result.additions.records)

    def test_multiple_final_outputs_remain_ambiguous_not_last_or_best(self):
        d=draft();unit=q('A-s2-plan','trial.real1');comp=q('A-s2-plan','comparison')
        p=proposal(d,comp,[unit],[entry(unit,[q('A-s1-trace','real1'),q('A-s1-trace','neutral2')])])
        result=core.record_population(comp,(q('A-s2-plan','plan'),p),ac(d))
        self.assertEqual(result.state,'partial');self.assertIn('s2.output_selection_ambiguous',{i.code for i in result.diagnostics})

    def test_conformance_alone_does_not_invent_native_trial_output_association(self):
        d=draft();ctx=ac(d);unit=q('A-s2-plan','trial.real1');comp=q('A-s2-plan','comparison')
        with d.records.begin(d.author,d.clock) as tx:
            checked=assessment(tx,ctx,contract('s2.condition_conformance'),(unit,),(),'pass');tx.commit()
        p=proposal(d,comp,[unit],[entry(unit,[q('A-s1-trace','real1')],basis=[checked])])
        result=core.record_population(comp,(p,),ctx)
        self.assertEqual(result.state,'partial');self.assertIn('s2.trial_output_association_unestablished',{i.code for i in result.diagnostics})

    def test_exclusion_without_a_reason_is_not_an_accounted_denominator(self):
        d=draft();_,comp=metadata_scope(d);unit=q('A-s2-receipts','case')
        p=proposal(d,comp,[unit],[entry(unit,disposition='excluded')])
        self.assertEqual(core.record_population(comp,(p,),ac(d)).state,'rejected')

    def test_nonconforming_inclusion_rejected_but_poor_quality_not_an_exclusion(self):
        d=draft();ctx=ac(d);unit=q('A-s2-plan','trial.real1');comp=q('A-s2-plan','comparison')
        with d.records.begin(d.author,d.clock) as tx:
            failed=assessment(tx,ctx,contract('s2.condition_conformance'),(unit,),(),'fail');tx.commit()
        p=proposal(d,comp,[unit],[entry(unit,[q('A-s1-trace','real1')],basis=[failed])])
        self.assertEqual(core.record_population(comp,(p,),ctx).state,'rejected')
        p=proposal(d,comp,[unit],[entry(unit,disposition='excluded',reasons=['s2.poor_quality_is_not_exclusion'])])
        self.assertEqual(core.record_population(comp,(p,),ctx).state,'rejected')

    def test_duplicate_unit_requires_distinct_trial_or_membership_identity(self):
        d=draft();_,comp=metadata_scope(d);unit=q('A-s2-receipts','case')
        p=proposal(d,comp,[unit],[entry(unit,key='a'),entry(unit,key='b')])
        self.assertEqual(core.record_population(comp,(p,),ac(d)).state,'rejected')

    def test_scientific_metric_descriptor_absent_not_invented_by_available_graph(self):
        d=draft();ctx=ac(d);plan,comp=metadata_scope(d,'s4.adjacency_f1');unit=q('A-s2-receipts','case')
        p=proposal(d,comp,[unit],[entry(unit)]);pop=core.record_population(comp,(p,),ctx)
        result=core.bind_evaluation(plan,comp,pop.value,(),(),(),(),(),ctx)
        self.assertEqual(result.state,'partial');self.assertIn('s2.measurement_descriptor_unavailable',{i.code for i in result.diagnostics})

    def test_reference_must_be_declared_not_whichever_scores_best(self):
        d=draft();ctx=ac(d);plan,comp=metadata_scope(d);unit=q('A-s2-receipts','case')
        p=proposal(d,comp,[unit],[entry(unit)]);pop=core.record_population(comp,(p,),ctx)
        result=core.bind_evaluation(plan,comp,pop.value,(q('B-s2-plan','ref_left'),),(),(),(),(),ctx)
        self.assertEqual(result.state,'rejected');self.assertEqual(result.diagnostics[0].code,'s2.reference_not_declared_by_plan')

    def test_baseline_and_active_target_parameters_are_not_substitutable(self):
        d=draft();ctx=ac(d)
        with d.records.begin(d.author,d.clock) as tx:
            baseline=parameter(tx,d,'intervention',{'task_target':known('baseline')})
            active=parameter(tx,d,'intervention',{'task_target':known('active_environment')})
            task=tx.add('task_binding',{'definition':q('H-s2-plan','task'),'cases':[q('H-s2-plan','case_slot')],
                'domains':[q('H-s1-definitions','domain')],'targets':[baseline],'scope':scope(baseline),'source':source(d.author)})
            ref=tx.add('reference_definition',{'reference_kind':contract('s2.source_model_claim'),'assertions':known(q('H-s1-definitions','active_reference')),
                'domain':known(q('H-s1-definitions','domain')),'applicability':[],'coverage':q('H-s2-plan','coverage'),
                'tier':known('T1'),'parameters':[active],'source':source(d.author)});tx.commit()
        plan,comp=metadata_scope(d,tasks=(task,),references=(ref,));unit=q('A-s2-receipts','case')
        p=proposal(d,comp,[unit],[entry(unit)]);pop=core.record_population(comp,(p,),ctx)
        result=core.bind_evaluation(plan,comp,pop.value,(ref,),(),(),(),(),ctx)
        self.assertEqual(result.state,'rejected');self.assertEqual(result.diagnostics[0].code,'s2.reference_target_mismatch')

if __name__=='__main__':unittest.main()
