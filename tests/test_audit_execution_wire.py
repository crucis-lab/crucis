"""B01 fixed-fixture structural/registry gates; no native execution (DLV-08/09)."""
import base64
import copy
from dataclasses import replace
import functools
import hashlib
import inspect
import json
import os
from pathlib import Path
import sys
import unittest
import typing
import dataclasses

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from crucis_causal.execution import api, codec, schema
from crucis_causal.execution.model import (ExecutionError, VERSION, Builder, canonical, contract,
    digest, identity, index, known, not_applicable, number, qualified, reference, scope, unknown, unknown_ref)
from crucis_causal.execution.registry import (DeclaredDriver, ExactDecisionRegistry, ExactDriverRegistry,
    PayloadRegistry, SuppliedRegistryContext, supplied_callable)
from crucis_causal.execution.registry import require_critical_semantics

FIX = ROOT / 'tests/audit_fixtures/sc3'
LIMITS = api.Limits()
MANIFEST = json.loads((FIX / 'manifest.json').read_bytes())

def covers(*cases):
    """Optional external execution receipt, emitted only after actual test entry."""
    def decorate(method):
        @functools.wraps(method)
        def wrapped(self, *args, **kwargs):
            status = 'failed'
            result_state = self._outcome.result
            before = (len(result_state.errors), len(result_state.failures))
            try:
                result = method(self, *args, **kwargs)
                if before == (len(result_state.errors), len(result_state.failures)):
                    status = 'passed'
                return result
            finally:
                directory = os.environ.get('CRUCIS_S3_CASE_RECEIPTS')
                if directory:
                    dest = Path(directory).resolve()
                    if dest.is_relative_to(ROOT): raise AssertionError('external receipt directory required')
                    dest.mkdir(parents=True, exist_ok=True)
                    with (dest / 'cases.jsonl').open('a', encoding='utf-8') as stream:
                        stream.write(json.dumps({'test': self.id(), 'cases': list(cases), 'status': status})+'\n')
        wrapped.s3_cases = cases
        return wrapped
    return decorate

def fixture_views():
    return tuple(codec.parse_snapshot((FIX / e['path']).read_bytes(), LIMITS) for e in MANIFEST['files']
                 if e['path'].endswith('.json') and 'format' in json.loads((FIX / e['path']).read_bytes()))

def fixture():
    view = codec.parse_snapshot((FIX / 'all-core-records.json').read_bytes(), LIMITS)
    return view, codec.Resolver(fixture_views(), limits=LIMITS)

def payload(package, kind):
    return next(r['payload'] for r in package['records'] if r['record_type'] == 's3.'+kind)

def record_ref(view, kind):
    record = next(r for r in view.records if r['record_type'] == ('s3.'+kind if '.' not in kind else kind))
    return reference(record['id'], record['record_type'], view.package_id)

def implementation(data=b'Supplied deterministic test implementation'):
    from crucis_causal.connections.model import Builder as S1Builder, contract as c1
    from crucis_causal.connections.evidence import capture_bytes
    from crucis_causal.connections.codec import dumps
    b = S1Builder('Explicit test implementation snapshot')
    artifact = capture_bytes(b, data, format_contract=c1('source_text'))
    view = codec.parse_snapshot(dumps(b.package([artifact])), LIMITS)
    pin = api.PinnedArtifactIdentity(qualified(artifact, view.package_id), digest(data), not_applicable(), view)
    return pin

