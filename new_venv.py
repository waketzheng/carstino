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

import functools
import os
import re
import sys

__version__ = "0.1.1"
VERSION_PATTERN = r"\d+(\.\d+)?"


def parse_dry():
    # type: () -> tuple[bool, list[str]]
    args = sys.argv[1:]
    dry_flag = "--dry"
    dry = dry_flag in args
    if dry:
        args = [i for i in args if i != dry_flag]
    return dry, args


def build_cmd(args, path, fmt, prompt):
    # type: (list[str], str, str, str) -> tuple[str, str]
    for a2 in args[1:]:
        if a2.startswith("-"):
            a2 = a2.split("=")[-1].strip()
            if not a2:
                continue
        if not re.match(VERSION_PATTERN, a2):
            path = a2
        break
    v = args[0]
    if v in ("2", "3"):
        cmd = "python{} {}".format(v, __file__)
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
            if args[1:]:
                a1 = args[1].split("=")[-1].strip()
                if re.match(VERSION_PATTERN, a1):
                    version = a1
        cmd = fmt.format(version, path, prompt)
    return cmd, path


def pop_flag(option, args):
    # type: (str, list[str]) -> bool
    try:
        index = args.index(option)
    except ValueError:
        return False
    else:
        args.pop(index)
        return True


def main():
    # type: () -> int | None
    if "-h" in sys.argv or "--help" in sys.argv:
        print(__doc__)
        return None
    if "-v" in sys.argv or "--version" in sys.argv:
        print(__version__)
        return None
    fmt = "python{0} -m venv {1} --prompt {2}{0}"
    prompt = path = "venv"
    dry, args = parse_dry()
    pop_arg_option = functools.partial(pop_flag, args=args)
    for i, flag in enumerate(["--project", "--parent"], 1):
        if pop_arg_option(flag):
            prompt = os.path.split(os.getcwd())[-i].replace(" ", "_") + "-"
            break
    upgrade_deps = not pop_arg_option("--no-upgrade")
    if args:
        cmd, path = build_cmd(args, path, fmt, prompt)
    else:
        version = "{0}.{1}".format(*sys.version_info)
        cmd = fmt.format(version, path, prompt)
    if upgrade_deps:
        cmd += " --upgrade-deps"
    print("--> " + cmd)
    if dry:
        return None
    if os.path.exists(path) and "--no-input" not in sys.argv:
        tip = "Directory '{}' exists! Do you want to override it?[y/N] ".format(path)
        try:
            a = raw_input(tip)  # type:ignore[name-defined]
        except NameError:
            a = input(tip)
        if not (a.strip() and a.lower().startswith("y")):
            return 1
    rc = os.system(cmd)
    return 1 if rc else None


if __name__ == "__main__":
    sys.exit(main())
