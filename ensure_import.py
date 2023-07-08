import platform
import re
import subprocess
import sys
from contextlib import AbstractContextManager
from pathlib import Path
from typing import Optional, Union


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
        "tortoise": "tortoise-orm",
        "dotenv": "python-dotenv",
        "snap7": "python-snap7",
    }
    retry = 30

    def __init__(self, _path: Optional[Path] = None, _exit=True, **kwargs):
        self._success = True
        self._exit = _exit
        self._path = _path
        self._mapping = kwargs

    @property
    def ok(self) -> bool:
        return self._success

    def __exit__(self, exc_type, exc_value, traceback):
        if isinstance(exc_value, (ImportError, ModuleNotFoundError)):
            self._success = False
            self.run(exc_value)
            return True

    def run(self, e):
        modules = re.findall(r"'([a-zA-Z][0-9a-zA-Z_]+)'", str(e))
        if not modules or "--no-install" in sys.argv:
            raise e
        package_mapping = dict(self.mapping, **self._mapping)
        ms = (package_mapping.get(i, i) for i in modules)
        rc = self.install_and_extend_sys_path(*ms)
        if rc and self._exit:
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

    @staticmethod
    def is_poetry_project(dirpath: Path) -> bool:
        toml_name = "pyproject.toml"
        for _ in range(3):
            if dirpath.joinpath(toml_name).exists():
                break
            dirpath = dirpath.parent
        else:
            return False
        cmd = "poetry run python -m pip --version"
        return subprocess.run(cmd.split()).returncode == 0

    @staticmethod
    def get_poetry_py_path() -> Path:
        cmd = "poetry env info --path"
        r = subprocess.run(cmd.split(), capture_output=True)
        return Path(r.stdout.strip().decode())

    def install_and_extend_sys_path(self, *packages) -> int:
        py: Union[str, Path] = Path(sys.executable)
        depends = " ".join(packages)
        if not self.is_venv():
            if self._path is None:
                self._path = Path.cwd()
            elif self._path.is_file():
                self._path = self._path.parent
            if self.is_poetry_project(self._path):
                p = self.get_poetry_py_path()
                py = "poetry run python"
            else:
                p = self._path / "venv"
                if not p.exists():
                    if self.run_and_echo(f"{py} -m venv venv"):
                        self.log_error(f"create virtual environment for {py}")
                        return 1
                if platform.platform().lower().startswith("win"):
                    py = p / "Scripts" / "python.exe"
                else:
                    py = p / "bin/python"
            self.run_and_echo(f"{py} -m pip install --upgrade pip")
            lib = list(p.rglob("site-packages"))[0]
            sys.path.append(lib.as_posix())
        if self.run_and_echo(f"{py} -m pip install {depends}"):
            self.log_error(f"install {depends}")
            return 2
        return 0
