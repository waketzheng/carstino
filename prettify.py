#!/usr/bin/env python
"""
A script to reformat the HTML files that can be found by this command:
    $ find . -name "*.html"
use bs4.BeautifulSoup.prettify to make every file prettify.
"""
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


def main():
    count_skip = count_prettify = 0
    for p in Path().rglob("*.html"):
        s = p.read_text()
        ss = BeautifulSoup(s, "html.parser").prettify()
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
