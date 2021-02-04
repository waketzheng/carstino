#!/usr/bin/env python3
import os
import re
import sys

SOURCES = {
    "163": "https://mirrors.163.com",
    "aliyun": "https://mirrors.aliyun.com",
    "qinghua": "https://mirrors.tuna.tsinghua.edu.cn",
    "huawei": "http://repo.huaweicloud.com",
    "tencent": "https://mirrors.cloud.tencent.com",
}
DEFAULT = SOURCES["aliyun"]
SOURCES["tx"] = SOURCES["tencent"]
SOURCE_FILE = "/etc/apt/sources.list"


def parse_argv(args):
    for arg in args:
        if arg.startswith("http"):
            return arg
        for k in SOURCES:
            if k in arg:
                return SOURCES[k]
    return DEFAULT


def main(fname=SOURCE_FILE):
    target = parse_argv(sys.argv[1:]).rstrip("/")
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
    # to be optimize: show current mirrors and ask to confirm
    ss = re.sub(r"https*://[^/]+/", target + "/", s)
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
