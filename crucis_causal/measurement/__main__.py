"""Offline inspection and planning for bounded measurement snapshots."""

import argparse
import json
from pathlib import Path

from crucis_causal.execution.api import supplied_read
from crucis_causal.execution.codec import loads
from crucis_causal.execution.model import ExecutionError

from .codec import VERSION, Limits, WireError, inspect
from .planning import ProcedureDescriptor, Registry, plan
from .resolution import ResolutionError, resolve


def _bytes(path, maximum):
    with Path(path).open("rb") as source:
        data = source.read(maximum + 1)
    if len(data) > maximum:
        raise WireError("supplied_file_limit")
    return data


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    inspection = commands.add_parser("inspect", help="Inspect exact canonical snapshot bytes")
    inspection.add_argument("snapshot")
    planning = commands.add_parser("plan", help="Prepare one selected plan from explicit inputs")
    planning.add_argument("snapshot")
    planning.add_argument("plan_id")
    planning.add_argument("--dependency", action="append", default=[], metavar="PACKAGE_ID=FILE")
    planning.add_argument("--descriptor", action="append", default=[], metavar="FILE",
                          help="Explicit procedure declaration for metadata-only planning")
    args = parser.parse_args(argv)
    limits = Limits()
    try:
        snapshot = inspect(_bytes(args.snapshot, limits.snapshot_bytes), limits)
        if args.command == "inspect":
            package = snapshot.package
            report = {"state": "valid_wire", "account_id": snapshot.account_id,
                      "snapshot_id": snapshot.snapshot_id, "sha256": snapshot.digest,
                      "records": len(package["records"]), "dependencies": len(package["dependencies"])}
        else:
            if len(args.dependency) > limits.external_snapshots or len(args.descriptor) > limits.external_snapshots:
                raise WireError("supplied_input_limit")
            supplied = {}
            remaining = limits.closure_bytes - len(snapshot.source_bytes)
            for option in args.dependency:
                identity, separator, name = option.partition("=")
                if not identity or not separator or not name or identity in supplied:
                    raise WireError("dependency_argument")
                raw = _bytes(name, min(limits.snapshot_bytes, remaining))
                supplied[identity] = raw
                remaining -= len(raw)
            descriptors = []
            for name in args.descriptor:
                raw = _bytes(name, min(limits.snapshot_bytes, remaining))
                remaining -= len(raw)
                try:
                    entry = loads(raw, limits.execution_limits())
                except ExecutionError as exc:
                    raise WireError("descriptor_wire") from exc
                if not isinstance(entry, dict) or set(entry) != {
                    "contract", "implementation_sha256", "slots", "output_roles",
                }:
                    raise WireError("descriptor_fields")
                descriptors.append(ProcedureDescriptor.from_declaration(
                    entry["contract"], entry["implementation_sha256"], entry["slots"],
                    entry["output_roles"],
                ))
            cap = supplied_read({snapshot.snapshot_id, *supplied})
            view = resolve(snapshot, supplied, cap, limits)
            selected = {"ref_kind": "local", "target_id": args.plan_id,
                        "expected_contract": {"name": "s4.plan", "version": VERSION}}
            result = plan(selected, view, Registry(descriptors), limits)
            report = {"state": result.state, "basis_digest": result.basis_digest,
                      "ready": [item.key for item in result.outputs],
                      "held": [{"key": item.key, "code": item.issue.code} for item in result.held],
                      "issues": [item.code for item in result.issues], "work_performed": False}
        print(json.dumps(report, sort_keys=True))
        return 0
    except (WireError, ResolutionError) as exc:
        code = exc.code if isinstance(exc, WireError) else exc.issue.code
        print(json.dumps({"state": "rejected", "code": code}))
        return 1
    except (OSError, ValueError, KeyError, TypeError, RecursionError):
        print(json.dumps({"state": "rejected", "code": "s4.supplied_input_invalid"}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
