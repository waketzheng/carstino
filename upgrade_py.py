#!/usr/bin/env python3
"""
Install latest version Python.
Only work for linux!
And python3 is required.

This script do the following steps:
    1. Download Python xz file from huaweicloud
    2. unzip it to ~/softwares (if folder not found with auto create)
    3. Run this command::
        ./configure --enable-optimizations --enable-loadable-sqlite-extensions\
                && make && sudo make altinstall
"""
import os
import sys
from pathlib import Path

TARGET_VERSION = "3.8"
VERSION = "{}.6".format(TARGET_VERSION)
DOWNLOAD_URL = "https://mirrors.huaweicloud.com/python/{0}/Python-{0}.tar.xz"
# ipython need sqlite3 enable to store history
INSTALL = (
    "./configure --enable-optimizations  --enable-loadable-sqlite-extensions"
    " && make && sudo make {}install"
)


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
    force_upgrade = "-f" in sys.argv or "--force" in sys.argv
    py_version = default_python_version()
    if not force_upgrade:
        if py_version.startswith(TARGET_VERSION):
            run_and_echo("python -V")
            return
        if sliently_run("which python3.8").strip():
            run_and_echo("python3.8 -V")
            return
    folder = Path.home() / "softwares"
    folder.exists() or folder.mkdir()
    url = DOWNLOAD_URL.format(VERSION)
    run_and_echo("cd {} && wget {}".format(folder, url))
    run_and_echo("cd {} && tar -xf {}".format(folder, Path(url).name))
    install = INSTALL.format("" if py_version.startswith("3") else "alt")
    glob = folder.glob("Python-{version}*".format(version=TARGET_VERSION))
    py_folder = [p for p in glob if p.is_dir()][0]
    run_and_echo("cd {} && {}".format(py_folder, install))
    print("Done!")


if __name__ == "__main__":
    main()
