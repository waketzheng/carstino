#!/usr/bin/env python
"""
This script is used to improve download speed for `brew install`
Requires Python2.7+

Usage::
    $ python pad_brew_download_url.py
"""

import datetime
import os
import subprocess
import sys

PROXY = "https://ghfast.top/"
PY_HOST = "https://mirrors.huaweicloud.com/python/"
PAD = """
elsif (url.start_with?("https://cdn.") || url.start_with?("https://desktop.docker.com"))
  puts "Leave #{url} to be itself."
elsif (url.start_with?("https://ftpmirror.") || url.start_with?("https://ftp.gnu.org"))
  puts "Skip #{url} padding."
elsif url.start_with?("https://www.python.org/ftp/python/3.")
  url = "%s" + url[34,url.length]
elsif !url.start_with?("https://mirror") && !url.start_with?("%s")
  url = "%s" + url
"""


def say_done():
    # type: () -> None
    try:
        from rich.console import Console
    except ImportError:
        print("\nDone~\n")
    else:
        console = Console()
        console.log("[bold magenta]Done.[/bold magenta]", ":vampire:")


def capture_output(cmd):
    # type: (str) -> str
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True)
    except (TypeError, AttributeError):  # For python<=3.6
        with os.popen(cmd) as p:
            return p.read().strip()
    else:
        return r.stdout.decode().strip()


def remove_old_pad(text, s):
    # type: (str, str) -> tuple[str, str, bool]
    s_index = text.index(s)
    pre = text[:s_index]
    lines = pre.splitlines()
    length = len(lines)
    if_index = length
    indent = " "
    for i in range(length - 1, -1, -1):
        line = lines[i]
        trim = line.lstrip()
        if trim.startswith("if "):
            if_index = i
            indent *= len(line) - len(trim)
            break
    updated = False
    elif_index = 0
    start = if_index + 2
    for i, one in enumerate(lines[start:], start):
        if one.lstrip().startswith("elsif "):
            elif_index = i
            break
    if elif_index:
        cut = "\n".join(lines[:elif_index])
        if pre.endswith("\n"):
            cut += "\n"
        removed = text[len(cut) + 1 : s_index]
        text = cut + text[s_index:]
        updated = True
        print("Old pad removed:\n" + removed)
    return text, indent, updated


def backup_it(file, text):
    # type: (str, str) -> None
    bak_file = file + ".{}.bak".format(datetime.date.today())
    if os.path.exists(bak_file):
        return
    with open(bak_file, "w") as fp:
        fp.write(text)
    print("Create backup file at: {}".format(bak_file))


def already_padded(pad, text):
    # type: (str, str) -> bool
    requires = {i.strip() for i in pad.splitlines()}
    got = {i.strip() for i in text.splitlines()}
    return not (requires - got)


def parse_endpoint(text, file):
    # type: (str, str) -> str
    s = '        end\n\n        ohai "Downloading #{url}"'
    if ("\n" + s) in text:
        return s
    ohai = s.splitlines()[-1].strip()
    try:
        index = text.index(ohai)
    except IndexError:
        index = 0
    for idx in range(index - 1, -1, -1):
        c = text[idx]
        if c not in ("\n", " "):
            break
        ohai = c + ohai
    ohai = "end" + ohai
    try:
        index = text.index(ohai)
    except IndexError:
        index = 0
    if index == 0:
        raise ValueError("Failed to find {} in {}".format(repr(ohai), file))
    for idx in range(index - 1, -1, -1):
        c = text[idx]
        if c == "\n":
            break
        ohai = c + ohai
    return ohai


def pad_it(text, pad, indent, endpoint):
    # type: (str, str, str, str) -> tuple[str, str]
    pad = "".join([indent + i + "\n" for i in pad.splitlines()])
    if not text[: text.index(endpoint)].endswith("\n"):
        pad = "\n" + pad
    return text.replace(endpoint, pad + endpoint), pad


def main():
    # type: () -> None
    brew_root = capture_output("brew --prefix")
    folder = "Homebrew/Library/Homebrew"
    name = "download_strategy.rb"
    file = os.path.join(brew_root, folder, name)
    with open(file) as f:
        text = f.read()
    pad = (PAD % (PY_HOST, PROXY, PROXY)).strip()
    if already_padded(pad, text) and "--force" not in sys.argv:
        print("{} already in {}\nNothing to do!".format(PROXY, file))
        return
    s = parse_endpoint(text, file)
    text, indent, updated = remove_old_pad(text, s)
    if not updated:
        backup_it(file, text)
    print("Going to pad {}".format(file))
    new_text, pad = pad_it(text, pad, indent, s)
    if "--dry" in sys.argv:
        import difflib

        try:
            a, b = text.splitlines(keepends=True), new_text.splitlines(keepends=True)
        except TypeError:
            a = [i + "\n" for i in text.splitlines()]
            b = [i + "\n" for i in new_text.splitlines()]
        diffs = difflib.context_diff(a, b, fromfile="before.py", tofile="after.py")
        sys.stdout.writelines(diffs)
    else:
        with open(file, "w") as f:
            f.write(new_text)
        print("Insert\n{} into {}".format(pad, file))
        say_done()


if __name__ == "__main__":
    main()
