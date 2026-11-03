"""Typed supplied artifact payloads, never a generic native metadata bag (DLV-08/09)."""
import base64
import copy
from jsonschema import Draft202012Validator
from .codec import loads
from .errors import ServiceError
from .model import VERSION,walk
from .schema import _catalog,_schema,fields

def read(payload_ref,anchor,resolver,access,limits):
    selected=resolver.record(payload_ref['artifact'],anchor,access,limits)
    if selected.record['record_type']!='s1.artifact_snapshot':raise ServiceError('s2.snapshot_payload_required')
    p=selected.record['payload'];fmt=p['format']
    formats={entry['contract']['name']:entry for entry in _catalog()['payload_contracts'].values()}
    if fmt['state']!='known' or fmt['value']['version']!=VERSION or fmt['value']['name'] not in formats:
        raise ServiceError('s2.unsupported_payload_contract')
    selector=payload_ref['selector']
    if selector['state']!='not_applicable' and not (selector['state']=='known' and selector['value']=={'selector_type':'json_pointer','pointer':''}):
        raise ServiceError('s2.full_typed_payload_selector_required')
    content=p['content']
    if content['content_form']=='inline_utf8':raw=content['text'].encode('utf-8')
    elif content['content_form']=='inline_base64':
        try:raw=base64.b64decode(content['data'],validate=True)
        except ValueError as exc:raise ServiceError('s2.invalid_base64') from exc
        if base64.b64encode(raw).decode('ascii')!=content['data']:raise ServiceError('s2.noncanonical_base64')
    else:raise ServiceError('s2.payload_bytes_not_supplied')
    if len(raw)>int(limits.max_external_bytes):raise ServiceError('s2.external_byte_limit')
    value=loads(raw,limits);spec={'$defs':_schema()['$defs'],**fields(formats[fmt['value']['name']]['fields'])}
    error=next(Draft202012Validator(spec).iter_errors(value),None)
    if error:raise ServiceError('s2.payload_schema','/'+'/'.join(map(str,error.absolute_path)))
    for path,ref,_ in walk(value):
        if isinstance(ref,dict) and 'binding' in ref and 'target_type' in ref:
            if ref['binding']=='internal':raise ServiceError('s2.qualified_payload_reference_required',path)
            if ref['binding']=='external':resolver.record(ref,selected.package_id,access,limits)
    return copy.deepcopy(value)
