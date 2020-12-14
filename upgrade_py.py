#!/usr/bin/env python
"""
Install latest version Python.
Only work for linux!
And python2.7 or python3 is required.

This script do the following steps:
    1. Download Python xz file from huaweicloud
    2. unzip it to ~/softwares (if folder not found with auto create)
    3. Run this command::
        ./configure --enable-optimizations --enable-loadable-sqlite-extensions\
                && make && sudo make altinstall
"""
import argparse
import os
import sys
import time

try:
    input = raw_input  # type:ignore
except NameError:
    pass

VERSION = "3.9.1"
DOWNLOAD_URL = "https://mirrors.huaweicloud.com/python/{0}/Python-{0}.tar.xz"
# ipython need sqlite3 enable to store history
INSTALL = (
    "./configure --enable-optimizations  --enable-loadable-sqlite-extensions"
    " && make && sudo make {}install"
)
DEFAULT_DIR = "~/softwares"

# Only for ubuntu
EXTEND = (
    "build-essential libssl-dev bzip2 libbz2-dev libxml2-dev "
    "libxslt1-dev zlib1g-dev libffi-dev"
)
APPEND = "sudo apt install -y python3-dev"

# To install python2, just run `sudo apt install python2`
SHORTCUTS = {
    "3": VERSION,
    "39": VERSION,
    "38": "3.8.6",
    "37": "3.7.9",
    "36": "3.6.9",
}


def python_version(py="python"):
    return silently_run("{} -V".format(py)).replace("Python ", "")


def default_python_version():
    print("Default python version:")
    return python_version()


def silently_run(cmd):
    with os.popen(cmd) as p:
        s = p.read()
    return s


def run_and_echo(cmd):
    print("--> " + cmd)
    return os.system(cmd)


def parse_args():
    """parse custom arguments and set default value"""
    parser = argparse.ArgumentParser(description="Install python by source")
    parser.add_argument(
        "-d", "--dir", nargs="?", default=DEFAULT_DIR, help="Where to install"
    )
    parser.add_argument(
        "-v",
        "--version",
        nargs="?",
        default=VERSION,
        help="Python version to be installed",
    )
    parser.add_argument(
        "--dep", action="store_true", help="Install some ubuntu packages"
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Force update (example:3.8.1 -> 3.8.6)",
    )
    parser.add_argument(
        "-n",
        "--no-input",
        action="store_true",
        help="Do not ask me anything",
    )
    parser.add_argument("--alt", action="store_true", help="Want altinstall?")
    return parser.parse_args()


def validated_args():
    args = parse_args()
    if "." in args.version:
        assert args.version >= "3", "Only support Python3 install"
    elif args.version not in SHORTCUTS:
        raise AssertionError("Version should be in " + repr(list(SHORTCUTS.keys())))
    else:
        args.version = SHORTCUTS[args.version]
    version = args.version
    target_version = version.rsplit(".", 1)[0]
    current_version = default_python_version()
    if not args.force:
        pyx = "python" + target_version
        has_same_version = current_version.startswith(target_version)
        can_upgrade = current_version < version
        if not has_same_version:
            if silently_run("which {}".format(pyx)).strip():
                has_same_version = True
                can_upgrade = python_version(pyx) < version
        if has_same_version:
            tip = "\n{} already installed. ".format(pyx.title())
            if args.no_input:
                print("Exit! " + tip)
                sys.exit()
            if can_upgrade:
                tip += "Do your want to upgrade to {}? [y/N] ".format(version)
            else:
                tip += "Do your want to reinstall? [y/N] "
            if input(tip).strip().lower() != "y":
                sys.exit()
    # if system python is py3, replace it, else `make altinstall`
    args.alt = args.alt or not current_version.startswith("3")
    return args


def home():
    try:
        return os.environ["HOME"]
    except KeyError:
        import pwd

        return pwd.getpwuid(os.getuid()).pw_dir


def install_py(folder, url, alt):
    commands = []
    if not folder.startswith("/"):
        folder = folder.replace("~", home())
    if not os.path.exists(folder):
        commands.append("mkdir -p {}".format(folder))
    fname = url.split("/")[-1]
    fpath = "{folder}/{fname}".format(folder=folder, fname=fname)
    cd_folder = "cd " + folder
    if not os.path.exists(fpath):
        # TODO: check md5 of exist file
        commands.append(cd_folder)
        commands.append("wget " + url)
    sub_folder = fname.split(".tar")[0]
    py_folder = os.path.join(folder, sub_folder)
    if not os.path.exists(py_folder):
        commands.append("tar -xf " + fname)
    if cd_folder in commands:
        commands.append("cd " + sub_folder)
    else:
        commands.append("cd " + py_folder)
    install = INSTALL.format("alt" if alt else "")
    return commands + install.split(" && ")

def is_ubuntu_sys():
    r = silently_run("which apt-get")
    return r and 'not found' not in r


def gen_cmds():
    args = validated_args()
    cmds = []
    is_ubuntu = is_ubuntu_sys()
    if is_ubuntu:
        dep = "sudo apt install -y " + EXTEND
        if args.dep:
            cmds.append(dep)
        elif not args.no_input:
            tip = "Do you want to install these: {}? [Y/n] ".format(EXTEND)
            if input(tip).lower() != "n":
                cmds.append(dep)
    url = DOWNLOAD_URL.format(args.version)
    cmds.extend(install_py(args.dir, url, args.alt))
    if is_ubuntu:
        cmds.append(APPEND)
    return cmds


def main():
    cmds = gen_cmds()
    is_root_user = home() == "/root"
    if is_root_user:
        cmds = [i.replace("sudo ", "") for i in cmds]
    print("The following commands will be executed to install python:")
    print("\n    " + "\n    ".join(cmds) + "\n")
    if not is_root_user:
        print("They need sudo permission.")
        if os.system("sudo echo going on ............") != 0:
            sys.exit()
    start = time.time()
    if run_and_echo('&&'.join(cmds)) != 0:
        sys.exit()
    print("Done! Cost: " + friendly_time(int(time.time() - start)))


def friendly_time(cost):
    if cost >= 3600:
        return ">= {}h".format(cost // 3600)
    elif cost > 60:
        return "{}m{}s".format(cost // 60, cost % 60)
    return "{} seconds".format(cost)


if __name__ == "__main__":
    main()
