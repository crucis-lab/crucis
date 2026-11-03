"""Run Crucis tests and record failures/skips explicitly (DLV-09)."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

parser=argparse.ArgumentParser()
parser.add_argument('--out',required=True,type=Path)
parser.add_argument('--pattern',default='test_audit_*.py')
args=parser.parse_args()
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))
if os.environ.get('CRUCIS_TEST_TEMP'):
    tempfile.tempdir=str(Path(os.environ['CRUCIS_TEST_TEMP']).resolve())
    Path(tempfile.tempdir).mkdir(parents=True,exist_ok=True)
suite=unittest.defaultTestLoader.discover(str(root/'tests'),pattern=args.pattern)
args.out.parent.mkdir(parents=True,exist_ok=True)
with args.out.with_suffix('.log').open('w',encoding='utf-8') as log:
    result=unittest.TextTestRunner(stream=log,verbosity=2).run(suite)
receipt={'tickets':['DLV-09'],'utc':datetime.now(timezone.utc).isoformat(),'ran':result.testsRun,
         'failures':[(str(t),e) for t,e in result.failures],'errors':[(str(t),e) for t,e in result.errors],
         'skipped':[(str(t),why) for t,why in result.skipped],'ok':result.wasSuccessful(),
         'evidence_root':os.environ.get('CRUCIS_DATA_ROOT'),'python':sys.version.split()[0]}
args.out.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:len(v) if isinstance(v,list) else v for k,v in receipt.items() if k!='tickets'}))
sys.exit(0 if receipt['ok'] else 1)
