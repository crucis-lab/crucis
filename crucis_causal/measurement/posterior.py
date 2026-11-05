"""Q06 exact finite model-conditional posterior."""

from dataclasses import dataclass
from fractions import Fraction

from .calculation import CalculationHold, exact_number
from .judgment import defined, undefined


@dataclass(frozen=True, slots=True)
class Alternative:
    key: str
    prior: Fraction
    likelihood: Fraction


@dataclass(frozen=True, slots=True)
class Posterior:
    weights: tuple[tuple[str, Fraction], ...]
    normalizer: Fraction
    values: tuple[tuple[str, Fraction], ...] | None

    def measure(self, role, deciding_basis=()):
        if role == "normalizer":
            return defined(self.normalizer)
        if role == "posterior" and self.values is None:
            if self.normalizer != 0:
                raise CalculationHold("posterior_not_evaluated")
            return undefined("zero_normalizer", deciding_basis)
        if role not in ("weights", "posterior"):
            raise CalculationHold("posterior_role")
        rows = self.weights if role == "weights" else self.values
        return {"tag": "defined", "value": {"value_kind": "keyed", "entries": [
            {"key": key, "value": exact_number(value)} for key, value in rows
        ]}}


def finite_posterior(alternatives, budget, *, partition_established, observation_matches,
                     include_posterior=True):
    if partition_established is not True:
        raise CalculationHold("model_partition_unestablished")
    if observation_matches is not True:
        raise CalculationHold("model_observation_mismatch")
    alternatives = tuple(alternatives)
    if (len(alternatives) < 2 or any(not isinstance(row, Alternative) for row in alternatives)
            or len({row.key for row in alternatives}) != len(alternatives)):
        raise CalculationHold("model_alternatives_contract")
    prior_total, normalizer = Fraction(0), Fraction(0)
    weights = []
    for row in sorted(alternatives, key=lambda item: item.key):
        if row.likelihood is None:
            raise CalculationHold("model_likelihood_unavailable")
        for amount in (row.prior, row.likelihood):
            if budget.compare(amount, 0) < 0 or budget.compare(amount, 1) > 0:
                raise CalculationHold("model_mass_out_of_range")
        prior_total = budget.add(prior_total, row.prior)
        weight = budget.multiply(row.prior, row.likelihood)
        normalizer = budget.add(normalizer, weight)
        weights.append((row.key, weight))
    if budget.compare(prior_total, 1) != 0:
        raise CalculationHold("model_prior_not_normalized")
    values = (tuple((key, budget.divide(weight, normalizer)) for key, weight in weights)
              if include_posterior and budget.compare(normalizer, 0) > 0 else None)
    return Posterior(tuple(weights), normalizer, values)


def evaluate_posterior(prepared, budget):
    from .procedure_inputs import category, deciding_basis, exact, keyed, result

    model = result(prepared, "model")
    observed = result(prepared, "observation")
    observation = observed["outcome"]["value"]
    match = (model["subject_key"] == observed["subject_key"]
             and observation.get("value_kind") == "boolean" and observation["value"] is True)
    alternatives = []
    for key, row in keyed(model["outcome"]["value"]).items():
        weights = keyed(row)
        if "likelihood" not in weights:
            raise CalculationHold("model_likelihood_unavailable")
        if set(weights) != {"likelihood", "prior"}:
            raise CalculationHold("model_alternatives_contract")
        alternatives.append(Alternative(key, exact(weights["prior"]), exact(weights["likelihood"])))
    return finite_posterior(
        alternatives, budget, partition_established=category(prepared, "partition") == "established",
        observation_matches=match, include_posterior=prepared.output_role == "posterior",
    ).measure(prepared.output_role, deciding_basis(prepared, "model"))
