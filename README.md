# Carstino
This is a repo about init my

1. a script to init my development environment at a new machine.
2. Some useful scripts for linux os system.

## scripts:
- rstrip.py: strip white spaces at the end of every line.
- pip_conf.py: switch pip source to aliyun or douban or qinghua.
- change_ubuntu_mirror_sources.py: change apt mirror sources of ubuntu16/18
- createdatabase.py: create database for django project
- django_manage_completion.bash: auto completion for my custom command `mg`, which is for django manage
- prettify.py: auto reformat javascript files
- .switch_source_pipenv.py: switch pip source of Pipfile


Usage:
```bash
curl https://raw.githubusercontent.com/waketzheng/carstino/master/pip_conf.py|python
```

- init_my_dev.py: setting for vim, git store, pipenv aliases.

PS: I usually init my development environment in a new machine as following

```bash
git clone https://github.com/waketzheng/carstino.git
cd carstino
./init_my_dev.py
```
