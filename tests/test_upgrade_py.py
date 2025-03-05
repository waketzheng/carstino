from __future__ import annotations

import platform
import shlex
import subprocess
from pathlib import Path


def run_by_subprocess(
    cmd: str, cwd: Path | None = None
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        shlex.split(cmd),
        cwd=cwd,
        capture_output=True,
        encoding="utf-8",
    )


def test_upgrade_py():
    r = run_by_subprocess("python upgrade_py.py --dry --no-input")
    if platform.system() == "Darwin":
        assert r.returncode == 1
        assert "brew" in r.stdout
    else:
        assert r.returncode == 0
