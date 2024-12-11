#!/usr/bin/env python
"""
This script is used to improve download speed for `brew install`

Usage::
    $ python pad_brew_download_url.py
"""

import os
import subprocess

HOST = "https://mirror.ghproxy.com/"
PY_HOST = "https://mirrors.huaweicloud.com/python/"
PAD = """
      elsif (url.start_with?("https://cdn.") || url.start_with?("https://desktop.docker.com"))
        puts "Leave #{url} to be itself."
      elsif (url.start_with?("https://ftpmirror.") || url.start_with?("https://ftp.gnu.org"))
        puts "Skip #{url} padding."
      elsif url.start_with?("https://www.python.org/ftp/python/3.")
        url = "%s" + url[34,url.length]
      elsif !url.start_with?("https://mirror")
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
    # type: (str, str) -> str
    s_index = text.index(s)
    pre = text[:s_index]
    lines = pre.splitlines()
    length = len(lines)
    if_index = length
    for i in range(length - 1, -1, -1):
        line = lines[i]
        if line.strip().startswith("if "):
            if_index = i
            break
    elif_index = 0
    start = if_index + 2
    for i, one in enumerate(lines[start:], start):
        if one.strip().startswith("elsif "):
            elif_index = i
            break
    if elif_index:
        cut = "\n".join(lines[:elif_index])
        if pre.endswith("\n"):
            cut += "\n"
        text = cut + text[s_index:]
    return text


def main():
    # type: () -> None
    brew_root = capture_output("brew --prefix")
    folder = "Homebrew/Library/Homebrew"
    name = "download_strategy.rb"
    file = os.path.join(brew_root, folder, name)
    with open(file) as f:
        text = f.read()
    pad = (PAD % (PY_HOST, HOST)).lstrip("\n")
    if pad in text:
        print("{} already in {}\nNothing to do!".format(HOST, file))
        return

    bak_file = file + ".bak"
    if not os.path.exists(bak_file):
        with open(bak_file, "w") as fp:
            fp.write(text)
        print("Create backup file at: {}".format(bak_file))
    else:
        print("Going to pad {}".format(file))
    s = '      end\n\n      ohai "Downloading #{url}"'
    try:
        text = remove_old_pad(text, s)
    except ValueError:
        w = "ohai"
        s = s.replace(w, " " * 2 + w)
        text = remove_old_pad(text, s)
    new_text = text.replace(s, pad + s)
    with open(file, "w") as f:
        f.write(new_text)
    print("Insert\n{} into {}".format(pad, file))
    say_done()


if __name__ == "__main__":
    main()
