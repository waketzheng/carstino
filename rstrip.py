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
    import re
    import os
    import sys
    from argparse import ArgumentParser
    if not sys.argv[1:]:
        print(__doc__.strip())
        print('\nUsage:')
        print('{}{} /path/to/file'.format(' '*4, sys.argv[0]))
        return
    parser = ArgumentParser()
    parser.add_argument('-R', '-r', action='store_true',
                        help='whether to resurive')
    args = parser.parse_args()
    if args.R:
        d = '.'
        files = []
        pattern_hiden = re.compile(r'\.\w')
        for r, ds, fs in os.walk(d):
            if any(pattern_hiden.match(i) for i in r.split(os.path.sep)):
                continue
            for fn in fs:
                if not pattern_hiden.match(fn):
                    files.append(os.path.join(r, fn))
    else:
        files = sys.argv[1:]
    count_skip = count_rstrip = 0
    for fn in files:
        try:
            rstrip_file(fn)
        except Exception as e:
            count_skip += 1
            print('{}: skip! {}'.format(fn, e))
        else:
            count_rstrip += 1
            print('{}: rstriped.'.format(fn))
    print('Done! {} skiped, {} rstriped.'.format(count_skip, count_rstrip))


if __name__ == '__main__':
    main()
