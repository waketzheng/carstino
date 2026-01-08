#!/usr/bin/env python3
"""
图片裁剪

Usage::
    $ python crop.py /path/to/image
"""

from __future__ import annotations

import operator
import re
import sys
from datetime import datetime
from pathlib import Path

# pip install pillow humanize
from humanize.filesize import naturalsize  # ty:ignore[unresolved-import]
from PIL import Image  # ty:ignore[unresolved-import]

RE_FLOAT = re.compile(r"\d*\.?\d+")
RE_EXPRESS = re.compile(r"(\d*\.?\d+)([-+*/])(\d*\.?\d+)")


def slim_number(f: float, ndigits=3) -> int | float:
    """Use builtin function `round` to limit the digits length of float

    Uasge::
        >>> slim_number(3.0)
        3
        >>> slim_number(3.1234)
        3.123
        >>> slim_number(0.1234, 2)
        0.12
    """
    fi = int(f)
    if f == fi:
        return fi
    return round(f, ndigits)


def to_value(s: str) -> int | float:
    if "." in s:
        return slim_number(float(s), 10)
    return int(s)


def auto_calc(s: str) -> str:
    """简单计算：'1920/2, 1080/2' -> '960, 540'"""
    if RE_EXPRESS.search(s):
        ss = s.split()
        should_calc = True
        if len(ss) <= 1:
            ss = s.split(",")
            if len(ss) <= 1:
                should_calc = False
        if should_calc:
            ss = ss[:2]
            calc = {
                "+": operator.add,
                "-": operator.sub,
                "*": operator.mul,
                "/": operator.truediv,
            }
            for i, v in enumerate(ss):
                # 简单计算
                m = RE_EXPRESS.search(v)
                if m:
                    a, b, c = m.groups()
                    r = calc[b](to_value(a), to_value(c))
                    if isinstance(r, float):
                        r = slim_number(r)
                    ss[i] = str(r)
            s = " ".join(ss)
    return s


def ask_point(name: str, default: tuple[float, float]) -> tuple[float, float]:
    tip = "Please enter {} point [Leave empty to use {}]: "
    enter = input(tip.format(name, default)).strip().strip("()")
    if not enter:
        point = default
    else:
        nums = RE_FLOAT.findall(auto_calc(enter))
        if len(nums) == 1:
            if enter.startswith(","):
                point = default[0], to_value(nums[0])
            else:
                point = to_value(nums[0]), default[1]
        else:
            point = to_value(nums[0]), to_value(nums[1])
    return point


def crop_pil(p: Path, filename=None) -> None:
    img = Image.open(p)
    print("Image Shape:", img.size)
    zero_point, end_point = (0, 0), img.size
    print("请输入要裁剪的左上角坐标")
    left, upper = ask_point("left-upper", zero_point)
    print("请输入要裁剪的右下角坐标")
    right, bottom = ask_point("right-bottom", end_point)
    if right == 0:
        height = bottom - upper
        if height <= 0:
            raise ValueError(
                f"Expected bottom to be bigger than upper({upper}). Got: {bottom}"
            )
        right = left + slim_number(height * img.size[0] / img.size[1])
    elif bottom == 0:
        width = right - left
        if width <= 0:
            raise ValueError(
                f"Expected right to be bigger than left({left}). Got: {right}"
            )
        bottom = upper + slim_number(width * img.size[1] / img.size[0])
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
