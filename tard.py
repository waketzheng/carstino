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
import shlex
import subprocess
import sys
from pathlib import Path


def run_and_echo(cmd: str) -> bool:
    print("-->", cmd)
    r = subprocess.run(shlex.split(cmd))
    return r.returncode == 0


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print(__doc__.replace("<me>", Path(__file__).stem))
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
    if not files:
        cmd = "xz" if xz else "zstd"
    else:
        target = files[0]
        suffix = Path(target).suffix
        if suffix == ".xz":
            cmd = "tar -xf " + target
        elif suffix == ".zst":
            cmd = "tar --use-compress-program=zstd -xf " + target
        else:
            cmd = "tar " + ("-cJf" if xz else "--use-compress-program=zstd -cf")
            out = target.strip(".") + ".tar." + ("xz" if xz else "zst")
            cmd += " " + out + " " + " ".join(files)
    if opts:
        cmd += "".join(opts)
    return int(run_and_echo(cmd))


if __name__ == "__main__":
    with contextlib.suppress(ImportError):
        from asynctor import Timer

        main = Timer(main, decimal_places=2)
    sys.exit(main())
