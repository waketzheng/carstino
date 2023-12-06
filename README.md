# Carstino
This is a repo about init my dev environment

1. a script to init my development environment at a new machine.
2. Some useful scripts for linux os system.

## scripts:
- rstrip.py: strip white spaces at the end of every line.
- pip_conf.py: switch pip source to aliyun or douban or qinghua.
- change_ubuntu_mirror_sources.sh: change apt mirror sources of ubuntu16/18/19/20/22
- createdatabase.py: create database for django project
- build_development_environment.sh: install packages for python and vue develop environment
- upgrade_py.sh: make it easy for ubuntu to install python


Usage:
```bash
# Change source of pip to mirrors.cloud.tencent.com, worked at both Linux and Windows(Run with Git Bash).
curl https://raw.githubusercontent.com/waketzheng/carstino/master/pip_conf.py|python
```

```bash
# Change apt source of ubuntu16/18/19/20 to tencent cloud.
curl https://raw.githubusercontent.com/waketzheng/carstino/master/change_ubuntu_mirror_sources.py|python
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
./build_development_environment.sh
```
## SSH script
- Initial
```bash
cd
mkdir archives
cd archives
git clone https://github.com/waketzheng/carstino.git
cd carstino
cp to_my_server.sh ${ANY_PATH}/any_name.sh
vi ${ANY_PATH}/any_name.sh  # change the var of `IP_OR_DOMAIN`
```
- Usage
1. ssh to your server
```bash
sh ${ANY_PATH}/any_name.sh
```
2. scp file or directory to your server
```bash
sh ${ANY_PATH}/any_name.sh /path/to/file_or_directory
```
3. scp file or directory from server to local
```bash
sh ${ANY_PATH}/any_name.sh /path/in/server/file_or_directory /local/path/
```
