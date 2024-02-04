#!/usr/bin/env python3
import os
import subprocess
import sys

try:
    from typing import Optional  # NOQA:F401
except ImportError:
    pass

"""
Custom install shortcut as i for pip

Usage::
    $ python .pipi.py

"""

TEXT = """
    if sys.argv[1:] and sys.argv[1] == 'i':
        sys.argv[1] = 'install'
"""


def run_and_echo(cmd):
    # type: (str) -> int
    print("--> " + cmd)
    sys.stdout.flush()
    return os.system(cmd)


def capture_output(cmd):
    # type: (str) -> str
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True)
    except (TypeError, AttributeError):  # For python<=3.6
        with os.popen(cmd) as p:
            return p.read().strip()
    else:
        return r.stdout.decode().strip()


def patch_it(filename):
    # type: (str) -> Optional[int]
    with open(filename) as f:
        text = f.read()
    if "install" not in text:
        ss = text.strip().splitlines()
        new_text = "\n".join(ss[:-1] + [TEXT] + ss[-1:])
        try:
            with open(filename, "w") as f:
                f.write(new_text)
        except IOError:
            print("Failed to write lines to {}:\n{}".format(filename, TEXT))
            return 1
        print("i command was configured!\n\nUsage::\n\n    pip i package-name\n")


def main():
    # type: () -> Optional[int]
    pip_file = os.path.join(os.path.dirname(sys.executable), "pip")
    if not os.path.exists(pip_file):
        pip_file = capture_output("which pip")
    args = sys.argv[1:]
    packages = " ".join(args)
    if patch_it(pip_file):
        return 1
    elif not args:
        return run_and_echo("pip install")
    if args:
        cmd = "pip i " + " ".join(args)
        run_and_echo(cmd)
        print("Next time you can use this instead:\n\n  pip i {}\n".format(packages))
        if "pip" in args:
            return patch_it(pip_file)


if __name__ == "__main__":
    sys.exit(main())
