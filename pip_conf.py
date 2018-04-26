#!/usr/bin/env python
import os


aliyun = '''
[global]
index-url = https://mirrors.aliyun.com/pypi/simple/
[install]
trusted-host = mirrors.aliyun.com
'''

douban = '''
[global]
index-url = https://pypi.douban.com/simple/
[install]
trusted-host = pypi.douban.com
'''


def pip_conf_path(user=None):
    user = user or os.popen('whoami').read().strip()
    return '/home/{}/.pip/pip.conf'.format(user)


def init_pip_conf(source=aliyun, conf_path=None, user=None):
    fname = conf_path or pip_conf_path(user)
    dn = os.path.dirname(fname)
    if not os.path.exists(dn):
        os.system('mkdir {}'.format(dn))
    with open(fname, 'w') as f:
        f.write(source.lstrip())


def main():
    import sys
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument(
        '-u', '--user',
        help='>> /home/{user}/.pip/pip.conf [default:`whoami`]')
    parser.add_argument('-y', action='store_true',
                        help='whether replace exist file')
    parser.add_argument('-s', '--source', default='aliyun',
                        help='the source of pip, douban or aliyun(default)')
    args = parser.parse_args()
    user = args.user
    fname = pip_conf_path(user)
    if os.path.exists(fname) and '-y' not in sys.argv:
        print('pip.conf exists!')
        print('If you want to replace it, add "-y" in args')
        return
    if sys.argv[1:] and 'douban' in sys.argv:
        source = douban
    else:
        source = aliyun
    init_pip_conf(source, fname)
    print('Done!')
    print('Write lines to `{}` as below:'.format(fname))
    print(source)


if __name__ == '__main__':
    main()
