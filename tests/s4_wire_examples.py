"""Symbolic wire-only examples for the approved S4 case reviews."""

from copy import deepcopy
import json


VERSION = "0.1.0-proposal.1"


def contract(name, version=VERSION):
    return {"name": name, "version": version}


def local(target, kind):
    return {"ref_kind": "local", "target_id": target,
            "expected_contract": contract("s4." + kind)}


def external(dependency, target, kind, version):
    return {"ref_kind": "external", "dependency_key": dependency,
            "target_id": target, "expected_contract": contract(kind, version)}


def pin(digest, length):
    return {"algorithm": "sha256", "digest": digest, "length": str(length),
            "extent": {"extent_kind": "whole"}}


AUDIENCE = external("execution", "audience", "s3.audience", "0.1.0-proposal.3")
OBSERVER = external("source", "observer", "s1.component", VERSION)
RAW = external("source", "original", "s1.artifact_snapshot", VERSION)
ARTIFACT = {"ref_kind": "artifact", "artifact_record": RAW,
            "content_pin": pin("c" * 64, 12)}
FRONTIER = [{"key": "native-output", "position": RAW}]


def integer(value):
    return {"number_kind": "int", "text": str(value)}


def rational(numerator, denominator):
    return {"number_kind": "rational", "numerator": str(numerator),
            "denominator": str(denominator)}


def category(value):
    return {"value_kind": "category", "value": value}


def keyed(**values):
    return {"value_kind": "keyed",
            "entries": [{"key": key, "value": values[key]} for key in sorted(values)]}


def gap(reason):
    return {"tag": "unresolved", "reason": reason, "basis": []}


def defined(value):
    return {"tag": "defined", "value": value}


class Example:
    def __init__(self, name, narrative):
        self.name = name
        self.records = {}
        self.source = self.add("src", "source", {
            "subject": name, "attribution": OBSERVER, "extent": "complete",
            "observations": [], "basis": [RAW], "verbatim": narrative,
        })
        self.root = self.add("acct", "account", {"observer": OBSERVER, "sources": [self.source]})

    def add(self, ident, kind, payload):
        assert ident not in self.records
        self.records[ident] = {
            "id": ident, "kind": "s4." + kind, "contract": contract("s4." + kind),
            "payload": payload,
        }
        return local(ident, kind)

    def scope(self, ident, kind="subject", **details):
        return self.add("scope." + ident, "scope", {
            "scope_kind": kind, "subject": self.source, "quantity": contract("fixture." + ident),
            "units": contract("fixture.dimensionless"), "basis": [self.source], **details,
        })

    def premise(self, ident, scope, determination="supported", stage="preflight"):
        requirement = self.add("req." + ident, "requirement", {
            "condition": contract("fixture." + ident), "rule": contract("fixture.assess"),
            "stage": stage, "subject_slots": [{"key": "subject", "role_class": "evidence",
                "contract": contract("s4.source"), "minimum": "1", "maximum": "1",
                "collection": "single"}],
        })
        basis = [self.source] if determination == "supported" else []
        assessment = self.add("prem." + ident, "premise_assessment", {
            "requirement": requirement, "subjects": [{"key": "subject", "values": [self.source]}],
            "scope": scope, "frontier": FRONTIER, "rule": contract("fixture.assess"),
            "audience": AUDIENCE, "determination": determination, "support": basis,
            "against": [], "gaps": [gap(ident)] if determination == "unresolved" else [],
        })
        return {"key": ident, "assessment": assessment}

    def job(self, ident, procedure, scope, outcomes, *, holds=None, premises=(), profile="p2"):
        roles = sorted(set(outcomes) | set(holds or {}))
        role_specs = [{"key": role, "value_contract": contract("fixture." + role),
                       "requirements": []} for role in roles]
        definition = self.add("def." + ident, "question_definition", {
            "target": contract("fixture." + ident), "slots": [], "output_roles": role_specs,
        })
        question = self.add("q." + ident, "question_instance", {
            "definition": definition, "target_slots": [],
        })
        binding = self.add("bind." + ident, "binding", {
            "question": question, "slots": [], "selection": self.source, "frontier": FRONTIER,
        })
        request = self.add("intent." + ident, "request", {"goals": [
            {"key": role, "question": question, "output_role": role, "scope": scope,
             "profiles": [profile], "binding": binding} for role in roles
        ]})
        for role, reason in (holds or {}).items():
            self.add(f"held.{ident}.{role}", "goal_assessment", {
                "goal": {"request": request, "goal_key": role}, "scope": scope,
                "premises": list(premises), "binding": binding,
                "outcome": {"tag": "held", "reason": reason, "basis": [self.source]},
            })
        if not outcomes:
            return None, {}
        proc = self.add("proc." + ident, "procedure", {
            "definition": contract(procedure), "implementation": ARTIFACT,
            "configuration": self.source, "dependencies": [], "slots": [],
            "output_roles": role_specs,
        })
        planned = [{"key": role, "binding": binding, "output_role": role,
                    "subject_key": ident, "scope": scope} for role in sorted(outcomes)]
        plan = self.add("plan." + ident, "plan", {
            "goal": {"request": request, "goal_key": sorted(outcomes)[0]}, "procedure": proc,
            "outputs": planned, "premises": list(premises), "basis": [self.source],
            "limits": self.source,
        })
        calc = local("calc." + ident, "calculation")
        emissions, results = [], {}
        for item in planned:
            role = item["key"]
            results[role] = self.add(f"val.{ident}.{role}", "result", {
                "binding": binding, "output_role": role, "subject_key": ident,
                "scope": scope, "origin": {"origin_kind": "computed",
                    "calculation": calc, "emission_key": role},
                "premises": list(premises), "outcome": outcomes[role],
            })
            emissions.append({k: v for k, v in item.items() if k != "scope"} |
                             {"result": results[role]})
        self.add(calc["target_id"], "calculation", {
            "invocation_id": "run." + ident, "plan": plan, "procedure": proc,
            "basis": [self.source], "work_state": "completed", "extent": "complete",
            "planned": planned, "emissions": emissions, "observations": [self.source],
        })
        return calc, results

    def package(self):
        return deepcopy({
            "format": contract("s4.measurement_package"), "account_id": "account." + self.name,
            "snapshot_id": "snapshot." + self.name, "audience": AUDIENCE, "frontier": FRONTIER,
            "roots": [self.root], "records": [self.records[key] for key in sorted(self.records)],
            "dependencies": [
                {"key": "execution", "format": contract("s3.account_package", "0.1.0-proposal.3"),
                 "package_id": "synthetic-execution", "pin": pin("a" * 64, 20)},
                {"key": "source", "format": contract("s1.connection_package"),
                 "package_id": "synthetic-source", "pin": pin("b" * 64, 24)},
            ],
        })


