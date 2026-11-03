"""Opt-in SC-1 commands, outside the adopted crucis/certificate CLI (DLV-08/09)."""
import argparse
import json
from pathlib import Path
import sys

from .codec import WireError, dumps, loads
from .model import contract

ROOT=Path(__file__).resolve().parents[2]


def external(path):
    destination=Path(path).resolve()
    if destination==ROOT or ROOT in destination.parents:raise WireError('runtime outputs must be outside cc-research')
    if destination.name.lower()=='.env':raise WireError('credential file is outside this command scope')
    return destination


def write_new(path,data):
    path=external(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('xb') as stream:stream.write(data)


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);commands=parser.add_subparsers(dest='command',required=True)
    schema=commands.add_parser('schema');schema.add_argument('--out',required=True)
    describe=commands.add_parser('describe')
    check=commands.add_parser('validate');check.add_argument('package');check.add_argument('--out',required=True)
    check.add_argument('--require',action='append',default=[]);check.add_argument('--profile',action='append',default=[])
    ingest=commands.add_parser('import-recorded');ingest.add_argument('audit');ingest.add_argument('--item');ingest.add_argument('--arm');ingest.add_argument('--out',required=True)
    gate=commands.add_parser('gate');gate.add_argument('bundle');gate.add_argument('--out',required=True);gate.add_argument('--dependencies')
    args=parser.parse_args(argv)
    try:
        if args.command=='schema':
            from .schema import schema
            write_new(args.out,dumps(schema()));return 0
        if args.command=='describe':
            from .core import PROFILES
            print(json.dumps({'tickets':['DLV-08','DLV-09'],'format':contract('connection_package'),
                'adoption':'opt-in experimental subsystem 1','commands':['schema','describe','validate','import-recorded','gate'],
                'execution':'no native/provider execution command','profiles':PROFILES,'scientific_evaluation':'legacy auditor remains authoritative'},indent=2));return 0
        if args.command=='validate':
            from .core import PROFILES
            from .semantics import validate
            path=Path(args.package).resolve()
            if path.name.lower()=='.env':raise WireError('credential file is outside evidence scope')
            package=loads(path.read_bytes());report=validate(package);required=list(args.require)
            for name in args.profile:
                name=name if '.' in name else 's1.'+name
                if name not in PROFILES:raise WireError('unsupported exact profile: '+name)
                required.extend(PROFILES[name])
                if any(c.contract==name and c.result!='pass' for c in report.checks):required.append(name)
            ok=True
            try:report.require([n if '.' in n else 's1.'+n for n in required])
            except WireError:ok=False
            result={'tickets':['DLV-08','DLV-09'],**report.to_json(),'required_claims_established':ok}
            write_new(args.out,dumps(result));return 0 if ok else 2
        if args.command=='import-recorded':
            from crucis.core import adapter,battery
            from crucis.run import AUDITS
            from .legacy import import_record
            from .semantics import validate
            from .store import PackageStore
            if args.audit not in AUDITS:raise WireError('select an existing recorded audit from crucis.run.AUDITS')
            spec=AUDITS[args.audit];ad=adapter.get(spec['system'],**spec.get('adapter_kw',{}));bt=battery.get(spec['battery'])
            item=bt.item(args.item) if args.item else bt.items[0];arm=args.arm or spec['arms'][0]
            if arm not in item.arms:raise WireError('arm not in selected item')
            out=external(args.out)
            if out.exists():raise WireError('choose a new output directory; existing results are immutable')
            record=ad.recorded(item,arm)
            result=import_record(record,n=item.n);package=result['package'];report=validate(package);report.require()
            receipt=PackageStore(out/'store').publish(package)
            write_new(out/'package.json',dumps(package));write_new(out/'validation.json',dumps(report.to_json()))
            write_new(out/'receipt.json',dumps({'tickets':['DLV-08','DLV-09'],'audit':args.audit,'item':item.item_id,'arm':arm,
                'legacy_reported_status':record.status,'legacy_snapshot':result['legacy_snapshot'],
                'native_execution':False,'legacy_default_changed':False,'published':receipt}))
            return 0
        if args.command=='gate':
            from .gates import run
            return 0 if run(args.bundle,external(args.out),args.dependencies)['pass'] else 1
    except (KeyError,OSError,ValueError,RuntimeError,WireError) as exc:
        print('SC-1 command: '+str(exc),file=sys.stderr);return 2


if __name__=='__main__':sys.exit(main())
