"""Opt-in facade over explicitly supplied S3 services (DLV-08/09).

Construction is pure. There is no default driver, evaluator, credential,
filesystem store, provider bootstrap or scientific-scoring implementation.
"""
from . import api,codec
from .coordinator import Coordinator
from .model import ExecutionError
from .registry import SuppliedRegistryContext,ExactDriverRegistry,ExactDecisionRegistry,PayloadRegistry


class Core:
    def __init__(self,*,registry=None,admission_rules=(),collector=None,recovery_intents=None,
                 recovery_policies=None,audience_policies=None):
        self.registry=registry if registry is not None else SuppliedRegistryContext(ExactDriverRegistry(),ExactDecisionRegistry(),PayloadRegistry())
        self.coordinator=Coordinator(admission_rules,collector=collector,recovery_intents=recovery_intents,
            recovery_policies=recovery_policies,audience_policies=audience_policies)

    def context(self,views,*,limits=None):
        limits=limits or api.Limits();resolver=codec.Resolver(views,limits=limits)
        return api.PinnedReadContext(tuple(resolver._views.values()),api.supplied_read(resolver._views),self.registry,limits)

    def inspect(self,view,context):
        if not context.access.permits(view.package_id):raise ExecutionError('s3.read_denied')
        resolver=codec.Resolver(context.views,limits=context.limits);actual=resolver.view(view.package_id)
        if actual.source_bytes!=view.source_bytes:raise ExecutionError('s3.package_identity_conflict')
        counts={}
        for record in actual.records:counts[record['record_type']]=counts.get(record['record_type'],0)+1
        return {'package_id':actual.package_id,'format':actual.format,'digest':actual.digest,'record_counts':counts,
            'declared_dependencies':[v['package_id'] for v in actual.package['external_packages']],
            'scope':'supplied-byte inventory; neither closed dependencies nor native/scientific success'}

    def validate(self,view,context):
        resolver=codec.Resolver(context.views,limits=context.limits)
        if any(not context.access.permits(v.package_id) for v in context.views):raise ExecutionError('s3.read_denied')
        actual=resolver.view(view.package_id)
        if actual.source_bytes!=view.source_bytes:raise ExecutionError('s3.package_identity_conflict')
        closure=resolver.closure(view.package_id)
        return {'package_id':actual.package_id,'digest':actual.digest,'closed_packages':str(len(closure)),
            'scope':'exact supplied-byte structure, identities and dependency pins; no native or causal correctness claim'}

    def plan(self,view,request,context):return self.coordinator.plan(view,request,context)
    def recover(self,view,goal,context):return self.coordinator.recover(view,goal,context)
    def freeze(self,view,audience,claims,context):return self.coordinator.freeze(view,audience,claims,context)


def install_import_reader(registry,component,implementation,boundary,store):
    """Guard the existing supplied-evidence backend with real admission/issue.

    The caller supplies the actual local store. Its cooperative S1 import-key
    profile is retained; no process-crash or distributed guarantee is added.
    """
    from .effects import EffectDriver,EffectMethod
    from .imports import read_import
    from .model import contract,index,qualified,reference
    from .registry import supplied_callable
    selected=contract('s3.op.import_evidence')
    if not callable(getattr(store,'import_once',None)):raise ExecutionError('s3.supplied_import_store_required')
    def prepare(binding,inputs,context):
        values={p['key']:p['value'] for p in binding.record['payload']['parameters']}
        if values['reader']['value']!=contract('s3.reader.supplied_evidence'):raise ExecutionError('s3.import_reader_unavailable')
        return {'occurrence':values['occurrence']['value'],'reader':values['reader']['value']}
    def execute(call):
        result=read_import(call.request,call.context.read,store)
        if result.state=='rejected':return result
        imported=result.value
        evidence=api.DriverEvidence(reference(call.request.binding.record['id'],'operation_binding',call.request.binding.context['package_id']),
            result.records,index(extent='unresolved'),index([imported.receipt]),index(),())
        return api.CallResult(result.state,evidence,records=result.records,issues=result.issues)
    driver=EffectDriver(component,implementation,boundary,component,contract('s3.local_supplied_evidence_import'),
        (EffectMethod(selected,supplied_callable(prepare),supplied_callable(execute),contract('s3.import_runtime_evidence')),))
    driver.install(registry)
    return driver
