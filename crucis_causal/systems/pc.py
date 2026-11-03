"""PC, upstream causal-learn 0.1.4.8: stable PC, Fisher-z, alpha 0.05, maxP orientation (uc_rule 1, uc_priority 3); the
AB-01 'PC (upstream, maxP)' row. Data only, deterministic. Glass box: skeleton, orientation phases."""
from ..core.adapter import Capabilities, register
from ._methods import StoredMethod


@register
class PC(StoredMethod):
    name, version = "pc", "1"
    capabilities = Capabilities(takes=frozenset({"data"}), marks=frozenset({"->", "--", "<->"}),
                                glass_box={"entry": "causallearn.search.ConstraintBased.PC:pc",
                                           "stages": ["skeleton", "v_structures", "meek"]},
                                modes=frozenset({"recorded", "live"}), cost="cpu")
    rows = {(f, arm): "pc_upstream_maxp_%s_obs_%s" % (f, s) for f in ("semantic", "formula")
            for arm, s in (("released", "rel"), ("shuffled", "shuf"))}

    def algorithm(self, X, presented):
        from causallearn.search.ConstraintBased.PC import pc
        return pc(X, alpha=0.05, indep_test="fisherz", stable=True, uc_rule=1, uc_priority=3, show_progress=False).G.graph
