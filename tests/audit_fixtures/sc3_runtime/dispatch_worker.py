"""Owned B07 coordinator subprocess. Real provider belongs to supervisor."""
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import dispatch_case as case


def main():
    packet = json.loads(Path(sys.argv[1]).read_bytes())
    # Actual runtime bootstrap travels separately from the stored evidence packet.
    auth = json.loads(sys.stdin.readline())
    if set(auth) != {'token'}: raise ValueError('actual supervisor bootstrap required')
    def fault(point):
        if point == 'before_issue_reply':
            print('READY:before_issue_reply', flush=True)
            sys.stdin.readline()
            raise RuntimeError('barrier released without termination')
    env, plan = case.reopen(packet, auth['token'], fault)
    head = env.journal.head(env.account, env.jctx)
    admitted = env.coordinator.admit(plan, head.value, env.context, packet['group'])
    if admitted.state != 'completed': raise AssertionError(admitted.issues)
    result = env.issue(admitted.value, transmission=packet['transmission'])
    raise AssertionError(('required barrier missing', result.state, result.issues))


if __name__ == '__main__': main()
