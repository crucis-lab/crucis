"""Read-only B00 acceptance (D00), existing S1/S2 APIs only; DLV-08/09."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from crucis_causal.experiments import ReaderLimits
from crucis_causal.experiments.resolver import PlanResolver, ReadAccess

def check():
    fixture = Path(__file__).resolve().parent
    manifest = json.loads((fixture / 'manifest.json').read_bytes())
    for entry in manifest['files']:
        assert hashlib.sha256((fixture / entry['path']).read_bytes()).hexdigest() == entry['sha256'], entry['path']
    limits = ReaderLimits.standard()
    trials, runs, requests, attempts = set(), set(), set(), set()
    for binding in manifest['bindings']:
        resolver = PlanResolver([(fixture / p).read_bytes() for p in binding['dependencies']], limits=limits)
        access = ReadAccess(frozenset(resolver._views))
        for pid in resolver._views:
            resolver.closure(pid, access, limits)
        run = resolver.record(binding['run_binding'], binding['run_binding']['package_id'], access, limits).record
        assert run['record_type'] == 's2.run_binding'
        runs.add(run['id'])
        trials.add(run['payload']['trial']['target'])
        r = resolver.lookup(binding['R_package_id'], access, limits)
        request = next(x for x in r.records if x['id'] == binding['request']['target'])
        assert request['payload']['route'] == 's1.direct'
        attempt = next(x for x in r.records if x['id'] == binding['attempt']['target'])
        assert attempt['payload']['native_identity']['state'] == 'unresolved'
        requests.add(request['id']); attempts.add(attempt['id'])
    assert all(len(x) == 4 for x in (trials, runs, requests, attempts))
    records = json.loads((fixture / 'all-core-records.json').read_bytes())['records']
    assert len({r['record_type'] for r in records}) == 38
    payloads = {r['record_type']: r['payload'] for r in records}
    assert len({x['axis'] for x in payloads['s3.support_claim']['axes']}) == 8
    assert len(payloads['s3.delivery']['actions']['members']) == len(payloads['s3.delivery']['responses']['members']) == 1
    negatives = json.loads((fixture / 'negative-oracles.json').read_bytes())
    assert len(negatives['missing_required_field']) == 38
    assert sum(map(len, negatives['inherited'].values())) == 30
    oracle = json.loads((fixture / 'oracles.json').read_bytes())
    assert oracle['checkpoint']['total'] == '9'
    assert oracle['remote']['jobs_after_lost_ack'] == oracle['interactive']['q1_deliveries'] == '1'
    assert oracle['interactive']['q2_missing_source_deliveries'] == '0'
    return {'case': 'D00', 'passed': True, 'fresh_S2_bindings': 4, 'S1_R_snapshots': 4,
            'all_core_specimens': 38, 'required_field_mutations': 38, 'inherited_negative_oracles': 30,
            'native_calls': 0, 'S3_calls': 0, 'scope': 'Fixed input/oracle baseline only; no S3 execution conformance'}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.out.resolve().is_relative_to(ROOT):
        raise SystemExit('Receipts must remain outside the checkout')
    result = check()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    if args.out.exists():
        raise SystemExit('Preserve previous receipt')
    args.out.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result))
