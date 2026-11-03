"""Strict bounded SC-2 bytes and local shape checks (DLV-08/09)."""
import copy
import json
import datetime
from decimal import Decimal
from functools import lru_cache
from jsonschema import Draft202012Validator
from .errors import ServiceError
from .model import VERSION, walk
from .schema import _catalog, _schema, expression

def _unique(pairs):
    result={}
    for k,v in pairs:
        if k in result:raise ServiceError('s2.duplicate_property',k)
        result[k]=v
    return result
def _constant(value):raise ServiceError('s2.nonstandard_json_number',message=value)
def loads(data,limits):
    if not isinstance(data,bytes):raise ServiceError('s2.bytes_required')
    if len(data)>int(limits.max_manifest_bytes):raise ServiceError('s2.manifest_limit')
    try:
        text=data.decode('utf-8',errors='strict')
        value=json.loads(text,object_pairs_hook=_unique,parse_constant=_constant)
        check_tree(value,limits)
        return value
    except (UnicodeError,json.JSONDecodeError,RecursionError,ValueError) as exc:
        if isinstance(exc,ServiceError):raise
        raise ServiceError('s2.invalid_json_or_unicode',message=str(exc)[:160]) from exc
def check_tree(value,limits):
    for path,item,depth in walk(value):
        if depth>int(limits.max_parameter_depth):raise ServiceError('s2.parameter_depth_limit',path)
        if isinstance(item,(int,float)) and not isinstance(item,bool):raise ServiceError('s2.tagged_numeric_value_required',path)
        if isinstance(item,str) and any(0xD800<=ord(c)<=0xDFFF for c in item):raise ServiceError('s2.invalid_unicode_scalar',path)
        if isinstance(item,dict) and any(not isinstance(k,str) or any(0xD800<=ord(c)<=0xDFFF for c in k) for k in item):raise ServiceError('s2.invalid_property_name',path)
@lru_cache(maxsize=1)
def _validator():return Draft202012Validator(_schema())
def validate_parameter(payload):
    schemas=_catalog()['parameter_schemas'];selected=next((x for x in schemas.values() if x['contract']==payload['schema']),None)
    if selected is None:return False
    bindings={b['key']:b for b in payload['bindings']}
    if len(bindings)!=len(payload['bindings']) or set(bindings)!=set(selected['fields']):raise ServiceError('s2.parameter_keys')
    for key,field in selected['fields'].items():
        b=bindings[key]
        if b['role']!=field['role']:raise ServiceError('s2.parameter_role',key)
        spec={'$defs':_schema()['$defs'],**expression('K('+field['type']+')')}
        error=next(Draft202012Validator(spec).iter_errors(b['value']),None)
        if error:raise ServiceError('s2.parameter_type',key)
        if b['value']['state']!='known':continue
        value=b['value']['value']
        if field['enum'] and value not in field['enum']:raise ServiceError('s2.parameter_enum',key)
        for c in field.get('constraints',[]):
            if value['number_type']=='nonfinite':raise ServiceError('s2.finite_parameter_required',key)
            d=Decimal(value['text'])
            if c=='nonnegative_integer_when_known' and (value['number_type']!='integer' or d<0):raise ServiceError('s2.nonnegative_count_required',key)
            if c=='finite_nonnegative_when_known' and d<0:raise ServiceError('s2.nonnegative_parameter_required',key)
    if payload['schema']==schemas['response_group']['contract']:
        value=lambda k:bindings[k]['value'].get('value')
        minimum,maximum=value('minimum'),value('maximum')
        if value('maximum_kind')=='finite' and minimum is not None and maximum is not None:
            if Decimal(maximum['text'])<Decimal(minimum['text']):raise ServiceError('s2.invalid_response_cardinality')
    return True
def validate_package(package,limits):
    check_tree(package,limits)
    if not isinstance(package,dict):raise ServiceError('s2.package_required')
    records=package.get('records',[])
    if len(records)>int(limits.max_records):raise ServiceError('s2.record_limit')
    error=next(_validator().iter_errors(package),None)
    if error:raise ServiceError('s2.schema','/'+'/'.join(map(str,error.absolute_path)),message=error.message[:240])
    mapping={r['id']:r for r in records}
    if len(mapping)!=len(records):raise ServiceError('s2.duplicate_record_identity')
    external=[p['package_id'] for p in package['external_packages']]
    if len(external)!=len(set(external)) or package['package_id'] in external:raise ServiceError('s2.duplicate_or_self_package_descriptor')
    roots=[(r.get('target_type'),r.get('target')) for r in package['roots']]
    if len(roots)!=len(set(roots)) or any(r['binding']!='internal' for r in package['roots']):raise ServiceError('s2.local_unique_roots_required')
    for path,r,_ in walk(package):
        if not isinstance(r,dict):continue
        if r.get('time_type')=='utc_instant':
            try:
                if not r['value'].endswith('Z'):raise ValueError('UTC marker required')
                datetime.datetime.fromisoformat(r['value'].replace('Z','+00:00'))
            except (ValueError,TypeError):raise ServiceError('s2.invalid_utc_instant',path)
        if r.get('binding')=='internal':
            actual=mapping.get(r['target'])
            if not actual or actual['record_type']!=r['target_type']:raise ServiceError('s2.reference_target',path)
        elif r.get('binding')=='external' and r['package_id'] not in external:raise ServiceError('s2.undeclared_external_package',path)
        if r.get('extent')=='not_examined' and r.get('members'):raise ServiceError('s2.unexamined_members',path)
        if 'minimum' in r and isinstance(r.get('maximum'),dict) and r['maximum'].get('kind')=='finite' and int(r['minimum'])>int(r['maximum']['value']):raise ServiceError('s2.invalid_cardinality',path)
    for r in records:
        if r['record_type']=='s2.parameter_set':validate_parameter(r['payload'])
    return package
def record_bytes(record):
    try:return json.dumps(record,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode('utf-8')
    except (TypeError,ValueError,UnicodeError,RecursionError) as exc:raise ServiceError('s2.encoding_error') from exc
def dumps(package,limits):
    validate_package(package,limits);p=copy.deepcopy(package)
    p['records'].sort(key=lambda r:r['id']);p['external_packages'].sort(key=lambda r:r['package_id']);p['roots'].sort(key=lambda r:(r['target_type'],r['target']))
    raw=record_bytes(p)
    if len(raw)>int(limits.max_manifest_bytes):raise ServiceError('s2.manifest_limit')
    return raw

