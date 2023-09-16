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
        if sys.argv[1:] and sys.argv[1] == "shell":
            cmd = "python -m IPython"
            print("--> {}".format(cmd))
            return os.system(cmd)
        print("Error:\n    `manage.py` not found. Is it a django project?")
        return 1
    return os.system("python {} {}".format(fn, " ".join(sys.argv[1:])))


if __name__ == "__main__":
    sys.exit(main())
