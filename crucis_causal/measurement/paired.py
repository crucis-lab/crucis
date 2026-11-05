"""Q04/Q05 exact paired contrasts and scoped delivery utility."""

from dataclasses import dataclass
from fractions import Fraction

from crucis_causal.execution.model import canonical

from .calculation import CalculationHold, exact_number
from .judgment import defined
from .procedure_inputs import exact, many, one


@dataclass(frozen=True, slots=True)
class Range:
    lower: Fraction
    upper: Fraction

    def __post_init__(self):
        if (any(isinstance(x, bool) or not isinstance(x, (int, Fraction))
                for x in (self.lower, self.upper)) or self.lower > self.upper):
            raise CalculationHold("range_contract")

    def value(self, kind):
        return {"value_kind": kind, "lower": exact_number(Fraction(self.lower)),
                "upper": exact_number(Fraction(self.upper))}


UNIT_RANGE = Range(Fraction(0), Fraction(1))
ZERO = Range(Fraction(0), Fraction(0))


@dataclass(frozen=True, slots=True)
class Candidate:
    key: str
    attempt: str
    channel: str
    boundary: str
    clock: str
    receipt_times: Range
    qualification: str
    quality: Range | None = None


@dataclass(frozen=True, slots=True)
class Closure:
    """An attributed assessment of the exact authorized history, including gaps."""

    slot: str
    attempts: frozenset[str]
    channels: frozenset[str]
    boundary: str
    clock: str
    covered_through: Fraction
    authoritative: bool
    gaps: tuple[str, ...]
    basis: str


@dataclass(frozen=True, slots=True)
class DeliveryPolicy:
    slot: str
    attempts: frozenset[str]
    channels: frozenset[str]
    boundary: str
    clock: str
    horizon: Fraction
    tie_rule: str = "unresolved"


@dataclass(frozen=True, slots=True)
class Utility:
    value: Range
    delivery: str
    selected: str | None
    possible_candidates: tuple[str, ...]
    closure_basis: str | None


def _eligible(candidate, policy):
    return (candidate.attempt in policy.attempts and candidate.channel in policy.channels
            and candidate.boundary == policy.boundary)


def _established(candidate, policy):
    return (candidate.qualification == "yes" and candidate.clock == policy.clock
            and candidate.receipt_times.upper <= policy.horizon)


def _always_earlier(a, b, policy):
    if not _established(a, policy) or b.clock != policy.clock:
        return False
    first, second = a.receipt_times.upper, b.receipt_times.lower
    return first < second or first == second and policy.tie_rule == "key_order" and a.key < b.key


def delivery_utility(policy, candidates, closure=None, *, total_utility_established):
    """Classify first qualifying delivery by the inclusive receiving horizon."""
    if total_utility_established is not True:
        raise CalculationHold("utility_target_unestablished")
    if (not policy.attempts or not policy.channels or not policy.boundary or not policy.clock
            or policy.tie_rule not in ("key_order", "unresolved")
            or isinstance(policy.horizon, bool) or not isinstance(policy.horizon, (int, Fraction))):
        raise CalculationHold("delivery_policy_contract")
    candidates = tuple(candidates)
    if len(candidates) > 8192:
        raise CalculationHold("delivery_candidate_limit")
    if len({c.key for c in candidates}) != len(candidates):
        raise CalculationHold("duplicate_delivery_candidate")
    relevant = []
    for candidate in candidates:
        if candidate.qualification not in ("yes", "no", "unresolved"):
            raise CalculationHold("delivery_qualification")
        if candidate.quality is not None and (
                candidate.quality.lower < 0 or candidate.quality.upper > 1):
            raise CalculationHold("utility_range_outside_domain")
        if not _eligible(candidate, policy) or candidate.qualification == "no":
            continue
        if candidate.clock == policy.clock and candidate.receipt_times.lower > policy.horizon:
            continue
        relevant.append(candidate)
    guaranteed = tuple(c for c in relevant if _established(c, policy))
    closed = (closure is not None and closure.slot == policy.slot
              and closure.attempts == policy.attempts and closure.channels == policy.channels
              and closure.boundary == policy.boundary and closure.clock == policy.clock
              and closure.covered_through >= policy.horizon and closure.authoritative is True
              and not closure.gaps and bool(closure.basis))
    # Only a necessarily earlier qualifying receipt rules out a candidate.
    leaders = sorted(guaranteed, key=lambda c: (c.receipt_times.upper, c.key))[:2]
    candidates = tuple(c for c in relevant
                       if not any(g.key != c.key and _always_earlier(g, c, policy)
                                  for g in leaders))
    keys = tuple(sorted(c.key for c in candidates))
    if not closed:
        return Utility(UNIT_RANGE, "established" if guaranteed else "unresolved", None, keys, None)
    if not candidates:
        return Utility(ZERO, "no_qualifying_delivery", None, (), closure.basis)
    selected = candidates[0].key if len(candidates) == 1 and guaranteed else None
    possibilities = [c.quality or UNIT_RANGE for c in candidates]
    if not guaranteed:
        possibilities.append(ZERO)
    value = Range(min(r.lower for r in possibilities), max(r.upper for r in possibilities))
    return Utility(value, "established" if guaranteed else "unresolved",
                   selected, keys, closure.basis)


@dataclass(frozen=True, slots=True)
class Pair:
    key: str
    a: str
    b: str


def _frame(pairs):
    pairs = tuple(pairs)
    units = {slot for pair in pairs for slot in (pair.a, pair.b)}
    if (not pairs or len({pair.key for pair in pairs}) != len(pairs)
            or len(units) != 2 * len(pairs)):
        raise CalculationHold("paired_frame_contract")
    return pairs, units


