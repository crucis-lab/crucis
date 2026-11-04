"""B00 supplied deterministic native-protocol fixture; no causal correctness claim.

DLV-08/09. Deliberately fixed before the S3 orchestration implementation.
"""

OUTPUT = b'{"order":["v1","v2","v0"],"edges":[["v1","v2"]]}\n'

def discover(data):
    if data != b'A,B,C\n0,1,0\n1,0,1\n':
        raise ValueError('fixture received different input')
    return OUTPUT

def restore(state):
    if set(state) != {'model', 'optimizer'}:
        raise ValueError('fixture requires explicit model and optimizer state')
    return dict(state)
