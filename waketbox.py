#!/usr/bin/env python
"""
Waket Box

Usage::
    FIX_ZWJ=xxx python <me>.py <path-to-file>.txt

"""

from __future__ import annotations

import base64
import os
import random
import string
import sys
import zlib
from functools import cached_property
from pathlib import Path


class DigitGame:
    def __init__(self, token: str) -> None:
        self._token = token

    @property
    def token(self) -> str:
        return self._token

    @cached_property
    def token_length(self) -> int:
        return len(self.token)

    def is_padded(self, text: str) -> bool:
        if len(text) % self.token_length != 1:
            return False
        return text[-1] in string.ascii_lowercase[: self.token_length]

    def black(self, raw: str) -> str:
        b1 = zlib.compress(raw.encode())
        b2 = base64.urlsafe_b64encode(b1)
        s1 = b2.strip(b"=").hex()
        len1 = len(s1)
        multi = int(len1 // self.token_length) + bool(len1 % self.token_length)
        tokens = self.token * multi
        delta = len(tokens) - len1
        last_char = string.ascii_lowercase[delta]
        if delta:
            choices = string.digits + "abcdef"
            s1 += "".join(random.choice(choices) for _ in range(delta))
        chars = [chr(int(a, 16) ^ ord(b)) for a, b in zip(s1, tokens, strict=True)]
        return "".join(chars) + last_char

    def white(self, pad: str) -> str:
        last_char = pad[-1]
        delta = string.ascii_lowercase.index(last_char)
        pad = pad[:-1]
        tokens = self.token * (len(pad) // self.token_length)
        unpad = [ord(p) ^ ord(t) for p, t in zip(pad, tokens, strict=True)]
        if delta:
            unpad = unpad[:-delta]
        s1 = "".join(hex(i)[2:] for i in unpad)
        b2 = bytes.fromhex(s1)
        len1 = len(b2)
        mod = len1 % 4
        if mod:
            b2 += b"=" * (4 - mod)
        b1 = base64.urlsafe_b64decode(b2)
        return zlib.decompress(b1).decode()


def main():
    if len(sys.argv) < 2:
        print(__doc__.replace("<me>", Path(__file__).stem))
        return
    file = Path(sys.argv[1])
    text = file.read_text()
    box = DigitGame(os.environ["FIX_ZWJ"])
    if "--pad" not in sys.argv and box.is_padded(text):
        raw = box.white(text)
        new_file = file.with_name(file.name + ".raw")
        new_file.write_text(raw)
        print(f"Save raw to {new_file}")
    else:
        padded = box.black(text)
        new_file = file.with_name(file.name + ".pad")
        new_file.write_text(padded)
        print(f"Create pad to {new_file}")


if __name__ == "__main__":
    main()
