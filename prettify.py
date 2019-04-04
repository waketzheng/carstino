#!/usr/bin/python3
"""
A script to reformat the HTML files that can be found by this command:
    $ find . -name "*.html"
use bs4.BeautifulSoup.prettify to make every file prettify.
Note: Python 3.6+ and bs4 (pip install bs4) is required.
"""
import re
from pathlib import Path

from bs4 import BeautifulSoup


def say_result(count_prettify, count_skip):
    """print the summary result after files be prettify"""
    if count_prettify == 1:
        files_prettify = "1 file reformatted"
    else:
        files_prettify = f"{count_prettify} files reformatted"
    if count_skip == 1:
        files_skip = "1 file left unchanged."
    else:
        files_skip = f"{count_skip} files left unchanged."
    if count_prettify == 0:
        print(files_skip)
    else:
        if count_skip == 0:
            print(files_prettify + ".")
        else:
            print(f"{files_prettify}, {files_skip}")


def prettify(html, indent_width=2):
    ss = BeautifulSoup(html, "html.parser").prettify()
    # Custom indent width
    re_indent = re.compile(r"^(\s*)", re.MULTILINE)
    ss = re_indent.sub(r"\1" * indent_width, ss)
    # Put them in one line, if there is no content between tags
    re_slim = re.compile(r"<(\w+)(.*)>\s*</\1>")
    ss = re_slim.sub(r"<\1\2></\1>", ss)
    return ss


def main():
    count_skip = count_prettify = 0
    for p in Path().rglob("*.html"):
        s = p.read_text()
        ss = prettify(s)
        if s == ss:
            count_skip += 1
            continue
        count_prettify += 1
        p.write_text(ss)
        print("reformatted", p)
    if count_skip or count_prettify:
        print("\nAll done!")
        say_result(count_prettify, count_skip)
    else:
        print("None of HTML file found!")


if __name__ == "__main__":
    main()
