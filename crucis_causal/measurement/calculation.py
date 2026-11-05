"""Bounded deterministic evaluator calls and outcome records."""

from dataclasses import dataclass
from fractions import Fraction
from hashlib import sha256
import json

from crucis_causal.execution.model import canonical

from .codec import WireError, check_outcome
from .planning import ProcedureDescriptor
from .resolution import Issue


class CalculationHold(ValueError):
    def __init__(self, reason):
        self.issue = Issue("s4." + reason.removeprefix("s4."))
        super().__init__(self.issue.code)


class ArithmeticBudget:
    def __init__(self, limits):
        self._ceiling = 10 ** limits.intermediate_digits
        self._maximum = limits.rational_operations
        self.operations = 0

    def _checked(self, operand):
        if isinstance(operand, bool) or not isinstance(operand, (int, Fraction)):
            raise CalculationHold("exact_operand_required")
        value = Fraction(operand)
        if abs(value.numerator) >= self._ceiling or value.denominator >= self._ceiling:
            raise CalculationHold("intermediate_digit_limit")
        return value

    def _charge(self, a, b):
        if self.operations == self._maximum:
            raise CalculationHold("arithmetic_operation_limit")
        self.operations += 1
        return self._checked(a), self._checked(b)

    def add(self, a, b):
        a, b = self._charge(a, b)
        return self._checked(a + b)

    def subtract(self, a, b):
        a, b = self._charge(a, b)
        return self._checked(a - b)

    def multiply(self, a, b):
        a, b = self._charge(a, b)
        return self._checked(a * b)

    def divide(self, a, b):
        a, b = self._charge(a, b)
        if b == 0:
            raise CalculationHold("unexpected_zero_denominator")
        return self._checked(a / b)

    def compare(self, a, b):
        a, b = self._charge(a, b)
        return -1 if a < b else 1 if a > b else 0


def exact_number(value):
    if isinstance(value, bool):
        raise CalculationHold("exact_operand_required")
    if isinstance(value, int):
        return {"number_kind": "int", "text": str(value)}
    if not isinstance(value, Fraction):
        raise CalculationHold("exact_operand_required")
    return {"number_kind": "rational", "numerator": str(value.numerator),
            "denominator": str(value.denominator)}


@dataclass(frozen=True, slots=True)
class Evaluator:
    descriptor: ProcedureDescriptor
    implementation: bytes
    call: object

    def __post_init__(self):
        if (not isinstance(self.descriptor, ProcedureDescriptor)
                or type(self.implementation) is not bytes
                or sha256(self.implementation).hexdigest() != self.descriptor.implementation_digest):
            raise ValueError("s4.evaluator_implementation_mismatch")
        if not callable(self.call):
            raise TypeError("s4.evaluator_callable_required")


@dataclass(frozen=True, slots=True)
class Emission:
    output_key: str
    outcome_bytes: bytes

    @property
    def outcome(self):
        return json.loads(self.outcome_bytes)


@dataclass(frozen=True, slots=True)
class EmissionBatch:
    emissions: tuple[Emission, ...]
    issues: tuple[Issue, ...]
    operations: int


def evaluate(prepared_inputs, exact_evaluator, limits):
    """Call a selected evaluator over each independently prepared output role."""
    if not isinstance(exact_evaluator, Evaluator):
        raise TypeError("s4.evaluator_required")
    budget = ArithmeticBudget(limits)
    emissions, issues = [], []
    size = 0
    for output in prepared_inputs:
        try:
            outcome = exact_evaluator.call(output, budget)
            check_outcome(outcome, limits)
            raw = canonical(outcome)
            # Leave space for the scoped ledger envelope and its identifiers.
            if size + len(raw) > limits.snapshot_bytes // 2:
                raise CalculationHold("emission_byte_limit")
            size += len(raw)
            emissions.append(Emission(output.key, raw))
        except CalculationHold as exc:
            issues.append(Issue(exc.issue.code, output.key))
        except WireError as exc:
            issues.append(Issue(exc.code, output.key))
        except Exception:
            # Native errors and messages are not public measurement evidence.
            issues.append(Issue("s4.evaluator_failed", output.key))
    return EmissionBatch(tuple(emissions), tuple(issues), budget.operations)
