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
import argparse
import os
import sys
import time

try:
    input = raw_input
except NameError:
    pass

VERSION = "3.9.1"
DOWNLOAD_URL = "https://mirrors.huaweicloud.com/python/{0}/Python-{0}.tar.xz"
# ipython need sqlite3 enable to store history
INSTALL = (
    "./configure --enable-optimizations  --enable-loadable-sqlite-extensions"
    " && make && sudo make {}install"
)
DEFAULT_DIR = "~/softwares"

# Only for ubuntu
EXTEND = (
    "build-essential libssl-dev bzip2 libbz2-dev libxml2-dev "
    "libxslt1-dev zlib1g-dev libffi-dev"
)
APPEND = "sudo apt install -y python3-dev"

# To install python2, just run `sudo apt install python2`
SHORTCUTS = {
    "3": VERSION,
    "39": VERSION,
    "38": "3.8.6",
    "37": "3.7.9",
    "36": "3.6.9",
}


def default_python_version():
    return silently_run("python -V").replace("Python ", "")


def silently_run(cmd):
    with os.popen(cmd) as p:
        s = p.read()
    return s


def run_and_echo(cmd):
    print("-->", cmd)
    return os.system(cmd)


def parse_args():
    """parse custom arguments and set default value"""
    parser = argparse.ArgumentParser(description="Install python by source")
    parser.add_argument(
        "-d", "--dir", nargs="?", default=DEFAULT_DIR, help="Where to install"
    )
    parser.add_argument(
        "-v", "--version", nargs="?", default=VERSION, help="Python version"
    )
    parser.add_argument(
        "--dep", action="store_true", help="Install some ubuntu packages"
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Force update (example:3.8.1 -> 3.8.6)",
    )
    parser.add_argument("--alt", action="store_true", help="Want altinstall?")
    return parser.parse_args()


def validated_args():
    args = parse_args()
    # if '.' in args.version:
    #     assert args.version >= '3', 'Only support Python3 install'
    # else:
    #     assert args.version in SHORTCUTS, 'Version should be in ' + str(list(SHORTCUTS.keys()))
    if "." in args.v:
        assert args.v >= "3", "Only support Python3 install"
    elif args.v not in SHORTCUTS:
        raise AssertionError("Version should be in " + repr(list(SHORTCUTS.keys())))
    return args


def main():
    args = validated_args()
    # is_ubuntu = bool(silently_run("which apt"))
    version = args.version
    start = time.time()
    target_version = version.rsplit(".", 1)[0]
    current_version = default_python_version()
    if not args.force_upgrade:
        pyx = "python" + target_version
        tip = "\n{} already installed. ".format(pyx.title())
        if current_version.startswith(target_version):
            run_and_echo("python -V")
            if current_version < version:
                tip += "Do your want to upgrade to {}? [y/N] ".format(version)
            else:
                tip += "Do your want to reinstall? [y/N] "
            a = input(tip)
            if a.strip().lower() != "y":
                sys.exit()
        elif silently_run("which {}".format(pyx)).strip():
            run_and_echo("{} -V".format(pyx))
            a = input(tip + "Do your want to reinstall? [y/N] ")
            if a.strip().lower() != "y":
                sys.exit()
    url = DOWNLOAD_URL.format(version)
    # if system python is py3, replace it, else `make altinstall`
    alt = args.alt or not current_version.startswith("3")
    folder = args.dir
    install_py(folder, url, alt)
    print("Done! Cost:", friendly_time(int(time.time() - start)))


def friendly_time(cost):
    if cost >= 3600:
        return ">= {}h".format(cost // 3600)
    elif cost > 60:
        return "{}m{}s".format(cost // 60, cost % 60)
    return "{} seconds".format(cost)


def home():
    try:
        return os.environ["HOME"]
    except KeyError:
        import pwd

        return pwd.getpwuid(os.getuid()).pw_dir


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
    if run_and_echo("cd {} && {}".format(py_folder, install)) != 0:
        sys.exit()


if __name__ == "__main__":
    if sys.version < "3":
        has_py3 = silently_run("which python3").strip()
        if not has_py3 or silently_run("python3 -V") < "Python 3.6":
            print("Python 3.6+ is required!")
        else:
            os.system("python3 " + " ".join(sys.argv))
    else:
        main()
