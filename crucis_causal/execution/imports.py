"""Supplied historical evidence and pure, explicitly installed interpreters.

DLV-08/09. Import occurrence is a storage key, never a native launch or trial.
No locator, environment file, Python import string or source text is executed.
"""
import copy
from dataclasses import dataclass
import inspect
from . import api,codec
from .journal import binding_digest,resolve_binding
from .model import ExecutionError,canonical,contract,digest,qualified,reference,unknown
from .registry import PayloadRegistry,_verify_implementation
from .schema import validate_binding,validate_value

@dataclass(frozen=True,slots=True)
class ImportedEvidence:
    occurrence:str
    receipt:dict
    snapshot:api.PinnedView
    dependencies:tuple
    native_occurrence:dict
    limitations:tuple

def import_supplied(occurrence,sources,resolver,store,*,reader=None,prior_import=None):
    """Explicit storage-admin helper; B06 admits Driver.read before using it.

    S1 PackageStore's cooperative import-key guarantee is deliberately retained;
    this helper does not promote its lock to a process-crash/distributed lease.
    """
    from crucis_causal.connections.model import Builder,contract as c1,source,unresolved
    from crucis_causal.connections.codec import dumps
    reader=reader or contract('s3.reader.supplied_evidence')
    validate_value(occurrence,'ID')
    if reader!=contract('s3.reader.supplied_evidence'):raise ExecutionError('s3.import_reader_unavailable')
    if not sources:raise ExecutionError('s3.import_sources_required')
    views={};bound=[];missing=[]
    for ref in sources:
        if ref.get('binding')!='external' or ref['target_type'] not in ('s1.artifact_snapshot','s1.artifact_declaration'):
            raise ExecutionError('s3.exact_import_source_required')
        record,pid=resolver.record(ref,ref['package_id'])
        bound.append({'reference':ref,'source_digest':resolver.view(pid).digest,'record':record})
        for v in resolver.closure(pid):
            if v.format['name']!='s1.connection_package':raise ExecutionError('s3.s1_import_dependency_required')
            views[v.package_id]=v
        if record['record_type']=='s1.artifact_declaration':missing.append(ref)
    if prior_import is not None:
        if prior_import.get('binding')!='external' or prior_import.get('target_type')!='s1.import_receipt':raise ExecutionError('s3.exact_prior_import_required')
        resolver.record(prior_import,prior_import['package_id'])
        for v in resolver.closure(prior_import['package_id']):views[v.package_id]=v
    fingerprint={'reader':reader,'sources':bound,'prior_import':prior_import,
        'closure':[{'package_id':v.package_id,'digest':v.digest} for v in views.values()]}
    def create():
        b=Builder('S3 supplied historical evidence reader')
        limits=['s3.original_native_occurrence_unestablished','s3.original_request_attempt_trial_unestablished']
        if missing:limits.append('s3.import_source_bytes_unavailable')
        gaps=[b.add('gap',{'subjects':list(sources),'reasons':[code],
            'scope':{'subjects':list(sources),'qualifiers':[]},'source':source('reconstructed',list(sources),b.producer)}) for code in limits]
        receipt=b.add('import_receipt',{'import_occurrence':occurrence,'sources':list(sources),'reader':b.producer,
            'configuration':unresolved(),'operation_policy':c1('supplied_evidence_import'),'result_roots':list(sources),
            'native_occurrence':unresolved('s1.original_native_occurrence_unestablished'),
            'source':source('reconstructed',[*sources,*([prior_import] if prior_import else [])],b.producer)})
        dependencies=[{'package_id':v.package_id,'locator':unresolved(),'expected_digest':{'state':'known','value':v.digest,'basis':[]},'access':'s1.supplied_metadata'} for v in views.values()]
        return {'package':b.package([receipt,*gaps],external_packages=dependencies),'receipt':receipt,'limits':limits}
    try:stored=store.import_once(occurrence,fingerprint,create)
    except ValueError as exc:raise ExecutionError('s3.import_occurrence_conflict') from exc
    snapshot=codec.parse_snapshot(dumps(stored['package']),resolver.limits)
    dependencies=(*views.values(),snapshot)
    codec.Resolver(dependencies,limits=resolver.limits).closure(snapshot.package_id)
    return ImportedEvidence(occurrence,qualified(stored['receipt'],snapshot.package_id),snapshot,dependencies,
        unknown('s3.original_native_occurrence_unestablished'),tuple(stored['limits']))

