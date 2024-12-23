#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
创建提示符带版本号的虚拟环境

Usage::
    $ alias new="python ~/archives/carstino/new_venv.py"
    $ new 310
    $ ve
    (venv3.10) $ python -V
    Python 3.10.x
"""

import os
import sys


def main():
    # type: () -> None
    fmt = "python{0} -m venv venv --prompt venv{0}"
    if sys.argv[1:]:
        v = sys.argv[1]
        if v in ("2", "3"):
            cmd = "python{} {}".format(v, __file__)
        else:
            if "." not in v:  # e.g.: 38, 39, 310, 311
                version = v[0] + "." + v[1:]
            elif v.count(".") > 1:
                vs = v.split(".")[:2]
                version = ".".join(vs)
            else:
                version = v
            cmd = fmt.format(version)
            print(cmd)
    else:
        version = "{0}.{1}".format(*sys.version_info)
        cmd = fmt.format(version)
    rc = os.system(cmd)
    sys.exit(1 if rc else None)


if __name__ == "__main__":
    main()
