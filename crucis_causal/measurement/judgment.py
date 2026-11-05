"""Q01 exact finite judgments and selected S1 answer readers."""

from dataclasses import dataclass
import json

from .calculation import CalculationHold, exact_number


_NATIVE = {"yes", "no", "abstain", "unreported", "unresolved"}
_REFERENCE = {"yes", "no", "indeterminate", "conflicting", "unresolved"}
_DEFINITE = {"yes", "no"}
_DECISION = {"assert": "yes", "deny": "no", "abstain": "abstain",
             "native_unresolved": "unresolved"}


@dataclass(frozen=True, slots=True)
class JudgmentRow:
    key: str
    native: str
    reference: str

    @property
    def eligibility(self):
        if self.native in _DEFINITE and self.reference in _DEFINITE:
            return "eligible"
        if self.native in {"abstain", "unreported"} or self.reference in {"indeterminate", "conflicting"}:
            return "ineligible"
        return "unresolved"


@dataclass(frozen=True, slots=True)
class Judgment:
    rows: tuple[JudgmentRow, ...]

    @property
    def judged(self):
        return tuple(row.key for row in self.rows if row.eligibility == "eligible")

    @property
    def matched(self):
        return sum(row.eligibility == "eligible" and row.native == row.reference
                   for row in self.rows)

    def measure(self, role, budget, deciding_basis):
        total = len(self.rows)
        judged = len(self.judged)
        if role == "judged_count":
            return defined(judged)
        if role == "match_count":
            return defined(self.matched)
        if role in ("judgment_mask", "ledger"):
            rows = self.rows if role == "ledger" else (
                row for row in self.rows if row.eligibility == "eligible")
            def entry(row):
                if role == "judgment_mask":
                    return {"value_kind": "boolean", "value": True}
                fields = {"eligibility": row.eligibility, "native": row.native,
                          "reference": row.reference}
                return {"value_kind": "keyed", "entries": [
                    {"key": key, "value": {"value_kind": "category", "value": value}}
                    for key, value in sorted(fields.items())]}
            return {"tag": "defined", "value": {"value_kind": "keyed", "entries": [
                {"key": row.key, "value": entry(row)} for row in sorted(rows, key=lambda row: row.key)
            ]}}
        if role in ("covered", "full"):
            if role == "full" and judged != total:
                raise CalculationHold("full_scope_unjudged")
            if not judged:
                if any(row.eligibility == "unresolved" for row in self.rows):
                    raise CalculationHold("judgment_eligibility_unresolved")
                return undefined("zero_judged_denominator", deciding_basis)
            return defined(budget.divide(self.matched, judged))
        if role == "captured_coverage":
            numerator = sum(row.native in _DEFINITE for row in self.rows)
        elif role == "reference_coverage":
            numerator = sum(row.reference in _DEFINITE for row in self.rows)
        else:
            raise CalculationHold("unsupported_judgment_role")
        return (defined(budget.divide(numerator, total)) if total
                else undefined("empty_requested_scope", deciding_basis))


def defined(value):
    return {"tag": "defined", "value": exact_number(value)}


def undefined(reason, basis):
    if not basis:
        raise CalculationHold("undefined_basis_required")
    return {"tag": "undefined", "reason": reason, "basis": list(basis)}


def judgment(universe, native, reference):
    """Compare independently sourced dispositions within an exact finite universe."""
    universe = tuple(universe)
    if len(universe) != len(set(universe)) or set(native) != set(universe) or set(reference) != set(universe):
        raise CalculationHold("judgment_scope_mismatch")
    rows = []
    for key in universe:
        a, b = native[key], reference[key]
        if a not in _NATIVE or b not in _REFERENCE:
            raise CalculationHold("judgment_disposition")
        rows.append(JudgmentRow(key, a, b))
    return Judgment(tuple(rows))


def pair_key(a, b):
    if a == b:
        raise CalculationHold("self_pair_outside_profile")
    return json.dumps(sorted((a, b)), ensure_ascii=False, separators=(",", ":"))


def _s1(record, kind):
    if record.contract["name"] != "s1." + kind or record.contract["version"] != "0.1.0-proposal.1":
        raise CalculationHold("s1_reader_contract")
    return record.value["payload"]


def _local(ref, target):
    return ref.get("binding") == "internal" and ref.get("target") == target


def _member(member, domain, keys):
    if not _local(member["domain"], domain) or member["key"] not in keys:
        raise CalculationHold("native_domain_mismatch")
    return member["key"]


