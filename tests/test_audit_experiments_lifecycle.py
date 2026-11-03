from crucis_causal.core.paths import ROOT as DATA_ROOT
"""S2-F fixed bytes, amendments, adaptive choices and exposure (DLV-08/09)."""
import copy
import json
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'tests'))
from test_audit_experiments_wire import package,desc,LIMITS,context
from test_audit_experiments_services import draft
from test_audit_experiments_definitions import q
from crucis_causal.experiments import core,api
from crucis_causal.experiments.model import contract,source,scope,index,known,unknown,number,reference,qualified,identity
from crucis_causal.experiments.operations import parameter,get
from crucis_causal.experiments.lifecycle import event_order,prospective_dependencies,record_decision,exposure_information

def event(d,subjects=()):
    with d.records.begin(d.author,d.clock) as tx:
        ref=tx.add('lifecycle_event',{'event_contract':contract('s2.observer_account'),'subjects':list(subjects),'parameters':[],
            'predecessors':[],'claimed_time':unknown(),'observed_time':unknown(),'source':source(d.author)});tx.commit()
    return ref
def commitment(d,assurance='local_snapshot'):
    plan=q('A-s2-plan','plan');ev=event(d,(plan,))
    with d.records.begin(d.author,d.clock) as tx:
        ref=parameter(tx,d,'commitment',{'fixed':known([plan]),'assurance':known(assurance)});tx.commit()
    return plan,api.CommitmentEvidence({'package_id':desc('A-s2-plan')['package_id'],'digest':copy.deepcopy(desc('A-s2-plan')['digest']),'selected_records':[plan['target']]},ev,ref,())
def action(d,value=1,state='selected',information=None):
    information=information or q('C-s1-trace','response1')
    with d.records.begin(d.author,d.clock) as tx:
        ref=parameter(tx,d,'action',{'target':known(q('C-s1-definitions','domain.Y')),'value':known(number(value)),
            'operation':known(contract('s2.set_value')),'state':known(state),'source_input':known([information])});tx.commit()
    return ref

