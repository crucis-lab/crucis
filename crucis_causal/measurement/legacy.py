"""Read-only, versioned interpretation of selected historical measurement fields."""

from dataclasses import dataclass
from decimal import Decimal, DecimalException
from hashlib import sha256
import json
from types import MappingProxyType

from .codec import Limits, WireError


@dataclass(frozen=True, slots=True)
class MappingRule:
    family: str
    required: frozenset[str]
    semantics: tuple[tuple[str, str], ...]


def _rule(family, required, **semantics):
    return MappingRule(family, frozenset(required), tuple(sorted(semantics.items())))


RULES = MappingProxyType({
    "legacy.l0.graph.v1": _rule("legacy_graph_metrics",
        {"adj_f1", "dir_f1@expect", "dir_f1@committed"},
        adjacency="historical_adjacency_f1", expected_direction="historical_seeded_expectation",
        committed_direction="historical_committed_only"),
    "legacy.l0.reference.v1": _rule("legacy_reference", {"tier", "path", "seed_name"},
        tier="original_reference_tier", seed="historical_orientation_seed_basis"),
    "legacy.l0.arm.v1": _rule("legacy_arm_summary", {"runs", "ok", "executed", "statuses"},
        completed="historical_completed_and_scored", delivered="historical_executed_failure_as_zero"),
    "legacy.paired.cluster.v1": _rule("legacy_cluster_paired",
        {"point", "lo", "hi", "units", "clusters", "B", "seed"},
        frame="historical_common_keys", interval="historical_cluster_bootstrap"),
    "legacy.calibration.v1": _rule("legacy_calibration_report", {"calibration"},
        calibration="historical_declared_calibration_payload"),
    "legacy.ranking.v1": _rule("legacy_ranking_report", {"ranking"},
        ranking="historical_declared_ranking_payload"),
    "legacy.report.v1": _rule("legacy_audit_report",
        {"audit", "protocol", "battery", "runs_manifest_sha256", "l0", "findings"},
        claims="historical_reported_findings", evidence="historical_report_manifest"),
    "legacy.certificate.v1": _rule("legacy_certificate", {"body", "sha256"},
        basis="historical_certificate_body", receipt="historical_recorded_integrity_claim"),
})


@dataclass(frozen=True, slots=True)
class LegacyAttribution:
    route: str
    expected_sha256: str
    source_reference: str
    selector: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class LegacyCapture:
    raw: bytes
    sha256: str
    state: str
    reason: str
    attribution: LegacyAttribution | None
    rule: MappingRule | None = None

    @property
    def reported_payload(self):
        if self.state != "interpreted":
            return None
        return _selected(self.raw, self.attribution.selector)


def _pairs(pairs):
    found = {}
    for key, value in pairs:
        if key in found:
            raise ValueError("duplicate historical field")
        found[key] = value
    return found


def _invalid_constant(_):
    raise ValueError("uninterpretable historical numeric token")


def _selected(raw, selector, max_digits=256):
    def integer(text):
        if len(text.lstrip("-")) > max_digits:
            raise ValueError("historical integer limit")
        return int(text)

    def decimal(text):
        coefficient, marker, exponent = text.lower().partition("e")
        if (len(coefficient) > max_digits + 2 or marker and
                (len(exponent.lstrip("+-")) > 4 or abs(int(exponent)) > 4096)):
            raise ValueError("historical decimal limit")
        return Decimal(text)

    value = json.loads(raw.decode("utf-8", errors="strict"), parse_int=integer,
                       parse_float=decimal, object_pairs_hook=_pairs,
                       parse_constant=_invalid_constant)
    for key in selector:
        if not isinstance(value, dict) or key not in value:
            raise ValueError("historical selector is unresolved")
        value = value[key]
    if not isinstance(value, dict):
        raise ValueError("historical payload must be an object")
    return value


def capture_legacy(raw, attribution=None, limits=Limits()):
    """Preserve supplied bytes, and interpret known historical roles when pinned.

    This is a reported-evidence view. It carries no S4 calculation, native
    history, scientific profile assessment or reproduction receipt.
    """
    if type(raw) is not bytes:
        raise WireError("immutable_bytes_required")
    if len(raw) > limits.snapshot_bytes:
        raise WireError("manifest_limit")
    digest = sha256(raw).hexdigest()
    if attribution is None:
        return LegacyCapture(raw, digest, "opaque", "origin_and_route_unresolved", None)
    if not isinstance(attribution, LegacyAttribution):
        raise TypeError("s4.legacy_attribution_required")
    if digest != attribution.expected_sha256:
        return LegacyCapture(raw, digest, "held", "historical_bytes_changed", attribution)
    rule = RULES.get(attribution.route)
    if rule is None or not attribution.source_reference:
        return LegacyCapture(raw, digest, "opaque", "historical_contract_unestablished", attribution)
    if len(attribution.selector) > limits.depth:
        return LegacyCapture(raw, digest, "held", "historical_selector_limit", attribution)
    try:
        payload = _selected(raw, attribution.selector, limits.integer_digits)
        if not rule.required <= payload.keys():
            raise ValueError("missing fields")
    except (UnicodeError, ValueError, DecimalException, RecursionError):
        return LegacyCapture(raw, digest, "held", "historical_payload_unestablished", attribution)
    return LegacyCapture(raw, digest, "interpreted", "reported_legacy_scope", attribution, rule)