def graph_adjacency(output, domain, requested_pairs, capture):
    """Read exact unordered adjacency for a materialized finite S1 graph.

    Capture is the qualified observation role: complete, committed_subset,
    or unavailable. Closure applies only to complete capture within coverage.
    """
    if capture not in ("complete", "committed_subset"):
        raise CalculationHold("interpreted_answer_unavailable")
    if output.package_id != domain.package_id:
        raise CalculationHold("native_domain_mismatch")
    payload, space = _s1(output, "output"), _s1(domain, "domain")
    if payload["output_type"] != "graph" or space["domain_kind"] != "finite":
        raise CalculationHold("graph_reader_contract")
    body = payload["body"]
    if (body["family"]["name"] not in {"s1.dag", "s1.directed_graph"}
            or body["family"]["version"] != domain.contract["version"]
            or not _local(body["domain"], domain.record_id)):
        raise CalculationHold("graph_reader_contract")
    keys = {item["key"] for item in space["members"]}
    coverage = body["coverage"]
    if (coverage["pairing"] != "unordered" or coverage["include_same_node"]
            or not _local(coverage["domain"], domain.record_id)
            or coverage["extent"] not in ("all_in_domain", "listed_only")):
        raise CalculationHold("graph_coverage_contract")

    def read_pair(item):
        return pair_key(_member(item["left"], domain.record_id, keys),
                        _member(item["right"], domain.record_id, keys))

    listed = {read_pair(item) for item in coverage["pairs"]}
    positives = set()
    for link in body["links"]:
        if (link["relation"]["name"] != "s1.direct_relation"
                or link["relation"]["version"] != domain.contract["version"]):
            raise CalculationHold("graph_link_contract")
        key = read_pair(link)
        if coverage["extent"] == "listed_only" and key not in listed:
            raise CalculationHold("graph_link_outside_coverage")
        positives.add(key)
    closed = body["omission"]["within_coverage"] == "asserted_absence"
    result = {}
    for a, b in requested_pairs:
        key = pair_key(a, b)
        if a not in keys or b not in keys or key in result:
            raise CalculationHold("requested_pair_scope")
        in_scope = coverage["extent"] == "all_in_domain" or key in listed
        if key in positives:
            result[key] = "yes"
        elif capture == "committed_subset" or not in_scope:
            result[key] = "unresolved"
        else:
            result[key] = "no" if closed else "unreported"
    return result


def local_parents(output, domain, propositions, target, candidates, capture, *, query=None):
    if capture not in ("complete", "committed_subset"):
        raise CalculationHold("interpreted_answer_unavailable")
    if output.package_id != domain.package_id:
        raise CalculationHold("native_domain_mismatch")
    payload, space = _s1(output, "output"), _s1(domain, "domain")
    candidates = tuple(candidates)
    keys = {item["key"] for item in space["members"]}
    if (space["domain_kind"] != "finite" or target not in keys or target in candidates
            or len(candidates) != len(set(candidates)) or not set(candidates) <= keys):
        raise CalculationHold("local_candidate_scope")
    body = payload["body"]
    if payload["output_type"] == "abstention":
        if capture != "complete" or query is None or not _local(body["query"], query.record_id):
            raise CalculationHold("abstention_scope_unestablished")
        return dict.fromkeys(candidates, "abstain")
    if payload["output_type"] != "claims" or body["omission"] not in ("s1.unreported", "s1.no_assertion"):
        raise CalculationHold("local_reader_contract")
    props = {prop.record_id: prop for prop in propositions}
    declared = any(_local(ref, domain.record_id) for ref in body["coverage"]["subjects"])
    omitted = "unreported" if declared and capture == "complete" else "unresolved"
    result = dict.fromkeys(candidates, omitted)
    seen = set()
    for decision in body["decisions"]:
        ref = decision["proposition"]
        prop = props.get(ref["target"])
        if prop is None or prop.package_id != domain.package_id or not _local(ref, prop.record_id):
            raise CalculationHold("local_proposition_unresolved")
        spec = _s1(prop, "proposition")
        args = {item["role"]: item["value"] for item in spec["arguments"]}
        if (spec["predicate"] != {"name": "s1.direct_relation", "version": domain.contract["version"]}
                or spec["conditioning"] or set(args) != {"s1.cause", "s1.effect"}
                or len(spec["arguments"]) != 2):
            raise CalculationHold("local_predicate_mismatch")
        cause = _member(args["s1.cause"], domain.record_id, keys)
        effect = _member(args["s1.effect"], domain.record_id, keys)
        if cause not in result or cause in seen or effect != target:
            raise CalculationHold("local_proposition_scope")
        seen.add(cause)
        result[cause] = _DECISION[decision["decision"]]
    return result


def evaluate_judgment(prepared, budget):
    """Q01 adapter over explicit selected S1 sources and scoped S4 label evidence."""
    from .procedure_inputs import category, deciding_basis, keyed, many, one, value

    universe = prepared.scope.value["payload"].get("universe")
    if universe is None:
        raise CalculationHold("judgment_scope_unestablished")
    native = one(prepared, "native", "s1.output")
    domain = one(prepared, "domain", "s1.domain")
    capture = category(prepared, "capture")
    answer_kind = native.value["payload"]["output_type"]
    if answer_kind == "graph":
        try:
            pairs = [json.loads(key) for key in universe]
            if any(not isinstance(row, list) or len(row) != 2
                   or any(not isinstance(member, str) for member in row) for row in pairs):
                raise ValueError()
            if [pair_key(*row) for row in pairs] != universe:
                raise ValueError()
        except (ValueError, TypeError) as exc:
            raise CalculationHold("requested_pair_scope") from exc
        dispositions = graph_adjacency(native, domain, pairs, capture)
    else:
        target = one(prepared, "target", "s4.source").value["payload"]["subject"]
        queries = many(prepared, "query")
        if len(queries) > 1:
            raise CalculationHold("local_query_ambiguous")
        dispositions = local_parents(native, domain, many(prepared, "propositions"), target,
                                     universe, capture, query=queries[0] if queries else None)
    if prepared.output_role == "captured_coverage" and not many(prepared, "reference"):
        labels = dict.fromkeys(universe, "unresolved")
    else:
        labels = {}
        for key, label in keyed(value(prepared, "reference")).items():
            if label.get("value_kind") != "category":
                raise CalculationHold("reference_label_contract")
            labels[key] = label["value"]
    return judgment(universe, dispositions, labels).measure(
        prepared.output_role, budget, deciding_basis(prepared, "capture"),
    )
