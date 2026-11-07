
"""Bounded exact S5 snapshots, with no dependency reads or scientific effects."""

from dataclasses import dataclass
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from crucis_causal.execution.codec import check_tree, loads
from crucis_causal.execution.model import ExecutionError, walk
from crucis_causal.measurement import codec as shared

FORMAT = "s5.finding_package"
VERSION = "0.1.0-proposal.1"


class WireError(ValueError):
    def __init__(self, code, path=""):
        self.code = "s5." + code.removeprefix("s5.")
        self.path = path
        super().__init__(f"{self.code}: {path}" if path else self.code)


@dataclass(frozen=True, slots=True)
class Limits:
    wire: shared.Limits = shared.Limits()
    predicate_nodes: int = 4096
    predicate_depth: int = 32
    decision_visits: int = 32768

    def __post_init__(self):
        if not isinstance(self.wire, shared.Limits):
            raise WireError("wire_limits_required")
        for name, cap in (("predicate_nodes", 4096), ("predicate_depth", 32),
                          ("decision_visits", 32768)):
            value = getattr(self, name)
            if type(value) is not int or not 0 < value <= cap:
                raise WireError("invalid_limit", name)


@dataclass(frozen=True, slots=True)
class Snapshot:
    source_bytes: bytes
    snapshot_id: str
    account_id: str
    digest: str

    @property
    def package(self):
        return json.loads(self.source_bytes)


@lru_cache(maxsize=1)
def _validators():
    schema = json.loads(Path(__file__).with_name("wire.schema.json").read_bytes())
    Draft202012Validator.check_schema(schema)
    defs = schema["$defs"]
    variants = {
        row["properties"]["kind"]["const"]: Draft202012Validator({"$defs": defs, **row})
        for row in defs["record"]["oneOf"]
    }
    envelope = {**schema, "properties": {**schema["properties"],
                                        "records": {"type": "array", "minItems": 1}}}
    return (Draft202012Validator(envelope), variants,
            Draft202012Validator({"$defs": defs, "$ref": "#/$defs/reference"}))


def _shared(check, *args):
    try:
        return check(*args)
    except (shared.WireError, ExecutionError) as exc:
        raise WireError(exc.code.split(".", 1)[-1], exc.path) from exc


_KEYED = {"frontier", "dependencies", "entries", "operands", "clauses", "trace",
          "statements", "reported"}
_SETS = {"items", "history", "profiles", "related", "dimensions", "adjudication",
         "evidence", "proof", "limitations", "prerequisites", "observations", "alternatives", "children"}


def _forms(value, limits):
    refs = []
    for path, item, _ in walk(value):
        if isinstance(item, list):
            key = path.rsplit("/", 1)[-1]
            if key in _KEYED or key == "records":
                _shared(shared._check_keys, item, "id" if key == "records" else "key", path)
            if key in _SETS:
                _shared(shared._check_set, item, path)
        if not isinstance(item, dict):
            continue
        if "ref_kind" in item:
            refs.append((path, item))
            if len(refs) > limits.reference_nodes:
                raise WireError("reference_count_limit", path)
        if item.get("number_kind") == "int":
            _shared(shared._check_decimal, item["text"], limits, path)
        if item.get("number_kind") == "rational":
            _shared(shared._fraction, item, limits, path)
        if item.get("algorithm") == "sha256":
            length = _shared(shared._check_decimal, item["length"], limits, path)
            extent = item["extent"]
            if extent["extent_kind"] == "byte_range":
                start = _shared(shared._check_decimal, extent["start"], limits, path)
                end = _shared(shared._check_decimal, extent["end_exclusive"], limits, path)
                if start > end or end - start != length:
                    raise WireError("extent_length_mismatch", path)
    return refs


def check_reference(reference, limits):
    _shared(check_tree, reference, limits.wire.execution_limits())
    _shared(shared._check_shape, _validators()[2], reference)
    _forms(reference, limits.wire)


def _role(reference, expected, path):
    if reference["expected_contract"]["name"] != expected:
        raise WireError("role_contract", path)


def _predicate(rule, limits, path):
    clauses = {clause["key"]: clause for clause in rule["clauses"]}
    operands = {operand["key"]: operand for operand in rule["operands"]}
    if len(clauses) > limits.predicate_nodes:
        raise WireError("predicate_node_limit", path)
    edges, used = {}, set()
    for key, clause in clauses.items():
        if clause["kind"] == "compare":
            operand = clause["operand"]
            if operand not in operands:
                raise WireError("unknown_operand", path)
            used.add(operand)
            edges[key] = ()
        else:
            if any(child not in clauses for child in clause["children"]):
                raise WireError("unknown_clause", path)
            edges[key] = clause["children"]
    policy = rule["decision_policy"]
    roots = (policy["root"],) if policy["kind"] == "predicate" else (policy["positive"], policy["negative"])
    if any(root not in clauses for root in roots) or len(set(roots)) != len(roots):
        raise WireError("decision_root", path)
    visited, active = {}, set()

    def visit(node, depth):
        if depth > limits.predicate_depth:
            raise WireError("predicate_depth_limit", path)
        if node in active:
            raise WireError("predicate_cycle", path)
        if node not in visited:
            active.add(node)
            visited[node] = max((visit(child, depth + 1) for child in edges[node]), default=0)
            active.remove(node)
        if depth + visited[node] > limits.predicate_depth:
            raise WireError("predicate_depth_limit", path)
        return 1 + visited[node]

    for root in roots:
        visit(root, 1)
    if visited.keys() != clauses.keys() or used != operands.keys():
        raise WireError("unused_predicate_definition", path)

