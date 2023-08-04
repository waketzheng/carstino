#!/usr/bin/env python
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
"""
import os
import platform
import pprint
import re
import socket
import subprocess
import sys

"""
A sample of the pip.conf/pip.ini:
```
[global]
index-url = https://mirrors.cloud.tencent.com/pypi/simple/

[install]
trusted-host = mirrors.cloud.tencent.com
```
"""

TEMPLATE = """
[global]
index-url = {}
[install]
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


def is_pingable(domain):
    if "/" in domain:
        domain = domain.split("/")[0]
    try:
        socket.gethostbyname(domain)
    except Exception:
        return False
    return True


def is_tx_cloud_server():
    return is_pingable(SOURCES["tx_ecs"])


def is_ali_cloud_server():
    return is_pingable(SOURCES["ali_ecs"])


def is_hw_inner():
    return is_pingable(SOURCES["hw_inner"])


def parse_host(url):
    return url.split("://", 1)[1].split("/", 1)[0]


def run_and_echo(cmd):
    print("--> " + cmd)
    sys.stdout.flush()
    return os.system(cmd)


def config_by_cmd(url):
    cmd = CONF_PIP + url
    if not url.startswith("https"):
        print("cmd = {}".format(repr(cmd)))
        cmd += " && pip config set install.trusted-host " + parse_host(url)
    return run_and_echo(cmd)


def detect_inner_net(source):
    args = sys.argv[1:]
    if not args or not [i for i in args if not i.startswith("-")]:
        if is_hw_inner():
            source = "hw_inner"
        elif is_tx_cloud_server():
            source = "tx_ecs"
        elif is_ali_cloud_server():
            source = "ali_ecs"
    elif source in ("huawei", "hw"):
        if is_hw_inner():
            source = "hw_inner"
    elif "ali" in source:
        if is_ali_cloud_server():
            source = "ali_ecs"
    elif "tx" in source or "ten" in source:
        if is_tx_cloud_server():
            source = "tx_ecs"
    return source


def build_index_url(source, force):
    if source.startswith("http"):
        return source
    if not force:
        source = detect_inner_net(source)
    host = SOURCES.get(source, SOURCES[DEFAULT])
    url = INDEX_URL.format(host)
    if source in ("hw_inner", "hw_ecs", "tx_ecs", "ali_ecs"):
        url = url.replace("https", "http")
    return url


def get_conf_path(is_windows, at_etc):
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
    if hasattr(subprocess, "run"):  # For python3
        r = subprocess.run(cmd, shell=True, capture_output=True)
        return r.stdout.decode().strip()
    with os.popen(cmd) as p:
        return p.read().strip()


class PdmMirror:
    @staticmethod
    def set(url):
        cmd = "pdm config pypi.url " + url
        if url.startswith("http:"):
            cmd += " && pdm config pypi.verify_ssl false"
        return run_and_echo(cmd)


