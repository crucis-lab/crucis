"""Standalone development gate, without historical research-layout assumptions."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


def source_identity(root):
    rows={}
    for directory in ('crucis_causal','tests'):
        for path in sorted((root/directory).rglob('*')):
            if path.is_file() and '__pycache__' not in path.parts and path.suffix in ('.py','.json','.txt','.sha256'):
                rows[path.relative_to(root).as_posix()]=hashlib.sha256(path.read_bytes()).hexdigest()
    return rows


def run(bundle,out,dependencies=None,*,accepted=None,predecessors=()):
    root=Path(__file__).resolve().parents[2]
    out=Path(out).resolve()
    if out==root or root in out.parents:raise ValueError('development gate output must be outside the Crucis checkout')
    if not (root/'tests/run_tests.py').exists():raise ValueError('run development gates from a source checkout; installed runtime has no test suite')
    if out.exists():raise ValueError('choose a new gate output; previous receipts are immutable')
    references=[]
    for path in ([accepted] if accepted else [])+list(predecessors):
        path=Path(path).resolve()
        references.append({'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    if dependencies is not None:raise ValueError('install declared dependencies into the interpreter; source-path injection is no longer supported')
    before=source_identity(root)
    out.mkdir(parents=True)
    result=subprocess.run([sys.executable,'-B',str(root/'tests/run_tests.py'),'--out',str(out/'tests.json')],cwd=root)
    tests=json.loads((out/'tests.json').read_text(encoding='utf-8'))
    after=source_identity(root)
    report={'tickets':['DLV-08','DLV-09'],'bundle_label':bundle,
            'scope':'standalone development conformance; does not recreate historical bundle acceptance or scientific certificates',
            'source_manifest':before,'source_stable':before==after,'tests':tests,
            'historical_reference_files':references,'api_spend':False,'native_dispatch':False,
            'pass':result.returncode==0 and before==after}
    report['passed']=report['pass']
    (out/'gate.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('bundle');parser.add_argument('--out',required=True)
    args=parser.parse_args();report=run(args.bundle,args.out)
    print(json.dumps({'passed':report['pass'],'scope':report['scope']}))
    sys.exit(0 if report['pass'] else 1)
