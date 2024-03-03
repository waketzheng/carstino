#!/usr/bin/env python3
import sys
import subprocess
from pathlib import Path

NAME = ".bash_aliases"
SH = "[[ -f ~/{0} ]] && . ~/{0}".format(NAME)
ZSHRC = ".zshrc"


def main() -> int:
    p = Path.home() / ZSHRC
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
        cmd = f"grep -rn {NAME} ~/{ZSHRC}"
        print("-->", cmd)
        return subprocess.run(cmd, shell=True).returncode


if __name__ == "__main__":
    sys.exit(main())
