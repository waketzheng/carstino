#!/usr/bin/env python3
import os
import re
import sys
from pathlib import Path


def cp_packages(from_path, to_path):
    already = set([p.name for p in to_path.glob('*')])
    print(f'already: {already}')
    for p in from_path.glob('*'):
        if p.name not in already:
            # TODO: cp real file instead of symlink
            os.system(f'sudo cp -r {p} {to_path}')
            print(f'cp {p} --> {to_path}')

def path_parsed(path, m=None, parent_level=None):
    if re.match(r'\d+(\.\d+)?', path):
        py = f'python{path}'
    elif re.match(r'python\d+(\.\d+)?', path):
        py = path
    elif Path(path).is_dir():
        return Path(path)
    modules = [m] if m else ('pip', 'CommandNotFound', 'lsb_release')
    for m in modules:
        cmd = f"{py} -c 'import {m} as m;print(m.__file__)'"
        if os.system(cmd) == 0:
            break
    else:
        raise Exception(
            f'Modules: {modules}, not found at {py}.\n'
            'You may need to try another version.\n'
            'Run `whereis python` to find avaliable versions.'
        )
    child = Path(os.popen(cmd).read().strip())
    if not parent_level:
        parent_level = 1 if child.name == '__init__.py' else 0
    return child.parents[parent_level]


def main():
    if sys.argv[1:]:
        from_path, to_path = sys.argv[1:3]
    else:
        from_path, to_path = '3', '3.6'
    from_path, to_path = path_parsed(from_path), path_parsed(to_path)
    cp_packages(from_path, to_path)
    print('Done!')

if __name__ == '__main__':
    main()
