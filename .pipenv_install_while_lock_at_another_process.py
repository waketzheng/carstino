#!/usr/bin/env python3.6
import os
import sys
from multiprocessing import Process


def subcmd(cmd):
    with os.popen(cmd) as f:
        f.read()


def main():
    os.system(f'pipenv install --skip-lock {" ".join(sys.argv[1:])}')
    cmd = "pipenv lock 2>&1 >/dev/null"
    p = Process(target=subcmd, args=(cmd,), daemon=True)
    p.start()


if __name__ == "__main__":
    main()
