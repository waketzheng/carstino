#!/usr/bin/env python
"""
Remove spaces at the end of every line,
and make sure there is just one and only one empty line at the end the file.

For example:
    "a line with some spaces   \r\n" => "a line with some spaces\n"

Usage::
    $ rstrip *.py  # rstrip all python files in current directory
    $ rstrip **/*.py  # rstrip all python files in current and its sub directories
    $ rstrip src/*.py  # rstrip all python files in src/
    $ rstrip -r src/*.py  # rstrip all python files in src/ and its sub directories
    $ rstrip src/**/*.py  # rstrip all python files in src/ and its sub directories
    $ rstrip a.py b.txt  # rstrip the two files

"""
import argparse
import os
import re
import sys


class ContentException(Exception):
    pass


def rstrip_file(fname, newlines=1):
    try:
        with open(fname) as fp:
            s = fp.read()
    except UnicodeDecodeError:
        with open(fname, encoding="utf8") as fp:
            s = fp.read()
    if not s:
        raise ContentException("Empty file.")
    ss = [line.rstrip() for line in s.rstrip().split("\n")]
    n = os.linesep
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
    parser = argparse.ArgumentParser(description="Lua file upload tool")
    # --------------
    parser.add_argument("-R", "-r", action="store_true", help="whether to recursive")
    parser.add_argument(
        "-t", "--type", default="*", help="filter file type(Example: *.py)"
    )
    parser.add_argument(
        "-d", "--dir", default=".", help="the directory path(default:.)"
    )
    # -------------
    parser.add_argument(
        "files", nargs="*", default=[], help="files or directories (support re)"
    )
    parser.add_argument(
        "-s", "--suffix", nargs="?", default="", help="upload file type"
    )
    parser.add_argument("-l", "--list", action="store_true", help="list all devices")
    parser.add_argument("-i", "--inter", action="store_true", help="terminal interface")
    return parser.parse_args()


def main():
    if not sys.argv[1:]:
        print(__doc__)
        return
    args = parse_args()

    # args, unknown = parser.parse_known_args()
    args, unknown = "", ""
    if args.R:
        files = []
        for r, ds, fs in os.walk(args.dir):
            if is_hidden(r):
                continue
            for fn in fs:
                if not is_hidden(fn) and is_required_file_type(fn, args.type):
                    files.append(os.path.join(r, fn))
    elif unknown:
        files = [os.path.join(args.dir, f) for f in unknown]
    count_skip = count_rstrip = 0
    for fn in files:
        try:
            rstrip_file(fn)
        except ContentException as e:
            count_skip += 1
            print("{}: skip! {}".format(fn, e))
        else:
            count_rstrip += 1
            print("{}: rstriped.".format(fn))
    print("Done! {} skiped, {} rstriped.".format(count_skip, count_rstrip))


if __name__ == "__main__":
    if sys.version < "3":
        os.system("python3 " + " ".join(sys.argv))
    else:
        main()
