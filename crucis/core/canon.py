"""Canonical JSON and hashing. A hash over a JSON object is the sha256 of its canonical form: sorted keys, no whitespace,
UTF-8, floats as Python repr. Tuples and sets are written as sorted lists so the same content always hashes the same."""
import hashlib
import json


def _norm(x):
    if isinstance(x, dict):
        return {str(k): _norm(v) for k, v in x.items()}
    if isinstance(x, (set, frozenset)):
        return sorted((_norm(v) for v in x), key=lambda v: json.dumps(v, sort_keys=True))
    if isinstance(x, (list, tuple)):
        return [_norm(v) for v in x]
    if hasattr(x, "item") and callable(x.item) and not isinstance(x, (str, bytes)):   # numpy scalar
        return x.item()
    return x


def canon(obj):
    return json.dumps(_norm(obj), sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha256_obj(obj):
    return sha256_bytes(canon(obj))


def sha256_file(path, _cache={}):
    """sha256 of a file's bytes; cached per (path, size, mtime) within one process."""
    import os
    st = os.stat(path)
    key = (str(path), st.st_size, st.st_mtime_ns)
    if key not in _cache:
        h = hashlib.sha256()
        with open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
        _cache[key] = h.hexdigest()
    return _cache[key]
