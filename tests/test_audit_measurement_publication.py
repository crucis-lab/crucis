"""B09 exact S4 capsule closure and actual local S3 publication fixtures."""

from hashlib import sha256
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).with_name("audit_fixtures") / "sc3_runtime"))
import publication_case as s3_case

from crucis_causal.execution import api
from crucis_causal.execution.model import identity, qualified, reference
from crucis_causal.measurement import (
    ResolutionError, dumps, inspect, prepare_projection, read_carrier, register_capsule, resolve,
)
from s4_wire_examples import contract, external, local, pin
from test_audit_execution_journal import scratch
from test_audit_execution_publication import oracle, receipts


def measurement(env, outer, audience, *, name="public", predecessor=None, allowed=True):
    producer = next(r for r in outer.records if r["record_type"] == "s3.component")
    source = external("audience", producer["id"], "s3.component", producer["contract"]["version"])
    selected = external("audience", audience["target"], "s3.audience", producer["contract"]["version"])
    dependency = {"key": "audience", "package_id": outer.package_id, "format": outer.format,
                  "pin": pin(outer.digest["value"], len(outer.source_bytes))}
    sources = {v.package_id: v.source_bytes for v in env.context.read.views}
    # The fixture may carry many unrelated views. Supply only the exact
    # S3 audience snapshot and its declared predecessor bytes.
    actual = {outer.package_id: outer.source_bytes}
    for dep in outer.package["external_packages"]:
        actual[dep["package_id"]] = sources[dep["package_id"]]
    dependencies = [dependency]
    basis = [source]
    if predecessor is not None:
        old = predecessor.snapshot
        dependencies.append({"key": "prior", "package_id": old.snapshot_id,
                             "format": old.package["format"],
                             "pin": pin(old.digest, len(old.source_bytes))})
        actual[old.snapshot_id] = old.source_bytes
        basis = [source, external("prior", "src", "s4.source", old.package["format"]["version"])]
    package = {
        "format": contract("s4.measurement_package"), "account_id": "account.measurement",
        "snapshot_id": "snapshot." + name, "audience": selected,
        "frontier": [{"key": "audience", "position": selected}],
        "dependencies": dependencies, "roots": [local("acct", "account")],
        "records": [
            {"id": "acct", "kind": "s4.account", "contract": contract("s4.account"),
             "payload": {"observer": source, "sources": [local("src", "source")]}},
            {"id": "src", "kind": "s4.source", "contract": contract("s4.source"),
             "payload": {"subject": "s4.fixture", "attribution": source, "extent": "complete",
                         "observations": [], "basis": basis, "verbatim": name + " fixture data"}},
        ],
    }
    snap = inspect(dumps(package))
    cap = api.supplied_read([snap.snapshot_id, *(actual if allowed else ())])
    return resolve(snap, actual, cap)


