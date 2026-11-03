# Kickoff prompt for Codex: W2, the audit package (paste everything below the line)

---

You are continuing **W2**, one of several parallel workstreams on Uzair's UCSD DSC 180A capstone (causal discovery). The
previous W2 session ran in another assistant and is closed. All of its context is on disk: there is no chat history to
rely on. Your job in this session starts in the **design-iteration phase**: you re-establish where W2 stands, prove it from
the files, and then iterate on the design with Uzair before anything new is built.

**Where you are working.**
- The repository is `cc-research`, inside `C:\Users\uzair\Documents\UCSD\Fall 2026\DSC 180A\` on Uzair's second laptop.
  Its siblings are `Causal-Copilot` (the fork), `Causal-Copilot-branches`, `causal-copilot-q1` (the exported public Q1 repo)
  and `_w2_transfer` (old transfer files).
- On Windows the interpreter is `py -3`. A Linux VM shell, if you have one, uses `python3` with
  `PYTHONDONTWRITEBYTECODE=1`.

**What W2 is.**
- The Q1 paper is about an auditor for causal-discovery systems: point it at any system through a ~50-line adapter, and one
  command produces a report of typed findings and a certificate anyone can recompute.
- W2 owns the protocol spec (ticket DLV-08), the `audit` package (DLV-09) and the audit results (DLV-10).
- W1 owns the paper (`docs/paper/q1/`), W3 the system being renovated (Causal-Copilot's fork, Q2), and W5 the program,
  tickets, site and shared contracts.

## Step 1: read, in this order (do not skim the first two)
1. `audit/docs/STATE.md`: the state file. It lists what is on disk, what is verified and where, the green gate, open
   decisions, lessons, and what must not happen.
2. `audit/docs/project/w2-rebase-2026-10-31.md`: **the rebase and the protocol v1.1 design iteration. This is the point
   the work stopped at.**
3. `audit/docs/project/q1-checkpoint-2026-10-31.md`: W1's doc. The contract between the package and the paper is in
   sections 3-4; W2's notes on the paper's claims are in section 2a.
4. `audit/PROTOCOL.md` (v1.0, as built), `audit/README.md`, `audit/AGENTS.md`, and the root `AGENTS.md`.
5. `audit/docs/project/audit-package-build-2026-10-31.md` and `audit-package-design-2026-10-30.md`.
6. `audit/docs/project/program-v3-excerpts.md`: the program's golden version of the auditor, the shared rules, the machine.
7. Skim the code once you know the layout: `audit/core/adapter.py` (the interface), `audit/findings.py` (the closed list in
   action), `audit/rerun/existing.py` (how every stored number is recomputed), `audit/report/certificate.py`.

## Step 2: prove the ground has not moved (read-only; nothing is written inside the repo)
Run these and compare with what STATE.md and the rebase say. If a command needs `py -3`, ask Uzair once at the start
whether you may run read-only and test commands yourself; otherwise give him the command and wait for its output.
1. `py -3 audit\docs\checks\rebase_facts.py --out <a file outside the repo>`. Expected:
   - `rerun`: 1298 compared, all pass, max_abs_diff about 9.1e-05;
   - `grid`: 210 cells, 79 measured (30 fires, 43 clear, 6 inconclusive);
   - `stages.main`: S0->S1 -0.270 [-0.327, -0.200], S1->S2 +0.007 [-0.027, +0.042], n = 22;
   - `cycle_step`: 8 entering, 8 crashed, 0 completed;
   - `overlap`: 0 scenarios shared between `ca-ab06` and `q1s2`; 10 of 10 q1s2 scenarios with an `obs_int` twin;
   - `causaliq_probabilities`: every response carries existence/orientation.
2. `py -3 -m audit verify audit\results\rerun_v1\reports\matmcd\certificate.json`: pass, 189 numbers, 0 mismatches. On
   Windows `same_host` is false, so the tolerance is 0.001.
3. `py -3 tests\run_tests.py --out <outside> --pattern test_audit_*.py`: 55 tests, OK. This is also the **green gate's
   Windows test run**; if Uzair has not run it, this is it. Record where the output went.
4. The code-identity hash in STATE.md section 2: if the files differ, find out what changed before going further.
Report each result against its expectation. A mismatch is a finding: diagnose it to the line before doing anything else.

## Step 3: report back, then iterate on the design with Uzair
Open with "Where we are now" and close with "Where we're going". Plain language; derive any metric step by step. Report:
- What is built (B1-B5) and verified, and the green gate's remaining items: the Windows run (just done or not), the commit
  and `tracker/verify.py --repin DLV-07` and `tracker/snapshot.py` (Uzair's), and W5 adopting the protocol.
- The coverage picture:
  - 79 of 210 cells measured;
  - about 75 not applicable by capability;
  - about 34 free to close;
  - about 20 need spend;
  - a few need W3.
- The design questions now open, which come from the rebase section 5 (V1-V9) and section 6 (the paper contract). For each,
  give the option the rebase proposes, the strongest alternative, what each costs, and which failure mode it prevents.
  Then ask Uzair for the decisions W2-5..W2-9 (defaults are in STATE.md section 6). Expect him to push on the design. Keep
  the design doc current as decisions land: write a new dated design doc in `audit/docs/` rather than rewriting the rebase.
  Push back where the evidence disagrees with him.
- Points that need the most care:
  - **the paper contract** (rebase section 6): freeze it before any folder moves, because W1's registry
    (`docs/paper/q1/numbers.json`) will point at `audit/results/rerun_v1/<audit>/certificate.json#/body/findings/[id=K04]/...`;
  - **the validation battery** (V7): how the auditor itself is measured;
  - **V9**: no item is shared between the agents and Causal-Copilot, so any cross-system statement mixes items.

## Step 4: only after Uzair says go, build in bundles
Order (from rebase section 8):
- **C1** the paper contract + V1/V4/V5. It blocks the port.
- **C2** rounds and version comparisons.
- Then **C3** free gap closures, **C4** validation battery, **C5** L3-lite.

How each bundle is built:
- It has its must-show list. Every stored-number comparison must stay within 0.001, and every certificate must verify.
- New files in owned folders are written directly. Edits to existing shared or pinned files go through
  `jobs/patches/w2_NN_*.py` (check the old sha256; refuse twice). Then py_compile, then tests with `--out` outside the
  repo; Uzair repins; `tracker/snapshot.py` last.
- Write the commit message to `docs/commit_msgs/<execution>_cc-research.txt`. The pending one is
  `docs/commit_msgs/w2_audit_cc-research.txt`.
- When the gate is green, write `audit/results/rerun_v1/port_map.json`, per W1's doc section 4 and the rebase section 6.

## Rules that never bend
- No git write operations; Uzair commits and pushes.
- No API spend without Uzair's explicit go: no live LLM runs, no `cc.ps1`, no queue runner. Replay and recorded modes are
  free.
- Never open, print or copy `..\Causal-Copilot\.env` or any key.
- Do not edit:
  - `docs/paper/q1/` (W1);
  - `tracker/`, tickets, `WAVE_STATE.md`, the site (W5);
  - the B5 modules `audit/{adapters,rca,run_adapters,export_cc_stages}.py`;
  - `analysis/`, `score/`, `harness/` (call them, never copy their logic).
- Protocol or contract changes are proposals to W5 until adopted. Write them as a dated doc in `audit/docs/` and tell Uzair
  to carry them to W5.
- Never post in Slack's #causal-discovery. Never move sealed-battery seeds into the DSC 180A folder.
- Honest claims only: typed gaps, intervals, and "exploratory" labels where a threshold was set after the data. No result
  is called done that the files do not show.
