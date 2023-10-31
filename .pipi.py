#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path
from typing import Optional

"""
Custom install shortcut as i for pip

Usage::
    $ python .pipi.py

"""

TEXT = """
    if sys.argv[1:] and sys.argv[1] == 'i':
        sys.argv[1] = 'install'
"""


def capture_output(cmd: str) -> str:
    p = subprocess.run(cmd, shell=True, capture_output=True)
    return p.stdout.strip().decode()


def patch_it(p: Path) -> Optional[int]:
    if "install" not in (c := p.read_text()):
        ss = c.strip().splitlines()
        try:
            p.write_text("\n".join(ss[:-1] + [TEXT] + ss[-1:]))
        except PermissionError:
            print(f"Failed to write lines to {p}:\n{TEXT}")
            return 1
        print("i command was configured!\n\nUsage::\n\n    pip i package-name\n")


def main():
    p = Path(sys.executable).parent / "pip"
    if not p.exists():
        p = Path(capture_output("which pip"))
    packages = " ".join(args := sys.argv[1:])
    if patch_it(p):
        return 1
    elif not args:
        print("--> pip install")
        subprocess.run(["pip", "install"])
    if args:
        cmd = "pip i " + " ".join(args)
        print("-->", cmd)
        subprocess.run(cmd, shell=True)
        print(f"Next time you can use this instead:\n\n  pip i {packages}\n")
        if "pip" in args:
            return patch_it(p)


if __name__ == "__main__":
    sys.exit(main())
