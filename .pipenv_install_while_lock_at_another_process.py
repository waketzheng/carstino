#!/usr/bin/env python
import os
import sys
from multiprocessing import Process


def subcmd(cmd):
    with os.popen(cmd) as f:
        f.read()


def main():
    os.system("pipenv install --skip-lock {}".format(" ".join(sys.argv[1:])))
    cmd = "pipenv lock 2>&1 >/dev/null"
    p = Process(target=subcmd, args=(cmd,), daemon=True)
    p.start()


if __name__ == "__main__":
    main()
