"""Regimes (protocol v1, section 1.2): what a system was OFFERED. Reuses the score contract's names
(analysis/score_record.py: D, D+I, D+K, D+I+K) and adds 'K' (knowledge only: a names-only system shown informative names) and 'none' (a names-only system
shown neutral names: offered nothing; its score is a floor, not a result).

offered channels x the channels the adapter TAKES -> the regime of a run. Neutral names close the K channel.
Rule R1: scores are compared only within one (regime, k_source). Rule R2: controls are paired differences across arms of
the same items; they are findings and are never ranked.
"""
REGIMES = ("none", "K", "D", "D+I", "D+K", "D+I+K")
K_SOURCES = ("none", "names_real", "names_swapped", "oracle", "wrong_supplier", "declared")
NAME_ARM_K = {"real": "names_real", "neutral": "none", "swapped": "names_swapped"}


def regime(takes, offered):
    """takes: the adapter's declared inputs; offered: channels the arm offers ({"data", "interventions", "names"/K})."""
    got = set(takes) & set(offered)
    k = bool(got & {"names", "knowledge"})
    d, i = "data" in got, "interventions" in got
    if not d:
        return "K" if k else "none"
    return "D" + ("+I" if i else "") + ("+K" if k else "")


def name_arm_offer(arm):
    """Channels a names arm offers: data always; names only when they carry information (real or swapped)."""
    return {"data", "context"} | ({"names"} if arm in ("real", "swapped") else set())


class CrossRegime(ValueError):
    pass


def check_comparable(rows):
    """rows: [{"regime", "k_source"}]; raise when a ranking would mix regimes (rule R1)."""
    keys = {(r["regime"], r.get("k_source")) for r in rows}
    if len(keys) > 1:
        raise CrossRegime("a ranking mixes regimes %s (rule R1); report a control instead" % sorted(keys))
    return keys.pop() if keys else None
