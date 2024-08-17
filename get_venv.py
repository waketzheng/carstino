#!/usr/bin/env python
"""Generate virtual environment activate shell command.

1. If venv/*/activate exists: print `source venv/*/activate`
2. elif it's a poetry project and not controlled by ssh: print `poetry shell`
3. elif .venv/*/activate exists: print `source .venv/*/activate`
4. else run `poetry env info --path` to get environment path then activated by `source ...`
"""

import os
import platform


def run_cmd(command):
    # type: (str) -> str
    with os.popen(command) as fp:
        if not hasattr(fp, "_stream"):  # For python2
            return fp.read().strip()
        bf = fp._stream.buffer.read().strip()
    try:
        return bf.decode()
    except UnicodeDecodeError:
        return bf.decode("gbk")


def read_content(filename):
    # type: (str) -> bytes
    if not os.path.exists(filename):
        return b""
    with open(filename, "rb") as f:
        return f.read()


def is_controlled_by_ssh():
    # type: () -> bool
    return any(os.getenv(i) for i in "SSH_CLIENT SSH_TTY SSH_CONNECTION".split())


def get_venv():
    # type: () -> str
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
        if is_windows or is_controlled_by_ssh():
            # If use Git Bash at Windows, which does not show venv prefix after
            # running `poetry shell`, should use `source ../activate` instead;
            # When controlling by ssh in cloud server, `poetry shell` something
            # cost 100% of CPU, sb got the similar issue in aws, and the `python-poetry`
            # suggest to run `poetry run` or `source ../activate` to avoid it.
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
    # type: () -> None
    shell_command_to_activate_virtual_env = get_venv()
    print(shell_command_to_activate_virtual_env)


if __name__ == "__main__":
    main()
