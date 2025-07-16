import os
import shutil
import sys

if "pip_conf.py" not in sys.argv:
    print("Skip as pip conf script not updated.")
    sys.exit()

if shutil.which("python2") is None:
    print("Skip because Python2 not found.")
    sys.exit()

if os.system("python2 pip_conf.py --version"):
    sys.exit(1)
