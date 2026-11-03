"""Subsystem 1 connection records (DLV-08, DLV-09), opt-in SC-1 contract.

The legacy auditor and certificates retain their existing interfaces. Importing this
package never imports a native system, installs a dependency, or invokes a job.
"""

from .codec import WireError, dumps, loads
from .model import Builder, contract, known, number, reference, unresolved

__all__ = ["Builder", "WireError", "contract", "dumps", "known", "loads", "number", "reference", "unresolved"]
