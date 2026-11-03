"""jobkit: helpers for resumable, chunked compute jobs (INF-04).

A job script processes a list of work items, appends one JSON record per finished item to a parts file, and stops when its
time budget is used. Run again, it skips finished items. When every item is done it writes the final output with records
sorted by key, so the output is byte-identical however the work was chunked (gate J1).

Exit codes: 0 = complete (prints JOB-COMPLETE), 3 = budget used, more to do.
"""
import hashlib, json, os, platform, sys, time
from pathlib import Path

MORE = 3


class Budget:
    def __init__(self, seconds):
        self.t0, self.seconds = time.time(), seconds

    def left(self):
        return float("inf") if not self.seconds else self.seconds - (time.time() - self.t0)

    def ok(self, need=0.0):
        return self.left() > need


class Parts:
    """Append-only store of finished items: parts.jsonl next to the final output."""

    def __init__(self, out_path):
        self.out = Path(out_path)
        self.parts = self.out.with_name(self.out.name + ".parts.jsonl")
        self.out.parent.mkdir(parents=True, exist_ok=True)
        self.done = {}
        if self.parts.exists():
            for line in open(self.parts, encoding="utf-8"):
                if line.strip():
                    r = json.loads(line)
                    self.done[r["key"]] = r

    def has(self, key):
        return key in self.done

    def add(self, key, record):
        rec = dict(record, key=key)
        with open(self.parts, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, sort_keys=True) + "\n")
        self.done[key] = rec

    def finalize(self, header):
        """Write the final output: header plus records sorted by key. Volatile fields (timing) are kept out of the hashed body."""
        rows = [self.done[k] for k in sorted(self.done)]
        body = {"header": header, "rows": rows}
        txt = json.dumps(body, sort_keys=True, indent=1)
        self.out.write_text(txt, encoding="utf-8")
        return hashlib.sha256(txt.encode()).hexdigest()


def input_key(*paths, extra=""):
    """Content-hash cache key: sha256 over the bytes of every input file plus any parameters (INF-05). Results keyed this way
    are reused only when the inputs are byte-identical, and recomputed when any input changes."""
    h = hashlib.sha256(extra.encode())
    for p in paths:
        h.update(Path(p).read_bytes())
    return h.hexdigest()


def environment():
    mods = {}
    for m in ("numpy", "scipy", "pandas", "sklearn", "networkx", "causallearn", "lingam", "castle"):
        try:
            mods[m] = getattr(__import__(m), "__version__", "present")
        except Exception:
            mods[m] = None
    return {"python": platform.python_version(), "modules": mods}


def finish(parts, header, items_total):
    if len(parts.done) < items_total:
        print("progress %d/%d" % (len(parts.done), items_total))
        sys.exit(MORE)
    h = parts.finalize(header)
    print("JOB-COMPLETE %s sha256=%s" % (parts.out, h))
    sys.exit(0)
