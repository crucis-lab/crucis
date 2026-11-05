"""Q02 strict-order and Q03 single-event exact loss."""

from dataclasses import dataclass
from fractions import Fraction

from .calculation import CalculationHold
from .judgment import _local, _member, _s1, defined


@dataclass(frozen=True, slots=True)
class OrderAssessment:
    fulfilled: bool
    violated: tuple[str, ...] | None
    admissible: bool | None

    def measure(self, role):
        if role == "fulfillment":
            return {"tag": "defined", "value": {"value_kind": "boolean", "value": self.fulfilled}}
        if role == "violations" and self.violated is not None:
            return defined(len(self.violated))
        if role == "violated_keys" and self.violated is not None:
            return {"tag": "defined", "value": {"value_kind": "keyed", "entries": [
                {"key": key, "value": {"value_kind": "boolean", "value": True}}
                for key in self.violated
            ]}}
        if role == "admissibility" and self.admissible is not None:
            return {"tag": "defined", "value": {"value_kind": "boolean", "value": self.admissible}}
        raise CalculationHold("ordering_role_held")


def _constraints(roster, conditions):
    targets = {member: [] for member in roster}
    in_degree = dict.fromkeys(roster, 0)
    labels = set()
    for key, before, after in conditions:
        if key in labels or before not in roster or after not in roster or before == after:
            raise CalculationHold("order_reference_contract")
        labels.add(key)
        targets[before].append(after)
        in_degree[after] += 1
    ready = [member for member, count in in_degree.items() if not count]
    seen = 0
    while ready:
        member = ready.pop()
        seen += 1
        for other in targets[member]:
            in_degree[other] -= 1
            if not in_degree[other]:
                ready.append(other)
    if seen != len(roster):
        raise CalculationHold("cyclic_order_reference")


def ordering(roster, sequence, conditions, reference_kind, capture):
    if capture != "complete":
        raise CalculationHold("sequence_capture_unresolved")
    roster, sequence, conditions = tuple(roster), tuple(sequence), tuple(conditions)
    members = set(roster)
    if not roster or len(roster) != len(members):
        raise CalculationHold("order_roster_contract")
    if len(sequence) != len(members) or set(sequence) != members:
        return OrderAssessment(False, None, None)
    if reference_kind not in ("complete", "necessary_only"):
        raise CalculationHold("order_reference_unresolved")
    _constraints(members, conditions)
    positions = {key: i for i, key in enumerate(sequence)}
    violated = tuple(sorted(label for label, before, after in conditions
                            if positions[before] >= positions[after]))
    admissible = False if violated else True if reference_kind == "complete" else None
    return OrderAssessment(True, violated, admissible)


def strict_sequence(output, domain):
    """Read a finite S1 sequence under an explicitly selected identity basis."""
    if output.package_id != domain.package_id:
        raise CalculationHold("native_domain_mismatch")
    space, native = _s1(domain, "domain"), _s1(output, "output")
    body = native["body"]
    if (space["domain_kind"] != "finite" or native["output_type"] != "order"
            or body["representation"] != "sequence" or body["pairs"]
            or not _local(body["domain"], domain.record_id)):
        raise CalculationHold("strict_sequence_reader_contract")
    keys = {member["key"] for member in space["members"]}
    return tuple(_member(member, domain.record_id, keys) for member in body["sequence"])


def _exact_s1_probability(output, event):
    value = _s1(output, "output")
    if value["output_type"] != "quantity":
        raise CalculationHold("probability_reader_contract")
    body = value["body"]
    if (body["quantity_kind"] != "s1.probability" or output.package_id != event.package_id
            or not _local(body["subject"], event.record_id)):
        raise CalculationHold("forecast_event_mismatch")
    value = body["value"]
    if value.get("state") != "known" or value["value"]["number_type"] not in ("integer", "finite_decimal"):
        raise CalculationHold("forecast_probability_unavailable")
    text = value["value"]["text"]
    # Cap the significand and exponent before Fraction expands a decimal.
    mantissa, marker, exponent = text.lower().partition("e")
    if (len(mantissa) > 258 or
            marker and (len(exponent.lstrip("+-")) > 3 or abs(int(exponent)) > 256)):
        raise CalculationHold("forecast_probability_digit_limit")
    return Fraction(text)


def binary_loss(probability, outcome, budget, *, event_match, prospective, order):
    if event_match is not True:
        raise CalculationHold("forecast_event_mismatch")
    if type(outcome) is not bool:
        raise CalculationHold("binary_outcome_unresolved")
    if prospective and order != "before":
        raise CalculationHold("forecast_issuance_" + ("contradicted" if order == "after" else "unresolved"))
    if isinstance(probability, bool) or not isinstance(probability, (int, Fraction)):
        raise CalculationHold("exact_probability_required")
    if budget.compare(probability, 0) < 0 or budget.compare(probability, 1) > 0:
        raise CalculationHold("probability_out_of_range")
    difference = budget.subtract(probability, int(outcome))
    return defined(budget.multiply(difference, difference))


def forecast_loss(output, event, outcome, budget, *, prospective, order):
    return binary_loss(_exact_s1_probability(output, event), outcome, budget,
                       event_match=True, prospective=prospective, order=order)


def evaluate_order(prepared, budget):
    from .procedure_inputs import category, keyed, one, value

    roster = prepared.scope.value["payload"].get("universe")
    if roster is None:
        raise CalculationHold("order_roster_unavailable")
    native = one(prepared, "native", "s1.output")
    domain = one(prepared, "domain", "s1.domain")
    sequence = strict_sequence(native, domain)
    capture = category(prepared, "capture")
    if prepared.output_role == "fulfillment":
        return ordering(roster, sequence, (), "necessary_only", capture).measure("fulfillment")
    conditions = []
    for label, encoded in keyed(value(prepared, "conditions")).items():
        endpoints = keyed(encoded)
        if (set(endpoints) != {"after", "before"}
                or any(v.get("value_kind") != "text" for v in endpoints.values())):
            raise CalculationHold("order_reference_contract")
        conditions.append((label, endpoints["before"]["value"], endpoints["after"]["value"]))
    return ordering(roster, sequence, conditions, category(prepared, "criteria"),
                    capture).measure(prepared.output_role)


def evaluate_forecast(prepared, budget):
    from .procedure_inputs import category, many, one, result

    if prepared.output_role != "loss":
        raise CalculationHold("forecast_role")
    native = one(prepared, "native", "s1.output")
    event = one(prepared, "event", "s1.proposition")
    observed = result(prepared, "outcome")
    label = observed["outcome"]["value"]
    if observed["subject_key"] != event.record_id or label.get("value_kind") != "boolean":
        raise CalculationHold("forecast_event_mismatch")
    body = native.value["payload"]["body"]
    condition = many(prepared, "conditioning")
    actual = body.get("conditioning", ())
    if (len(actual) != len(condition) or any(
        item.package_id != native.package_id or not _local(ref, item.record_id)
        for ref, item in zip(actual, condition)
    )):
        raise CalculationHold("forecast_conditioning_mismatch")
    return forecast_loss(native, event, label["value"], budget, prospective=True,
                         order=category(prepared, "issuance_order"))
