"""Guard the agreed publication boundary (INF-06, BLD-11)."""
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
private={Path(p).name for p in json.loads((ROOT/'provenance/publication.json').read_text())['excluded_private_paths']}
for required in ('LICENSE','NOTICE','CITATION.cff','THIRD_PARTY_NOTICES.md'):
    assert (ROOT/required).is_file(), 'Missing publication metadata: '+required
try:
    top=Path(subprocess.check_output(['git','rev-parse','--show-toplevel'],cwd=ROOT,stderr=subprocess.DEVNULL,text=True).strip()).resolve()
    assert top==ROOT
    rows=subprocess.check_output(['git','rev-list','--objects','HEAD'],cwd=ROOT,text=True).splitlines()
    paths=[r.split(' ',1)[1] for r in rows if ' ' in r]
    history=True
except (subprocess.CalledProcessError,AssertionError):
    paths=[p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and '.git' not in p.parts]
    history=False
bad=[p for p in paths if Path(p).name in private]
assert not bad, 'Private planning paths remain in publication scope: '+repr(bad)
print(json.dumps({'publication_metadata':'pass','private_paths':0,'reachable_history_checked':history}))
