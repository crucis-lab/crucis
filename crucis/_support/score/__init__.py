"""Scorer v2 (deliverable D0.4 of plans/q2_dag.json, bundle B0). One package for every number the Q2 build reports.

Pure Python + NumPy, so it runs in CI. Every function states its rule; the reproduction test
(tests/test_score.py, and score/repro.py on the CausalArena files) checks that it gives the audit chapter's numbers
(AB-01 controlled scoreboard, AB-04 decision value) to 0.001 before any build result is computed with it.

Modules
  graph     directed F1 under the expectation rule, S / c / q / a, reachability
  dv        DV-1 claims ("if I set T, does Y move?"), pooled precision and coverage, the selective view, usefulness
  calib     reliability bins, expected calibration error, risk-coverage, claimed vs realised precision
  rca       AC@k at stated coverage
  paired    paired differences with a scenario-cluster bootstrap interval
Tickets: BLD-02, BLD-05, EVL-03, CAP-07, CAP-08, TGT-12
"""
