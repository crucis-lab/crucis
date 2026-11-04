"""Immutable local artifact bytes, explicitly staged before references (DLV-08/09).

Qualified for cooperative same-host processes/process death, not hostile writers,
shared/network filesystems, whole-host failure, or power-loss durability.
"""
import hashlib
import os
from pathlib import Path
import re
import uuid
from .model import ExecutionError, digest

class ArtifactStore:
    def __init__(self, root, *, max_bytes='67108864', fault=None):
        self.root = Path(root).resolve()
        if str(self.root).startswith('\\\\'):
            raise ExecutionError('s3.network_store_not_qualified')
        if not re.fullmatch(r'[1-9][0-9]*', max_bytes): raise ExecutionError('s3.positive_artifact_limit_required')
        self.max_bytes, self.fault = int(max_bytes), fault
        self.root.mkdir(parents=True, exist_ok=True)
        self.staging = self.root / 'staging'
        self.staging.mkdir(exist_ok=True)

    def _barrier(self, label):
        if self.fault: self.fault(label)

    def _path(self, hexdigest):
        if not isinstance(hexdigest, str) or not re.fullmatch(r'[0-9a-f]{64}', hexdigest):
            raise ExecutionError('s3.full_content_digest_required')
        return self.root / (hexdigest + '.blob')

    def stage(self, data):
        if not isinstance(data, bytes) or len(data) > self.max_bytes:
            raise ExecutionError('s3.artifact_bytes_or_limit')
        bound = digest(data)
        dest = self._path(bound['value'])
        if dest.exists():
            if self.read(bound) != data: raise ExecutionError('s3.artifact_identity_conflict')
            return bound
        temporary = self.staging / (str(uuid.uuid4()) + '.stage')
        # An interrupted stage is retained as an orphan; no root/cursor references it.
        with temporary.open('xb') as stream:
            stream.write(data)
            self._barrier('artifact_before_flush')
            stream.flush()
            os.fsync(stream.fileno())
        self._barrier('artifact_after_flush')
        if hashlib.sha256(temporary.read_bytes()).hexdigest() != bound['value']:
            raise ExecutionError('s3.artifact_stage_integrity')
        try:
            # Exclusive link gives readers only the completely written file. Never
            # replace an existing identity, even if its current bytes are corrupted.
            os.link(temporary, dest)
        except FileExistsError:
            if self.read(bound) != data: raise ExecutionError('s3.artifact_identity_conflict')
        temporary.unlink()
        self._barrier('artifact_after_install')
        return bound

    def read(self, expected):
        if expected.get('algorithm') != 'sha256' or expected.get('scope') != {'kind':'full_content'}:
            raise ExecutionError('s3.full_content_digest_required')
        path = self._path(expected['value'])
        with path.open('rb') as stream:
            data = stream.read(self.max_bytes + 1)
        if len(data) > self.max_bytes or digest(data) != expected:
            raise ExecutionError('s3.artifact_integrity_mismatch')
        return data

    def orphans(self, referenced=()):
        """Inspection only: retention/cleanup is a separately authorized operation."""
        referenced = set(referenced)
        return tuple(sorted(p.name for p in self.root.glob('*.blob') if p.stem not in referenced)) + tuple(sorted('staging/'+p.name for p in self.staging.glob('*.stage')))
