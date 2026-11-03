"""PyWhy-LLM (py-why/pywhy-llm, MIT), Modeler flow, Pairwise strategy. Names only: no data interface, so under neutral
names it is offered nothing (regime 'none'). Every arrow comes from the LLM; it never leaves a pair undecided."""
from ..core.adapter import Capabilities, register
from ._probe import ProbeAgent


@register
class PyWhyLLM(ProbeAgent):
    name, version = "pywhyllm", "1"
    capabilities = Capabilities(takes=frozenset({"names", "context"}), marks=frozenset({"->"}), edge_source=True,
                                glass_box={"entry": "pywhyllm.suggesters.model_suggester:ModelSuggester.suggest_relationships",
                                           "stages": ["domain_expertises", "pairwise"]},
                                modes=frozenset({"recorded", "replay", "live"}), cost="llm")
