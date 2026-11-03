"""Exact offline registries and caller-owned identity/clock services (DLV-08/09)."""
import copy
import json
from dataclasses import replace
from .api import FamilyReader,AssessmentProcedure,ProjectionProcedure,LegacyProcedure
from .codec import record_bytes
from .errors import ServiceError
from .model import identity,timestamp,digest

def key(contract):return contract['name'],contract['version']

class ClockService:
    def now(self):return timestamp()

class IdentityService:
    def __init__(self,store=None):self.store=store
    def allocate(self):return identity()
    def import_once(self,occurrence,bound_digest,create):
        if self.store is None:raise ServiceError('s2.persistent_occurrence_store_required')
        from .schema import expression,_schema
        from jsonschema import Draft202012Validator
        for value,typ in [(occurrence,'ID'),(bound_digest,'Digest')]:
            if not Draft202012Validator({'$defs':_schema()['$defs'],**expression(typ)}).is_valid(value):raise ServiceError('s2.invalid_occurrence_binding')
        return self.store.import_once(occurrence,bound_digest,create)

class OccurrenceStore:
    """Explicit durable metadata store; no native identity or implicit deduplication."""
    def __init__(self,root):
        from pathlib import Path
        self.root=Path(root).resolve();self.root.mkdir(parents=True,exist_ok=True)
    def import_once(self,occurrence,bound_digest,create):
        from crucis.connections.store import _atomic,_lock
        from .api import ReaderLimits
        from .codec import loads
        from jsonschema import Draft202012Validator
        from .schema import _schema,expression
        for value,typ in [(occurrence,'ID'),(bound_digest,'Digest')]:
            if not Draft202012Validator({'$defs':_schema()['$defs'],**expression(typ)}).is_valid(value):raise ServiceError('s2.invalid_occurrence_binding')
        path=self.root/(occurrence+'.json')
        with _lock(path.with_suffix('.lock')):
            if path.exists():
                receipt=loads(path.read_bytes(),ReaderLimits.standard())
                if receipt['bound_digest']!=bound_digest:raise ServiceError('s2.occurrence_input_conflict')
                return copy.deepcopy(receipt['result'])
            result=create()
            # Strict JSON-compatible metadata only, never pickle/runtime values.
            from .codec import check_tree
            check_tree(result,ReaderLimits.standard())
            _atomic(path,record_bytes({'occurrence':occurrence,'bound_digest':bound_digest,'result':result}))
            return copy.deepcopy(result)

class ExactRegistry:
    expected=None;callback=None
    def __init__(self):self._entries={}
    def _key(self,entry):return key(entry.contract)
    def register(self,entry):
        if not isinstance(entry,self.expected) or not callable(getattr(entry,self.callback)):
            raise ServiceError('s2.typed_registry_entry_required')
        k=self._key(entry)
        if k in self._entries:raise ServiceError('s2.duplicate_registration')
        self._entries[k]=copy.deepcopy(entry)
    def lookup(self,contract):return copy.deepcopy(self._entries.get(key(contract)))

class FamilyRegistry(ExactRegistry):expected=FamilyReader;callback='read'
class AssessmentRegistry(ExactRegistry):expected=AssessmentProcedure;callback='assess'
class ProjectionRegistry(ExactRegistry):
    expected=ProjectionProcedure;callback='project'
    def _key(self,e):return key(e.scientific_operation),key(e.native_operation),key(e.response),e.route_kind
    def lookup(self,scientific_operation,native_operation,response,route_kind):
        return copy.deepcopy(self._entries.get((key(scientific_operation),key(native_operation),key(response),route_kind)))
class LegacyRegistry(ExactRegistry):
    expected=LegacyProcedure;callback='import_value'
    def _key(self,e):return key(e.source_contract),key(e.target_contract)
    def register(self,e):
        if not isinstance(e,LegacyProcedure) or not callable(e.project_value):raise ServiceError('s2.typed_legacy_procedure_required')
        super().register(e)
    def lookup(self,source,target):return copy.deepcopy(self._entries.get((key(source),key(target))))
