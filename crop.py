#!/usr/bin/env python3
"""
图片裁剪

Usage::
    $ python crop.py /path/to/image
"""
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Tuple

from humanize.filesize import naturalsize

# pip install pillow humanize
from PIL import Image


def ask_point(name: str, default: Tuple[int, int]) -> Tuple[int, int]:
    tip = "Please enter {} point [Leave empty to use {}]: "
    enter = input(tip.format(name, default)).strip().strip("()")
    if not enter:
        point = default
    else:
        nums = re.findall(r"\d+", enter)
        if len(nums) == 1:
            if enter.startswith(","):
                point = default[0], int(nums[0])
            else:
                point = int(nums[0]), default[1]
        else:
            point = int(nums[0]), int(nums[1])
    return point


def crop_pil(p: Path, filename=None) -> None:
    img = Image.open(p)
    print("Image Shape:", img.size)
    zero_point, end_point = (0, 0), img.size
    print("请输入要裁剪的左上角坐标")
    left, upper = ask_point("left-upper", zero_point)
    print("请输入要裁剪的右下角坐标")
    right, bottom = ask_point("right-bottom", end_point)
    # (left, upper, right, bottom)
    dest = (left, upper, right, bottom)
    cropped = img.crop(dest)
    if filename is None:
        filename = "new" + p.suffix
    cropped.save(filename)
    print(f"Save to {filename} with {dest=}")


def main() -> None:
    if not sys.argv[1:]:
        print(__doc__)
        return
    p = Path(sys.argv[1])
    stat = p.stat()
    print(f"File Size: {naturalsize(stat.st_size, False, True)}")
    print(f"File Created: {datetime.fromtimestamp(stat.st_ctime)}")
    if stat.st_mtime - stat.st_ctime > 10:
        print(f"File Updated: {datetime.fromtimestamp(stat.st_mtime)}")
    crop_pil(p)


if __name__ == "__main__":
    main()
