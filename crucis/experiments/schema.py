"""Static accepted SC-2 catalog compiler; no document parsing (DLV-08/09)."""
import copy
import json
from functools import lru_cache
from pathlib import Path
from crucis.connections.schema import SHAPES as S1_SHAPES, VARIANTS as S1_VARIANTS
from .model import VERSION

@lru_cache(maxsize=1)
def _catalog():return json.loads(Path(__file__).with_name('catalog.json').read_text(encoding='utf-8'))
def catalog():return copy.deepcopy(_catalog())
def object_schema(fields):return {'type':'object','properties':fields,'required':list(fields),'additionalProperties':False}
def split(expr):
    depth=0;start=0;parts=[]
    for i,ch in enumerate(expr):
        if ch=='(':depth+=1
        elif ch==')':depth-=1
        elif ch=='|' and not depth:parts.append(expr[start:i]);start=i+1
    return parts+[expr[start:]]
def expression(expr):
    parts=split(expr)
    if len(parts)>1:return {'anyOf':[expression(p) for p in parts]}
    if expr.endswith('[]'):return {'type':'array','items':expression(expr[:-2])}
    if expr=='Ref' or expr.startswith('Ref('):
        kinds=[k if '.' in k else 's2.'+k for k in expr[4:-1].split('|')] if expr!='Ref' else None
        base={'target':expression('ID'),'target_type':{'enum':kinds} if kinds else expression('QName')}
        return {'oneOf':[object_schema({'binding':{'const':'internal'},**base}),
            object_schema({'binding':{'const':'external'},'package_id':expression('ID'),**base}),
            object_schema({'binding':{'const':'unresolved'},'target_type':base['target_type'],'reason':expression('Code'),'evidence':{'type':'array','items':{'$ref':'#/$defs/Ref'}},'source_labels':expression('String[]')})]}
    if expr.startswith('K('):
        return {'oneOf':[object_schema({'state':{'const':'known'},'value':expression(expr[2:-1]),'basis':expression('Ref[]')}),
            object_schema({'state':{'const':'unresolved'},'reasons':{**expression('Code[]'),'minItems':1},'evidence':expression('Ref[]')}),
            object_schema({'state':{'const':'not_applicable'},'rule':expression('Contract'),'scope':expression('Ref[]')})]}
    if expr.startswith('IndexList('):return object_schema({'members':expression(expr[10:-1]+'[]'),'extent':{'enum':['complete_for_scope','partial_for_scope','not_examined','unresolved']},'scope':expression('Scope'),'gaps':expression('Ref(diagnostic|s1.gap)[]')})
    if expr in ('true','false'):return {'const':expr=='true'}
    if expr[0].islower() or expr in ('T1','T2','T3','T4'):return {'const':expr}
    return {'$ref':'#/$defs/'+expr}
def fields(mapping):return object_schema({k:expression(v) for k,v in mapping.items()})
@lru_cache(maxsize=1)
def _schema():
    qname=r'^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$'
    defs={k:{'type':'string'} for k in ('String','NonemptyString','QName','Code','ID','Index','Hex64','IntegerText','DecimalText')}
    patterns={'QName':qname,'Code':qname,'ID':r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$','Index':r'^(0|[1-9][0-9]*)$','Hex64':r'^[0-9a-f]{64}$','IntegerText':r'^-?(0|[1-9][0-9]*)$','DecimalText':r'^-?(0|[1-9][0-9]*)(\.[0-9]+)?([eE][+-]?[0-9]+)?$'}
    for k,p in patterns.items():defs[k]['pattern']=p
    defs['NonemptyString']['minLength']=1;defs['Boolean']={'type':'boolean'}
    shapes={k:copy.deepcopy(S1_SHAPES[k]) for k in ('Contract','Unit','Scope','NativeIdentity','Endpoint','Extension')}
    shapes.update({'ScopedKey':{'namespace':'String','key':'String'},'Source':{'basis':'reported|observed|reconstructed|derived|intrinsic','evidence':'Ref[]','procedure':'K(Ref(s2.component|s1.component))','inputs':'Ref[]'},'PayloadRef':{'artifact':'Ref(s1.artifact_snapshot)','selector':'K(Selector)'},'Digest':{'algorithm':'sha256','value':'Hex64','byte_length':'Index','scope':'ByteScope'},'Cardinality':{'minimum':'Index','maximum':'Maximum'},'Deliverable':{'role':'Code','contract':'Contract','scope':'Scope','cardinality':'Cardinality','required':'Boolean','abstention':'allowed|forbidden','parameters':'Ref(parameter_set)[]'},'ParameterBinding':{'key':'String','role':'Code','value':'K(ParameterValue)'},'ResolutionEntry':{'role':'Code','requirement':'Ref','selected':'IndexList(Ref)','rule':'Contract','basis':'Ref[]'},'PopulationEntry':{'key':'String','unit':'Ref','members':'Endpoint[]','disposition':'included|excluded|unmatched|unresolved|not_applicable','reasons':'Code[]','basis':'Ref[]','weight':'K(Number)'},'ContentBinding':{'package_id':'ID','digest':'Digest','selected_records':'ID[]'},'ProfileClaim':{'profile':'Contract','families':'Contract[]','scope':'Scope','evidence':'Ref[]','limits':'Ref(diagnostic)[]'},'ExternalPackage':{'package_id':'ID','format':'Contract','locator':'K(String)','expected_digest':'K(Digest)','access':'Code'}})
    shapes.update(_catalog()['auxiliary_payload_shapes'])
    defs.update({k:fields(v) for k,v in shapes.items()})
    variants=copy.deepcopy(S1_VARIANTS)
    variants['Maximum']=[{'kind':'finite','value':'Index'},{'kind':'unbounded'}]
    variants['Time'][0]['clock']='K(Ref(s2.component|s1.component))'
    variants['BytePayload'][2]['locations']='Ref(s1.location)[]'
    variants['Selector'][3]['axes']='Ref(s1.schema)'
    defs.update({k:{'oneOf':[fields(v) for v in cases]} for k,cases in variants.items()})
    defs['Ref']=expression('Ref');defs['ParameterValue']=expression(_catalog()['parameter_value']);defs['Tier']={'enum':['T1','T2','T3','T4']}
    cases=[]
    for name,payload in _catalog()['core_payloads'].items():
        cases.append({'if':{'properties':{'record_type':{'const':name}}},'then':{'properties':{'payload':fields(payload),'contract':{'const':{'name':name,'version':VERSION}}}}})
    defs['Record']=object_schema({'id':expression('ID'),'record_type':{'enum':list(_catalog()['core_payloads'])},'contract':expression('Contract'),'producer':expression('Ref(component)'),'created_at':expression('K(Time)'),'payload':{'type':'object'},'extensions':expression('Extension[]')})
    defs['Record']['allOf']=cases
    root=object_schema({'format':{'const':{'name':'s2.experiment_package','version':VERSION}},'package_id':expression('ID'),'roots':{**expression('Ref[]'),'minItems':1},'records':expression('Record[]'),'external_packages':expression('ExternalPackage[]'),'extensions':expression('Extension[]')})
    return {'$schema':'https://json-schema.org/draft/2020-12/schema',**root,'$defs':defs}
def schema():return copy.deepcopy(_schema())

