#!/usr/bin/env python3
"""
Configure python development environment.
Only work for linux that use bash!
And python3.6+ is required.
"""
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional

FILES = ALIAS_FILE, *_ = [
    ".bash_aliases",
    ".mg.py",
    ".vimrc",
    ".lint.sh",
]

PACKAGES = "ipython ruff black isort mypy"


def get_cmd_result(cmd: str) -> str:
    ret = subprocess.run(cmd, shell=True, capture_output=True)
    return ret.stdout.decode().strip()


def run_cmd(command: str) -> int:
    print("-->", command)
    return subprocess.run(command, shell=True).returncode


def get_shell() -> str:
    return Path(get_cmd_result("echo $SHELL")).name


def set_alias_for_git(home: Path) -> None:
    config = home / ".gitconfig"
    if not config.exists():
        _git_unstage()
        _git_dog()
    else:
        content = config.read_bytes()
        if b"unstage" not in content:
            _git_unstage()
        if b"dog" not in content:
            _git_dog()


def _git_unstage():
    run_cmd("git config --global alias.unstage 'reset HEAD'")


def _git_dog():
    fmt = (
        "%C(bold blue)%h%C(reset) - "
        "%C(bold green)(%ar)%C(reset) "
        "%C(white)%s%C(reset) %C(dim white)- "
        "%an%C(reset)%C(bold yellow)%d%C(reset)"
    )
    dog = f"log --graph --abbrev-commit --decorate --format=format:{fmt!r} --all"
    run_cmd("git config --global alias.dog {}".format(repr(dog)))


def configure_aliases(rc: Path, txt: Optional[str] = None) -> None:
    if txt is None:
        txt = rc.read_text()
    if ALIAS_FILE not in txt:
        with rc.open("a") as fp:
            fp.write("\n[[ -f ~/{0} ]] && . ~/{0}".format(ALIAS_FILE))
    # change nvm node mirrors
    if "--nvm" in sys.argv:
        nvm = "export NVM_NODEJS_ORG_MIRROR=https://repo.huaweicloud.com/nodejs/"
        if nvm not in txt:
            with rc.open("a") as fp:
                fp.write(f"\n# For nvm\n{nvm}\n")


def configure_path(rc: Path, txt: Optional[str] = None) -> None:
    if txt is None:
        txt = rc.read_text()
    if "/.local" not in txt:
        line = "export PATH=$HOME/.local/bin:$PATH"
        with rc.open("a") as fp:
            fp.write(f"\n{line}\n")


def get_dirpath() -> Path:
    try:
        return Path(__file__).parent.resolve()
    except NameError:
        return Path(".").resolve()


def update_aliases(repo: Path, aliases_path: Path, home) -> str:
    s = aliases_path.read_text()
    ss = re.sub(r'(rstrip|prettify)="(.*)"', rf'\1="{repo}/\1.py"', s)
    ss = re.sub(r'(httpa)="(.*)"', rf'\1="{repo}/\1.sh"', s)
    if run_cmd("which vi") and "alias vi=" not in get_cmd_result("alias"):
        ss += "alias vi=vim\n"
    if s != ss:
        aliases_path.write_text(ss)
    set_alias_for_git(home)
    return ss


def get_rc_file(home) -> Path:
    names = [".zshrc", ".bashrc", ".profile", ".zprofile", ".bash_profile"]
    for name in names:
        rc = home / name
        if rc.exists():
            break
    else:
        raise Exception(f"Startup file not found, including {names!r}")
    return rc


def init_pip_source(home: Path, repo: Path) -> None:
    swith_pip_source = repo / "pip_conf.py"
    p = home.joinpath(".config/pip/pip.conf")
    if p.exists():
        print("pip source already config as follows:\n\n")
        print(p.read_bytes().decode())
        tip = f"\nDo you want to rerun ./{swith_pip_source.name}? [y/N] "
        if input(tip).lower() == "y":
            run_cmd(f"{swith_pip_source}")
    else:
        run_cmd(f"{swith_pip_source}")


def main():
    home = Path.home()
    aliases_path = home / ALIAS_FILE
    if aliases_path.exists():
        a = input(f"`{aliases_path}` exists. Continue and replace it?[y/(n)] ")
        if not a.lower().strip().startswith("y"):
            return
    run_init(home, aliases_path)


def run_init(home, aliases_path):
    repo = get_dirpath()
    init_pip_source(home, repo)
    for fn in FILES:
        run_cmd(f"cp {repo / fn} {home}")
    txt = update_aliases(repo, aliases_path, home)
    # activate aliases at .bashrc or .zshrc ...
    rc = get_rc_file(home)
    configure_aliases(rc, txt)
    # Install some useful python modules
    if run_cmd(f"python3 -m pip install --upgrade --user {PACKAGES}") != 0:
        if run_cmd(f"sudo pip3 install -U {PACKAGES}") != 0:
            print("Please install python3-pip and then rerun this script.")
            sys.exit(1)
    # Activate installed python package scripts, such as: ipython, ruff
    configure_path(rc, txt)
    # Reactive rc file
    sh = "zsh" if "zsh" in rc.name else "bash"
    run_cmd(f"{sh} {rc}")
    print(f"`{rc}` activated")
    print("Done!")


if __name__ == "__main__":
    if sys.argv[1:] and sys.argv[1] == "dog":
        set_alias_for_git(Path.home())
    else:
        main()
