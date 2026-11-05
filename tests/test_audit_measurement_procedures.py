"""Independent small oracles and S1 readers for Q01, Q02, Q03 and Q06."""

from fractions import Fraction as F
from itertools import permutations, product
import unittest

from crucis_causal.connections.codec import dumps as dump_s1
from crucis_causal.connections.domains import directed_link, finite_domain, graph_body, member
from crucis_causal.connections.model import Builder, contract, known, number, scope, source, unresolved
from crucis_causal.execution.api import Limits as S3Limits
from crucis_causal.execution.codec import parse_snapshot
from crucis_causal.execution.model import canonical
from crucis_causal.measurement import ArithmeticBudget, CalculationHold, Limits
from crucis_causal.measurement.codec import check_outcome
from crucis_causal.measurement.judgment import (
    evaluate_judgment, graph_adjacency, judgment, local_parents, pair_key,
)
from crucis_causal.measurement.planning import PreparedOutput, PreparedSlot
from crucis_causal.measurement.point import binary_loss, evaluate_order, forecast_loss, ordering, strict_sequence
from crucis_causal.measurement.posterior import Alternative, evaluate_posterior, finite_posterior
from crucis_causal.measurement.procedure_inputs import exact
from crucis_causal.measurement.resolution import ResolvedRecord
from s4_wire_examples import category, keyed, local, rational


def inspected(builder, roots):
    view = parse_snapshot(dump_s1(builder.package(roots)), S3Limits())
    return {row["id"]: ResolvedRecord(view.package_id, view.digest["value"], row["id"],
                                      canonical(row["contract"]), canonical(row))
            for row in view.records}


def record(records, ref):
    return records[ref["target"]]


def graph(capture, omission, pairs):
    b = Builder("Q01 unordered adjacency fixture")
    d = finite_domain(b, ["A", "B", "C"])
    coverage = {"pairing": "unordered", "domain": d, "include_same_node": False,
                "pairs": [], "extent": "all_in_domain"}
    out = b.output("graph", graph_body(d, [directed_link(d, a, c) for a, c in pairs],
                                       coverage=coverage, omission=omission))
    rows = inspected(b, [out])
    return graph_adjacency(record(rows, out), record(rows, d),
                           [("0", "1"), ("0", "2"), ("1", "2")], capture)


def prepared_record(ident, kind, payload):
    c = {"name": "s4." + kind, "version": "0.1.0-proposal.1"}
    return ResolvedRecord("fixture.s4", "b" * 64, ident, canonical(c),
                          canonical({"id": ident, "kind": c["name"], "contract": c, "payload": payload}))


def input_result(key, value, subject="fixture"):
    return PreparedSlot(key, (prepared_record(key, "result", {
        "subject_key": subject, "outcome": {"tag": "defined", "value": value},
    }),))


