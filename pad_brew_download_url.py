#!/usr/bin/env python
"""
This script is used to improve download speed for `brew install`

Usage::
    $ python pad_brew_download_url.py
"""

import os
import subprocess

HOST = "https://g.waketzheng.top/"
PAD = """
      elsif (url.start_with?("https://cdn.") || url.start_with?("https://desktop.docker.com"))
        puts "Leave #{url} to be itself."
      elsif !url.start_with?("https://mirrors.")
        url = "%s" + url
"""


def capture_output(cmd):
    # type: (str) -> str
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True)
    except (TypeError, AttributeError):  # For python<=3.6
        with os.popen(cmd) as p:
            return p.read().strip()
    else:
        return r.stdout.decode().strip()


def main():
    # type: () -> None
    brew_root = capture_output("brew --prefix")
    folder = "Homebrew/Library/Homebrew"
    name = "download_strategy.rb"
    file = os.path.join(brew_root, folder, name)
    with open(file) as f:
        text = f.read()
    if HOST in text:
        print("{} already in {}\nNothing to do!".format(HOST, file))
        return

    s = '      end\n\n      ohai "Downloading #{url}"'
    pad = PAD % HOST
    new_text = text.replace(s, pad.lstrip("\n") + s)
    with open(file, "w") as f:
        f.write(new_text)
    print("Insert {} into {}".format(pad, file))


if __name__ == "__main__":
    main()