class LifecycleCases(unittest.TestCase):
    def test_commitment_pins_exact_prior_bytes_without_inventing_original_time(self):
        d=draft();plan,e=commitment(d);result=core.record_commitment(plan,e,d)
        self.assertEqual(result.state,'completed',result.diagnostics);p=get(result.value,d)['payload']
        self.assertEqual(p['content']['digest'],desc('A-s2-plan')['digest']);self.assertNotEqual(p['content']['package_id'],d.records.package_id)
        self.assertEqual(get(e.event,d)['payload']['observed_time']['state'],'unresolved')

    def test_changed_digest_self_content_or_wrong_selected_plan_rejected(self):
        from dataclasses import replace
        for mode in ['digest','self','selected']:
            d=draft();plan,e=commitment(d);subject=copy.deepcopy(e.subject)
            if mode=='digest':subject['digest']['value']='0'*64
            elif mode=='self':subject['package_id']=d.records.package_id
            else:subject['selected_records']=[]
            result=core.record_commitment(plan,replace(e,subject=subject),d)
            self.assertEqual(result.state,'rejected');self.assertFalse(result.additions.records)

    def test_local_record_never_creates_external_attestation_or_grant(self):
        d=draft();plan,e=commitment(d,'external_attestation');result=core.record_commitment(plan,e,d)
        self.assertEqual(result.state,'partial');self.assertEqual(result.diagnostics[0].code,'s2.external_assurance_not_established_by_local_record')
        self.assertFalse(any(r['record_type'].startswith('s1.') for r in result.additions.records))

    def test_cycle_in_event_predecessors_is_not_observed_chronology(self):
        d=draft();ref=reference(identity(),'lifecycle_event')
        with d.records.begin(d.author,d.clock) as tx:
            tx.add('lifecycle_event',{'event_contract':contract('s2.test_event'),'subjects':[],
                'parameters':[],'predecessors':[ref],'claimed_time':unknown(),'observed_time':unknown(),'source':source(d.author)},ref['target']);tx.commit()
        self.assertEqual(event_order((ref,),d).result,'fail')

    def test_future_bytes_in_dependency_block_definition_even_without_direct_record_link(self):
        from crucis_causal.experiments.resolver import parse_snapshot,ReadAccess
        from crucis_causal.experiments.codec import dumps
        from crucis_causal.experiments.writer import S2RecordWriter
        d=draft();plan=q('A-s2-plan','plan');future=q('A-s1-trace','real1')
        self.assertEqual(prospective_dependencies(plan,(future,),d).result,'pass')
        p=package('A-s2-plan');p['package_id']=identity()
        o=d.read.resolver.lookup(future['package_id'],d.read.access,LIMITS)
        p['external_packages'].append({'package_id':o.package_id,'format':o.format,'locator':unknown(),'expected_digest':known(o.snapshot_digest),'access':'s2.supplied'})
        view=parse_snapshot(dumps(p,LIMITS),LIMITS);base=d.records.base.with_view(view)
        other=S2RecordWriter(base,ReadAccess(frozenset(base._views)),LIMITS).context()
        self.assertEqual(prospective_dependencies(reference(plan['target'],'plan_snapshot',view.package_id),(future,),other).result,'fail')

    def test_amendment_retains_old_new_and_prior_exposure_no_native_rerun(self):
        d=draft();old=q('A-s2-plan','plan');new=q('bridge-P2-amended-plan','plan');ev=event(d,(old,new))
        explanation=q('bridge-H-handoff-and-amendment','projection')
        evidence=api.AmendmentEvidence(ev,scope(old,new),'s2.declared_revision',explanation,index([q('C-s1-trace','response1')]))
        result=core.record_amendment(old,new,evidence,d);self.assertEqual(result.state,'completed')
        p=get(result.value,d)['payload'];self.assertEqual(p['previous'],old);self.assertEqual(p['revised'],new);self.assertEqual(len(p['prior_observed']['members']),1)
        self.assertEqual(get(q('A-s2-plan','trial.real1'),d)['payload']['origin_plan']['target'],old['target'])
        self.assertEqual(core.record_amendment(old,old,evidence,d).state,'rejected')

    def test_threshold_decision_records_selected_action_and_no_delivery(self):
        d=draft();choice=action(d);ev=event(d,(choice,))
        result=record_decision(q('C-s2-plan','selection'),(q('C-s1-trace','response1'),),(choice,),contract('s2.threshold_action_selection'),ev,d)
        self.assertEqual(result.state,'completed',result.diagnostics)
        p=get(result.value,d)['payload'];self.assertEqual(p['chosen']['members'],[choice])
        self.assertFalse(any(r['record_type']=='s1.transmission' for r in result.additions.records))

    def test_nonconforming_or_claimed_delivered_choice_preserved_with_failed_conformance(self):
        for value,state in [(-1,'selected'),(1,'delivered')]:
            d=draft();choice=action(d,value,state);ev=event(d,(choice,))
            result=record_decision(q('C-s2-plan','selection'),(q('C-s1-trace','response1'),),(choice,),contract('s2.threshold_action_selection'),ev,d)
            self.assertEqual(result.state,'partial');self.assertEqual(get(choice,d)['payload']['bindings'][1]['value']['value']['text'],str(value))
            self.assertIn('fail',[r['payload']['result'] for r in result.additions.records if r['record_type']=='s2.assessment'])

    def test_partial_exposure_survives_failure_and_unknown_admission(self):
        d=draft();info,issues=exposure_information((q('C-s2-receipts','exposure'),),d)
        self.assertEqual(len(info),1);self.assertEqual(info[0]['target'],q('C-s1-trace','response1')['target'])
        self.assertTrue(issues);self.assertFalse(any('grant' in r['record_type'] for r in d.records.snapshot().records))

    def test_negative_branch_and_evaluator_feedback_are_not_conflated(self):
        from crucis_causal.connections.model import Builder,contract as c1,unresolved
        from crucis_causal.connections.codec import dumps as s1bytes
        from crucis_causal.experiments.resolver import parse_snapshot,ReadAccess
        from crucis_causal.experiments.writer import S2RecordWriter
        for scalar,foreign in [('-0.25',False),('0.25',True)]:
            d=draft();b=Builder('synthetic scalar response source')
            view=d.read.resolver.lookup(desc('C-s1-trace')['package_id'],d.read.access,LIMITS)
            prop=q('C-s1-trace','action_proposition')
            if foreign:prop=b.add('proposition',{'predicate':contract('s4.hidden_quality_score'),'arguments':[],'conditioning':[],'scope':scope(b.producer)})
            response=b.output('quantity',{'quantity_kind':'s1.mean','subject':prop,'value':known(number(scalar)),
                'units':unresolved(),'conditioning':[],'basis':unresolved(),'procedure':b.producer,'associated_rule':known(contract('s2.mean_z_after_action'))})
            raw=s1bytes(b.package([response],external_packages=[{'package_id':view.package_id,'locator':unresolved(),'expected_digest':known(view.snapshot_digest),'access':'s1.supplied'}]))
            new=parse_snapshot(raw,LIMITS);base=d.records.base.with_view(new);other=S2RecordWriter(base,ReadAccess(frozenset(base._views)),LIMITS).context()
            info=qualified(response,new.package_id);chosen=action(other,-1,information=info);ev=event(other,(chosen,))
            result=record_decision(q('C-s2-plan','selection'),(info,),(chosen,),contract('s2.threshold_action_selection'),ev,other)
            self.assertEqual(result.state,'partial' if foreign else 'completed',result.diagnostics)
            if foreign:self.assertIn('s2.adaptive_input_unestablished',{i.code for i in result.diagnostics})

if __name__=='__main__':unittest.main()
