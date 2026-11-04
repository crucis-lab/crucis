"""Opt-in execution accounts; no import-time execution or dependency probing.

DLV-08/09. Representation, permission, native effect and scientific correctness
are independent judgments. Only explicitly supplied mechanisms can cause effects.
"""
from .model import ExecutionError, VERSION, contract, identity, known, unknown, reference

__all__ = ['ExecutionError', 'VERSION', 'contract', 'identity', 'known', 'unknown', 'reference']

from .core import Core
__all__ += ['Core']
