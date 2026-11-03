"""Typed observer errors; never native failure attribution (DLV-08/09)."""

class ServiceError(ValueError):
    def __init__(self, code, path='', evidence=(), message=''):
        super().__init__(message or code)
        self.code, self.path, self.evidence = code, path, tuple(evidence)

