"""Shared atomic metadata operations and sourced assessments (DLV-08/09)."""
from .api import PlanOp,PlanIssue,RecordDelta,reject
from .errors import ServiceError
from .model import source,scope,contract,unknown,known
from .schema import catalog

def read_context(context):return context.read if hasattr(context,'read') else context
def draft_context(context):return context.draft if hasattr(context,'draft') else context
def bound(reference,owner,context):
    from .model import qualified
    return reference if owner==read_context(context).active_package else qualified(reference,owner)
def get(ref,context,kind=None):
    read=read_context(context);found=read.resolver.record(ref,read.active_package,read.access,read.limits)
    if kind and found.record['record_type'] not in ({kind} if isinstance(kind,str) else set(kind)):
        raise ServiceError('s2.unexpected_subject_kind',evidence=(ref,))
    return found.record
def atomic(context,build):
    draft=draft_context(context)
    try:
        with draft.records.begin(draft.author,draft.clock) as tx:
            value,issues,roots=build(tx)
            additions=tx.commit();additions=RecordDelta(additions.records,tuple(roots))
        return PlanOp('partial' if issues else 'completed',value,additions,tuple(issues))
    except Exception as exc:return reject(exc)
def parameter(tx,context,name,values=None):
    draft=draft_context(context);values=values or {};schema=catalog()['parameter_schemas'][name]
    if set(values)-set(schema['fields']):raise ServiceError('s2.unrecognized_parameter')
    return tx.add('parameter_set',{'schema':schema['contract'],'bindings':[{'key':k,'role':f['role'],'value':values.get(k,unknown())} for k,f in schema['fields'].items()],
        'source':source(draft.author,basis='derived')})
def diagnostic(tx,context,subjects,code):
    draft=draft_context(context)
    return tx.add('diagnostic',{'subjects':list(subjects),'reasons':[code],'scope':scope(*subjects),'source':source(draft.author,basis='observed')})
def assessment(tx,context,claim,subjects,inputs,result,issues=(),parameters=()):
    draft=draft_context(context)
    gaps=[diagnostic(tx,context,subjects,i.code if isinstance(i,PlanIssue) else i) for i in issues]
    meta=parameter(tx,context,'assessment_context',{'boundary':known(contract('s2.metadata_assessment')),
        'cutoff':known(list(inputs)),'observed_time':known(draft.clock.now()),'limits':known(gaps),'claim_scope':known(list(subjects))})
    return tx.add('assessment',{'claim':claim,'subjects':list(subjects),'inputs':list(inputs),'procedure':draft.author,
        'scope':scope(*subjects),'result':result,'diagnostics':gaps,'parameters':[meta,*parameters],
        'source':source(draft.author,basis='derived',inputs=inputs)})
