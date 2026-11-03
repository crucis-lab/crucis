from crucis_causal.core.paths import ROOT as DATA_ROOT
"""S2-B transactional, registry and scoped-profile acceptance (DLV-08/09)."""
import copy
from dataclasses import replace
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'tests'))
from test_audit_experiments_wire import resolver,context,local,desc,LIMITS
from crucis_causal.experiments import ServiceError,known,unknown
from crucis_causal.experiments import api,core
from crucis_causal.experiments.model import source,scope,contract,qualified,digest,identity
from crucis_causal.experiments.operations import atomic,assessment
from crucis_causal.experiments.writer import S2RecordWriter
from crucis_causal.experiments.services import IdentityService,OccurrenceStore,FamilyRegistry,AssessmentRegistry,ProjectionRegistry

def draft():
    c=context('A-s2-plan');w=S2RecordWriter(c.resolver,c.access,LIMITS);return w.context()
def subject():return qualified(local('A-s2-plan','task'),desc('A-s2-plan')['package_id'])
def claim(name='s2.preserve',families=()):
    return {'profile':contract(name),'families':list(families),'scope':scope(subject()),'evidence':[],'limits':[]}
def ac(d=None,procedures=None):
    d=d or draft();return api.PlanAssessmentContext(d.read,d,procedures or AssessmentRegistry())
def requirement(d):return {'predicate':contract('s2.explicit_requirement'),'subjects':[subject()],'parameters':[],'scope':scope(subject()),'source':source(d.author)}

