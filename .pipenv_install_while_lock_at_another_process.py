#!/usr/bin/env python3.6
import os
import sys
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Process


def subcmd(cmd):
    with os.popen(cmd) as f:
        f.read()


def main():
    os.system(f'pipenv install --skip-lock {" ".join(sys.argv[1:])}')
    # p = Process(target=subcmd, args=('pipenv lock &>/dev/null',))
    # p.start()
    # executor = ProcessPoolExecutor()
    # yield executor.submit(subcmd, 'pipenv lock>/dev/null')
    # executor.submit(subcmd, 'pipenv lock>/dev/null')
    ProcessPoolExecutor().submit(subcmd, 'pipenv lock')



if __name__ == '__main__':
    a = main()
    # next(a)
