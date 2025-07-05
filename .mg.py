#!/usr/bin/env python
import os
import re
import sys


def run_shell(cmd, verbose=True):
    # type: (str, bool) -> int
    if verbose:
        print("--> " + str(cmd))
    rc = os.system(cmd)
    if rc != 0:
        # if rc > 255, sys.exit will raise error
        return 1
    return 0


def is_venv():
    # type: () -> bool
    """Whether in a virtual environment"""
    return hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    )


def main():
    # type: () -> int
    fn = "manage.py"
    for _ in range(5):
        if os.path.exists(fn):
            break
        fn = "../" + fn
    else:
        if sys.argv[1:]:
            command = sys.argv[1]
            if command == "shell":
                try:
                    from IPython import start_ipython
                except ImportError:
                    if is_venv():
                        raise
                    return run_shell("python3.11 -m IPython")
                else:
                    sys.argv[0] = re.sub(r"(-script\.pyw|\.exe)?$", "", sys.argv[0])
                    sys.argv.pop(1)
                    return start_ipython()
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
