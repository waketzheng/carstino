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
    ssh_path = Path.home() / '.ssh'
    if not ssh_path.exists():
        ssh_path.mkdir()
    pri_repo = ssh_path / 'ssh'
    if not pri_repo.exists():
        os.system(GIT_CLONE)
    pri_key = ssh_path / '213.key'
    if not pri_key.exists():
        os.system(f'cp ~/.ssh/ssh/{pri_key.name} {ssh_path}')
        os.system(f'sudo chmod 400 {pri_key}')


if __name__ == '__main__':
    conf_scripts()
    print('Done!')
