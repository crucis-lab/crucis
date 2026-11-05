"""S4 evidence capsules carried by existing S3 projection and publication ports."""

from dataclasses import dataclass
import json

from crucis_causal.connections.codec import dumps as dump_source
from crucis_causal.connections.evidence import capture_bytes
from crucis_causal.connections.model import Builder as SourceBuilder
from crucis_causal.connections.validation import content_bytes
from crucis_causal.execution import api
from crucis_causal.execution.codec import Resolver, dumps as dump_execution, parse_snapshot
from crucis_causal.execution.model import Builder, ExecutionError, contract, index, not_applicable, qualified, reference
from crucis_causal.execution.projection import AudiencePolicies, validate_audience

from .codec import FORMAT, VERSION, Limits, WireError, dumps, inspect
from .resolution import ResolutionError, ResolvedView


CAPSULE = {"name": "s4.measurement_capsule", "version": VERSION}


def register_capsule(payload_registry, limits=Limits()):
    """Install the exact S4 carrier decoder; this confers no claim or permission."""
    def decode(value):
        try:
            return inspect(dumps(value, limits), limits)
        except WireError as exc:
            raise ExecutionError("s3.s4_capsule_wire", exc.path) from exc

    payload_registry.register(CAPSULE, decode)


@dataclass(frozen=True, slots=True)
class Carrier:
    snapshot_id: str
    snapshot_digest: str
    outer: api.PinnedView
    dependencies: tuple[api.PinnedView, ...]
    typed_payload_id: str


@dataclass(frozen=True, slots=True)
class Projection:
    carrier: Carrier
    draft: api.PackageDraft
    read_context: api.PinnedReadContext


def _insert(views, item):
    old = views.get(item.package_id)
    if old is not None and old.source_bytes != item.source_bytes:
        raise ResolutionError("carrier_identity_conflict")
    views[item.package_id] = item


def _raw_for(view, identity):
    return view.snapshot.source_bytes if identity == view.snapshot.snapshot_id else view._supplied[identity]


def _capsule_payload(carrier, resolver, registry):
    if not registry.supports(CAPSULE):
        raise ResolutionError("s4_capsule_decoder_unavailable")
    outer = resolver.view(carrier.outer.package_id)
    subject = reference(carrier.typed_payload_id, "typed_payload", outer.package_id)
    root, _ = resolver.record(outer.package["roots"][0], outer.package_id)
    if (root["record_type"] != "s3.projection_view"
            or not any(r["target"] == carrier.typed_payload_id and r["binding"] == "internal"
                       and r["target_type"] == "s3.typed_payload"
                       for r in root["payload"]["members"]["members"])):
        raise ResolutionError("carrier_root_mismatch")
    resolved, _ = resolver.record(subject, outer.package_id)
    if resolved["payload"]["payload_contract"] != CAPSULE:
        raise ResolutionError("carrier_payload_contract")
    resolver.payload(subject, outer.package_id, registry)
    artifact, _ = resolver.record(resolved["payload"]["content"]["artifact"], outer.package_id)
    return content_bytes(artifact["payload"]["content"])


def _predecessor_views(view, identities, nested, context):
    selected = {}
    for identity in sorted(identities - {view.snapshot.snapshot_id}):
        raw = _raw_for(view, identity)
        name = json.loads(raw)["format"]["name"]
        if name != FORMAT:
            _insert(selected, parse_snapshot(raw, context.limits, access=view._access))
            continue
        supplied = nested.get(identity)
        if not isinstance(supplied, Carrier) or supplied.snapshot_id != identity:
            raise ResolutionError("nested_carrier_required")
        nested_resolver = Resolver((supplied.outer, *supplied.dependencies), limits=context.limits)
        nested_resolver.closure(supplied.outer.package_id)
        carrier_bytes = _capsule_payload(supplied, nested_resolver, context.registry.payloads)
        verified = inspect(carrier_bytes, view.limits)
        if carrier_bytes != raw or verified.digest != supplied.snapshot_digest:
            raise ResolutionError("nested_carrier_integrity")
        for item in (supplied.outer, *supplied.dependencies):
            _insert(selected, item)
    return selected


