from crucis.core.paths import ROOT as DATA_ROOT
"""SC-1 whole-record goldens and release-boundary negatives (DLV-08/09)."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'tests'))
from crucis.connections import Builder, WireError, dumps, known, loads, number
from crucis.connections import api,core
from crucis.connections.domains import directed_link,finite_domain,graph_body,member
from crucis.connections.evidence import Resolver,capture_bytes,evidence_record
from crucis.connections.history import accounting_total
from crucis.connections.model import contract,scope,source,unknown_ref,unresolved
from crucis.connections.schema import BODY_FIELDS,PAYLOAD_FIELDS,schema
from crucis.connections.semantics import validate
from crucis.connections.services import CaptureSink,ContractRegistry,IdentityService,RecordBuffer


class IntegrationCases(unittest.TestCase):
    def goldens(self):return [loads(p.read_bytes()) for p in sorted((ROOT/'tests/audit_fixtures/sc1').glob('*.json'))]

    def test_complete_frozen_scenarios_and_all_record_body_types(self):
        cases=self.goldens();self.assertEqual({c['id'] for c in cases},{'c'+str(i) for i in range(1,10)}|{'h1','o1'})
        kinds=set();bodies=set()
        for case in cases:
            self.assertIs(case['synthetic'],True);report=validate(case['package']);self.assertTrue(report.ok,(case['id'],report.to_json()))
            for expected in case['expectations']:
                self.assertTrue(any(c.subject==expected['subject'] and c.contract==expected['contract'] and c.result==expected['result'] for c in report.checks),expected)
            for record in case['package']['records']:
                kinds.add(record['record_type'])
                if record['record_type']=='s1.output':bodies.add(record['payload']['output_type'])
            if case['id'] in ('c2','c7','c8'):
                self.assertFalse(any(r['record_type']=='s1.attempt' for r in case['package']['records']))
        self.assertEqual(kinds,set(PAYLOAD_FIELDS));self.assertEqual(bodies,set(BODY_FIELDS))

    def test_checked_in_schema_matches_generator_and_copies_cannot_change_validator(self):
        self.assertEqual(loads((ROOT/'crucis/connections/sc1.schema.json').read_bytes()),schema())
        edited=schema();edited['properties']['package_id']={'type':'integer'}
        p=self.goldens()[0]['package'];self.assertTrue(validate(p).ok)

    def test_empty_record_cannot_claim_evidence_foundation(self):
        b=Builder();root=evidence_record(b,[]);p=b.package([root]);report=validate(p)
        self.assertTrue(report.ok)
        with self.assertRaises(WireError):report.require(['s1.connection_minimum'])

    def test_unknown_relation_and_inconsistent_marks_do_not_gain_dag_or_encoding_guarantee(self):
        b=Builder();d=finite_domain(b,['A','B']);link=directed_link(d,0,1)
        link['relation']={'name':'foreign.opaque_relation','version':'1'};link['endpoint_marks']=['s1.arrowhead','s1.tail']
        g=b.output('graph',graph_body(d,[link],'dag'));report=validate(b.package([g]))
        self.assertEqual(next(c.result for c in report.checks if c.subject==g['target'] and c.contract=='s1.dag'),'unknown')
        link=directed_link(d,0,1);link['endpoint_marks']=['s1.circle','s1.circle'];bad=b.output('graph',graph_body(d,[link],'dag'))
        with self.assertRaises(WireError):validate(b.package([bad])).require(['s1.graph_encoding'],[bad['target']])

    def test_distinct_sub_float_temporal_coordinates_do_not_collapse(self):
        b=Builder();d=finite_domain(b,['X']);p=b.get(d)['payload'];var=p['members'][0]['variable']
        p['domain_kind']='absolute_temporal';p['coordinate_contract']=known(contract('absolute_seconds'))
        p['members']=[{'key':str(i),'variable':var,'coordinates':[{'dimension':contract('absolute_second'),
            'value':number('1.0000000000000000000000000000000000000'+str(i+1)),'reference':unresolved()}]} for i in range(2)]
        domain=b.add('domain',p);validate(b.package([domain])).require(['s1.domain'],[domain['target']])

    def test_parameter_sample_cannot_claim_another_graphs_subject(self):
        from crucis.connections.specimens import quantity
        b=Builder();d=finite_domain(b,['A','B']);a=b.output('graph',graph_body(d,[]));z=b.output('graph',graph_body(d,[]))
        q=quantity(b,z,'0.5','coefficient');c=b.output('collection',{'collection_kind':'sample_bank','member_contracts':[contract('graph')],
            'members':[{'key':'one','object':a,'multiplicity':'1','associated':[{'role':'s1.parameters','target':q}]}],
            'extent':scope(d),'ordering':'native_sequence','generation':unresolved(),'weights':[]})
        with self.assertRaises(WireError):validate(b.package([c])).require(['s1.collection_members'],[c['target']])

    def test_exact_count_ratio_checks_the_result_and_not_only_denominator(self):
        from crucis.connections.specimens import quantity
        b=Builder();d=finite_domain(b,['X']);n=quantity(b,d,1,'count');denom=quantity(b,d,2,'count')
        basis=b.add('relation',{'relation_contract':contract('ratio_components'),'endpoints':[{'role':'s1.numerator','target':n},
            {'role':'s1.denominator','target':denom}],'parameters':[],'scope':scope(d),'source':source()})
        q=b.output('quantity',{'quantity_kind':'s1.frequency','subject':d,'value':known(number('0.4')),
            'units':known({'name':'dimensionless','convention':contract('dimensionless')}),'conditioning':[],
            'basis':known(basis),'procedure':b.producer,'associated_rule':known(contract('count_ratio'))})
        with self.assertRaises(WireError):validate(b.package([q])).require(['s1.ratio_basis'],[q['target']])
        p=b.package([q]);next(r for r in p['records'] if r['id']==q['target'])['payload']['body']['value']=known(number('0.5'))
        validate(p).require(['s1.ratio_basis'],[q['target']])

    def test_mixed_member_contracts_are_alternatives_and_foreign_quantities_stay_unknown(self):
        from crucis.connections.specimens import quantity
        b=Builder();d=finite_domain(b,['X']);g=b.output('graph',graph_body(d,[]));q=quantity(b,d,'2.0','foreign_score')
        c=b.output('collection',{'collection_kind':'sequence','member_contracts':[contract('graph'),contract('quantity')],
            'members':[{'key':str(i),'object':obj,'multiplicity':'1','associated':[]} for i,obj in enumerate([g,q])],
            'extent':scope(d),'ordering':'native_sequence','generation':unresolved(),'weights':[]})
        report=validate(b.package([c]));report.require(['s1.collection_member_contract'],[c['target']])
        self.assertEqual(next(x.result for x in report.checks if x.subject==q['target'] and x.contract=='s1.quantity_value'),'unknown')

    def test_registered_route_does_not_give_recorded_adapter_an_invoke_path(self):
        from test_audit_connections_ports import setup,bind
        from crucis.connections.ports import recorded_connection,attached_connection
        b,s,sink=setup();reader=recorded_connection(b.producer,s)
        _,_,result=bind(b,s,reader,'direct');self.assertEqual(result.state,'rejected')
        observed=attached_connection(b.producer,s,lambda *args:None)
        self.assertIsNone(observed.invoke);self.assertEqual(observed.supported(),('describe','bind','observe'))

    def test_empty_graph_cannot_hide_mapping_twice(self):
        from crucis.connections.domains import mapped_graph,permutation
        b=Builder();target=finite_domain(b,['A','B']);payload=b.get(target)['payload'];payload['members']=list(reversed(payload['members']))
        native=b.add('domain',payload);mapping=permutation(b,native,target,[('1','1'),('0','0')])
        graph=b.output('graph',graph_body(native,[]));view=mapped_graph(b,b.package([graph]),graph,mapping)
        with self.assertRaises(WireError):mapped_graph(b,b.package([view]),view,mapping)

    def test_unknown_predecessor_withholds_order_without_inventing_an_edge(self):
        from test_audit_connections_history import event,request
        b=Builder();r,_=request(b);e=event(b,r,predecessors=[unknown_ref('event')]);report=validate(b.package([e]))
        self.assertEqual(next(c.result for c in report.checks if c.subject==e['target'] and c.contract=='s1.event_precedence'),'unknown')

    def test_two_checkpoint_branches_preserve_shared_ancestry_without_independence(self):
        from test_audit_connections_history import request,attempt
        b=Builder();r,policy=request(b);parent=attempt(b,r);branches=[attempt(b,r),attempt(b,r)];links=[]
        for child in branches:
            links.append(b.add('recovery',{'successor':child,'predecessor':parent,'recovery_kind':'branch',
                'request_relation':'same_request','state':unresolved(),'load':unresolved(),'reason':known('s1.branch'),
                'policy':policy,'source':source()}))
        p=b.package(links);report=validate(p);report.require(['s1.recovery_identity','s1.recovery_ancestry'])
        self.assertNotEqual(branches[0],branches[1]);self.assertEqual(len([r for r in p['records'] if r['record_type']=='s1.attempt']),3)
        self.assertFalse(any(c.contract=='s1.independent_trials' for c in report.checks))

    def test_malformed_native_numbers_and_file_declarations_preserve_legacy_evidence(self):
        from crucis.core.runs import RunRecord
        from crucis.connections.legacy import import_record,echo,encode
        for literal in ('unknown','1_0',' 1 '):
            with self.assertRaises(WireError):number(literal)
        record=RunRecord('fixture','i','real','failed',cost={'usd':'unknown'},files={'unfamiliar':'native declaration without a supported locator'})
        imported=import_record(record);report=validate(imported['package']);self.assertTrue(report.ok,report.to_json())
        self.assertTrue(imported['gaps']);self.assertEqual(encode(echo(imported['package'],imported['legacy_snapshot'])),encode(record))

    def test_unknown_usage_is_not_zero_and_profile_extension_blocks_only_its_claim(self):
        b=Builder();raw=capture_bytes(b,b'captured');root=evidence_record(b,[raw]);p=b.package([root])
        self.assertEqual(accounting_total(p,[])['state'],'unresolved')
        # Unknown optional/required extension handling is independently scoped by guarantee.
        p['extensions']=[{'contract':{'name':'foreign.unregistered','version':'1'},'affects':[root],
            'critical_for':['s1.evidence_foundation'],'payload':{'content_form':'inline_utf8','text':'native extension bytes'}}]
        records=RecordBuffer(b);ctx=api.ReadContext(unknown_ref('policy'),Resolver(p),IdentityService(),records)
        report=core.validate(p,[contract('evidence_foundation'),contract('available_snapshots')],ctx)
        self.assertEqual(report.claims_withheld,(contract('evidence_foundation'),));self.assertEqual(report.claims_satisfied,(contract('available_snapshots'),))

    def test_opt_in_cli_round_trip_and_no_in_repo_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp);case=self.goldens()[0];package=out/'package.json';package.write_bytes(dumps(case['package']))
            command=[sys.executable,'-B','-m','crucis.connections']
            result=subprocess.run(command+['validate',str(package),'--out',str(out/'validation.json'),'--profile','evidence_foundation'],
                cwd=ROOT,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertTrue(loads((out/'validation.json').read_bytes())['required_claims_established'])
            result=subprocess.run(command+['validate',str(package),'--out',str(out/'quantity-validation.json'),'--require','quantity_value'],cwd=ROOT,capture_output=True,text=True)
            self.assertEqual(result.returncode,2);self.assertFalse(loads((out/'quantity-validation.json').read_bytes())['required_claims_established'])
            result=subprocess.run(command+['schema','--out',str(ROOT/'crucis/connections/forbidden-runtime-output.json')],cwd=ROOT,capture_output=True,text=True)
            self.assertEqual(result.returncode,2);self.assertFalse((ROOT/'crucis/connections/forbidden-runtime-output.json').exists())


if __name__=='__main__':unittest.main()
