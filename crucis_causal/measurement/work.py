"""S4 calculation admission, observation and durable S3 journal evidence."""

from dataclasses import dataclass
import fractions
from hashlib import sha256
from importlib.metadata import version
import json
import platform
import sys
from threading import RLock
from uuid import UUID, uuid4

from crucis_causal.execution import api
from crucis_causal.execution.journal import delta_binding
from crucis_causal.execution.model import Builder, canonical, digest, scope

from .calculation import EmissionBatch, Evaluator, evaluate
from .planning import Registry, plan
from .resolution import Issue


def _key(account, invocation, phase):
    material = canonical(["s4.work", account, invocation, phase])
    # S3's ID grammar requires the version-four and RFC variant bits. This
    # is a deterministic correlation ID; journal append checks the full basis.
    return str(UUID(bytes=sha256(material).digest()[:16], version=4))


def _runtime_pin(path):
    total = 0
    digestor = sha256()
    with open(path, "rb") as source:
        for chunk in iter(lambda: source.read(65536), b""):
            total += len(chunk)
            if total > 33554432:
                raise ValueError("s4.runtime_pin_limit")
            digestor.update(chunk)
    return digestor.hexdigest()


@dataclass(frozen=True, slots=True)
class WorkReport:
    invocation_id: str
    basis_digest: str | None
    occurrence_id: str | None
    state: str
    entry_revision: str | None
    emissions: EmissionBatch | None
    issues: tuple[Issue, ...]
    plan_evidence: bytes | None = None


@dataclass(frozen=True, slots=True)
class RecordDisposition:
    state: str
    issue: Issue | None = None
    receipt_bytes: bytes | None = None


@dataclass(frozen=True, slots=True)
class Recovery:
    state: str
    occurrence_id: str | None = None
    event_bytes: bytes | None = None


