#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
创建提示符带版本号的虚拟环境
支持Python2和Python3

Usage::
    $ alias new="python ~/archives/carstino/new_venv.py"
    $ new 310
    $ ve
    (venv3.10) $ python -V
    Python 3.10.x
    (venv3.10) $ which python
    venv/bin/python

    $ new 3.12 .venv
    $ ve
    (venv3.12) $ python -V
    Python 3.12.x
    (venv3.12) $ which python
    .venv/bin/python

    $ new .venv  # Will use current python (sys.executable)
    $ ve
    (venv3.12) $ python -V
    Python 3.12.x
    (venv3.12) $ which python
    .venv/bin/python
"""

import os
import re
import sys

VERSION_PATTERN = r"\d+(\.\d+)?"


def parse_dry():
    # type: () -> tuple[bool, list[str]]
    args = sys.argv[1:]
    dry_flag = "--dry"
    dry = dry_flag in args
    if dry:
        args = [i for i in args if i != dry_flag]
    return dry, args


def main():
    # type: () -> int | None
    fmt = "python{0} -m venv {1} --prompt venv{0}"
    path = "venv"
    dry, args = parse_dry()
    if args:
        for a2 in args[1:]:
            if a2.startswith("-"):
                a2 = a2.split("=")[-1].strip()
                if not a2:
                    continue
            path = a2
            break
        v = args[0]
        if v in ("2", "3"):
            cmd = "python{} {}".format(v, __file__)
        elif v in ("-h", "--help"):
            print(__doc__)
            return None
        else:
            if re.match(VERSION_PATTERN, v):
                if "." not in v:  # e.g.: 38, 39, 310, 311
                    version = v[0] + "." + v[1:]
                elif v.count(".") > 1:
                    vs = v.split(".")[:2]
                    version = ".".join(vs)
                else:
                    version = v
                if not all(i.isdigit() for i in version.split(".")):
                    raise ValueError("Invalid version value: {v!r}".format(v=v))
            else:
                path = v
                version = "{0}.{1}".format(*sys.version_info)
            cmd = fmt.format(version, path)
            print(cmd)
    else:
        version = "{0}.{1}".format(*sys.version_info)
        cmd = fmt.format(version, path)
    if dry:
        print("--> " + cmd)
        rc = 0
    else:
        rc = os.system(cmd)
    return 1 if rc else None


if __name__ == "__main__":
    sys.exit(main())
