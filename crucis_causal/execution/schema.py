"""Closed accepted SC-3 schema and operation/family contracts (DLV-08/09).

Only packaged declarative data is loaded. A contract string never imports code
or retrieves a schema. Preservation checks do not establish admission.
"""
import copy
import json
import re
from functools import lru_cache
from pathlib import Path
from jsonschema import Draft202012Validator
from .model import ExecutionError, VERSION

@lru_cache(maxsize=1)
def _catalog():
    return json.loads(Path(__file__).with_name('catalog.json').read_bytes())

def catalog():
    return copy.deepcopy(_catalog())

def object_schema(fields):
    return {'type': 'object', 'properties': fields, 'required': list(fields), 'additionalProperties': False}

def split(expr):
    depth = 0; start = 0; parts = []
    for i, char in enumerate(expr):
        if char == '(': depth += 1
        elif char == ')': depth -= 1
        elif char == '|' and depth == 0:
            parts.append(expr[start:i]); start = i + 1
    return parts + [expr[start:]]

def expression(expr):
    parts = split(expr)
    if len(parts) > 1:
        return {'anyOf': [expression(x) for x in parts]}
    if expr.endswith('[]'):
        return {'type': 'array', 'items': expression(expr[:-2])}
    cardinality = re.fullmatch(r'(.+)\[(\d+)(?:\.\.(\d+|n))?\]', expr)
    if cardinality:
        base, lower, upper = cardinality.groups()
        out = {'type': 'array', 'items': expression(base), 'minItems': int(lower)}
        if upper != 'n': out['maxItems'] = int(upper if upper is not None else lower)
        return out
    if expr == 'Ref' or expr == 'KnownRef' or expr.startswith(('Ref(', 'KnownRef(')):
        known = expr.startswith('KnownRef')
        kinds = expr[expr.index('(')+1:-1].split('|') if '(' in expr else None
        kinds = [x if '.' in x else 's3.' + x for x in kinds] if kinds else None
        base = {'target': expression('ID'), 'target_type': {'enum': kinds} if kinds else expression('QName')}
        variants = [object_schema({'binding': {'const': 'internal'}, **base}),
                    object_schema({'binding': {'const': 'external'}, 'package_id': expression('ID'), **base})]
        if not known:
            variants.append(object_schema({'binding': {'const': 'unresolved'}, 'target_type': base['target_type'],
                'reason': expression('Code'), 'evidence': {'type': 'array', 'items': {'$ref': '#/$defs/Ref'}}, 'source_labels': expression('String[]')}))
        return {'oneOf': variants}
    if expr.startswith('K('):
        return {'oneOf': [object_schema({'state': {'const': 'known'}, 'value': expression(expr[2:-1]), 'basis': expression('Ref[]')}),
            object_schema({'state': {'const': 'unresolved'}, 'reasons': {**expression('Code[]'), 'minItems': 1}, 'evidence': expression('Ref[]')}),
            object_schema({'state': {'const': 'not_applicable'}, 'rule': expression('Contract'), 'scope': expression('Ref[]')})]}
    if expr.startswith('IndexList('):
        return object_schema({'members': expression(expr[10:-1]+'[]'),
            'extent': {'enum': ['complete_for_scope', 'partial_for_scope', 'not_examined', 'unresolved']},
            'scope': expression('Scope'), 'gaps': expression('KnownRef(diagnostic)[]')})
    if expr in ('true', 'false'):
        return {'const': expr == 'true'}
    if expr[0].islower():
        return {'const': expr}
    return {'$ref': '#/$defs/' + expr}

def fields(shape):
    return object_schema({k: expression(v) for k, v in shape.items()})

@lru_cache(maxsize=1)
def _schema():
    c = _catalog()
    patterns = {'QName': r'^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$',
        'ID': r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$',
        'Index': r'^(0|[1-9][0-9]*)$', 'PositiveIndex': r'^[1-9][0-9]*$',
        'Hex64': r'^[0-9a-f]{64}$', 'IntegerText': r'^-?(0|[1-9][0-9]*)$',
        'DecimalText': r'^-?(0|[1-9][0-9]*)(\.[0-9]+)?([eE][+-]?[0-9]+)?$'}
    defs = {k: {'type': 'string', 'pattern': v} for k, v in patterns.items()}
    defs.update(String={'type': 'string'}, Code=defs['QName'], Boolean={'type': 'boolean'})
    defs.update({k: fields(v) if isinstance(v, dict) else expression(v) for k, v in c['common_primitives'].items()})
    defs['Contract']['properties']['version']['minLength'] = 1
    defs.update({k: {'oneOf': [fields(v) for v in variants]} for k, variants in c['value_variants'].items()})
    defs['Ref'] = expression('Ref'); defs['KnownRef'] = expression('KnownRef')
    defs['SupportAxis'] = {'enum': list(c['support_axis_statuses'])}
    defs['AxisSpecificStatus'] = {'enum': sorted({v for statuses in c['support_axis_statuses'].values() for v in statuses})}
    for name, shape in c['parameter_grammars'].items():
        defs['grammar_' + name] = fields(shape)
        if name[0].isupper(): defs[name] = fields(shape)
    defs['NativeDescriptor'] = fields(c['parameter_grammars']['native_descriptor'])
    defs['Record'] = fields(c['record'])
    defs['Record']['properties']['record_type'] = {'enum': list(c['core_payloads'])}
    defs['Record']['properties']['payload'] = {'type': 'object'}
    defs['Record']['allOf'] = [{'if': {'properties': {'record_type': {'const': kind}}}, 'then': {'properties': {
        'payload': fields(shape), 'contract': {'const': {'name': kind, 'version': VERSION}}}}} for kind, shape in c['core_payloads'].items()]
    defs['Binding'] = fields(c['core_payloads']['s3.operation_binding'])
    # ClosedPayload is resolved per exact record kind above, not a fallback dict.
    root = fields(c['package'])
    root['properties']['format'] = {'const': {'name': 's3.account_package', 'version': VERSION}}
    root['properties']['roots']['items'] = expression('KnownRef(account_view|projection_view)')
    return {'$schema': 'https://json-schema.org/draft/2020-12/schema', **root, '$defs': defs}

