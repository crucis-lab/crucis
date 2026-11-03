from crucis_causal.core.paths import ROOT as DATA_ROOT
"""S2-C case, membership, question/reference and resolution cases (DLV-08/09)."""
import copy
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'tests'))
from test_audit_experiments_wire import local,desc,package,record,context,MANIFEST,RAW
from test_audit_experiments_services import draft,ac,claim,subject
from crucis_causal.experiments import core,ServiceError
from crucis_causal.experiments.contracts import inspect,install
from crucis_causal.experiments.model import qualified,reference,identity,source,scope,known,not_applicable,index,contract
from crucis_causal.experiments.operations import get

def q(name,alias):return qualified(local(name,alias),desc(name)['package_id'])

class DefinitionCases(unittest.TestCase):
    def test_accepted_static_collection_membership_and_task_invariants(self):
        d=draft()
        for name,alias in [('A-s2-receipts','collection'),('A-s2-receipts','membership'),('A-s2-plan','task'),('A-s2-plan','response'),('A-s2-plan','coverage')]:
            result=inspect(q(name,alias),d);self.assertEqual(result.result,'pass',(name,result))

    def test_partial_contested_reference_keeps_both_sources_and_unknown_original_history(self):
        d=draft();p=package('B-s2-plan')
        self.assertFalse(any(r['record_type']=='s2.trial_slot' for r in p['records']))
        ev=get(q('B-s2-receipts','evaluation'),d)['payload'];self.assertEqual(len(ev['references']),2)
        self.assertEqual(inspect(q('B-s2-plan','coverage'),d).result,'unknown')
        self.assertNotEqual(q('B-s2-plan','ref_left')['target'],q('B-s2-plan','ref_right')['target'])
        result=core.resolve_slots((q('B-s2-plan','case_slot'),),(),d)
        self.assertEqual(result.state,'partial');self.assertFalse(result.value.selected)

    def test_unique_slot_resolution_uses_declared_source_and_retains_receipt(self):
        d=draft();result=core.resolve_slots((q('A-s2-plan','case_slot'),),(q('A-s2-receipts','case'),),d)
        self.assertEqual(result.state,'completed');self.assertEqual(result.value.selected,(q('A-s2-receipts','case'),))
        receipt=get(result.value.receipt,d)['payload'];self.assertEqual(receipt['entries'][0]['rule'],contract('s2.explicit_single_selection'))

    def test_multiple_or_wrong_source_candidates_not_latest_best_or_empty_success(self):
        d=draft()
        multiple=core.resolve_slots((q('D-s2-plan','case_slot'),),(q('D-s2-receipts','case'),q('D-s2-receipts','case1')),d)
        self.assertEqual(multiple.state,'partial');self.assertFalse(multiple.value.selected)
        self.assertEqual(multiple.diagnostics[0].code,'s2.ambiguous_resolution')
        wrong=core.resolve_slots((q('A-s2-plan','case_slot'),),(q('B-s2-receipts','case'),),d)
        self.assertEqual(wrong.state,'partial');self.assertFalse(wrong.value.selected)
        duplicate=core.resolve_slots((q('A-s2-plan','case_slot'),),(q('A-s2-receipts','case'),q('A-s2-receipts','case')),d)
        self.assertEqual(duplicate.state,'rejected')

    def test_bare_predicate_has_no_implicit_selection_rule(self):
        d=draft();result=core.resolve_slots((q('A-s2-plan','case_resolution'),),(q('A-s2-receipts','case'),),d)
        self.assertEqual(result.state,'partial');self.assertEqual(result.diagnostics[0].code,'s2.resolution_rule_unavailable')

    def test_complete_collection_detects_wrong_member_owner(self):
        d=draft()
        with d.records.begin(d.author,d.clock) as tx:
            cref=reference(identity(),'collection_release')
            m=tx.add('membership',{'collection':q('A-s2-receipts','collection'),'case':q('A-s2-receipts','case'),
                'selection_slot':not_applicable(),'role':'s2.test_member','basis':[],'source':source(d.author)})
            tx.add('collection_release',{'collection_key':{'namespace':'test','key':'release'},'previous':not_applicable(),
                'membership':index([m]),'selection':not_applicable(),'ordering':'ordered','multiplicity':'unique_case_revisions',
                'scope':scope(m),'exposure':index([], 'not_examined'),'source':source(d.author)},cref['target']);tx.commit()
        result=inspect(cref,d);self.assertEqual(result.result,'fail');self.assertIn('s2.membership_wrong_collection',{i.code for i in result.issues})

    def test_duplicate_required_response_role_is_known_false_not_missing_output(self):
        d=draft();original=get(q('A-s2-plan','response'),d)['payload'];original=copy.deepcopy(original)
        original['coverage']=q('A-s2-plan','coverage')
        for deliverable in original['deliverables']:
            deliverable['scope']['subjects']=[q('A-s1-definitions','domain')];deliverable['parameters']=[q('A-s2-plan','response_group')]
        original['parameters']=[q('A-s2-plan','response_group')];original['source']=source(d.author)
        original['deliverables'].append(copy.deepcopy(original['deliverables'][0]))
        with d.records.begin(d.author,d.clock) as tx:r=tx.add('response_contract',original);tx.commit()
        self.assertEqual(inspect(r,d).result,'fail')
        install(d.read.registry,d.author);c=claim('s2.interpret',(contract('s2.response_contract'),));c['scope']=scope(r)
        result=core.assess((r,),(c,),ac(d));self.assertFalse(result.value.satisfied)
        self.assertEqual(get(result.value.assessments[-1],d)['payload']['result'],'fail')

    def test_ingest_cannot_change_record_identity_from_immutable_base(self):
        d=draft();r=get(q('A-s2-plan','subject'),d);r['payload']['requirements']=[]
        with self.assertRaises(ServiceError):
            with d.records.begin(d.author,d.clock) as tx:tx.ingest([r]);tx.commit()

    def test_response_omission_scope_and_valid_order_alternatives(self):
        from crucis_causal.connections.model import Builder,contract as c1,known as k1
        from crucis_causal.connections.domains import finite_domain,directed_link,graph_body,member
        from crucis_causal.connections.codec import dumps as bytes1
        from crucis_causal.experiments.resolver import parse_snapshot,ReadAccess
        from crucis_causal.experiments.api import PlanReadContext
        from crucis_causal.experiments.services import FamilyRegistry
        from crucis_causal.experiments.responses import graph_adjacency,order_admissible
        b=Builder();dom=finite_domain(b,['A','B','C']);graph=b.output('graph',graph_body(dom,[directed_link(dom,0,2)],'dag'))
        openbody=graph_body(dom,[directed_link(dom,0,2)],'dag');openbody['omission']['within_coverage']='unreported'
        opened=b.output('graph',openbody)
        orders=[]
        for seq in [[0,1,2],[1,0,2],[0,2,1]]:
            orders.append(b.output('order',{'predicate':c1('precedes'),'domain':dom,'representation':'sequence',
                'sequence':[member(dom,i) for i in seq],'pairs':[],'coverage':scope(dom),'omission':'s1.unreported'}))
        view=parse_snapshot(bytes1(b.package([graph,opened,*orders])),context('A-s2-plan').limits)
        r=context('A-s2-plan').resolver.with_view(view)
        ctx=PlanReadContext(context('A-s2-plan').limits,r,FamilyRegistry(),ReadAccess(frozenset(r._views)),view.package_id)
        self.assertEqual(graph_adjacency(graph,'0','2',ctx),'assert')
        self.assertEqual(graph_adjacency(graph,'0','1',ctx),'deny')
        self.assertEqual(graph_adjacency(opened,'0','1',ctx),'unreported')
        self.assertEqual(graph_adjacency(graph,'0','0',ctx),'unreported')
        expected=['valid','valid','invalid']
        self.assertEqual([order_admissible(o,dom,[('0','2'),('1','2')],ctx) for o in orders],expected)

if __name__=='__main__':unittest.main()
