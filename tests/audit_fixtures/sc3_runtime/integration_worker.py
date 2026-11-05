"""Explicit test-supervisor cold bootstrap; no installed/default CLI execution."""
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'tests'))
import integration_case as fixture
from crucis_causal.execution import api
from crucis_causal.execution.journal import Journal
value=json.loads(Path(sys.argv[1]).read_bytes());bootstrap=json.loads(sys.stdin.readline(16385))
env=fixture.cold_reopen(value,bootstrap)
if value['kind']=='local':
    journal=Journal(env.root/'journal');ctx=api.RuntimeContext(env.context.read,journal.control(env.account))
    head=journal.head(env.account,ctx)
    if head.state!='completed':raise RuntimeError(str(head.issues))
    states=[r['payload']['components'] for r in head.value.snapshot.records if r['record_type']=='s3.recovery' and r['payload']['kind']=='state_restore']
    print(json.dumps({'state':'completed','revision':head.value.revision,'snapshot':head.value.snapshot.package_id,'digest':head.value.snapshot.digest,'native_dispatch':False,'state_restoration_receipts':states}))
elif value['kind']=='remote':
    capture=env.capture(value['capture'])
    result=env.run(env.acknowledge(capture))
    if result.state!='completed':raise RuntimeError(str(result.issues))
    print(json.dumps({'state':result.state,'capture':capture.occurrence,'cursor':capture.durable_cursor,'ack':env.oracle_ack()}))
else:
    result=env.run(env.lookup_answer(value['command']))
    if result.state!='completed':raise RuntimeError(str(result.issues))
    print(json.dumps({'state':result.state,'oracle':env.client.call('interaction_oracle')}))
