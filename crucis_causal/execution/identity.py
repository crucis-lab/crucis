"""Actual native connections and exact descriptor coordinates (DLV-08/09)."""
import copy
from dataclasses import dataclass
import weakref
from . import api
from .model import ExecutionError, canonical, contract
from .registry import PayloadRegistry


def validate_descriptor(value):
    PayloadRegistry().decode(contract('s3.payload.native_descriptor'), value)
    return copy.deepcopy(value)


def coordinate(value, *, require_incarnation=True):
    value = validate_descriptor(value)
    incarnation = value['incarnation']
    if require_incarnation and incarnation['state'] != 'known':
        raise ExecutionError('s3.native_incarnation_adequacy_unestablished')
    return (value['authority'], value['namespace'], value['native_id'],
        incarnation['value'] if incarnation['state'] == 'known' else canonical(incarnation))


@dataclass(frozen=True, slots=True)
class ConnectionBinding:
    descriptor: dict
    runtime: object
    role: str
    epoch: str
    source: dict


class NativeConnections:
    """Issuer-owned process-local handle registry, never a native launch cache."""
    def __init__(self): self._handles = weakref.WeakKeyDictionary()

    def bind(self, descriptor, runtime, role, epoch, source):
        descriptor = validate_descriptor(descriptor)
        if runtime is None or isinstance(runtime, (dict, list, tuple, str, bytes, int, float, bool)):
            raise ExecutionError('s3.actual_runtime_connection_required')
        if role not in ('s3.connection.observer', 's3.connection.controller', 's3.connection.consumer') or not isinstance(epoch, str) or not epoch:
            raise ExecutionError('s3.connection_role_epoch_required')
        handle = api.OpaqueHandle(api._OPAQUE_KEY, self)
        self._handles[handle] = ConnectionBinding(descriptor, runtime, role, epoch, copy.deepcopy(source))
        return handle

    def get(self, handle, *, descriptor=None, role=None, epoch=None):
        value = self._handles.get(handle) if isinstance(handle, api.OpaqueHandle) else None
        if value is None: raise ExecutionError('s3.actual_native_connection_required')
        if descriptor is not None and coordinate(descriptor) != coordinate(value.descriptor):
            raise ExecutionError('s3.native_connection_incarnation_mismatch')
        if role is not None and role != value.role: raise ExecutionError('s3.native_connection_role_mismatch')
        if epoch is not None and epoch != value.epoch: raise ExecutionError('s3.native_connection_epoch_mismatch')
        return ConnectionBinding(copy.deepcopy(value.descriptor), value.runtime, value.role, value.epoch, copy.deepcopy(value.source))

    def revoke(self, handle):
        if isinstance(handle, api.OpaqueHandle): self._handles.pop(handle, None)
