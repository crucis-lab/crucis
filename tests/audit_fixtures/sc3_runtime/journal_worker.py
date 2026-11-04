"""Deterministic B02 crash barrier. Only a supervisor-owned scratch journal."""
import argparse
import base64
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from crucis_causal.execution import api,codec
from crucis_causal.execution.journal import Journal,resolve_binding,binding_digest
from crucis_causal.execution.model import unknown

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',required=True,type=Path);p.add_argument('--input',required=True,type=Path);p.add_argument('--barrier',required=True)
    args=p.parse_args();request=json.loads(args.input.read_bytes());journal=Journal(args.root)
    views=tuple(codec.parse_snapshot(base64.b64decode(raw,validate=True),api.Limits()) for raw in request['dependencies'])
    read=api.PinnedReadContext(views,api.supplied_read(v.package_id for v in views),None,api.Limits())
    def barrier(label):
        if label==args.barrier:
            print('READY:'+label,flush=True)
            if sys.stdin.readline().strip()!='continue':raise RuntimeError('supervisor did not authorize continuation')
    ctx=api.RuntimeContext(read,journal.control(request['account']),fault=barrier)
    delta=api.CommitDelta(tuple(request['records']),tuple(request['roots']),views)
    mode=request.get('mode','append')
    if mode=='append':
        result=journal.append(request['account'],request['revision'],request['transaction'],delta,ctx)
    elif mode=='capture':
        source=api.SourceIdentity(**request['source'])
        raw=tuple(api.CapturedBytes(r['occurrence'],source,base64.b64decode(r['bytes'],validate=True),r['extent'],api.RecordDelta()) for r in request['raw'])
        result=journal.commit_capture(source,request['revision'],request['transaction'],raw,delta,request['cursor'],ctx)
    elif mode=='prepare':
        head=journal.head(request['account'],ctx).value
        resolver=codec.Resolver((*views,head.snapshot),limits=api.Limits())
        c,c_pid=resolver.record(request['command'],head.snapshot.package_id)
        grants=api.OwnerBindingReceipts((),binding_digest(resolve_binding(c['payload']['binding'],c_pid,resolver)),api.ValidityContext((),unknown(),(),api.RecordDelta()))
        result=journal.prepare_issue(request['command'],head,grants,ctx,request['transmission'])
    else:raise ValueError('unknown controlled fixture mode')
    print(json.dumps({'state':result.state,'issues':[i.code for i in result.issues]}),flush=True)

if __name__=='__main__':main()
