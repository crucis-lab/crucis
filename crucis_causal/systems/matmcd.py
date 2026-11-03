"""MATMCD (D2I-Group/matmcd, MIT): PC, then an LLM constraint matrix, then PC with those constraints (CC-Agent only).
Takes data, names and a theme; exposes the source of every final arrow and its own first PC graph (data only)."""
from ..core.adapter import Capabilities, register
from ._probe import ProbeAgent


@register
class MATMCD(ProbeAgent):
    name, version = "matmcd", "1"
    capabilities = Capabilities(takes=frozenset({"data", "names", "context"}), marks=frozenset({"->", "--"}),
                                edge_source=True, variants={"data_only": "pc_only_initial"},
                                glass_box={"entry": "ConstrainAgent.ConstrainAgent:ConstrainNormalAgent.run",
                                           "stages": ["pc_only_initial", "constraint_matrix", "final"]},
                                modes=frozenset({"recorded", "replay", "live"}), cost="llm")