def _local_semantics(records, limits):
    for ident, record in records.items():
        kind, payload = record["kind"], record["payload"]
        if kind in {"s5.assessment", "s5.basis", "s5.decision", "s5.registration"}:
            _role(payload["question"], "s5.question", ident)
            _role(payload["rule"], "s5.rule", ident)
        if kind in {"s5.assessment", "s5.decision", "s5.registration"}:
            _role(payload["basis"], "s5.basis", ident)
        if kind == "s5.rule":
            _predicate(payload, limits, ident)
        if kind == "s5.assessment":
            for axis in ("applicability", "execution", "sufficiency", "decision", "registration"):
                state = payload[axis]
                for name in ("basis", "decision", "registration"):
                    if name in state:
                        _role(state[name], "s5." + name, ident)
            if payload["decision"]["state"] == "completed":
                if (payload["applicability"]["state"] != "applicable"
                        or payload["sufficiency"]["state"] != "sufficient"):
                    raise WireError("decision_prerequisite", ident)
        if kind == "s5.basis" and (bool(payload["entries"]) == ("empty_reason" in payload)):
            raise WireError("basis_extent", ident)
        if kind == "s5.history":
            relationship = payload["relationship"]
            if relationship == "dispute" and len(payload["related"]) < 2:
                raise WireError("history_dispute_cardinality", ident)
            if relationship in {"correction", "retraction", "resolution"} and "adjudication" not in payload:
                raise WireError("history_adjudication_required", ident)
            for ref in (payload["subject"], *payload["related"]):
                _role(ref, "s5.assessment", ident)
        if kind == "s5.decision":
            _role(payload["work"], "s3.diagnostic", ident)
            for row in payload["trace"]:
                established = row["state"] in {"true", "false", "inconclusive"}
                if (established and "evidence" not in row) or (not established and "reason" not in row):
                    raise WireError("decision_trace_basis", ident)
        if kind == "s5.account":
            allowed = {"s5.assessment", "s5.capture", "s5.handoff"}
            if any(ref["expected_contract"]["name"] not in allowed or ref["ref_kind"] != "local"
                   or "selector" in ref for ref in payload["items"]):
                raise WireError("account_item_contract", ident)
            for field, expected in (("history", "s5.history"), ("profiles", "s5.profile_claim")):
                for ref in payload.get(field, ()):
                    _role(ref, expected, ident)


def _links(package, records, refs, limits):
    dependencies = {item["key"]: item for item in package["dependencies"]}
    identities = [item["package_id"] for item in dependencies.values()]
    if len(identities) != len(set(identities)) or package["snapshot_id"] in identities:
        raise WireError("duplicate_or_self_dependency", "/dependencies")
    edges = {key: set() for key in records}
    members = {key: {row["key"] for row in value["payload"]["entries"]}
               for key, value in records.items() if value["kind"] == "s5.basis"}
    for visit, (path, ref) in enumerate(refs, 1):
        if visit > limits.reference_visits:
            raise WireError("reference_visit_limit", path)
        kind = ref["ref_kind"]
        if kind == "artifact":
            _role(ref["artifact_record"], "s1.artifact_snapshot", path)
            if "selector" in ref["artifact_record"]:
                raise WireError("artifact_record_selector", path)
            continue
        if kind == "external":
            if ref["dependency_key"] not in dependencies:
                raise WireError("undeclared_dependency", path)
            continue
        target = records.get(ref["target_id"])
        if target is None or target["contract"] != ref["expected_contract"]:
            raise WireError("reference_target", path)
        if "selector" in ref and ref["selector"]["key"] not in members.get(target["id"], ()):
            raise WireError("selector_target", path)
        if path.startswith("/records/"):
            index = int(path.split("/", 3)[2])
            owner = package["records"][index]
            if owner["kind"] != "s5.account":
                edges[owner["id"]].add(target["id"])
    _shared(shared._verify_proof_dag, edges)
    root = package["roots"][0]
    if root["ref_kind"] != "local" or "selector" in root:
        raise WireError("local_account_required", "/roots")
    _role(root, "s5.account", "/roots")
    _role(package["audience"], "s3.audience", "/audience")
    if "selector" in package["audience"]:
        raise WireError("whole_audience_required", "/audience")


def _validate(value, limits):
    envelope, variants, _ = _validators()
    _shared(shared._check_shape, envelope, value)
    if len(value["records"]) > limits.wire.records:
        raise WireError("record_limit", "/records")
    if len(value["dependencies"]) > limits.wire.external_snapshots:
        raise WireError("dependency_limit", "/dependencies")
    for index, record in enumerate(value["records"]):
        path = f"/records/{index}"
        kind = record.get("kind") if isinstance(record, dict) else None
        if not isinstance(kind, str) or kind not in variants:
            raise WireError("record_kind", path)
        _shared(shared._check_shape, variants[kind], record, path)
    refs = _forms(value, limits.wire)
    records = {record["id"]: record for record in value["records"]}
    _links(value, records, refs, limits.wire)
    _local_semantics(records, limits)


def _encode(value, limit):
    output = bytearray()
    encoder = json.JSONEncoder(sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    for token in encoder.iterencode(value):
        chunk = token.encode("utf-8")
        if len(output) + len(chunk) > limit:
            raise WireError("manifest_limit")
        output.extend(chunk)
    return bytes(output)


def dumps(value, limits=Limits()):
    _shared(check_tree, value, limits.wire.execution_limits())
    _validate(value, limits)
    return _encode(value, limits.wire.snapshot_bytes)


def inspect(source_bytes, limits=Limits()):
    value = _shared(loads, source_bytes, limits.wire.execution_limits())
    _validate(value, limits)
    if _encode(value, limits.wire.snapshot_bytes) != source_bytes:
        raise WireError("noncanonical_bytes")
    return Snapshot(source_bytes, value["snapshot_id"], value["account_id"],
                    sha256(source_bytes).hexdigest())
