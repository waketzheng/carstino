#!/usr/bin/env python
import os
import platform


def run_cmd(command):
    with os.popen(command) as p:
        return p.read().strip()


def get_venv():
    is_windows = platform.platform().lower().startswith("windows")
    common_venv_names = ("venv", ".venv") if is_windows else ("venv",)
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
