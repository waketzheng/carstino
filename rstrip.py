#!/usr/bin/env python
"""
rstrip every line of file(s)
"""
import sys


def rstrip_file(fname):
    with open(fname, 'r+') as f:
        ss = f.readlines()
        f.seek(0)
        f.truncate()
        f.write('\n'.join([i.rstrip() for i in ss]))


def main():
    if not sys.argv[1:]:
        print(__doc__.strip())
        print('\nUsage:')
        print('{}{} /path/to/file'.format(' '*4, sys.argv[0]))
        return
    files = sys.argv[1:]
    for fn in files:
        try:
            rstrip_file(fn)
        except Exception as e:
            print('{}: skip!'.format(fn))
        else:
            print('{}: rstriped.'.format(fn))
    print('Done!')


if __name__ == '__main__':
    main()
