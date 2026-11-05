#!/usr/bin/env python
"""
Change ubuntu mirrors. Support Python2.7 and Python3.5+

Usage::
    # ./change_ubuntu_mirror_sources.py
    # ./change_ubuntu_mirror_sources.py tx
    # ./change_ubuntu_mirror_sources.py qinghua
    # ./change_ubuntu_mirror_sources.py --list
"""

import os
import pprint
import re
import sys

SOURCES = {
    "163": "https://mirrors.163.com",
    "aliyun": "https://mirrors.aliyun.com",
    "huawei": "https://repo.huaweicloud.com",
    "qinghua": "https://mirrors.tuna.tsinghua.edu.cn",
    "tencent": "https://mirrors.cloud.tencent.com",
    "tx": "http://mirrors.tencentyun.com",
}
_default = "tencent"
DEFAULT = SOURCES[_default]
SOURCE_FILE = "/etc/apt/sources.list"
RE_SOURCE = re.compile(r"https?://[^/]+/")

if sys.version_info < (3,):
    input = raw_input  # NOQA:F821 type:ignore


def parse_argv(args):
    # type: (list[str]) -> str
    for arg in args:
        if arg.startswith("http"):
            return arg
        for k, v in SOURCES.items():
            if k in arg:
                return v
    return DEFAULT


def show_choices():
    # type: () -> None
    print("There are several mirrors can be used for ubuntu:")
    pprint.pprint(SOURCES)


def _read_text(fname):
    # type: (str) -> str:
    with open(fname) as fp:
        return fp.read()


def main(fname=SOURCE_FILE):
    # type: (str) -> None
    args = sys.argv[1:]
    if "-l" in args or "--list" in args:
        show_choices()
        sys.exit()
    new_name = "/etc/apt/sources.list.d/ubuntu.sources"
    if "-h" in args or "--help" in args:
        show_choices()
        tip = "\nThis script is to modify mirrors url in {filepath} (Or: {name})\n\nUsage::"
        print(tip.format(filepath=fname, name=new_name))
        print("    $ python {} {}".format(sys.argv[0], _default))
        sys.exit()
    s = _read_text(fname)
    if all(not i.strip() or i.strip().startswith("#") for i in s.splitlines()):
        fname = "/etc/apt/sources.list.d/ubuntu.sources"
        try:
            s = _read_text(fname)
        except FileNotFoundError:
            print("Exit! As " + fname + " not exist.")
            parent = os.path.dirname(fname)
            print("Please run the following command to confirm:\nls " + parent)
            sys.exit(1)
    use_http = False
    if "--http" in args:
        use_http = True
        args = [i for i in args if i != "--http"]
    target = parse_argv(args).rstrip("/")
    if use_http:
        target = target.replace("https:", "http:")
    if target in s:
        msg = "Sources of `{}` already set to `{}`\nSkip."
        print(msg.format(fname, target))
        return
    if "aliyun" in target:
        aliyuncs = "mirrors.cloud.aliyuncs.com"
        if aliyuncs in s:
            msg = "Sources of `{}` already set to `{}`\nSkip."
            print(msg.format(fname, aliyuncs))
            return
    current_sources = list(set(RE_SOURCE.findall(s)))
    is_origin_mirrors = all("ubuntu" in i for i in current_sources)
    if not is_origin_mirrors:
        if len(current_sources) == 1:
            print("Current source is `{}`".format(current_sources[0].strip("/")))
        else:
            print("Current sources are:\n" + "\n    ".join(current_sources))
        if "-y" not in sys.argv:
            a = input("Do you want to replace to `{}`? [y/N] ".format(target))
            if a.lower() != "y":
                return
    ss = RE_SOURCE.sub(target + "/", s)
    try:
        with open(fname, "w") as fp:
            fp.write(ss)
    except IOError as e:
        print(e)
        tip = "\nYou may need to run as root:\n\n  sudo python {}\n"
        print(tip.format(sys.argv[0]))
        return

    bak = fname + ".bak"
    if not os.path.exists(bak):
        with open(bak, "w") as fp:
            fp.write(s)
            print("Backup old sources file to `{}`".format(bak))

    print("Changed sources of `{}` to `{}`\nDone.".format(fname, target))


if __name__ == "__main__":
    main()
