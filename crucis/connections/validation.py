"""Scoped wire/reference validation, never scientific truth; DLV-08, DLV-09."""
import base64
import datetime
import re
from dataclasses import asdict, dataclass, field
from decimal import Decimal, InvalidOperation

from .codec import WireError, dumps
from .model import VERSION
from .schema import _schema


@dataclass(frozen=True)
class Issue:
    code: str
    path: str
    message: str
    subject: str = ""


@dataclass(frozen=True)
class Check:
    subject: str
    contract: str
    result: str
    details: str = ""


@dataclass
class ValidationReport:
    issues: list = field(default_factory=list)
    withheld: list = field(default_factory=list)
    checks: list = field(default_factory=list)

    @property
    def structural_ok(self):
        return not any(i.code.startswith(("s1.schema", "s1.encoding")) for i in self.issues)

    @property
    def reference_ok(self):
        return self.structural_ok and not any(i.code.startswith("s1.reference") for i in self.issues)

    @property
    def ok(self):
        """Wire/reference conformance only; inspect named checks for stronger guarantees."""
        return not self.issues

    def to_json(self):
        return {"wire_reference_ok": self.ok, "structural_ok": self.structural_ok,
                "reference_ok": self.reference_ok, "issues": [asdict(i) for i in self.issues],
                "withheld": [asdict(i) for i in self.withheld], "checks": [asdict(c) for c in self.checks],
                "scientific_correctness": "not_assessed"}

    def require(self, contracts=(), subjects=()):
        if not self.ok:
            raise WireError("; ".join(i.path + ": " + i.message for i in self.issues[:8]))
        for name in contracts:
            matching = [c for c in self.checks if c.contract == name and (not subjects or c.subject in subjects)]
            if not matching or any(c.result != "pass" for c in matching):
                raise WireError("required conformance not established: " + name)
        return self


def walk(value, path=""):
    yield path, value
    if isinstance(value, dict):
        for key, child in value.items():
            yield from walk(child, path + "/" + str(key).replace("~", "~0").replace("/", "~1"))
    elif isinstance(value, list):
        for i, child in enumerate(value):
            yield from walk(child, path + "/" + str(i))


def content_bytes(content, resolver=None):
    kind = content["content_form"]
    if kind == "inline_utf8":
        return content["text"].encode("utf-8", errors="strict")
    if kind == "inline_base64":
        raw = base64.b64decode(content["data"], validate=True)
        if base64.b64encode(raw).decode("ascii") != content["data"]:
            raise WireError("noncanonical padded base64")
        return raw
    if resolver is None:
        raise FileNotFoundError("external snapshot requires an explicit resolver")
    return resolver(content)


def decimal_value(value):
    if value["number_type"] == "nonfinite":
        return Decimal({"nan":"NaN", "positive_infinity":"Infinity", "negative_infinity":"-Infinity"}[value["value"]])
    return Decimal(value["text"])


def validate_wire(package):
    report = ValidationReport()
    try:
        dumps(package)  # catches invalid Unicode, non-string keys and nonstandard nonfinite values
    except (WireError, RecursionError) as exc:
        report.issues.append(Issue("s1.encoding", "", str(exc)))
        return report
    try:
        from jsonschema import Draft202012Validator
    except ImportError as exc:
        raise RuntimeError("SC-1 validation requires jsonschema==4.25.1; see connections/requirements.txt") from exc
    validator = Draft202012Validator(_schema())
    for error in validator.iter_errors(package):
        path = "/" + "/".join(str(k) for k in error.absolute_path)
        message = error.message
        if len(message) > 400:
            message = message[:400] + "..."
        report.issues.append(Issue("s1.schema", path, message))
    if not report.structural_ok:
        return report
    records = {}
    for i, record in enumerate(package["records"]):
        if record["id"] in records:
            report.issues.append(Issue("s1.reference_duplicate", "/records/" + str(i), "duplicate record ID", record["id"]))
        records[record["id"]] = record
    external = {p["package_id"] for p in package["external_packages"]}
    if len(external) != len(package["external_packages"]) or package["package_id"] in external:
        report.issues.append(Issue("s1.reference_package", "/external_packages", "duplicate/self external package identity"))
    for path, item in walk(package):
        if not isinstance(item, dict):
            continue
        if item.get("binding") == "internal":
            target = records.get(item["target"])
            if target is None or target["record_type"] != item["target_type"]:
                report.issues.append(Issue("s1.reference_target", path, "missing target or wrong record type", item["target"]))
        elif item.get("binding") == "external" and item["package_id"] not in external:
            report.issues.append(Issue("s1.reference_external", path, "external package is not declared"))
        if item.get("state") == "unresolved" or item.get("binding") == "unresolved":
            report.withheld.append(Issue("s1.unresolved", path, "source knowledge/association remains unresolved"))
        if "critical_for" in item and "contract" in item:
            # Extensions are evidence, not trusted code. Exact readers must be
            # registered explicitly; no URI retrieval or guessed compatibility.
            for guarantee in item["critical_for"]:
                report.checks.append(Check(package["package_id"], guarantee, "unknown",
                                           "extension reader not registered: " + item["contract"]["name"]))
                report.withheld.append(Issue("s1.unsupported_semantics", path,
                                             "unknown required extension withholds " + guarantee))
        try:
            if item.get("content_form") in ("inline_base64", "inline_utf8"):
                content_bytes(item)
            if item.get("number_type") == "finite_decimal" and not decimal_value(item).is_finite():
                raise ValueError("finite decimal is not finite")
            if item.get("kind") == "byte_range" and int(item["end_exclusive"]) < int(item["start"]):
                raise ValueError("byte-range end precedes start")
            if item.get("time_type") == "utc_instant":
                pattern = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:[0-5]\d" + (r"\.\d+Z" if item["precision"] == "fractional_second" else "Z")
                if not re.fullmatch(pattern, item["value"]):
                    raise ValueError("UTC timestamp/precision mismatch")
                datetime.datetime.fromisoformat(item["value"].replace("Z", "+00:00"))
            if item.get("selector_type") == "json_pointer":
                pointer = item["pointer"]
                if pointer and (not pointer.startswith("/") or re.search(r"~(?![01])", pointer)):
                    raise ValueError("invalid JSON pointer")
        except (ValueError, TypeError, UnicodeError, InvalidOperation) as exc:
            report.issues.append(Issue("s1.encoding_value", path, str(exc)))
    report.checks.append(Check(package["package_id"], "s1.wire_references", "pass" if report.ok else "fail"))
    return report
