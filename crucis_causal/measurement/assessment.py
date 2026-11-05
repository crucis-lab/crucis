"""Explicit, scoped support assessment over caller-authorized recorded evidence."""

from dataclasses import dataclass
import json

from crucis_causal.execution.api import ReadCapability, supplied_read
from crucis_causal.execution.model import canonical

from .codec import WireError, check_profile_assessment
from .planning import _record
from .resolution import Issue, ResolvedView, ResolutionError, resolve


@dataclass(frozen=True, slots=True)
class ProfileCriterion:
    name: str
    version: str
    profile: str
    check: object


@dataclass(frozen=True, slots=True)
class ProfileAssessment:
    outcome: str
    payload_bytes: bytes | None = None
    issue: Issue | None = None

    @property
    def payload(self):
        return json.loads(self.payload_bytes) if self.payload_bytes is not None else None


def assess(target, recorded_view, criterion, read_context):
    """Assess one proposed role. The explicit trusted criterion owns its scientific rule.

    Target supplies the target, audience, frontier, premises, qualifications and
    basis references in the enclosing snapshot's namespace. No input supplies
    an outcome. The scoped reader is the only evidence interface to the check.
    """
    if not isinstance(recorded_view, ResolvedView) or not isinstance(read_context, ReadCapability):
        raise TypeError("s4.assessment_read_context_required")
    if not isinstance(criterion, ProfileCriterion) or not callable(criterion.check):
        raise TypeError("s4.profile_criterion_required")
    if not isinstance(target, dict) or target.keys() != {
        "target", "audience", "frontier", "premises", "qualifications", "basis",
    }:
        return ProfileAssessment("unassessed", issue=Issue("s4.assessment_fields"))
    limits = recorded_view.limits
    payload = {**target, "profile": criterion.profile,
               "criterion": {"name": criterion.name, "version": criterion.version},
               "outcome": "withheld"}
    try:
        check_profile_assessment(payload, limits)
        snapshot = recorded_view.snapshot
        access = supplied_read({pid for pid in read_context.packages
                                if read_context.permits(pid) and recorded_view._access.permits(pid)})
        reader = resolve(snapshot, recorded_view._supplied, access, limits).reader()
        audience = _record(reader, payload["audience"], "s3.audience")
        if audience != _record(reader, snapshot.package["audience"], "s3.audience"):
            raise ResolutionError("assessment_audience_mismatch")
        if payload["frontier"] != snapshot.package["frontier"]:
            raise ResolutionError("assessment_frontier_mismatch")
        for row in payload["frontier"]:
            if "ref_kind" in row["position"]:
                reader.read(row["position"])
        ref = payload["target"]
        if "goal_key" in ref:
            ref = {**ref["request"], "selector": {"selector_kind": "member", "key": ref["goal_key"]}}
            if ref["expected_contract"]["name"] != "s4.request":
                raise ResolutionError("assessment_goal_contract")
        selected = reader.read(ref)
        premises = tuple(_record(reader, row["assessment"], "s4.premise_assessment")
                         for row in payload["premises"])
        qualifications = tuple(_record(reader, ref, "s4.qualification")
                               for ref in payload["qualifications"])
        basis = tuple(reader.read(ref) for ref in payload["basis"])
        if not basis or criterion.profile in {"p2", "p3", "p4", "p5"} and not qualifications:
            return ProfileAssessment("withheld", canonical(payload), Issue("s4.assessment_basis_missing"))
        for entry in qualifications:
            value = entry.value["payload"]
            _record(reader, value["procedure"], "s4.procedure", entry.package_id)
            _record(reader, value["scope"], "s4.scope", entry.package_id)
            reader.read(value["receipt"], entry.package_id)
            if value["outcome"] != "pass":
                return ProfileAssessment("withheld", canonical(payload), Issue("s4.qualification_not_passed"))
        if criterion.check(reader, selected, audience, premises, qualifications, basis) is not True:
            return ProfileAssessment("withheld", canonical(payload), Issue("s4.criterion_not_established"))
        payload["outcome"] = "established"
        return ProfileAssessment("established", canonical(payload))
    except WireError as exc:
        return ProfileAssessment("unassessed", issue=Issue(exc.code))
    except ResolutionError as exc:
        return ProfileAssessment("withheld", issue=exc.issue)
