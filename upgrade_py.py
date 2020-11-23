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
    from pathlib import Path  # Put it here to compatitable with Python2

    force_upgrade = "-f" in sys.argv or "--force" in sys.argv
    py_version = default_python_version()
    if not force_upgrade:
        tip = 'Python3.8 already installed. Do your want to reinstall? [y/N]'
        if py_version.startswith(TARGET_VERSION):
            run_and_echo("python -V")
            a = input(tip)
            if a.strip().lower() != 'y':
                return
        elif sliently_run("which python3.8").strip():
            run_and_echo("python3.8 -V")
            a = input(tip)
            if a.strip().lower() != 'y':
                return
    folder = Path.home() / "softwares"
    folder.exists() or folder.mkdir()
    url = DOWNLOAD_URL.format(VERSION)
    fname = Path(url).name
    fpath = folder / fname
    if not fpath.exists():
        if run_and_echo("cd {} && wget {}".format(folder, url)) != 0:
            print('Exit! Fail to get file from', url)
            return
    py_folder = folder / fpath.stem.rstrip('.tar')
    if not py_folder.exists():
        if run_and_echo(f"cd {folder} && tar -xf {fname}") != 0:
            return
    install = INSTALL.format("" if py_version.startswith("3") else "alt")
    if run_and_echo(f"cd {py_folder} && {install}") == 0:
        print("Done!")


if __name__ == "__main__":
    if sys.version < "3":
        os.system("python3 " + ' '.join(sys.argv))
    else:
        main()
