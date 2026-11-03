"""Opt-in scientific metadata contracts, SC-2 (DLV-08/09).

Importing this package never imports a native causal-discovery system or reads a
protected store. Execution and scientific metrics remain separate subsystems.
"""
from .errors import ServiceError
from .model import contract,reference,qualified,known,unknown,not_applicable,number
from .api import ReaderLimits,PlanIssue,PlanOp,RecordDelta,PackageView

