from crucis.core.paths import ROOT as DATA_ROOT
"""Optional ports, authority and consumer compatibility (DLV-08, DLV-09)."""
from dataclasses import replace
import copy
import hashlib
from pathlib import Path
import sys
import tempfile
import unittest
import uuid
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'tests'))
from crucis.connections import Builder, WireError, known
from crucis.connections import api, core
from crucis.connections.domains import directed_link, finite_domain, graph_body, permutation
from crucis.connections.evidence import Resolver, capture_bytes, evidence_record
from crucis.connections.legacy import echo, encode, import_record, project
from crucis.connections.model import contract, not_applicable, scope, source, unknown_ref, unresolved
from crucis.connections.ports import make_connection, prepared_connection, recorded_connection, supplied_connection, with_decoder
from crucis.connections.semantics import validate
from crucis.connections.services import IdentityService
from crucis.connections.services import (ActionChannel,CaptureSink,ContractRegistry,HandleRegistry,MappingRegistry,
    RecordBuffer,RuntimeAuthority,execution_binding,delivery_binding,cancellation_binding)
from crucis.connections.store import PackageStore
from test_audit_connections_history import request,attempt


def setup(store=None):
    b=Builder();records=RecordBuffer(b);registry=ContractRegistry();ids=IdentityService(store)
    services=api.AdapterServices(ids,records,registry);sink=CaptureSink(records,ids)
    return b,services,sink


def read_context(b,services,policy):
    return api.ReadContext(policy,Resolver(b.package([b.producer])),services.identities,services.records)


def bind(b,services,ports,route_kind='recorded',dependencies=(),inventory=None):
    r,policy=request(b,route='s1.'+route_kind);operation=contract('fixture_discovery')
    services.registry.register_route(operation,route_kind,dependencies=dependencies)
    route=api.RouteSpec(route_kind,contract('fixture_transport'),operation)
    result=ports.bind(r,api.PresentedBundle((),policy),route,inventory or api.DependencyInventory((),scope(r)),api.BindContext(services,scope(r)))
    return r,policy,result


