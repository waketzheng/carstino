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
DEFAULT_DIR = "~/softwares"

# To install python2, just run `sudo apt install python2`
SHORTCUTS = {
    "3": "3.9.1",
    "39": "3.9.1",
    "38": "3.8.6",
    "37": "3.7.9",
    "36": "3.6.9",
}


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
    sys_argv = sys.argv[1:]
    print(f'{sys_argv = }')
    for idx, arg in enumerate(sys_argv):
        # todo: use argparser instead
        print(f'{arg = }, {arg == "-v"}, {arg.startswith("--version")}')
        if arg == "-v":
            v = sys_argv[idx + 1]
            version = SHORTCUTS.get(v, v)
            target_version = version.rsplit(".", 1)[0]
            break
        if arg.startswith("--version="):
            v = arg.replace("--version=", "")
            version = SHORTCUTS.get(v, v)
            target_version = version.rsplit(".", 1)[0]
            break
    else:
        target_version, version = TARGET_VERSION, VERSION
    print(f'{target_version = }, {version = }')
    force_upgrade = "-f" in sys_argv or "--force" in sys_argv
    py_version = default_python_version()
    if not force_upgrade:
        pyx = "python" + target_version
        tip = "\n{} already installed. ".format(pyx.title())
        if py_version.startswith(target_version):
            run_and_echo("python -V")
            if py_version < version:
                tip += "Do your want to upgrade to {}? [y/N] ".format(version)
            else:
                tip += "Do your want to reinstall? [y/N] "
            a = input(tip)
            if a.strip().lower() != "y":
                return
        elif sliently_run("which {}".format(pyx)).strip():
            run_and_echo("{} -V".format(pyx))
            a = input(tip + "Do your want to reinstall? [y/N] ")
            if a.strip().lower() != "y":
                return
    url = DOWNLOAD_URL.format(version)
    # if system python is py3, replace it, else `make altinstall`
    alt = not py_version.startswith("3") or "--alt" in sys_argv
    folder = DEFAULT_DIR
    for idx, arg in enumerate(sys_argv):
        # todo: use argparser instead
        if arg == "-d":
            folder = sys_argv[idx + 1]
            break
        if arg.startswith("--dir="):
            folder = arg.replace("--dir=", "")
            break
    install_py(folder, url, alt)


def install_py(folder, url, alt):
    from pathlib import Path  # Put it here to compatitable with Python2

    if isinstance(folder, str):
        if not folder.startswith("/"):
            folder = folder.replace("~", str(Path.home()))
        folder = Path(folder)
    folder.exists() or folder.mkdir()
    fname = Path(url).name
    fpath = folder / fname
    if not fpath.exists():
        if run_and_echo("cd {} && wget {}".format(folder, url)) != 0:
            print("Exit! Fail to get file from", url)
            return
    py_folder = folder / fpath.stem.rstrip(".tar")
    if not py_folder.exists():
        cmd = "cd {} && tar -xf {}".format(folder, fname)
        if run_and_echo(cmd) != 0:
            return
    install = INSTALL.format("alt" if alt else "")
    if run_and_echo("cd {} && {}".format(py_folder, install)) == 0:
        print("Done!")


if __name__ == "__main__":
    if sys.version < "3":
        has_py3 = sliently_run("which python3").strip()
        if not has_py3 or sliently_run("python3 -V") < "Python 3.6":
            print("Python 3.6+ is required!")
        else:
            os.system("python3 " + " ".join(sys.argv))
    else:
        main()
