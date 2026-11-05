"""Typed materialized inputs for the first versioned measurement procedures."""

from fractions import Fraction

from .calculation import CalculationHold
from .resolution import ResolvedRecord


def many(prepared, key):
    values = next((slot.values for slot in prepared.slots if slot.key == key), ())
    if any(not isinstance(item, ResolvedRecord) for item in values):
        raise CalculationHold("procedure_input_record_required")
    return values


def one(prepared, key, contract=None):
    values = many(prepared, key)
    if len(values) != 1:
        raise CalculationHold("procedure_slot_required")
    record = values[0]
    if contract is not None and record.contract["name"] != contract:
        raise CalculationHold("procedure_slot_contract")
    return record


def result(prepared, key):
    payload = one(prepared, key, "s4.result").value["payload"]
    if payload["outcome"]["tag"] != "defined":
        raise CalculationHold("procedure_input_value_unavailable")
    return payload


def value(prepared, key, kind=None):
    selected = result(prepared, key)["outcome"]["value"]
    if kind is not None and selected.get("value_kind") != kind:
        raise CalculationHold("procedure_value_contract")
    return selected


def category(prepared, key):
    return value(prepared, key, "category")["value"]


def exact(value):
    kind = value.get("number_kind")
    if kind == "int":
        return Fraction(int(value["text"]))
    if kind == "rational":
        return Fraction(int(value["numerator"]), int(value["denominator"]))
    raise CalculationHold("exact_value_required")


def keyed(value):
    if value.get("value_kind") != "keyed":
        raise CalculationHold("keyed_value_required")
    return {row["key"]: row["value"] for row in value["entries"]}


def deciding_basis(prepared, key):
    # The selected source is an existing plan binding role. Local result
    # coordinates remain local when the work is appended to that snapshot.
    source = one(prepared, key)
    if source.package_id != prepared.binding.package_id:
        raise CalculationHold("local_diagnostic_basis_required")
    return ({"ref_kind": "local", "target_id": source.record_id,
             "expected_contract": source.contract},)
