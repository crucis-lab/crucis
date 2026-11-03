"""Free recorded bundle gates, outputs outside the repo (DLV-08, DLV-09, DLV-10).

No live invocation, tracker mutation, folder migration or API calls. Reuses the
existing auditor and certificate verifier rather than reimplementing scoring.
"""
import argparse
import contextlib
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
import py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _comparison_key(row):
    return json.dumps({k:row.get(k) for k in ("bundle","audit","system","arm","metric","source")}, sort_keys=True)


def source_identity(out,compile_files=True):
    """Original 64-file identity plus the complete new runtime/test/fixture identity."""
    project=ROOT.parent;baseline=Path(__file__).with_name('legacy-baseline.sha256')
    rows=[line.split(' *',1) for line in baseline.read_text(encoding='utf-8').splitlines() if line]
    actual=[];mismatches=[]
    for expected,name in rows:
        path=project/name;observed=hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else 'missing'
        actual.append((observed,name))
        if observed!=expected:mismatches.append({'path':name,'expected':expected,'observed':observed})
    digest=hashlib.sha256(''.join(h+'  '+name+'\n' for h,name in actual).encode()).hexdigest()
    expected='d615f61a2ce46862b9093ee7309374c825a5684dcf0d4561453a7d71444e42ae'
    paths=set(Path(__file__).parent.rglob('*'))|set((project/'tests').glob('test_audit_connections_*.py'))
    paths |= set((project/'tests/audit_fixtures/sc1').glob('*.json'))|{project/'tests/audit_fixtures/s1_native_fixture.py'}
    out.mkdir(parents=True,exist_ok=True)
    paths=sorted((p for p in paths if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.md'),key=lambda p:p.relative_to(project).as_posix())
    new_rows=[(hashlib.sha256(p.read_bytes()).hexdigest(),p.relative_to(project).as_posix()) for p in paths]
    manifest=''.join(h+'  '+name+'\n' for h,name in new_rows)
    (out/'implementation.sha256').write_text(manifest,encoding='utf-8')
    compile_dir=out/'bytecode';compile_dir.mkdir(exist_ok=True)
    for path in paths:
        if path.suffix=='.py' and compile_files:
            destination=compile_dir/(hashlib.sha256(str(path).encode()).hexdigest()+'.pyc')
            py_compile.compile(str(path),cfile=str(destination),doraise=True)
    return {'legacy_files':len(rows),'legacy_expected':expected,'legacy_observed':digest,'mismatches':mismatches,
        'legacy_pass':len(rows)==64 and not mismatches and digest==expected,'implementation_files':len(new_rows),
        'implementation_manifest_sha256':hashlib.sha256(manifest.encode()).hexdigest(),'compile':'pass' if compile_files else 'not_repeated',
        'identity_scope':'new runtime, schema, dependency lock, baseline pins, tests, frozen fixtures; explanatory docs excluded'}


def run(bundle, out, dependencies=None):
    out = Path(out).resolve()
    if out == ROOT.parent or ROOT.parent in out.parents:
        raise ValueError("bundle evidence must be outside cc-research")
    out.mkdir(parents=True, exist_ok=True)
    # Sealed-storage tests deliberately require their synthetic seed store outside
    # the entire shared DSC directory, not merely outside this git repository.
    tmp = Path(tempfile.gettempdir())
    if ROOT.parent.parent == tmp or ROOT.parent.parent in tmp.parents:
        raise ValueError("system temporary directory must be outside the shared DSC folder")
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE":"1", "TMP":str(tmp), "TEMP":str(tmp), "PYTHONIOENCODING":"utf-8"}
    if dependencies:
        deps=str(Path(dependencies).resolve())
        sys.path.insert(0,deps)
        env["PYTHONPATH"]=deps+os.pathsep+str(ROOT.parent)+os.pathsep+env.get("PYTHONPATH","")
    started = time.time()
    report = {"tickets":["DLV-08","DLV-09","DLV-10"], "bundle":bundle, "native_execution":False,
              "offline_fixture_process_execution":True,
              "api_spend":False, "output":str(out), "pass":False}
    if (out/'gate.json').exists():raise ValueError('choose a new gate directory; prior evidence must not be overwritten')
    report['source_identity']=source_identity(out)
    if not report['source_identity']['legacy_pass']:
        report['failed_gate']='legacy_source_identity'
        (out/'gate.json').write_text(json.dumps(report,indent=2),encoding='utf-8');return report
    with (out / "tests.log").open("w", encoding="utf-8") as log:
        proc = subprocess.run([sys.executable,"-B",str(ROOT.parent / "tests/run_tests.py"),
                               "--out",str(out / "tests.json"),"--pattern","test_audit_*.py"],
                              cwd=ROOT.parent, env=env, stdout=log, stderr=subprocess.STDOUT)
    # ROOT is crucis/, project root is its parent.
    if proc.returncode:
        report["failed_gate"]="tests"
        (out / "gate.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
        return report
    report["tests"] = json.loads((out / "tests.json").read_text(encoding="utf-8"))
    # A real stored result also passes through the new capture/publication CLI.
    new_paths=[]
    for name in ('pc@semantic','matmcd','causaliq','causal_copilot@bnd08'):
        destination=out/('connection_'+name.replace('@','_'))
        with (out/('connection_'+name.replace('@','_')+'.log')).open('w',encoding='utf-8') as log:
            imported=subprocess.run([sys.executable,'-B','-m','crucis.connections','import-recorded',name,'--out',str(destination)],
                cwd=ROOT.parent,env=env,stdout=log,stderr=subprocess.STDOUT)
            verified=subprocess.run([sys.executable,'-B','-m','crucis.connections','validate',str(destination/'package.json'),
                '--out',str(destination/'foundation.json'),'--profile','evidence_foundation','--require','snapshot_integrity'],
                cwd=ROOT.parent,env=env,stdout=log,stderr=subprocess.STDOUT) if imported.returncode==0 else imported
        new_paths.append({'audit':name,'pass':imported.returncode==verified.returncode==0,'directory':str(destination)})
    report['new_connection_paths']=new_paths
    from crucis.rerun import existing as existing
    from crucis.report import certificate
    from crucis import run as runner
    with (out / "rerun.log").open("w",encoding="utf-8") as log, contextlib.redirect_stdout(log):
        rc = existing.main(out / "rerun", ("B1","B2","B3"), reports=True)
    comp = json.loads((out / "rerun/comparison.json").read_text(encoding="utf-8"))
    baseline = json.loads((ROOT / "results/rerun_v1/comparison.json").read_text(encoding="utf-8"))
    report["comparison"] = comp["summary"]["all"]
    report["comparison_key_parity"] = sorted(map(_comparison_key,comp["rows"])) == sorted(map(_comparison_key,baseline["rows"]))
    report["exact_count_parity"] = all(r["stored"] == r["recomputed"] for r in comp["rows"] if r.get("exact"))
    fresh = {name:json.loads(Path(paths["report"]).read_text(encoding="utf-8")) for name,paths in comp["reports"].items()}
    cache = {}
    def recompute(name,spec):
        key = (name,json.dumps(spec,sort_keys=True))
        if key not in cache:
            candidate = fresh.get(name)
            cache[key] = candidate if candidate is not None and candidate["spec"] == spec else runner.audit(runner.spec_from_json(spec),name)
        return cache[key]
    verifies=[]
    for name, paths in comp["reports"].items():
        for origin, path in (("fresh",Path(paths["certificate"])),
                             ("stored",ROOT / "results/rerun_v1/reports" / name.replace("@","_") / "certificate.json")):
            cert = json.loads(path.read_text(encoding="utf-8"))
            verified = certificate.verify(cert,recompute)
            body, result = cert["body"], recompute(name,cert["body"]["spec"])
            verified["finding_key_parity"] = [(f["id"],f["kind"],f["verdict"]) for f in body["findings"]] == [(f["id"],f["kind"],f["verdict"]) for f in result["findings"]]
            verifies.append({"audit":name,"origin":origin,**verified})
    report["certificates"] = verifies
    report["pass"] = (not rc and report["comparison"]["pass"] and report["comparison"]["compared"] == 1298
                      and report["comparison_key_parity"] and report["exact_count_parity"] and len(verifies)==28
                      and all(v["pass"] and v["finding_key_parity"] for v in verifies) and all(p['pass'] for p in new_paths))
    # No source changes may slip between identity capture and completion of the gate.
    identity_after=source_identity(out/'after',compile_files=False)
    report['source_stable_during_gate']=(identity_after['legacy_pass'] and identity_after['implementation_manifest_sha256']==report['source_identity']['implementation_manifest_sha256'])
    report['pass'] &= report['source_stable_during_gate']
    report["elapsed_seconds"] = time.time()-started
    (out / "gate.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    return report


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle");parser.add_argument("--out",required=True);parser.add_argument("--dependencies")
    args=parser.parse_args()
    result=run(args.bundle,args.out,args.dependencies)
    print(json.dumps({k:v for k,v in result.items() if k not in ("certificates",)},indent=2))
    sys.exit(0 if result["pass"] else 1)
