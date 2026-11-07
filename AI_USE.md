# AI use and human contributions

Tickets: DLV-08, DLV-09, DLV-10. Prepared 6 November 2026.

Crucis was developed with extensive AI assistance. ChatGPT/Codex helped design
contracts and subsystem boundaries, work through examples, write implementation
and tests, investigate failures, prepare documentation and review evidence.
Earlier project handoffs also identify Claude-assisted work. Exact model versions
were not preserved for every historical conversation.

Uzair Gheewala set the intended contribution, directed the design iterations,
selected boundaries and priorities, approved the designs and implementation
bundles, and retained responsibility for scientific and release decisions.
Substantial code and prose were AI-produced. This does not mean every line has
been manually authored or independently inspected by a human.

## Important prompt families

| Area | Reconstructed summary of important instructions | Verification |
|---|---|---|
| Scope and support | Design an independent auditor with declared native semantics, uncertainty, supported connections and explicit evidence gaps; distinguish intended scope from tested implementation. | Versioned contracts, support profiles, synthetic conformance and separately scoped legacy compatibility checks. |
| System connections and experiments | Specify identities, capabilities, inputs, controlled comparisons, authority, budgets and what is not supported. Iterate with worked examples before implementation. | S1/S2 schema, codecs, validators and test records. Declaring an adapter is not proof of native support. |
| Execution | Design and implement bounded launch/capture/recovery with durable records, lost-reply handling, authority checks, retries and immutable evidence handoff. Test adverse paths without hidden live dispatch. | S3 controlled profiles and fault cases, with process-kill tests distinguished from simulated boundary failures. |
| Measurement | Define output/reference semantics, applicability, scope, calculation and withholding conditions for graph, local-answer, ordering, probability, paired and exact-reproduction cases. | S4 qualified procedures, independent known-answer fixtures, dependency/custody and recovery tests. |
| Implementation and review | Implement approved bundles with acceptance and recovery gates; preserve failures and limits; make validated local commits. | Exact staged-tree gates, standalone tests and package checks. No paid scientific campaign follows from a passing development gate. |

Available exact human prompt excerpts from measurement design and implementation:

> “Let's map the full measurement capability space, including output/reference combinations, their prerequisites, and what must remain withheld, before choosing support profiles. Still no implementation.”

> “Use concrete examples, still no implementation.”

> “Great, I went through the final design for S4 and I approve of it so please proceed onward with the detailed implementations for the bundles for S4, combing through the DAG o your own with their relevant validation gates and acceptance criteria as well all the way through to the end”

These excerpts are selected from a longer conversation; the table consolidates
repeated design, testing and debugging instructions. Older exact messages and
some model identities have not been fully recovered. This is a structured
summary, not an exhaustive transcript. The human author should add important
omissions before claiming a complete historical prompt inventory.
On 6 November the author confirmed the disclosed task families cover the
important uses he recalls; exact historical message recovery remains incomplete.

## Validation and scientific limits

Synthetic fixtures, typed-record validation, explicit missing-evidence cases,
adversarial failure/recovery tests, staged-tree checks and isolated package
checks were used to challenge AI-produced code. Actual execution and skip counts
belong to the versioned test receipts; they must not be inferred from test names.
The source includes implemented-scope and release-review documents for S1–S4.

This checkpoint snapshot is based on the public S1–S4 release. Later findings
subsystem work is excluded from it. Scientific observations in the paper come
from earlier recorded audits in a separate repository. Controlled software
conformance does not establish full native-system coverage, causal correctness
or a completed new multi-system empirical campaign. AI reviewers can share models
and assumptions; their agreement is not proof of truth.

Private research-assistance tooling helped organize evidence, review and drafting.
Its role is disclosed here without distributing private tooling, conversations
or unrelated records. Public code/tests and declared evidence requirements remain
the route for checking the included software.