def paired_differences(pairs, scores, budget):
    pairs, units = _frame(pairs)
    if set(scores) != units:
        raise CalculationHold("intended_slot_ledger_required")
    return {pair.key: budget.subtract(scores[pair.a], scores[pair.b])
            for pair in pairs if scores[pair.a] is not None and scores[pair.b] is not None}


def paired_point(pairs, scores, budget):
    pairs, _ = _frame(pairs)
    differences = paired_differences(pairs, scores, budget)
    if len(differences) != len(pairs):
        raise CalculationHold("incomplete_quality_frame")
    total = 0
    for difference in differences.values():
        total = budget.add(total, difference)
    return budget.divide(total, len(pairs))


def paired_enclosure(pairs, ranges, budget):
    pairs, units = _frame(pairs)
    if set(ranges) != units or any(not isinstance(value, Range) for value in ranges.values()):
        raise CalculationHold("complete_utility_range_frame_required")
    lower = upper = 0
    for pair in pairs:
        a, b = ranges[pair.a], ranges[pair.b]
        lower = budget.add(lower, budget.subtract(a.lower, b.upper))
        upper = budget.add(upper, budget.subtract(a.upper, b.lower))
    return Range(budget.divide(lower, len(pairs)), budget.divide(upper, len(pairs)))


def _population(prepared):
    population = one(prepared, "population", "s4.population")
    payload = population.value["payload"]
    arms = tuple(canonical(arm) for arm in payload["arms"])
    if arms[0] == arms[1]:
        raise CalculationHold("distinct_arms_required")
    groups, selected = {}, {}
    for row in payload["slots"]:
        case, arm = canonical(row["case"]), canonical(row["arm"])
        group = groups.setdefault(case, {})
        if arm not in arms or arm in group or canonical(row["slot"]) in selected:
            raise CalculationHold("paired_slot_ambiguous")
        group[arm] = row["key"]
        selected[canonical(row["slot"])] = row
    if any(set(group) != set(arms) for group in groups.values()):
        raise CalculationHold("paired_slot_missing")
    pairs = tuple(Pair(case.decode("utf-8"), group[arms[0]], group[arms[1]])
                  for case, group in sorted(groups.items()))
    return population, pairs, {row["key"]: row for row in selected.values()}


def _slot_results(prepared, slot, kind, population, by_key):
    observed = {}
    for record in many(prepared, slot):
        if record.contract["name"] != "s4.result":
            raise CalculationHold("paired_result_contract")
        payload = record.value["payload"]
        key = payload["subject_key"]
        if key not in by_key or key in observed or payload["output_role"] != kind:
            raise CalculationHold("paired_result_scope")
        field = "range" if kind == "slot_range" else "outcome"
        ref = by_key[key].get(field)
        # First route uses explicitly associated local records in the population
        # snapshot. Other cross-package association routes need a named reader.
        if (ref is None or ref.get("ref_kind") != "local" or ref["target_id"] != record.record_id
                or record.package_id != population.package_id or payload["outcome"]["tag"] != "defined"):
            raise CalculationHold("paired_result_association")
        observed[key] = payload["outcome"]["value"]
    return observed


def evaluate_paired_point(prepared, budget):
    population, pairs, by_key = _population(prepared)
    scores = dict.fromkeys(by_key)
    scopes = {(row.package_id, row.record_id): row
              for row in many(prepared, "score_scopes") if row.contract["name"] == "s4.scope"}
    comparability = set()
    for score in many(prepared, "scores"):
        payload = score.value["payload"]
        ref = payload["scope"]
        selected = scopes.get((score.package_id, ref["target_id"])) if ref["ref_kind"] == "local" else None
        if selected is None or payload["subject_key"] not in by_key:
            raise CalculationHold("paired_score_scope_required")
        shape = selected.value["payload"]
        if (shape["scope_kind"] != "judgment" or not shape.get("universe")
                or shape.get("mask") != shape["universe"]
                or canonical(shape["subject"]) != canonical(by_key[payload["subject_key"]]["case"])):
            raise CalculationHold("paired_score_scope")
        comparability.add(canonical([shape["quantity"], shape["units"]]))
    if len(comparability) > 1:
        raise CalculationHold("incompatible_paired_quantities")
    for key, encoded in _slot_results(prepared, "scores", "full", population, by_key).items():
        score = exact(encoded)
        if score < 0 or score > 1:
            raise CalculationHold("quality_scale")
        scores[key] = score
    if prepared.output_role == "point":
        return defined(paired_point(pairs, scores, budget))
    differences = paired_differences(pairs, scores, budget)
    if prepared.output_role == "complete_pair_count":
        return defined(len(differences))
    if prepared.output_role == "case_differences":
        return {"tag": "defined", "value": {"value_kind": "keyed", "entries": [
            {"key": pair.key, "value": exact_number(differences[pair.key]) if pair.key in differences
             else {"tag": "unresolved", "reason": "unavailable_pair_score", "basis": []}}
            for pair in sorted(pairs, key=lambda item: item.key)
        ]}}
    raise CalculationHold("paired_role")


def evaluate_utility_enclosure(prepared, budget):
    population, pairs, by_key = _population(prepared)
    ranges = {}
    for key, encoded in _slot_results(prepared, "ranges", "slot_range", population, by_key).items():
        if encoded.get("value_kind") != "slot_range":
            raise CalculationHold("slot_range_contract")
        item = Range(exact(encoded["lower"]), exact(encoded["upper"]))
        if item.lower < 0 or item.upper > 1:
            raise CalculationHold("utility_range_outside_domain")
        ranges[key] = item
    if prepared.output_role != "outer_bound":
        raise CalculationHold("paired_role")
    return {"tag": "defined", "value": paired_enclosure(pairs, ranges, budget).value("outer_interval")}
