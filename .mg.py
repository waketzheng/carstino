#!/usr/bin/env python
import os
import sys


def main():
    fn = "manage.py"
    for _ in range(5):
        if os.path.exists(fn):
            break
        fn = "../" + fn
    else:
        print("Error:\n    `manage.py` not found. Is it a django project?")
        return
    os.system("python {} {}".format(fn, " ".join(sys.argv[1:])))


if __name__ == "__main__":
    main()
