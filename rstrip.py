#!/usr/bin/env python
"""
rstrip every line of file(s)
"""
import re
import os


class ContentException(Exception):
    pass


def rstrip_file(fname, newlines=1):
    with open(fname) as fp:
        s = fp.read()
    if not s:
        raise ContentException("Empty file.")
    ss = [line.rstrip() for line in s.rstrip().split("\n")]
    required = "\n".join(ss) + "\n" * newlines
    if s == required:
        raise ContentException("Already meet requirement.")
    with open(fname, "w") as fp:
        fp.write(required)


def is_hidden(dir_or_file):
    re_hidden = re.compile(r"\.\w")
    return any(re_hidden.match(i) for i in dir_or_file.split(os.path.sep))


def is_required_file_type(s, required):
    return required == "*" or s.endswith(required.rsplit(".", 1)[-1])


def main():
    import sys
    from argparse import ArgumentParser

    if not sys.argv[1:]:
        print(__doc__.strip())
        print("\nUsage:")
        print("{}{} /path/to/file".format(" " * 4, sys.argv[0]))
        return
    parser = ArgumentParser()
    parser.add_argument(
        "-R", "-r", action="store_true", help="whether to recursive"
    )
    parser.add_argument(
        "-t", "--type", default="*", help="filter file type(Example: *.py)"
    )
    parser.add_argument(
        "-d", "--dir", default=".", help="the directory path(default:.)"
    )
    args, unknown = parser.parse_known_args()
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
    main()
