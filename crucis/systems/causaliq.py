"""causaliq-knowledge (CausalIQ, MIT): one LLM call returns a probabilistic graph (P forward / backward / undirected /
none per pair). Names only. States a probability per pair (confidence), so K14 is checkable once those are recorded."""
from ..core.adapter import Capabilities, register
from ._probe import ProbeAgent


@register
class CausalIQ(ProbeAgent):
    name, version = "causaliq", "1"
    capabilities = Capabilities(takes=frozenset({"names", "context"}), marks=frozenset({"->", "--"}), edge_source=True,
                                confidence=True, variants={"knowledge_only": "library_greedy_dag"},
                                glass_box={"entry": "causaliq_knowledge.graph.generator:GraphGenerator.generate_pdg_from_context",
                                           "stages": ["pdg", "most_likely_state"]},
                                modes=frozenset({"recorded", "replay", "live"}), cost="llm")
