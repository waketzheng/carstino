#!/usr/bin/env python3
from pathlib import Path

SH = "[[ -f ~/.bash_aliases ]] && . ~/.bash_aliases"
ZSHRC = ".zshrc"


def main():
    p = Path.home() / ZSHRC
    s = p.read_text()
    if SH not in s:
        s += "\n" + SH + "\n"
        p.write_text(s)
        print(f"{ZSHRC} updated!")
        print("\n" + "+ \n" + f"+ {SH}\n" + "+ \n")
    else:
        print("Already in, skip.")


if __name__ == "__main__":
    main()
