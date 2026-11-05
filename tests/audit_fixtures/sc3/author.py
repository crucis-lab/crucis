"""B00 authoring only: fresh synthetic metadata, never S3/native execution.

DLV-08/09. Run explicitly to create a NEW fixture revision, not during tests.
Original archived S3 examples and the accepted expectation records are not edited.
"""
import copy
import hashlib
import inspect
import json
from pathlib import Path
import re
import sys
import uuid

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'tests')]
import test_audit_experiments_handoff as existing
from crucis_causal.connections.codec import dumps
from crucis_causal.experiments.model import digest, qualified, identity
from crucis_causal.experiments.handoff import freeze_s1
from crucis_causal.experiments.resolver import PlanResolver, ReadAccess

HERE = Path(__file__).resolve().parent
CAT = json.loads((ROOT / 'crucis_causal/docs/subsystem3-final-contract-catalog-2026-11-03.json').read_bytes())
VERSION = CAT['version']

def write(name, value):
    path = HERE / name
    if path.exists():
        raise RuntimeError('Preserve old fixture: choose a new revision directory')
    path.write_bytes(dumps(value))

def metadata(label):
    # Reuse accepted metadata APIs, with fresh source, trial and run identities.
    # This authoring helper is not imported by Crucis runtime.
    code = inspect.getsource(existing.ready).replace('def ready(', 'def fresh(')
    code = code.replace("b'Synthetic native metadata descriptor; not executed.'", "Path(__file__).with_name('native_program.py').read_bytes()")
    code = code.replace("b'X,Y\\n0,1\\n1,0\\n'", "b'A,B,C\\n0,1,0\\n1,0,1\\n'")
    code = code.replace("['X','Y']", "['A','B','C']")
    code = code.replace('synthetic no-execution method', 'B00 supplied offline fixture ' + label)
    code = code.replace("'recorded'", "'direct'")
    namespace = dict(vars(existing), __file__=__file__)
    exec(compile(code, '<B00 metadata authoring>', 'exec'), namespace)
    d, context, binding, native, route, initial = namespace['fresh']()
    occurrence = existing.api.ProjectionOccurrence(identity(), identity())
    projection = existing.core.project_request(binding, occurrence, native, route, context)
    assert projection.state == 'completed', projection.diagnostics
    frozen = freeze_s1(context.s1_records.builder.package([projection.value.request]), existing.LIMITS)
    views = {**d.records.base._views, frozen.package_id: frozen}
    # Only the exact reachable supplied closure, not the old helper's other cases.
    selected = set()
    def visit(pid):
        if pid in selected:
            return
        selected.add(pid)
        for desc in views[pid].package['external_packages']:
            visit(desc['package_id'])
    visit(binding['package_id'])
    visit(frozen.package_id)
    paths = []
    for n, pid in enumerate(sorted(selected)):
        name = f'{label}-dependency-{n:02}.json'
        path = HERE / name
        if path.exists():
            raise RuntimeError('Preserve old fixture: choose a new revision directory')
        path.write_bytes(views[pid].source_bytes)
        paths.append(name)
    resolver = PlanResolver([(HERE / p).read_bytes() for p in paths], limits=existing.LIMITS)
    access = ReadAccess(frozenset(selected))
    for pid in selected:
        resolver.closure(pid, access, existing.LIMITS)
    result = {'path': label, 'run_binding': binding, 'request': qualified(projection.value.request, frozen.package_id),
              'attempt': qualified(projection.value.attempt, frozen.package_id), 'R_package_id': frozen.package_id,
              'trial_count': '1', 'dependencies': paths}
    write(label + '-binding.json', result)
    return result, views, selected

