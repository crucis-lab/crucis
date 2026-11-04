"""SC-3 identities and explicit evidence constructors (DLV-08/09)."""
import copy
import hashlib
import json
import re
import uuid
from decimal import Decimal, InvalidOperation

VERSION = '0.1.0-proposal.3'

class ExecutionError(ValueError):
    """Scoped coordinator/representation error, never a native causal result."""
    def __init__(self, code, path='', evidence=()):
        self.code, self.path, self.evidence = code, path, tuple(evidence)
        super().__init__(code + (':' + path if path else ''))

def identity():
    return str(uuid.uuid4())

def contract(name, version=VERSION):
    return {'name': name if '.' in name else 's3.' + name, 'version': version}

def reference(target, kind, package_id=None):
    out = {'binding': 'external' if package_id else 'internal', 'target': target,
           'target_type': kind if '.' in kind else 's3.' + kind}
    if package_id:
        out['package_id'] = package_id
    return out

def qualified(ref, package_id):
    return {**copy.deepcopy(ref), 'binding': 'external', 'package_id': package_id} if ref['binding'] == 'internal' else copy.deepcopy(ref)

def known(value, basis=()):
    return {'state': 'known', 'value': copy.deepcopy(value), 'basis': list(basis)}

def unknown(reason='s3.not_observed', evidence=()):
    return {'state': 'unresolved', 'reasons': [reason], 'evidence': list(evidence)}

def not_applicable(rule='s3.not_applicable', subjects=()):
    return {'state': 'not_applicable', 'rule': contract(rule), 'scope': list(subjects)}

def unknown_ref(kind, reason='s3.identity_unestablished'):
    return {'binding': 'unresolved', 'target_type': kind if '.' in kind else 's3.' + kind,
            'reason': reason, 'evidence': [], 'source_labels': []}

def scope(*subjects):
    return {'subjects': list(subjects), 'qualifiers': []}

def index(members=(), extent='complete_for_scope', subjects=(), gaps=()):
    return {'members': list(members), 'extent': extent, 'scope': scope(*subjects), 'gaps': list(gaps)}

def source(basis='observed', evidence=(), procedure=None, inputs=()):
    return {'basis': basis, 'evidence': list(evidence), 'procedure': known(procedure) if procedure else unknown(), 'inputs': list(inputs)}

def number(value):
    if isinstance(value, bool) or not isinstance(value, (int, str, Decimal)):
        raise ExecutionError('s3.numeric_lexeme_required')
    text = str(value)
    try:
        d = Decimal(text)
    except InvalidOperation as exc:
        raise ExecutionError('s3.invalid_number') from exc
    if not d.is_finite():
        return {'number_type': 'nonfinite', 'value': 'nan' if d.is_nan() else 'negative_infinity' if d.is_signed() else 'positive_infinity'}
    if re.fullmatch(r'-?(0|[1-9][0-9]*)(\.[0-9]+)?([eE][+-]?[0-9]+)?', text) is None:
        raise ExecutionError('s3.invalid_numeric_lexeme')
    return {'number_type': 'integer' if re.fullmatch(r'-?(0|[1-9][0-9]*)', text) else 'finite_decimal', 'text': text}

def digest(data):
    if not isinstance(data, bytes):
        raise ExecutionError('s3.bytes_required')
    return {'algorithm': 'sha256', 'value': hashlib.sha256(data).hexdigest(), 'byte_length': str(len(data)), 'scope': {'kind': 'full_content'}}

def canonical(value):
    """Internal exact-content comparison; not a scientific canonicalization."""
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode('utf-8')

def walk(value):
    pending = [('', value, 0)]
    while pending:
        path, item, depth = pending.pop()
        yield path, item, depth
        if isinstance(item, dict):
            pending.extend((path + '/' + k.replace('~', '~0').replace('/', '~1'), v, depth + 1) for k, v in item.items())
        elif isinstance(item, list):
            pending.extend((path + '/' + str(i), v, depth + 1) for i, v in enumerate(item))

class Builder:
    """Local staging only; no clock, native call, grant, file read or publication."""
    def __init__(self, name, *, package_id=None, producer_id=None, created_at=None, implementation=None):
        self.package_id = package_id or identity()
        self.producer = reference(producer_id or identity(), 'component')
        self.created_at = copy.deepcopy(created_at) if created_at is not None else unknown('s3.recorder_time_not_supplied')
        self._records = {}
        self.add('component', {'name': name, 'role': 's3.recorder', 'implementation': implementation or unknown()}, record_id=self.producer['target'], basis='intrinsic')

    def add(self, kind, payload, *, record_id=None, basis='observed', evidence=(), procedure=None):
        kind = kind if '.' in kind else 's3.' + kind
        rid = record_id or identity()
        record = {'id': rid, 'record_type': kind, 'contract': contract(kind), 'producer': copy.deepcopy(self.producer),
                  'created_at': copy.deepcopy(self.created_at), 'provenance': source(basis, evidence, procedure), 'payload': copy.deepcopy(payload), 'extensions': []}
        from .schema import validate_record
        validate_record(record)
        old = self._records.get(rid)
        if old is not None and canonical(old) != canonical(record):
            raise ExecutionError('s3.record_identity_conflict')
        self._records[rid] = record
        return reference(rid, kind)

    def ingest(self, records):
        from .schema import validate_record
        if not isinstance(records, (tuple, list)):
            raise ExecutionError('s3.bounded_record_sequence_required')
        for r in records:
            validate_record(r)
            old = self._records.get(r['id'])
            if old is not None and canonical(old) != canonical(r):
                raise ExecutionError('s3.record_identity_conflict')
        for r in records:
            self._records[r['id']] = copy.deepcopy(r)

    def package(self, root, dependencies=()):
        return {'format': contract('account_package'), 'package_id': self.package_id, 'roots': [copy.deepcopy(root)],
                'records': copy.deepcopy(list(self._records.values())), 'external_packages': [
                    {'package_id': v.package_id, 'format': v.format, 'locator': unknown(), 'expected_digest': known(v.digest), 'access': 's3.explicitly_supplied'} for v in dependencies], 'extensions': []}
