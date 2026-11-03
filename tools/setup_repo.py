"""Install the repository's local hook configuration in this clone only."""
import os
from pathlib import Path
import stat
import subprocess

ROOT=Path(__file__).resolve().parents[1]
subprocess.run(['git','config','--local','core.hooksPath','tools/hooks'],cwd=ROOT,check=True)
if os.name!='nt':
    hook=ROOT/'tools/hooks/pre-commit'
    hook.chmod(hook.stat().st_mode|stat.S_IXUSR|stat.S_IXGRP|stat.S_IXOTH)
print('Local commit hooks configured: tools/hooks')
