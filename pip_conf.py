#!/usr/bin/env python
"""
This script is for pip source config.
Worked both windows and linux, support python2.7 and python3.5+
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Use:
    $ python pip_conf.py  # default to tencent source

Or:
    $ python pip_conf.py -s tx
    $ python pip_conf.py -s aliyun
    $ python pip_conf.py -s douban
    $ python pip_conf.py -s qinghua
    $ sudo python pip_conf.py -r  # Set conf file to /etc
"""
import os
import platform
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
conf_cmd = "pip config set global.index-url https://{}/simple/"


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


def init_pip_conf(
    source=DEFAULT, replace=False, root=False, force=False, template=TEMPLATE
):
    if not force:
        if "ali" in source:
            if is_ali_cloud_server():
                source = "ali_ecs"
                template = template.replace("https", "http")
        elif "tx" in source or "ten" in source:
            if is_tx_cloud_server():
                source = "tx_ecs"
                template = template.replace("https", "http")
    url = SOURCES.get(source, SOURCES[DEFAULT])
    is_windows = platform.system() == "Windows"
    if (not root or is_windows) and can_set_global():
        cmd = conf_cmd.format(url)
        print("--> " + cmd)
        os.system(cmd)
        return
    if is_windows:
        _pip_conf = ("pip", "pip.ini")
        conf_file = os.path.join(os.path.expanduser("~"), *_pip_conf)
    else:
        if root:
            conf_file = os.path.join("/etc", "pip.conf")
        else:
            _pip_conf = (".pip", "pip.conf")
            conf_file = os.path.join(os.path.expanduser("~"), *_pip_conf)
    parent = os.path.dirname(conf_file)
    if not os.path.exists(parent):
        os.mkdir(parent)
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
    if version and [int(i) for i in version.groups()] >= [10, 1, 0]:
        return True
    return False


def main():
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("-y", action="store_true", help="whether replace existing file")
    parser.add_argument("-r", action="store_true", help="Set conf file to /etc")
    parser.add_argument("-f", action="store_true", help="Force to skip ecs cloud check")
    parser.add_argument(
        "-s",
        "--source",
        default=DEFAULT,
        help="the source of pip, douban/qinghua/aliyun or tx(default)",
    )
    args = parser.parse_args()
    init_pip_conf(args.source, args.y, args.r, args.f)


if __name__ == "__main__":
    main()
