#!/usr/bin/env python3.6
from pathlib import Path


fname = 'Pipfile'

aliyun = '''
[[source]]
url = "https://mirrors.aliyun.com/pypi/simple"
verify_ssl = true
name = "aliyun"

'''

douban = '''
[[source]]
url = "https://pypi.douban.com/simple"
verify_ssl = true
name = "douban"

'''

def main():
    import sys
    p = Path(fname)
    if p.exists():
        source = douban if 'douban' in sys.argv else aliyun
        with p.open('r+') as f:
            s = f.read()
            f.seek(0)
            f.truncate()
            f.write(source.lstrip()+s)

if __name__ == '__main__':
    main()
