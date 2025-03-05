#!/usr/bin/env python
"""
Install latest version Python.
Only work for Linux!
And python2.7 or python3 is required.

This script do the following steps:
    1. Download Python xz file from huaweicloud
    2. unzip it to ~/softwares (if folder does not exist will auto create)
    3. Run this command::
        ./configure --enable-optimizations --enable-loadable-sqlite-extensions\
                && make && sudo make altinstall
"""

import argparse
import os
import pprint
import re
import socket
import sys
import time
from datetime import date
from enum import Enum

if sys.version_info < (3,):
    input = raw_input  # NOQA:F821 type:ignore

VERSION = "3.11.9"
# Mirror of> https://www.python.org/ftp/python/
HOST = "https://mirrors.huaweicloud.com/python/"
DOWNLOAD_PATH = "{0}/Python-{0}.tar.xz"
ENABLE_OPTIMIZE = "--enable-optimizations"
# ipython need sqlite3 enable to store history
ENABLE_SQLITE = "--enable-loadable-sqlite-extensions"
INSTALL = "./configure {} && make && sudo make {}install"
DEFAULT_DIR = "~/softwares"

_apt_extra_deps = """
libssl-dev
bzip2
libbz2-dev
libxml2-dev
libxslt1-dev
zlib1g-dev
libffi-dev
libsqlite3-dev
"""
PREDEPENDS = {
    "apt": [
        "sudo apt install -y wget build-essential"
        + "".join(
            " {}".format(i.split("#")[0].strip())
            for i in _apt_extra_deps.strip().splitlines()
        )
    ],
    "yum": [
        "sudo yum update -y",
        'sudo yum groups mark install "Development Tools"',
        'sudo yum groups mark convert "Development Tools"',
        'sudo yum groupinstall -y "Development Tools"',
        (
            "sudo yum install -y wget make cmake gcc bzip2-devel"
            " tk-devel db4-devel uuid-devel xz-devel sqlite-devel"
            " readline-devel gdbm-devel libpcap-devel ncurses-devel"
            " openssl-devel openssl11 openssl11-devel"
            " libffi-devel"
            " zlib*"
        ),
        'export CFLAGS="$(pkg-config --cflags openssl11)"',
        'export LDFLAGS="$(pkg-config --libs openssl11)"',
    ],
}
APPENDS = {
    "apt": "python3-dev",
    "yum": "python3-devel",
}

# To install python2, just run `sudo apt install python2`
SHORTCUTS = {
    "3": VERSION,
    "313": "3.13.1",
    "312": "3.12.8",
    "311": VERSION,
    "310": "3.10.14",
    "39": "3.9.19",
    "38": "3.8.19",
    "37": "3.7.17",
    "36": "3.6.15",
}


def get_full_version(shortcut):
    # type: (str) -> str
    if "." in shortcut:
        return SHORTCUTS[shortcut.replace(".", "")]
    return SHORTCUTS[shortcut]


def is_pingable(domain):
    # type: (str) -> bool
    if "/" in domain:
        domain = domain.split("/")[0]
    try:
        socket.gethostbyname(domain)
    except Exception:
        return False
    return True


def fetch_html(url):
    # type: (str) -> str
    try:
        from urllib.request import urlopen
    except ImportError:  # For python2
        from urllib import urlopen  # type:ignore[attr-defined,no-redef]
    html = urlopen(url).read().strip()
    if not isinstance(html, str):
        return html.decode()  # For python3
    return html


def update_versions_by_http():
    # type: () -> None
    global VERSION
    global HOST
    domain = (
        HOST.split("://")[-1].split("/")[0].replace("cloud", "").replace("s", "s.tools")
    )
    if is_pingable(domain):
        HOST = "http://" + domain + "/python/"
    filename = "pyversions_{}.html".format(date.today())
    for _ in range(1):
        if os.path.exists(filename):
            with open(filename) as f:
                text = f.read().strip()
                if text:
                    break
    else:
        text = fetch_html(HOST)
        with open(filename, "w") as f:
            f.write(text)
    minors = [k[1:] for k in SHORTCUTS if k[1:]]
    for i in minors:
        pattern = r'<a href="3.{}.(\d+)/"'.format(i)
        patches = sorted(int(i) for i in re.findall(pattern, text))
        if patches:
            latest = "3.{}.{}".format(i, patches[-1])
            SHORTCUTS["3{}".format(i)] = latest
            if latest != VERSION and latest.split(".")[:2] == VERSION.split(".")[:2]:
                SHORTCUTS["3"] = VERSION = latest


