#!/usr/bin/env python3.6
from pathlib import Path


aliyun = """
[global]
index-url = https://mirrors.aliyun.com/pypi/simple/
[install]
trusted-host = mirrors.aliyun.com
"""

douban = """
[global]
index-url = https://pypi.douban.com/simple/
[install]
trusted-host = pypi.douban.com
"""


def init_pip_conf(source=aliyun, replace=False):
    p = Path.home() / ".pip/pip.conf"
    if not p.parent.exists():
        p.parent.mkdir()
    source = source.strip()
    if p.exists():
        if source in p.read_text():
            return
        if not replace:
            print("pip.conf exists! content:")
            print(p.read_text())
            print('If you want to replace it, rerun with "-y" in args')
            return
    p.write_text(source + "\n")
    print(f"Write lines to `{p}` as below:")
    print(source)


def main():
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument(
        "-y", action="store_true", help="whether replace exist file"
    )
    parser.add_argument(
        "-s",
        "--source",
        default="aliyun",
        help="the source of pip, douban or aliyun(default)",
    )
    args = parser.parse_args()
    source = douban if args.source == "douban" else aliyun
    init_pip_conf(source, args.y)
    print("Done!")


if __name__ == "__main__":
    main()
