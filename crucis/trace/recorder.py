"""L2 glass-box recorder for Python systems (protocol v1, level L2).

Observation only, the contract of harness/cc_trace.py: every hook calls the original callable with the original arguments
and returns (or re-raises) exactly what the original produced. Nothing is seeded, reordered, retried or copied back.
What it records per call: sequence number, hook name, wall time, an optional stage graph (an extractor turns the call's
arguments or return value into a Graph), and on an exception its type, message and the innermost frame inside the
system's own code. Hooks are installed by dotted path ("package.module:Class.method" or "package.module:function") and
are always removed on exit, also after an exception.

    with Recorder(system_root="/opt/probes/src/matmcd") as rec:
        rec.hook("Utils.CausalDiscovery:causal_discovery", stage="pc", graph_from=lambda ret, a, kw: ...)
        result = system_entry(...)
    rec.stages    -> [(stage name, Graph)]            rec.calls -> [{seq, hook, seconds, ok, error}]
"""
import functools
import importlib
import time
import traceback


def _resolve(path):
    mod, _, qual = path.partition(":")
    owner = importlib.import_module(mod)
    parts = qual.split(".")
    for p in parts[:-1]:
        owner = getattr(owner, p)
    return owner, parts[-1]


class Recorder:
    def __init__(self, system_root=None):
        self.system_root = str(system_root) if system_root else None
        self.calls, self.stages, self.errors = [], [], []
        self._undo = []
        self._seq = 0

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.unhook_all()
        return False

    def hook(self, path, stage=None, graph_from=None, when="return"):
        """Wrap the callable at path. graph_from(ret, args, kwargs) -> Graph or None gives the stage graph:
        when='return' reads it after the call, when='call' before it (the graph handed INTO the step)."""
        owner, attr = _resolve(path)
        orig = getattr(owner, attr)
        rec = self

        @functools.wraps(orig)
        def wrapper(*args, **kwargs):
            rec._seq += 1
            seq, t0 = rec._seq, time.time()
            entry = {"seq": seq, "hook": path, "stage": stage}
            if graph_from is not None and when == "call":
                rec._stage(stage, graph_from, None, args, kwargs, entry)
            try:
                ret = orig(*args, **kwargs)
            except BaseException as e:
                entry.update({"ok": False, "seconds": time.time() - t0, "error": rec._where(e)})
                rec.calls.append(entry)
                rec.errors.append(dict(entry["error"], seq=seq, hook=path, stage=stage))
                raise
            entry.update({"ok": True, "seconds": time.time() - t0})
            if graph_from is not None and when == "return":
                rec._stage(stage, graph_from, ret, args, kwargs, entry)
            rec.calls.append(entry)
            return ret

        setattr(owner, attr, wrapper)
        self._undo.append((owner, attr, orig))
        return wrapper

    def unhook_all(self):
        while self._undo:
            owner, attr, orig = self._undo.pop()
            setattr(owner, attr, orig)

    def _stage(self, stage, graph_from, ret, args, kwargs, entry):
        try:
            g = graph_from(ret, args, kwargs)
        except Exception as e:  # noqa: BLE001  an extractor failure is recorded, never raised into the system
            entry["extract_error"] = "%s: %s" % (type(e).__name__, e)
            return
        if g is not None:
            self.stages.append((stage or entry["hook"], g))

    def _where(self, e):
        tb = traceback.extract_tb(e.__traceback__)
        inner = tb[-1] if tb else None
        mine = [f for f in tb if self.system_root and self.system_root in f.filename]
        fmt = lambda f: "%s:%d (%s)" % (f.filename, f.lineno, f.name)  # noqa: E731
        return {"type": type(e).__name__, "message": str(e)[:300], "innermost_frame": fmt(inner) if inner else None,
                "innermost_system_frame": fmt(mine[-1]) if mine else None}
