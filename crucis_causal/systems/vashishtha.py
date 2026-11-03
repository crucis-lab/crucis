"""Vashishtha et al., causal order from imperfect experts (no licence shown: evaluation use only). Triplet LLM order,
then PC with the order orienting PC's undirected pairs (harness code). Exposes sources, PC alone and the LLM-only DAG."""
from ..core.adapter import Capabilities, register
from ._probe import ProbeAgent


@register
class Vashishtha(ProbeAgent):
    name, version = "vashishtha", "1"
    capabilities = Capabilities(takes=frozenset({"data", "names", "context"}), marks=frozenset({"->", "--"}),
                                edge_source=True, variants={"data_only": "pc_only", "knowledge_only": "llm_only_triplet_dag"},
                                glass_box={"entry": "causal_discovery.strategies.triplet:run_triplet_experiment",
                                           "stages": ["pc_only", "llm_only_triplet_dag", "final"]},
                                modes=frozenset({"recorded", "replay", "live"}), cost="llm")
