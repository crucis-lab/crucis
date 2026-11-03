"""Validate the exact staged Git tree in isolation before a local commit.

No commit, push, repin or change to the working tree is performed here. The
repository's staged .commit-policy.json supplies commands run in a temporary
checkout. This avoids accidentally validating unstaged fixes or snapshots.
"""
import argparse
import io
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tempfile
import zipfile


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args])


def extract_index(repo, destination):
    tree = git(repo, "write-tree").decode().strip()
    raw = git(repo, "archive", "--format=zip", tree)
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        for entry in archive.infolist():
            path = PurePosixPath(entry.filename)
            if path.is_absolute() or ".." in path.parts or "\\" in entry.filename:
                raise ValueError("Unsafe path in staged tree")
            if (entry.external_attr >> 16) & 0o170000 == 0o120000:
                raise ValueError("Commit gate needs explicit support for staged symlinks")
        archive.extractall(destination)
    return tree


def validate(repo, *, full=True):
    repo = Path(repo).resolve()
    start_head = subprocess.run(["git", "-C", str(repo), "rev-parse", "--verify", "HEAD"],
                                capture_output=True).stdout
    with tempfile.TemporaryDirectory(prefix="milestone-gate-", dir=os.environ.get("MILESTONE_TEMP_DIR")) as scratch:
        # Existing evidence digests require this exact checkout basename.
        checkout = Path(scratch) / repo.name
        checkout.mkdir()
        tree = extract_index(repo, checkout)
        config = json.loads((checkout / ".commit-policy.json").read_text(encoding="utf-8"))
        if config.get("version") != 1:
            raise ValueError("Unsupported commit policy version")
        commands = config["checks"] + (config.get("full_checks", []) if full else [])
        env = os.environ.copy()
        env.update(PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1", VERIFY_NO_CACHE="1")
        # Do not accidentally import the live research checkout during validation.
        env.pop("PYTHONPATH", None)
        env.pop("CAUSAL_AUDIT_DATA_ROOT", None)
        env.pop("CRUCIS_DATA_ROOT", None)
        env["CRUCIS_TEST_TEMP"] = scratch
        env["TMP"] = scratch
        env["TEMP"] = scratch
        for command in commands:
            args = [part.replace("{python}", sys.executable).replace("{scratch}", scratch)
                    for part in command]
            print("commit gate:", " ".join(command), flush=True)
            subprocess.run(args, cwd=checkout, env=env, check=True)
        if tree != git(repo, "write-tree").decode().strip():
            raise RuntimeError("Index changed during validation; validate the new staged tree")
        end_head = subprocess.run(["git", "-C", str(repo), "rev-parse", "--verify", "HEAD"],
                                  capture_output=True).stdout
        if start_head != end_head:
            raise RuntimeError("HEAD changed during validation; inspect the concurrent commit")
        print(json.dumps({"staged_tree": tree, "checks": len(commands), "passed": True}), flush=True)
        return tree


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--quick", action="store_true", help="core checks only; full checks are required before committing")
    args = parser.parse_args(argv)
    try:
        validate(args.repo, full=not args.quick)
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"commit gate failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
