"""SC-2 primitives; identity and byte content remain distinct (DLV-08/09)."""
import copy
import datetime
import hashlib
import uuid
from decimal import Decimal
from .errors import ServiceError

VERSION = '0.1.0-proposal.1'

def contract(name, version=VERSION):
    return {'name':name if '.' in name else 's2.'+name, 'version':version}

def reference(target, kind, package_id=None):
    result={'binding':'external' if package_id else 'internal','target':target,
            'target_type':kind if '.' in kind else 's2.'+kind}
    if package_id: result['package_id']=package_id
    return result

def qualified(ref, package_id):
    if ref.get('binding')!='internal': return copy.deepcopy(ref)
    return {**ref,'binding':'external','package_id':package_id}

def known(value, basis=()): return {'state':'known','value':copy.deepcopy(value),'basis':list(basis)}
def unknown(reason='s2.not_observed', evidence=()): return {'state':'unresolved','reasons':[reason],'evidence':list(evidence)}
def not_applicable(rule='s2.not_applicable', subjects=()): return {'state':'not_applicable','rule':contract(rule),'scope':list(subjects)}
def unknown_ref(kind, reason='s2.unresolved_identity'):
    return {'binding':'unresolved','target_type':kind if '.' in kind else 's2.'+kind,
            'reason':reason,'evidence':[],'source_labels':[]}
def scope(*subjects): return {'subjects':list(subjects),'qualifiers':[]}
def source(producer=None, basis='observed', evidence=(), inputs=()):
    return {'basis':basis,'evidence':list(evidence),'procedure':known(producer) if producer else unknown(),'inputs':list(inputs)}
def index(members=(), extent='complete_for_scope', subjects=(), gaps=()):
    return {'members':list(members),'extent':extent,'scope':scope(*subjects),'gaps':list(gaps)}
def identity(): return str(uuid.uuid4())
def timestamp():
    return {'time_type':'utc_instant','value':datetime.datetime.now(datetime.timezone.utc).isoformat().replace('+00:00','Z'),
            'precision':'fractional_second','clock':unknown(),'uncertainty_seconds':unknown()}
def number(value):
    if isinstance(value,bool) or not isinstance(value,(int,str,Decimal)):
        raise ServiceError('s2.numeric_lexeme_required')
    text=str(value)
    try: val=Decimal(text)
    except Exception as exc: raise ServiceError('s2.invalid_number') from exc
    if not val.is_finite():
        return {'number_type':'nonfinite','value':'nan' if val.is_nan() else 'negative_infinity' if val.is_signed() else 'positive_infinity'}
    import re
    return {'number_type':'integer' if re.fullmatch(r'-?(0|[1-9][0-9]*)',text) else 'finite_decimal','text':text}
def digest(data):
    return {'algorithm':'sha256','value':hashlib.sha256(data).hexdigest(),'byte_length':str(len(data)),'scope':{'kind':'full_content'}}
def walk(value):
    pending=[('',value,0)]
    while pending:
        path,item,depth=pending.pop();yield path,item,depth
        if isinstance(item,dict): pending.extend((path+'/'+str(k).replace('~','~0').replace('/','~1'),v,depth+1) for k,v in item.items())
        elif isinstance(item,list): pending.extend((path+'/'+str(i),v,depth+1) for i,v in enumerate(item))

