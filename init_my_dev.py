#!/usr/bin/env python3.6
"""
Configure python development environment.
Only work for linux that use bash!
"""
import os
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


def main():
    home = Path.home()
    p = home / FS[0]
    if p.exists():
        a = input(f"`{p}` exists. Do you really want to continue?[y/(n)] ")
        if not a.lower().strip().startswith("y"):
            return
    try:
        p = Path(__file__).parent
    except NameErro:
        p = Path(".")
    for fn in FS:
        os.system(f"cp {p / fn} {home}")
    swith_pip_source = p / "pip_conf.py"
    os.system(f"{swith_pip_source.resolve()}")
    # git push auto fill in username and password after input once
    os.system("git config --global credential.helper store")
    # auto complete for command `mg`
    if not Path("/etc/bash_completion.d/django_manage.bash").exists():
        os.system("sudo cp django_manage.bash /etc/bash_completion.d/")
    # Install some useful python modules
    os.system(
        "python3 -m pip install --upgrade --user "
        "pipenv ipython django pylint flake8 white black"
    )
    p = home / ".bashrc"
    if FS[0] not in p.read_text():
        with p.open("a") as f:
            f.write(ACTIVE_ALIASES)
    # add pipenv auto complete to user profile
    a = 'eval "$(pipenv --completion)"'
    ps = home.glob(".*profile")
    for p in ps:
        if not p.name in (".profile", ".bash_profile"):
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
        os.system(". ~/.bashrc")
        print(f"`~/.bashrc` activated")


if __name__ == "__main__":
    main()
