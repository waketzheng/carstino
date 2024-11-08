#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
This script is for pip source config.
Worked both Windows and Linux/Mac, support python2.7 and python3.5+
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Usage:
    $ ./pip_conf.py  # default to tencent source

Or:
    $ python pip_conf.py tx
    $ python pip_conf.py huawei
    $ python pip_conf.py aliyun
    $ python pip_conf.py douban
    $ python pip_conf.py qinghua

    $ python pip_conf.py https://pypi.mirrors.ustc.edu.cn/simple  # conf with full url

    $ python pip_conf.py --list  # show choices
    $ python pip_conf.py --poetry  # set mirrors in poetry's config.toml
    $ python pip_conf.py --pdm  # set pypi.url for pdm

    $ sudo python pip_conf.py --etc  # Set conf to /etc/pip.[conf|ini]

If there is any bug or feature request, report it to:
    https://github.com/waketzheng/carstino/issues
"""

__author__ = "waketzheng@gmail.com"
__updated_at__ = "2024.11.08"
__version__ = "0.5.1"
import os
import platform
import pprint
import re
import socket
import subprocess
import sys

try:
    import typing
except ImportError:
    pass
else:
    if typing.TYPE_CHECKING:
        from typing import Optional  # NOQA:F401

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
    "aliyun": "mirrors.aliyun.com/pypi",
    "douban": "pypi.douban.com",
    "qinghua": "pypi.tuna.tsinghua.edu.cn",
    "tx": "mirrors.cloud.tencent.com/pypi",
    "tx_ecs": "mirrors.tencentyun.com/pypi",
    "huawei": "repo.huaweicloud.com/repository/pypi",
    "ali_ecs": "mirrors.cloud.aliyuncs.com/pypi",
    "pypi": "pypi.org",
}
SOURCES["tencent"] = SOURCES["tengxun"] = SOURCES["tx"]
SOURCES["ali"] = SOURCES["aliyun"]
SOURCES["hw"] = SOURCES["huawei"]
SOURCES["hw_inner"] = SOURCES["hw_ecs"] = (
    SOURCES["hw"]
    .replace("cloud", "")
    .replace("/repository", "")
    .replace("repo", "mirrors.tools")
)
CONF_PIP = "pip config set global.index-url "
INDEX_URL = "https://{}/simple/"


class ParamError(Exception):
    """Invalid parameters"""


def is_pingable(domain):
    # type: (str) -> bool
    if "/" in domain:
        domain = domain.split("/")[0]
    try:
        socket.gethostbyname(domain)
    except Exception:
        return False
    return os.system("ping -c 1 {}".format(domain)) == 0


def load_bool(name):
    # type: (str) -> bool
    v = os.getenv(name)
    if not v:
        return False
    return v.lower() in ("1", "yes", "on", "true", "y")


def is_tx_cloud_server():
    # type: () -> bool
    return is_pingable(SOURCES["tx_ecs"])


def is_ali_cloud_server():
    # type: () -> bool
    return is_pingable(SOURCES["ali_ecs"])


def is_hw_inner():
    # type: () -> bool
    return is_pingable(SOURCES["hw_inner"])


def parse_host(url):
    # type: (str) -> str
    return url.split("://", 1)[1].split("/", 1)[0]


def run_and_echo(cmd):
    # type: (str) -> int
    print("--> " + cmd)
    sys.stdout.flush()
    return os.system(cmd)


def config_by_cmd(url, is_windows=False):
    # type: (str, bool) -> None
    if not is_windows and platform.system() == "Darwin":
        # MacOS need sudo to avoid PermissionError
        _config_by_cmd(url, sudo=True)
    else:
        _config_by_cmd(url)


def _config_by_cmd(url, sudo=False):
    # type: (str, bool) -> int
    cmd = CONF_PIP + url
    if not url.startswith("https"):
        print("cmd = {}".format(repr(cmd)))
        host = parse_host(url)
        if host in SOURCES["hw_inner"]:
            extra_host = host.replace("mirrors", "socapi").replace("tools", "cloudbu")
            try:
                socket.gethostbyname(extra_host.split("://")[-1].split("/")[0])
            except socket.gaierror:
                print("Ingore {} as it's not pingable".format(extra_host))
            else:
                extra_index = SOURCES["hw_inner"].replace(host, extra_host)
                extra_index_url = INDEX_URL.replace("https", "http").format(extra_index)
                cmd += " && pip config set global.extra-index-url " + extra_index_url
                host = '"{host} {extra_host}"'.format(host=host, extra_host=extra_host)
        cmd += " && pip config set global.trusted-host " + host
    if sudo:
        cmd = " && ".join("sudo " + i.strip() for i in cmd.split("&&"))
    return run_and_echo(cmd)


def detect_inner_net(source, verbose=False):
    # type: (str, bool) -> str
    args = sys.argv[1:]
    inner = False
    if not args or all(i.startswith("-") for i in args):
        if is_hw_inner():
            source = "hw_inner"
            inner = True
        elif is_tx_cloud_server():
            source = "tx_ecs"
            inner = True
        elif is_ali_cloud_server():
            source = "ali_ecs"
            inner = True
    elif source in ("huawei", "hw"):
        if is_hw_inner():
            source = "hw_inner"
            inner = True
    elif "ali" in source:
        if is_ali_cloud_server():
            source = "ali_ecs"
            inner = True
    elif "tx" in source or "ten" in source:
        inner = is_tx_cloud_server()
        source = "tx_ecs" if inner else "tx"
    if verbose and inner:
        print("Use {} as it's pingable".format(source))
    return source


def build_index_url(source, force, verbose=False, strict=False):
    # type: (str, bool, bool, bool) -> str
    if source.startswith("http"):
        return source
    if not force:
        source = detect_inner_net(source, verbose)
    if strict:
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
    parent = os.path.dirname(conf_file)
    if not os.path.exists(parent):
        os.mkdir(parent)
    return conf_file


def capture_output(cmd):
    # type: (str) -> str
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True)
    except (TypeError, AttributeError):  # For python<=3.6
        with os.popen(cmd) as p:
            return p.read().strip()
    else:
        return r.stdout.decode().strip()


class PdmMirror:
    @staticmethod
    def set(url):
        # type: (str) -> int
        cmd = "pdm config pypi.url " + url
        if url.startswith("http:"):
            cmd += " && pdm config pypi.verify_ssl false"
        return run_and_echo(cmd)


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
    def build_content(self, url=None):
        # type: (Optional[str]) -> str
        if url is None:
            url = self.url
        text = 'index-url="{}"'.format(url)
        if not url.startswith("https"):
            domain = parse_host(url)
            text += os.linesep + 'allow-insecure-host=["{}"]'.format(domain)
        return text

    def set(self):
        # type: () -> Optional[int]
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
                        text = content.replace(already, self.url)
        elif not os.path.exists(dirpath):
            parent = os.path.dirname(dirpath)
            if not os.path.exists(parent):
                os.mkdir(parent)
            os.mkdir(dirpath)
        do_write(config_toml_path, text)

    def _get_dirpath(self, is_windows, filename):
        # type: (bool, str) -> str
        if is_windows:
            parent = os.getenv("APPDATA", "~")
        else:
            parent = os.getenv("XDG_CONFIG_HOME", "")
            if not parent:
                parent = "~"
            else:
                parent = os.path.expanduser(parent)
                uv_dir = os.path.join(parent, "uv")
                if os.path.exists(os.path.join(uv_dir, filename)):
                    return uv_dir
                uv_dir = os.path.join(os.path.expanduser("~"), "uv")
                if os.path.exists(os.path.join(uv_dir, filename)):
                    return uv_dir
        return os.path.join(os.path.expanduser(parent), "uv")

    def get_dirpath(self, is_windows, url, filename):
        # type: (bool, str, str) -> Optional[str]
        if self.check_installed():
            return None
        return self._get_dirpath(is_windows, filename)


class PoetryMirror(Mirror):
    plugin_name = "poetry-plugin-pypi-mirror"

    def fix_poetry_v1_6_error(self, version):
        # type: (str) -> None
        if version >= "1.6":
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
            path = capture_output("python -c {}".format(repr(code)))
            file = os.path.join(os.path.dirname(path), filename)
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
        run_and_echo(" && ".join(cmds))

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
            if run_and_echo(install_plugin + mirror_plugin) != 0:
                print("Failed to install plugin: {}".format(repr(mirror_plugin)))
                return None
            if not load_bool("PIP_CONF_NO_EXTRA_POETRY_PLUGINS"):
                run_and_echo(
                    install_plugin
                    + "poetry-dotenv-plugin poetry-plugin-i poetry-plugin-version"
                )
        return self._get_dirpath(is_windows)

    def _get_dirpath(self, is_windows):
        # type: (bool) -> str
        dirpath = "~/Library/Preferences/pypoetry/"
        if is_windows:
            dirpath = os.getenv("APPDATA", "") + "/pypoetry/"
        elif platform.system() != "Darwin":
            dirpath = "~/.config/pypoetry/"
        elif self.poetry_version >= "1.5":
            dirpath = "~/Library/Application Support/pypoetry/"
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
            parent = os.path.dirname(dirpath)
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
):
    # type: (str, bool, bool, bool, bool, bool, bool, bool) -> Optional[int]
    is_windows = platform.system() == "Windows"
    if poetry:
        return PoetryMirror(url, is_windows, replace).set()
    poetry_set_env = "SET_POETRY"
    if load_bool(poetry_set_env):
        env_name = "PIP_CONF_POETRY_MIRROR"
        v = os.getenv(env_name)
        if v:
            tip = "Poetry mirror source will be set to {}"
            print(tip.format(repr(v)))
            url = build_index_url(v, force=True, verbose=True, strict=True)
            replace = True
        elif verbose:
            tip = "Going to configure poetry mirror source, because {} was set to {}"
            print(tip.format(repr(poetry_set_env), os.getenv(poetry_set_env)))
        return PoetryMirror(url, is_windows, replace).set()
    if pdm or load_bool("PIP_CONF_SET_PDM"):
        return PdmMirror.set(url)
    if uv or load_bool("PIP_CONF_SET_UV"):
        return UvMirror(url, is_windows, replace).set()
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


def main():
    # type: () -> Optional[int]
    from argparse import ArgumentParser

    parser = ArgumentParser()
    source_help = "the source of pip, ali/douban/huawei/qinghua or tx(default)"
    parser.add_argument("name", nargs="?", default="", help=source_help)
    parser.add_argument("files", nargs="*", default="", help="Add for pre-commit")
    # Be compatible with old version
    parser.add_argument("-s", "--source", default=DEFAULT, help=source_help)
    parser.add_argument(
        "-l", "--list", action="store_true", help="Show available mirrors"
    )
    parser.add_argument("-y", action="store_true", help="whether replace existing file")
    parser.add_argument("--etc", action="store_true", help="Set conf file to /etc")
    parser.add_argument("-f", action="store_true", help="Force to skip ecs cloud check")
    parser.add_argument("--write", action="store_true", help="Conf by write file")
    parser.add_argument("--poetry", action="store_true", help="Set mirrors for poetry")
    parser.add_argument("--pdm", action="store_true", help="Set pypi.url for pdm")
    parser.add_argument("--uv", action="store_true", help="Set index url for uv")
    parser.add_argument("--url", action="store_true", help="Show mirrors url")
    parser.add_argument("--verbose", action="store_true", help="Print more info")
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
        print("There are several mirrors that can be used for pip/poetry:")
        pprint.pprint(SOURCES)
    elif args.fix:
        PoetryMirror.fix_v1_6_error()
    else:
        source = args.name or args.source
        url = build_index_url(source, args.f, args.verbose)
        if args.url:
            print(url)
            return None
        if init_pip_conf(
            url,
            replace=args.y,
            at_etc=args.etc,
            write=args.write,
            poetry=args.poetry,
            pdm=args.pdm,
            verbose=args.verbose,
            uv=args.uv,
        ):
            return 1


if __name__ == "__main__":
    if "--url" not in sys.argv:
        try:
            from asynctor import timeit
        except (ImportError, SyntaxError, AttributeError):
            pass
        else:
            main = timeit(main)
    sys.exit(main())