class JudgmentCases(unittest.TestCase):
    def test_materialized_graph_adapter_emits_the_actual_mask(self):
        b = Builder("Q01 selected graph")
        domain = finite_domain(b, ["A", "B", "C"])
        native = b.output("graph", graph_body(
            domain, [directed_link(domain, "0", "1"), directed_link(domain, "0", "2")],
            coverage={"pairing": "unordered", "domain": domain, "include_same_node": False,
                      "pairs": [], "extent": "all_in_domain"}))
        actual = inspected(b, [native])
        a, bkey, c = pair_key("0", "1"), pair_key("0", "2"), pair_key("1", "2")
        capture = prepared_record("capture", "result", {"outcome": {
            "tag": "defined", "value": category("complete")}})
        reference = prepared_record("reference", "result", {"outcome": {
            "tag": "defined", "value": keyed(**{
                a: category("yes"), bkey: category("indeterminate"), c: category("no"),
            })}})
        target = prepared_record("scope", "scope", {"universe": [a, bkey, c]})
        binding = prepared_record("bind", "binding", {})
        selected = PreparedOutput("mask", binding, target, "judgment_mask", "pair", (
            PreparedSlot("native", (record(actual, native),)),
            PreparedSlot("domain", (record(actual, domain),)),
            PreparedSlot("capture", (capture,)), PreparedSlot("reference", (reference,)),
        ), ())
        result = evaluate_judgment(selected, ArithmeticBudget(Limits()))
        check_outcome(result, Limits())
        self.assertEqual([row["key"] for row in result["value"]["entries"]], [a, c])

    def test_graph_closed_open_partial_and_unavailable_are_distinct(self):
        a, b, c = pair_key("0", "1"), pair_key("0", "2"), pair_key("1", "2")
        truth = {a: "yes", b: "indeterminate", c: "no"}
        native = graph("complete", "asserted_absence", [("0", "1"), ("0", "2")])
        closed = judgment((a, b, c), native, truth)
        self.assertEqual((closed.judged, closed.matched), ((a, c), 2))
        self.assertEqual(exact(closed.measure("covered", ArithmeticBudget(Limits()), ())["value"]), 1)
        with self.assertRaisesRegex(CalculationHold, "full_scope_unjudged"):
            closed.measure("full", ArithmeticBudget(Limits()), ())
        corrected = judgment((a, b, c), native, {**truth, b: "no"})
        self.assertEqual(exact(corrected.measure("full", ArithmeticBudget(Limits()), ())["value"]), F(2, 3))
        open_answer = graph("complete", "unreported", [("0", "1"), ("0", "2")])
        self.assertEqual(open_answer[c], "unreported")
        self.assertEqual(judgment((a, b, c), open_answer, truth).judged, (a,))
        partial = graph("committed_subset", "asserted_absence", [("0", "1")])
        self.assertEqual(partial, {a: "yes", b: "unresolved", c: "unresolved"})
        with self.assertRaisesRegex(CalculationHold, "interpreted_answer_unavailable"):
            graph("unavailable", "asserted_absence", [])

    def test_local_membership_exact_predicate_and_explicit_abstention(self):
        b = Builder("Q01 local parent fixture")
        domain = finite_domain(b, ["A", "B", "C", "Z"])
        propositions = []
        for key in ("0", "1", "2"):
            propositions.append(b.add("proposition", {
                "predicate": contract("direct_relation"),
                "arguments": [{"role": "s1.cause", "value": member(domain, key)},
                              {"role": "s1.effect", "value": member(domain, "3")}],
                "conditioning": [], "scope": scope(domain),
            }))
        out = b.output("claims", {"propositions": propositions, "decisions": [
            {"proposition": prop, "decision": decision, "reason": unresolved(), "source": source()}
            for prop, decision in zip(propositions, ("assert", "abstain", "deny"))],
            "coverage": scope(domain), "omission": "s1.unreported"})
        abstained = b.output("abstention", {"query": propositions[0], "reason": unresolved(),
                                             "scope": scope(domain)})
        rows = inspected(b, [out, abstained])
        candidates = ("0", "1", "2")
        props = [record(rows, ref) for ref in propositions]
        native = local_parents(record(rows, out), record(rows, domain), props, "3",
                               candidates, "complete")
        truth = {"0": "yes", "1": "no", "2": "indeterminate"}
        self.assertEqual(judgment(candidates, native, truth).judged, ("0",))
        with self.assertRaisesRegex(CalculationHold, "local_proposition_scope"):
            local_parents(record(rows, out), record(rows, domain), props, "2",
                          ("0", "1", "3"), "complete")
        no_answer = local_parents(record(rows, abstained), record(rows, domain), props, "3",
                                  candidates, "complete", query=props[0])
        judged = judgment(candidates, no_answer, truth)
        budget = ArithmeticBudget(Limits())
        self.assertEqual(exact(judged.measure("captured_coverage", budget, ())["value"]), 0)
        diagnostic = judged.measure("covered", budget, [local("src", "source")])
        self.assertEqual(diagnostic["reason"], "zero_judged_denominator")
        check_outcome(diagnostic, Limits())

    def test_small_exhaustive_ledger_and_conflict(self):
        basis = [local("src", "source")]
        for a, b in product(("yes", "no", "abstain"), ("yes", "no", "conflicting")):
            expected = a != "abstain" and b != "conflicting"
            result = judgment(["x"], {"x": a}, {"x": b})
            self.assertEqual(result.judged, ("x",) if expected else ())
            computed = result.measure("covered", ArithmeticBudget(Limits()), basis)
            self.assertEqual(exact(computed["value"]) if expected else computed["tag"],
                             int(a == b) if expected else "undefined")
        with self.assertRaisesRegex(CalculationHold, "judgment_eligibility_unresolved"):
            judgment(["x"], {"x": "unresolved"}, {"x": "yes"}).measure(
                "covered", ArithmeticBudget(Limits()), basis)


