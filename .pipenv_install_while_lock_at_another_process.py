#!/usr/bin/env python3.6
import os
import sys
from concurrent.futures import ProcessPoolExecutor


def main():
    os.system(f'pipenv install --skip-lock {" ".join(sys.argv[1:])}')
    executor = ProcessPoolExecutor()
    executor.submit(os.system, 'pipenv lock')


if __name__ == '__main__':
    main()
