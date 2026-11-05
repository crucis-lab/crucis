# S4 measurement release review

DLV-08, DLV-09, DLV-10. This is the local implementation review for the
[approved contract and bundle graph](approved-2026-11-04/s4-candidate-build-dag.json).
The [build entry](approved-2026-11-04/build-entry.json) preserves the approval
and baseline. The wire retains the exact approved review version.

## Methodology and support

The evidence chain runs from the intended question through a selected
binding, a scoped plan, actual work and a recorded result. Applicability and
qualification are separate claims. Evidence can stay unavailable, be
withheld at one output while another completes, or support a defined result
only on a named subset. A later snapshot preserves its own frontier.

| Scope | Implemented and tested | Scope limit |
|---|---|---|
| P0 preservation and P1 interpretation | [Wire](b01-wire-implementation.md), [binding](b02-binding-implementation.md) and [legacy capture](b10-legacy-implementation.md). Seven golden wire packages preserve roles and exact values. Tests check typed S1/S2/S3 dependencies, opaque bytes, historical field attribution, and mismatched or restricted evidence. | A preserved field or a historical label supports only its stated attribution and scope. |
| P2 Q01 proposition judgment | [Judgment](../../measurement/judgment.py) and [independent ledger fixtures](../../../tests/test_audit_measurement_procedures.py). The selected finite adjacency and direct-parent membership readers distinguish closed, open, partial, missing and abstaining responses. | Covered judgment and full judgment have separate masks and denominators. Unreported relationships need evidence of closure before they count as absent. |
| P2 Q02 strict sequence and Q03 binary loss | [Point procedures](../../measurement/point.py) and [permutation and forecast fixtures](../../../tests/test_audit_measurement_procedures.py). All six small permutations, necessary-only precedence, prospective timing, exact endpoints and event mismatches are exercised. | Admissibility requires sufficient reference semantics. The loss applies to the named binary event under the selected information policy. Population calibration needs separate evidence. |
| P2/P3 Q04 paired point and Q05 delivery utility enclosure | [Paired procedures](../../measurement/paired.py) and [intended-frame fixtures](../../../tests/test_audit_measurement_paired.py). Each planned slot is accounted for. Scope and delivery tests distinguish established zero, observed quality, unresolved capture and an outer range. | A full-frame point requires all its inputs. The enclosure has no sampling, sharpness or causal-attribution claim. |
| P2/P4 Q06 finite conditional posterior | [Posterior](../../measurement/posterior.py), [joint-mass oracle](../../../tests/test_audit_measurement_procedures.py) and [integrated recorded fixture](../../../tests/test_audit_measurement_release.py). The integrated fixture checks separately pinned qualification evidence, actual journal work, exact roles and a scoped conditional criterion. | The posterior is conditional on the supplied finite model and observed protocol. Missing likelihood and zero normalizer have different dispositions. Model adequacy requires separate evidence. |
| P5 exact computational reproduction | [Comparison](b08-reproduction-implementation.md) and [separate-work fixtures](../../../tests/test_audit_measurement_reproduction.py). Exact quantity agreement, changed basis and same-basis mask disagreement are distinct. Tests also exercise access denial and incomplete work. | The claim is agreement or disagreement at the exact comparator boundary. Native or stochastic reproduction and independent scientific replication require separate qualification. |

The [assessment interface](../../measurement/assessment.py) resolves the
selected target, frontier, audience, premises, qualification receipts and
basis under explicit read authority. The supplied criterion owns the
scientific rule. The core withholds the claim when required evidence cannot
be resolved, and registry or descriptor metadata alone cannot establish a
profile. The fixture criteria cover their named cases. New scientific
combinations require their own criteria and evidence.

## Operation and recovery

- [Calculation lifecycle](b03-calculation-implementation.md) separates
  invocation, occurrence, work and recording. Tests inject lost replies,
  interrupt after entry, reject changed basis, and reconcile duplicate
  admission without running a second evaluator. The integrated Q06 fixture
  reopens a typed result tied to the actual committed S3 journal observation.
- [Publication](b09-publication-implementation.md) preserves exact S4 bytes
  inside an S3 carrier. Tests cover inner and outer dependency closure,
  restricted projection, lost commit replies and stale pointer updates.
- The [CLI](../../measurement/__main__.py) inspects exact bytes and prepares
  plans using caller-supplied dependencies and bounded declarations.
  The integrated test uses normal CLI entry points and checks that planning
  performs no work. The distribution gate builds from the exact staged tree,
  runs wire tests from the unpacked sdist and probes the installed wheel with
  research imports blocked.

## Evidence receipts

Bundle review notes above connect source and fixture scope to the exact
staged and enabled-hook receipts. The workspace build ledger keeps
per-bundle tree and commit identities, gate logs, and the final staged
distribution receipt. Offline test reports preserve the data and dependency
skips as skips.

The separate [B10 compatibility gate](b10-legacy-implementation.md) checked
1,298 stored comparisons at tolerance 0.001 and verified 14 stored plus
14 freshly computed certificates. It used the unchanged historical route.
Its results do not qualify an S4 calculation, expand a profile or port a
paper number. The S4 fixture evidence does not establish native-system or
benchmark-wide coverage.
