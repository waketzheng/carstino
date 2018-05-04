#!/usr/bin/env python3
import os
from pathlib import Path


scripts = ['aliyun', 'gullwing', 'ssh212', 'ssh2123']
GIT_CLONE = 'git clone http://192.168.0.12/wenjie.zheng/ssh.git ~/.ssh/ssh'


def conf_scripts():
    pa, pb = Path(__file__).parent, Path.home()
    for i in scripts:
        t = pa / i
        if not (pb / i).exists():
            os.system(f'cp {t} {pb}')
            print(f'cp: {t} -> {pb}/')
    pri_repo = Path.home() / '.ssh'
    if not pri_repo.exists():
        pri_repo.mkdir()
    pri_repo /= 'ssh'
    if not pri_repo.exists():
        os.system(GIT_CLONE)


if __name__ == '__main__':
    conf_scripts()
    print('Done!')