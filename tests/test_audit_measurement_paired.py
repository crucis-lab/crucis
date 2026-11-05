"""B06 finite frame, delivery scope and exact outer interval gates."""

from dataclasses import replace
from fractions import Fraction as F
from itertools import product
import unittest

from crucis_causal.measurement import ArithmeticBudget, CalculationHold, Limits
from crucis_causal.measurement.paired import (
    Candidate, Closure, DeliveryPolicy, Pair, Range, UNIT_RANGE, ZERO,
    delivery_utility, evaluate_utility_enclosure, paired_differences, paired_enclosure, paired_point,
)
from crucis_causal.measurement.planning import PreparedOutput, PreparedSlot
from crucis_causal.measurement.procedure_inputs import exact
from s4_wire_examples import EXAMPLES
from test_audit_measurement_procedures import prepared_record
from test_audit_measurement_wire import record


def budget():
    return ArithmeticBudget(Limits())


def evidence():
    policy = DeliveryPolicy("k2-b", frozenset({"attempt"}), frozenset({"answer"}), "receiver",
                            "clock", F(10))
    closure = Closure(policy.slot, policy.attempts, policy.channels, policy.boundary, policy.clock,
                      F(10), True, (), "verified_authoritative_history")
    candidate = Candidate("candidate", "attempt", "answer", "receiver", "clock",
                          Range(F(10), F(10)), "yes", Range(F(4, 5), F(4, 5)))
    return policy, closure, candidate


class PairedCases(unittest.TestCase):
    def test_intended_frame_point_and_partial_diagnostics(self):
        pairs = [Pair("k1", "1a", "1b"), Pair("k2", "2a", "2b")]
        slots = {"1a": F(4, 5), "1b": F(1, 2), "2a": F(1, 5), "2b": F(3, 10)}
        independent = (slots["1a"] + slots["2a"] - slots["1b"] - slots["2b"]) / 2
        self.assertEqual(paired_point(pairs, slots, budget()), independent)
        reverse = [Pair(p.key, p.b, p.a) for p in reversed(pairs)]
        self.assertEqual(paired_point(reverse, slots, budget()), -independent)
        slots["2a"] = None
        self.assertEqual(paired_differences(pairs, slots, budget()), {"k1": F(3, 10)})
        with self.assertRaisesRegex(CalculationHold, "incomplete_quality_frame"):
            paired_point(pairs, slots, budget())
        del slots["2a"]
        with self.assertRaisesRegex(CalculationHold, "intended_slot_ledger_required"):
            paired_differences(pairs, slots, budget())

    def test_delivery_zero_requires_full_scope_and_authoritative_history(self):
        policy, closure, candidate = evidence()
        late = replace(candidate, receipt_times=Range(F(11), F(11)))
        self.assertEqual(delivery_utility(policy, [late], closure, total_utility_established=True).value,
                         ZERO)
        for missing in (None, replace(closure, gaps=("capture_gap",)),
                        replace(closure, channels=frozenset({"other"}))):
            unresolved = delivery_utility(policy, [late], missing, total_utility_established=True)
            self.assertEqual(unresolved.value, UNIT_RANGE)
            self.assertEqual(unresolved.delivery, "unresolved")
        with self.assertRaisesRegex(CalculationHold, "utility_target_unestablished"):
            delivery_utility(policy, [], closure, total_utility_established=False)

    def test_inclusive_horizon_earlier_receipt_and_selection_uncertainty(self):
        policy, closure, candidate = evidence()
        selected = delivery_utility(policy, [candidate], closure, total_utility_established=True)
        self.assertEqual(selected.selected, "candidate")
        self.assertEqual(selected.value, Range(F(4, 5), F(4, 5)))
        straddles = replace(candidate, receipt_times=Range(F(9), F(11)))
        unresolved = delivery_utility(policy, [straddles], closure, total_utility_established=True)
        self.assertEqual(unresolved.value, Range(F(0), F(4, 5)))
        earlier = replace(candidate, key="earlier", receipt_times=Range(F(8), F(8)),
                          qualification="unresolved", quality=Range(F(1, 5), F(1, 5)))
        unknown_winner = delivery_utility(policy, [candidate, earlier], closure,
                                          total_utility_established=True)
        self.assertEqual(unknown_winner.delivery, "established")
        self.assertIsNone(unknown_winner.selected)
        self.assertEqual(unknown_winner.value, Range(F(1, 5), F(4, 5)))
        zero = delivery_utility(policy, [replace(candidate, quality=ZERO)], closure,
                                total_utility_established=True)
        self.assertEqual((zero.value, zero.delivery), (ZERO, "established"))

    def test_enclosure_matches_independent_corners_and_widens_for_unknown_slot(self):
        pairs = [Pair("k1", "1a", "1b"), Pair("k2", "2a", "2b")]
        for last, expected in ((ZERO, Range(F(3, 20), F(13, 20))),
                               (UNIT_RANGE, Range(F(-7, 20), F(13, 20)))):
            ranges = {"1a": Range(F(4, 5), F(4, 5)), "1b": Range(F(1, 2), F(1, 2)),
                      "2a": UNIT_RANGE, "2b": last}
            corners = [(F(3, 10)+a-b)/2 for a, b in product((F(0), F(1)), (last.lower, last.upper))]
            self.assertEqual(paired_enclosure(pairs, ranges, budget()), expected)
            self.assertEqual(expected, Range(min(corners), max(corners)))
        singletons = {"1a": F(4, 5), "1b": F(1, 2), "2a": F(0), "2b": F(1, 5)}
        point = paired_point(pairs, singletons, budget())
        self.assertEqual(paired_enclosure(pairs, {key: Range(x, x) for key, x in singletons.items()},
                                         budget()), Range(point, point))

    def test_materialized_ranges_must_match_every_exact_planned_slot(self):
        package = EXAMPLES["paired"]()
        population = prepared_record("pop", "population", record(package, "pop")["payload"])
        slots = tuple(prepared_record(r["id"], "result", r["payload"])
                      for r in package["records"] if r["id"].startswith("range."))
        selected = PreparedOutput("bound", prepared_record("bind", "binding", {}),
                                  prepared_record("scope", "scope", {}), "outer_bound", "frame", (
                                      PreparedSlot("population", (population,)), PreparedSlot("ranges", slots),
                                  ), ())
        outcome = evaluate_utility_enclosure(selected, budget())["value"]
        self.assertEqual((exact(outcome["lower"]), exact(outcome["upper"])), (F(3, 20), F(13, 20)))
        incomplete = replace(selected, slots=(selected.slots[0], PreparedSlot("ranges", slots[:-1])))
        with self.assertRaisesRegex(CalculationHold, "complete_utility_range_frame_required"):
            evaluate_utility_enclosure(incomplete, budget())
