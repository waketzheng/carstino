#!/usr/bin/env python
"""
rstrip every line of file(s)
"""


def rstrip_file(fname, newlines=1):
    with open(fname, 'r+') as f:
        s = f.read()
        if not s:
            raise Exception('Empty file.')
        ss = [line.rstrip() for line in s.rstrip().split('\n')]
        required = '\n'.join(ss) + '\n'*newlines
        if s == required:
            raise Exception('Already meet requirement.')
        f.seek(0)
        f.truncate()
        f.write(required)


def main():
    import sys
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
            print('{}: skip! {}'.format(fn, e))
        else:
            print('{}: rstriped.'.format(fn))
    print('Done!')


if __name__ == '__main__':
    main()
