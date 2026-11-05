"""Exact S4 wire validation. Decoding never resolves or fetches external evidence."""

from collections import deque
from dataclasses import dataclass, fields
from functools import lru_cache
from hashlib import sha256
import json
from math import gcd
from pathlib import Path

from jsonschema import Draft202012Validator

from crucis_causal.execution import codec as execution_codec
from crucis_causal.execution.api import Limits as ExecutionLimits
from crucis_causal.execution.model import ExecutionError, canonical, walk

FORMAT = "s4.measurement_package"
VERSION = "0.1.0-proposal.1"


class WireError(ValueError):
    """A scoped wire or integrity failure."""

    def __init__(self, code, path=""):
        self.code = "s4." + code.removeprefix("s4.")
        self.path = path
        super().__init__(f"{self.code}: {path}" if path else self.code)


_CAPS = {
    "snapshot_bytes": 524288,
    "depth": 48,
    "records": 4096,
    "collection_items": 8192,
    "scalar_bytes": 32768,
    "reference_nodes": 32768,
    "reference_visits": 131072,
    "external_snapshots": 64,
    "dependency_depth": 16,
    "closure_bytes": 33554432,
    "integer_digits": 256,
    "intermediate_digits": 4096,
    "rational_operations": 250000,
}


@dataclass(frozen=True, slots=True)
class Limits:
    """Review-version policy caps. A caller may supply stricter positive limits."""

    snapshot_bytes: int = _CAPS["snapshot_bytes"]
    depth: int = _CAPS["depth"]
    records: int = _CAPS["records"]
    collection_items: int = _CAPS["collection_items"]
    scalar_bytes: int = _CAPS["scalar_bytes"]
    reference_nodes: int = _CAPS["reference_nodes"]
    reference_visits: int = _CAPS["reference_visits"]
    external_snapshots: int = _CAPS["external_snapshots"]
    dependency_depth: int = _CAPS["dependency_depth"]
    closure_bytes: int = _CAPS["closure_bytes"]
    integer_digits: int = _CAPS["integer_digits"]
    intermediate_digits: int = _CAPS["intermediate_digits"]
    rational_operations: int = _CAPS["rational_operations"]

    def __post_init__(self):
        for field in fields(self):
            value = getattr(self, field.name)
            if type(value) is not int or not 0 < value <= _CAPS[field.name]:
                raise WireError("invalid_limit", field.name)

    def execution_limits(self):
        return ExecutionLimits(
            max_manifest_bytes=str(self.snapshot_bytes),
            max_depth=str(self.depth),
            max_records=str(self.records),
            max_collection_items=str(self.collection_items),
            max_total_reference_nodes=str(self.reference_nodes),
            max_scalar_utf8_bytes=str(self.scalar_bytes),
            max_external_packages=str(self.external_snapshots),
            max_external_bytes=str(self.closure_bytes),
            max_reference_depth=str(self.dependency_depth),
        )


@dataclass(frozen=True, slots=True)
class Snapshot:
    """The original, validated canonical bytes and their byte identity."""

    source_bytes: bytes
    snapshot_id: str
    account_id: str
    digest: str

    @property
    def package(self):
        # Return an owned view. Mutating it cannot change the frozen bytes.
        return json.loads(self.source_bytes)


