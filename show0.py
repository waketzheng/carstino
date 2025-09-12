#!/usr/bin/env python
import os
import string


def main():
    fs = os.listdir(".")
    cs = {f[0].upper() for f in fs}
    print("Aleady: {}".format("".join(sorted(cs))))
    ok = set(string.ascii_uppercase) - cs
    print("Available:")
    for i in sorted(ok):
        print(i)


if __name__ == "__main__":
    main()
