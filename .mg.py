#!/usr/bin/env python3.6
import os
import sys
from pathlib import Path


def main():
    fn = "manage.py"
    for _ in range(5):
        if Path(fn).exists():
            break
        fn = "../" + fn
    else:
        print(f'Error:\n{" "*4}`manage.py` not found. Is it a django project?')
        return
    os.system(f'python {fn} {" ".join(sys.argv[1:])}')


if __name__ == "__main__":
    main()
