"""python -m crucis <command>   (protocol v1; DLV-08, DLV-09, DLV-10)

  systems                          adapters and their declared capabilities
  battery ID [--manifest FILE]     a battery's identity and hash (ca-ab06, q1s2, ca-semantic, ca-formula)
  audit NAME --out DIR             one standard audit (run.AUDITS) from recorded runs -> report.json, report.md, certificate
  verify CERT                      recompute a certificate's every number from its raw files
  rerun --out DIR [--bundle B1,..] the existing audits through the package: comparison table + one report per system
No command spends API credit: live and replay runs are run-sheet jobs.
"""
import argparse
import json
import sys
from pathlib import Path


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m crucis", description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("systems")
    b = sub.add_parser("battery")
    b.add_argument("id")
    b.add_argument("--manifest", default=None)
    a = sub.add_parser("audit")
    a.add_argument("name")
    a.add_argument("--out", required=True)
    v = sub.add_parser("verify")
    v.add_argument("cert")
    r = sub.add_parser("rerun")
    r.add_argument("--out", required=True)
    r.add_argument("--bundle", default="B1,B2,B3")
    r.add_argument("--no-reports", action="store_true")
    s = sub.add_parser("sealed-check")
    s.add_argument("--reads", default=None)
    s.add_argument("--system", required=True)
    s.add_argument("--version", required=True)
    s.add_argument("--battery-hash", required=True)
    args = ap.parse_args(argv)

    if args.cmd == "systems":
        from .core import adapter as A
        for n in A.names():
            print(n, json.dumps(A.get(n).capabilities.to_json()))
        return 0
    if args.cmd == "battery":
        from .core import battery as B
        bt = B.get(args.id)
        print(json.dumps({"id": bt.battery_id, "version": bt.version, "visibility": bt.visibility, "items": len(bt.items),
                          "clusters": len(bt.clusters()), "hash": bt.hash()}, indent=1))
        if args.manifest:
            Path(args.manifest).write_text(json.dumps(bt.manifest(True), indent=1, sort_keys=True), encoding="utf-8")
        return 0
    if args.cmd == "audit":
        from . import run as RN
        from .report import build
        res = RN.audit(RN.AUDITS[args.name], args.name)
        out = build.write(res, args.out, "python -m crucis audit %s --out %s" % (args.name, args.out))
        print(json.dumps(out, indent=1))
        return 0
    if args.cmd == "verify":
        from . import run as RN
        from .report import certificate as CERT
        cert = json.loads(Path(args.cert).read_text(encoding="utf-8"))
        res = CERT.verify(cert, lambda name, spec: RN.audit(RN.spec_from_json(spec), name))
        print(json.dumps({k: v for k, v in res.items() if k != "numbers_not_in_certificate"}, indent=1))
        return 0 if res["pass"] else 1
    if args.cmd == "rerun":
        from .rerun import existing as E
        return E.main(args.out, tuple(args.bundle.split(",")), reports=not args.no_reports)
    if args.cmd == "sealed-check":
        from .core import sealed
        ok, why = sealed.read_allowed(args.system, args.version, args.battery_hash, args.reads)
        print(json.dumps({"allowed": ok, "why": why}))
        return 0 if ok else 1
    return 2


if __name__ == "__main__":
    sys.exit(main())