def python_version(py="python"):
    # type: (str) -> str
    return silently_run("{} -V".format(py)).replace("Python ", "")


def default_python_version():
    # type: () -> str
    v = python_version()
    print("Default python version: " + v)
    return v


def silently_run(cmd):
    # type: (str) -> str
    with os.popen(cmd) as fp:
        if not hasattr(fp, "_stream"):  # For python2
            return fp.read().strip()
        bf = fp._stream.buffer.read().strip()
    try:
        return bf.decode()
    except UnicodeDecodeError:
        return bf.decode("gbk")


def run_and_echo(cmd):
    # type: (str) -> int
    print("--> " + cmd)
    return os.system(cmd)


class Options(Enum):
    dir = "--dir"
    version = "--version"
    dep = "--dep"
    dry = "--dry"
    list = "--list"
    force = "--force"
    no_sqlite = "--no-sqlite"
    no_ops = "--no-ops"
    no_input = "--no-input"
    alt = "--alt"


def parse_args():
    # type: () -> argparse.Namespace
    """parse custom arguments and set default value"""
    parser = argparse.ArgumentParser(description="Install python by source")
    parser.add_argument(
        "-d", Options.dir.value, nargs="?", default=DEFAULT_DIR, help="Where to install"
    )
    parser.add_argument(
        "-v",
        Options.version.value,
        nargs="?",
        default=VERSION,
        help="Python version to be installed",
    )
    parser.add_argument(
        Options.dep.value,
        action="store_true",
        help="Install some ubuntu/centos packages",
    )
    parser.add_argument(
        Options.dry.value, action="store_true", help="Only print command without run it"
    )
    parser.add_argument(
        Options.list.value,
        action="store_true",
        help="List available python version shortcuts",
    )
    parser.add_argument(
        "-f",
        Options.force.value,
        action="store_true",
        help="Force update (example:3.8.1 -> 3.8.6)",
    )
    parser.add_argument(
        Options.no_sqlite.value,
        action="store_true",
        help="Do not enable sqlite option",
    )
    parser.add_argument(
        Options.no_ops.value,
        action="store_true",
        help="Do not enable optimizations",
    )
    parser.add_argument(
        "-n",
        Options.no_input.value,
        action="store_true",
        help="Do not ask me anything",
    )
    parser.add_argument(Options.alt.value, action="store_true", help="Want altinstall?")
    return parser.parse_args()


def validated_args(ret_pre=False):
    # type: (bool) -> tuple[argparse.Namespace, bool]
    if sys.argv[1:] and sys.argv[1].startswith("3"):
        sys.argv.insert(1, "-v")
    args = parse_args()
    if args.list:
        return args, False
    if args.version.count(".") > 1:
        assert args.version >= "3", "Only support Python3 install"
    else:
        try:
            args.version = get_full_version(args.version)
        except KeyError:
            msg = "Version should be in " + repr(list(SHORTCUTS.keys()))
            raise AssertionError(msg)  # NOQA:B904
    version = args.version
    target_version = version.rsplit(".", 1)[0]
    current_version = default_python_version()
    has_same_version = current_version.startswith(target_version)
    if not args.force:
        pyx = "python" + target_version
        can_upgrade = current_version < version
        if not has_same_version and silently_run("which {}".format(pyx)).strip():
            has_same_version = True
            can_upgrade = python_version(pyx) < version
        if has_same_version and not args.dry:
            tip = "\n{} already installed. ".format(pyx.title())
            if args.no_input:
                print("Exit! " + tip)
                sys.exit()
            if can_upgrade:
                tip += "Do you want to upgrade to {}? [y/N] ".format(version)
            else:
                tip += "Do you want to reinstall? [y/N] "
            if input(tip).strip().lower() != "y":
                sys.exit()
    # if system python is py3, replace it, else `make altinstall`
    args.alt = args.alt or not current_version.startswith("3")
    if ret_pre:
        prefer_to_prepare = (
            not has_same_version and target_version == VERSION.rsplit(".", 1)[0]
        )
        return args, prefer_to_prepare
    return args, False


