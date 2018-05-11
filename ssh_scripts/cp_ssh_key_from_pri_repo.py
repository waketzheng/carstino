#!/usr/bin/env python3
import os
from pathlib import Path


scripts = ['aliyun', 'gullwing', 'romanload', 'ssh212', 'ssh2123']
GIT_CLONE = 'git clone http://192.168.0.12/wenjie.zheng/ssh.git ~/.ssh/ssh'


def auto_install_expect_if_not_exist():
    """Install expect to auto input password for ssh scripts"""
    if not os.popen('which expect').read():
        # TODO: auto choose the os system
        if 'ubuntu':
            os.system('sudo apt install -y expect')
        elif 'centos':
            os.system('sudo yum install -y expect')
        elif 'suse':
            os.system('sudo zypper in -y expect')


def conf_scripts():
    pa, pb = Path(__file__).parent, Path.home()
    for i in scripts:
        t = pa / i
        if not (pb / i).exists():
            os.system(f'cp {t} {pb}')
            print(f'cp: {t} -> {pb}/')
    auto_install_expect_if_not_exist()
    ssh_path = Path.home() / '.ssh'
    if not ssh_path.exists():
        ssh_path.mkdir()
    pri_repo = ssh_path / 'ssh'
    if not pri_repo.exists():
        os.system(GIT_CLONE)
    pri_key = ssh_path / '213.key'
    if not pri_key.exists():
        os.system(f'cp {pri_repo / pri_key.name} {ssh_path}')
        os.system(f'sudo chmod 400 {pri_key}')
        print(f'cp `{pri_key.name}`: {pri_repo} -> {ssh_path}/')
    for k in ('id_rsa', 'id_rsa.pub'):
        ssh_key = ssh_path / k
        if not ssh_key.exists():
            os.system(f'cp {pri_repo / ssh_key.name} {ssh_path}')
            os.system(f'sudo chmod 400 {ssh_key}')
            print(f'cp `{ssh_key.name}`: {pri_repo} -> {ssh_path}/')


if __name__ == '__main__':
    conf_scripts()
    print('Done!')
