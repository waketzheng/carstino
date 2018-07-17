#!/usr/bin/env python3
import os
import re
import sys
from pathlib import Path


def cp_follow_symlink(from_path, to_path):
    from_path = from_path.resolve()
    if from_path.is_file():
        os.system(f"sudo cp {from_path} {to_path}")
        return
    if not any(p.is_symlink() for p in from_path.rglob("*")):
        os.system(f"sudo cp -r {from_path} {to_path}")
        return
    to_path = to_path / from_path.name
    to_path.exists() or os.system(f"sudo mkdir {to_path}")
    for p in from_path.glob("*"):
        cp_follow_symlink(p, to_path)


def cp_packages(from_path, to_path):
    already = set([p.name for p in to_path.glob("*")])
    for p in from_path.glob("*"):
        if p.name not in already:
            cp_follow_symlink(p, to_path)
            print(f"cp {p} --> {to_path}")


def path_parsed(path, onlyone=False, m=None):
    if re.match(r"\d+(\.\d+)?", path):
        py = f"python{path}"
    elif re.match(r"python(\d+)?(\.\d+)?", path):
        py = path
    elif Path(path).is_dir():
        return Path(path) if onlyone else [Path(path)]
    if m:
        modules = [m] if isinstance(m, str) else m
    else:
        modules = ("pip", "CommandNotFound", "lsb_release")
    paths = set()
    for m in modules:
        cmd = f"{py} -c 'import {m} as m;print(m.__file__)'"
        if os.system(f"{cmd}  > /dev/null") != 0:
            continue
        child = Path(os.popen(cmd).read().strip())
        parent_level = 1 if child.name == "__init__.py" else 0
        paths.add(child.parents[parent_level])
        if onlyone:
            return paths.pop()
    if not paths:
        raise Exception(
            f"Modules: {modules}, not found at {py}.\n"
            "You may need to try another version.\n"
            "Run `whereis python` to find avaliable versions."
        )
    return paths


def main():
    if "-h" in sys.argv or "--help" in sys.argv or len(sys.argv) == 2:
        print(
            "copy modules in site-packages from one python version to another.\n\n"
            f"Usage:\n{' '*4}python3 {sys.argv[0]} python_version-or-python_script_path python_version-or-python_script_path\n"
            f"Example 1:\n{' '*4}python3 {sys.argv[0]} 3 3.6   # this will copy site-packages from python3 to python3.6\n"
            f"Example 2:\n{' '*4}python3 /usr/lib/python3/site-packages 3.7  # copy /usr/lib/python3/site-packages to site-packages of python3.7\n"
        )
        return
    if sys.argv[1:]:
        from_path, to_path = sys.argv[1:3]
    else:
        from_path, to_path = "3", "3.6"
    from_paths = path_parsed(from_path)
    to_path = path_parsed(to_path, 1, ["subprocess", "pip", "CommandNotFound"])
    print("from_paths", from_paths)
    for from_path in from_paths:
        cp_packages(from_path, to_path)
    print("Done!")


if __name__ == "__main__":
    main()