def prepare_projection(view, audience, supplied_policy, read_context, *, nested=None, claims=()):
    """Construct and authorize exact projection bytes. No storage effect occurs."""
    if not isinstance(view, ResolvedView) or not isinstance(supplied_policy, AudiencePolicies):
        raise ResolutionError("audience_policy_required")
    if (not isinstance(read_context, api.PinnedReadContext) or read_context.registry is None
            or not read_context.registry.payloads.supports(CAPSULE)):
        raise ResolutionError("s4_capsule_decoder_unavailable")
    reader = view.reader()
    identities = reader.verified_closure()
    audience_record = reader.read(view.snapshot.package["audience"])
    expected_audience = reference(audience_record.record_id, "audience", audience_record.package_id)
    if audience != expected_audience:
        raise ResolutionError("s4_projection_audience_mismatch")
    selected = _predecessor_views(view, identities, nested or {}, read_context)
    if any(not read_context.access.permits(item.package_id) for item in selected.values()):
        raise ResolutionError("carrier_read_denied")

    source = SourceBuilder("S4 exact snapshot capsule")
    artifact = capture_bytes(source, view.snapshot.source_bytes, format_contract=CAPSULE,
                             basis="intrinsic")
    artifact_bytes = dump_source(source.package([artifact]))
    artifact_view = parse_snapshot(artifact_bytes, read_context.limits)
    _insert(selected, artifact_view)

    outer = Builder("S4 measurement audience projection")
    payload = outer.add("typed_payload", {
        "payload_contract": CAPSULE,
        "content": {"artifact": qualified(artifact, artifact_view.package_id),
                    "selector": not_applicable()},
        "reference_context": {"package_id": outer.package_id, "format": contract("account_package")},
    })
    root = outer.add("projection_view", {
        "view_role": "audience_projection", "audience": expected_audience,
        "projection_contract": contract("s4.measurement_projection"), "members": index([payload]),
        "claims": index(), "limits": index(),
    })
    dependencies = tuple(selected[identity] for identity in sorted(selected))
    raw = dump_execution(outer.package(root, dependencies), read_context.limits)
    outer_view = parse_snapshot(raw, read_context.limits)
    carrier = Carrier(view.snapshot.snapshot_id, view.snapshot.digest, outer_view,
                      dependencies, payload["target"])
    all_views = (outer_view, *dependencies)
    context = api.PinnedReadContext(all_views, api.supplied_read(v.package_id for v in all_views),
                                   read_context.registry, read_context.limits)
    resolver = Resolver(all_views, limits=context.limits)
    if _capsule_payload(carrier, resolver, context.registry.payloads) != view.snapshot.source_bytes:
        raise ResolutionError("carrier_payload_integrity")
    result = supplied_policy.freeze(outer_view, expected_audience, claims, context)
    if result.state != "completed":
        raise ResolutionError(result.issues[0].code if result.issues else "audience_policy_held")
    validate_audience(outer_view, result.value.audience, resolver, context.registry.payloads)
    return Projection(carrier, result.value, context)


@dataclass(frozen=True, slots=True)
class AuthorizedStorage:
    store: api.StoragePort
    grants: object
    issue_token: api.IssueToken
    context: api.StorageContext


def read_carrier(carrier, read_context, limits=Limits()):
    """Read the exact inner package using the caller's established S3 access."""
    if not read_context.access.permits(carrier.outer.package_id):
        raise ResolutionError("carrier_read_denied")
    if any(not read_context.access.permits(v.package_id) for v in read_context.views):
        raise ResolutionError("carrier_read_denied")
    resolver = Resolver(read_context.views, limits=read_context.limits)
    outer = resolver.view(carrier.outer.package_id)
    if outer.source_bytes != carrier.outer.source_bytes:
        raise ResolutionError("carrier_identity_conflict")
    if any(not read_context.access.permits(v.package_id) for v in resolver.closure(outer.package_id)):
        raise ResolutionError("carrier_read_denied")
    inner = inspect(_capsule_payload(carrier, resolver, read_context.registry.payloads), limits)
    if (inner.snapshot_id, inner.digest) != (carrier.snapshot_id, carrier.snapshot_digest):
        raise ResolutionError("carrier_payload_integrity")
    return inner


def publish(projection, publication_id, authorization):
    """Use S3's existing storage admission, correlation and commit boundary."""
    if not isinstance(projection, Projection) or not isinstance(authorization, AuthorizedStorage):
        raise TypeError("s4.projection_and_storage_authorization_required")
    carrier, draft = projection.carrier, projection.draft
    if draft.bytes != carrier.outer.source_bytes or draft.digest != carrier.outer.digest:
        raise ResolutionError("projection_draft_changed")
    read = projection.read_context
    resolver = Resolver(read.views, limits=read.limits)
    validate_audience(carrier.outer, draft.audience, resolver, read.registry.payloads)
    read_carrier(carrier, read)
    return authorization.store.publish(
        publication_id, draft.bytes, draft.package_id, draft.digest, draft.audience,
        authorization.grants, authorization.issue_token, authorization.context,
    )
