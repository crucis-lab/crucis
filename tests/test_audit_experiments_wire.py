from crucis.core.paths import ROOT as DATA_ROOT
"""S2-A: accepted envelopes, strict bytes, pins and resolver negatives (DLV-08/09)."""
import copy
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import sys
import unittest
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from crucis.experiments import ReaderLimits,ServiceError,known,number
from crucis.experiments import codec,core
from crucis.experiments.model import digest,identity,reference
from crucis.experiments.resolver import PlanResolver,ReadAccess,parse_snapshot
from crucis.experiments.schema import catalog,schema

FIX=ROOT/'tests/audit_fixtures/sc2'
LIMITS=ReaderLimits.standard()
MANIFEST=json.loads((FIX/'manifest.json').read_text(encoding='utf-8'))
RAW={d['path']:(FIX/d['path']).read_bytes() for d in MANIFEST['packages']}
_resolver=None
def resolver():
    global _resolver
    if _resolver is None:_resolver=PlanResolver(RAW.values(),limits=LIMITS)
    return _resolver
def package(name):return json.loads(RAW[name+'.json'])
def desc(name):return next(d for d in MANIFEST['packages'] if d['path']==name+'.json')
def local(name,alias):return copy.deepcopy(desc(name)['aliases'][alias])
def record(p,alias,name):return next(r for r in p['records'] if r['id']==local(name,alias)['target'])
def context(name):
    return SimpleNamespace(limits=LIMITS,resolver=resolver(),active_package=desc(name)['package_id'],access=ReadAccess(frozenset(d['package_id'] for d in MANIFEST['packages'])))

