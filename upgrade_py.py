#!/usr/bin/env python3
"""
Install latest version Python.
Only work for linux!
And python3.6+ is required.
"""
import os
from pathlib import Path

TARGET_VERSION = "3.8"
DOWNLOAD_URL = "https://www.shequyi.fun/media/python.xz"
INSTALL = "./configure --enable-optimizations && make && sudo make {}install"


def default_python_version():
    return sliently_run("python -V").replace("Python ", "")


def sliently_run(cmd):
    with os.popen(cmd) as p:
        s = p.read()
    return s


def run_and_echo(cmd):
    print("-->", cmd)
    return os.system(cmd)


def main():
    py_version = default_python_version()
    if py_version.startswith(TARGET_VERSION):
        run_and_echo("python -V")
        return
    if sliently_run("which python3.8").strip():
        run_and_echo("python3.8 -V")
        return
    folder = Path.home() / "softwares"
    folder.exists() or folder.mkdir()
    run_and_echo(f"cd {folder} && wget {DOWNLOAD_URL}")
    run_and_echo(f"cd {folder} && tar -xf {Path(DOWNLOAD_URL).name}")
    install = INSTALL.format("" if py_version.startswith("3") else "alt")
    glob = folder.glob(f"Python-{TARGET_VERSION}*")
    py_folder = [p for p in glob if p.is_dir()][0]
    run_and_echo(f"cd {py_folder} && {install}")
    print("Done!")


if __name__ == "__main__":
    main()
