#!/usr/bin/env python
"""
This script is for pip source config.
Worked both Windows and Linux/Mac, support python2.7 and python3.5+
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Usage:
    $ ./pip_conf.py  # default to tencent source

Or:
    $ python pip_conf.py tx
    $ python pip_conf.py huawei
    $ python pip_conf.py aliyun
    $ python pip_conf.py douban
    $ python pip_conf.py qinghua

    $ python pip_conf.py --list  # show choices

    $ sudo python pip_conf.py --etc  # Set conf file to /etc
"""
import os
import platform
import pprint
import re
import socket

"""
A sample of the pip.conf/pip.ini:
```
[global]
index-url = https://mirrors.cloud.tencent.com/pypi/simple/

[install]
trusted-host = mirrors.cloud.tencent.com
```
"""

TEMPLATE = """
[global]
index-url = https://{}/simple/
[install]
trusted-host = {}
""".strip()
DEFAULT = "tx"
SOURCES = {
    "aliyun": "mirrors.aliyun.com/pypi",
    "douban": "pypi.douban.com",
    "qinghua": "pypi.tuna.tsinghua.edu.cn",
    "tx": "mirrors.cloud.tencent.com/pypi",
    "tx_ecs": "mirrors.tencentyun.com/pypi",
    "huawei": "repo.huaweicloud.com/repository/pypi",
    "ali_ecs": "mirrors.cloud.aliyuncs.com/pypi",
}
SOURCES["tencent"] = SOURCES["tengxun"] = SOURCES["tx"]
SOURCES["ali"] = SOURCES["aliyun"]
CONF_CMD = "pip config set global.index-url https://{}/simple/"


def is_pingable(domain):
    try:
        socket.gethostbyname(domain)
    except Exception:
        return False
    return True


def is_tx_cloud_server():
    return is_pingable("mirrors.tencentyun.com")


def is_ali_cloud_server():
    return is_pingable("mirrors.cloud.aliyuncs.com")


def config_by_cmd(url, conf_cmd=None):
    if conf_cmd is None:
        conf_cmd = CONF_CMD
    if url.startswith("http"):
        cmd = conf_cmd.split("http")[0] + url
    else:
        cmd = conf_cmd.format(url)
    if "https" not in cmd:
        print(f"{cmd = }")
        host = cmd.split("://", 1)[1].split("/", 1)[0]
        cmd += " && pip config set install.trusted-host " + host
    print("--> " + cmd)
    os.system(cmd)


def init_pip_conf(
    source=DEFAULT,
    replace=False,
    at_etc=False,
    force=False,
    template=TEMPLATE,
    conf_cmd=CONF_CMD,
):
    if not force:
        if "ali" in source:
            if is_ali_cloud_server():
                source = "ali_ecs"
                template = template.replace("https", "http")
                conf_cmd = conf_cmd.replace("https", "http")
        elif "tx" in source or "ten" in source:
            if is_tx_cloud_server():
                source = "tx_ecs"
                template = template.replace("https", "http")
                conf_cmd = conf_cmd.replace("https", "http")
    is_raw_url = source.startswith("http")
    if is_raw_url:
        url = source
    else:
        url = SOURCES.get(source, SOURCES[DEFAULT])
    is_windows = platform.system() == "Windows"
    if (not at_etc or is_windows) and can_set_global():
        config_by_cmd(url, conf_cmd)
        return
    if is_windows:
        _pip_conf = ("pip", "pip.ini")
        conf_file = os.path.join(os.path.expanduser("~"), *_pip_conf)
    else:
        if at_etc:
            conf_file = os.path.join("/etc", "pip.conf")
        else:
            _pip_conf = (".pip", "pip.conf")
            conf_file = os.path.join(os.path.expanduser("~"), *_pip_conf)
    parent = os.path.dirname(conf_file)
    if not os.path.exists(parent):
        os.mkdir(parent)
    if is_raw_url:
        url = url.split("://")[-1].split("/simple")[0]
    text = template.format(url, url.split("/")[0])
    if os.path.exists(conf_file):
        with open(conf_file) as fp:
            s = fp.read()
        if text in s:
            print("Pip source already be configured as expected.\nSkip!")
            return
        if not replace:
            print("The pip file {} exists! content:".format(conf_file))
            print(s)
            print('If you want to replace it, rerun with "-y" in args.\nExit!')
            return
    with open(conf_file, "w") as fp:
        fp.write(text + "\n")
    print("Write lines to `{}` as below:\n{}\n".format(conf_file, text))
    print("Done!")


def can_set_global():
    with os.popen("pip --version") as p:
        s = p.read()
    version = re.search(r"^pip (\d+)\.(\d+).(\d+)", s)
    if not version:
        version = re.search(r"^pip (\d+)\.(\d+)", s)
    if version and [int(i) for i in version.groups()] >= [10, 1, 0]:
        return True
    return False


def main():
    from argparse import ArgumentParser

    parser = ArgumentParser()
    source_help = "the source of pip, ali/douban/huawei/qinghua or tx(default)"
    parser.add_argument("name", nargs="?", default="", help=source_help)
    # Be compatible with old version
    parser.add_argument("-s", "--source", default=DEFAULT, help=source_help)
    parser.add_argument(
        "-l", "--list", action="store_true", help="Show available mirrors"
    )
    parser.add_argument("-y", action="store_true", help="whether replace existing file")
    parser.add_argument("--etc", action="store_true", help="Set conf file to /etc")
    parser.add_argument("-f", action="store_true", help="Force to skip ecs cloud check")
    args = parser.parse_args()
    if args.list:
        print("There are several mirrors that can be used for pip/poetry:")
        pprint.pprint(SOURCES)
    else:
        init_pip_conf(args.name or args.source, args.y, args.etc, args.f)


if __name__ == "__main__":
    main()
