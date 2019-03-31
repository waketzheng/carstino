#!/usr/bin/env python3
import os
import re
from pathlib import Path


def auto_install_expect_if_not_exist():
    """Install expect to auto input password for ssh scripts"""
    if not os.popen("which expect").read():
        if os.popen("which apt").read():
            os.system("sudo apt install -y expect")
        elif os.popen("which yum").read():
            os.system("sudo yum install -y expect")
        elif os.popen("which zyyper").read():
            os.system("sudo zypper in -y expect")
        elif os.popen("which pacman").read():
            os.system("sudo pacman -S expect")


def conf_scripts():
    pa, pb = Path(__file__).parent, Path.home()
    expect_file = ".ssh_server.exp"
    here, there = pa / expect_file, pb / expect_file
    if here.exists() and not there.exists():
        cmd = f"cp {here} {there.parent}"
        os.system(cmd)
        print(cmd)

    for p in pa.glob("*.bash"):
        target = pb / p.stem
        if not target.exists():
            os.system(f"cp {p} {target}")
            print(f"cp: {p} -> {target}")
            content = target.read_text()
            host = re.search(r'@\w+\.\w+.\w+"', content).group().strip('@"')
            user = input(f"User for {host}: ")
            passwd = input(f"password for {host}: ")
            new_txt = content.replace("USER", user).replace("PASSWD", passwd)
            target.write_text(new_txt)
    auto_install_expect_if_not_exist()


if __name__ == "__main__":
    conf_scripts()
    print("Done!")