class PointCases(unittest.TestCase):
    def test_six_permutations_and_necessary_only_reference(self):
        rules = [("r1", "A", "C"), ("r2", "B", "C")]
        passing = {''.join(p) for p in permutations("ABC")
                   if ordering("ABC", p, rules, "complete", "complete").admissible}
        self.assertEqual(passing, {"ABC", "BAC"})
        necessary = ordering("ABC", "BAC", rules, "necessary_only", "complete")
        self.assertEqual(necessary.violated, ())
        self.assertIsNone(necessary.admissible)
        excluded = ordering("ABC", "ACB", rules, "necessary_only", "complete")
        self.assertEqual(excluded.violated, ("r2",))
        self.assertFalse(excluded.admissible)
        self.assertFalse(ordering("ABC", "BA", rules, "complete", "complete").fulfilled)
        with self.assertRaisesRegex(CalculationHold, "sequence_capture_unresolved"):
            ordering("ABC", "BA", rules, "complete", "partial")
        self.assertTrue(ordering("ABC", "BAC", [], "complete", "complete").admissible)
        with self.assertRaisesRegex(CalculationHold, "cyclic_order_reference"):
            ordering("ABC", "BAC", [*rules, ("r3", "C", "B")], "complete", "complete")

    def test_s1_order_and_forecast_readers(self):
        b = Builder("Q02/Q03 finite fixture")
        d = finite_domain(b, ["A", "B", "C"])
        order = b.output("order", {"predicate": contract("precedence"), "domain": d,
                                     "representation": "sequence",
                                     "sequence": [member(d, key) for key in ("1", "0", "2")],
                                     "pairs": [], "coverage": scope(d), "omission": "s1.no_assertion"})
        event = b.add("proposition", {"predicate": contract("fixture_event"),
                    "arguments": [], "conditioning": [], "scope": scope(d)})

        def quantity(kind):
            return b.output("quantity", {"quantity_kind": kind, "subject": event,
                        "value": known(number("0.8")), "units": unresolved(), "conditioning": [],
                        "basis": unresolved(), "procedure": b.producer, "associated_rule": unresolved()})

        forecast, p_value = quantity("s1.probability"), quantity("s1.p_value")
        rows = inspected(b, [order, forecast, p_value])
        self.assertEqual(strict_sequence(record(rows, order), record(rows, d)), ("1", "0", "2"))
        target = prepared_record("scope", "scope", {"universe": ["0", "1", "2"]})
        binding = prepared_record("bind", "binding", {})
        condition = keyed(after={"value_kind": "text", "value": "2"},
                          before={"value_kind": "text", "value": "0"})
        check_outcome({"tag": "defined", "value": condition}, Limits())
        selected = PreparedOutput("violations", binding, target, "violations", "order", (
            PreparedSlot("native", (record(rows, order),)),
            PreparedSlot("domain", (record(rows, d),)),
            input_result("capture", category("complete")),
            input_result("criteria", category("necessary_only")),
            input_result("conditions", keyed(r1=condition)),
        ), ())
        self.assertEqual(exact(evaluate_order(selected, ArithmeticBudget(Limits()))["value"]), 0)
        result = forecast_loss(record(rows, forecast), record(rows, event), True,
                               ArithmeticBudget(Limits()), prospective=True, order="before")
        self.assertEqual(exact(result["value"]), F(1, 25))
        with self.assertRaisesRegex(CalculationHold, "forecast_event_mismatch"):
            forecast_loss(record(rows, p_value), record(rows, event), True,
                          ArithmeticBudget(Limits()), prospective=True, order="before")

    def test_binary_loss_endpoints_complements_and_timing(self):
        def loss(p, y, order="before"):
            return exact(binary_loss(p, y, ArithmeticBudget(Limits()), event_match=True,
                                     prospective=True, order=order)["value"])
        self.assertEqual((loss(F(0), True), loss(F(1), True)), (1, 0))
        for p in (F(0), F(1, 2), F(4, 5), F(1)):
            self.assertEqual(loss(p, True), loss(1-p, False))
        for order, reason in (("unresolved", "unresolved"), ("after", "contradicted")):
            with self.assertRaisesRegex(CalculationHold, "forecast_issuance_" + reason):
                loss(F(4, 5), True, order)


