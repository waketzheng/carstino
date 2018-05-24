#!/usr/bin/env python3.6
"""
Configure python development environment.
Only work for linux that use bash!
"""
import os
import re
from pathlib import Path


FS = [
    ".bash_aliases",
    ".pipenv_install_while_lock_at_another_process.py",
    ".switch_source_pipenv.py",
    ".mg.py",
    ".vimrc",
]

ACTIVE_ALIASES = """
if [ -f ~/.bash_aliases ]; then
    . ~/.bash_aliases
fi
"""
PACKAGES = "pipenv ipython django pylint flake8 white black"


def main():
    home = Path.home()
    aliases = home / FS[0]
    if aliases.exists():
        a = input(f"`{aliases}` exists. Continue and replace it?[y/(n)] ")
        if not a.lower().strip().startswith("y"):
            return
    try:
        repo = Path(__file__).parent.resolve()
    except NameError:
        repo = Path(".").resolve()
    for fn in FS:
        os.system(f"cp {repo / fn} {home}")
    s = aliases.read_text()
    ss = re.sub(r'(rstrip=")(.*)"', rf'\1{repo/"rstrip.py"}"', s)
    if s != ss:
        aliases.write_text(ss)
    swith_pip_source = repo / "pip_conf.py"
    os.system(f"{swith_pip_source}")
    # git push auto fill in username and password after input once
    os.system("git config --global credential.helper store")
    # auto complete for command `mg`
    if not Path("/etc/bash_completion.d/django_manage.bash").exists():
        os.system("sudo cp django_manage.bash /etc/bash_completion.d/")
    # Install some useful python modules
    os.system(f"python3 -m pip install --upgrade --user {PACKAGES}")
    bashrc = home / ".bashrc"
    if FS[0] not in bashrc.read_text():
        with bashrc.open("a") as f:
            f.write(ACTIVE_ALIASES)
    # add pipenv auto complete to user profile
    a = 'eval "$(pipenv --completion)"'
    ps = home.glob(".*profile")
    for p in ps:
        if p.name not in (".profile", ".bash_profile"):
            continue
        if a in p.read_text():
            print(f"`{a}` already in {p}")
            continue
        cmd = f"echo '{a}'>>{p}"
        os.system(cmd)
        print(cmd)
        os.system(f"bash {p}")
        print(f"`{p}` activated")
        break
    else:
        os.system(f". {bashrc}")
        print(f"`{bashrc}` activated")
    if os.system("pipenv --version") != 0:
        os.system("sudo cp -r ~/.pip /home/root/")
        os.system(f"sudo pip3 install -U {PACKAGES}")


if __name__ == "__main__":
    main()