def graph_example(name="graph"):
    ex = Example(name, "Closed unordered adjacency AB yes, BC no, AC yes. "
                       "Benchmark AB yes, BC no, AC undetermined.")
    scope = ex.scope("covered", "judgment", universe=["AB", "AC", "BC"],
                     mask=["AB", "BC"], numerator=integer(2), denominator=integer(2))
    closure = ex.premise("closure", scope)
    calc, roles = ex.job("graph", "s4.q01", scope, {
        "covered": defined(rational(1, 1)), "judged_count": defined(integer(2)),
    }, premises=[closure])
    full_scope = ex.scope("full", "judgment", universe=["AB", "AC", "BC"],
                          mask=["AB", "BC"])
    missing = ex.premise("missing_label", full_scope, "unresolved")
    ex.job("full", "s4.q01", full_scope, {}, holds={"agreement": "missing_label"},
           premises=[missing])
    return ex, calc, roles["covered"]


def local_example():
    ex = Example("local", "Parent membership for A,B,C relative to Z. "
                         "One complete scoped abstention and a separately missing capture.")
    empty = ex.scope("empty", "judgment", universe=["A", "B", "C"], mask=[],
                     numerator=integer(0), denominator=integer(0))
    coverage = ex.scope("coverage", "judgment", universe=["A", "B", "C"], mask=[],
                        numerator=integer(0), denominator=integer(3))
    ex.job("coverage", "s4.q01", coverage, {"coverage": defined(rational(0, 1))})
    ex.job("ratio", "s4.q01", empty, {"agreement": {
        "tag": "undefined", "reason": "zero_judged_denominator", "basis": [ex.source],
    }})
    ex.job("missing", "s4.q01", empty, {}, holds={"agreement": "required_answer_unavailable"})
    return ex.package()


