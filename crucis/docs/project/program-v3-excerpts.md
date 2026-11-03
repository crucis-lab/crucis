# Excerpts of the program docs that bind W2 (copied 31 Oct 2026 from the claude.ai project "DSC 180 - Causal Discovery")

The full docs live in the project; these are the parts W2's work depends on, copied verbatim (headings kept). If the
project copy is newer, it wins: ask Uzair for it.

---

## From `claude/program-v3-2026-10-29.md` (29 Oct)

### 0. What the TA meeting settled (summary)
- One-person group approved by the TA (to be confirmed in writing, CRS-09).
- **Q1 and Q2 are separate.** Each gets its own paper and its own repository. **Q1** is the field side: a generic,
  automated auditing system for causal-discovery systems. **Q2** is the architecture side: Causal-Copilot rebuilt into our
  own system.
- **Next deadline: Fri 6 Nov.** The Q1 checkpoint: title, abstract, introduction including the literature review, the data,
  and the public code link.

### 1. The two endeavours (excerpt)
- A, the auditor (Q1): tell anyone how far to trust a causal-discovery system's claims, and why. Consumes any system as a
  black box (an adapter) or a glass box (stage traces). Produces an audit report: typed findings, scores under controls, a
  reproducible certificate.
- B, the system (Q2): produce causal claims that survive the auditor, with their sources and with abstention.
- **The contract between them is the claim-ledger format plus the audit protocol, both public.** A audits B through the same
  adapter interface as every other system. B gets no private door into A. B may read A's development battery. It never
  sees A's sealed battery.

### 2. A, the auditor: what the golden version is
**A one-line target: a continuous-integration check for causal claims.**
- Point it at any causal-discovery system with an adapter of about 50 lines.
- One command later, you have an audit report that says: what the system gets right; where its answers come from (the
  numbers, the names, the file layout, its own rules); how its errors behave under controlled change; whether its
  confidence means anything; what it costs.
- The report is reproducible by anyone and cannot be gamed by renaming or reordering columns.

#### 2.1 Levels (each one usable on its own; each adds a kind of finding)
| Level | Name | Needs from the system | Finds |
|---|---|---|---|
| L0 | Output scoring | its final graph | adjacency and direction accuracy against known truth, completion, cost |
| L1 | Metamorphic controls | the ability to run on transformed copies | name reliance (real / neutral / swapped), layout reliance (column order, file path), robustness (sample size, noise, mechanism family), knowledge reliance (none / oracle / wrong supplier) |
| L2 | Stage tracing | a glass-box hook (Python entry point) | which step adds, deletes or flips each edge; where crashes happen; which model call caused what |
| L3 | Claim provenance | the system's claims, or A's inferred attribution | per edge, the share explained by data, names, layout or rules; calibration and abstention quality |
| L4 | Adversarial search | repeated runs | scenarios generated to break the system (shortcut probes, near-boundary identifiability, plurality traps like gas/void) |

#### 2.2 The protocol (what makes an audit comparable)
- **Typed findings.** Each finding has: a kind (from a closed list), the control that shows it, an effect size with an
  interval, and its evidence files.
- **Regimes.** Data only; data plus interventions; data plus declared knowledge; all three. A score is only ever compared
  within its regime.
- **Pre-registered thresholds** for each finding kind, hashed before the run.
- **Truth tiers** for reference graphs: exact (simulated), contested (Sachs), provenance-only, mismatched. A "score" on a
  contested reference is reported as agreement, never as accuracy.
- **Batteries.** A development battery (public, anyone may tune on it) and a sealed battery (hashed, generator seeds
  withheld, read once per declared version).
- **The certificate.** System identity, battery hash, every number with its source, and the rerun command.

#### 2.3 Why the field needs it (the claims the Q1 paper argues)
1. Benchmarks reward shortcuts (CausalArena layout, AB-01; CausalBench, BEN-13).
2. LLM causal agents read names, not data (AB-06; inside Causal-Copilot 81 of 101 model edges follow swapped labels, BND-08).
3. Agents' own steps can destroy what the data found. Causal-Copilot's review halves link recovery (0.584 to 0.321) and
   crashes in every run that reaches its cycle step (BLD-06). **(W2, 31 Oct: the loss is in the bootstrap step, which
   makes no model call; see w2-rebase section 7.)**
4. Nobody publishes how often these systems should say "I don't know" (AB-14).

