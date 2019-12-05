#!/usr/bin/env python
"""
This script is for pip source config.
Worked both windows and linux, both python2.7 and python3.5+
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Use:
    $ python pip_conf.py
    $ python pip_conf.py -y -s douban
    $ python pip_conf.py -y -s qinghua
    $ python pip_conf.py -y -s aliyun
"""
import os
import re
import platform

"""
A sample of the pip.conf/pip.ini:
```
[global]
index-url = https://mirrors.aliyun.com/pypi/simple/
[install]
trusted-host = mirrors.aliyun.com
```
"""

TEMPLATE = """
[global]
index-url = https://{}/simple/
[install]
trusted-host = {}
""".strip()
DEFAULT = "aliyun"
SOURCES = {
    "aliyun": "mirrors.aliyun.com/pypi",
    "douban": "pypi.douban.com",
    "qinghua": "pypi.tuna.tsinghua.edu.cn",
}
conf_cmd = "pip config set global.index-url https://{}/simple/"


def init_pip_conf(source=DEFAULT, replace=False):
    if platform.system() == "Windows":
        _pip_conf = ("pip", "pip.ini")
    else:
        _pip_conf = (".pip", "pip.conf")
    conf_file = os.path.join(os.path.expanduser("~"), *_pip_conf)
    parent = os.path.dirname(conf_file)
    if not os.path.exists(parent):
        os.mkdir(parent)
    url = SOURCES.get(source, SOURCES[DEFAULT])
    text = TEMPLATE.format(url, url.split("/")[0])
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
    if can_set_global():
        cmd = conf_cmd.format(url)
        print("--> " + cmd)
        os.system(cmd)
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
    parser.add_argument(
        "-y", action="store_true", help="whether replace existing file"
    )
    parser.add_argument(
        "-s",
        "--source",
        default=DEFAULT,
        help="the source of pip, douban/qinghua or aliyun(default)",
    )
    args = parser.parse_args()
    source = args.source
    init_pip_conf(source, args.y)


if __name__ == "__main__":
    main()
