"""Bundle evidence orchestration, reusing unchanged S1 gates (DLV-08/09/10)."""
import argparse
import hashlib
import json
from pathlib import Path
import py_compile
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]

def identity(out):
    paths=sorted(list((ROOT/'crucis/experiments').glob('*.py'))+list((ROOT/'crucis/experiments').glob('*.json'))+
                 list((ROOT/'crucis/experiments').glob('*.txt'))+list((ROOT/'tests').glob('test_audit_experiments_*.py'))+
                 list((ROOT/'tests/audit_fixtures/sc2').glob('*.json')))
    rows=[];(out/'bytecode').mkdir(parents=True,exist_ok=True)
    for p in paths:
        rows.append({'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
        if p.suffix=='.py':py_compile.compile(str(p),cfile=str(out/'bytecode'/(hashlib.sha256(str(p).encode()).hexdigest()+'.pyc')),doraise=True)
    return rows

def test_ids(suite):
    for case in suite:
        if isinstance(case,unittest.TestSuite):yield from test_ids(case)
        else:yield case.id()

def run(bundle,out,accepted,predecessors,dependencies):
    from crucis.connections.gates import run as preserve
    out=Path(out).resolve()
    if out==ROOT or ROOT in out.parents:raise ValueError('gate outputs must be outside repository')
    if (out/'gate.json').exists():raise ValueError('choose a new immutable gate attempt')
    out.mkdir(parents=True,exist_ok=True)
    acceptance=json.loads(Path(accepted).read_text(encoding='utf-8'))
    for row in acceptance['accepted_files']:
        if hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()!=row['sha256']:raise ValueError('accepted design hash mismatch: '+row['path'])
    plan=json.loads((ROOT/'crucis/docs/subsystem2-implementation-dag-2026-11-02.json').read_text(encoding='utf-8'))
    definition=next(b for b in plan['bundles'] if b['id']==bundle)
    prior=[json.loads(Path(p).read_text(encoding='utf-8')) for p in predecessors]
    if any(not p.get('passed',p.get('pass',False)) for p in prior):raise ValueError('failed predecessor')
    needed=set(definition['depends_on']) or {'S2-entry'}
    if needed!={p['bundle'] for p in prior}:raise ValueError('exact required predecessor receipts missing')
    before=identity(out)
    inventory=sorted(test_ids(unittest.defaultTestLoader.discover(str(ROOT/'tests'),pattern='test_audit_experiments_*.py')))
    if not inventory:raise ValueError('no S2 acceptance tests discovered')
    preservation=preserve(bundle,out/'preservation',dependencies)
    acceptance_ledger=None
    if bundle=='S2-I':
        from .acceptance import build,recorded_path
        if preservation['pass']:
            recorded=recorded_path(ROOT,out)
        else:recorded={'passed':False}
        all_inventory=sorted(test_ids(unittest.defaultTestLoader.discover(str(ROOT/'tests'),pattern='test_audit_*.py')))
        acceptance_ledger=build(ROOT,plan,all_inventory,preservation['pass'])
        acceptance_ledger['recorded_s2_path']=recorded
        acceptance_ledger['passed'] &= recorded['passed']
        (out/'acceptance-ledger.json').write_text(json.dumps(acceptance_ledger,indent=2)+'\n',encoding='utf-8')
    after=identity(out/'after')
    report={'tickets':['DLV-08','DLV-09','DLV-10'],'bundle':bundle,'candidate_baseline':str(Path(accepted).resolve()),
        'predecessor_receipts':[{'path':str(Path(p).resolve()),'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()} for p in predecessors],
        'source_identity':before,'source_stable':before==after,'environment':{'python':sys.version,'dependencies':str(Path(dependencies).resolve())},
        'checks':{'common_preservation':preservation['pass'],'test_inventory':inventory,'required_common_gates':definition['common_gates']},
        'must_show':definition['must_show'],'artifacts':[str(out/'preservation/gate.json')],
        'known_limits':['Metadata/recorded scope only; no fresh native or scientific inference claims','Existing optional causal-learn dependency skip remains disclosed'],
        'passed':preservation['pass'] and before==after and preservation['tests']['skipped']<=1,
        'api_spend':False,'native_dispatch':False,'protected_store_access':False}
    if acceptance_ledger is not None:
        report['acceptance_ledger']={'path':str(out/'acceptance-ledger.json'),'sha256':hashlib.sha256((out/'acceptance-ledger.json').read_bytes()).hexdigest(),
            'adverse_cases':len(acceptance_ledger['adverse_cases']),'api_scenarios':len(acceptance_ledger['api_scenarios']),'passed':acceptance_ledger['passed']}
        report['passed'] &= acceptance_ledger['passed']
    (out/'gate.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('bundle');ap.add_argument('--out',required=True);ap.add_argument('--accepted',required=True);ap.add_argument('--predecessor',action='append',required=True);ap.add_argument('--dependencies',required=True)
    a=ap.parse_args();r=run(a.bundle,a.out,a.accepted,a.predecessor,a.dependencies)
    print(json.dumps({'bundle':a.bundle,'passed':r['passed'],'tests':len(r['checks']['test_inventory']),'output':a.out},indent=2));sys.exit(0 if r['passed'] else 1)
