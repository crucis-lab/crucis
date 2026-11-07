
"""Scoped finding preparation with exact versioned rule declarations."""

from dataclasses import asdict, dataclass
from hashlib import sha256
from types import MappingProxyType

from crucis_causal.execution.model import canonical
from crucis_causal.measurement.resolution import ResolvedArtifact, ResolvedRecord

from .codec import Limits
from .resolution import ResolvedView, ResolutionError, identity, pin, whole


@dataclass(frozen=True, slots=True)
class RuleDescriptor:
    name: str
    version: str
    implementation_digest: str
    declaration_digest: str
    evidence_check: object

    @classmethod
    def bind(cls, declaration, implementation_bytes, evidence_check):
        if type(implementation_bytes) is not bytes or not callable(evidence_check):
            raise TypeError("s5.exact_rule_descriptor_required")
        contract = declaration["definition"]
        return cls(contract["name"], contract["version"], sha256(implementation_bytes).hexdigest(),
                   sha256(canonical(declaration)).hexdigest(), evidence_check)


class RuleRegistry:
    def __init__(self, descriptors=()):
        catalogue = {}
        for descriptor in descriptors:
            if not isinstance(descriptor, RuleDescriptor):
                raise TypeError("s5.rule_descriptor_required")
            key = descriptor.name, descriptor.version
            if key in catalogue:
                raise ValueError("s5.duplicate_rule")
            catalogue[key] = descriptor
        self._entries = MappingProxyType(catalogue)

    def get(self, contract):
        return self._entries.get((contract["name"], contract["version"]))


@dataclass(frozen=True, slots=True)
class SelectedEvidence:
    key: str
    role: str
    material: ResolvedRecord | ResolvedArtifact | None
    reason: str | None = None


@dataclass(frozen=True, slots=True)
class PreparedAssessment:
    state: str
    assessment: ResolvedRecord | None
    rule: ResolvedRecord | None
    question: ResolvedRecord | None
    basis: ResolvedRecord | None
    selection: tuple[SelectedEvidence, ...]
    basis_digest: str | None
    issues: tuple[str, ...]
    limits: Limits


def _selected(reader, rows, anchor):
    result = []
    for row in rows:
        e = row["evidence"]
        state = e["state"]
        if state != "selected":
            refs = e.get("alternatives", e.get("observations", ()))
            for ref in refs:
                reader.read(ref, anchor)
            result.append(SelectedEvidence(row["key"], row["role"], None, e["reason"]))
            continue
        try:
            value = reader.read(e["reference"], anchor)
        except ResolutionError as exc:
            result.append(SelectedEvidence(row["key"], row["role"], None, exc.code))
        else:
            result.append(SelectedEvidence(row["key"], row["role"], value))
    return tuple(result)


