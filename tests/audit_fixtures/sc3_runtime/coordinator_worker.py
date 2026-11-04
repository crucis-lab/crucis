"""Owned deterministic B06 process-death barrier; no external provider."""
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import test_audit_execution_coordinator as t


def main():
    packet = json.loads(Path(sys.argv[1]).read_bytes())
    barrier = sys.argv[2]
    def fault(point):
        if point == barrier:
            print('READY:' + point, flush=True)
            sys.stdin.readline()
            raise RuntimeError('owned barrier released without termination')
    c, ctx, plan, journal, jctx, _, _ = t.reopen_packet(packet, fault)
    account = t.reference(packet['account'], 'account')
    admitted = c.admit(plan, journal.head(account, jctx).value, ctx, packet['group'])
    if admitted.state != 'completed': raise AssertionError(admitted.issues)
    issued = c.issue(admitted.value, ctx, packet['transmission'])
    raise AssertionError(('barrier not reached', issued.state, issued.issues))


if __name__ == '__main__': main()
