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

    $ python pip_conf.py https://pypi.mirrors.ustc.edu.cn/simple  # conf with full url

    $ python pip_conf.py --list  # show choices

    $ sudo python pip_conf.py --etc  # Set conf file to /etc
"""
import os
import platform
import pprint
import re
import socket
import sys

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
index-url = {}
[install]
trusted-host = {}
""".lstrip()
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
SOURCES["hw"] = SOURCES["huawei"]
SOURCES["hw_inner"] = SOURCES["hw_ecs"] = (
    SOURCES["hw"]
    .replace("cloud", "")
    .replace("/repository", "")
    .replace("repo", "mirrors.tools")
)
CONF_PIP = "pip config set global.index-url "
INDEX_URL = "https://{}/simple/"


def is_pingable(domain):
    if "/" in domain:
        domain = domain.split("/")[0]
    try:
        socket.gethostbyname(domain)
    except Exception:
        return False
    return True


def is_tx_cloud_server():
    return is_pingable(SOURCES["tx_ecs"])


def is_ali_cloud_server():
    return is_pingable(SOURCES["ali_ecs"])


def is_hw_inner():
    return is_pingable(SOURCES["hw_inner"])


def parse_host(url):
    return url.split("://", 1)[1].split("/", 1)[0]


def config_by_cmd(url):
    cmd = CONF_PIP + url
    if not url.startswith("https"):
        print("cmd = {}".format(repr(cmd)))
        cmd += " && pip config set install.trusted-host " + parse_host(url)
    print("--> " + cmd)
    return os.system(cmd)


def detect_inner_net(source):
    args = sys.argv[1:]
    if not args or not [i for i in args if not i.startswith("-")]:
        if is_hw_inner():
            source = "hw_inner"
        elif is_tx_cloud_server():
            source = "tx_ecs"
        elif is_ali_cloud_server():
            source = "ali_ecs"
    elif source in ("huawei", "hw"):
        if is_hw_inner():
            source = "hw_inner"
    elif "ali" in source:
        if is_ali_cloud_server():
            source = "ali_ecs"
    elif "tx" in source or "ten" in source:
        if is_tx_cloud_server():
            source = "tx_ecs"
    return source


def build_index_url(source, force):
    if source.startswith("http"):
        return source
    if not force:
        source = detect_inner_net(source)
    host = SOURCES.get(source, SOURCES[DEFAULT])
    url = INDEX_URL.format(host)
    if source in ("hw_inner", "hw_ecs", "tx_ecs", "ali_ecs"):
        url = url.replace("https", "http")
    return url


def init_pip_conf(
    source=DEFAULT,
    replace=False,
    at_etc=False,
    force=False,
    write=False,
):
    url = build_index_url(source, force)
    is_windows = platform.system() == "Windows"
    if not write and (not at_etc or is_windows) and can_set_global():
        sys.exit(config_by_cmd(url))
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
    text = TEMPLATE.format(url, parse_host(url))
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
    parser.add_argument("--write", action="store_true", help="Conf by write file")
    args = parser.parse_args()
    if args.list:
        print("There are several mirrors that can be used for pip/poetry:")
        pprint.pprint(SOURCES)
    else:
        init_pip_conf(args.name or args.source, args.y, args.etc, args.f, args.write)


if __name__ == "__main__":
    main()
