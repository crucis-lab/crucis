"""GIES with the released intervention targets (D+I; gies 0.0.3); the AB-01 'GIES with targets (D+I)' row. Kept beside
PC and GES as the interventional baseline. Recorded only in this package version."""
from ..core.adapter import Capabilities, register
from ._methods import StoredMethod


@register
class GIES(StoredMethod):
    name, version = "gies", "1"
    capabilities = Capabilities(takes=frozenset({"data", "interventions"}), marks=frozenset({"->", "--"}),
                                modes=frozenset({"recorded"}), cost="cpu")
    rows = {(f, arm): "gies_targets_%s_obsint_%s" % (f, s) for f in ("semantic", "formula")
            for arm, s in (("released", "rel"), ("shuffled", "shuf"))}