def home():
    # type: () -> str
    try:
        return os.environ["HOME"]
    except KeyError:
        import pwd

        return pwd.getpwuid(os.getuid()).pw_dir


def install_py(folder, url, alt, configure_options=""):
    # type: (str, str, bool, str) -> list[str]
    commands = []
    if not folder.startswith("/"):
        folder = folder.replace("~", home())
    if not os.path.exists(folder):
        commands.append("mkdir -p {}".format(folder))
    fname = url.split("/")[-1]
    fpath = "{folder}/{fname}".format(folder=folder, fname=fname)
    cd_folder = "cd " + folder
    if not os.path.exists(fpath):
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
    install = INSTALL.format(configure_options, "alt" if alt else "")
    return commands + install.split(" && ")


def get_tool_name():
    # type: () -> str
    for name in PREDEPENDS:
        if detect_command(name):
            return name
    return ""


def detect_command(name):
    # type: (str) -> bool
    r = silently_run("which {name}".format(name=name))
    return bool(r) and "not found" not in r


def gen_cmds(ret_dry=False):
    # type: (bool) -> tuple[list[str], bool, bool]
    args, prefer_to_prepare = validated_args(True)
    if args.list:
        return [], False, True
    version = args.version
    is_mac = sys.platform == "darwin"
    if is_mac:
        print("For MacOS, try this:\n")
        if silently_run("which pyenv"):
            print("    brew update&&brew upgrade pyenv&&./pyinstall.py " + version)
            print("\nSee more at https://github.com/pyenv/pyenv\n")
        else:
            minor_version = ".".join(version.split(".")[:2])
            if silently_run("which python" + minor_version):
                print("    brew upgrade python@" + minor_version)
            else:
                print("    brew install python@" + minor_version)
        sys.exit(1)
    cmds = []
    tool = get_tool_name()
    should_prepare = args.dep or args.no_input or prefer_to_prepare
    if tool:
        deps = PREDEPENDS[tool]
        if not should_prepare:
            tip = "Do you want to install these: {}? [Y/n] ".format(
                "\n  " + "\n  ".join(deps) + "\n"
            )
            if input(tip).lower() != "n":
                should_prepare = True
        if should_prepare:
            cmds.extend(deps)
    url = (HOST + DOWNLOAD_PATH).format(version)
    conf = ""
    if Options.no_ops.value not in sys.argv:
        centos_info = "/etc/centos-release"
        if os.path.exists(centos_info):
            with open(centos_info) as f:
                text = f.read()
            args.no_ops = "release 7.9" in text
    if not args.no_ops:
        conf += ENABLE_OPTIMIZE + " "
    if Options.no_sqlite.value not in sys.argv:
        openssl_version = silently_run("openssl version")
        if openssl_version and openssl_version.lower() < "openssl 3":
            args.no_sqlite = True
    if not args.no_sqlite:
        conf += ENABLE_SQLITE + " "
    cmds.extend(install_py(args.dir, url, args.alt, conf))
    if tool and should_prepare:
        cmds.append("sudo {} install -y ".format(tool) + APPENDS[tool])
    if ret_dry:
        return cmds, args.dry, False
    return cmds, False, False


def main():
    # type: () -> None
    update_versions_by_http()
    cmds, dry, only_list = gen_cmds(True)
    if only_list:
        pprint.pprint(SHORTCUTS)
        return
    is_root_user = home() == "/root"
    if is_root_user:
        cmds = [i.replace("sudo ", "").replace(ENABLE_OPTIMIZE, "") for i in cmds]
    print("The following commands will be executed to install python:")
    print("\n    " + "\n    ".join(cmds) + "\n")
    if dry:
        return
    if not is_root_user:
        print("They need sudo permission.")
        if os.system("sudo echo going on ............") != 0:
            sys.exit()
    start = time.time()
    if run_and_echo("&&".join(cmds)) != 0:
        sys.exit(1)
    print("Done! Cost: " + friendly_time(int(time.time() - start)))


def friendly_time(cost):
    # type: (float) -> str
    if cost >= 3600:
        return ">= {}h".format(cost // 3600)
    elif cost > 60:
        return "{}m{}s".format(cost // 60, cost % 60)
    return "{} seconds".format(cost)


if __name__ == "__main__":
    main()
