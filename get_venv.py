#!/usr/bin/env python
import os
import platform


def run_cmd(command):
    with os.popen(command) as fp:
        if not hasattr(fp, "_stream"):  # For python2
            return fp.read().strip()
        bf = fp._stream.buffer.read().strip()
    try:
        return bf.decode()
    except UnicodeDecodeError:
        return bf.decode("gbk")


def read_content(filename):
    if not os.path.exists(filename):
        return b""
    with open(filename, "rb") as f:
        return f.read()


def get_venv():
    is_windows = platform.platform().lower().startswith("windows")
    filename = "pyproject.toml"
    common_venv_names = ["venv"]
    if is_windows or b"[tool.poetry]" not in read_content(filename):
        common_venv_names += [".venv"]
    venv_dir = ""
    for dirname in common_venv_names:
        if os.path.exists(dirname):
            venv_dir = dirname
            break
    else:
        if is_windows:
            # I use Git Base at Windows, which does not show venv prefix
            # after running `poetry shell`, so use `source ../activate` instead
            cache_dir = run_cmd("poetry env info --path")
            if cache_dir:
                try:
                    from pathlib import Path
                except ImportError:
                    import sys

                    sys.exit(os.system("python3 " + sys.argv[0]))

                venv_dir = Path(cache_dir).as_posix()
    if venv_dir:
        bin_dir = "*" if is_windows else "bin"
        return "source {}/{}/activate".format(venv_dir, bin_dir)
    return "poetry shell"


def main():
    shell_command_to_activate_virtual_env = get_venv()
    print(shell_command_to_activate_virtual_env)


if __name__ == "__main__":
    main()
