"""Closed runtime values, independent of wire capabilities (DLV-08/09)."""
import copy
from dataclasses import dataclass, field
from typing import Generic, TypeVar
from .errors import ServiceError
from .model import digest

T=TypeVar('T')

@dataclass(frozen=True, slots=True)
class PlanIssue:
    code:str; path:str=''; message:str=''; evidence:tuple=()

@dataclass(frozen=True, slots=True)
class RecordDelta:
    records:tuple=(); roots:tuple=()

@dataclass(frozen=True, slots=True)
class PlanOp(Generic[T]):
    state:str; value:T|None=None; additions:RecordDelta=field(default_factory=RecordDelta); diagnostics:tuple=()
    def __post_init__(self):
        if self.state not in ('completed','partial','rejected'):raise ServiceError('s2.invalid_operation_state')
        if self.state=='rejected' and (self.value is not None or self.additions.records or self.additions.roots or not self.diagnostics):
            raise ServiceError('s2.rejection_must_be_atomic')
        if self.state=='partial' and (self.value is None or not self.diagnostics):raise ServiceError('s2.partial_requires_useful_value_and_gap')
        if any(not isinstance(x,PlanIssue) for x in self.diagnostics):raise ServiceError('s2.typed_diagnostic_required')

@dataclass(frozen=True, slots=True)
class ReaderLimits:
    max_manifest_bytes:str; max_records:str; max_packages:str; max_external_bytes:str; max_reference_depth:str; max_parameter_depth:str
    def __post_init__(self):
        import re
        for key in self.__slots__:
            value=getattr(self,key)
            if not isinstance(value,str) or not re.fullmatch(r'[1-9][0-9]*',value):raise ServiceError('s2.positive_reader_bound_required',key)
    @classmethod
    def standard(cls): return cls('8388608','20000','128','67108864','64','128')

@dataclass(frozen=True, slots=True)
class PackageView:
    _package:dict; source_bytes:bytes; snapshot_digest:dict; resolved_packages:tuple=()
    def __post_init__(self):object.__setattr__(self,'_package',copy.deepcopy(self._package))
    @property
    def package(self):return copy.deepcopy(self._package)
    @property
    def package_id(self):return self._package['package_id']
    @property
    def format(self):return copy.deepcopy(self._package['format'])
    @property
    def records(self):return tuple(copy.deepcopy(self._package['records']))

ResolvedPackage=PackageView

@dataclass(frozen=True, slots=True)
class ResolvedPlanRecord:
    record:dict; package_id:str; availability:tuple=(); integrity:tuple=()

def reject(error):
    if isinstance(error,ServiceError):issue=PlanIssue(error.code,error.path,str(error),error.evidence)
    else:issue=PlanIssue('s2.observer_contract_error',message=type(error).__name__)
    return PlanOp('rejected',diagnostics=(issue,))

@dataclass(frozen=True, slots=True)
class PlanReadContext:
    limits:ReaderLimits; resolver:object; registry:object; access:object; active_package:str|None=None
    def for_view(self,view):
        from dataclasses import replace
        return replace(self,resolver=self.resolver.with_view(view),active_package=view.package_id)

@dataclass(frozen=True, slots=True)
class DraftContext:
    read:PlanReadContext; identities:object; records:object; author:dict; clock:object
    def __post_init__(self):
        if self.read.active_package!=self.records.package_id or self.author!=self.records.producer:
            raise ServiceError('s2.draft_scope_mismatch')

@dataclass(frozen=True, slots=True)
class PlanAssessmentContext:
    read:PlanReadContext; draft:DraftContext; procedures:object
    def __post_init__(self):
        if self.read is not self.draft.read:raise ServiceError('s2.assessment_view_mismatch')

@dataclass(frozen=True, slots=True)
class PlanValidationReport:
    assessments:tuple; requested:tuple; satisfied:tuple; withheld:tuple; issues:tuple=()

@dataclass(frozen=True, slots=True)
class ResolutionDraft:
    receipt:dict; selected:tuple; outstanding:tuple

@dataclass(frozen=True, slots=True)
class RunBindingDraft:
    binding:dict; outstanding:tuple; assessments:tuple

@dataclass(frozen=True, slots=True)
class ProjectionOccurrence:
    request_id:str; attempt_id:str

@dataclass(frozen=True, slots=True)
class S1RequestProjection:
    request:dict; attempt:dict; presented:object; route:object; s1_records:tuple; provenance:tuple; assessments:tuple

@dataclass(frozen=True, slots=True)
class EvaluationBindingDraft:
    binding:dict; population:dict; outstanding:tuple

@dataclass(frozen=True, slots=True)
class CommitmentEvidence:
    subject:dict; event:dict; assurance:dict; exposure:tuple

@dataclass(frozen=True, slots=True)
class AmendmentEvidence:
    event:dict; affected:dict; reason:str; explanation:dict; prior_observed:dict

@dataclass(frozen=True, slots=True)
class InterpretedValue:
    contract:dict; subjects:tuple; parameters:tuple; evidence:tuple; limits:tuple=()

@dataclass(frozen=True, slots=True)
class FamilyReader:
    contract:dict; implementation:dict; input_contract:dict; output_contract:dict; read:object

@dataclass(frozen=True, slots=True)
class AssessmentProcedure:
    contract:dict; implementation:dict; assess:object

@dataclass(frozen=True, slots=True)
class ProjectionProcedure:
    scientific_operation:dict; native_operation:dict; response:dict; route_kind:str; implementation:dict; project:object

@dataclass(frozen=True, slots=True)
class LegacyProcedure:
    source_contract:dict; target_contract:dict; implementation:dict; import_value:object; project_value:object

@dataclass(frozen=True, slots=True)
class S1ProjectionContext:
    draft:DraftContext; s1_records:object; s1_identities:object; s1_registry:object; s1_recorder:dict; compiler:dict; s1_view:PackageView; projections:object

@dataclass(frozen=True, slots=True)
class LegacyContext:
    draft:DraftContext; s1_read:object; s1_capture:object; s1_services:object; legacy:object

@dataclass(frozen=True, slots=True)
class LegacyImportSource:
    occurrence_id:str; captured_sources:tuple; legacy_contract:dict; source_identity:dict

@dataclass(frozen=True, slots=True)
class LegacyImportScope:
    kind:str; bindings:dict; interpretation_claims:tuple

@dataclass(frozen=True, slots=True)
class LegacyImportDelta:
    receipt:dict; roots:tuple; s1_evidence:tuple; losses:tuple

@dataclass(frozen=True, slots=True)
class LegacyProjectionPolicy:
    rule:dict; selection:dict; require_lossless:bool

@dataclass(frozen=True, slots=True)
class LegacyProjectionDelta:
    projections:tuple; provenance:tuple; losses:tuple