class PosteriorCases(unittest.TestCase):
    def test_materialized_posterior_preserves_alternative_keys(self):
        binding = prepared_record("bind", "binding", {})
        scope_record = prepared_record("scope", "scope", {})
        selected = PreparedOutput("post", binding, scope_record, "posterior", "model", (
            input_result("model", keyed(
                h1=keyed(likelihood=rational(4, 5), prior=rational(1, 2)),
                h0=keyed(likelihood=rational(1, 5), prior=rational(1, 2))), "event-d"),
            input_result("observation", {"value_kind": "boolean", "value": True}, "event-d"),
            input_result("partition", category("established")),
        ), ())
        emitted = evaluate_posterior(selected, ArithmeticBudget(Limits()))
        check_outcome(emitted, Limits())
        self.assertEqual([(row["key"], exact(row["value"])) for row in emitted["value"]["entries"]],
                         [("h0", F(1, 5)), ("h1", F(4, 5))])

    def infer(self, rows, matches=True):
        return finite_posterior(rows, ArithmeticBudget(Limits()),
                                partition_established=True, observation_matches=matches)

    def test_independent_joint_mass_table_and_key_associations(self):
        table = {"h0": (F(1, 10), F(4, 10)), "h1": (F(4, 10), F(1, 10))}
        conditional = {key: observed / sum(observed for observed, _ in table.values())
                       for key, (observed, _) in table.items()}
        result = self.infer([Alternative("h1", F(1, 2), F(4, 5)),
                             Alternative("h0", F(1, 2), F(1, 5))])
        self.assertEqual(dict(result.values), conditional)
        self.assertEqual(result.normalizer, F(1, 2))
        self.assertEqual(dict(result.weights), {key: pair[0] for key, pair in table.items()})

    def test_zero_normalizer_and_missing_likelihood_have_distinct_results(self):
        result = self.infer([Alternative("h0", F(1), F(0)), Alternative("h1", F(0), F(1))])
        self.assertEqual(exact(result.measure("normalizer")["value"]), 0)
        self.assertEqual(result.measure("posterior", [local("src", "source")])["reason"],
                         "zero_normalizer")
        with self.assertRaisesRegex(CalculationHold, "model_likelihood_unavailable"):
            self.infer([Alternative("h0", F(1), F(0)), Alternative("h1", F(0), None)])
        with self.assertRaisesRegex(CalculationHold, "model_observation_mismatch"):
            self.infer([Alternative("h0", F(1), F(0)), Alternative("h1", F(0), F(1))], False)
