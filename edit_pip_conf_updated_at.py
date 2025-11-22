#!/usr/bin/env python
import re
from datetime import datetime


def main():
    file = "pip_conf.py"
    with open(file, "rb") as f:
        s = f.read().decode("utf-8")
    r = re.compile(r'(__updated_at__ = )"([\d.]+)"')
    now = datetime.now()
    day = str(now.date()).replace("-", ".")
    m = r.search(s)
    assert m
    if m.group(2) != day:
        pattern = r'\1"' + day + '"'
        ss = r.sub(pattern, s)
        with open(file, "wb") as f:
            f.write(ss.encode("utf-8"))


if __name__ == "__main__":
    main()
