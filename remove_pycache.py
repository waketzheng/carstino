#!/usr/bin/env python3
import shlex
import subprocess

try:
    from pathlib import Path
except ImportError:
    from pathlib2 import Path  # ty:ignore[unresolved-import]


def remove_one(i):
    cmd = "rm -rf " + str(i)
    print("--> " + cmd)
    subprocess.call(shlex.split(cmd))
    print(i, "removed!")


for i in Path().rglob("__pycache__"):
    if i.exists():
        remove_one(i)
