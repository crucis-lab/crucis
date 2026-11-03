"""Parameterised additive reader for the eight existing adapters (DLV-09).

System-specific native parsing stays in existing readers. No branch on system
names is added to the generic contract, mapping, publication or outcome rules.
"""
from ..api import AdapterPorts, EvidenceDelta, Op, SupportClaim, SupportDeclaration
from ..legacy import import_record
from ..model import contract, unresolved
from ..ports import bind_request
from ..codec import WireError


def require_unique_names(names):
    """Explicit prerequisite for a route using core.harness.present's legacy format."""
    if len(set(names))!=len(names):raise WireError('legacy presentation requires unique shown names')
    return tuple(names)


def connection(component, services, adapter, item, arm, *, roots=()):
    def read(source, context, sink):
        before={r['id'] for r in services.records.snapshot()}
        try:
            record=adapter.recorded(item,arm) # Existing recorded reader only; never run/live.
            result=import_record(record,builder=services.records.builder,n=item.n,roots=roots)
        except Exception as exc:
            detail=sink.capture(str(exc).encode('utf-8',errors='backslashreplace'))
            gap=services.records.gap(source.sources,'s1.recorded_read_not_established',[detail])
            delta=EvidenceDelta(tuple(r for r in services.records.snapshot() if r['id'] not in before),
                (detail,),source.sources,(gap,),unresolved())
            return Op('partial',delta,(gap,))
        delta=EvidenceDelta(tuple(r for r in services.records.snapshot() if r['id'] not in before),
            (result['legacy_snapshot'],),(result['root'],),tuple(result['gaps']),unresolved())
        return Op('partial' if result['gaps'] else 'completed',delta,tuple(result['gaps']))
    return AdapterPorts(describe=lambda:SupportDeclaration(component,
        (SupportClaim(contract('legacy_import'),contract('legacy_runrecord_codec'),'recorded','preserve'),),
        ('describe','bind','read')),
        bind=lambda request,presented,route,inventory,context:bind_request(component,services,request,presented,route,inventory,context,allowed_routes=('recorded',)),read=read)
