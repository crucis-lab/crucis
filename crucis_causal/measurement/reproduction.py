"""P5 exact, scope-aware comparison of separately recorded computations."""

from dataclasses import dataclass
import json

from crucis_causal.execution.model import canonical

from .planning import plan
from .procedure_inputs import exact
from .resolution import ResolutionError, ResolvedRecord


@dataclass(frozen=True, slots=True)
class ExactComparator:
    output: str
    diagnostics: tuple[str, ...] = ()
    boundary: str = "selected_roles"
    compare_undefined: bool = False
    version: str = "0.1.0-proposal.1"

    def __post_init__(self):
        keys = self.keys
        if (self.version != "0.1.0-proposal.1" or self.boundary not in
                ("selected_roles", "mask_derivation", "score_only")
                or any(not isinstance(key, str) or not key for key in keys)
                or len(keys) != len(set(keys))):
            raise ValueError("s4.comparator_contract")

    @property
    def keys(self):
        return (self.output, *self.diagnostics)


@dataclass(frozen=True, slots=True)
class ReplayGoal:
    plan_reference: bytes
    original_invocation: str
    replay_invocation: str
    original_basis: str
    replay_basis: str
    comparator: ExactComparator

    @classmethod
    def bind(cls, plan_reference, original, replay, original_basis, replay_basis, comparator):
        return cls(canonical(plan_reference), original, replay, original_basis, replay_basis, comparator)


@dataclass(frozen=True, slots=True)
class Comparison:
    state: str
    reason: str
    original_occurrence: str | None = None
    replay_occurrence: str | None = None
    compared: tuple[str, ...] = ()
    differences: tuple[str, ...] = ()


def _normalized(value):
    if isinstance(value, list):
        return [_normalized(item) for item in value]
    if not isinstance(value, dict):
        return value
    if value.get("number_kind") in ("int", "rational"):
        n = exact(value)
        return {"number_kind": "rational", "numerator": str(n.numerator),
                "denominator": str(n.denominator)}
    return {key: _normalized(item) for key, item in value.items()}


def _indexed(event, field):
    rows = event[field]
    indexed = {row["key"]: row for row in rows}
    if len(indexed) != len(rows):
        raise ResolutionError("replay_duplicate_output")
    return indexed


def _diagnostic_basis(outcome, reader, anchor):
    selected = []
    for ref in outcome["basis"]:
        resolved = reader.read(ref, anchor)
        selected.append((
            resolved.package_id, resolved.package_digest, resolved.record_id,
            canonical(resolved.value) if isinstance(resolved, ResolvedRecord) else resolved.source_bytes,
        ))
    return outcome["reason"], tuple(selected)


def compare(goal, view, registry, original, replay):
    """Check original input access, journal evidence and the named comparator."""
    if not isinstance(goal, ReplayGoal) or not isinstance(goal.comparator, ExactComparator):
        raise TypeError("s4.reproduction_goal_required")
    prepared = plan(json.loads(goal.plan_reference), view, registry)
    if not prepared.outputs:
        return Comparison("held", "original_basis_unavailable")
    if prepared.basis_digest != goal.original_basis:
        return Comparison("basis_mismatch", "original_plan_basis_changed")
    left = original.recover(goal.original_invocation, goal.original_basis)
    if left.state != "recorded":
        return Comparison("held", "original_work_" + left.state)
    right = replay.recover(goal.replay_invocation, goal.replay_basis)
    if right.state != "recorded":
        state = "incomplete" if right.state in ("entry_observed", "intent_observed", "unknown") else "held"
        return Comparison(state, "replay_work_" + right.state, left.occurrence_id,
                          right.occurrence_id)
    if left.occurrence_id == right.occurrence_id:
        return Comparison("held", "separate_replay_required", left.occurrence_id, right.occurrence_id)
    if goal.original_basis != goal.replay_basis:
        return Comparison("basis_mismatch", "selected_inputs_changed",
                          left.occurrence_id, right.occurrence_id)
    l_event, r_event = json.loads(left.event_bytes), json.loads(right.event_bytes)
    l_basis, r_basis = l_event["plan_evidence"], r_event["plan_evidence"]
    pinned_plan = prepared.plan_record
    if l_basis["plan"] != {"package_id": pinned_plan.package_id, "digest": pinned_plan.package_digest,
                          "record_id": pinned_plan.record_id}:
        return Comparison("basis_mismatch", "recorded_plan_pin_changed",
                          left.occurrence_id, right.occurrence_id)
    if l_basis != r_basis:
        return Comparison("basis_mismatch", "execution_basis_changed",
                          left.occurrence_id, right.occurrence_id)
    comparator = goal.comparator
    prepared_by_key = {out.key: out for out in prepared.outputs}
    if any(key not in prepared_by_key for key in comparator.keys):
        return Comparison("held", "selected_scope_unavailable", left.occurrence_id, right.occurrence_id)
    primary = prepared_by_key[comparator.output]
    if comparator.boundary == "mask_derivation" and not any(
        prepared_by_key[key].output_role == "judgment_mask"
        and prepared_by_key[key].scope == primary.scope
        for key in comparator.diagnostics
    ):
        return Comparison("held", "derived_mask_comparator_required", left.occurrence_id,
                          right.occurrence_id)
    if comparator.boundary == "score_only" and not any(
        slot.key == "mask" and slot.values for slot in primary.slots
    ):
        return Comparison("held", "pinned_input_mask_required", left.occurrence_id, right.occurrence_id)

    compared, differences = [], []
    try:
        expected = _indexed(l_basis, "outputs")
        l_emissions, r_emissions = _indexed(l_event, "emissions"), _indexed(r_event, "emissions")
        for key in comparator.keys:
            if key not in expected or key not in l_emissions or key not in r_emissions:
                return Comparison("incomplete", "selected_emission_unavailable", left.occurrence_id,
                                  right.occurrence_id, tuple(compared), tuple(differences))
            a, b = l_emissions[key]["outcome"], r_emissions[key]["outcome"]
            if a["tag"] == "undefined" or b["tag"] == "undefined":
                if not comparator.compare_undefined:
                    return Comparison("held", "diagnostic_comparator_required", left.occurrence_id,
                                      right.occurrence_id, tuple(compared), tuple(differences))
                reader = view.reader()
                anchor = prepared_by_key[key].binding.package_id
                av = _diagnostic_basis(a, reader, anchor) if a["tag"] == "undefined" else _normalized(a)
                bv = _diagnostic_basis(b, reader, anchor) if b["tag"] == "undefined" else _normalized(b)
            else:
                av, bv = _normalized(a), _normalized(b)
            compared.append(key)
            if av != bv:
                differences.append(key)
    except ResolutionError as exc:
        return Comparison("held", exc.issue.code, left.occurrence_id, right.occurrence_id)
    return Comparison("disagreement" if differences else "agreement",
                      "exact_comparison_completed", left.occurrence_id, right.occurrence_id,
                      tuple(compared), tuple(differences))
