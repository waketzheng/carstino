#!/usr/bin/env python3
"""
Configure python development environment.
Only work for linux that use bash!
And python3.6+ is required.
"""
import os
import re
from pathlib import Path

FILES = ALIAS_FILE, *_ = [
    ".bash_aliases",
    ".switch_source_pipenv.py",
    ".mg.py",
    ".vimrc",
    ".lint.sh",
]

PACKAGES = "pipenv ipython django flake8 black isort mypy"


def get_cmd_result(cmd):
    with os.popen(cmd) as p:
        return p.read().strip()


def get_shell():
    return Path(get_cmd_result("echo $SHELL")).name


def set_completions(home, repo, aliases_path):
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
                    # zsh used, no need now@2020-05-02
                    # os.system(f"sudo cp {fpath} {sys_completion_path}")
                    pass
            else:
                os.system(f"cp {fpath} {target}")
        # append mg and git completion activate alias to aliases file
        if target.exists():
            a = f"source {target}"
        elif sys_completion_path.exists():
            a = f"source {sys_completion_path}"
    git_completion_path = Path("/etc/bash_completion.d/git-completion.bash")
    if git_completion_path.exists():
        a += f"&&source {git_completion_path}"
    if a and a not in aliases_path.read_text():
        os.system(f"echo 'alias activate_completion=\"{a}\"'>>{aliases_path}")
    return target


def vim_vue():
    folder = "~/.vim/pack/plugins/start"
    repo_url = "https://github.com/posva/vim-vue.git"
    cmd = "mkdir -p {0} && git clone {1} {0}/vim-vue".format(folder, repo_url)
    print("-->", cmd)
    os.system(cmd)


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
        os.system(f"cp {repo / fn} {home}")
    vim_vue()
    s = aliases_path.read_text()
    ss = re.sub(r'(rstrip|prettify)="(.*)"', rf'\1="{repo}/\1.py"', s)
    ss = re.sub(r'(httpa)="(.*)"', rf'\1="{repo}/\1.sh"', s)
    if os.system("which vi") and "alias vi=" not in get_cmd_result("alias"):
        ss += "alias vi=vim\n"
    if s != ss:
        aliases_path.write_text(ss)
    mg_completion_path = set_completions(home, repo, aliases_path)
    # activate aliases at .bashrc or .zshrc ...
    names = [".bashrc", ".zshrc", ".profile", ".zprofile", ".bash_profile"]
    for name in names:
        rc = home / name
        if rc.exists():
            break
    else:
        raise Exception(f"Startup file not found, including {names!r}")
    txt = rc.read_text()
    if ALIAS_FILE not in txt:
        with rc.open("a") as fp:
            fp.write(f"[[ -f ~/{ALIAS_FILE} ]] && . ~/{ALIAS_FILE}")
    # change nvm node mirrors
    nvm = "export NVM_NODEJS_ORG_MIRROR=https://npm.taobao.org/mirrors/node"
    if nvm not in txt:
        with rc.open("a") as fp:
            fp.write(f"# For nvm\n{nvm}\n")

    # switch pip source to aliyun
    swith_pip_source = repo / "pip_conf.py"
    os.system(f"{swith_pip_source}")
    if not Path("/home/root/.pip/pip.conf").exists():
        os.system("sudo cp -r ~/.pip /home/root/")
    # git push auto fill in username and password after input once
    os.system("git config --global credential.helper store")
    # Install some useful python modules
    if os.system(f"python3 -m pip install --upgrade --user {PACKAGES}") != 0:
        if os.system(f"sudo pip3 install -U {PACKAGES}") != 0:
            print("Please install python3-pip and then rerun this script.")
            return
    # Commented the following 5 lines because pipenv will work after reboot
    # # make sure pipenv work
    # if os.system("pipenv --version") != 0:
    #     with os.popen("which python3") as p:
    #         cmd = f"{p.read()} -m pipenv"
    #     os.system(f"echo 'alias pipenv=\"{cmd}\"'>>{aliases_path}")

    # add pipenv auto complete to user bashrc/profile/zshrc, and avoid pyc
    a = 'eval "$(pipenv --completion)"'
    b = "export PYTHONDONTWRITEBYTECODE=1"
    ps = home.glob(".*profile")
    for p in ps:
        if p.name not in (".profile", ".bash_profile"):
            continue
        s = p.read_text()
        if a in s and b in s:
            print(f"`{a}` and `{b}` already in {p}")
            continue
        for i in (a, b):
            if i in s:
                print(f"`{i}` already in {p}")
            else:
                os.system(f"echo >> {p}")  # add empty line
                cmd = f"echo '{i}'>>{p}"
                os.system(cmd)
                print(cmd)
        os.system(f"bash {p}")
        print(f"`{p}` activated")
        break
    else:
        p = rc
        os.system(f". {rc}")
        print(f"`{rc}` activated")
    if mg_completion_path.exists():
        if mg_completion_path.name not in p.read_text():
            a = f"[[ -f {mg_completion_path} ]] && . {mg_completion_path}"
            os.system(f"echo -e '\n# django manage completion\n{a}'>>{p}")
    print("Done!")


if __name__ == "__main__":
    main()