class WireCases(unittest.TestCase):
    def test_all_accepted_snapshots_schema_refs_and_exact_stored_bytes(self):
        kinds=set()
        for name,raw in RAW.items():
            view=parse_snapshot(raw,LIMITS)
            self.assertEqual(view.snapshot_digest,digest(raw))
            d=next(d for d in MANIFEST['packages'] if d['path']==name)
            self.assertEqual(d['digest'],view.snapshot_digest)
            if view.format['name']=='s2.experiment_package':
                self.assertEqual(codec.dumps(view.package,LIMITS),raw)
                kinds.update(r['record_type'] for r in view.records)
            ctx=context(name[:-5]);resolver().closure(view.package_id,ctx.access,LIMITS)
        self.assertEqual(kinds,set(catalog()['core_payloads']))

    def test_schema_and_catalog_are_owned_closed_copies(self):
        from jsonschema import Draft202012Validator
        Draft202012Validator.check_schema(schema())
        c=catalog();c['core_payloads'].clear();self.assertEqual(len(catalog()['core_payloads']),40)
        self.assertEqual(len(catalog()['parameter_schemas']),25);self.assertEqual(len(catalog()['payload_contracts']),11)
        edited=schema();edited.clear();self.assertIn('$defs',schema())

    def test_all_eleven_typed_payload_formats_and_their_reference_contexts(self):
        found=set()
        from crucis.experiments.model import not_applicable
        for d in MANIFEST['packages']:
            p=json.loads(RAW[d['path']]);ctx=context(d['path'][:-5])
            for r in p['records']:
                if r['record_type']!='s1.artifact_snapshot':continue
                fmt=r['payload']['format']
                if fmt['state']!='known' or not fmt['value']['name'].startswith('s2.payload.'):continue
                value=resolver().payload({'artifact':reference(r['id'],'s1.artifact_snapshot'),'selector':not_applicable()},p['package_id'],ctx.access,LIMITS)
                self.assertIsInstance(value,dict);found.add(fmt['value']['name'])
        self.assertEqual(found,{p['contract']['name'] for p in catalog()['payload_contracts'].values()})

    def test_payload_fragment_and_unqualified_nested_reference_do_not_gain_full_contract(self):
        from crucis.experiments.model import not_applicable
        ctx=context('A-s1-definitions');ref={'artifact':local('A-s1-definitions','coordinates'),'selector':known({'selector_type':'json_pointer','pointer':'/indices'})}
        with self.assertRaises(ServiceError):resolver().payload(ref,ctx.active_package,ctx.access,LIMITS)
        p=package('A-s1-definitions');p['package_id']=identity();r=record(p,'coordinates','A-s1-definitions')
        body=json.loads(r['payload']['content']['text']);body['domain']=local('A-s1-definitions','domain');r['payload']['content']['text']=json.dumps(body)
        r['id']=identity()
        raw=(json.dumps(p,indent=2)+'\n').encode();other=resolver().with_view(parse_snapshot(raw,LIMITS));access=ReadAccess(frozenset(other._views))
        with self.assertRaises(ServiceError):other.payload({'artifact':reference(r['id'],'s1.artifact_snapshot'),'selector':not_applicable()},p['package_id'],access,LIMITS)

    def test_bad_json_never_silently_repaired(self):
        for raw in [b'{"x":1,"x":2}',b'{"x":NaN}',b'\xff',b'{"x":"\\ud800"}',b'\xef\xbb\xbf{}',b'{"n":1.3}']:
            with self.subTest(raw=raw):self.assertEqual(core.read_package(raw,context('A-s2-plan')).state,'rejected')

    def test_exact_versions_unknown_core_fields_and_null_rejected(self):
        for mutate in [lambda p:p['format'].update(version='9'),lambda p:p.update(extra='x'),lambda p:p['records'][0].update(created_at=None),lambda p:p['records'][0].update(record_type='foreign.new_record')]:
            p=package('A-s2-plan');mutate(p)
            with self.assertRaises(ServiceError):codec.validate_package(p,LIMITS)

    def test_duplicate_id_root_and_descriptor_rejected(self):
        for field in ['records','roots','external_packages']:
            p=package('A-s2-plan');p[field].append(copy.deepcopy(p[field][0]))
            with self.assertRaises(ServiceError):codec.validate_package(p,LIMITS)

    def test_missing_target_wrong_kind_and_undeclared_external_rejected(self):
        for mode in ['missing','kind','external']:
            p=package('A-s2-plan');ref=p['roots'][0]
            if mode=='missing':ref['target']=identity()
            elif mode=='kind':ref['target_type']='s2.case_revision'
            else:ref.update(binding='external',package_id=identity())
            with self.assertRaises(ServiceError):codec.validate_package(p,LIMITS)

    def test_parameters_keys_roles_types_enums_and_counts(self):
        for mode in ['key','role','bool','negative','duplicate']:
            p=package('A-s2-plan');r=record(p,'response_group','A-s2-plan')['payload'];b=r['bindings'][1]
            if mode=='key':b['key']='extra'
            elif mode=='role':b['role']='s2.other_role'
            elif mode=='bool':b['value']=known(True)
            elif mode=='negative':b['value']=known(number(-1))
            else:r['bindings'].append(copy.deepcopy(b))
            with self.assertRaises(ServiceError):codec.validate_package(p,LIMITS)

    def test_unknown_parameter_contract_is_preservable_not_installed(self):
        p=package('A-s2-plan');r=record(p,'response_group','A-s2-plan')['payload'];r['schema']={'name':'foreign.response','version':'unrecognized'}
        codec.validate_package(p,LIMITS);self.assertFalse(codec.validate_parameter(r))

    def test_lexical_numbers_array_order_and_package_set_order(self):
        p=package('H-s2-plan');r=record(p,'measurement','H-s2-plan')['payload']
        next(b for b in r['bindings'] if b['key']=='scale')['value']=known(number('-0.000'))
        a=codec.dumps(p,LIMITS);self.assertIn(b'-0.000',a)
        p['records'].reverse();p['external_packages'].reverse();self.assertEqual(a,codec.dumps(p,LIMITS))
        definition=record(p,'plan','H-s2-plan')['payload']['definitions'];definition.reverse();self.assertNotEqual(a,codec.dumps(p,LIMITS))
        with self.assertRaises(ServiceError):number(True)
        with self.assertRaises(ServiceError):number(0.1)

    def test_pretty_received_bytes_digest_not_canonical_digest(self):
        p=package('A-s2-plan');raw=json.dumps(p,indent=2).encode();view=parse_snapshot(raw,LIMITS)
        self.assertEqual(view.snapshot_digest,digest(raw));self.assertNotEqual(view.snapshot_digest,digest(core.encode_package(view)))

    def test_reader_limits_positive_and_enforced(self):
        with self.assertRaises(ServiceError):replace(LIMITS,max_records='0')
        with self.assertRaises(ServiceError):replace(LIMITS,max_packages='01')
        for field,value in [('max_manifest_bytes','8'),('max_records','1'),('max_parameter_depth','2')]:
            with self.subTest(field=field),self.assertRaises(ServiceError):parse_snapshot(RAW['A-s2-plan.json'],replace(LIMITS,**{field:value}))
        with self.assertRaises(ServiceError):PlanResolver(RAW.values(),limits=replace(LIMITS,max_packages='1'))

    def test_scope_access_no_locator_fetch_and_explicit_anchor(self):
        ctx=context('A-s2-plan');ref=local('A-s2-plan','task')
        self.assertEqual(core.resolve(ref,ctx).state,'completed')
        denied=SimpleNamespace(**{**vars(ctx),'access':ReadAccess(frozenset())})
        self.assertEqual(core.resolve(ref,denied).diagnostics[0].code,'s2.access_denied')
        noanchor=SimpleNamespace(**{**vars(ctx),'active_package':None})
        self.assertEqual(core.resolve(ref,noanchor).diagnostics[0].code,'s2.reference_anchor_required')
        with self.assertRaises(ServiceError):resolver().lookup(ctx.active_package,ctx.access,replace(LIMITS,max_records='1'))

    def test_external_digest_changed_not_reported_as_valid(self):
        p=package('A-s2-plan');p['package_id']=identity();p['external_packages'][0]['expected_digest']['value']['value']='0'*64
        view=parse_snapshot(codec.dumps(p,LIMITS),LIMITS);r=resolver().with_view(view)
        with self.assertRaises(ServiceError):r.closure(view.package_id,ReadAccess(frozenset(r._views)),LIMITS)

    def test_record_identity_conflict_even_when_packages_differ(self):
        p=package('A-s2-plan');p['package_id']=identity();record(p,'subject','A-s2-plan')['payload']['requirements']=[]
        with self.assertRaises(ServiceError):resolver().with_view(parse_snapshot(codec.dumps(p,LIMITS),LIMITS))

    def test_views_cannot_mutate_resolver_state(self):
        ctx=context('A-s2-plan');view=resolver().lookup(ctx.active_package,ctx.access,LIMITS)
        view.package['records'].clear();view.snapshot_digest['value']='0'*64
        other=resolver().lookup(ctx.active_package,ctx.access,LIMITS)
        self.assertTrue(other.records);self.assertNotEqual(view.snapshot_digest,other.snapshot_digest)

    def test_structural_cycles_allowed_but_package_dependency_cycle_rejected(self):
        # Plan/trial cycles are present in the accepted goldens.
        p=package('A-s2-plan');codec.validate_package(p,LIMITS)
        q=copy.deepcopy(p);q['package_id']=identity()
        from crucis.experiments.model import unknown
        p['external_packages'].append({'package_id':q['package_id'],'format':q['format'],'locator':unknown(),'expected_digest':unknown(),'access':'s2.supplied'})
        q['external_packages'].append({'package_id':p['package_id'],'format':p['format'],'locator':unknown(),'expected_digest':unknown(),'access':'s2.supplied'})
        r=PlanResolver([codec.dumps(p,LIMITS),codec.dumps(q,LIMITS)],limits=LIMITS)
        with self.assertRaises(ServiceError):r.closure(p['package_id'],ReadAccess(frozenset(r._views)),LIMITS)

if __name__=='__main__':unittest.main()
