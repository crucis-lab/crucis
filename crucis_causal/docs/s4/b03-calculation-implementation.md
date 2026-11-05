# B03 calculation work and recovery

DLV-08, DLV-09.

The [coordinator](../../measurement/work.py) prepares the selected plan
again before admission. It binds the invocation and fresh claim to the
exact plan, procedure, selected output scopes and basis. Intent, entry
and observed result use distinct S3 transactions. The entry event
establishes entry to the calculation boundary. If work is interrupted
there, the evaluator outcome remains unobserved.

The [evaluation boundary](../../measurement/calculation.py) supplies
materialized output inputs and an exact arithmetic budget to an explicitly
installed callable. It checks outcome form and extent per role. A result
may be partial or failed with zero emissions. Recording accepts locally
observed work or reconciles exact existing evidence. It has no evaluator
path. Cold recovery verifies the durable transaction chain and retains
an uncertain or disputed result where the exact evidence cannot close it.

The B03 fixture uses the existing local S3 journal and controlled callable.
It verifies concurrent claims, denied write access, interrupted entry,
failed or partial work, and lost replies on intent and result commits.
These checks establish the local mechanism scope. Scientific evaluator
qualification, S4 publication and broader runtime support have separate
bundle gates.
