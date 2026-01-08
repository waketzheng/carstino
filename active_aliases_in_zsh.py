#!/usr/bin/env python3
import contextlib
import shlex
import subprocess
import sys
from pathlib import Path

with contextlib.suppress(ImportError):
    from rich import print  # ty:ignore[unresolved-import]

NAME = ".bash_aliases"
SH = "[[ -f ~/{0} ]] && . ~/{0}".format(NAME)
ZSHRC = ".zshrc"


def main() -> int:
    home = Path.home()
    p = home / ZSHRC
    s = p.read_text()
    if NAME not in s:
        s += "\n" + SH + "\n"
        p.write_text(s)
        print(f"{ZSHRC} updated!")
        print("\n" + "+ \n" + f"+ {SH}\n" + "+ \n")
        print(f"To activate aliases immediately: source ~/{ZSHRC}")
        return 1
    else:
        print("Already in, skip.")
        cmd = f'grep -rn "{NAME}" "{home / ZSHRC}"'
        print("-->", cmd)
        return subprocess.run(shlex.split(cmd)).returncode


if __name__ == "__main__":
    sys.exit(main())
