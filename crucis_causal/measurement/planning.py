"""Exact procedure selection and per-output preparation without running a calculation."""

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from types import MappingProxyType

from crucis_causal.execution.model import canonical

from .codec import Limits
from .resolution import Issue, ResolvedArtifact, ResolvedRecord, ResolvedView, ResolutionError


@dataclass(frozen=True, slots=True)
class ProcedureDescriptor:
    """An explicitly installed, pinned declaration, independent of qualification."""

    name: str
    version: str
    implementation_digest: str
    slots_bytes: bytes
    output_roles_bytes: bytes

    @classmethod
    def from_declaration(cls, contract, implementation_digest, slots, output_roles):
        if (not isinstance(implementation_digest, str) or len(implementation_digest) != 64
                or any(ch not in "0123456789abcdef" for ch in implementation_digest)):
            raise ValueError("s4.invalid_implementation_digest")
        return cls(contract["name"], contract["version"], implementation_digest,
                   canonical(slots), canonical(output_roles))


class Registry:
    """A finite caller-selected catalogue; serialized names cannot load code."""

    def __init__(self, descriptors=()):
        entries = {}
        for descriptor in descriptors:
            if not isinstance(descriptor, ProcedureDescriptor):
                raise TypeError("s4.procedure_descriptor_required")
            key = descriptor.name, descriptor.version
            if key in entries:
                raise ValueError("s4.duplicate_procedure")
            entries[key] = descriptor
        self._entries = MappingProxyType(entries)

    def get(self, contract):
        return self._entries.get((contract["name"], contract["version"]))


@dataclass(frozen=True, slots=True)
class PreparedSlot:
    key: str
    values: tuple[ResolvedRecord | ResolvedArtifact, ...]


@dataclass(frozen=True, slots=True)
class PreparedOutput:
    key: str
    binding: ResolvedRecord
    scope: ResolvedRecord
    output_role: str
    subject_key: str
    slots: tuple[PreparedSlot, ...]
    premises: tuple[ResolvedRecord, ...]


@dataclass(frozen=True, slots=True)
class HeldOutput:
    key: str
    issue: Issue


@dataclass(frozen=True, slots=True)
class PlanReport:
    state: str
    plan_record: ResolvedRecord | None
    descriptor: ProcedureDescriptor | None
    basis_digest: str | None
    outputs: tuple[PreparedOutput, ...]
    held: tuple[HeldOutput, ...]
    issues: tuple[Issue, ...]
    limits: Limits


def _record(reader, ref, name, anchor=None):
    if "selector" in ref:
        raise ResolutionError("whole_record_required")
    found = reader.read(ref, anchor)
    if not isinstance(found, ResolvedRecord) or found.contract["name"] != name:
        raise ResolutionError("role_contract")
    return found


def _scope_match(left, right):
    return (left.package_id, left.package_digest, left.record_id) == (
        right.package_id, right.package_digest, right.record_id
    )


def _materialize_slots(reader, specs, supplied, anchor):
    declared = {item["key"]: item for item in specs}
    selected = {item["key"]: item["values"] for item in supplied}
    if selected.keys() - declared.keys():
        raise ResolutionError("unexpected_slot")
    output = []
    for key in sorted(declared):
        spec = declared[key]
        values = selected.get(key, ())
        if not int(spec["minimum"]) <= len(values) <= int(spec["maximum"]):
            raise ResolutionError("slot_cardinality", key)
        if spec["collection"] in ("keyed", "set"):
            order = [canonical(item) for item in values]
            if len(order) != len(set(order)) or order != sorted(order):
                raise ResolutionError("slot_collection", key)
            if spec["collection"] == "keyed":
                keys = [item.get("selector", {}).get("key", item.get("target_id")) for item in values]
                if None in keys or len(keys) != len(set(keys)):
                    raise ResolutionError("slot_key_conflict", key)
        found = []
        for value in values:
            if "ref_kind" not in value:
                raise ResolutionError("slot_unresolved", key)
            material = reader.read(value, anchor)
            if isinstance(material, ResolvedRecord):
                contract = material.contract
            else:
                contract = value["artifact_record"]["expected_contract"]
            if contract != spec["contract"]:
                raise ResolutionError("slot_contract", key)
            found.append(material)
        output.append(PreparedSlot(key, tuple(found)))
    return tuple(output)


