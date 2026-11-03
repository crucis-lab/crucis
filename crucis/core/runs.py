"""Run records (protocol v1, section 1.1). One record per (system, item, arm).

Statuses are typed so infrastructure never counts as a system failure:
  ok              the system returned a graph
  failed          the system's own fault (exception, crash); counted by K01
  aborted_cap     a spend cap stopped it (resumable)         } infrastructure: excluded from scores,
  aborted_quota   the provider refused (resumable)           } counted and reported, never a crash
  interrupted     stopped from outside                       }
  host_error      the host failed under the system (OSError EIO on the Windows Docker bind mount, seen 14 Oct)  }
  not_run         planned but never executed (e.g. a budget tier left it out)
"""
from dataclasses import dataclass, field

from .graph import Graph

OK, FAILED, NOT_RUN = "ok", "failed", "not_run"
INFRA = ("aborted_cap", "aborted_quota", "interrupted", "host_error")
STATUSES = (OK, FAILED, NOT_RUN) + INFRA


@dataclass
class RunRecord:
    system: str
    item: str
    arm: str
    status: str
    graph: Graph = None
    variants: dict = field(default_factory=dict)        # variant name -> Graph (the system's own intermediate graphs)
    edge_source: dict = field(default_factory=dict)     # (a, b) -> label the system exposes ("data", "llm", ...)
    confidence: dict = field(default_factory=dict)      # claim key -> probability, when the system states one
    cost: dict = field(default_factory=dict)            # usd, calls, seconds
    failure: dict = None
    stages: list = None                                 # [(stage name, Graph)] for L2
    files: dict = field(default_factory=dict)           # role -> {path, sha256} of the raw outputs this record was read from
    notes: dict = field(default_factory=dict)

    def __post_init__(self):
        if self.status not in STATUSES:
            raise ValueError("unknown run status %r" % self.status)
        if self.status == OK and self.graph is None:
            raise ValueError("an ok run needs a graph")

    @property
    def replicates(self):
        """Earlier runs of the same (system, item, arm), e.g. a run repeated after a host error; the record itself is the
        last run. Every count of runs (K01) includes them."""
        return self.notes.get("replicates", [])

    def summary(self):
        return {"system": self.system, "item": self.item, "arm": self.arm, "status": self.status,
                "graph": self.graph.canonical() if self.graph else None, "cost": self.cost, "failure": self.failure,
                "files": self.files, "variants": sorted(self.variants)}


def host_error(failure):
    """A failure that is the host's, not the system's: OSError with errno 5 (Input/output error)."""
    f = failure or {}
    return f.get("type") == "OSError" and ("Errno 5" in str(f.get("message")) or "Input/output error" in str(f.get("message")))


def all_runs(records):
    """Every run, replicates included."""
    for r in records:
        yield from r.replicates
        yield r
