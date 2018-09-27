#!/usr/bin/env python3
from pathlib import Path


PIPFILE = "Pipfile"

ALIYUN = """
[[source]]
url = "https://mirrors.aliyun.com/pypi/simple"
verify_ssl = true
name = "aliyun"

"""

DOUBAN = """
[[source]]
url = "https://pypi.douban.com/simple"
verify_ssl = true
name = "douban"

"""


def main():
    import sys

    p = Path(PIPFILE)
    if not p.exists():
        return
    source = DOUBAN if "douban" in sys.argv else ALIYUN
    s = p.read_text()
    source = source.lstrip()
    if source not in s:
        p.write_text(source + s)


if __name__ == "__main__":
    main()