class Coordinator:
    """Use the supplied S3 account owner and append/lookup ports.

    The registry, journal, account, and live journal authority are injected
    by the caller. A serialized S4 plan never grants execution authority.
    """

    def __init__(self, journal, account, journal_context, evaluators, *, fault=None):
        selected = {}
        for evaluator in evaluators:
            if not isinstance(evaluator, Evaluator):
                raise TypeError("s4.evaluator_required")
            descriptor = evaluator.descriptor
            key = descriptor.name, descriptor.version
            if key in selected:
                raise ValueError("s4.duplicate_evaluator")
            selected[key] = evaluator
        self._evaluators = selected
        self._registry = Registry(entry.descriptor for entry in selected.values())
        self._journal = journal
        self._account_bytes = canonical(account)
        self._context = journal_context
        self._fault = fault
        self._environment = canonical({
            "implementation": platform.python_implementation(),
            "python": platform.python_version(),
            "system": platform.system(),
            "machine": platform.machine(),
            "byteorder": sys.byteorder,
            "jsonschema": version("jsonschema"),
            "interpreter_sha256": _runtime_pin(getattr(sys, "_base_executable", sys.executable)),
            "fractions_sha256": _runtime_pin(fractions.__file__),
        })
        self._reports = {}
        self._lock = RLock()

    @property
    def account(self):
        return json.loads(self._account_bytes)

    def _event_delta(self, invocation, phase, event):
        account = self.account
        producer = _key(account, "measurement-recorder", "component")
        builder = Builder("S4 measurement journal recorder", producer_id=producer)
        event_id = _key(account, invocation, phase)
        builder.add("diagnostic", {
            "code": "s4.work." + phase,
            "scope": scope(account),
            "details": canonical(event).decode("utf-8"),
            "evidence": [],
        }, record_id=event_id)
        return api.CommitDelta(tuple(builder._records.values()))

    def _append(self, invocation, phase, revision, event):
        account = self.account
        delta = self._event_delta(invocation, phase, event)
        transaction = _key(account, invocation, phase + ".tx")
        expected = digest(canonical({
            "account": account, "expected_revision": revision, "delta": delta_binding(delta),
        }))
        result = self._journal.append(account, revision, transaction, delta, self._context)
        if result.state == "completed" and result.value.binding_digest == expected:
            return result.value, expected, None
        issue = result.issues[0].code if result.issues else "s4.commit_unconfirmed"
        return None, expected, Issue(issue)

    def _event(self, head, invocation, phase):
        event_id = _key(self.account, invocation, phase)
        for record in head.snapshot.records:
            if record["id"] != event_id:
                continue
            payload = record["payload"]
            if record["record_type"] != "s3.diagnostic" or payload["code"] != "s4.work." + phase:
                raise ValueError("s4.journal_event_contract")
            raw = payload["details"].encode("utf-8")
            event = json.loads(raw)
            if raw != canonical(event) or event["invocation_id"] != invocation or event["phase"] != phase:
                raise ValueError("s4.journal_event_contract")
            return event
        return None

    def _head(self):
        result = self._journal.head(self.account, self._context)
        return result.value if result.state == "completed" else None

    def _checkpoint(self, name):
        if self._fault is not None:
            self._fault(name)

    def _plan_evidence(self, selected):
        def pin(record):
            return {"package_id": record.package_id, "digest": record.package_digest,
                    "record_id": record.record_id}

        descriptor = selected.descriptor
        return {
            "plan": pin(selected.plan_record),
            "procedure": {"name": descriptor.name, "version": descriptor.version,
                          "implementation_digest": descriptor.implementation_digest},
            "environment": json.loads(self._environment),
            "outputs": [{"key": out.key, "binding": pin(out.binding), "scope": pin(out.scope),
                         "role": out.output_role, "subject_key": out.subject_key}
                        for out in selected.outputs],
        }

    def execute(self, goal, invocation_id, view):
        """Prepare and admit one calculation. Each request makes a new claim."""
        if (not isinstance(invocation_id, str) or not invocation_id or len(invocation_id) > 128
                or not invocation_id.isascii()
                or any(not (ch.isalnum() or ch in "._-") for ch in invocation_id)):
            raise ValueError("s4.invocation_id")
        selected = plan(goal, view, self._registry)
        basis = selected.basis_digest
        if not selected.outputs:
            issues = selected.issues + tuple(out.issue for out in selected.held)
            return WorkReport(invocation_id, basis, None, "held", None, None, issues)
        head = self._head()
        if head is None:
            return WorkReport(invocation_id, basis, None, "held", None, None,
                              (Issue("s4.journal_head_unavailable"),))
        prior = self._event(head, invocation_id, "intent")
        if prior is not None:
            issue = "s4.invocation_already_admitted" if prior["basis_digest"] == basis else "s4.invocation_basis_conflict"
            return WorkReport(invocation_id, basis, None, "held", None, None, (Issue(issue),))
        with self._lock:
            if len(self._reports) >= view.limits.records:
                return WorkReport(invocation_id, basis, None, "held", None, None,
                                  (Issue("s4.observation_capacity"),))
        # A fresh claim makes a concurrent duplicate conflict at S3's stable
        # transaction identity, even if it selected the same plan and bytes.
        claim = uuid4().hex
        evidence = self._plan_evidence(selected)
        event = {"invocation_id": invocation_id, "basis_digest": basis, "claim": claim,
                 "phase": "intent", "previous_revision": head.revision, "plan_evidence": evidence}
        intent, _, issue = self._append(invocation_id, "intent", head.revision, event)
        if intent is None:
            state = "admission_unconfirmed" if issue.code in (
                "s3.journal_commit_unconfirmed", "s4.commit_unconfirmed") else "held"
            return WorkReport(invocation_id, basis, None, state, None,
                              None, (issue,))
        self._checkpoint("after_intent")
        occurrence = _key(self.account, invocation_id, "occurrence." + claim)
        entry = {**event, "phase": "entry", "previous_revision": intent.head.revision,
                 "occurrence_id": occurrence}
        entered, _, issue = self._append(invocation_id, "entry", intent.head.revision, entry)
        if entered is None:
            return WorkReport(invocation_id, basis, None, "entry_unconfirmed", None, None, (issue,))
        self._checkpoint("after_entry")
        descriptor = selected.descriptor
        evaluator = self._evaluators[(descriptor.name, descriptor.version)]
        batch = evaluate(selected.outputs, evaluator, selected.limits)
        issues = tuple(Issue(out.issue.code, out.key) for out in selected.held) + batch.issues
        state = "partial" if batch.emissions and issues else "completed" if batch.emissions else "failed"
        report = WorkReport(invocation_id, basis, occurrence, state, entered.head.revision, batch,
                            issues, canonical(evidence))
        with self._lock:
            self._reports[invocation_id] = (report, claim)
        return report

    def _work_event(self, report, claim, revision):
        return {
            "phase": "result", "invocation_id": report.invocation_id, "claim": claim,
            "basis_digest": report.basis_digest, "occurrence_id": report.occurrence_id,
            "previous_revision": revision, "entry_revision": report.entry_revision,
            "state": report.state, "rational_operations": str(report.emissions.operations),
            "plan_evidence": json.loads(report.plan_evidence),
            "emissions": [{"key": item.output_key, "outcome": item.outcome}
                          for item in report.emissions.emissions],
            "issues": [{"code": issue.code, "scope": issue.scope} for issue in report.issues],
        }

    def record(self, work_report, expected_head=None):
        """Durably record an observed report, with no path back to evaluation."""
        if not isinstance(work_report, WorkReport):
            return RecordDisposition("held", Issue("s4.observed_work_required"))
        invocation = work_report.invocation_id
        head = self._head()
        if head is None:
            return RecordDisposition("unknown", Issue("s4.journal_head_unavailable"))
        saved = self._event(head, invocation, "result")
        with self._lock:
            minted = self._reports.get(invocation)
        if saved is not None:
            reconstructed = None
            if work_report.emissions and work_report.plan_evidence:
                reconstructed = self._work_event(work_report, saved["claim"], saved["previous_revision"])
            if reconstructed != saved:
                return RecordDisposition("disputed", Issue("s4.recorded_work_conflict"))
            disposition = self._lookup_event(saved)
            if disposition.state == "committed":
                with self._lock:
                    self._reports.pop(invocation, None)
            return disposition
        if minted is None or minted[0] is not work_report:
            return RecordDisposition("held", Issue("s4.observed_work_required"))
        revision = head.revision if expected_head is None else expected_head
        event = self._work_event(work_report, minted[1], revision)
        committed, _, issue = self._append(invocation, "result", revision, event)
        if committed is None:
            if issue.code == "s3.transaction_binding_conflict":
                return RecordDisposition("disputed", issue)
            if issue.code not in ("s3.journal_commit_unconfirmed", "s4.commit_unconfirmed"):
                return RecordDisposition("held", issue)
            return RecordDisposition("unknown", issue)
        with self._lock:
            self._reports.pop(invocation, None)
        return RecordDisposition("committed", receipt_bytes=canonical(committed.receipt))

    def _lookup_event(self, event):
        invocation, phase = event["invocation_id"], event["phase"]
        account = self.account
        delta = self._event_delta(invocation, phase, event)
        expected = digest(canonical({
            "account": account, "expected_revision": event["previous_revision"],
            "delta": delta_binding(delta),
        }))
        result = self._journal.lookup_transaction(
            account, _key(account, invocation, phase + ".tx"), expected, self._context,
        )
        if result.state != "completed":
            return RecordDisposition("unknown", Issue("s4.commit_lookup_unconfirmed"))
        lookup = result.value
        if lookup.state == "committed":
            return RecordDisposition("committed", receipt_bytes=canonical(lookup.commit))
        return RecordDisposition(lookup.state, Issue("s4.commit_" + lookup.state))

    def recover(self, invocation_id, basis_digest):
        """Read the exact journal account. Recovery never evaluates again."""
        head = self._head()
        if head is None:
            return Recovery("unknown")
        phases = (("intent", "intent_observed"), ("entry", "entry_observed"),
                  ("result", "recorded"))
        events = [self._event(head, invocation_id, phase) for phase, _ in phases]
        if not any(events):
            return Recovery("no_intent_observed")
        if events[0] is None or events[2] is not None and events[1] is None:
            return Recovery("disputed")
        claim = events[0]["claim"]
        observed = Recovery("unknown")
        for event, (_, state) in zip(events, phases):
            if event is None:
                break
            if (event["basis_digest"] != basis_digest or event["claim"] != claim
                    or event["plan_evidence"] != events[0]["plan_evidence"]):
                return Recovery("disputed")
            expected = _key(self.account, invocation_id, "occurrence." + claim)
            if "occurrence_id" in event and event["occurrence_id"] != expected:
                return Recovery("disputed")
            lookup = self._lookup_event(event)
            if lookup.state != "committed":
                return Recovery("disputed" if lookup.state == "disputed" else "unknown")
            observed = Recovery(state, event.get("occurrence_id"), canonical(event))
        return observed
