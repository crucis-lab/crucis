"""Refuse to let a credential or an oversized file into git.

  python tools/secret_scan.py               scan every file git would track (git ls-files, else a walk that honours .gitignore roots)
  python tools/secret_scan.py --staged      scan only staged files (the pre-commit hook)
  python tools/secret_scan.py FILE ...      scan the named files

Exit 1 on any finding. Findings print the file and line number, never the matched text.
Patterns cover OpenAI, Anthropic, GitHub, Slack, AWS and Google keys, private-key blocks, Jupyter tokens in URLs,
and an OPENAI_API_KEY= / ANTHROPIC_API_KEY= line with a value. Files over 50 MB are refused (GitHub's soft limit).
"""
import os, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAX_BYTES = 50 * 1024 * 1024
PATTERNS = [
    ("openai key", re.compile(rb"sk-(?:proj-|svcacct-|admin-)?[A-Za-z0-9_-]{32,}")),
    ("anthropic key", re.compile(rb"sk-ant-[A-Za-z0-9_-]{20,}")),
    ("github token", re.compile(rb"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}")),
    ("slack token", re.compile(rb"\bxox[abprs]-[0-9A-Za-z-]{10,}")),
    ("aws key id", re.compile(rb"\bAKIA[0-9A-Z]{16}\b")),
    ("google api key", re.compile(rb"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("private key block", re.compile(rb"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("jupyter token", re.compile(rb"[?&]token=[0-9a-f]{32,}")),
    ("api key assignment", re.compile(rb"(?:OPENAI|ANTHROPIC|AZURE_OPENAI|HF|HUGGINGFACE)_(?:API_)?(?:KEY|TOKEN)\s*[=:]\s*['\"]?[A-Za-z0-9_-]{16,}")),
]
EXCLUDED_ROOTS = ("external/", "runs/", "jobs/transfer/", "queue/")
SKIP_SUFFIX = (".png", ".jpg", ".jpeg", ".gif", ".pdf", ".npz", ".npy", ".pkl", ".gz", ".tar")


def tracked_files():
    try:
        out = subprocess.run(["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"], cwd=ROOT,
                             capture_output=True, check=True).stdout
        return [ROOT / p.decode() for p in out.split(b"\0") if p]
    except (OSError, subprocess.CalledProcessError):
        files = []
        for dp, dn, fn in os.walk(ROOT):
            rel = os.path.relpath(dp, ROOT).replace(os.sep, "/") + "/"
            dn[:] = [d for d in dn if d not in (".git", "__pycache__") and not (rel + d + "/").lstrip("./").startswith(EXCLUDED_ROOTS)]
            files += [Path(dp) / f for f in fn]
        return files


def staged_files():
    out = subprocess.run(["git", "diff", "--cached", "--name-only", "-z", "--diff-filter=ACMR"], cwd=ROOT,
                         capture_output=True, check=True).stdout
    return [ROOT / p.decode() for p in out.split(b"\0") if p]


def scan(paths):
    bad = []
    for p in paths:
        if not p.is_file():
            continue
        rel = p.relative_to(ROOT).as_posix()
        size = p.stat().st_size
        if size > MAX_BYTES:
            bad.append((rel, 0, "file is %.1f MB (limit 50 MB); list it in manifests/excluded instead" % (size / 1e6)))
            continue
        if rel.endswith(SKIP_SUFFIX):
            continue
        data = p.read_bytes()
        for name, rx in PATTERNS:
            for m in rx.finditer(data):
                line = data.count(b"\n", 0, m.start()) + 1
                bad.append((rel, line, name))
    return bad


def main():
    args = sys.argv[1:]
    if args == ["--staged"]:
        paths = staged_files()
    elif args:
        paths = [Path(a).resolve() for a in args]
    else:
        paths = tracked_files()
    bad = scan(paths)
    for rel, line, what in bad:
        print("SECRET-SCAN %s:%d  %s" % (rel, line, what))
    print("secret scan: %d files, %d findings" % (len(paths), len(bad)))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
