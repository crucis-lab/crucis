"""Opt-in metadata inspection/validation/import/echo; no execution (DLV-08/09/10)."""
import argparse
from collections import Counter
from dataclasses import asdict
import json
from pathlib import Path
import sys
from . import api,core
from .model import contract,reference,qualified,known,unknown,scope
from .resolver import PlanResolver,ReadAccess,parse_snapshot
from .services import FamilyRegistry,AssessmentRegistry,LegacyRegistry,IdentityService,OccurrenceStore
from .writer import S2RecordWriter
from .operations import parameter
from . import legacy

ROOT=Path(__file__).resolve().parents[2]

def _read(path,limits):
    path=Path(path).resolve()
    if path.name.lower()=='.env':raise ValueError('credential file is outside metadata scope')
    with path.open('rb') as handle:data=handle.read(int(limits.max_manifest_bytes)+1)
    return parse_snapshot(data,limits)

def _output(path):
    root=Path(path).resolve()
    if root==ROOT or ROOT in root.parents:raise ValueError('outputs must be outside cc-research')
    root.mkdir(parents=True,exist_ok=True)
    return root

def _write(path,data):
    # Reuse immutable atomic publication; never overwrite an earlier report.
    from crucis.connections.store import _atomic
    _atomic(path,data)

def _json(value):return (json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf-8')

def _save(view,writer,out):
    pending=[p['package_id'] for p in view.package['external_packages']];seen=set()
    snapshots=[]
    while pending:
        pid=pending.pop()
        if pid in seen:continue
        seen.add(pid);dep=writer.base.lookup(pid,writer.access,writer.limits)
        if dep is None:raise ValueError('explicit dependency snapshot missing')
        snapshots.append((pid,dep.source_bytes))
        pending.extend(p['package_id'] for p in dep.package['external_packages'])
    # Resolve the whole explicit closure before publication; publish its manifest
    # last so an unavailable dependency cannot leave an apparently complete root.
    (out/'dependencies').mkdir(exist_ok=True)
    for pid,raw in snapshots:_write(out/'dependencies'/(pid+'.json'),raw)
    _write(out/'package.json',view.source_bytes)

def run(args):
    limits=api.ReaderLimits.standard();view=_read(args.package,limits)
    views=[view,*[_read(p,limits) for p in args.input]]
    base=PlanResolver([v.source_bytes for v in views],limits=limits)
    access=ReadAccess(frozenset(base._views));registry=FamilyRegistry()
    read=api.PlanReadContext(limits,base,registry,access,view.package_id)
    if args.command=='inspect':
        return {'tickets':['DLV-08','DLV-09'],'package_id':view.package_id,'format':view.format,
            'received_digest':view.snapshot_digest,'record_counts':dict(sorted(Counter(r['record_type'] for r in view.records).items())),
            'roots':view.package['roots'],'external_packages':view.package['external_packages'],
            'scope':'Supplied metadata only; native/scientific validity unestablished'},0
    out=_output(args.out)
    w=S2RecordWriter(base,access,limits);d=w.context()
    if args.command=='validate':
        from .contracts import install as definitions
        from .families import install as families
        definitions(d.read.registry,d.author);families(d.read.registry,d.author)
        roots=tuple(qualified(r,view.package_id) for r in view.package['roots'])
        claim={'profile':contract('s2.'+args.profile),'families':[contract(x) for x in args.family],
            'scope':scope(*roots),'evidence':[],'limits':[]}
        result=core.assess(roots,(claim,),api.PlanAssessmentContext(d.read,d,AssessmentRegistry()))
        satisfied=result.state!='rejected' and not result.value.withheld
        report={'tickets':['DLV-08','DLV-09'],'state':result.state,'metadata_claim_satisfied':satisfied,
            'profile':claim,'issues':[asdict(x) for x in (result.value.issues if result.value else result.diagnostics)],
            'input_digest':view.snapshot_digest,'native_execution':False,'scientific_accuracy':'unestablished'}
        if result.value:_save(w.frozen(result.value.assessments),w,out)
        _write(out/'report.json',_json(report));return report,0 if satisfied else 2
    if args.command=='import':
        from types import SimpleNamespace
        w.identities=IdentityService(OccurrenceStore(out/'occurrences'))
        from dataclasses import replace
        d=replace(d,identities=w.identities)
        ref=reference(args.snapshot,'s1.artifact_snapshot',view.package_id)
        found=base.record(ref,view.package_id,access,limits)
        fmt=found.record['payload']['format']
        if fmt['state']!='known':raise ValueError('source format must be explicit')
        fields={'battery':known(args.battery) if args.battery else unknown(),'version':known(args.source_version) if args.source_version else unknown(),
            'projection':known(contract('s2.legacy_echo'))}
        with w.begin(d.author,d.clock) as tx:config=parameter(tx,d,'legacy',fields);tx.commit()
        reg=LegacyRegistry();legacy.install(reg,d.author)
        context=api.LegacyContext(d,None,None,SimpleNamespace(legacy_views={}),reg)
        result=core.import_legacy(api.LegacyImportSource(args.occurrence,(ref,),fmt['value'],unknown()),api.LegacyImportScope(args.kind,config,()),context)
        if result.state=='rejected':raise ValueError(result.diagnostics[0].code)
        published=w.frozen(result.value.roots);_save(published,w,out)
        report={'tickets':['DLV-08','DLV-09','DLV-10'],'state':result.state,'receipt':result.value.receipt,
            'selection':config,'package_id':published.package_id,'issues':[asdict(i) for i in result.diagnostics],
            'native_execution':False,'original_history':'unestablished'}
        _write(out/'report.json',_json(report));return report,0
    if args.command=='project':
        from types import SimpleNamespace
        reg=LegacyRegistry();legacy.install(reg,d.author)
        ctx=api.LegacyContext(d,None,None,SimpleNamespace(legacy_views={}),reg)
        refs=tuple(reference(r,'s2.import_receipt',view.package_id) for r in args.receipt)
        selected=reference(args.selection,'s2.parameter_set',view.package_id)
        result=core.project_legacy(refs,api.LegacyProjectionPolicy(contract('s2.legacy_echo'),selected,True),ctx)
        if result.state=='rejected':raise ValueError(result.diagnostics[0].code)
        from crucis.connections.legacy import encode
        from crucis.connections.codec import dumps
        _write(out/'legacy.json',dumps([encode(p.record) for p in result.value.projections]))
        report={'tickets':['DLV-08','DLV-09'],'state':result.state,'projection_count':len(result.value.projections),
            'contract':contract('s2.legacy_echo'),'scope':'Exact encoded value; original file bytes/history not established','losses':[]}
        _write(out/'report.json',_json(report));return report,0
    raise ValueError('unsupported metadata command')

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    for name in ('inspect','validate','import','project'):
        q=sub.add_parser(name);q.add_argument('package');q.add_argument('--input',action='append',default=[],help='Explicit additional metadata snapshot; never locator retrieval')
        if name!='inspect':q.add_argument('--out',required=True)
        if name=='validate':
            q.add_argument('--profile',choices=['preserve','interpret','bind_inputs_sources','bind_native_request','bind_evaluation'],default='preserve')
            q.add_argument('--family',action='append',default=[])
        if name=='import':
            q.add_argument('--snapshot',required=True);q.add_argument('--occurrence',required=True)
            q.add_argument('--kind',choices=['run_record','battery_manifest','audit_spec'],default='run_record')
            q.add_argument('--battery');q.add_argument('--source-version')
        if name=='project':q.add_argument('--receipt',action='append',required=True);q.add_argument('--selection',required=True)
    args=p.parse_args(argv)
    try:report,status=run(args)
    except Exception as exc:
        print(_json({'state':'rejected','reason':str(exc)[:240],'native_execution':False}).decode(),end='');return 2
    print(_json(report).decode(),end='');return status

if __name__=='__main__':sys.exit(main())
