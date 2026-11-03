"""Truth tiers (protocol v1, section 1.3). T1 exact (simulated), T2 contested (e.g. Sachs), T3 provenance-only,
T4 mismatched (a reference known not to describe the data; diagnostic only, inside controls such as K11).
Rule R3: T1 numbers are 'accuracy', T2/T3 'agreement', T4 is never scored alone; items of different tiers are not pooled."""
TIERS = {"T1": "exact (simulated)", "T2": "contested", "T3": "provenance-only", "T4": "mismatched (diagnostic)"}
WORD = {"T1": "accuracy", "T2": "agreement", "T3": "agreement"}