class ServiceCases(unittest.TestCase):
    def test_new_writer_records_actual_s2_code_identity_not_default_s1_manifest(self):
        d=draft();r=d.records.get(d.author);ref=r['payload']['implementation']['value']['artifact']
        s=d.read.resolver.record(ref,d.read.active_package,d.read.access,LIMITS)
        manifest=json.loads(s.record['payload']['content']['text'])
        self.assertIn('writer.py',manifest);self.assertIn('catalog.json',manifest);self.assertIn('core.py',manifest)
        self.assertEqual(s.record['payload']['format']['value']['name'],'s2.code_identity_manifest')

    def test_no_add_without_transaction_and_rejected_operation_rolls_back(self):
        d=draft();before=d.records.view().source_bytes
        with self.assertRaises(ServiceError):d.records.add('requirement',requirement(d))
        def broken(tx):tx.add('requirement',requirement(d));raise RuntimeError('foreign observer handler')
        result=atomic(d,broken)
        self.assertEqual(result.state,'rejected');self.assertFalse(result.additions.records);self.assertEqual(d.records.view().source_bytes,before)
        self.assertEqual(result.diagnostics[0].code,'s2.observer_contract_error')

    def test_commit_has_immutable_occurrence_and_distinct_frozen_package_identity(self):
        d=draft()
        with d.records.begin(d.author,d.clock) as tx:
            ref=tx.add('requirement',requirement(d));delta=tx.commit()
        one=d.records.frozen([ref]);two=d.records.frozen([ref])
        self.assertNotEqual(one.package_id,two.package_id);self.assertEqual(one.records,two.records)
        self.assertEqual(len(delta.records),1)
        with self.assertRaises(ServiceError):
            with d.records.begin(d.author,d.clock) as tx:tx.add('requirement',requirement(d),ref['target'])

    def test_invalid_commit_discards_all_new_records_and_dependencies(self):
        d=draft();before=d.records.snapshot()
        with self.assertRaises(ServiceError):
            with d.records.begin(d.author,d.clock) as tx:
                p=requirement(d);p['subjects']=[{'binding':'internal','target':identity(),'target_type':'s2.requirement'}]
                tx.add('requirement',p);tx.commit()
        self.assertEqual(before,d.records.snapshot())

    def test_nested_transactions_and_wrong_clock_or_author_rejected(self):
        d=draft()
        with d.records.begin(d.author,d.clock):
            with self.assertRaises(ServiceError):d.records.begin(d.author,d.clock)
        with self.assertRaises(ServiceError):d.records.begin(subject(),d.clock)
        with self.assertRaises(ServiceError):d.records.begin(d.author,object())

    def test_occurrence_identity_persisted_and_conflicts_not_content_deduplication(self):
        with tempfile.TemporaryDirectory() as tmp:
            ids=IdentityService(OccurrenceStore(tmp));occ=ids.allocate();bound=digest(b'exact inputs')
            one=ids.import_once(occ,bound,lambda:{'record_id':identity()})
            two=IdentityService(OccurrenceStore(tmp)).import_once(occ,bound,lambda:self.fail('must not create twice'))
            self.assertEqual(one,two)
            with self.assertRaises(ServiceError):ids.import_once(occ,digest(b'changed'),lambda:{})
            other=ids.import_once(ids.allocate(),bound,lambda:{'record_id':identity()});self.assertNotEqual(one,other)
            with self.assertRaises(ServiceError):ids.store.import_once('../outside',bound,lambda:{})
        with self.assertRaises(ServiceError):IdentityService().import_once(identity(),digest(b'x'),lambda:{})

    def test_exact_registry_no_implicit_version_or_duplicate_registration(self):
        d=draft();registry=FamilyRegistry();c=contract('toy.domain')
        reader=api.FamilyReader(c,d.author,contract('s2.task_definition'),contract('toy.interpreted'),lambda r,ctx:api.PlanOp('completed',api.InterpretedValue(contract('toy.interpreted'),(r,),(),())))
        registry.register(reader);c['version']='changed'
        self.assertIsNotNone(registry.lookup(contract('toy.domain')))
        self.assertIsNone(registry.lookup(contract('toy.domain','9')))
        with self.assertRaises(ServiceError):registry.register(replace(reader,contract=contract('toy.domain')))
        with self.assertRaises(ServiceError):registry.register(contract('foreign.handler'))

    def test_scientific_native_projection_pair_is_not_a_name_coincidence(self):
        d=draft();r=ProjectionRegistry();s=contract('task.structure');n=contract('native.learn');out=contract('response.graph')
        p=api.ProjectionProcedure(s,n,out,'recorded',d.author,lambda *args:None);r.register(p)
        self.assertIsNotNone(r.lookup(s,n,out,'recorded'));self.assertIsNone(r.lookup(s,s,out,'recorded'))
        self.assertIsNone(r.lookup(s,n,out,'direct'))

    def test_preserve_profile_and_missing_interpretation_are_independent(self):
        d=draft();ctx=ac(d);result=core.assess((subject(),),(claim(),claim('s2.interpret',(contract('foreign.domain'),))),ctx)
        self.assertEqual(result.state,'completed');self.assertEqual(len(result.value.satisfied),1);self.assertEqual(len(result.value.withheld),1)
        self.assertIn('s2.family_reader_unavailable',{i.code for i in result.value.issues})
        self.assertFalse(any(r['record_type']=='s1.attempt' for r in result.additions.records))

    def test_interpretation_requires_exact_reader_input_output_and_scope(self):
        d=draft();c=contract('toy.domain');out=contract('toy.interpreted')
        reader=api.FamilyReader(c,d.author,contract('s2.task_definition'),out,lambda ref,ctx:api.PlanOp('completed',api.InterpretedValue(out,(ref,),(),())))
        d.read.registry.register(reader)
        result=core.assess((subject(),),(claim('s2.interpret',(c,)),),ac(d))
        self.assertEqual(len(result.value.satisfied),1)
        # Correct version but wrong interpretation target is not support.
        e=draft();e.read.registry.register(replace(reader,input_contract=contract('s2.case_revision')))
        result=core.assess((subject(),),(claim('s2.interpret',(c,)),),ac(e));self.assertFalse(result.value.satisfied)

    def test_known_false_predicate_completes_operation_without_passing_profile(self):
        d=draft();c=contract('toy.domain');out=contract('toy.interpreted')
        d.read.registry.register(api.FamilyReader(c,d.author,contract('s2.task_definition'),out,lambda r,ctx:api.PlanOp('completed',api.InterpretedValue(out,(r,),(),()))))
        procedures=AssessmentRegistry()
        def false(roots,evidence,parameters,ctx):
            ref=assessment(ctx.draft.records,ctx,contract('s2.bind_inputs_sources'),roots,evidence,'fail')
            return api.PlanOp('completed',(ref,))
        procedures.register(api.AssessmentProcedure(contract('s2.bind_inputs_sources'),d.author,false))
        result=core.assess((subject(),),(claim('s2.bind_inputs_sources',(c,)),),ac(d,procedures))
        self.assertEqual(result.state,'completed');self.assertFalse(result.value.satisfied)
        results=[r['payload']['result'] for r in result.additions.records if r['record_type']=='s2.assessment']
        self.assertEqual(results,['fail','fail'])

    def test_runtime_outcomes_and_context_scope_cannot_claim_success_implicitly(self):
        with self.assertRaises(ServiceError):api.PlanOp('rejected',value='kept',diagnostics=(api.PlanIssue('s2.no'),))
        with self.assertRaises(ServiceError):api.PlanOp('partial')
        d=draft()
        with self.assertRaises(ServiceError):api.PlanAssessmentContext(replace(d.read,active_package=None),d,AssessmentRegistry())
        self.assertEqual(core.assess((),(claim(),),ac(d)).state,'rejected')

    def test_profile_does_not_expand_scope_to_unassessed_subject(self):
        d=draft();c=claim();c['scope']['subjects']=[qualified(local('A-s2-plan','subject'),desc('A-s2-plan')['package_id'])]
        result=core.assess((subject(),),(c,),ac(d));self.assertEqual(result.state,'rejected');self.assertFalse(result.additions.records)

    def test_unknown_critical_extension_kept_without_interpretation_claim(self):
        d=draft()
        from crucis_causal.experiments.model import reference
        with d.records.begin(d.author,d.clock) as tx:
            ref=tx.add('requirement',requirement(d));r=tx.get(ref);r['id']=identity();ref=reference(r['id'],'requirement')
            r['extensions']=[{'contract':contract('foreign.opaque'),'affects':[ref],'critical_for':['s2.interpret'],'payload':{'content_form':'inline_utf8','text':'opaque'}}]
            tx.ingest([r]);tx.commit()
        c=claim('s2.interpret');c['scope']=scope(ref)
        result=core.assess((ref,),(c,),ac(d));self.assertFalse(result.value.satisfied)
        self.assertIn('s2.critical_extension_uninterpreted',{i.code for i in result.value.issues})

    def test_invalid_utc_clock_rolls_back_without_native_failure_attribution(self):
        from crucis_causal.experiments.services import ClockService
        class BadClock(ClockService):
            def now(self):return {'time_type':'utc_instant','value':'not-a-time','precision':'second','clock':unknown(),'uncertainty_seconds':unknown()}
        d=draft();d.records.clock=BadClock();bad=replace(d,clock=d.records.clock)
        result=atomic(bad,lambda tx:(tx.add('requirement',requirement(bad)),(),()))
        self.assertEqual(result.state,'rejected');self.assertEqual(result.diagnostics[0].code,'s2.invalid_utc_instant')

if __name__=='__main__':unittest.main()
