#!/usr/bin/env python
"""Generate virtual environment activate shell command.

Support Python2.7 and 3.6+

1. If venv/*/activate exists: print `source venv/*/activate`
2. elif it's a poetry project and not controlled by ssh: print `poetry shell`
3. elif .venv/*/activate exists: print `source .venv/*/activate`
4. else run `poetry env info --path` to get environment path then activated by `source ...`
"""

import functools
import os
import platform
import shutil
import sys

try:
    from functools import cache
except ImportError:
    _caching = {}  # type: dict

    def cache(func):  # type:ignore
        @functools.wraps(func)
        def runner(*args, **kw):
            key = func.__name__ + "(*{}, **{})".format(args, kw)
            if key in _caching:
                return _caching[key]
            res = _caching[key] = func(*args, **kw)
            return res

        return runner


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


@cache
def read_content(filename):
    # type: (str) -> bytes
    if not os.path.exists(filename):
        return b""
    with open(filename, "rb") as f:
        return f.read()


def is_poetry_v2():
    # type: () -> bool
    version = run_cmd("poetry --version --no-ansi")
    return "version 2" in version


def is_poetry_installed():
    # type: () -> bool
    try:
        return shutil.which("poetry") is not None
    except AttributeError:  # For Python2
        return os.system("poetry check --quiet") == 0


def is_controlled_by_ssh():
    # type: () -> bool
    return any(os.getenv(i) for i in ["SSH_CLIENT", "SSH_TTY", "SSH_CONNECTION"])


@cache
def is_poetry_project(filename):
    # type: (str) -> bool
    text = read_content(filename)
    return b'build-backend = "poetry' in text


def source_activate(venv_dir, is_windows=False):
    # type: (str, bool) -> str
    bin_dir = "*" if is_windows else "bin"
    return "source {}/{}/activate".format(venv_dir, bin_dir)


def get_poetry_venv_path():
    # type: () -> str
    # If use Git Bash at Windows, which does not show venv prefix after
    # running `poetry shell`, should use `source ../activate` instead;
    # When controlling by ssh in cloud server, `poetry shell` something
    # cost 100% of CPU, sb got the similar issue in aws, and the `python-poetry`
    # suggest to run `poetry run` or `source ../activate` to avoid it.
    cache_dir = run_cmd("poetry run poetry env info --path")
    if cache_dir:
        project_virtualenv = cache_dir.splitlines()[-1]
        try:
            from pathlib import Path
        except ImportError:
            return project_virtualenv.strip()
        else:
            return Path(project_virtualenv).as_posix()
    return ""


def get_venv():
    # type: () -> str
    is_windows = platform.platform().lower().startswith("windows")
    if "--poetry" in sys.argv:
        venv_dir = get_poetry_venv_path()
        if venv_dir:
            return source_activate(venv_dir, is_windows)
    if sys.argv[1:]:
        a1 = sys.argv[1]
        if not a1.startswith("-") and os.path.exists(a1):
            return source_activate(a1, is_windows)
    filename = "pyproject.toml"
    common_venv_names = ["venv"]
    if is_windows or not is_poetry_project(filename):
        common_venv_names += [".venv"]
    for venv_dir in common_venv_names:
        if os.path.exists(venv_dir):
            return source_activate(venv_dir, is_windows)
    if os.path.exists("activate"):
        return "source activate"
    fastapi_full_stack_venv_path = "backend/.venv"
    for venv_dir in (".", fastapi_full_stack_venv_path):
        if (
            is_windows and os.path.exists("{}/Scripts/activate".format(venv_dir))
        ) or os.path.exists(
            "{}/bin/activate".format(venv_dir)  # Cygwin in Windows system also use this
        ):
            return source_activate(venv_dir, is_windows)
    venv_dir = ""
    if (is_windows or is_controlled_by_ssh()) and is_poetry_project(filename):
        if not is_poetry_installed():
            if not is_windows:
                for path in (".venv", "../.venv"):
                    if os.path.exists(path + "/bin"):
                        return source_activate(path)
            msg = (
                "{0} not found!\n"
                "You can install it by:\n"
                "    pip install --user --upgrade pipx\n"
                "    pipx install {0}\n"
            )
            raise RuntimeError(msg.format("poetry"))
        venv_dir = get_poetry_venv_path()
    if venv_dir:
        return source_activate(venv_dir, is_windows)
    elif is_poetry_project(filename):
        return "poetry shell"
    else:
        cmd = ""
        if "--pip" in sys.argv:
            script = os.path.join(os.path.dirname(__file__), "new_venv.py")
            cmd = "{} --project .venv".format(script)
        elif "--pdm" in sys.argv or b'build-backend = "pdm' in read_content(filename):
            cmd = "pdm venv create"
        elif "--uv" in sys.argv or b"[tool.uv]" in read_content(filename):
            cmd = "uv venv"
        if cmd:
            return cmd + " && " + source_activate(".venv", is_windows)
        return "echo ERROR: Virtual environment not found! You should create it first."


def main():
    # type: () -> None
    shell_command_to_activate_virtual_env = get_venv()
    print(shell_command_to_activate_virtual_env.replace("source ", ". "))


if __name__ == "__main__":
    main()
