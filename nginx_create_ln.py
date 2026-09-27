#!/usr/bin/env python3
"""
Use for Nginx deployment.
After add new file in /etc/nginx/sites-avaliable/,
run this script to create soft link into ../sites-enabled/
"""

import subprocess
from pathlib import Path


def run_and_echo(cmd: str) -> int:
    print("-->", cmd)
    return subprocess.call(cmd, shell=True)


def main():
    pwd = Path(__file__).resolve().parent
    dirname = "sites-avaliable"
    if pwd.name != dirname:
        pwd = pwd.with_name(dirname)
        if not pwd.exists():
            pwd = Path("/etc/nginx/") / dirname
    target = pwd.parent / "sites-enabled"
    count = linked = 0
    for i in pwd.glob("*.*"):
        name = i.name
        if name.endswith((".bak", ".py")):
            continue
        count += 1
        p = target.joinpath(name)
        if not p.exists():
            print(f"creating ln of {name} ...")
            run_and_echo(f"sudo ln -s {i} {p}")
            linked += 1
    if not linked:
        print(f"{count} conf files found, but no one need to create soft link.")


if __name__ == "__main__":
    main()
