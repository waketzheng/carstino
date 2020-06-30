#!/usr/bin/env python3
"""
Install latest version Python.
Only work for linux!
And python3.6+ is required.
"""
import os
from pathlib import Path

TARGET_VERSION = "3.8"
TAR_URL = 'https://mirrors.huaweicloud.com/python/3.8.3/Python-3.8.3.tar.xz'
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
    target = 'Python' + TARGET_VERSION
    tip = f'{target} already installed. Do your want to reinstall? [y/N]'
    if py_version.startswith(TARGET_VERSION):
        run_and_echo("python -V")
        a = input(tip)
        if a.strip().lower() != 'y':
            return
    elif sliently_run(f"which {target}").strip():
        run_and_echo(f"{target} -V")
        a = input(tip)
        if a.strip().lower() != 'y':
            return
    sudo = f'sudo echo {target} will be installed, it may take several minutes'
    run_and_echo(sudo)
    folder = Path.home() / "softwares"
    folder.exists() or folder.mkdir()
    fname = Path(TAR_URL).name
    fpath = folder / fname
    if not fpath.exists():
        if run_and_echo(f"cd {folder} && wget {TAR_URL}") != 0:
            return
    py_folder = folder / fpath.stem.rstrip('.tar')
    if not py_folder.exists():
        if run_and_echo(f"cd {folder} && tar -xf {fname}") != 0:
            return
    install = INSTALL.format("" if py_version.startswith("3") else "alt")
    if run_and_echo(f"cd {py_folder} && {install}") == 0:
        print("Done!")


if __name__ == "__main__":
    main()