def _exact_request(request,context,operation_name):
    if not isinstance(context,api.PinnedReadContext) or not isinstance(request,api.ExactOperationRequest):raise ExecutionError('s3.exact_read_context_required')
    if any(not context.access.permits(v.package_id) for v in context.views):raise ExecutionError('s3.read_denied')
    resolver=codec.Resolver(context.views,limits=context.limits);original=request.binding
    actual=resolve_binding(reference(original.record['id'],'operation_binding',original.context['package_id']),original.context['package_id'],resolver)
    if binding_digest(actual)!=binding_digest(original):raise ExecutionError('s3.binding_pin_mismatch')
    def exact_inputs(entries):
        return [{'role':e.role,'reference':e.reference,'record':e.record,'source_package':e.source_package,'source_digest':e.source_digest} for e in entries]
    if canonical(exact_inputs(actual.inputs.entries))!=canonical(exact_inputs(request.inputs.entries)):
        raise ExecutionError('s3.inputs_substituted')
    validate_binding(actual.record['payload'],admission=True)
    if actual.record['payload']['operation']!=contract(operation_name):raise ExecutionError('s3.operation_mismatch')
    return actual,resolver

def read_import(request,context,store):
    """Exact OP27 backend for a caller-owned local store, not native admission.

    The coordinator must admit its Driver.read wrapper before crossing external
    boundaries. This metadata backend has no provider connection or launch API.
    """
    retained=api.RecordDelta(dependencies=getattr(context,'views',()))
    try:
        actual,resolver=_exact_request(request,context,'s3.op.import_evidence')
        params={p['key']:p['value'] for p in actual.record['payload']['parameters']}
        prior=params['prior_import'];prior=None if prior['state']=='not_applicable' else prior['value']
        if prior is not None:prior=qualified(prior,actual.context['package_id'])
        refs=[qualified(e.reference,e.source_package) for e in actual.inputs.entries]
        value=import_supplied(params['occurrence']['value'],refs,resolver,store,reader=params['reader']['value'],prior_import=prior)
        return api.CallResult('completed',value,records=api.RecordDelta(dependencies=value.dependencies))
    except ExecutionError as exc:return api.rejected(exc.code,records=retained)
    except Exception:return api.rejected('s3.import_commit_unconfirmed',records=retained)

class OutputInterpreter:
    """One installed exact decoder; generic code never guesses native semantics."""
    def __init__(self,decoder,target,selectors_contract,selector_decoder,reader,implementation):
        for value in (decoder,target,selectors_contract):validate_value(value,'Contract')
        if list(inspect.signature(reader).parameters)!=['inputs','selectors','target','context']:
            raise ExecutionError('s3.output_decoder_signature')
        _verify_implementation(implementation)
        self.decoder=copy.deepcopy(decoder);self.target=copy.deepcopy(target)
        self.selectors_contract=copy.deepcopy(selectors_contract);self.reader=reader
        self.implementation=implementation;self.payloads=PayloadRegistry()
        self.payloads.register(selectors_contract,selector_decoder)

    def decode(self,request,context):
        """Exact Driver.decode signature; only supplied immutable read context."""
        sources=api.RecordDelta(dependencies=getattr(context,'views',()))
        try:
            actual,resolver=_exact_request(request,context,'s3.op.decode_output')
            _verify_implementation(self.implementation)
            if request.descriptor.implementation.content_digest!=self.implementation.content_digest or request.descriptor.implementation.reference!=self.implementation.reference:
                raise ExecutionError('s3.output_implementation_pin_mismatch')
            p=actual.record['payload'];validate_binding(p,admission=True)
            if p['operation']!=contract('s3.op.decode_output'):raise ExecutionError('s3.output_operation_mismatch')
            params={entry['key']:entry['value']['value'] for entry in p['parameters']}
            if params['decoder']!=self.decoder or params['target_contract']!=self.target:raise ExecutionError('s3.output_decoder_unavailable')
            selector,pid=resolver.record(params['selectors'],actual.context['package_id'])
            if selector['payload']['payload_contract']!=self.selectors_contract:raise ExecutionError('s3.output_selector_contract')
            selectors=resolver.payload(params['selectors'],actual.context['package_id'],self.payloads)
            # Reader is an explicitly supplied cooperative pure procedure. Its
            # implementation pin identifies it; this is not hostile-code isolation.
            value=self.reader(actual.inputs,selectors,copy.deepcopy(self.target),context)
            if not isinstance(value,api.DriverEvidence):raise ExecutionError('s3.output_decoder_result_contract')
            if value.binding!=reference(actual.record['id'],'operation_binding',actual.context['package_id']):raise ExecutionError('s3.output_decoder_result_binding')
            return api.CallResult('completed',value,records=value.records)
        except ExecutionError as exc:return api.rejected(exc.code,records=sources)
        except Exception:return api.rejected('s3.output_interpretation_unestablished',records=sources)
