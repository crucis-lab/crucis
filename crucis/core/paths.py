"""Explicit evidence locations; importing Crucis never adds research code paths."""
import os
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
ROOT = Path(os.environ.get("CRUCIS_DATA_ROOT", Path.cwd())).resolve()
ANALYSIS = ROOT / "analysis"
HARNESS = ROOT / "harness"


def import_paths():
    """Compatibility no-op: all required Python helpers are package-internal."""


def rel(path):
    """Path relative to the repository root, with forward slashes (what records and certificates store)."""
    p = Path(path).resolve()
    try:
        return p.relative_to(ROOT).as_posix()
    except ValueError:
        return p.as_posix()


def research_path(p):
    """Plans and capped run lists name container paths (/research/... or research:...); map them to this checkout."""
    s = str(p)
    for pre in ("/research/", "research:"):
        if s.startswith(pre):
            return ROOT / s[len(pre):]
    return Path(s)
