"""Numbers with their sources (protocol v1, section 1.7).

Every number a report prints is a Num: its value, the file it was derived from (path + sha256) or the stored file it is
compared with, a JSON pointer into that file where the number lives, and the derivation (function and arguments).
"""
import json
from dataclasses import dataclass, field

from .canon import sha256_file
from .paths import ROOT


def pointer_get(obj, pointer):
    """RFC 6901 JSON pointer ('/a/b/0'); '~1' is '/', '~0' is '~'."""
    if pointer in ("", "/"):
        return obj
    for tok in pointer.lstrip("/").split("/"):
        tok = tok.replace("~1", "/").replace("~0", "~")
        obj = obj[int(tok)] if isinstance(obj, list) else obj[tok]
    return obj


def pointer(*parts):
    return "/" + "/".join(str(p).replace("~", "~0").replace("/", "~1") for p in parts)


_JSON = {}


def load_json(path):
    p = ROOT / path
    key = (str(p), p.stat().st_mtime_ns)
    if key not in _JSON:
        _JSON[key] = json.loads(p.read_text(encoding="utf-8"))
    return _JSON[key]


def stored(path, ptr):
    """(value, source) of a number in a stored results file."""
    return pointer_get(load_json(path), ptr), {"file": path, "sha256": sha256_file(ROOT / path), "pointer": ptr}


@dataclass
class Num:
    value: object
    unit: str = ""
    source: dict = None
    derivation: dict = field(default_factory=dict)

    def to_json(self):
        return {"value": self.value, "unit": self.unit, "source": self.source, "derivation": self.derivation}
