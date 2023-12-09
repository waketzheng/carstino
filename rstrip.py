#!/usr/bin/env python
"""
Remove spaces at the end of every line,
and make sure there is just one and only one empty line at the end the file.

For example:
    "a line with some spaces   \\r\\n" => "a line with some spaces\\n"

Usage::
    $ rstrip *.py  # rstrip all python files in current directory
    $ rstrip **/*.py  # rstrip all python files in current and its sub directories
    $ rstrip src/*.py  # rstrip all python files in src/
    $ rstrip src/**/*.py  # rstrip all python files in src/ and its sub directories
    $ rstrip -r src/  # rstrip all files in src/ and its sub directories
    $ rstrip -t .py src/  # rstrip all python files in src/
    $ rstrip -r -t .py src/  # rstrip all python files in src/ and its sub directories
    $ rstrip a.py b.txt  # rstrip the two files

"""
import argparse
import os
import re
import sys

try:
    from enum import StrEnum
except ImportError:
    try:
        from enum import Enum
    except ImportError:  # For python2

        class AttrIter(type):
            def __iter__(cls):
                return [
                    v
                    for k, v in cls.__dict__.items()
                    if not k.startswith("_") and isinstance(v, str)
                ]

        class StrEnum(object):  # type:ignore
            __metaclass__ = AttrIter

    else:

        class StrEnum(str, Enum):  # type:ignore
            __str__ = str.__str__


class LineBreakChoices(StrEnum):
    win = r"\r\n"
    unix = r"\n"


class ContentException(Exception):
    pass


def rstrip_file(fname, newlines=1, linesep=None):
    try:
        with open(fname) as fp:
            s = fp.read()
    except UnicodeDecodeError:
        with open(fname, encoding="utf8") as fp:
            s = fp.read()
    if not s:
        raise ContentException("Empty file.")
    ss = [line.rstrip() for line in s.rstrip().split("\n")]
    n = linesep or os.linesep
    required = n.join(ss) + n * newlines
    with open(fname, "rb") as fp:
        byt = fp.read()
    new_byt = required.encode()
    if byt == new_byt:
        raise ContentException("Already meet requirement.")
    with open(fname, "wb") as fp:
        fp.write(new_byt)


def is_hidden(dir_or_file):
    re_hidden = re.compile(r"\.\w")
    return any(re_hidden.match(i) for i in dir_or_file.split(os.path.sep))


def is_required_file_type(s, required):
    return required == "*" or s.endswith(required.rsplit(".", 1)[-1])


def parse_args():
    """parse custom arguments and set default value"""
    parser = argparse.ArgumentParser(
        description="Trim spaces at the end of every lines."
    )
    parser.add_argument("-R", "-r", action="store_true", help="Whether to recursive")
    parser.add_argument("-y", "--yes", action="store_true", help="No ask")
    parser.add_argument(
        "-t", "--type", default="*", help="Filter file type(Example: *.py)"
    )
    parser.add_argument("-d", "--dir", default="", help="The directory path")
    parser.add_argument("-b", "--br", default="", help=r"Line break(Example: '\r\n')")
    parser.add_argument(
        "files",
        nargs="+",
        default=[],
        metavar="*.py",
        help="files or directories",
    )
    return parser.parse_args()


def only_files(paths):
    return [i for i in paths if i.is_file()]


def get_filepaths(args):
    from pathlib import Path

    fpaths = []
    if args.dir:
        parent = Path(args.dir)
        if not parent.exists():
            raise Exception("Directory `{}` not exists!".format(args.dir))
    else:
        parent = Path()
    # to be optimize
    for i in args.files:
        if "*" not in i:
            p = Path(i) if i.startswith("/") else (parent / i)
            if p.exists():
                if p.is_file():
                    fpaths.append(p)
                elif p.is_dir():
                    if args.type != "*":
                        args.type = "*." + args.type.lstrip("*").lstrip(".")
                    if args.R:
                        fpaths += list(p.rglob(args.type))
                    else:
                        fpaths += only_files(p.glob(args.type))
        else:
            if "**" in i:
                if i.startswith("**"):
                    i = i.lstrip("*").lstrip("/") or "*"
                    fpaths += list(Path().rglob(i))
                else:
                    if i.endswith("**") or i.endswith("**/"):
                        i = i.rstrip("/").rstrip("*")
                        fpaths += list(Path(i).rglob("*"))
                    else:
                        ps = i.split("/**/")
                        assert (
                            len(ps) == 2
                        ), "Invalid pattern! Must sure only one double `*`."
                        fpaths += list(Path(ps[0]).rglob(ps[1]))
            else:
                if i == "*" or i.startswith("*."):
                    fpaths += only_files(Path().glob(i))
                elif i.startswith("*/"):
                    suffix = i.lstrip("*").lstrip("/") or "*"
                    for j in Path().glob("*"):
                        if j.is_file():
                            fpaths.append(j)
                        elif j.is_dir():
                            fpaths += only_files(j.glob(suffix))
                elif i.endswith("*/"):
                    suffix = "*"
                    i = i.rstrip("/").rstrip("*")
                    ps = i.split("/*/")
                    assert len(ps) < 3, "Too many `*`!"
                    root = Path(ps[0])
                    if len(ps) == 1:
                        fpaths += only_files(root.glob(suffix))
                    else:
                        for j in root.glob("*"):
                            j = j / ps[1]
                            if j.is_dir():
                                fpaths += only_files(j.glob(suffix))
                else:
                    ps = i.split("/*/")
                    assert 3 > len(ps) > 1, "Invalid `*` pattern!"
                    root = Path(ps[0])
                    suffix = ps[-1]
                    for j in root.glob("*"):
                        if j.is_dir():
                            fpaths += only_files(j.glob(suffix))
    return fpaths


def main():
    if not sys.argv[1:]:
        print(__doc__)
        return
    args = parse_args()
    linesep = args.br
    if linesep:
        if linesep == "rn":  # python2 get '\r\n' to be 'rn'
            linesep = "\r\n"
        elif linesep == "n":
            linesep = "\n"
        else:
            choices = [i.value for i in LineBreakChoices]
            if linesep not in choices:
                print("linesep: {}".format(repr(linesep)))
                print("br must be one of this: {}".format(choices))
                return
            linesep = "\r\n" if linesep == LineBreakChoices.win else "\n"
    files = get_filepaths(args)
    count_skip = count_rstrip = 0
    for fn in files:
        try:
            rstrip_file(fn, linesep=linesep)
        except ContentException as e:
            count_skip += 1
            print("{}: skip! {}".format(fn, e))
        except UnicodeDecodeError as e:
            count_skip += 1
            print("{}: failed! {}".format(fn, e))
        else:
            count_rstrip += 1
            print("{}: rstriped.".format(fn))
    print("Done! {} skiped, {} rstriped.".format(count_skip, count_rstrip))


if __name__ == "__main__":
    if sys.version < "3":
        os.system("python3 " + " ".join(sys.argv))
    else:
        main()