#### 2.4 A's deliverables
| # | Deliverable | Q1 checkpoint (6 Nov) | Q1 final (4 Dec) |
|---|---|---|---|
| A1 | The Q1 paper | title, abstract, introduction, literature review, data | full paper |
| A2 | Audit protocol spec | outlined in the paper's introduction | v1: finding kinds, regimes, truth tiers, batteries, certificate format |
| A3 | `audit` package | the Q1 repo as it stands (reproduces BLD-06) | one command audits a system end to end; adapters for the 5 audited systems plus plain PC and GES |
| A4 | Audit results | cited in the introduction | tables per system: L0-L2, provenance by arm difference (L3-lite) |
| A5 | Benchmark shortcut audits | cited | CausalArena layout, CausalBench metric, as an appendix |
| A6 | Public scorecards | (site) | one page per audited system, generated from the reports |

### 4. The adversary loop (rules that keep it honest)
1. B tunes on A's development battery only. The sealed battery, and the generator seeds behind it, never reach B's
   developers. Each declared B version reads the sealed battery once.
2. A's new finding kinds are pre-registered before they are run on B.
3. Every round is logged: A version, B version, battery hash, findings opened, findings closed, any regressions.
4. A finding is closed only by a sealed read.
5. Cases like gas/void become regression checks, never tuning targets or thresholds.

### 11. Failure modes, named before they happen (excerpt)
1. B overfits A. 2. The two papers claim the same result. 3. The auditor is too specific to Causal-Copilot (the adapter
interface is designed against all 5 audited systems plus plain algorithms before it is frozen). 4. The product story
outruns the evidence. 5. The chats drift from each other: each chat owns named files and tickets; W5 keeps the program doc,
tracker and site; **changes to the contract (ledger format, protocol) go through W5**. 6. The checkpoint is missed while
building: W1 has priority until 6 Nov.

---

## From `claude/program-v3-kickoffs-2026-10-29.md`: the shared rules, and the W2 block
Rules shared by every chat:
- Never run git write operations on the mounted repos. Uzair commits and pushes; write commit messages to
  `docs/commit_msgs/<execution>_<repo>.txt`.
- Edits to existing pinned or shared files go through patch scripts in `jobs/patches/`, followed by py_compile, the relevant
  unittests run with `--out` outside the repo, `tracker/verify.py` repins after review, and `tracker/snapshot.py` last.
- Follow cc-research's AGENTS.md: never open or print `../Causal-Copilot/.env`; spend no API credit without Uzair's go;
  never post in #causal-discovery (prepare drafts with relay.py); #cd-tracker is fine.
- Open every reply with "where we are now" and close with "where we're going". Plain language; derive metrics step by step.
- Full design first, then bundles that are each verifiable in one run, each with a must-show list.
- Stay inside your owned files. Anything that changes the shared contract (ledger format, audit protocol, tickets) goes to
  the program chat (W5).

W2 (the audit package: A2, A3, A4):
> Read `claude/program-v3-2026-10-29.md` section 2, then the cc-research harness (`harness/`), the scorer (`score/`,
> `analysis/cc_graph.py`), the field-audit adapters (`harness/agents/`, `analysis/ab06_*`), `tools/export_q1.py`, and the Q1
> repo. Design, before writing any code: the audit protocol v1 (finding kinds as a closed list, regimes, truth tiers,
> development and sealed batteries, the certificate); the `audit` package architecture. Design the adapter interface
> against all five audited systems plus PC and GES before freezing it. Then build in bundles: (1) adapter interface and the
> L0 scorer; (2) L1 controls; (3) L2 tracing for Python systems; (4) reports and certificates; (5) rerun the existing
> audits, with no new API spend except where a rerun is needed; ask first.
> Owned files: a new package folder in cc-research (`audit/`), its tests, and the Q1 repo's export allowlist.
> Must show per bundle: tests; one system audited end to end; the numbers equal the existing audit results to 0.001.

---

## From `claude/w5-restart-2026-10-30.md` (30 Oct): the machine and the ticket IDs
- The work is on the second laptop (Intel Core Ultra 7 155U, AVX2, no AVX-512; BLAS family HASWELL, as on laptop 1).
- Agents reached it through a Linux VM shell with the folder mounted at `$HOME/mnt/DSC 180A`. It is slow (`git status` on
  cc-research takes about 2 minutes). Use `python3` with `PYTHONDONTWRITEBYTECODE=1` there, and
  `git --no-optional-locks -c safe.directory=*` for read-only git. That shell cannot delete files. `py -3` and `cc.ps1` are
  Uzair's to run on Windows.
- Ticket changes go to W5. W2 owns DLV-08 (A2 protocol), DLV-09 (A3 package), DLV-10 (A4 results). Neighbours: DLV-05/06
  (W1, paper), DLV-07 (Q1 repo export), DLV-11 (benchmark appendix), ADV-01 (adversary loop, W3), BLD-15 (the B5 claim
  checker that shares the `audit/` folder).
