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

FILES = ALIAS_FILE, *_ = [
    ".bash_aliases",
    ".mg.py",
    ".vimrc",
    ".lint.sh",
]

PACKAGES = "ipython flake8 black isort mypy autoflake"


def get_cmd_result(cmd: str) -> str:
    ret = subprocess.run(cmd, shell=True, capture_output=True)
    return ret.stdout.decode().strip()


def run_cmd(command: str) -> int:
    return subprocess.run(command, shell=True).returncode


def get_shell() -> str:
    return Path(get_cmd_result("echo $SHELL")).name


def set_completions(home: Path, repo: Path, aliases_path: Path) -> Path:
    # auto complete for command `mg`
    shell = get_shell()
    fname = f".mg_completion.{shell}"
    fpath = repo / fname
    target = home / fname
    sys_completion_path = Path("/etc/bash_completion.d") / fname
    a = ""  # content of activate_completion alias
    if fpath.exists():
        if not target.exists():
            if sys_completion_path.parent.exists():
                if not sys_completion_path.exists():
                    if shell == "bash":
                        run_cmd(f"sudo cp {fpath} {sys_completion_path}")
                        a = f"source {sys_completion_path}"
                else:
                    a = f"source {sys_completion_path}"
            else:
                if shell == "bash":
                    run_cmd(f"cp {fpath} {target}")
        else:
            a = f"source {target}"
    git_completion_path = Path("/etc/bash_completion.d/git-completion.bash")
    if git_completion_path.exists():
        a += f"&&source {git_completion_path}"
    if a and a not in aliases_path.read_text():
        # append mg and git completion activate alias to aliases file
        run_cmd(f"echo 'alias activate_completion=\"{a}\"'>>{aliases_path}")
    return target


def configure_aliases(rc: Path) -> None:
    txt = rc.read_text()
    if ALIAS_FILE not in txt:
        with rc.open("a") as fp:
            fp.write(f"\n[[ -f ~/{ALIAS_FILE} ]] && . ~/{ALIAS_FILE}")
    # change nvm node mirrors
    if "--nvm" in sys.argv:
        nvm = "export NVM_NODEJS_ORG_MIRROR=https://repo.huaweicloud.com/nodejs/"
        if nvm not in txt:
            with rc.open("a") as fp:
                fp.write(f"\n# For nvm\n{nvm}\n")


def main():
    home = Path.home()
    aliases_path = home / ALIAS_FILE
    if aliases_path.exists():
        a = input(f"`{aliases_path}` exists. Continue and replace it?[y/(n)] ")
        if not a.lower().strip().startswith("y"):
            return
    try:
        repo = Path(__file__).parent.resolve()
    except NameError:
        repo = Path(".").resolve()
    for fn in FILES:
        run_cmd(f"cp {repo / fn} {home}")
    s = aliases_path.read_text()
    ss = re.sub(r'(rstrip|prettify)="(.*)"', rf'\1="{repo}/\1.py"', s)
    ss = re.sub(r'(httpa)="(.*)"', rf'\1="{repo}/\1.sh"', s)
    if run_cmd("which vi") and "alias vi=" not in get_cmd_result("alias"):
        ss += "alias vi=vim\n"
    if s != ss:
        aliases_path.write_text(ss)
    mg_completion_path = set_completions(home, repo, aliases_path)
    # activate aliases at .bashrc or .zshrc ...
    names = [".bashrc", ".zshrc", ".profile", ".zprofile", ".bash_profile"]
    if get_shell() == "zsh":
        names = names[1:] + names[:1]
    for name in names:
        rc = home / name
        if rc.exists():
            break
    else:
        raise Exception(f"Startup file not found, including {names!r}")
    configure_aliases(rc)

    # switch pip source to aliyun
    swith_pip_source = repo / "pip_conf.py"
    p = Path.home().joinpath(".config/pip/pip.conf")
    if p.exists():
        print("pip source already config as follows:\n\n")
        print(p.read_bytes().decode())
        tip = f"\nDo you want to rerun ./{swith_pip_source.name}? [y/N] "
        if input(tip).lower() == "y":
            run_cmd(f"{swith_pip_source}")
    else:
        run_cmd(f"{swith_pip_source}")
    # Install some useful python modules
    if run_cmd(f"python3 -m pip install --upgrade --user {PACKAGES}") != 0:
        if run_cmd(f"sudo pip3 install -U {PACKAGES}") != 0:
            print("Please install python3-pip and then rerun this script.")
            return
    # avoid pyc
    b = "export PYTHONDONTWRITEBYTECODE=1"
    ps = home.glob(".*profile")
    for p in ps:
        if p.name not in (".profile", ".bash_profile"):
            continue
        s = p.read_text()
        if b in s:
            print(f"`{b}` already in {p}")
            continue
        for i in (b,):
            if i in s:
                print(f"`{i}` already in {p}")
            else:
                run_cmd(f"echo >> {p}")  # add empty line
                cmd = f"echo '{i}'>>{p}"
                run_cmd(cmd)
                print(cmd)
        run_cmd(f"bash {p}")
        print(f"`{p}` activated")
        break
    else:
        p = rc
        run_cmd(f". {rc}")
        print(f"`{rc}` activated")
    if mg_completion_path.exists():
        if mg_completion_path.name not in p.read_text():
            a = f"[[ -f {mg_completion_path} ]] && . {mg_completion_path}"
            run_cmd(f"echo -e '\n# django manage completion\n{a}'>>{p}")
    print("Done!")


if __name__ == "__main__":
    main()
