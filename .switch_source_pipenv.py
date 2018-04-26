#!/usr/bin/env python
import os


fname = 'Pipfile'

if os.path.exists(fname):
    with open(fname, 'r+') as f:
        s = f.read()
        f.seek(0)
        f.write(s.replace(
            'pypi.python.org',
            'mirrors.aliyun.com/pypi'
        ))