def _required_premises(reader, requirements, assess_refs, scope, frontier, audience, anchor,
                       selected_slots):
    expected = {}
    for ref, owner in requirements:
        requirement = _record(reader, ref, "s4.requirement", owner)
        value = requirement.value["payload"]
        if value["stage"] == "preflight":
            expected[(requirement.package_id, requirement.record_id)] = value
    if not expected:
        return ()
    observed = {}
    for item in assess_refs:
        assessment = _record(reader, item["assessment"], "s4.premise_assessment", anchor)
        value = assessment.value["payload"]
        requirement = _record(reader, value["requirement"], "s4.requirement",
                              assessment.package_id)
        key = requirement.package_id, requirement.record_id
        if key not in expected:
            continue
        actual_scope = _record(reader, value["scope"], "s4.scope", assessment.package_id)
        if not _scope_match(actual_scope, scope):
            continue
        if key in observed:
            raise ResolutionError("ambiguous_premise_assessment", requirement.record_id)
        actual_audience = _record(reader, value["audience"], "s3.audience", assessment.package_id)
        if (value["frontier"] != frontier or not _scope_match(actual_audience, audience)
                or value["rule"] != expected[key]["rule"]):
            raise ResolutionError("premise_basis_mismatch", requirement.record_id)
        subjects = _materialize_slots(reader, expected[key]["subject_slots"],
                                      value["subjects"], assessment.package_id)
        for subject in subjects:
            if subject.key not in selected_slots or subject.values != selected_slots[subject.key]:
                raise ResolutionError("premise_subject_mismatch", requirement.record_id)
        if value["determination"] != "supported" or value["gaps"]:
            raise ResolutionError("premise_" + value["determination"], requirement.record_id)
        if not value["support"]:
            raise ResolutionError("premise_basis_missing", requirement.record_id)
        for evidence in (*value["support"], *value["against"]):
            reader.read(evidence, assessment.package_id)
        observed[key] = assessment
    if expected.keys() != observed.keys():
        raise ResolutionError("premise_unassessed")
    return tuple(observed[key] for key in sorted(observed))


def _prepared_output(reader, output, goal, declaration, assess_refs, audience, anchor,
                     procedure_anchor):
    binding = _record(reader, output["binding"], "s4.binding", anchor)
    bound = binding.value["payload"]
    question = _record(reader, bound["question"], "s4.question_instance", binding.package_id)
    intended = _record(reader, goal["question"], "s4.question_instance", anchor)
    if not _scope_match(question, intended):
        raise ResolutionError("binding_question_mismatch")
    if "binding" in goal and not _scope_match(
            binding, _record(reader, goal["binding"], "s4.binding", anchor)):
        raise ResolutionError("goal_binding_mismatch")
    scope = _record(reader, output["scope"], "s4.scope", anchor)
    if not _scope_match(scope, _record(reader, goal["scope"], "s4.scope", anchor)):
        raise ResolutionError("goal_scope_mismatch")
    instance = question.value["payload"]
    definition = _record(reader, instance["definition"], "s4.question_definition", question.package_id)
    defined = definition.value["payload"]
    role_key = output["output_role"]
    proc_role = next((item for item in declaration["output_roles"] if item["key"] == role_key), None)
    goal_role = next((item for item in defined["output_roles"] if item["key"] == role_key), None)
    if proc_role is None or goal_role is None or proc_role["value_contract"] != goal_role["value_contract"]:
        raise ResolutionError("output_contract")
    if declaration["slots"] != defined["slots"]:
        raise ResolutionError("procedure_slot_contract")
    slots = _materialize_slots(reader, [s for s in defined["slots"] if s["role_class"] == "target"],
                               instance["target_slots"], question.package_id)
    slots += _materialize_slots(reader, [s for s in defined["slots"] if s["role_class"] == "evidence"],
                                bound["slots"], binding.package_id)
    reader.read(bound["selection"], binding.package_id)
    for position in bound["frontier"]:
        if "ref_kind" in position["position"]:
            reader.read(position["position"], binding.package_id)
    subjects = {item.key: item.values for item in slots}
    subjects["scope"] = (scope,)
    requirements = ([(ref, definition.package_id) for ref in goal_role["requirements"]] +
                    [(ref, procedure_anchor) for ref in proc_role["requirements"]])
    assessments = _required_premises(reader, requirements, assess_refs, scope,
                                     bound["frontier"], audience, anchor, subjects)
    return PreparedOutput(output["key"], binding, scope, role_key, output["subject_key"],
                          slots, assessments)