def paired_example():
    ex = Example("paired", "Frame K1/K2 and arms A/B. K1 scores 4/5 and 1/2; "
                          "K2/A unresolved delivery; K2/B established no qualifying delivery.")
    frame = ex.scope("utility", "frame", functional=contract("fixture.equal_case_a_minus_b"))
    arms = [ex.scope("arm-a"), ex.scope("arm-b")]
    slots = []
    for case in ("k1", "k2"):
        case_scope = ex.scope(case)
        for letter, arm in zip(("a", "b"), arms):
            name = case + "-" + letter
            slot_scope = ex.scope(name)
            lower, upper = {
                "k1-a": (rational(4, 5), rational(4, 5)),
                "k1-b": (rational(1, 2), rational(1, 2)),
                "k2-a": (rational(0, 1), rational(1, 1)),
                "k2-b": (rational(0, 1), rational(0, 1)),
            }[name]
            slot_range = ex.add("range." + name, "result", {
                "binding": local("bind.bound", "binding"), "output_role": "slot_range",
                "subject_key": name, "scope": slot_scope,
                "origin": {"origin_kind": "reported", "source": ex.source},
                "premises": [], "outcome": defined({
                    "value_kind": "slot_range", "lower": lower, "upper": upper,
                }),
            })
            slots.append({"key": name, "case": case_scope, "arm": arm,
                          "slot": slot_scope, "outcome": ex.source if case == "k1"
                          else gap("capture_gap" if letter == "a" else "no_answer"),
                          "range": slot_range})
    ex.add("pop", "population", {"frame": frame, "functional": contract("fixture.equal_case"),
                                 "arms": arms, "slots": slots})
    ex.job("point", "s4.q04", frame, {}, holds={"point": "missing_comparable_pair"}, profile="p3")
    ex.job("bound", "s4.q05", frame, {"outer_bound": defined({
        "value_kind": "outer_interval", "lower": rational(3, 20), "upper": rational(13, 20),
    })}, profile="p3")
    return ex.package()


def order_example():
    ex = Example("order", "Strict BAC satisfies supplied A<C and B<C. "
                         "The selected reference is necessary-only.")
    scope = ex.scope("sequence", "sequence", universe=["A", "B", "C"])
    necessary = ex.premise("criteria_completeness", scope, "unresolved")
    ex.job("order", "s4.q02", scope, {"fulfillment": defined(category("fulfilled")),
        "violations": defined(integer(0))}, holds={"admissibility": "necessary_only"},
        premises=[necessary])
    return ex.package()


def forecast_example():
    ex = Example("forecast", "Event E, p=4/5, y=1. Issued at 10 and outcome available at 20.")
    scope = ex.scope("event", "forecast")
    timing = ex.premise("timely_issuance", scope)
    ex.job("forecast", "s4.q03", scope, {"loss": defined(rational(1, 25))}, premises=[timing])
    return ex.package()


def posterior_example():
    ex = Example("posterior", "Finite H0/H1 model and observed event D.")
    scope = ex.scope("posterior", "model")
    _, roles = ex.job("posterior", "s4.q06", scope, {
        "normalizer": defined(rational(1, 2)),
        "posterior": defined(keyed(h0=rational(1, 5), h1=rational(4, 5))),
        "weights": defined(keyed(h0=rational(1, 10), h1=rational(2, 5))),
    }, profile="p4")
    ex.add("inference", "inference", {"target": scope, "model": ex.source,
                                      "premises": [], "result": roles["posterior"]})
    ex.job("zero", "s4.q06", scope, {"normalizer": defined(rational(0, 1)),
        "posterior": {"tag": "undefined", "reason": "zero_normalizer", "basis": [ex.source]},
    }, profile="p4")
    return ex.package()


def replay_example():
    ex, original, result = graph_example("replay")
    scope = ex.scope("replay", "replay", universe=["AB", "AC", "BC"],
                     mask=["AB"], numerator=integer(1), denominator=integer(1))
    replay, outputs = ex.job("replay", "s4.q01", scope,
                             {"covered": defined(rational(1, 1))})
    comparison = ex.add("comparison", "comparison", {
        "original": result, "replay": outputs["covered"], "scope": scope,
        "comparator": contract("fixture.exact"), "outcome": "disagreement",
        "basis": [ex.source],
    })
    ex.add("replay", "reproduction", {
        "original_result": result, "original_calculation": original,
        "boundary": contract("fixture.derive_mask"), "comparator": contract("fixture.exact"),
        "basis": [ex.source], "outcome": "disagreement", "replay": replay,
        "comparison": comparison,
    })
    return ex.package()


EXAMPLES = {
    "graph": lambda: graph_example()[0].package(), "local": local_example,
    "order": order_example, "forecast": forecast_example, "paired": paired_example,
    "posterior": posterior_example, "replay": replay_example,
}


def expected_bytes(package):
    return json.dumps(package, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")