class WireCases(unittest.TestCase):
    @covers('W01')
    def test_W01_38_fixed_specimens_pins_and_complete_closure(self):
        from jsonschema import Draft202012Validator
        Draft202012Validator.check_schema(schema.schema())
        view, resolver = fixture()
        self.assertEqual({r['record_type'] for r in view.records}, set(schema.catalog()['core_payloads']))
        self.assertEqual(view.digest, digest((FIX/'all-core-records.json').read_bytes()))
        self.assertEqual(codec.parse_snapshot(codec.dumps(view.package, LIMITS), LIMITS).package, view.package)
        self.assertEqual(len(resolver.closure(view.package_id)), 6)
        for entry in MANIFEST['files']:
            self.assertEqual(hashlib.sha256((FIX/entry['path']).read_bytes()).hexdigest(), entry['sha256'])

    @covers('W02')
    def test_W02_all_38_missing_required_fields_fail_closed(self):
        view, _ = fixture()
        for mutation in json.loads((FIX/'negative-oracles.json').read_bytes())['missing_required_field']:
            with self.subTest(kind=mutation['record_type']):
                p = view.package
                r = next(r for r in p['records'] if r['record_type'] == mutation['record_type'])
                del r['payload'][mutation['remove']]
                with self.assertRaises(ExecutionError): codec.dumps(p, LIMITS)

    @covers('W02')
    def test_W02_raw_null_numbers_duplicates_unicode_and_depth(self):
        for raw in [b'{"x":1}',b'{"x":0.5}',b'{"x":NaN}',b'{"x":null}',b'{"x":true,"x":false}',b'{"x":"\\ud800"}',b'\xff']:
            with self.subTest(raw=raw):
                with self.assertRaises(ExecutionError): codec.loads(raw,LIMITS)
        self.assertEqual(codec.loads(b'{"x":true,"y":"e\\u0301"}',LIMITS), {'x':True,'y':'e\u0301'})
        with self.assertRaises(ExecutionError): codec.loads(b'['*65+b']'*65,LIMITS)
        with self.assertRaises(ExecutionError): codec.loads(b'"abcdef"',replace(LIMITS,max_scalar_utf8_bytes='2'))
        with self.assertRaises(ExecutionError): codec.loads(b'{}',replace(LIMITS,max_manifest_bytes='1'))
        with self.assertRaises(ExecutionError): codec.loads(b'[true,false]',replace(LIMITS,max_collection_items='1'))
        with self.assertRaises(ExecutionError): codec.loads(b'{}',api.Limits(max_depth='0'))

    @covers('W02')
    def test_W02_knowledge_axes_conflicts_and_later_assessments(self):
        view, _ = fixture()
        p = view.package
        support = payload(p,'support_claim')
        support['axes'][0]['status']='not_run'
        with self.assertRaisesRegex(ExecutionError,'s3.axis_status'): codec.dumps(p,LIMITS)
        p = view.package; payload(p,'support_claim')['axes'].pop()
        with self.assertRaisesRegex(ExecutionError,'eight_unique'): codec.dumps(p,LIMITS)
        p = view.package; r = next(r for r in p['records'] if r['record_type']=='s3.assessment')
        r['payload']['result']=known(True); later=copy.deepcopy(r);later['id']=identity()
        later['payload']['result']=known(False);later['payload']['conflicts_with']=[reference(r['id'],'assessment')]
        p['records'].append(later)
        result=codec.parse_snapshot(codec.dumps(p,LIMITS),LIMITS)
        values=[r['payload']['result']['value'] for r in result.records if r['record_type']=='s3.assessment']
        self.assertEqual(values,[True,False])
        p=view.package;payload(p,'native_association')['assessment']=known(unknown_ref('assessment'))
        with self.assertRaises(ExecutionError):codec.dumps(p,LIMITS)
        p=view.package;payload(p,'account')['related_accounts']['extent']='not_examined'
        payload(p,'account')['related_accounts']['members']=[reference(payload(p,'account_view')['account']['target'],'account')]
        with self.assertRaisesRegex(ExecutionError,'unexamined_members'):codec.dumps(p,LIMITS)

    @covers('W02')
    def test_W02_duplicate_identity_wrong_pin_type_version_and_root(self):
        view,resolver=fixture();p=view.package;p['records'].append(copy.deepcopy(p['records'][0]))
        with self.assertRaisesRegex(ExecutionError,'duplicate_record'):codec.dumps(p,LIMITS)
        p=view.package;p['format']['version']='latest'
        with self.assertRaises(ExecutionError):codec.dumps(p,LIMITS)
        p=view.package;p['roots'][0]['target_type']='s1.request'
        with self.assertRaises(ExecutionError):codec.dumps(p,LIMITS)
        p=view.package;p['package_id']=identity();p['external_packages'][0]['expected_digest']['value']['value']='0'*64
        wrong=codec.parse_snapshot(codec.dumps(p,LIMITS),LIMITS);resolver.add(wrong)
        with self.assertRaisesRegex(ExecutionError,'integrity_mismatch'):resolver.closure(wrong.package_id)
        forged=replace(view,digest={**view.digest,'value':'0'*64})
        with self.assertRaisesRegex(ExecutionError,'pinned_view_mismatch'):resolver.add(forged)
        with self.assertRaisesRegex(ExecutionError,'package_identity_conflict'):resolver.add(codec.parse_snapshot(b' '+view.source_bytes,LIMITS))
        p=view.package;p['package_id']=identity();p['records'][0]['payload']['name']='changed'
        with self.assertRaisesRegex(ExecutionError,'record_identity_conflict'):resolver.add(codec.parse_snapshot(codec.dumps(p,LIMITS),LIMITS))

    @covers('W02')
    def test_W02_reference_budget_is_for_the_complete_traversal(self):
        view,resolver=fixture()
        limited=codec.Resolver(resolver.closure(view.package_id),limits=replace(LIMITS,max_total_reference_nodes='200'))
        # Every supplied package fits200 refs individually; their closure exceeds it.
        with self.assertRaisesRegex(ExecutionError,'reference_count_limit'):limited.closure(view.package_id)

    @covers('W02')
    def test_W02_temporal_numeric_range_and_base64_forms(self):
        self.assertEqual(number('-0')['text'],'-0')
        self.assertEqual(number('1.200e+3')['text'],'1.200e+3')
        with self.assertRaises(ExecutionError):number(0.5)
        with self.assertRaises(ExecutionError):number('01')
        for val in [{'kind':'byte_range','start':'2','end_exclusive':'1'},
                    {'content_form':'inline_base64','data':'YQ'},
                    {'time_type':'utc_instant','value':'2026-02-30T00:00:00Z','precision':'second','uncertainty_seconds':unknown()}]:
            with self.assertRaises(ExecutionError):codec._semantics({'records':[],'value':val})

    @covers('W02')
    def test_W02_31_operations_exact_keys_missingness_and_cardinality(self):
        # Shape fixtures follow the accepted grammar; not OPxx execution receipts.
        def example(expr):
            parts=schema.split(expr)
            if len(parts)>1:return example(next(p for p in parts if p!='NA'))
            if expr.endswith('[]'):return []
            match=__import__('re').fullmatch(r'(.+)\[(\d+)\.\.(?:n|\d+)\]',expr)
            if match:return [example(match[1]) for _ in range(int(match[2]))]
            if expr.startswith('Ref('):return reference(identity(),expr[4:-1].split('|')[0])
            return {'Contract':contract('fixture_rule'),'ID':identity(),'String':'0','Code':'s3.fixture_reason','PositiveIndex':'1',
                'Digest':digest(b'x'),'Time':{'time_type':'utc_instant','value':'2026-11-03T00:00:00Z','precision':'second','clock':unknown(),'uncertainty_seconds':known(number('0'))},
                'Cursor':{'contract':contract('fixture_cursor'),'position':'0','scope':scope()}}.get(expr,expr)
        for op in schema.catalog()['operations']:
            roles=[]
            for name,spec in op['roles'].items():
                kinds,lower,_=schema.role_spec(spec)
                roles.append({'role':'s3.role.'+name,'members':index(reference(identity(),kinds[0]) for _ in range(lower))})
            binding={'operation':op['contract'],'roles':roles,'parameters':[{'key':k,'value':known(example(v))} for k,v in op['parameters'].items()]}
            with self.subTest(op=op['id']):
                self.assertTrue(schema.validate_binding(binding,admission=True))
                bad=copy.deepcopy(binding);bad['parameters'].append(copy.deepcopy(bad['parameters'][0]))
                with self.assertRaises(ExecutionError):schema.validate_binding(bad)
                bad=copy.deepcopy(binding);bad['roles'][0]['members']=index([],extent='unresolved')
                self.assertTrue(schema.validate_binding(bad))
                with self.assertRaises(ExecutionError):schema.validate_binding(bad,admission=True)
                bad=copy.deepcopy(binding);bad['roles'][0]['members']['members']=[reference(identity(),'s1.gap')]
                with self.assertRaises(ExecutionError):schema.validate_binding(bad)

    @covers('W02')
    def test_W02_all_18_families_and_77_roles(self):
        c=schema.catalog();count=0
        for family in c['conditional_families']:
            roles=[{'role':name,'members':index([unknown_ref(kinds.split('|')[0])],extent='unresolved')} for name,kinds in c['family_role_types'][family['id']].items()]
            p={'family':family['contract'],'applicability':'applies','roles':roles}
            self.assertTrue(schema.validate_family(p));count+=len(roles)
            p['roles'].append(copy.deepcopy(roles[0]))
            with self.assertRaises(ExecutionError):schema.validate_family(p)
        self.assertEqual(count,77)
        self.assertFalse(schema.validate_family({'family':contract('family.future'),'applicability':'not_examined','roles':[]}))

    @covers('W02')
    def test_W02_payload_context_is_not_artifact_host(self):
        view,resolver=fixture()
        value={'subject':reference(view.records[0]['id'],view.records[0]['record_type']),
            'keys':{**record_ref(view,'typed_payload'),'binding':'internal'},'time_scope':{**record_ref(view,'typed_payload'),'binding':'internal'},
            'retention':contract('fixture_retention'),'negative_coverage':contract('fixture_query_coverage')}
        for key in ['keys','time_scope']:value[key].pop('package_id')
        from crucis_causal.connections.model import Builder as S1Builder,contract as c1
        from crucis_causal.connections.evidence import capture_bytes
        from crucis_causal.connections.codec import dumps as s1dumps
        b=S1Builder('Explicit typed query storage host');artifact=capture_bytes(b,canonical(value),format_contract=c1('json'))
        host=codec.parse_snapshot(s1dumps(b.package([artifact])),LIMITS)
        def staged(context_view):
            builder=Builder('Explicit context test');builder.ingest(view.records)
            typed=builder.add('typed_payload',{'payload_contract':contract('s3.payload.query'),
                'content':{'artifact':qualified(artifact,host.package_id),'selector':not_applicable()},
                'reference_context':{'package_id':context_view.package_id,'format':context_view.format}},basis='intrinsic')
            deps=(*resolver.closure(view.package_id),host)
            p=builder.package(view.package['roots'][0],deps)
            v=codec.parse_snapshot(codec.dumps(p,LIMITS),LIMITS)
            return v,qualified(typed,v.package_id)
        staged_view,typed=staged(view);resolver.add(host);resolver.add(staged_view)
        self.assertEqual(resolver.payload(typed,staged_view.package_id,PayloadRegistry()),value)
        wrong,typed=staged(host);resolver.add(wrong)
        with self.assertRaisesRegex(ExecutionError,'reference_target'):resolver.payload(typed,wrong.package_id,PayloadRegistry())

    @covers('X10')
    def test_X10_failed_partial_native_bytes_preserved_without_output_repair(self):
        from crucis_causal.connections.model import Builder as S1Builder
        from crucis_causal.connections.evidence import capture_bytes
        from crucis_causal.connections.codec import dumps as s1dumps
        from crucis_causal.connections.validation import content_bytes
        raw=b'\xff{"edges":[null'
        b=S1Builder('Failed partial byte capture');ref=capture_bytes(b,raw)
        view=codec.parse_snapshot(s1dumps(b.package([ref])),LIMITS)
        r=next(r for r in view.records if r['id']==ref['target'])
        self.assertEqual(content_bytes(r['payload']['content']),raw)
        self.assertFalse(any(r['record_type']=='s1.output' for r in view.records))
        with self.assertRaises(ExecutionError):codec.loads(raw,LIMITS)

    @covers('M01')
    def test_M01_pure_declarations_preparation_registry_and_48_signatures(self):
        calls=[];pin=implementation(Path(__file__).read_bytes());view,_=fixture();component=record_ref(view,'component')
        def invoke(request,context,grants,issue_token,sink):
            calls.append('native');raise AssertionError('native call during pure phase')
        descriptor=api.ExactDriverDescriptor(component,contract('s3.op.launch'),contract('s3.payload.function_invocation'),contract('fixture_result'),pin,(),supplied_callable(invoke))
        declaration=api.DriverDeclaration(component,(descriptor,),())
        registry=ExactDriverRegistry();registry.register(declaration)
        context=api.PinnedReadContext((view,),view.read_scope,SuppliedRegistryContext(registry,ExactDecisionRegistry(),PayloadRegistry()),LIMITS)
        binding=api.ResolvedOperationBinding({'payload':{'operation':descriptor.operation}}, {'package_id':view.package_id,'format':view.format},api.PinnedInputs((),(view,)))
        driver=DeclaredDriver(declaration,lambda binding,inputs,context:{'kind':'function','entrypoint':'supplied','arguments':record_ref(view,'typed_payload'),'callable_binding':contract('fixture_callable')})
        self.assertEqual(driver.describe(context),declaration)
        self.assertEqual(driver.prepare(binding,binding.inputs,context).state,'completed')
        self.assertEqual(calls,[])
        with self.assertRaises(ExecutionError):registry.lookup({**descriptor.operation,'version':'latest'})
        def wrong(request):return None
        bad=replace(descriptor,method=supplied_callable(wrong))
        with self.assertRaisesRegex(ExecutionError,'signature_mismatch'):ExactDriverRegistry().register(api.DriverDeclaration(component,(bad,),()))
        with self.assertRaisesRegex(ExecutionError,'unsupported_payload'):PayloadRegistry().decode(contract('payload.future'),{})
        for row in schema.catalog()['ports']:
            group,method=row['port'].split('.')
            actual=inspect.signature(getattr(getattr(api,group+'Port'),method))
            self.assertEqual(list(actual.parameters)[1:],list(row['arguments']))
            typing.get_type_hints(getattr(getattr(api,group+'Port'),method))
        for name,fields in schema.catalog()['runtime_values'].items():
            cls=getattr(api,'CallResult' if name=='CallResult[T]' else name)
            self.assertEqual([f.name for f in dataclasses.fields(cls)],list(fields))
        class Decision:
            def describe(self,context):return None
            def requirements(self,actions,policy,context):return api.CallResult('completed',api.InformationRequirements(actions,(),policy,{}))
            def select(self,actions,policy,inputs,frontier,context):raise AssertionError('selection not requested')
        d=api.DecisionDeclaration(component,contract('fixture_decision'),contract('fixture_input'),contract('fixture_output'),contract('fixture_sources'),unknown(),pin)
        decisions=ExactDecisionRegistry();decisions.register(d,Decision())
        _,decision=decisions.lookup(d.procedure)
        self.assertEqual(decision.requirements((),None,context).state,'completed');self.assertEqual(calls,[])

    @covers('W02')
    def test_W02_inherited_negatives_and_critical_extensions_never_use_latest(self):
        # N01/N02/N03/N05 are exercised by the malformed/knowledge cases above;
        # NR01 pin and NR02 target failures and N12 critical semantics are explicit.
        view,_=fixture();original=view.source_bytes;p=view.package
        p['roots'][0]['target_type']='s3.projection_view'
        with self.assertRaisesRegex(ExecutionError,'reference_target'):codec.dumps(p,LIMITS)
        p=view.package;p['records'][0]['payload']['extra']='unrecognized'
        with self.assertRaisesRegex(ExecutionError,'schema'):codec.dumps(p,LIMITS)
        p=view.package;p['records'][0]['record_type']='s3.future_record'
        with self.assertRaisesRegex(ExecutionError,'schema'):codec.dumps(p,LIMITS)
        p=view.package;p['extensions']=[{'contract':contract('extension.future'), 'affects':[],
            'critical_for':['s3.claim.control'],'payload':{'content_form':'inline_utf8','text':'{"native":null}'}}]
        extended=codec.parse_snapshot(codec.dumps(p,LIMITS),LIMITS)
        registry=PayloadRegistry()
        require_critical_semantics(extended,[],registry,LIMITS)
        with self.assertRaisesRegex(ExecutionError,'critical_extension_uninterpreted'):
            require_critical_semantics(extended,['s3.claim.control'],registry,LIMITS)
        self.assertEqual(view.source_bytes,original)
        self.assertEqual(extended.package['extensions'][0]['payload']['text'],'{"native":null}')

    @covers('M01')
    def test_M01_registered_descriptors_resist_caller_mutation(self):
        pin=implementation();view,_=fixture();component=record_ref(view,'component')
        def invoke(request,context,grants,issue_token,sink):raise AssertionError('not invoked')
        selected=contract('s3.op.launch')
        descriptor=api.ExactDriverDescriptor(component,selected,contract('fixture_input'),contract('fixture_output'),pin,(),supplied_callable(invoke))
        registry=ExactDriverRegistry();registry.register(api.DriverDeclaration(component,(descriptor,),()))
        original=copy.deepcopy(selected);selected['version']='changed'
        self.assertEqual(registry.lookup(original).operation,original)
        found=registry.lookup(original);found.operation['version']='changed-again'
        self.assertEqual(registry.lookup(original).operation,original)
        found.implementation.content_digest['value']='0'*64
        self.assertEqual(registry.lookup(original).implementation.content_digest,digest(b'Supplied deterministic test implementation'))

    @covers('M01')
    def test_M01_runtime_objects_do_not_serialize_or_forge_access(self):
        view,_=fixture()
        for obj in [view,view.read_scope]:
            with self.assertRaises(ExecutionError):codec.check_tree({'runtime':obj},LIMITS)
            with self.assertRaises(TypeError):canonical({'runtime':obj})
        with self.assertRaises(TypeError):copy.deepcopy(view.read_scope)
        with self.assertRaises(TypeError):view.read_scope._packages=frozenset()
        forged=object.__new__(api.ReadCapability);forged._issuer=object();forged._packages=frozenset([view.package_id])
        with self.assertRaisesRegex(ExecutionError,'read_denied'):codec.parse_snapshot(view.source_bytes,LIMITS,access=forged)
        with self.assertRaisesRegex(ExecutionError,'read_denied'):codec.parse_snapshot(view.source_bytes,LIMITS,access={})
        with self.assertRaises(ExecutionError):api.CallResult('rejected')
        with self.assertRaises(ExecutionError):api.CallResult('partial',issues=(api.Issue('s3.gap',scope(),()),))

if __name__ == '__main__':
    unittest.main()
