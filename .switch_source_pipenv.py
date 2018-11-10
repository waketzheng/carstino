#!/usr/bin/env python
import os
import re
import sys


PIPFILE = "Pipfile"
DEFAULT = "aliyun"
SOURCES = {
    "aliyun": "https://mirrors.aliyun.com/pypi/simple",
    "douban": "https://pypi.douban.com/simple",
    "qinghua": "https://pypi.tuna.tsinghua.edu.cn/simple",
}


def main():
    if not os.path.exists(PIPFILE):
        print("Error: ``{}`` not found!\nExit!".format(PIPFILE))
        return
    source = SOURCES[DEFAULT]
    if len(sys.argv) > 1:
        for i in ("douban", "qinghua"):
            if i in sys.argv:
                source = SOURCES.get(i)
                break
    with open(PIPFILE, "r+") as fp:
        text = fp.read()
        if source in text:
            tip = "Source of {} already be:\n{}\nSkip!"
        else:
            pattern = r"(\[\[source\]\]\s*url\s*=\s*\")(.+?)(\")"
            new_text = re.sub(pattern, r"\1{}\3".format(source), text)
            fp.seek(0)
            fp.truncate()
            fp.write(new_text)
            tip = "{} switched source to:\n{}\nDone."
    print(tip.format(PIPFILE, source))


if __name__ == "__main__":
    main()
