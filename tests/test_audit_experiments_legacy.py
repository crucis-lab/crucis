from crucis_causal.core.paths import ROOT as DATA_ROOT
"""S2-H source scope, durable imports and compatibility losses (DLV-08/09/10)."""
import copy
from dataclasses import replace
from pathlib import Path
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'tests'))
from test_audit_experiments_services import draft
from test_audit_experiments_wire import LIMITS
from crucis_causal.experiments import api,core,known,unknown
from crucis_causal.experiments.model import identity,qualified,contract,source
from crucis_causal.experiments.services import IdentityService,OccurrenceStore,LegacyRegistry
from crucis_causal.experiments.resolver import ReadAccess,parse_snapshot
from crucis_causal.experiments.operations import parameter
from crucis_causal.experiments import legacy
from crucis_causal.connections.model import Builder,contract as c1
from crucis_causal.connections.evidence import capture_bytes
from crucis_causal.connections.codec import dumps as s1bytes
from crucis_causal.connections.legacy import encode
from crucis_causal.core.runs import RunRecord
from crucis_causal.core.graph import Graph

def imported_context(tmp,value=None,fmt=None,kind='run_record'):
    value=value if value is not None else RunRecord('fixture','case','real','ok',graph=Graph.from_edges(2,[(0,1)]),
        notes={'replicates':[RunRecord('fixture','case','real','host_error')],'cost':None},confidence={(0,1):0.7})
    fmt=fmt or c1('legacy_runrecord_codec');b=Builder();blob=capture_bytes(b,s1bytes(encode(value)),format_contract=fmt)
    view=parse_snapshot(s1bytes(b.package([blob])),LIMITS);d=draft()
    d.records.identities=IdentityService(OccurrenceStore(tmp))
    # DraftContext uses the same explicit caller-owned identity service.
    d=replace(d,identities=d.records.identities)
    d.records.base=d.records.base.with_view(view);d.records.access=ReadAccess(frozenset(set(d.records.access.packages)|{view.package_id}))
    fields={'battery':known('source-a'),'version':known('captured-v1'),'projection':known(contract('s2.legacy_echo'))}
    if isinstance(value,RunRecord):fields.update(item=known(value.item),arm=known(value.arm),status=known(value.status))
    with d.records.begin(d.author,d.clock) as tx:
        config=parameter(tx,d,'legacy',fields);tx.commit()
    registry=LegacyRegistry();legacy.install(registry,d.author)
    ctx=api.LegacyContext(d,None,None,SimpleNamespace(legacy_views={}),registry)
    src=api.LegacyImportSource(identity(),(qualified(blob,view.package_id),),fmt,unknown())
    sc=api.LegacyImportScope(kind,config,())
    return ctx,src,sc,value

