"""The adapter interface (protocol v1, section 2.2), designed against PC, GES, MATMCD, Vashishtha et al., PyWhy-LLM,
causaliq and Causal-Copilot (design table: claude/audit-package-design-2026-10-30.md section 2.1).

An adapter declares what it TAKES and what it GIVES; the harness owns everything else (column shuffle and the mapping back,
names arms, the file label, caps). Three modes:
  recorded  read a past run of the system (no spend; this is how the existing audits rerun)
  replay    re-execute the system with its recorded model answers (no spend; needs the system's environment)
  live      execute and spend; refused unless the caller passes allow_spend=True and caps
"""
from dataclasses import dataclass, field

INPUTS = frozenset({"data", "names", "context", "interventions", "knowledge"})
MARKS = frozenset({"->", "--", "<->", "o->", "o-o", "o-", "~", "mixed"})
MODES = frozenset({"live", "replay", "recorded"})


@dataclass(frozen=True)
class Capabilities:
    takes: frozenset
    marks: frozenset
    edge_source: bool = False
    confidence: bool = False
    variants: dict = field(default_factory=dict)          # role -> variant name, e.g. {"data_only": "pc_only_initial"}
    glass_box: dict = None                                # {"entry": "module:function", "stages": [...]}
    modes: frozenset = frozenset({"recorded"})
    cost: str = "cpu"                                     # "cpu" | "llm"

    def __post_init__(self):
        bad = (set(self.takes) - INPUTS) | (set(self.marks) - MARKS) | (set(self.modes) - MODES)
        if bad:
            raise ValueError("undeclared capability values: %s" % sorted(bad))
        if self.cost not in ("cpu", "llm"):
            raise ValueError("cost must be cpu or llm")

    def to_json(self):
        return {"takes": sorted(self.takes), "marks": sorted(self.marks), "edge_source": self.edge_source,
                "confidence": self.confidence, "variants": dict(self.variants), "glass_box": self.glass_box,
                "modes": sorted(self.modes), "cost": self.cost}


@dataclass
class Presented:
    """What the system may see, in SHOWN column order. The system never sees the true order or the reference graph."""
    data: object                 # n x d array, or None for a names-only system
    names: list
    context: str
    file_label: str              # opaque label; an adapter that needs a file writes it under this name
    interventions: dict = None   # {"targets": [...], "rows": array} in shown positions, D+I only
    knowledge: dict = None       # {"required": [(a, b)], "forbidden": [(a, b)], "tiers": [...]} in shown positions
    seed: int = 0


class SpendRefused(RuntimeError):
    pass


class Adapter:
    """Subclasses set name, version and capabilities, and implement recorded() and, where they can, run()."""
    name = None
    version = None
    capabilities = None

    def identity(self):
        """Code identity of the adapter and of the system it wraps (filled by subclasses)."""
        import inspect
        from .canon import sha256_file
        f = inspect.getsourcefile(type(self))
        return {"adapter": self.name, "adapter_version": self.version, "adapter_file_sha256": sha256_file(f)}

    def recorded(self, item, arm, **ref):
        """-> RunRecord over the item's ORIGINAL column indices, read from the system's stored outputs."""
        raise NotImplementedError

    def run(self, presented, budget, out_dir, mode="live", allow_spend=False):
        """-> RunRecord over SHOWN positions (the harness maps it back)."""
        if mode == "live" and self.capabilities.cost == "llm" and not allow_spend:
            raise SpendRefused("%s live spends API credit: pass allow_spend=True with caps (Uzair's go)" % self.name)
        raise NotImplementedError("%s has no %s mode in this package version" % (self.name, mode))


_REGISTRY = {}


def register(cls):
    _REGISTRY[cls.name] = cls
    return cls


def get(name, **kw):
    from .. import systems  # noqa: F401  (imports every adapter module, which registers it)
    return _REGISTRY[name](**kw)


def names():
    from .. import systems  # noqa: F401
    return sorted(_REGISTRY)
