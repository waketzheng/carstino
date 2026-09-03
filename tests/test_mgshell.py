from __future__ import annotations

import builtins
import imp
import platform
import shutil
import sys
from pathlib import Path

import pytest


def test_win32(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(platform, "system", lambda: "Windows")
    file = Path(__file__).parent.parent / ".mg.py"
    mg = imp.load_source("mg", file.as_posix())
    cmd = mg.uvx_ipython(is_windows=True)
    assert cmd == "uvx --with ensure-import ipython"
    py = Path(".venv", "Scripts", "python.exe")
    py.parent.mkdir(parents=True)
    py.touch()
    cmd = mg.uvx_ipython(is_windows=True)
    assert cmd == "uvx --with ensure-import --no-python-downloads --python 3.12 ipython"
    py.with_stem("python3.10").touch()
    cmd = mg.uvx_ipython(is_windows=True)
    assert cmd == "uvx --with ensure-import --no-python-downloads --python 3.10 ipython"
    monkeypatch.setattr(mg, "run_shell", lambda x: x)
    monkeypatch.setattr(builtins, "input", lambda x: "")
    monkeypatch.setattr(sys, "executable", py.resolve().as_posix())
    cmd = mg.MgShell.run_in_venv(
        offline=False, prefer_uvx=True, is_windows=True, verbose=False
    )
    expected = "uvx --with ensure-import --no-python-downloads --python .venv/Scripts/python.exe ipython"
    assert cmd == expected
    cmd = mg.MgShell.ipython_not_installed([])
    assert cmd == expected
    monkeypatch.setattr(shutil, "which", lambda x: None if x == "ipython" else x)
    with pytest.raises(SystemExit):
        mg.MgShell.ipython_not_installed(["--no-uvx"])
    monkeypatch.setattr(shutil, "which", lambda x: x)
    cmd = mg.MgShell.ipython_not_installed(["--no-uvx"])
    assert cmd == "ipython"
