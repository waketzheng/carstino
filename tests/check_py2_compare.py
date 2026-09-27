import shlex
import shutil
import subprocess
import sys

if "pip_conf.py" not in sys.argv:
    print("Skip as pip conf script not updated.")
    sys.exit()

if shutil.which("python2") is None:
    print("Skip because Python2 not found.")
    sys.exit()

cmd = "python2 pip_conf.py --version"
print("--> " + cmd)
if subprocess.call(shlex.split(cmd)):
    sys.exit(1)