@lru_cache(maxsize=1)
def _validators():
    schema = json.loads(Path(__file__).with_name("wire.schema.json").read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    # Dispatch by exact kind. A malformed record need not traverse all branches.
    record_schemas = schema["$defs"]["record"]["oneOf"]
    envelope = {
        **schema,
        "properties": {**schema["properties"], "records": {"type": "array", "minItems": 1}},
    }
    records = {
        shape["properties"]["kind"]["const"]: Draft202012Validator(
            {"$defs": schema["$defs"], **shape}
        )
        for shape in record_schemas
    }
    reference = Draft202012Validator({"$defs": schema["$defs"], "$ref": "#/$defs/reference"})
    return Draft202012Validator(envelope), records, reference


def _check_shape(validator, value, path=""):
    error = next(validator.iter_errors(value), None)
    if error is not None:
        trail = "".join("/" + str(key).replace("~", "~0").replace("/", "~1")
                        for key in error.absolute_path)
        raise WireError("shape", path + trail)


def _check_tree(value, limits):
    try:
        execution_codec.check_tree(value, limits.execution_limits())
    except ExecutionError as exc:
        raise WireError(exc.code.removeprefix("s3."), exc.path) from exc


def _check_keys(items, key, path):
    keys = [item[key] for item in items]
    if len(keys) != len(set(keys)):
        raise WireError("duplicate_key", path)
    if keys != sorted(keys):
        raise WireError("noncanonical_key_order", path)


def _check_set(items, path):
    encoded = [canonical(item) for item in items]
    if len(encoded) != len(set(encoded)):
        raise WireError("duplicate_set_member", path)
    if encoded != sorted(encoded):
        raise WireError("noncanonical_set_order", path)


def _check_decimal(text, limits, path):
    digits = text.removeprefix("-")
    if not digits.isascii() or not digits.isdecimal():
        raise WireError("invalid_decimal", path)
    if len(digits) > limits.integer_digits:
        raise WireError("integer_digit_limit", path)
    return int(text)


def _fraction(value, limits, path):
    n = _check_decimal(value["numerator"], limits, path + "/numerator")
    d = _check_decimal(value["denominator"], limits, path + "/denominator")
    if d <= 0 or gcd(abs(n), d) != 1:
        raise WireError("noncanonical_rational", path)
    return n, d


def _member_keys(record):
    kind, payload = record["kind"], record["payload"]
    if kind == "s4.ledger":
        return {row["key"] for row in payload["entries"]}
    if kind == "s4.population":
        return {row["key"] for row in payload["slots"]}
    if kind == "s4.request":
        return {row["key"] for row in payload["goals"]}
    if kind == "s4.result" and payload["outcome"]["tag"] == "defined":
        value = payload["outcome"]["value"]
        if value.get("value_kind") == "keyed":
            return {row["key"] for row in value["entries"]}
    return set()


def _emission_identity(emission):
    return canonical(emission["binding"]), emission["output_role"], emission["subject_key"]


def _validate_selector(ref, target, path, selector_targets):
    selector = ref.get("selector")
    if selector is None:
        return
    kind = selector["selector_kind"]
    if kind == "member":
        members = selector_targets.get(target["id"])
        if members is None:
            members = _member_keys(target)
            selector_targets[target["id"]] = members
        if selector["key"] not in members:
            raise WireError("selector_target", path)
    elif kind == "output" and target["kind"] == "s4.calculation":
        cache_key = (target["id"], "output")
        outputs = selector_targets.get(cache_key)
        if outputs is None:
            outputs = {
                (item["binding"]["target_id"], item["output_role"], item["subject_key"])
                for item in target["payload"]["emissions"]
                if item["binding"]["ref_kind"] == "local"
            }
            selector_targets[cache_key] = outputs
        if (selector["binding_id"], selector["role"], selector["subject_key"]) not in outputs:
            raise WireError("selector_target", path)
    else:
        raise WireError("selector_target", path)


_SET_FIELDS = {
    "sources", "relations", "observations", "basis", "support", "against",
    "gaps", "qualifications", "requirements", "profiles", "universe", "mask",
}
_KEYED_FIELDS = {
    "frontier", "records", "dependencies", "slots", "target_slots", "subject_slots",
    "output_roles", "goals", "subjects", "premises", "outputs", "planned", "emissions",
    "entries",
}


def _validate_forms(package, limits):
    references = []
    for path, item, _ in walk(package):
        if isinstance(item, list):
            field = path.rsplit("/", 1)[-1]
            if field in _SET_FIELDS or field == "dependencies" and path != "/dependencies":
                _check_set(item, path)
            if field in _KEYED_FIELDS and (field != "dependencies" or path == "/dependencies"):
                _check_keys(item, "id" if field == "records" else "key", path)
        if not isinstance(item, dict):
            continue
        if "ref_kind" in item:
            references.append((path, item))
            if len(references) > limits.reference_nodes:
                raise WireError("reference_count_limit", path)
        if item.get("number_kind") == "int":
            _check_decimal(item["text"], limits, path + "/text")
        elif item.get("number_kind") == "rational":
            _fraction(item, limits, path)
        if item.get("value_kind") in ("outer_interval", "slot_range"):
            a, b = _fraction(item["lower"], limits, path + "/lower")
            c, d = _fraction(item["upper"], limits, path + "/upper")
            if a * d > c * b:
                raise WireError("reversed_interval", path)
        if {"start", "end_exclusive"} <= item.keys():
            start = _check_decimal(item["start"], limits, path + "/start")
            end = _check_decimal(item["end_exclusive"], limits, path + "/end_exclusive")
            if start > end:
                raise WireError("reversed_byte_range", path)
        if item.get("algorithm") == "sha256":
            length = _check_decimal(item["length"], limits, path + "/length")
            extent = item["extent"]
            if extent["extent_kind"] == "byte_range":
                a = _check_decimal(extent["start"], limits, path + "/extent/start")
                b = _check_decimal(extent["end_exclusive"], limits, path + "/extent/end_exclusive")
                if length != b - a:
                    raise WireError("extent_length_mismatch", path)
        if {"minimum", "maximum", "collection"} <= item.keys():
            minimum = _check_decimal(item["minimum"], limits, path + "/minimum")
            maximum = _check_decimal(item["maximum"], limits, path + "/maximum")
            if maximum < minimum or (item["collection"] == "single" and maximum != 1):
                raise WireError("slot_cardinality", path)
    return references


def _validate_calculation(record, path):
    payload = record["payload"]
    planned = {item["key"]: _emission_identity(item) for item in payload["planned"]}
    if len(set(planned.values())) != len(planned):
        raise WireError("duplicate_planned_output", path)
    for item in payload["emissions"]:
        if planned.get(item["key"]) != _emission_identity(item):
            raise WireError("unplanned_emission", path + "/emissions")
    if payload["extent"] in ("unexamined", "unavailable", "known_empty") and payload["emissions"]:
        raise WireError("emission_extent", path + "/emissions")


def _validate_output_links(records):
    emissions = {
        (record["id"], entry["key"]): entry
        for record in records.values()
        if record["kind"] == "s4.calculation"
        for entry in record["payload"]["emissions"]
    }
    for record in records.values():
        if record["kind"] != "s4.result":
            continue
        payload = record["payload"]
        origin = payload["origin"]
        if origin["origin_kind"] != "computed":
            continue
        calc = origin["calculation"]
        if calc["expected_contract"]["name"] != "s4.calculation" or "selector" in calc:
            raise WireError("calculation_origin_contract", record["id"])
        if calc["ref_kind"] == "local":
            entry = emissions.get((calc["target_id"], origin["emission_key"]))
            if (entry is None or _emission_identity(entry) != _emission_identity(payload)
                    or entry["result"]["ref_kind"] != "local"
                    or entry["result"]["target_id"] != record["id"]
                    or "selector" in entry["result"]):
                raise WireError("calculation_origin_mismatch", record["id"])
    for (calculation_id, key), entry in emissions.items():
        target = entry["result"]
        if target["expected_contract"]["name"] != "s4.result" or "selector" in target:
            raise WireError("emitted_result_contract", "/records")
        if target["ref_kind"] == "local":
            origin = records[target["target_id"]]["payload"]["origin"]
            if (origin["origin_kind"] != "computed" or origin["emission_key"] != key
                    or origin["calculation"]["ref_kind"] != "local"
                    or origin["calculation"]["target_id"] != calculation_id):
                raise WireError("calculation_origin_mismatch", target["target_id"])


def _verify_proof_dag(edges):
    indegree = {key: 0 for key in edges}
    for targets in edges.values():
        for target in targets:
            indegree[target] += 1
    ready = deque(key for key, degree in indegree.items() if degree == 0)
    visited = 0
    while ready:
        key = ready.popleft()
        visited += 1
        for target in edges[key]:
            indegree[target] -= 1
            if indegree[target] == 0:
                ready.append(target)
    if visited != len(edges):
        raise WireError("proof_cycle", "/records")


def _navigation(owner, tail):
    return (
        owner["kind"] == "s4.calculation" and tail.startswith("payload/emissions/")
        and tail.endswith("/result")
    ) or (
        owner["kind"] == "s4.relation" and tail in ("payload/source", "payload/target")
    )


def _validate_links(package, records, references, limits):
    externals = {row["key"]: row for row in package["dependencies"]}
    identities = [row["package_id"] for row in externals.values()]
    if package["snapshot_id"] in identities or len(identities) != len(set(identities)):
        raise WireError("duplicate_or_self_dependency", "/dependencies")
    edges = {record_id: set() for record_id in records}
    selector_targets = {}
    for visit, (path, ref) in enumerate(references, 1):
        if visit > limits.reference_visits:
            raise WireError("reference_visit_limit", path)
        kind = ref["ref_kind"]
        if kind == "artifact":
            if ref["artifact_record"]["expected_contract"]["name"] != "s1.artifact_snapshot":
                raise WireError("artifact_target_contract", path)
            if "selector" in ref["artifact_record"]:
                raise WireError("artifact_record_selector", path)
            selector = ref.get("selector")
            if selector is not None and selector["selector_kind"] == "byte_range":
                content = ref["content_pin"]
                extent = content["extent"]
                first = int(extent.get("start", "0"))
                end = int(extent.get("end_exclusive", content["length"]))
                if not first <= int(selector["start"]) <= int(selector["end_exclusive"]) <= end:
                    raise WireError("artifact_selector_extent", path)
            continue
        if kind == "external":
            if ref["dependency_key"] not in externals:
                raise WireError("undeclared_dependency", path)
            continue
        record = records.get(ref["target_id"])
        if record is None or record["contract"] != ref["expected_contract"]:
            raise WireError("reference_target", path)
        _validate_selector(ref, record, path, selector_targets)
        if path.startswith("/records/"):
            _, _, index, tail = path.split("/", 3)
            owner = package["records"][int(index)]
            if not _navigation(owner, tail):
                edges[owner["id"]].add(record["id"])
    _verify_proof_dag(edges)
    root = package["roots"][0]
    if root["expected_contract"]["name"] != "s4.account" or "selector" in root:
        raise WireError("account_root_required", "/roots/0")
    if package["audience"]["expected_contract"]["name"] != "s3.audience":
        raise WireError("audience_contract", "/audience")


def _validate(package, limits):
    _check_tree(package, limits)
    envelope, variants, _ = _validators()
    _check_shape(envelope, package)
    if len(package["records"]) > limits.records:
        raise WireError("record_limit", "/records")
    if len(package["dependencies"]) > limits.external_snapshots:
        raise WireError("dependency_limit", "/dependencies")
    for i, record in enumerate(package["records"]):
        path = f"/records/{i}"
        kind = record.get("kind") if isinstance(record, dict) else None
        if not isinstance(kind, str) or kind not in variants:
            raise WireError("record_kind", path)
        _check_shape(variants[kind], record, path)
        if kind == "s4.calculation":
            _validate_calculation(record, path + "/payload")
    refs = _validate_forms(package, limits)
    records = {r["id"]: r for r in package["records"]}
    _validate_links(package, records, refs, limits)
    _validate_output_links(records)


def check_reference(ref, limits):
    """Validate one caller-supplied reference before interpreting its fields."""
    _check_tree(ref, limits)
    _check_shape(_validators()[2], ref)
    _validate_forms(ref, limits)


def dumps(package, limits=Limits()):
    """Encode a structurally valid package in its canonical representation."""
    _check_tree(package, limits)
    encoder = json.JSONEncoder(sort_keys=True, ensure_ascii=False, separators=(",", ":"),
                               allow_nan=False)
    data = bytearray()
    for token in encoder.iterencode(package):
        chunk = token.encode("utf-8")
        if len(data) + len(chunk) > limits.snapshot_bytes:
            raise WireError("manifest_limit")
        data.extend(chunk)
    _validate(package, limits)
    return bytes(data)


def inspect(data, limits=Limits()):
    """Inspect exact immutable bytes without resolving external dependencies."""
    try:
        package = execution_codec.loads(data, limits.execution_limits())
    except ExecutionError as exc:
        raise WireError(exc.code.removeprefix("s3."), exc.path) from exc
    _validate(package, limits)
    if canonical(package) != data:
        raise WireError("noncanonical_bytes")
    return Snapshot(data, package["snapshot_id"], package["account_id"], sha256(data).hexdigest())
