"""Standalone conformance gate; prior release gates are archived in provenance/."""
from ..dev.gates import run as _run
def run(bundle,out,accepted=None,predecessors=(),dependencies=None):
    return _run(bundle,out,dependencies,accepted=accepted,predecessors=predecessors)

if __name__=='__main__':
    import argparse,json,sys
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('bundle');parser.add_argument('--out',required=True)
    args=parser.parse_args();result=run(args.bundle,args.out)
    print(json.dumps({'passed':result['pass'],'scope':result['scope']}))
    sys.exit(0 if result['pass'] else 1)
