"""Strict, lossless manifest encoding; DLV-08, DLV-09. Native bytes stay opaque."""
import json
import math


class WireError(ValueError):
    """Manifest encoding/contract error, never a native scientific failure."""


def _pairs(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise WireError("duplicate JSON property: %r" % key)
        out[key] = value
    return out


def _constant(value):
    raise WireError("nonstandard JSON numeric token: " + value)


def _unicode(value):
    if isinstance(value, str):
        if any(0xD800 <= ord(c) <= 0xDFFF for c in value):
            raise WireError("unpaired Unicode surrogate; capture native bytes as base64")
    elif isinstance(value, dict):
        for key, child in value.items():
            if not isinstance(key, str):
                raise WireError("manifest keys must be strings")
            _unicode(key)
            _unicode(child)
    elif isinstance(value, (list, tuple)):
        for child in value:
            _unicode(child)
    elif isinstance(value, float) and not math.isfinite(value):
        raise WireError("nonfinite manifest number must use a tagged representation")


def loads(data):
    """Decode strict UTF-8 JSON, rejecting duplicates before data can be overwritten."""
    try:
        if isinstance(data, bytes):
            data = data.decode("utf-8", errors="strict")
        value = json.loads(data, object_pairs_hook=_pairs, parse_constant=_constant)
        _unicode(value)
        return value
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise WireError(str(exc)) from exc


def dumps(value):
    """Deterministic manifest representation, not a new scientific canonical hash."""
    _unicode(value)
    try:
        return (json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2) + "\n").encode("utf-8")
    except (TypeError, ValueError, UnicodeError) as exc:
        raise WireError(str(exc)) from exc