class PoetryMirror:
    def __init__(self, url, is_windows, replace):
        self.url = url
        self.is_windows = is_windows
        self.replace = replace

    @staticmethod
    def get_poetry_version():
        v = capture_output("poetry --version")
        return v.replace("Poetry (version ", "")

    @staticmethod
    def unset():
        print("By pipx:\n", "pipx runpip poetry uninstall <plugin-name>")
        print("By poetry self:\n", "poetry self remove <plugin-name>")

    def get_dirpath(self, is_windows, url):
        if run_and_echo("poetry --version") != 0:
            print("poetry not found!\nYou can install it by:")
            print("    pip install --user pipx")
            print("    pipx install poetry\n")
            return
        plugins = capture_output("poetry self show plugins")
        mirror_plugin = "poetry-plugin-pypi-mirror"
        if mirror_plugin not in plugins:
            if run_and_echo("pipx --version") == 0:
                install_plugin = "pipx inject poetry "
            else:
                config_path = self._get_dirpath(is_windows)
                if not os.path.exists(os.path.join(config_path, "pyproject.toml")):
                    try:
                        from poetry.console.commands.self.self_command import (
                            SelfCommand,
                        )
                    except (ImportError, ModuleNotFoundError):
                        pass
                    else:
                        SelfCommand().generate_system_pyproject()
                set_self_pypi_mirror = (
                    "cd {} && poetry source add -v --priority=default pypi_mirror {}"
                )
                run_and_echo(set_self_pypi_mirror.format(config_path, url))
                install_plugin = "poetry self add "
            if run_and_echo(install_plugin + mirror_plugin) != 0:
                print("Failed to install plugin: {}".format(repr(mirror_plugin)))
                return
        return self._get_dirpath(is_windows)

    def _get_dirpath(self, is_windows):
        dirpath = "~/Library/Preferences/pypoetry/"
        if is_windows:
            dirpath = os.getenv("APPDATA", "") + "/pypoetry/"
        elif platform.system() != "Darwin":
            dirpath = "~/.config/pypoetry/"
        elif self.get_poetry_version() >= "1.5":
            dirpath = "~/Library/Application Support/pypoetry/"
        return os.path.expanduser(dirpath)

    def set(self):
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
                return
            if item in content:
                pattern = r'\[plugins\.pypi_mirror\].url = "([^"]*)"'
                m = re.search(pattern, content, re.S)
                if m:
                    already = m.group(1)
                    if not self.replace:
                        print("The poetry's config.toml content:")
                        print(m.group())
                        print('If you want to replace it, rerun with "-y" in args.')
                        print("Exit!")
                        return
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
):
    is_windows = platform.system() == "Windows"
    if poetry:
        return PoetryMirror(url, is_windows, replace).set()
    if pdm:
        return PdmMirror.set(url)
    if not write and (not at_etc or is_windows) and can_set_global():
        return config_by_cmd(url)
    text = TEMPLATE.format(url, parse_host(url))
    conf_file = get_conf_path(is_windows, at_etc)
    if os.path.exists(conf_file):
        with open(conf_file) as fp:
            s = fp.read()
        if text in s:
            print("Pip source already be configured as expected.\nSkip!")
            return
        if not replace:
            print("The pip file {} exists! content:".format(conf_file))
            print(s)
            print('If you want to replace it, rerun with "-y" in args.\nExit!')
            return
    do_write(conf_file, text)


def do_write(conf_file, text):
    with open(conf_file, "w") as fp:
        fp.write(text + "\n")
    print("Write lines to `{}` as below:\n{}\n".format(conf_file, text))
    print("Done.")


def can_set_global():
    s = capture_output("pip --version")
    m = re.search(r"^pip (\d+)\.(\d+)", s)
    if not m:
        return False
    return [int(i) for i in m.groups()] >= [10, 1]


def main():
    from argparse import ArgumentParser

    parser = ArgumentParser()
    source_help = "the source of pip, ali/douban/huawei/qinghua or tx(default)"
    parser.add_argument("name", nargs="?", default="", help=source_help)
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
    parser.add_argument("--url", action="store_true", help="Show mirrors url")
    if not sys.argv[1:]:
        # In case of runing by curl result, try to get args from ENV
        env = os.getenv("PIP_CONF_ARGS")
        if env:
            sys.argv.extend(env.split())
    args = parser.parse_args()
    if args.list:
        print("There are several mirrors that can be used for pip/poetry:")
        pprint.pprint(SOURCES)
    else:
        source = args.name or args.source
        url = build_index_url(source, args.f)
        if args.url:
            print(url)
            return
        if init_pip_conf(url, args.y, args.etc, args.write, args.poetry, args.pdm):
            sys.exit(1)


if __name__ == "__main__":
    if "--url" not in sys.argv:
        try:
            from kitty import timeit
        except (ImportError, ModuleNotFoundError):
            pass
        else:
            main = timeit(main)
    main()