class PortCases(unittest.TestCase):
    def test_recorded_only_and_pure_description_have_no_execution_methods(self):
        b,s,sink=setup();ports=recorded_connection(b.producer,s)
        self.assertIsNone(ports.invoke);self.assertIsNone(ports.cancel);self.assertIsNone(ports.prepare)
        self.assertEqual(ports.verify_declaration().ports,('describe','bind','read'))
        self.assertEqual(make_connection(b.producer,s).supported(),('describe',))
        r,policy,bound=bind(b,s,ports);self.assertEqual(bound.value.readiness,'ready')
        raw=capture_bytes(b,b'original native bytes',format_contract=contract('fixture_bytes'))
        spec=api.SourceSpec((raw,),(contract('fixture_bytes'),),str(uuid.uuid4()),unresolved())
        result=ports.read(spec,read_context(b,s,policy),sink)
        self.assertEqual(result.state,'completed')
        self.assertEqual(Resolver(b.package(result.value.artifacts)).bytes(result.value.artifacts[0]),b'original native bytes')

    def test_unknown_and_absent_dependency_narrow_readiness_without_import(self):
        b,s,sink=setup();ports=recorded_connection(b.producer,s);dependency=b.producer
        _,_,bound=bind(b,s,ports,dependencies=[dependency]);self.assertEqual(bound.value.readiness,'unresolved')
        self.assertTrue(bound.diagnostics)
        b,s,sink=setup();ports=recorded_connection(b.producer,s)
        inventory=api.DependencyInventory((api.DependencyEntry(dependency,known(False),unresolved()),),scope())
        _,_,bound=bind(b,s,ports,dependencies=[dependency],inventory=inventory)
        self.assertEqual(bound.value.readiness,'not_ready')
        self.assertTrue(all(s.records.get(g)['record_type']=='s1.gap' for g in bound.diagnostics))

    def test_prepared_process_is_only_argv_descriptor(self):
        b,s,sink=setup();inv={'kind':'process','executable':'supplied-fixture','argv':['literal;not-a-shell','$(literal)'],
            'cwd':unknown_ref('location'),'environment_policy':unknown_ref('policy')}
        ports=prepared_connection(b.producer,s,inv);_,policy,bound=bind(b,s,ports,'prepared_command')
        result=ports.prepare(bound.value,api.PrepareContext(policy,s.identities),sink)
        self.assertEqual(result.value.invocation,inv);self.assertIsNone(ports.invoke)
        self.assertEqual(len([x for x in s.records.snapshot() if x['record_type']=='s1.attempt']),0)

    def test_execution_exact_grant_and_no_implicit_retry(self):
        b,s,sink=setup();authority=RuntimeAuthority();called=[]
        inv={'kind':'function','entrypoint':contract('fixture_function'),'arguments':[]}
        def executor(descriptor,ctx,capture):
            called.append(descriptor);raw=capture.capture(b'fixture result')
            return api.NativeHandle(ctx.attempt,unresolved(),object(),(raw,),())
        ports=supplied_connection(b.producer,s,inv,authority=authority,executor=executor)
        r,policy,bound=bind(b,s,ports,'direct');a=attempt(b,r)
        spec=ports.prepare(bound.value,api.PrepareContext(policy,s.identities),sink).value
        auth=b.add('authority_evidence',{'actor':b.producer,'policy':policy,'operation':spec.route.operation,
            'subjects':[a],'permitted_effects':['s1.cpu'],'decision':'permitted','validity':scope(a),'source':source()})
        grant=api.ExecutionGrant(r,a,(spec.route.operation,),('s1.cpu',),(),(policy,),auth,object())
        ctx=api.ExecutionContext(grant,a,HandleRegistry())
        self.assertEqual(ports.invoke(spec,ctx,sink).state,'rejected');self.assertEqual(called,[])
        token=authority.issue('execute',execution_binding(grant));grant=replace(grant,runtime_capability=token);ctx=replace(ctx,grant=grant)
        self.assertEqual(ports.invoke(spec,ctx,sink).state,'completed');self.assertEqual(len(called),1)
        self.assertEqual(ports.invoke(spec,ctx,sink).state,'rejected');self.assertEqual(len(called),1)
        wrong=replace(grant,effects=('s1.network',));self.assertEqual(ports.invoke(spec,replace(ctx,grant=wrong),sink).state,'rejected')

    def test_reconnect_reuses_handle_not_attempt_identity(self):
        b,s,_=setup();r,_=request(b);a=attempt(b,r);registry=HandleRegistry()
        native={'authority':'fixture','namespace':'job','native_id':'one','source':source()}
        handle=api.NativeHandle(a,known(native),object(),(),());registry.attach(handle)
        self.assertIs(registry.reconnect(native),handle)
        with self.assertRaises(WireError):registry.attach(api.NativeHandle(attempt(b,r),known(native),object(),(),()))

    def test_parser_failure_preserves_source_and_returned_diagnostics_resolve(self):
        b,s,_=setup();raw=capture_bytes(b,b'{broken native JSON');reader=contract('fixture_json')
        ports=with_decoder(recorded_connection(b.producer,s),b.producer,s,reader=reader,targets=(contract('graph'),),
            decoder=lambda raw,req,ctx:__import__('json').loads(raw))
        resolver=Resolver(b.package([raw]));ctx=api.DecodeContext(resolver,MappingRegistry(resolver),s.identities)
        result=ports.decode(api.ArtifactView(raw,(),reader,scope(raw)),api.DecodeRequest(contract('graph'),(),(),(),'interpret'),ctx)
        self.assertEqual(result.state,'partial');self.assertEqual(result.value.outputs,())
        self.assertEqual(resolver.bytes(raw),b'{broken native JSON')
        self.assertTrue(all(s.records.get(g)['record_type']=='s1.gap' for g in result.diagnostics))

    def test_all_statuses_and_nested_replicate_selection_echo_exactly(self):
        from crucis.core.graph import Graph
        from crucis.core.runs import RunRecord,STATUSES
        for status in STATUSES:
            rec=RunRecord('fixture','i','real',status,graph=Graph.from_edges(2,[(0,1)]) if status=='ok' else None,
                confidence={(1,0):0.8},notes={'file_read':'seed-exact-path','replicates':[RunRecord('fixture','i','real','host_error')]})
            imported=import_record(rec);back=echo(imported['package'],imported['legacy_snapshot'])
            self.assertEqual(encode(back),encode(rec));self.assertEqual(len(back.replicates),1)
            self.assertTrue(validate(imported['package']).ok)

    def test_historical_digest_mismatch_is_new_evidence_not_repinned_history(self):
        from crucis.core.runs import RunRecord
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'result.json';path.write_bytes(b'changed')
            rec=RunRecord('fixture','i','real','failed',files={'result':{'path':str(path),'sha256':hashlib.sha256(b'old').hexdigest()}})
            imported=import_record(rec,roots=[tmp]);self.assertTrue(imported['gaps'])
            self.assertEqual(echo(imported['package'],imported['legacy_snapshot']).files,rec.files)
            self.assertTrue(validate(imported['package']).ok)

    def test_core_import_occurrence_reuses_receipt_and_rejects_changed_value(self):
        from crucis.core.graph import Graph
        from crucis.core.runs import RunRecord
        with tempfile.TemporaryDirectory() as tmp:
            b,s,sink=setup(PackageStore(tmp));r,policy=request(b);d=finite_domain(b,['A','B'])
            labels=api.LegacyBinding(b.producer,'i','real',d,'original',unresolved(),unresolved(),contract('legacy_runrecord_codec'))
            spec=api.SourceSpec((),(contract('legacy_runrecord_codec'),),str(uuid.uuid4()),unresolved());ctx=read_context(b,s,policy)
            rec=RunRecord('fixture','i','real','ok',graph=Graph.from_edges(2,[(0,1)]))
            first=core.import_legacy(rec,labels,spec,ctx,sink);second=core.import_legacy(rec,labels,spec,ctx,sink)
            self.assertEqual(first.state,'completed');self.assertEqual(first.value.subjects,second.value.subjects)
            rec.notes['file_read']='changed binding'
            self.assertEqual(core.import_legacy(rec,labels,spec,ctx,sink).state,'rejected')

    def test_explicit_projection_rejects_graphless_unknown_and_partial(self):
        b,s,_=setup();r,policy=request(b);d=finite_domain(b,['A','B']);m=permutation(b,d,d,[('0','0'),('1','1')])
        g=b.output('graph',graph_body(d,[directed_link(d,0,1)]));raw=capture_bytes(b,b'explicit status evidence')
        assessment=b.add('assessment',{'subjects':[g],'rule':contract('legacy_status_explicit'),'parameters':[],
            'basis':[raw],'conclusions':[{'facet':'s1.legacy_status','value':known('ok',[raw]),'supporting':[raw],'disputed':[]}],
            'cutoff':[raw],'revises':[]})
        labels=api.LegacyBinding(b.producer,'i','real',d,'original',known(m),unresolved(),contract('legacy_runrecord_codec'))
        selection=api.LegacySelection((g,),g,assessment,m,(),(),labels,contract('legacy_projection_explicit'))
        p=b.package([g]);projection=project(p,selection);self.assertEqual(projection.record.graph.directed,frozenset({(0,1)}))
        changed=copy.deepcopy(p);next(x for x in changed['records'] if x['id']==assessment['target'])['payload']['conclusions'][0]['value']=unresolved()
        with self.assertRaises(WireError):project(changed,selection)
        broad=b.output('collection',{'collection_kind':'sequence','member_contracts':[],'members':[],
            'extent':scope(d),'ordering':'native_sequence','generation':unresolved(),'weights':[]})
        with self.assertRaises(WireError):project(b.package([broad]),replace(selection,graph=broad))
        changed=copy.deepcopy(p);next(x for x in changed['records'] if x['id']==g['target'])['payload']['body']['coverage']['extent']='listed_only'
        with self.assertRaises(WireError):project(changed,selection)

    def test_core_outcome_conflicts_and_later_assessment_do_not_rewrite(self):
        b,s,_=setup();r,policy=request(b);s.registry.register_rule(contract('outcome_observations'),core.outcome_observations)
        def observed(value):
            prop=b.add('proposition',{'predicate':contract('native_property'),'arguments':[{'role':'s1.subject','value':r},
                {'role':'s1.property','value':'s1.outcome.termination'},{'role':'s1.value','value':value}], 'conditioning':[],'scope':scope(r)})
            return b.add('observation',{'subject':r,'proposition':prop,'value':value,'scope':scope(r),'source_time':unresolved(),
                'capture_time':unresolved(),'source':source('reported'),'event':unresolved()})
        first=observed('normal');ctx=api.AssessmentContext(Resolver(b.package([first])),s)
        old=core.assess(contract('outcome_observations'),[r],[first],[],ctx).value;snapshot=b.get(old)
        second=observed('failed');ctx=replace(ctx,resolver=Resolver(b.package([second])))
        new=core.assess(contract('outcome_observations'),[r],[first,second],[],ctx).value
        self.assertEqual(b.get(old),snapshot)
        self.assertEqual(b.get(new)['payload']['conclusions'][0]['value']['state'],'unresolved')

    def test_bounded_observation_is_not_native_completion(self):
        b,s,sink=setup();r,policy=request(b);a=attempt(b,r);handle=api.NativeHandle(a,unresolved(),object(),(),())
        inv={'kind':'function','entrypoint':contract('fixture_function'),'arguments':[]}
        def observer(handle,cursor,limit,context,sink):
            return api.Op('completed',api.ObservationBatch(({'one':'a'},{'two':'b'}),cursor,True,scope(a),()))
        ports=supplied_connection(b.producer,s,inv,authority=RuntimeAuthority(),executor=lambda *args:None,observer=observer)
        cursor=api.Cursor('fixture','0',unresolved());context=read_context(b,s,policy)
        self.assertEqual(ports.observe(handle,cursor,api.BatchLimit('1','10000',unresolved()),context,sink).state,'rejected')
        good=ports.observe(handle,cursor,api.BatchLimit('2','10000',unresolved()),context,sink)
        self.assertTrue(good.value.exhausted);self.assertEqual(good.state,'completed')
        self.assertIsNone(ports.cancel)

    def test_delivery_and_cancellation_need_separate_exact_authority(self):
        from test_audit_connections_history import event
        b,s,sink=setup();r,policy=request(b);a=attempt(b,r);authority=RuntimeAuthority();delivered=[]
        session=b.add('session',{'request':r,'native_identity':unresolved(),'parent':not_applicable('no_parent'),
            'membership':{'members':[a],'extent':'complete_for_scope','scope':scope(a),'gaps':[]},'completion_rule':contract('fixture_completion'),'source':source()})
        endpoint=b.add('endpoint',{'owner':b.producer,'operation':contract('expert'),'request_contract':contract('expert_question'),
            'response_contract':contract('expert_answer'),'input_domains':[],'allowed_information':policy,'transport':contract('fixture_transport'),'source':source()})
        action=b.add('action_request',{'session':session,'attempt':a,'requester':b.producer,'endpoint':endpoint,'arguments':[],
            'question':not_applicable('non_propositional_action'),'authority':unknown_ref('authority_evidence'),'native_action_identity':unresolved(),'source':source()})
        response=b.add('action_response',{'request':action,'responder':b.producer,'content':[],'response_state':'abstained','delivery':[],'source':source()})
        auth=b.add('authority_evidence',{'actor':b.producer,'policy':policy,'operation':contract('expert'),'subjects':[action],
            'permitted_effects':['s1.deliver'],'decision':'permitted','validity':scope(action),'source':source()})
        dg=api.DeliveryGrant(action,response,endpoint,('s1.deliver',),(policy,),auth,object())
        dg=replace(dg,runtime_capability=authority.issue('deliver',delivery_binding(dg)))
        def delivery(ref,channel,context,sink):
            delivered.append(ref);return api.Op('completed',api.DeliveryReceipt(ref,(),(),unresolved()))
        def canceller(handle,context,sink):
            asked=event(b,a,'cancel_requested');ack=event(b,a,'cancel_acknowledged')
            ref=b.add('cancellation',{'subject':a,'requester':b.producer,'policy':policy,'requested':asked,'acknowledgment':known(ack),'observed_stop':unresolved(),'source':source()})
            return api.Op('completed',api.CancellationReceipt(ref,(ack,),unresolved()))
        ports=supplied_connection(b.producer,s,{'kind':'function','entrypoint':contract('fixture'),'arguments':[]},
            authority=authority,executor=lambda *args:None,delivery=delivery,canceller=canceller)
        wrong_channel=ActionChannel(unknown_ref('endpoint'),lambda *args:None)
        self.assertEqual(ports.deliver(response,wrong_channel,api.DeliveryContext(dg),sink).state,'rejected');self.assertEqual(delivered,[])
        self.assertEqual(ports.deliver(response,ActionChannel(endpoint,lambda *args:None),api.DeliveryContext(dg),sink).state,'completed')
        ca=b.add('authority_evidence',{'actor':b.producer,'policy':policy,'operation':contract('cancel'),'subjects':[a],
            'permitted_effects':[],'decision':'permitted','validity':scope(a),'source':source()})
        cg=api.CancellationGrant(a,(policy,),ca,object());cg=replace(cg,runtime_capability=authority.issue('cancel',cancellation_binding(cg)))
        handle=api.NativeHandle(a,unresolved(),object(),(),());receipt=ports.cancel(handle,api.CancellationContext(cg),sink)
        self.assertEqual(receipt.state,'completed');self.assertEqual(receipt.value.stop_established['state'],'unresolved')

    def test_core_profiles_publication_and_alias_cas(self):
        with tempfile.TemporaryDirectory() as tmp:
            b,s,sink=setup(PackageStore(tmp));raw=capture_bytes(b,b'complete captured bytes')
            selection=b.add('selection',{'purpose':'s1.current','selected':[raw],'rule':contract('explicit_selection'),'basis':[raw],'source':source()})
            location=b.add('location',{'locator':str(Path(tmp).resolve()),'access_contract':contract('local_immutable_store'),
                'expected_snapshot':unknown_ref('artifact_snapshot'),'retrievals':[],'automatic_access':False})
            policy=b.add('policy',{'policy_contract':contract('local_publication'),'parameters':[],'scope':scope(location,selection),
                'authority':known(b.producer),'source':source()})
            root=evidence_record(b,[raw],context=[selection])
            p=b.package([root]);resolver=Resolver(p);read=api.ReadContext(policy,resolver,s.identities,s.records)
            profiles=core.validate(p,[contract('evidence_foundation'),contract('dag')],read)
            self.assertEqual(profiles.claims_satisfied,(contract('evidence_foundation'),));self.assertEqual(profiles.claims_withheld,(contract('dag'),))
            ctx=api.WriteContext(policy,resolver,s);publication=api.PublicationPolicy((contract('evidence_foundation'),),
                (contract('snapshot_integrity'),),contract('local_immutable_store'),location)
            result=core.publish(p,publication,ctx);self.assertEqual(result.state,'completed')
            alias=api.SelectionAlias(str(uuid.uuid4()),'current result')
            one=core.select_current(alias,selection,not_applicable('no_prior_selection'),ctx);self.assertEqual(one.state,'completed')
            self.assertEqual(core.select_current(alias,selection,not_applicable('no_prior_selection'),ctx).state,'rejected')
            self.assertEqual(s.identities.store.load(p['package_id']),p)

    def test_restricted_legacy_presentation_requires_unique_names(self):
        # Core permits duplicate display labels; the old route has a narrower prerequisite.
        from crucis.core.harness import present
        from crucis.core import battery
        self.assertTrue(callable(present))
        b,s,_=setup();d=finite_domain(b,['same','same'])
        self.assertEqual(len(b.get(d)['payload']['members']),2)
        from crucis.connections.integrations.legacy_recorded import require_unique_names
        with self.assertRaises(WireError):require_unique_names(['same','same'])

    @unittest.skipUnless((DATA_ROOT / 'runs/ab06').is_dir(),'recorded sources absent')
    def test_all_eight_existing_adapters_remain_read_only_and_echo(self):
        from crucis.core import adapter,battery
        from crucis.run import AUDITS
        from crucis.connections.integrations.legacy_recorded import connection
        names=adapter.names();self.assertEqual(len(names),8)
        for name in names:
            spec=next(v for v in AUDITS.values() if v['system']==name);ad=adapter.get(name,**spec.get('adapter_kw',{}));bt=battery.get(spec['battery']);item=bt.items[0];arm=spec['arms'][0]
            b,s,sink=setup();_,policy=request(b);ports=connection(b.producer,s,ad,item,arm)
            self.assertIsNone(ports.invoke);ports.verify_declaration()
            with patch.object(ad,'run',side_effect=AssertionError('native execution forbidden')):
                result=ports.read(api.SourceSpec((),(),str(uuid.uuid4()),unresolved()),read_context(b,s,policy),sink)
                expected=ad.recorded(item,arm)
            package=b.package(result.value.subjects);report=validate(package);self.assertTrue(report.ok,(name,report.to_json()))
            blob=result.value.artifacts[0];self.assertEqual(encode(echo(package,blob)),encode(expected))


if __name__=='__main__':unittest.main()
