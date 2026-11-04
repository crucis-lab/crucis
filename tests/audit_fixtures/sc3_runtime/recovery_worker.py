"""Supervisor-controlled process-death barrier after actual native reply."""
import json
from pathlib import Path
import sys
import threading
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/'tests'))
import recovery_case as r
value=json.loads(Path(sys.argv[1]).read_bytes())
token=json.loads(sys.stdin.readline())['token']
def barrier(label,data):
    print('READY:'+label,flush=True)
    threading.Event().wait(120)
env,plan=r.reopen(value,token,native_fault=barrier)
admitted=env.admit(plan,group=value['group'])
if admitted.state!='completed':raise RuntimeError(str(admitted.issues))
result=env.issue(admitted.value,transmission=value['transmission'])
raise RuntimeError('Expected process-death barrier was not reached: '+str(result.issues))
