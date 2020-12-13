# Carstino
This is a repo about init my dev environment

1. a script to init my development environment at a new machine.
2. Some useful scripts for linux os system.

## scripts:
- rstrip.py: strip white spaces at the end of every line.
- pip_conf.py: switch pip source to aliyun or douban or qinghua.
- change_ubuntu_mirror_sources.sh: change apt mirror sources of ubuntu16/18/19/20
- createdatabase.py: create database for django project
- .switch_source_pipenv.py: switch pip source of Pipfile
- build_development_environment.sh: install packages for python and vue develop environment


Usage:
```bash
# Change source of pip to aliyun.com, worked at both Linux and Windows(Run with Git Bash).
curl https://raw.githubusercontent.com/waketzheng/carstino/master/pip_conf.py|python
```

```bash
# Change apt source of ubuntu16/18/19/20 to aliyun cloud.
curl https://raw.githubusercontent.com/waketzheng/carstino/master/change_ubuntu_mirror_sources.py|python
```

```bash
# Swith source of pipenv to aliyun
curl https://raw.githubusercontent.com/waketzheng/carstino/master/.switch_source_pipenv.py|python
```

- init_my_dev.py: setting for vim, git store, pipenv aliases.

PS: I usually init my development environment in a new machine as following

```bash
git clone https://github.com/waketzheng/carstino.git
cd carstino
./init_my_dev.py
```

- build_development_environment.sh: For new ubuntu machine(version>=16), just run this script.
```bash
git clone https://github.com/waketzheng/carstino.git
cd carstino
./build_development_environment.sh
```
