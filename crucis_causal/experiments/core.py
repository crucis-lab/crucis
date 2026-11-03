"""SC-2 metadata entry points; never execution/spend authority (DLV-08/09)."""
from .api import PlanOp,reject
from .codec import dumps
from .errors import ServiceError
from .resolver import parse_snapshot

def read_package(data,context):
    try:return PlanOp('completed',parse_snapshot(data,context.limits))
    except (ValueError,TypeError,KeyError,RecursionError) as exc:return reject(exc)
def encode_package(view):
    from .api import ReaderLimits
    if view.format['name']!='s2.experiment_package':raise ServiceError('s2.sc2_view_required')
    return dumps(view.package,ReaderLimits.standard())
def resolve(reference,context):
    try:return PlanOp('completed',context.resolver.record(reference,context.active_package,context.access,context.limits))
    except (ValueError,TypeError,KeyError) as exc:return reject(exc)

from .profiles import assess
from .selection import resolve_slots
from .bindings import record_materialization,bind_run
from .evaluation import record_population,bind_evaluation
from .lifecycle import record_commitment,record_amendment
from .handoff import project_request,record_handoff,link_evidence
from .legacy import import_legacy,project_legacy