def specimen(views, selected):
    """All core record shapes, intentionally unresolved where no effect occurred."""
    from crucis_causal.connections.model import Builder, contract as c1, source, unknown_ref, unresolved
    from crucis_causal.connections.evidence import capture_bytes
    b = Builder('Authored action wire specimens; not an executed interaction')
    endpoint = b.add('endpoint', {'owner': b.producer, 'operation': c1('fixture_question'),
        'request_contract': c1('fixture_question'), 'response_contract': c1('fixture_answer'),
        'input_domains': [], 'allowed_information': unknown_ref('policy'), 'transport': c1('direct'), 'source': source()})
    action = b.add('action_request', {'session': unknown_ref('session'), 'attempt': unknown_ref('attempt'),
        'requester': b.producer, 'endpoint': endpoint, 'arguments': [], 'question': unresolved(),
        'authority': unknown_ref('authority_evidence'), 'native_action_identity': unresolved(), 'source': source()})
    answer = capture_bytes(b, b'Authored answer wire specimen; not an observed delivery.', format_contract=c1('text'))
    response = b.add('action_response', {'request': action, 'responder': b.producer, 'content': [answer],
        'response_state': 'returned', 'delivery': [], 'source': source()})
    companion = freeze_s1(b.package([action, response]), existing.LIMITS)
    write('wire-actions.json', companion.package)
    views = {**views, companion.package_id: companion}
    selected = set(selected) | {companion.package_id}
    pid = identity()
    ids = {kind: identity() for kind in CAT['core_payloads']}
    candidates = {}
    for package in selected:
        for record in views[package].records:
            candidates.setdefault(record['record_type'], (package, record['id']))
    def ref(kind='s3.component'):
        kind = kind if '.' in kind else 's3.' + kind
        if kind.startswith('s3.'):
            return {'binding': 'internal', 'target': ids[kind], 'target_type': kind}
        package, rid = candidates[kind]
        return {'binding': 'external', 'package_id': package, 'target': rid, 'target_type': kind}
    def unknown():
        return {'state': 'unresolved', 'reasons': ['s3.not_observed'], 'evidence': []}
    def ct(name='s3.fixture_raw'):
        return {'name': name, 'version': VERSION}
    def value(expr):
        if expr.endswith('[]'):
            return []
        if expr.startswith('K('):
            return unknown()
        if expr.startswith('IndexList('):
            return {'members': [], 'extent': 'complete_for_scope', 'scope': value('Scope'), 'gaps': []}
        if expr.startswith(('KnownRef', 'Ref')):
            kinds = expr[expr.index('(')+1:-1].split('|') if '(' in expr else ['s3.component']
            return ref(kinds[0])
        if expr in CAT['common_primitives'] and isinstance(CAT['common_primitives'][expr], dict):
            return {k: value(v) for k, v in CAT['common_primitives'][expr].items()}
        if expr in CAT['value_variants']:
            return {k: value(v) for k, v in CAT['value_variants'][expr][0].items()}
        if expr == 'Contract':
            return ct()
        if expr in ['String', 'QName', 'Code']:
            return 's3.fixture_value'
        if expr == 'ID':
            return identity()
        if expr == 'Boolean':
            return False
        if expr == 'Index':
            return '0'
        if expr == 'Hex64':
            return '0' * 64
        if '|' in expr:
            return value(expr.split('|')[0])
        return expr
    records = []
    for kind, fields in CAT['core_payloads'].items():
        payload = {k: value(v) for k, v in fields.items()}
        records.append({'id': ids[kind], 'record_type': kind, 'contract': ct(kind), 'producer': ref(),
                        'created_at': unknown(), 'provenance': {'basis': 'intrinsic', 'evidence': [], 'procedure': unknown(), 'inputs': []},
                        'payload': payload, 'extensions': []})
    bykind = {r['record_type']: r['payload'] for r in records}
    bykind['s3.component']['name'] = 'B00 structural fixture author; no native effect'
    bykind['s3.component']['role'] = 's3.fixture_author'
    bykind['s3.typed_payload']['reference_context'] = {'package_id': pid, 'format': ct('s3.account_package')}
    bykind['s3.operation_binding'].update(operation=ct('s3.op.close_collection'), roles=[
        {'role': 's3.role.period', 'members': {**value('IndexList(Ref)'), 'members': [ref('collection_period')]}},
        {'role': 's3.role.frontier', 'members': {**value('IndexList(Ref)'), 'members': [ref('frontier')]}},
        {'role': 's3.role.obligations', 'members': value('IndexList(Ref)')}], parameters=[
        {'key': k, 'value': {'state': 'known', 'value': v, 'basis': []}}
        for k, v in [('stopping_rule', ct('s3.fixture_bound')), ('reason', 's3.fixture_complete'), ('expected_journal_revision', '0')]])
    bykind['s3.effect_command']['operation'] = ct('s3.op.close_collection')
    bykind['s3.requirement_case']['family'] = ct('s3.family.scientific_binding')
    bykind['s3.requirement_case']['applicability'] = 'not_examined'
    def ext(r):
        return {**r, 'binding': 'external', 'package_id': companion.package_id}
    for kind in ['s3.delivery', 's3.action_decision']:
        bykind[kind]['actions']['members'] = [ext(action)]
    bykind['s3.delivery']['responses']['members'] = [ext(response)]
    bykind['s3.action_decision']['selected']['members'] = [ext(response)]
    axes = {'representation': 'not_examined', 'mechanism': 'not_examined', 'readiness': 'not_examined',
        'authority': 'unresolved', 'enforcement': 'unresolved', 'tests': 'not_run',
        'native_evidence': 'not_examined', 'coverage': 'not_examined'}
    bykind['s3.support_claim']['axes'] = [{'axis': axis, 'status': status,
        'evidence': value('IndexList(Ref)'), 'limits': value('IndexList(Ref)')} for axis, status in axes.items()]
    descriptors = [{'package_id': p, 'format': views[p].format, 'locator': unknown(), 'expected_digest': {'state': 'known', 'value': views[p].snapshot_digest, 'basis': []}, 'access': 's3.fixture_supplied'} for p in sorted(selected)]
    package = {'format': ct('s3.account_package'), 'package_id': pid, 'roots': [ref('account_view')], 'records': records, 'external_packages': descriptors, 'extensions': []}
    write('all-core-records.json', package)

