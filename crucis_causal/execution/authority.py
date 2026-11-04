"""Actual issuer-owned process capabilities, never receipt deserialization.

DLV-08/09. Cooperative Python capability boundaries; not hostile-code isolation.
"""
import threading
import weakref
from . import api
from .model import ExecutionError,canonical

class Authority:
    def __init__(self):
        self._issued=weakref.WeakKeyDictionary();self._lock=threading.RLock()

    def issue(self, binding, *, control=False):
        cls=api.OpaqueControlCapability if control else api.OpaqueGrant
        cap=cls(api._OPAQUE_KEY,self)
        with self._lock:self._issued[cap]=canonical(binding)
        return cap

    def check(self,cap,binding):
        if not isinstance(cap,(api.OpaqueControlCapability,api.OpaqueGrant)):
            raise ExecutionError('s3.actual_owner_capability_required')
        with self._lock:
            if self._issued.get(cap)!=canonical(binding):raise ExecutionError('s3.owner_capability_binding_mismatch')

    def revoke(self,cap):
        with self._lock:
            if isinstance(cap,(api.OpaqueControlCapability,api.OpaqueGrant)):self._issued.pop(cap,None)

def require_owner_grants(entries,binding,boundary):
    """Current per-owner checks; no distributed atomicity/receiver fence inferred.

    Each entry is (supplied owner port, its actual result, owner control context).
    Pure missingness checks precede any further admitted owner query. Existing
    partial holds remain untouched if another owner is unavailable or denies.
    """
    if not entries:raise ExecutionError('s3.required_owner_set_unestablished')
    for owner,result,context in entries:
        if not isinstance(result,api.CallResult) or result.state!='completed' or not isinstance(result.value,api.OwnerReceiptAndOptionalLiveGrant) or not isinstance(result.value.grant,api.OpaqueGrant):
            raise ExecutionError('s3.owner_group_incomplete')
        ref=result.value.receipt
        view=next((v for v in result.records.dependencies if v.package_id==ref.get('package_id')),None)
        record=next((r for r in view.records if r['id']==ref['target']),None) if view else None
        if record is None or record['record_type']!='s3.owner_receipt' or record['payload']['decision']!='permitted':
            raise ExecutionError('s3.owner_decision_unestablished')
    for owner,result,context in entries:
        checked=owner.check(result.value.grant,binding,boundary,context)
        if checked.state!='completed' or checked.value.decision!='permitted':raise ExecutionError('s3.owner_group_not_current')
    return tuple(result.value.grant for owner,result,context in entries)
