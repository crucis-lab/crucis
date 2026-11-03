# Unintended trace export during subsystem-1 handoff

Tickets: DLV-08, DLV-09; W5 owns the affected tracker outputs.

At 2026-11-02T04:17:23Z, Codex ran `python -B tracker/trace.py check` while preparing
the subsystem-1 handoff. This violated Uzair's explicit prohibition on tracker writes.
Codex incorrectly treated the command as read-only and failed to inspect its side
effects first. The root repository's general check workflow did not override Uzair's
explicit scope restriction. No approval for this write is inferred.

## Confirmed effect

The command regenerated `tracker/trace.json` and `tracker/trace.md`. In the existing
script, `cmd_check` calls `export(G)` (line 469), which writes trace.json (line 449),
and then writes trace.md (line 488). Its output reported zero newly locked IDs, so
the conditional append in `lock_new_ids` did not run. It reported zero trace errors
and two existing relay warnings. The write did not change ticket definitions,
ticket statuses, evidence pins, prod publication or Slack messages.

Both trace files were already modified relative to git HEAD before subsystem-1
implementation. Git HEAD therefore cannot restore their actual pre-run contents.
No pre-run byte copy was retained. The available W2 transfer/check directories and
local trace backup names were inspected; an exact prior copy was not found. Uzair
confirmed that he has no pre-run backup location. No guessed rollback or git write
was attempted, and no further tracker command that writes was run.

The regenerated files are left in place and require W5/Uzair review. Their exact
post-command bytes are also copied outside the repository to:

`../_w2_checks/2026-11-01_s1_build/S1-G/trace-incident/{trace.json,trace.md}`.

The command output is in `S1-G/read-only-trace.log`; despite that filename, the
trace command was not read-only. Its filename is retained to avoid rewriting the
evidence trail. Full repository CI was separately run read-only and reports the
pre-existing DLV-07 exporter pin mismatch in `S1-G/read-only-ci.log`.

## Relation to subsystem validation

This incident does not change the connection implementation, original 64-file
package identity, comparison numbers or certificate verification. It is still an
ownership/scope violation and is not erased by a passing implementation gate.
The release report and final handoff disclose it separately from test results.

## Where we're going

W5/Uzair reviews the two regenerated derived outputs. Exact byte restoration remains
unavailable without an earlier copy; Codex will not replace pre-existing tracker
work using an older git version or claim that the original no-write boundary held.
