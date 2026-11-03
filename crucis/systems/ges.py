"""GES with the Gaussian BIC score (the `ges` package 1.1.0, lambda = log(n)/2, z-scored columns); the AB-01 'GES (BIC)'
row. Data only, deterministic. Glass box: forward, backward, turning phases."""
from ..core.adapter import Capabilities, register
from ._methods import StoredMethod


@register
class GES(StoredMethod):
    name, version = "ges", "1"
    capabilities = Capabilities(takes=frozenset({"data"}), marks=frozenset({"->", "--"}),
                                glass_box={"entry": "ges:fit_bic", "stages": ["forward", "backward", "turning"]},
                                modes=frozenset({"recorded", "live"}), cost="cpu")
    rows = {("semantic", "released"): "gesbic_semantic_obs", ("semantic", "shuffled"): "gesbic_semantic_obs_shuf",
            ("formula", "released"): "gesbic_formula_obs_rel", ("formula", "shuffled"): "gesbic_formula_obs_shuf"}

    def algorithm(self, X, presented):
        from crucis._support.causalarena_methods import run
        return run("gesbic", X)