def schema():
    return copy.deepcopy(_schema())

def validate_value(value, expr, path=''):
    error = next(Draft202012Validator({'$defs': _schema()['$defs'], **expression(expr)}).iter_errors(value), None)
    if error:
        raise ExecutionError('s3.schema', path + '/' + '/'.join(map(str, error.absolute_path)))

def validate_record(record):
    # Positive structural results only. Exact schema is static/package-owned;
    # per-read limits, calendar/value semantics, references and access are still
    # checked by their callers. No decoded object or authority is cached.
    global _RECORD_CACHE_BYTES
    from .model import canonical
    try: encoded = canonical(record)
    except (TypeError, ValueError): encoded = None
    if encoded is not None:
        with _RECORD_CACHE_LOCK:
            if encoded in _RECORD_CACHE:
                _RECORD_CACHE.move_to_end(encoded)
                return
    validate_value(record, 'Record')
    if encoded is not None and len(encoded) <= _RECORD_CACHE_MAX_BYTES:
        with _RECORD_CACHE_LOCK:
            if encoded not in _RECORD_CACHE:
                while _RECORD_CACHE and (_RECORD_CACHE_BYTES + len(encoded) > _RECORD_CACHE_MAX_BYTES or len(_RECORD_CACHE) >= 8192):
                    old, _ = _RECORD_CACHE.popitem(last=False); _RECORD_CACHE_BYTES -= len(old)
                _RECORD_CACHE[encoded] = True; _RECORD_CACHE_BYTES += len(encoded)


from collections import OrderedDict
import threading
_RECORD_CACHE, _RECORD_CACHE_LOCK = OrderedDict(), threading.RLock()
_RECORD_CACHE_BYTES, _RECORD_CACHE_MAX_BYTES = 0, 67108864

def operation(selected):
    return next((o for o in _catalog()['operations'] if o['contract'] == selected), None)

def role_spec(text):
    found = re.fullmatch(r'(.+)\[(\d+)(?:\.\.(\d+|n))?\]', text)
    if not found:
        raise ExecutionError('s3.invalid_catalog_role')
    kinds, lower, upper = found.groups()
    return kinds.split('|'), int(lower), None if upper == 'n' else int(upper if upper is not None else lower)

def validate_binding(payload, *, admission=False):
    validate_value(payload, 'Binding')
    selected = operation(payload['operation'])
    if selected is None:
        if admission: raise ExecutionError('s3.unsupported_contract')
        return False
    roles = {r['role']: r['members'] for r in payload['roles']}
    expected = {'s3.role.' + k: v for k, v in selected['roles'].items()}
    if len(roles) != len(payload['roles']) or set(roles) != set(expected):
        raise ExecutionError('s3.operation_roles')
    for name, spec in expected.items():
        kinds, lower, upper = role_spec(spec)
        idx = roles[name]
        for ref in idx['members']:
            if ref['target_type'] not in kinds:
                raise ExecutionError('s3.operation_role_type', name)
        if admission and (idx['extent'] != 'complete_for_scope' or not lower <= len(idx['members']) or
                          (upper is not None and len(idx['members']) > upper) or
                          any(r['binding'] == 'unresolved' for r in idx['members'])):
            raise ExecutionError('s3.operation_cardinality_or_knowledge', name)
    parameters = {p['key']: p['value'] for p in payload['parameters']}
    if len(parameters) != len(payload['parameters']) or set(parameters) != set(selected['parameters']):
        raise ExecutionError('s3.operation_parameter_keys')
    for key, expr in selected['parameters'].items():
        val = parameters[key]
        if val['state'] == 'not_applicable':
            if 'NA' not in split(expr): raise ExecutionError('s3.parameter_not_applicable_forbidden', key)
        else:
            validate_value(val, 'K(' + '|'.join(x for x in split(expr) if x != 'NA') + ')', key)
            if admission and val['state'] != 'known':
                raise ExecutionError('s3.parameter_unresolved', key)
    return True

def validate_family(payload):
    families = _catalog()['conditional_families']
    family = next((f for f in families if f['contract'] == payload['family']), None)
    if family is None:
        return False  # Preservable unrecognized meaning; cannot satisfy admission.
    roles = payload['roles']
    if payload['applicability'] != 'applies':
        if roles: raise ExecutionError('s3.inactive_family_roles')
        return True
    allowed = _catalog()['family_role_types'][family['id']]
    if len(roles) != len({r['role'] for r in roles}) or {r['role'] for r in roles} != set(allowed):
        raise ExecutionError('s3.family_roles')
    for role in roles:
        if any(r['target_type'] not in allowed[role['role']].split('|') for r in role['members']['members']):
            raise ExecutionError('s3.family_role_type', role['role'])
    return True
