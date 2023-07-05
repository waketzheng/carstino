import platform
import re
import subprocess
import sys
from contextlib import AbstractContextManager
from pathlib import Path


class EnsureImport(AbstractContextManager):
    """Auto install modules if import error.

    Usage::
        >>> for _ range(EnsureImport.retry):
        ...     with EnsureImport(
        ...         multipart='python-multipart', dotenv='python-dotenv'
        ...     ) as _m:
        ...         import six
        ...         import multipart
        ...         from dotenv import load_dotenv
        ...         # more imports ...
        ...     if _m.ok:
        ...         break
        ...
    """

    mapping = {
        "multipart": "python-multipart",
        "dotenv": "python-dotenv",
        "snap7": "python-snap7",
    }
    retry = 10

    def __init__(self, **kwargs):
        self.exception = None
        self._success = True
        self.package_mapping = dict(self.mapping, **kwargs)

    @property
    def ok(self) -> bool:
        return self._success

    def __exit__(self, exc_type, exc_value, traceback):
        if isinstance(exc_value, (ImportError, ModuleNotFoundError)):
            self.exception = exc_value
            self._success = False
            self.run()
            return True

    def run(self):
        e = self.exception
        modules = re.findall(r"'([a-zA-Z][0-9a-zA-Z_-]+)'", str(e))
        if "--no-install" in sys.argv or not modules:
            raise e
        ms = (self.package_mapping.get(i, i) for i in modules)
        rc = self.install_and_extend_sys_path(*ms)
        if rc:
            sys.exit(rc)

    @staticmethod
    def is_venv() -> bool:
        """Whether in a virtual environment(also work for poetry)"""
        return hasattr(sys, "real_prefix") or (
            hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
        )

    @staticmethod
    def run_and_echo(cmd: str) -> int:
        print("-->\n", cmd, flush=True)
        return subprocess.call(cmd, shell=True)

    @staticmethod
    def log_error(action: str) -> None:
        print(f"ERROR: failed to {action}")

    @classmethod
    def install_and_extend_sys_path(cls, *packages) -> int:
        py = Path(sys.executable)
        depends = " ".join(packages)
        if not cls.is_venv():
            p = Path.cwd() / "venv"
            if not p.exists():
                if cls.run_and_echo(f"{py} -m venv venv"):
                    cls.log_error(f"create virtual environment for {py}")
                    return 1
            if platform.platform().lower().startswith("win"):
                py = p / "Scripts" / "python.exe"
            else:
                py = p / "bin/python"
            cls.run_and_echo(f"{py} -m pip install --upgrade pip")
            lib = list(p.rglob("site-packages"))[0]
            sys.path.append(lib.as_posix())
        if cls.run_and_echo(f"{py} -m pip install {depends}"):
            cls.log_error(f"install {depends}")
            return 2
        return 0
