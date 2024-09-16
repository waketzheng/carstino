#!/usr/bin/env python
import os
import sys


def run_shell(cmd, verbose=True):
    if verbose:
        print("--> {}".format(cmd))
    return os.system(cmd)


def main():
    fn = "manage.py"
    for _ in range(5):
        if os.path.exists(fn):
            break
        fn = "../" + fn
    else:
        if sys.argv[1:]:
            command = sys.argv[1]
            if command == "shell":
                return run_shell("python -m IPython")
            elif command == "runserver":
                if run_shell("which fast") == 0:
                    return run_shell("fast dev")
                elif os.path.exists("main.py"):
                    with open("main.py") as f:
                        txt = f.read()
                    if "__name__ ==" in txt:
                        return run_shell("python main.py")
                    return run_shell("uvicorn main:app")
        print("Error:\n    `manage.py` not found. Is it a django project?")
        return 1
    cmd = "python {} {}".format(fn, " ".join(sys.argv[1:]))
    return run_shell(cmd, verbose=False)


if __name__ == "__main__":
    sys.exit(main())