def _pin(material):
    if isinstance(material, ResolvedRecord):
        selected_digest = sha256(material.selected_bytes).hexdigest()
    else:
        selected_digest = material.digest
    return [material.package_id, material.package_digest, material.record_id, selected_digest]


def plan(goal, resolved_view, registry, limits=None):
    """Validate a selected s4.plan record and report ready and held roles.

    The plan is a declaration of intended work. This function only prepares
    selected evidence; it cannot produce an observed occurrence or claim.
    """
    if not isinstance(resolved_view, ResolvedView) or not isinstance(registry, Registry):
        raise TypeError("s4.resolved_view_and_registry_required")
    limits = resolved_view.limits if limits is None else limits
    if limits != resolved_view.limits:
        raise ResolutionError("read_plan_limits_mismatch")
    selected_plan = descriptor = None
    try:
        reader = resolved_view.reader()
        root = resolved_view.snapshot
        selected_plan = _record(reader, goal, "s4.plan")
        anchor = selected_plan.package_id
        payload = selected_plan.value["payload"]
        procedure = _record(reader, payload["procedure"], "s4.procedure", anchor)
        declaration = procedure.value["payload"]
        descriptor = registry.get(declaration["definition"])
        if descriptor is None:
            raise ResolutionError("procedure_unavailable")
        implementation = reader.read(declaration["implementation"], procedure.package_id)
        if not isinstance(implementation, ResolvedArtifact) or implementation.digest != descriptor.implementation_digest:
            raise ResolutionError("implementation_mismatch")
        if (canonical(declaration["slots"]) != descriptor.slots_bytes
                or canonical(declaration["output_roles"]) != descriptor.output_roles_bytes):
            raise ResolutionError("procedure_declaration_mismatch")
        configuration = reader.read(declaration["configuration"], procedure.package_id)
        dependencies = tuple(reader.read(ref, procedure.package_id)
                             for ref in declaration["dependencies"])
        declared_basis = tuple(reader.read(ref, anchor) for ref in payload["basis"])
        limit_basis = reader.read(payload["limits"], anchor)
        audience = _record(reader, root.package["audience"], "s3.audience", root.snapshot_id)
        request = _record(reader, payload["goal"]["request"], "s4.request", anchor)
        goals = request.value["payload"]["goals"]
        primary = next((g for g in goals if g["key"] == payload["goal"]["goal_key"]), None)
        if primary is None:
            raise ResolutionError("request_goal_unknown")
        if not any(o["output_role"] == primary["output_role"] and o["scope"] == primary["scope"]
                   for o in payload["outputs"]):
            raise ResolutionError("primary_goal_output_missing")
    except ResolutionError as exc:
        return PlanReport("held", selected_plan, descriptor, None, (), (), (exc.issue,), limits)

    ready, held = [], []
    for output in payload["outputs"]:
        try:
            matching = [g for g in goals if g["output_role"] == output["output_role"]
                        and g["scope"] == output["scope"]]
            if len(matching) != 1:
                raise ResolutionError("output_goal_ambiguous")
            ready.append(_prepared_output(reader, output, matching[0], declaration,
                                         payload["premises"], audience, anchor,
                                         procedure.package_id))
        except ResolutionError as exc:
            held.append(HeldOutput(output["key"], exc.issue))
    fixed = [_pin(x) for x in (selected_plan, procedure, implementation, configuration,
                               limit_basis, *dependencies, *declared_basis)]
    selected = [
        [out.key, _pin(out.binding), _pin(out.scope),
         [[slot.key, [_pin(x) for x in slot.values]] for slot in out.slots],
         [_pin(x) for x in out.premises]]
        for out in ready
    ]
    budget = {key: str(value) for key, value in asdict(limits).items()}
    basis_digest = sha256(canonical([root.digest, fixed, selected, budget])).hexdigest() if ready else None
    state = "partial" if ready and held else "ready" if ready else "held"
    return PlanReport(state, selected_plan, descriptor, basis_digest, tuple(ready), tuple(held),
                      (), limits)