class LegacyCases(unittest.TestCase):
    def test_exact_echo_preserves_statuses_stages_confidence_cost_and_nested_occurrences(self):
        from crucis_causal.core.runs import STATUSES
        with tempfile.TemporaryDirectory() as tmp:
            for status in STATUSES:
                record=RunRecord('fixture','case','real',status,graph=Graph.from_edges(2,[(0,1)]) if status=='ok' else None,
                    stages=[('surviving',Graph.from_edges(2,[(1,0)]))],confidence={(0,1):0.8},cost=None,
                    notes={'replicates':[RunRecord('fixture','case','real','host_error')]})
                ctx,src,sc,_=imported_context(tmp,record);result=core.import_legacy(src,sc,ctx)
                self.assertEqual(result.state,'partial',result.diagnostics)
                back=core.project_legacy((result.value.receipt,),api.LegacyProjectionPolicy(contract('s2.legacy_echo'),sc.bindings,True),ctx)
                self.assertEqual(back.state,'completed',back.diagnostics)
                self.assertEqual(encode(record),encode(back.value.projections[0].record));self.assertFalse(back.value.losses)
                self.assertFalse(any(r['record_type'] in ('s1.request','s1.attempt','s2.trial_slot') for r in result.additions.records))

    def test_occurrence_reuse_preserves_ids_and_timestamps_and_rejects_changed_scope(self):
        with tempfile.TemporaryDirectory() as tmp:
            c,s,sc,_=imported_context(tmp);one=core.import_legacy(s,sc,c);two=core.import_legacy(s,sc,c)
            self.assertEqual(one.state,'partial',one.diagnostics);self.assertEqual(one.value,two.value);self.assertFalse(two.additions.records)
            before=c.draft.records.snapshot();changed=replace(s,source_identity=known({'authority':'fixture','namespace':'run','native_id':'changed','source':source(c.draft.author)}))
            result=core.import_legacy(changed,sc,c);self.assertEqual(result.state,'rejected');self.assertEqual(before,c.draft.records.snapshot())
            self.assertEqual(result.diagnostics[0].code,'s2.occurrence_input_conflict')
            new=core.import_legacy(replace(s,occurrence_id=identity()),sc,c);self.assertNotEqual(new.value.receipt,one.value.receipt)

    def test_source_scope_and_manifest_meanings_remain_encoded_without_fabricated_defaults(self):
        manifest={'battery':'source-b','hash':'reported-cached-value','items':[{'item_id':'case','n':8,'cluster':'cluster-1','family':'native',
            'arms':['real','not-executed'],'files':{'source':{'path':'unavailable.csv','sha256':'reported-old'}},'meta':{}}]}
        with tempfile.TemporaryDirectory() as tmp:
            c,s,sc,_=imported_context(tmp,manifest,contract('s2.legacy_manifest_codec'),'battery_manifest');result=core.import_legacy(s,sc,c)
            self.assertEqual(result.state,'partial',result.diagnostics)
            echoed=core.project_legacy((result.value.receipt,),api.LegacyProjectionPolicy(contract('s2.legacy_echo'),sc.bindings,True),c)
            self.assertEqual(echoed.value.projections[0].record,manifest)
            p=c.draft.records.get(result.value.receipt)['payload'];self.assertEqual(p['original_identity']['state'],'unresolved')
            self.assertEqual(p['interpretations'],[]);self.assertGreater(len(p['gaps']),0)

    def test_no_implicit_file_capture_pickle_or_unsupported_version(self):
        with tempfile.TemporaryDirectory() as tmp:
            c,s,sc,_=imported_context(tmp)
            with patch('crucis_causal.connections.evidence.capture_file',side_effect=AssertionError('no file reads')):
                result=core.import_legacy(s,sc,c);self.assertEqual(result.state,'partial',result.diagnostics)
            before=c.draft.records.snapshot()
            for changed in [replace(s,legacy_contract=contract('foreign.pickle')),replace(s,captured_sources=(dict(s.captured_sources[0],binding='internal'),))]:
                self.assertEqual(core.import_legacy(changed,sc,c).state,'rejected');self.assertEqual(before,c.draft.records.snapshot())
            with self.assertRaises(ValueError):__import__('crucis_causal.connections.legacy',fromlist=['decode']).decode({'legacy_type':'pickle','data':'unsafe'})

    def test_incompatible_source_labels_and_unsupported_interpretations_reject_atomically(self):
        with tempfile.TemporaryDirectory() as tmp:
            c,s,sc,_=imported_context(tmp);before=c.draft.records.snapshot()
            result=core.import_legacy(s,replace(sc,interpretation_claims=(contract('s2.independent_repetitions'),)),c)
            self.assertEqual(result.state,'rejected');self.assertEqual(before,c.draft.records.snapshot())

    def test_repeated_score_keys_reject_lossless_echo_without_silent_best_or_last(self):
        with tempfile.TemporaryDirectory() as tmp:
            c,s,sc,_=imported_context(tmp);a=core.import_legacy(s,sc,c);b=core.import_legacy(replace(s,occurrence_id=identity()),sc,c)
            out=core.project_legacy((a.value.receipt,b.value.receipt),api.LegacyProjectionPolicy(contract('s2.legacy_echo'),sc.bindings,True),c)
            self.assertEqual(out.state,'rejected');self.assertEqual(out.diagnostics[0].code,'s2.legacy_repeated_key_collision')
            narrow=core.project_legacy((a.value.receipt,),api.LegacyProjectionPolicy(contract('s2.legacy_explicit_view'),sc.bindings,True),c)
            self.assertEqual(narrow.state,'rejected');self.assertEqual(narrow.diagnostics[0].code,'s2.legacy_narrow_view_is_lossy')

    def test_missing_capture_and_persistent_store_withhold_import(self):
        with tempfile.TemporaryDirectory() as tmp:
            c,s,sc,_=imported_context(tmp)
            self.assertEqual(core.import_legacy(replace(s,captured_sources=()),sc,c).state,'rejected')
            c=replace(c,draft=replace(c.draft,identities=IdentityService()))
            self.assertEqual(core.import_legacy(s,sc,c).diagnostics[0].code,'s2.persistent_occurrence_store_required')

    def test_explicit_narrow_compatibility_view_calls_s1_and_reports_losses(self):
        from crucis_causal.connections import api as a1
        from crucis_causal.connections.domains import finite_domain,permutation,graph_body,directed_link
        from crucis_causal.connections.model import scope as sc1,unresolved
        from crucis_causal.experiments.model import scope
        with tempfile.TemporaryDirectory() as tmp:
            c,_,config,_=imported_context(tmp);b=Builder();dom=finite_domain(b,['A','B']);m=permutation(b,dom,dom,[('0','0'),('1','1')])
            graph=b.output('graph',graph_body(dom,[directed_link(dom,0,1)]));raw=capture_bytes(b,b'explicit reported status')
            status=b.add('assessment',{'subjects':[graph],'rule':c1('legacy_status_explicit'),'parameters':[],'basis':[raw],
                'conclusions':[{'facet':'s1.legacy_status','value':known('ok',[raw]),'supporting':[raw],'disputed':[]}],'cutoff':[raw],'revises':[]})
            labels=a1.LegacyBinding(b.producer,'case','real',dom,'original',known(m),unresolved(),c1('legacy_runrecord_codec'))
            selection=a1.LegacySelection((graph,),graph,status,m,(),(),labels,c1('legacy_projection_explicit'))
            view=parse_snapshot(s1bytes(b.package([graph])),LIMITS);d=c.draft
            d.records.base=d.records.base.with_view(view);d.records.access=ReadAccess(frozenset(set(d.records.access.packages)|{view.package_id}))
            g=qualified(graph,view.package_id)
            with d.records.begin(d.author,d.clock) as tx:
                rule=tx.add('selection_rule',{'rule':contract('s2.legacy_explicit_view'),'population':config.bindings,'inputs':[g],'parameters':[],
                    'randomization':unknown(),'stopping':unknown(),'source':source(d.author)});tx.commit()
            c.s1_services.legacy_views[rule['target']]=legacy.CompatibilityView(view,selection)
            out=core.project_legacy((g,),api.LegacyProjectionPolicy(contract('s2.legacy_explicit_view'),rule,False),c)
            self.assertEqual(out.state,'completed',out.diagnostics);self.assertTrue(out.value.losses)
            self.assertEqual(out.value.projections[0].record.graph.directed,frozenset({(0,1)}))
            self.assertEqual(core.project_legacy((g,),api.LegacyProjectionPolicy(contract('s2.legacy_explicit_view'),rule,True),c).state,'rejected')

    @unittest.skipUnless((DATA_ROOT/'runs/ab06').is_dir(),'recorded sources absent')
    def test_all_eight_recorded_adapters_echo_through_s2_without_run(self):
        from crucis_causal.core import adapter,battery
        from crucis_causal.run import AUDITS
        names=adapter.names();self.assertEqual(len(names),8)
        with tempfile.TemporaryDirectory() as tmp:
            for name in names:
                with self.subTest(adapter=name):
                    spec=next(v for v in AUDITS.values() if v['system']==name);ad=adapter.get(name,**spec.get('adapter_kw',{}))
                    item=battery.get(spec['battery']).items[0]
                    with patch.object(ad,'run',side_effect=AssertionError('no native execution')):
                        expected=ad.recorded(item,spec['arms'][0]);c,s,sc,_=imported_context(tmp,expected)
                        result=core.import_legacy(s,sc,c);self.assertEqual(result.state,'partial',result.diagnostics)
                        echo=core.project_legacy((result.value.receipt,),api.LegacyProjectionPolicy(contract('s2.legacy_echo'),sc.bindings,True),c)
                        self.assertEqual(echo.state,'completed',echo.diagnostics);self.assertEqual(encode(echo.value.projections[0].record),encode(expected))

if __name__=='__main__':unittest.main()
