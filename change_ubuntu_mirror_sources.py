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
RE_SOURCE = re.compile(r"https*://[^/]+/")

try:
    input = raw_input  # type:ignore
except NameError:
    pass


def parse_argv(args):
    for arg in args:
        if arg.startswith("http"):
            return arg
        for k in SOURCES:
            if k in arg:
                return SOURCES[k]
    return DEFAULT


def show_choices():
    print("There are several mirrors can be used for ubuntu:")
    pprint.pprint(SOURCES)


def main(fname=SOURCE_FILE):
    args = sys.argv[1:]
    if "-l" in args or "--list" in args:
        show_choices()
        sys.exit()
    if "-h" in args or "--help" in args:
        show_choices()
        tip = "\nThis script is to modify mirrors url in {filepath}\n\nUsage::"
        print(tip.format(filepath=SOURCE_FILE))
        print("    $ ./{} {}".format(sys.argv[0], _default))
        sys.exit()
    use_http = False
    if "--http" in args:
        use_http = True
        args = [i for i in args if i != "--http"]
    target = parse_argv(args).rstrip("/")
    if use_http:
        target = target.replace("https:", "http:")
    with open(fname) as fp:
        s = fp.read()
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
