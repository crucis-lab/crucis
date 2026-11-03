---
name: milestone-commit
description: Make an authorized local commit after a coherent research or software milestone, checking the staged files without absorbing another workstream's changes.
---

Use this workflow at completed design decisions, verified implementation bundles,
focused fixes and useful documentation updates, and check for a ready milestone
before ending a development turn. Local commits are authorized by repository
AGENTS.md. A message draft alone does not complete this workflow.

1. At the start of work in a clone, run python -B tools/setup_repo.py to ensure
   the local validation hook is configured. Then inspect HEAD, status and the index before editing; distinguish pre-existing
   work from this milestone. Record the intended files and ticket IDs.
2. Review the diff and stage explicit paths or hunks. If someone else has staged
   files, preserve them and resolve ownership before committing; never reset their
   index, stage the whole checkout, or include unrelated changes.
3. Run relevant tests. For research evidence changes, deliberately review any pin
   changes, use tracker/verify.py for repins, and regenerate the snapshot last.
   Never repin merely to suppress an unexplained mismatch.
4. Run `python -B tools/commit_gate.py` with a working interpreter. It exports the
   index to a temporary directory and validates exactly the bytes to be committed.
   All configured checks must pass. The pre-commit hook repeats this gate.
5. Commit with an informative subject and ticket/validation details. Use a message
   file with actual newlines. Recheck HEAD, the committed file list and status;
   report the commit hash and any remaining unrelated work.

Do not push, merge, tag a release, publish packages or sites, rewrite history,
skip hooks, or change repository visibility without authorization for that action.
Keep failed or incomplete checks visible. When a commit is blocked, record the
specific blocker, the intended files and the message; continue independent work.

The initial extraction hold is lifted only after the separation receipt passes.
Thereafter, commit each ready local milestone automatically; network publication
is tracked separately and does not block local commits.
