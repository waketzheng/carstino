#!/usr/bin/env python3
"""
Script for pyenv to install python from huaweicloud mirror.
Require: python3.7+

Usage::
    cp pyinstall.py ~/.pyinstall.py
    alias pyinstall="~/.pyinstall.py"
    pyinstall 3.10.8
    pyinstall 3.11.0rc2

Or just::
    python pyinstall.py 3.11.5
"""

import functools
import os
import re
import subprocess
import sys
import time
from pathlib import Path

HOST = os.getenv("PYTHON_MIRROR", "https://repo.huaweicloud.com/python/")
DOWNLOAD_URL = HOST + "{}/Python-{}.tar.xz"


def build_url(version: str) -> str:
    slim_version = ".".join(re.findall(r"\d+", version)[:3])
    return DOWNLOAD_URL.format(slim_version, version)


def humanize(seconds: float) -> str:
    if seconds < 60:
        return "{} seconds".format(round(seconds, 1))
    m = int(seconds // 60)
    s = int(seconds % 60)
    if m < 60:
        return "{}m{}s".format(m, s)
    h = m // 60
    m = m % 60
    return "{}h{}m{}s".format(h, m, s)


def say_cost(func):
    @functools.wraps(func)
    def deco(*args, **kwargs):
        start = time.time()
        res = func(*args, **kwargs)
        end = time.time()
        cost = end - start
        print("Function `{}` cost: {}".format(func.__name__, humanize(cost)))
        return res

    return deco


@say_cost
def pyinstall(version: str) -> subprocess.CompletedProcess[str]:
    cache_dir = Path.home() / ".pyenv" / "cache"
    cmd = "cd {} && (".format(cache_dir)
    url = build_url(version)
    filepath = cache_dir / Path(url).name
    if filepath.exists():
        print(filepath, "exists, skip wget")
    else:
        if not cache_dir.exists():
            cache_dir.mkdir(parents=True)
        cmd += "wget {}&&".format(url)
    cmd += "pyenv install {0};cd -)".format(version)
    print("Start running ...")
    print("-->", cmd)
    return subprocess.run(cmd, shell=True, text=True)


def main() -> int:
    version = sys.argv[1:] and sys.argv[1]
    if version:
        if version.count(".") > 1:
            return pyinstall(version).returncode
        else:
            cmd = "pyenv install " + version
    else:
        cmd = "pyenv --help"
    return os.system(cmd)


if __name__ == "__main__":
    sys.exit(main())