class MeasurementPublicationCases(unittest.TestCase):
    def test_carrier_preserves_inner_bytes_and_lost_reply_reconciles(self):
        with scratch() as root:
            env = s3_case.Environment(root)
            audience_view, audience = env.target()
            view = measurement(env, audience_view, audience)
            policies = env.coordinator.audience_policies
            with self.assertRaisesRegex(ResolutionError, "s4_capsule_decoder_unavailable"):
                prepare_projection(view, audience, policies, env.context.read)
            register_capsule(env.registry.payloads)
            projection = prepare_projection(view, audience, policies, env.context.read)
            self.assertEqual(read_carrier(projection.carrier, projection.read_context).source_bytes,
                             view.snapshot.source_bytes)
            env.include(*projection.read_context.views)
            draft = projection.draft
            request = env.publish_request(draft)
            publication_id = next(p["value"]["value"] for p in request.parameters
                                  if p["key"] == "publication_id")
            planned = env.plan(request)
            self.assertEqual(planned.state, "completed", planned.issues)
            group, transmission = identity(), identity()
            packet = s3_case.packet(env, planned.value, group, transmission)

            def dropped(label):
                if label == "publication_after_commit":
                    raise OSError("fixture lost reply")

            env.store_fault = dropped
            admitted = env.admit(planned.value, group=group)
            self.assertEqual(admitted.state, "completed", admitted.issues)
            lost = env.issue(admitted.value, transmission=transmission)
            self.assertNotEqual(lost.state, "completed")
            self.assertEqual(len(oracle(env)["publications"]), 1)
            cold, _ = s3_case.reopen(packet)
            register_capsule(cold.registry.payloads)
            found = cold.run(cold.lookup_request(planned.value.command, draft, publication_id))
            self.assertEqual(found.state, "completed", found.issues)
            self.assertEqual(cold.store.artifacts.read(draft.digest), draft.bytes)
            self.assertEqual(len(oracle(cold)["publications"]), 1)
            self.assertEqual(projection.carrier.snapshot_digest, sha256(view.snapshot.source_bytes).hexdigest())

    def test_public_projection_excludes_restricted_dependency_and_nested_pins_match(self):
        with scratch() as root:
            env = s3_case.Environment(root)
            register_capsule(env.registry.payloads)
            outer, audience = env.target(label="explicit-audience-fixture")
            policies = env.coordinator.audience_policies
            restricted = measurement(env, outer, audience, name="restricted")
            denied = measurement(env, outer, audience, name="restricted", allowed=False)
            with self.assertRaisesRegex(ResolutionError, "read_denied"):
                prepare_projection(denied, audience, policies, env.context.read)
            original = prepare_projection(restricted, audience, policies, env.context.read)
            env.include(*original.read_context.views)

            narrow = measurement(env, outer, audience, name="narrow")
            public = prepare_projection(narrow, audience, policies, env.context.read)
            self.assertNotIn(b"restricted fixture data", narrow.snapshot.source_bytes)
            self.assertNotIn(original.carrier.outer.package_id,
                             {v.package_id for v in public.carrier.dependencies})
            follow = measurement(env, outer, audience, name="follow", predecessor=restricted)
            with self.assertRaisesRegex(ResolutionError, "nested_carrier_required"):
                prepare_projection(follow, audience, policies, env.context.read)
            closed = prepare_projection(follow, audience, policies, env.context.read,
                                        nested={restricted.snapshot.snapshot_id: original.carrier})
            self.assertIn(original.carrier.outer.package_id,
                          {v.package_id for v in closed.carrier.dependencies})

    def test_committed_carrier_survives_failed_pointer_revision(self):
        with scratch() as root:
            env = s3_case.Environment(root)
            register_capsule(env.registry.payloads)
            outer, audience = env.target()
            view = measurement(env, outer, audience, name="pointer")
            prepared = prepare_projection(view, audience, env.coordinator.audience_policies, env.context.read)
            env.include(*prepared.read_context.views)

            def interrupt_stage(label):
                if label == "publication_after_stage":
                    raise OSError("fixture interrupted staged bytes")

            env.store_fault = interrupt_stage
            interrupted = env.run(env.publish_request(prepared.draft))
            self.assertNotEqual(interrupted.state, "completed")
            self.assertEqual(oracle(env)["publications"], [])
            env.store_fault = None
            outcome = env.run(env.publish_request(prepared.draft))
            self.assertEqual(outcome.state, "completed", outcome.issues)
            rec = receipts(outcome)[0]
            carrier = prepared.carrier.outer
            receipt_package = next(v.package_id for v in outcome.records.dependencies
                                   if any(r["id"] == rec["id"] for r in v.records))
            ref = qualified(reference(rec["id"], "publication_receipt"), receipt_package)
            self.assertEqual(env.run(env.pointer_request(carrier, ref, "0")).state, "completed")
            stale = env.run(env.pointer_request(carrier, ref, "0"))
            self.assertNotEqual(stale.state, "completed")
            self.assertEqual(env.store.artifacts.read(prepared.draft.digest), prepared.draft.bytes)
