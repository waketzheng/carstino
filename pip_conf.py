#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
This script is for pip/poetry/pdm/uv source config.
Worked both Windows and Linux/Mac, support python2.7 and python3.6+
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Usage:
    $ ./pip_conf.py  # default to tencent source

Or:
    $ python pip_conf.py tx --tool=pip
    $ python pip_conf.py huawei
    $ python pip_conf.py aliyun
    $ python pip_conf.py douban
    $ python pip_conf.py qinghua

    $ python pip_conf.py https://pypi.mirrors.ustc.edu.cn/simple  # conf with full url

    $ python pip_conf.py --list  # show choices
    $ python pip_conf.py --poetry  # set mirrors in poetry's config.toml
    $ python pip_conf.py --pdm     # set pypi.url for pdm
    $ python pip_conf.py --uv      # set mirror for uv
    $ python pip_conf.py --pip     # set mirror for pip
    $ python pip_conf.py --tool=auto # find out manage tool at current directory and set mirror for it

    $ sudo python pip_conf.py --etc  # Set conf to /etc/pip.[conf|ini]

If there is any bug or feature request, report it to:
    https://github.com/waketzheng/carstino/issues
"""

__author__ = "waketzheng@gmail.com"
__updated_at__ = "2025.11.18"
__version__ = "0.8.6"
import contextlib
import functools
import os
import platform
import pprint
import re
import shutil
import socket
import subprocess
import sys

try:
    import typing
except ImportError:
    pass
else:
    if typing.TYPE_CHECKING:
        from argparse import Namespace  # NOQA:F401
        from typing import Literal, Optional  # NOQA:F401

"""
A sample of the pip.conf/pip.ini:
```
[global]
index-url = https://mirrors.cloud.tencent.com/pypi/simple/
trusted-host = mirrors.cloud.tencent.com
```
"""

TEMPLATE = """
[global]
index-url = {}
trusted-host = {}
""".lstrip()
DEFAULT = "tx"
SOURCES = {
    "ali": "mirrors.aliyun.com/pypi",
    "db": "pypi.doubanio.com",
    "qh": "pypi.tuna.tsinghua.edu.cn",
    "tx": "mirrors.cloud.tencent.com/pypi",
    "tx_ecs": "mirrors.tencentyun.com/pypi",
    "hw": "repo.huaweicloud.com/repository/pypi",
    "ali_ecs": "mirrors.cloud.aliyuncs.com/pypi",
    "pypi": "pypi.org",
}
SOURCES["tencent"] = SOURCES["tengxun"] = SOURCES["tx"]
SOURCES["aliyun"] = SOURCES["ali"]
SOURCES["douban"] = SOURCES["db"]
SOURCES["qinghua"] = SOURCES["qh"]
SOURCES["huawei"] = SOURCES["hw"]
_hw_inner_source = (
    SOURCES["hw"]
    .replace("cloud", "")
    .replace("/repository", "")
    .replace("repo", "mirrors.tools")
)
CONF_PIP = "pip config set global.index-url "
INDEX_URL = "https://{}/simple/"
socket.setdefaulttimeout(5)


class PipConfError(Exception):
    pass


class ParamError(PipConfError):
    """Invalid parameters"""


class ConfigError(PipConfError):
    """Failed to determide or set config"""


class System:
    _system = None  # type: Optional[str]

    @classmethod
    def get_system(cls):
        # type: () -> str
        system = cls._system
        if system is None:
            system = cls._system = platform.system()
        return system

    @classmethod
    def is_win(cls):
        # type: () -> bool
        return cls.get_system() == "Windows"

    @classmethod
    def is_mac(cls):
        # type: () -> bool
        return cls.get_system() == "Darwin"

    @classmethod
    def is_linux(cls):
        # type: () -> bool
        return cls.get_system() == "Linux"


def is_command_exists(tool):
    # type: (str) -> bool
    # tool: Literal['uv', 'pdm', 'poetry']
    try:
        return shutil.which(tool) is not None
    except AttributeError:  # For Python2
        return os.system(tool + " --version --no-ansi") == 0


def get_python(check_download_command=False):
    # type: (bool) -> str
    if not System.is_linux():
        return "python"
    py = "/usr/bin/python"
    if not os.path.exists(py) and os.path.exists(py + "3"):
        # Ubuntu default to have python3 but not python
        return "python3"
    if not check_download_command:
        return "python"
    is_py3 = sys.version_info >= (3,)
    try:
        import pip
    except ImportError:
        # Virtual environment created by uv/pdm may no include pip module
        return "python"
    else:
        if is_py3 or pip.__version__ >= "18.1":
            return sys.executable
        if os.system("python3 -V") == 0:
            return "python3"
        # Does not support `pip download`
        is_py2 = "import sys;py2=int(sys.version_info<(3,));sys.exit(py2)"
        if os.system('python -c "{}"'.format(is_py2)) == 1:
            # Default python is py2
            cmd = "python -m pip download --help"
            if capture_output(cmd).lower().startswith("error"):
                raise ConfigError("pip is to old, need to be upgraded")
    return "python"


def check_mirror_by_pip_download(domain, tmp=False):
    # type: (str, bool) -> bool
    if "/" not in domain:
        domain = "http://{0}/pypi/simple/ --trusted-host {0}".format(domain)
    elif "https:" not in domain:
        if not domain.startswith("http"):
            domain = "http://" + domain
        if domain.endswith("pypi"):
            domain += "/simple/"
        domain += " --trusted-host " + parse_host(domain)
    elif not domain.startswith("http"):
        domain = (
            "http://"
            + domain.lstrip("/")
            + " --trusted-host "
            + ensure_domain_name(domain)
        )
    try:
        cmd = "{} -m pip download -i {} --isolated six".format(get_python(True), domain)
    except ConfigError:
        cmd = ping_command(ensure_domain_name(domain))
    else:
        if tmp:
            cmd += " -d /tmp"
    print("Checking whether {} reachable...".format(repr(domain)))
    if os.system(cmd) == 0:
        if not cmd.startswith("ping"):
            dirname = "/tmp" if tmp else "."
            for name in os.listdir(dirname):
                if name.startswith("six-") and name.endswith(".whl"):
                    os.remove(os.path.join(dirname, name))
        return True
    return False


def ensure_domain_name(host):
    # type: (str) -> str
    if "/" not in host:
        return host
    domain = host.split("://", 1)[-1].split("/", 1)[0]
    return domain


def is_pip_ready(py="python"):
    # type: (str) -> bool
    return os.system("{py} -m pip --version".format(py=py)) == 0


def check_url_reachable(url):
    # type: (str) -> bool
    try:
        from urllib.request import urlopen as _urlopen

        urlopen = functools.partial(_urlopen, timeout=5)
    except ImportError:
        from urllib import urlopen as _urlopen  # type:ignore

        class Response(object):
            def __init__(self, status):
                self.status = status

        @contextlib.contextmanager
        def urlopen(url):  # type:ignore
            f = _urlopen(url)
            r = f.read()
            status = 200 if r else 400
            yield Response(status)

    try:
        with urlopen(url) as response:
            if response.status == 200:
                return True
    except Exception as e:
        print(e)
        pass
    return False


def build_mirror_url(host):
    # type: (str) -> str
    if host.startswith("http"):
        url = host
    elif "/" not in host:
        url = "http://" + host
        if "pypi" not in host:
            url += "/pypi"
        url += "/simple/"
    else:
        url = "http://" + host
        if "simple" not in host:
            url += url.rstrip("/") + "/simple/"
    return url


def ping_command(domain):
    # type: (str) -> str
    # Cost about 11 seconds to ping mirrors.cloud.aliyuncs.com
    return "ping -c 1 {}".format(domain)


def is_pingable(host="", is_windows=False, domain=""):
    # type: (str, bool,str) -> bool
    host = host or domain
    if is_windows:
        # 2024.12.23 Windows may need administrator to run `ping -c 1 xxx`
        # So use `pip download ...` instead.
        if is_pip_ready():
            return check_mirror_by_pip_download(host)
        else:
            url = build_mirror_url(host)
            return check_url_reachable(url)
    domain = ensure_domain_name(host)
    try:
        socket.gethostbyname(domain)
    except Exception:
        return False
    else:
        if is_pip_ready(get_python()):
            return check_mirror_by_pip_download(host, tmp=True)
        return check_url_reachable(build_mirror_url(host))
    return os.system(ping_command(domain)) == 0


def load_bool(name):
    # type: (str) -> bool
    v = os.getenv(name)
    if not v:
        return False
    return v.lower() in ("1", "yes", "on", "true", "y")


def is_tx_cloud_server(is_windows=False):
    # type: (bool) -> bool
    return is_pingable(SOURCES["tx_ecs"], is_windows=is_windows)


def is_ali_cloud_server(is_windows=False):
    # type: (bool) -> bool
    return is_pingable(SOURCES["ali_ecs"], is_windows=is_windows)


def is_hw_inner(is_windows=False):
    # type: (bool) -> bool
    return is_pingable(_hw_inner_source, is_windows=is_windows)


def parse_host(url):
    # type: (str) -> str
    return url.split("://", 1)[-1].split("/", 1)[0]


def run_and_echo(cmd, dry=False):
    # type: (str, bool) -> int
    print("--> " + cmd)
    sys.stdout.flush()
    if dry:
        return 1
    return os.system(cmd)


def capture_output(cmd):
    # type: (str) -> str
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True)
    except (TypeError, AttributeError):  # For python<=3.6
        with os.popen(cmd) as p:
            return p.read().strip()
    else:
        return r.stdout.decode(errors="ignore").strip()


def config_by_cmd(url, is_windows=False):
    # type: (str, bool) -> None
    if is_windows:
        _config_by_cmd(url, is_windows=True)
    elif System.is_mac():
        # MacOS need sudo to avoid PermissionError
        _config_by_cmd(url, sudo=True)
    else:
        _config_by_cmd(url, is_windows=is_windows)


class ExtraIndex:
    caching = {}  # type: dict[str, Optional[tuple[str, str]]]

    def __init__(self, host):
        self._host = host

    def get(self):
        # type: () -> Optional[tuple[str, str]]
        host = self._host
        if host in self.caching:
            return self.caching[host]
        value = self.caching[host] = self.get_extra_index(host)
        return value

    @staticmethod
    def get_extra_index(host):
        # type: (str) -> Optional[tuple[str, str]]
        if host not in _hw_inner_source:
            return None
        extra_host = host.replace("mirrors", "socapi").replace("tools", "cloudbu")
        try:
            socket.gethostbyname(ensure_domain_name(extra_host))
        except socket.gaierror:
            print("Ignore {} as it's not pingable".format(extra_host))
            return None
        extra_index = _hw_inner_source.replace(host, extra_host)
        extra_index_url = INDEX_URL.replace("https", "http").format(extra_index)
        return extra_host, extra_index_url


def _config_by_cmd(url, sudo=False, is_windows=False):
    # type: (str, bool, bool) -> int
    cmd = CONF_PIP + url
    if not url.startswith("https"):
        print("cmd = {}".format(repr(cmd)))
        host = parse_host(url)
        extra_info = ExtraIndex(host).get()
        if extra_info is not None:
            extra_host, extra_index_url = extra_info
            cmd += " && pip config set global.extra-index-url " + extra_index_url
            host = '"{host} {extra_host}"'.format(host=host, extra_host=extra_host)
        cmd += " && pip config set global.trusted-host " + host
    if sudo:
        cmd = " && ".join("sudo " + i.strip() for i in cmd.split("&&"))
    return run_and_echo(cmd, dry="--dry" in sys.argv)


def smart_detect(source, is_windows):
    # type: (str, bool) -> tuple[str, bool]
    if is_windows:
        if is_hw_inner(True):
            return "hw_inner", True
    elif not System.is_mac():
        mirror_map = {
            "huawei": (is_hw_inner, "hw_inner"),
            "tencent": (is_tx_cloud_server, "tx_ecs"),
            "aliyun": (is_ali_cloud_server, "ali_ecs"),
        }
        mirrors = []
        welcome_file = "/etc/motd"
        if os.path.exists(welcome_file):
            with open(welcome_file) as f:
                msg = f.read().strip()
        else:
            msg = capture_output("{} -m pip config list".format(get_python()))
        if msg:
            mirrors = [v for k, v in mirror_map.items() if k in msg.lower()]
        if not mirrors:
            mirrors = list(mirror_map.values())
        for detect_func, source_name in mirrors:
            if detect_func(False):
                return source_name, True
    return source, False


def detect_inner_net(source, verbose=False, is_windows=False):
    # type: (str, bool, bool) -> str
    args = sys.argv[1:]
    inner = False
    if not args or all(i.startswith("-") for i in args):
        source, inner = smart_detect(source, is_windows=is_windows)
    elif source in ("huawei", "hw"):
        if is_hw_inner(is_windows):
            source = "hw_inner"
            inner = True
    elif "ali" in source:
        if is_ali_cloud_server(is_windows):
            source = "ali_ecs"
            inner = True
    elif "tx" in source or "ten" in source:
        inner = is_tx_cloud_server(is_windows)
        source = "tx_ecs" if inner else "tx"
    if verbose and inner:
        print("Use {} as it's pingable".format(source))
    return source


def build_index_url(source, force, verbose=False, strict=False, is_windows=False):
    # type: (str, bool, bool, bool, bool) -> str
    if source.startswith("http"):
        return source
    if not force:
        source = detect_inner_net(source, verbose, is_windows=is_windows)
    if source in ("hw_inner", "hw_ecs"):
        host = _hw_inner_source
    elif strict:
        try:
            host = SOURCES[source]
        except KeyError:
            raise ParamError(  # noqa: B904
                "Unknown source: {}\nAvailables: {}".format(repr(source), list(SOURCES))
            )
    else:
        host = SOURCES.get(source, SOURCES[DEFAULT])
    url = INDEX_URL.format(host)
    if source in ("hw_inner", "hw_ecs", "tx_ecs", "ali_ecs"):
        url = url.replace("https", "http")
    return url


def get_parent_path(path):
    # type: (str) -> str
    return os.path.dirname(path.rstrip("/").rstrip("\\"))


def get_conf_path(is_windows, at_etc):
    # type: (bool, bool) -> str
    if is_windows:
        _pip_conf = ("pip", "pip.ini")
        conf_file = os.path.join(os.path.expanduser("~"), *_pip_conf)
    else:
        if at_etc:
            conf_file = os.path.join("/etc", "pip.conf")
        else:
            _pip_conf = (".pip", "pip.conf")
            conf_file = os.path.join(os.path.expanduser("~"), *_pip_conf)
    parent = get_parent_path(conf_file)
    if not os.path.exists(parent):
        os.mkdir(parent)
    return conf_file


class PdmMirror:
    @staticmethod
    def set(url, verify_ssl=False):
        # type: (str, bool) -> int
        cmd = "pdm config pypi.url " + url
        host = parse_host(url)
        if url.startswith("https:") and not verify_ssl:
            cmd = "pdm config pypi.verify_ssl false && " + cmd
        extra_info = ExtraIndex(host).get()
        if extra_info is not None:
            extra_host, extra_index_url = extra_info
            cmd += " && pdm config pypi.extra.url " + extra_index_url
            if extra_index_url.startswith("https:") and not verify_ssl:
                cmd += " && pdm config pypi.extra.verify_ssl false"
        return run_and_echo(cmd, dry="--dry" in sys.argv)


class Mirror:
    def __init__(self, url, is_windows, replace):
        # type: (str, bool, bool) -> None
        self.url = url
        self.is_windows = is_windows
        self.replace = replace
        self._version = ""

    @property
    def tool(self):
        # type: () -> str
        return self.__class__.__name__.replace("Mirror", "").lower()

    def prompt_y(self, filename, content):
        print("The {}'s {} content:".format(self.tool, filename))
        print(content)
        print('If you want to replace it, rerun with "-y" in args.')
        print("Exit!")

    def check_installed(self):
        # type: () -> Optional[bool]
        if self.tool == "poetry":
            not_install = run_and_echo(self.tool + " check --quiet") > 256
        else:
            not_install = run_and_echo(self.tool + " --version") != 0
        if not_install:
            msg = (
                "{0} not found!\n"
                "You can install it by:\n"
                "    pip install --user --upgrade pipx\n"
                "    pipx install {0}\n"
            )
            print(msg.format(self.tool))
            return True


class UvMirror(Mirror):
    GITHUB_PROXY = "https://hub.gitmirror.com/"
    PYTHON_DOWNLOAD_URL = (
        "https://github.com/astral-sh/python-build-standalone/releases/download"
    )
    TEMPLATE = 'python-install-mirror = "{}"'
    _python = False

    @staticmethod
    def allow_insecure(url):
        # type: (str) -> str
        if url.startswith("https"):
            return ""
        return '\nallow-insecure-host=["{}"]'.format(parse_host(url))

    @classmethod
    def python_install_mirror(cls):
        # type: () -> str
        return cls.TEMPLATE.format(cls.GITHUB_PROXY + cls.PYTHON_DOWNLOAD_URL)

    def build_content(self, url=None, extra_index=None):
        # type: (Optional[str], Optional[str]) -> str
        if url is None:
            url = self.url
        text = '[[index]]\nurl = "{}"\ndefault = true'.format(
            url
        ) + self.allow_insecure(url)
        if extra_index is None:
            extra_info = ExtraIndex(parse_host(url)).get()
            if extra_info is not None:
                _, extra_index = extra_info
        if extra_index:
            text += '\n[[index]]\nurl = "{}"'.format(extra_index) + self.allow_insecure(
                extra_index
            )
        return self.set_python(text)

    def set_python(self, text):
        # type: (str) -> str
        if self._python:
            text = self.python_install_mirror() + "\n\n" + text
        return text

    def set(self, set_python_mirror=False):
        # type: (bool) -> Optional[int]
        self._python = set_python_mirror
        filename = "uv.toml"
        dirpath = self.get_dirpath(self.is_windows, self.url, filename)
        if not dirpath:
            return 1
        config_toml_path = os.path.join(dirpath, filename)
        text = self.build_content()
        if os.path.exists(config_toml_path):
            with open(config_toml_path) as f:
                content = f.read().strip()
            if text in content:
                print("uv mirror set as expected. Skip!")
                return None
            if "index-url" in content:
                pattern = r'index-url\s*=\s*"([^"]*)"'
                m = re.search(pattern, content, re.S)
                if m:
                    already = m.group(1)
                    if not self.replace:
                        self.prompt_y(filename, m.group())
                        return None
                    if self.url.startswith("https"):
                        text = self.set_python(content.replace(already, self.url))
            elif "[[index]]" in content:
                pattern = r'url\s*=\s*"([^"]*)"'
                m = re.search(pattern, content, re.S)
                if m:
                    already = m.group(1)
                    if not self.replace:
                        self.prompt_y(filename, m.group())
                        return None
                    if self.url.startswith("https"):
                        text = self.set_python(content.replace(already, self.url))
        elif not os.path.exists(dirpath):
            parent = get_parent_path(dirpath)
            if not os.path.exists(parent):
                os.mkdir(parent)
            os.mkdir(dirpath)
        do_write(config_toml_path, text)

    def _get_dirpath(self, is_windows, filename, is_etc=False):
        # type: (bool, str, bool) -> str
        if is_etc:
            parent = (
                os.path.join(os.environ["SYSTEMDRIVE"], "ProgramData")
                if is_windows
                else os.getenv("XDG_CONFIG_DIRS", "/etc")
            )
        else:
            default = "~/.config"
            env_key = "APPDATA" if is_windows else "XDG_CONFIG_HOME"
            parent = os.path.expanduser(os.getenv(env_key, default))
        return os.path.join(parent, "uv")

    def get_dirpath(self, is_windows, url, filename):
        # type: (bool, str, str) -> Optional[str]
        if self.check_installed():
            return None
        return self._get_dirpath(is_windows, filename)


class PoetryMirror(Mirror):
    plugin_name = "poetry-plugin-pypi-mirror"
    extra_plugins = [  # You can set PIP_CONF_NO_EXTRA_POETRY_PLUGINS=1 to skip install extra plugins
        "poetry-dotenv-plugin",
        "poetry-plugin-i",
        "poetry-plugin-version",
    ]

    def fix_poetry_v1_6_error(self, version):
        # type: (str) -> None
        if version.startswith("1.6."):
            self.fix_v1_6_error()

    @classmethod
    def fix_v1_6_error(cls):
        # type: () -> None
        pipx_envs = capture_output("pipx environment")
        env_key = "PIPX_LOCAL_VENVS"
        key = "PIPX_HOME"
        module = cls.plugin_name.replace("-", "_")
        filename = "plugins.py"
        if env_key in pipx_envs:
            path = pipx_envs.split(env_key + "=")[1].splitlines()[0]
            lib = os.path.join(path, "poetry/lib")
            ds = os.listdir(lib)
            file = os.path.join(lib, ds[0], "site-packages", module, filename)
        elif key in pipx_envs:
            path = pipx_envs.split(key + "=")[1].splitlines()[0]
            lib = os.path.join(path, "venvs/poetry/lib")
            ds = os.listdir(lib)
            file = os.path.join(lib, ds[0], "site-packages", module, filename)
        else:
            code = "import {} as m;print(m.__file__)".format(module)
            path = capture_output("{} -c {}".format(get_python(), repr(code)))
            file = os.path.join(get_parent_path(path), filename)
        if not os.path.exists(file):
            print("WARNING: plugin file not found {}".format(file))
            return
        s = "semver"
        with open(file) as f:
            text = f.read()
        if s in text:
            text = text.replace(s, "constraints")
            with open(file, "w") as f:
                f.write(text)
            print("pypi mirror plugin error fixed.")

    @property
    def poetry_version(self):
        # type: () -> str
        if not self._version:
            self._version = self.get_poetry_version()
        self.fix_poetry_v1_6_error(self._version)
        return self._version

    @staticmethod
    def get_poetry_version():
        # type: () -> str
        v = capture_output("poetry --version")
        return v.replace("Poetry (version ", "")

    @staticmethod
    def unset():
        # type: () -> None
        print("By pipx:\n", "pipx runpip poetry uninstall <plugin-name>")
        print("By poetry self:\n", "poetry self remove <plugin-name>")

    def set_self_pypi_mirror(self, is_windows, url):
        # type: (bool, str) -> None
        config_path = self._get_dirpath(is_windows)
        if not os.path.exists(os.path.join(config_path, "pyproject.toml")):
            try:
                from poetry.console.commands.self.self_command import SelfCommand
            except ImportError:
                pass
            else:
                SelfCommand().generate_system_pyproject()
        cmds = [
            "cd {}".format(config_path),
            "poetry source add -v --priority=default pypi_mirror {}".format(url),
        ]
        run_and_echo(" && ".join(cmds), dry="--dry" in sys.argv)

    def get_dirpath(self, is_windows, url):
        # type: (bool, str) -> Optional[str]
        if self.check_installed():
            return None
        plugins = capture_output("poetry self show plugins")
        mirror_plugin = self.plugin_name
        if mirror_plugin not in plugins:
            if run_and_echo("pipx --version") == 0:
                install_plugin = "pipx inject poetry "
            else:
                self.set_self_pypi_mirror(is_windows, url)
                install_plugin = "poetry self add "
            dry = "--dry" in sys.argv
            if run_and_echo(install_plugin + mirror_plugin, dry=dry) != 0:
                print("Failed to install plugin: {}".format(repr(mirror_plugin)))
                return None
            if not load_bool("PIP_CONF_NO_EXTRA_POETRY_PLUGINS"):
                cmd = install_plugin + " ".join(self.extra_plugins)
                run_and_echo(cmd, dry=dry)
        return self._get_dirpath(is_windows)

    def _get_dirpath(self, is_windows):
        # type: (bool) -> str
        dirpath = "~/Library/Application Support/pypoetry/"
        if is_windows:
            dirpath = os.getenv("APPDATA", "") + "/pypoetry/"
        elif not System.is_mac():
            dirpath = "~/.config/pypoetry/"
        elif self.poetry_version < "1.5":
            dirpath = "~/Library/Preferences/pypoetry/"
        return os.path.expanduser(dirpath)

    def set(self):
        # type: () -> Optional[int]
        filename = "config.toml"
        dirpath = self.get_dirpath(self.is_windows, self.url)
        if not dirpath:
            return 1
        config_toml_path = os.path.join(dirpath, filename)
        item = "[plugins.pypi_mirror]"
        text = item + '{}url = "{}"'.format(os.linesep, self.url)
        if os.path.exists(config_toml_path):
            with open(config_toml_path) as f:
                content = f.read().strip()
            if text in content:
                print("poetry mirror set as expected. Skip!")
                return None
            if item in content:
                pattern = r'\[plugins\.pypi_mirror\].url = "([^"]*)"'
                m = re.search(pattern, content, re.S)
                if m:
                    already = m.group(1)
                    if not self.replace:
                        self.prompt_y(filename, m.group())
                        return None
                    text = content.replace(already, self.url)
            else:
                text = content + os.linesep + text
        elif not os.path.exists(dirpath):
            parent = get_parent_path(dirpath)
            if not os.path.exists(parent):
                os.mkdir(parent)
            os.mkdir(dirpath)
        do_write(config_toml_path, text)


def init_pip_conf(
    url,
    replace=False,
    at_etc=False,
    write=False,
    poetry=False,
    pdm=False,
    verbose=False,
    uv=False,
    is_windows=False,
    verify_ssl=False,
    set_python_mirror=False,
):
    # type: (str, bool, bool, bool, bool, bool, bool, bool, bool, bool, bool) -> Optional[int]
    if poetry:
        return PoetryMirror(url, is_windows, replace).set()
    poetry_set_env = "SET_POETRY"
    if load_bool(poetry_set_env):
        env_name = "PIP_CONF_POETRY_MIRROR"
        v = os.getenv(env_name)
        if v:
            tip = "Poetry mirror source will be set to {}"
            print(tip.format(repr(v)))
            url = build_index_url(
                v, force=True, verbose=True, strict=True, is_windows=is_windows
            )
            replace = True
        elif verbose:
            tip = "Going to configure poetry mirror source, because {} was set to {}"
            print(tip.format(repr(poetry_set_env), os.getenv(poetry_set_env)))
        return PoetryMirror(url, is_windows, replace).set()
    if pdm or load_bool("PIP_CONF_SET_PDM"):
        return PdmMirror.set(url, verify_ssl)
    if uv or load_bool("PIP_CONF_SET_UV"):
        set_python_mirror = set_python_mirror or load_bool("PIP_CONF_PYTHON_MIRROR")
        return UvMirror(url, is_windows, replace).set(set_python_mirror)
    if not write and (not at_etc or is_windows) and can_set_global():
        config_by_cmd(url, is_windows)
        return None
    text = TEMPLATE.format(url, parse_host(url))
    conf_file = get_conf_path(is_windows, at_etc)
    if os.path.exists(conf_file):
        with open(conf_file) as fp:
            s = fp.read()
        if text in s:
            print("Pip source already be configured as expected.\nSkip!")
            return None
        if not replace:
            print("The pip file {} exists! content:".format(conf_file))
            print(s)
            print('If you want to replace it, rerun with "-y" in args.\nExit!')
            return None
    do_write(conf_file, text)


def do_write(conf_file, text):
    # type: (str, str) -> None
    with open(conf_file, "w") as fp:
        fp.write(text + "\n")
    print("Write lines to `{}` as below:\n{}\n".format(conf_file, text))
    print("Done.")


def can_set_global():
    # type: () -> bool
    s = capture_output("pip --version")
    m = re.search(r"^pip (\d+)\.(\d+)", s)
    if not m:
        return False
    return [int(i) for i in m.groups()] >= [10, 1]


def read_lines(filename):
    # type: (str) -> list[str]
    with open(filename) as f:
        s = f.read()
    return s.splitlines()


def auto_detect_tool(args):
    # type: (Namespace) -> Namespace
    if args.tool == "pip":
        return args
    if args.tool in ("uv", "poetry", "pdm"):
        setattr(args, args.tool, True)
    elif args.tool != "auto":
        raise ValueError("Unknown tool: " + repr(args.tool))
    else:
        files = os.listdir(".")
        pyproject = "pyproject.toml"
        locks = {"uv.lock", "poetry.lock", "pdm.lock"} - set(files)
        if len(locks) == 1:
            tool = list(locks)[0].split(".")[0]
        elif pyproject not in files:
            return args  # Same as args.tool == 'pip'
        else:
            tools = set()  # type: set[str]
            for line in read_lines(pyproject):
                if not line:
                    continue
                elif line.startswith("build-backend"):
                    m = re.search(r"(uv|pdm|poetry)", line)
                    if m:
                        tools = {m.group(1)}
                        break
                else:
                    m = re.match(r"\[\[?tool\.(uv|pdm|poetry)[.\]]", line)
                    if m:
                        tools.add(m.group(1))
            if len(tools) == 1:
                tool = list(tools)[0]
            else:  # Can't determine which tool, change pip mirror only.
                return args
        if is_command_exists(tool):
            setattr(args, tool, True)
    return args


def main():
    # type: () -> Optional[int]
    from argparse import ArgumentParser

    parser = ArgumentParser()
    source_help = "the source of pip, ali/douban/hw/qinghua or tx(default)"
    parser.add_argument("name", nargs="?", default="", help=source_help)
    # Be compatible with old version
    parser.add_argument("-s", "--source", default=DEFAULT, help=source_help)
    # Not support yet.
    # parser.add_argument("files", nargs="*", default="", help="Add for pre-commit")
    parser.add_argument(
        "-l", "--list", action="store_true", help="Show available mirrors"
    )
    parser.add_argument("-y", action="store_true", help="whether replace existing file")
    parser.add_argument("--etc", action="store_true", help="Set conf file to /etc")
    parser.add_argument("-f", action="store_true", help="Force to skip ecs cloud check")
    parser.add_argument("--write", action="store_true", help="Conf by write file")
    parser.add_argument("--poetry", action="store_true", help="Set mirrors for poetry")
    parser.add_argument("--pdm", action="store_true", help="Set pypi.url for pdm")
    parser.add_argument("--verify_ssl", action="store_true", help="Verify ssl for pdm")
    parser.add_argument("--uv", action="store_true", help="Set index url for uv")
    parser.add_argument(
        "--python", action="store_true", help="Set python download mirror url for uv"
    )
    parser.add_argument("--pip", action="store_true", help="Set index url for pip")
    parser.add_argument(
        "-t", "--tool", default="auto", help="Choices: pip/uv/pdm/poetry"
    )
    parser.add_argument("--url", action="store_true", help="Show mirrors url")
    parser.add_argument(
        "--dry",
        action="store_true",
        help="Display cmd command without actually executing",
    )
    parser.add_argument("--verbose", action="store_true", help="Print more info")
    parser.add_argument("--version", action="store_true", help="Show script version")
    parser.add_argument(
        "--fix", action="store_true", help="Fix poetry pypi mirror plugin error"
    )
    if not sys.argv[1:]:
        # In case of runing by curl result, try to get args from ENV
        env = os.getenv("PIP_CONF_ARGS")
        if env:
            sys.argv.extend(env.split())
    args = parser.parse_args()
    if args.list:
        print("There are several mirrors that can be used for pip/uv/pdm/poetry:")
        sources = (
            SOURCES
            if args.verbose
            else ({k: v for k, v in SOURCES.items() if len(k) > 3 and k != "tengxun"})
        )
        pprint.pprint(sources)
    elif args.fix:
        PoetryMirror.fix_v1_6_error()
    elif args.version:
        print("pip-conf-mirror {}".format(__version__))
    else:
        source = args.name or args.source
        is_windows = System.is_win()
        url = build_index_url(source, args.f, args.verbose, is_windows=is_windows)
        if args.url:  # Only display prefer source url, but not config
            print(url)
            return None
        if not args.poetry and not args.pdm and not args.uv and not args.pip:
            args = auto_detect_tool(args)
            if (
                args.tool == "auto"
                and any([args.poetry, args.pdm, args.uv])
                and ("index-url" not in capture_output("pip config list"))
            ):
                # Config mirror for pip before configure mirror of manage tool
                init_pip_conf(
                    url,
                    replace=args.y,
                    at_etc=args.etc,
                    write=args.write,
                    verbose=args.verbose,
                    is_windows=is_windows,
                )
        if init_pip_conf(
            url,
            replace=args.y,
            at_etc=args.etc,
            write=args.write,
            poetry=args.poetry,
            pdm=args.pdm,
            verbose=args.verbose,
            uv=args.uv,
            is_windows=is_windows,
            verify_ssl=args.verify_ssl,
            set_python_mirror=args.python,
        ):
            return 1


if __name__ == "__main__":
    if "--url" not in sys.argv and "--list" not in sys.argv:
        try:
            from asynctor import timeit
        except (ImportError, SyntaxError, AttributeError):
            pass
        else:
            main = timeit(main)  # Display script cost time
    sys.exit(main())
