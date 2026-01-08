#!/usr/bin/python3
"""
Compress file/directory by zstandard or xz

Usage::

- Compress by zstandard

    $ python <me>.py file_or_directory

- Compress by xz

    $ python <me>.py file_or_directory --xz

- Decompress by zstandard

    $ python <me>.py <file>.zst

- Decompress by xz

    $ python <me>.py <file>.xz

"""

import contextlib
import platform
import shlex
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def run_and_echo(cmd: str, cwd: Path | None = None) -> bool:
    print("-->", cmd)
    r = (
        subprocess.run(cmd, shell=True, cwd=cwd)
        if "&&" in cmd
        else subprocess.run(shlex.split(cmd), cwd=cwd)
    )
    return r.returncode == 0


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print(__doc__ and __doc__.replace("<me>", Path(__file__).stem))
        return 1
    xz = False
    opts: list[str] = []
    files: list[str] = []
    for a in args:
        if a.startswith("-"):
            if a.strip("-") == "xz":
                xz = True
            else:
                opts.append(" " + a)
        else:
            files.append(a)
    cwd = None
    if not files:
        cmd = "xz" if xz else "zstd"
    else:
        target = files[0]
        src = Path(target)
        if not src.exists():
            raise FileNotFoundError(target)
        suffix = src.suffix
        if suffix == ".xz":
            cmd = "tar -xf " + target
        elif suffix == ".zst":
            cmd = f"tar --use-compress-program=zstd -xf {target}"
            if platform.system() == "Darwin":
                # 2025.11.22 MacOS not support decompress zstd by tar
                day = datetime.now().date()
                tmpfile = f"{src.stem}.{day}.tmp"
                cmd = (
                    f"zstd -d {target} -o {tmpfile} && tar xf {tmpfile} && rm {tmpfile}"
                )
        else:
            cmd = "tar " + ("-cJf" if xz else "--use-compress-program=zstd -cf")
            stem = Path(target.strip(".")).name
            if not stem.endswith(".tar"):
                stem += ".tar"
            out = stem + "." + ("xz" if xz else "zst")
            if Path(src.parent, out).exists() and input(
                f"{out} exists! Does you want to replace it?[y/N] "
            ).lower() not in ("y", "yes", "1"):
                return 0
            if len(files) == 1 and src.name != target:  # 切换工作目录，避免嵌套路径
                cwd = src.parent
                print(f"--> cd {cwd}")
                files[0] = src.name
            cmd += " " + out + " " + " ".join(files)
    if opts:
        cmd += "".join(opts)
    return int(run_and_echo(cmd, cwd=cwd))


if __name__ == "__main__":
    with contextlib.suppress(ImportError):
        from asynctor import Timer

        main = Timer(main, decimal_places=2)  # ty: ignore[invalid-assignment]
    sys.exit(main())
