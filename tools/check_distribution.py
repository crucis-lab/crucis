"""Inspect built distributions and probe the installed wheel without checkout imports.

Tickets: DLV-09, DLV-10. No data downloads, native model execution or API calls.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tarfile
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE_EXAMPLES = {
    'crucis/docs/system-connections-sc1-example-2026-11-01.json',
    'crucis/docs/subsystem2-review-traceability-2026-11-02.json',
}


def check_names(names, *, source):
    for name in names:
        path = PurePosixPath(name)
        if path.is_absolute() or '..' in path.parts or '\\' in name:
            raise ValueError('Unsafe distribution path: ' + name)
        if 'crucis/docs/' in name and (not source or name not in SOURCE_EXAMPLES):
            raise ValueError('Development planning document in distribution: ' + name)
        if any(p in path.parts for p in ('external', 'runs', 'sealed', '.git', '__pycache__')):
            raise ValueError('Excluded material in distribution: ' + name)
        if path.name.startswith('.env') or path.name == 'SECRET_seeds.json' or path.suffix in ('.key', '.pem', '.pyc'):
            raise ValueError('Excluded material in distribution: ' + name)


PROBE = r'''
import hashlib, importlib.abc, json, pathlib, sys
checkout = pathlib.Path(sys.argv[1]).resolve()
installed_root = sys.argv[2]
expected = json.loads(sys.argv[3])
if installed_root:
    sys.path.insert(0, installed_root)
class BlockResearch(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in {'analysis','audit','harness','score','cc_graph','lineage','partial_stages','probe_io'}:
            raise ImportError('Research import forbidden: '+fullname)
sys.meta_path.insert(0, BlockResearch())
import crucis
from crucis.connections.schema import schema as sc1
from crucis.experiments.schema import schema as sc2
from crucis.core.graph import Graph
from crucis.core.adapter import names
import crucis.systems
module = pathlib.Path(crucis.__file__).resolve()
assert not module.is_relative_to(checkout), 'Imported the source checkout'
assert sc1() and sc2() and Graph.from_edges(2, [(0,1)]).n == 2
assert len(names()) == 8
base = module.parent.parent
for rel, sha in expected.items():
    assert hashlib.sha256((base/rel).read_bytes()).hexdigest() == sha, 'Installed bytes differ: '+rel
print(json.dumps({'module':str(module),'schemas':'pass','toy_graph':'pass','adapters':len(names()),
                  'runtime_files_verified':len(expected),'research_imports_blocked':True}))
'''


def run(dist_dir, installed_root=None):
    wheels = list(dist_dir.glob('*.whl'))
    sdists = list(dist_dir.glob('*.tar.gz'))
    if len(wheels) != 1 or len(sdists) != 1:
        raise ValueError('Expected exactly one wheel and one source distribution')
    with zipfile.ZipFile(wheels[0]) as archive:
        wheel_names = [i.filename for i in archive.infolist() if not i.is_dir()]
        check_names(wheel_names, source=False)
        for required in ('crucis/connections/sc1.schema.json','crucis/experiments/catalog.json'):
            json.loads(archive.read(required))
        if not any(n.endswith('/licenses/LICENSES/NOTEARS-Apache-2.0.txt') for n in wheel_names):
            raise ValueError('Wheel is missing retained NOTEARS license')
        if not any(n.endswith('/licenses/THIRD_PARTY_NOTICES.md') for n in wheel_names):
            raise ValueError('Wheel is missing third-party attribution')
        expected = {n:hashlib.sha256(archive.read(n)).hexdigest() for n in wheel_names if n.startswith('crucis/')}
    with tarfile.open(sdists[0], 'r:gz') as archive:
        source_names = [str(PurePosixPath(m.name).relative_to(PurePosixPath(m.name).parts[0]))
                        for m in archive.getmembers() if m.isfile()]
        check_names(source_names, source=True)
        if not SOURCE_EXAMPLES.issubset(source_names):
            raise ValueError('Source distribution lacks technical examples needed by tests')
        for required in ('tests/audit_fixtures/sc1/h1.json','tests/audit_fixtures/sc2/manifest.json',
                         'LICENSES/NOTEARS-Apache-2.0.txt','THIRD_PARTY_NOTICES.md'):
            if required not in source_names:
                raise ValueError('Source distribution lacks '+required)
    installed_root = str(installed_root.resolve()) if installed_root else ''
    with tempfile.TemporaryDirectory(prefix='crucis-wheel-probe-') as scratch:
        probe = subprocess.run([sys.executable,'-I','-B','-c',PROBE,str(ROOT),installed_root,json.dumps(expected)],
                               cwd=scratch,capture_output=True,text=True,check=True)
        installed = json.loads(probe.stdout)
        for module in ('crucis','crucis.connections','crucis.experiments'):
            command = 'import sys,runpy; '
            if installed_root:
                command += 'sys.path.insert(0,'+repr(installed_root)+'); '
            command += 'sys.argv=['+repr(module)+',"--help"]; runpy.run_module('+repr(module)+',run_name="__main__")'
            subprocess.run([sys.executable,'-I','-B','-c',command],cwd=scratch,check=True,stdout=subprocess.DEVNULL)
    return {'tickets':['DLV-09','DLV-10'],'utc':datetime.now(timezone.utc).isoformat(),
            'wheel':{'file':wheels[0].name,'sha256':hashlib.sha256(wheels[0].read_bytes()).hexdigest(),'files':len(wheel_names)},
            'sdist':{'file':sdists[0].name,'sha256':hashlib.sha256(sdists[0].read_bytes()).hexdigest(),'files':len(source_names)},
            'installed':installed,'isolated_cli':'pass','api_spend':False,'pass':True}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dist-dir',type=Path,required=True)
    parser.add_argument('--installed-root',type=Path,help='Explicit wheel installation directory, never a source checkout')
    parser.add_argument('--out',type=Path,required=True)
    args = parser.parse_args()
    receipt = run(args.dist_dir,args.installed_root)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(receipt))