def main():
    bindings = []
    for label in ['local', 'remote', 'interactive', 'checkpoint']:
        binding, views, selected = metadata(label)
        bindings.append(binding)
        if label == 'local':
            specimen(views, selected)
    # Fixed oracle constants are independent of future runtime responses.
    write('oracles.json', {
        'scope': 'Controlled protocol fixtures, not causal correctness or real provider integration',
        'local': {'jobs': '1', 'native_order': ['v1','v2','v0'], 'canonical_order': ['A','B','C'], 'mapping': {'v1':'A','v2':'B','v0':'C'}, 'charge': '0.7', 'cap': '1'},
        'remote': {'jobs_after_lost_ack': '1', 'captures': '3', 'distinct_events': '2', 'charge': '4', 'cap': '10', 'negative_before_delayed_acceptance': 'hold_without_receiver_closure'},
        'interactive': {'same_text_action_occurrences': '2', 'q1_deliveries': '1', 'q2_missing_source_choices': '0', 'q2_missing_source_deliveries': '0', 'policy_consumed': '1', 'policy_remaining': '1', 'native_termination': 'unresolved'},
        'checkpoint': {'scientific_trials': '1', 'attempts': '2', 'required_variants': ['captured_payload','native_reference'], 'restored': ['model','optimizer'], 'unknown': ['rng','history'], 'overlap': 'predecessor_observed_stopped', 'interim_bill': '3', 'replacement_bill': '5', 'successor_bill': '4', 'total': '9', 'cap': '20', 'expired_handle_launches': '0'},
        'faults': 'Every F01-F20 variant in the accepted case plan must run under deterministic barriers with independent durable oracle',
        'no_native_or_S3_execution_during_authoring': True})
    # Pin all inherited negatives plus independently fixed mutations per record.
    write('negative-oracles.json', {'missing_required_field': [{'record_type': k, 'remove': next(iter(v)), 'expected': 'schema_rejection'} for k,v in CAT['core_payloads'].items()],
        'inherited': {n: json.loads((ROOT / ('crucis_causal/docs/' + n)).read_bytes())[key] for n,key in [('subsystem3-complete-package-review-2026-11-03.json','negative_reviews'),('subsystem3-serialization-specimens-2026-11-03.json','counterexamples')]}})
    manifest = {'revision': '1', 'tickets': ['DLV-08','DLV-09','DLV-10'], 'approved_source': 'c2ec53f3a30562fe31690df8ab0d9b1351784996', 'native_execution': False, 'S3_execution': False, 'bindings': bindings,
                'files': [{'path': p.name, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(HERE.iterdir()) if p.suffix in ('.json', '.py')]}
    write('manifest.json', manifest)
    print(json.dumps({'fresh_bindings': len(bindings), 'files': len(manifest['files']), 'core_specimens': len(CAT['core_payloads']), 'native_calls': 0}))

if __name__ == '__main__':
    main()