def _intended(reader, assessment, question, rule, basis, selected, descriptor):
    ap, bp = assessment.value["payload"], basis.value["payload"]
    qp, rp = question.value["payload"], rule.value["payload"]
    for name, target in (("question", question), ("rule", rule)):
        actual = whole(reader, bp[name], "s5." + name, basis.package_id)
        if identity(actual) != identity(target):
            raise ResolutionError("basis_scope_mismatch")
    if rp["target"] != qp["quantity"]:
        raise ResolutionError("rule_target_mismatch")
    subject = reader.read(qp["subject"], question.package_id)
    scope = reader.read(qp["scope"], question.package_id)
    selection = reader.read(bp["selection"], basis.package_id)
    extra = []
    for key, fields in (("comparison", ("first", "second", "selection")),
                        ("reference", ("target",))):
        if key in qp:
            extra.extend(reader.read(qp[key][field], question.package_id) for field in fields)
    if ap["applicability"]["state"] != "applicable":
        return ap["applicability"]["state"], (subject, scope, selection, *extra)
    for name in ("applicability", "execution"):
        disposition = ap[name]
        if "basis" in disposition:
            selected_basis = reader.read(disposition["basis"], assessment.package_id)
            if identity(selected_basis) != identity(basis):
                raise ResolutionError("assessment_basis_mismatch")
    if ap["execution"]["state"] not in ("established", "inapplicable"):
        return ap["execution"]["state"], (subject, scope, selection, *extra)
    values = {item.key: item for item in selected}
    for key in rp.get("prerequisites", ()):
        if key not in values or values[key].material is None:
            return "shared_prerequisite_unresolved", (subject, scope, selection, *extra)
    for operand in rp["operands"]:
        item = values.get(operand["key"])
        if item is None or item.material is None:
            if rp["partial"] == "require_all":
                return "required_operand_unresolved", (subject, scope, selection, *extra)
        elif not isinstance(item.material, ResolvedRecord) or item.material.contract != operand["evidence_contract"]:
            return "operand_contract_mismatch", (subject, scope, selection, *extra)
    try:
        supported = descriptor.evidence_check(reader, question, basis, selected)
    except ResolutionError:
        raise
    except Exception:
        return "evidence_policy_failed", (subject, scope, selection, *extra)
    if supported is not True:
        return "evidence_scope_unqualified", (subject, scope, selection, *extra)
    return None, (subject, scope, selection, *extra)


def prepare(request_ref, resolved_view, rule_registry, limits=None):
    """Prepare one attributed assessment. No rule evaluation or durable effects."""
    if not isinstance(resolved_view, ResolvedView) or not isinstance(rule_registry, RuleRegistry):
        raise TypeError("s5.resolved_view_and_registry_required")
    actual_limits = resolved_view.limits
    if limits is not None and limits != actual_limits:
        raise ResolutionError("read_prepare_limits_mismatch")
    assessment = rule = question = basis = None
    selected = ()
    try:
        reader = resolved_view.reader()
        root = resolved_view.snapshot
        audience = whole(reader, root.package["audience"], "s3.audience")
        frontier = tuple(reader.read(row["position"]) for row in root.package["frontier"]
                         if "ref_kind" in row["position"])
        assessment = whole(reader, request_ref, "s5.assessment")
        ap = assessment.value["payload"]
        anchor = assessment.package_id
        if anchor != root.snapshot_id:
            raise ResolutionError("local_request_required")
        question = whole(reader, ap["question"], "s5.question", anchor)
        rule = whole(reader, ap["rule"], "s5.rule", anchor)
        basis = whole(reader, ap["basis"], "s5.basis", anchor)
        rp = rule.value["payload"]
        descriptor = rule_registry.get(rp["definition"])
        if descriptor is None:
            raise ResolutionError("rule_unavailable")
        implementation = reader.read(rp["implementation"], rule.package_id)
        if (not isinstance(implementation, ResolvedArtifact)
                or implementation.digest != descriptor.implementation_digest
                or sha256(canonical(rp)).hexdigest() != descriptor.declaration_digest):
            raise ResolutionError("rule_identity_mismatch")
        selected = _selected(reader, basis.value["payload"]["entries"], basis.package_id)
        issue, additional = _intended(reader, assessment, question, rule, basis, selected, descriptor)
        fixed = (assessment, rule, question, basis, audience, implementation, *frontier, *additional)
        evidence = [[item.key, item.role, pin(item.material) if item.material is not None else item.reason]
                    for item in selected]
        budget = [[key, str(value)] for key, value in sorted(asdict(actual_limits.wire).items())]
        budget += [[key, str(getattr(actual_limits, key))]
                   for key in ("predicate_nodes", "predicate_depth", "decision_visits")]
        digest = sha256(canonical([root.digest, [pin(item) for item in fixed], evidence, budget])).hexdigest()
        return PreparedAssessment("held" if issue else "ready", assessment, rule, question, basis,
                                  selected, digest, (issue,) if issue else (), actual_limits)
    except ResolutionError as exc:
        return PreparedAssessment("held", assessment, rule, question, basis, selected, None,
                                  (exc.code,), actual_limits)
