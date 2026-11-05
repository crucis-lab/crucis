"""Read supplied S3 bytes; live bindings must be explicitly injected in Python."""
import argparse
import json
from pathlib import Path
import sys
from . import api,codec
from .core import Core
from .model import ExecutionError,contract


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    commands=parser.add_subparsers(dest='command')
    for name in ('inspect','validate','plan','recovery-plan'):
        p=commands.add_parser(name)
        p.add_argument('snapshot',type=Path)
        p.add_argument('--dependency',action='append',type=Path,default=[])
        if name=='plan':p.add_argument('--request',type=Path,required=True)
        if name=='recovery-plan':
            p.add_argument('--kind',choices=['wait','reconcile','reconnect','retransmit','restart','stop','close'],required=True)
            p.add_argument('--policy',required=True,help='Exact policy name; the CLI does not install policy code')
    args=parser.parse_args(argv)
    if args.command is None:parser.print_help();return 0
    try:
        limits=api.Limits()
        def read(path):
            with path.open('rb') as stream:
                raw=stream.read(int(limits.max_manifest_bytes)+1)
            if len(raw)>int(limits.max_manifest_bytes):raise ExecutionError('s3.manifest_limit')
            return raw
        views=tuple(codec.parse_snapshot(read(p),limits) for p in [args.snapshot,*args.dependency])
        core=Core();ctx=core.context(views,limits=limits);view=views[0]
        if args.command=='inspect':report=core.inspect(view,ctx)
        elif args.command=='validate':report=core.validate(view,ctx)
        elif args.command=='plan':
            value=codec.loads(read(args.request),limits)
            if not isinstance(value,dict) or set(value)!={'operation','roles','parameters','request_occurrence'}:raise ExecutionError('s3.operation_request_shape')
            request=api.OperationRequest(value['operation'],tuple(value['roles']),tuple(value['parameters']),value['request_occurrence'])
            result=core.plan(view,request,ctx)
            report={'state':result.state,'issues':[i.code for i in result.issues],'effects':[],'live_bindings_installed':False}
        else:
            goal=api.RecoveryGoal(args.kind,{'subjects':[],'qualifiers':[]},contract(args.policy))
            result=core.recover(view,goal,ctx)
            report={'state':result.state,'issues':[i.code for i in result.issues],'effects':[],'live_bindings_installed':False}
        print(json.dumps(report,sort_keys=True));return 2 if report.get('state') in ('partial','rejected') else 0
    except ExecutionError as exc:
        print(json.dumps({'state':'held','issues':[exc.code],'effects':[]},sort_keys=True));return 2
    except (OSError,ValueError,TypeError,KeyError):
        print(json.dumps({'state':'held','issues':['s3.supplied_input_unavailable_or_invalid'],'effects':[]},sort_keys=True));return 2


if __name__=='__main__':sys.exit(main())
