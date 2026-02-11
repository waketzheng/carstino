#!/usr/bin/env python
import os
import platform
import re
import shutil
import subprocess
import sys


def run_shell(cmd, verbose=True):
    # type: (str, bool) -> int
    if verbose:
        print("--> " + str(cmd))
    if "--dry" not in sys.argv:
        rc = os.system(cmd)
        if rc != 0:
            # if rc > 255, sys.exit will raise error
            return 1
    return 0


def capture_output(cmd, verbose=False):
    # type: (str,bool) -> str
    if verbose:
        print(f"--> {cmd}")
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True)
    except (TypeError, AttributeError):  # For python<=3.6
        with os.popen(cmd) as p:
            return p.read().strip()
    else:
        return r.stdout.decode(errors="ignore").strip()


def get_python_version(not_windows, parent=".venv"):
    # type: (bool, str) -> str
    exec_dir = "bin" if not_windows else "Scripts"
    folder = os.path.join(parent, exec_dir)
    files = os.listdir(folder)
    pattern = re.compile(r"python(\d\.\d+)$")
    if not_windows:
        for f in files:
            m = pattern.match(f)
            if m:
                return m.group(1)
    else:
        for f in files:
            stem, ext = os.path.splitext(f)
            m = pattern.match(stem)
            if m:
                return m.group(1)
    return "3.12"


def get_argument(not_windows, directory, verbose, version=""):
    # type: (bool, str, bool, str) -> str
    venv_dir = os.path.join(directory, ".venv")
    if os.path.exists(venv_dir):
        argument = "" if directory == "." else (" --directory " + directory)
        if not version:
            version = get_python_version(not_windows, venv_dir)
            if verbose:
                print("virtual environment found: " + venv_dir)
                print("python version: " + version)
                print("Add {argument} to argument")
        return argument + " --no-python-downloads --python " + version
    return ""


def uvx_ipython(not_windows=True, version=""):
    # type: (bool, str) -> str
    verbose = "--verbose" in sys.argv
    toml = "pyproject.toml"
    venv_dir = ".venv"
    argument = ""
    if os.path.exists(venv_dir):
        version = get_python_version(not_windows, venv_dir)
        if verbose:
            print("virtual environment found: " + venv_dir)
            print("python version: " + version)
        argument = " --no-python-downloads --python " + version
        print("You may want to load virtual environment libs by:")
        print("```py")
        print("from ensure_import import *;EnsureImport.activate(verbose=True)")
        print("```")
    elif not os.path.exists(toml):
        if os.path.exists(os.path.join("..", toml)):
            argument = get_argument(not_windows, "..", verbose, version=version)
        elif os.path.exists(os.path.join("..", "..", toml)):
            directory = os.path.join("..", "..")
            argument = get_argument(not_windows, directory, verbose, version=version)
    return "uvx --with ensure-import" + argument + " ipython"


def is_venv():
    # type: () -> bool
    """Whether in a virtual environment"""
    return hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    )


def without_manage_py():
    # type: () -> int
    args = sys.argv[1:]
    if args:
        command = args[0]
        if command == "shell":
            try:
                from IPython import start_ipython  # ty:ignore[unresolved-import]
            except ImportError:
                offline = "--offline" in sys.argv
                not_windows = platform.system() != "Windows"
                prefer_uvx = not_windows or "fast" in capture_output("uvx tool list")
                if is_venv():
                    msg = "ipython not installed. "
                    if offline or (
                        (not_windows and shutil.which("uvx") is None)
                        or (not not_windows and shutil.which("ipython") is None)
                    ):
                        print(msg + "You may need to install it by:\n")
                        tip = "pip install ipython"
                        if not_windows:
                            tip = "uv " + tip
                        print("  " + tip)
                        raise
                    version = "" if not_windows else sys.executable
                    command = (
                        uvx_ipython(not_windows, version=version)
                        if prefer_uvx
                        else "ipython"
                    )
                    prompt = msg + "Do you want to run it by `" + command + "`?[Y/n] "
                    a = input(prompt).strip().lower()
                    if a in ("n", "0", "no"):
                        print("Abort!")
                        sys.exit(1)
                    return run_shell(command)
                if not offline and not_windows:
                    return run_shell(uvx_ipython(not_windows))
                elif hasattr(shutil, "which"):  # For Python3
                    if shutil.which("ipython") is not None:
                        return run_shell("ipython")
                    return run_shell("python3 -m IPython")
                else:
                    return run_shell("python3.11 -m IPython")  # For my mac
            else:
                sys.argv[0] = re.sub(r"(-script\.pyw|\.exe)?$", "", sys.argv[0])
                for index in list(range(len(sys.argv)))[::-1]:
                    if index >= 1:
                        sys.argv.pop(index)
                    else:
                        break
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


def main():
    # type: () -> int
    fn = "manage.py"
    for _ in range(5):
        if os.path.exists(fn):
            break
        fn = "../" + fn
    else:
        return without_manage_py()
    cmd = "python {} {}".format(fn, " ".join(sys.argv[1:]))
    return run_shell(cmd, verbose=False)


if __name__ == "__main__":
    sys.exit(main())
