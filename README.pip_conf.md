# PIP CONF MIRROR

Make it easy for pip/uv/pdm/poetry to change mirror

Python工具包之一行命令换源

## Install

```bash
pip install pip-conf-mirror
```
Or:
```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple pip-conf-mirror
```
Or:
```bash
pipx install pip-conf-mirror
```
Or:
```bash
uv tool install pip-conf-mirror
```
## Usage
```bash
pip-conf-mirror --pip qinghua  # 给pip/pipx换清华源
pip-conf-mirror --uv aliyun  # 给uv换阿里源
pip-conf-mirror --pdm tencent  # 给pdm换腾讯源
pip-conf-mirror --poetry huawei  # 给poetry换华为源
pip-conf-mirror --tool=pip douban  # 给pip/pipx换豆瓣源
```
给uv换好源之后，也可以这样用：
```bash
uvx pip-conf-mirror --pip qh  # 给pip更换清华源
```
展示可选的镜像源：
```
pip-conf-mirror --list
```
- 注：名称为`_ecs`结尾的，只能用在他们自家的服务器上

## From github
- Change source of pip to mirrors.cloud.tencent.com, worked at both Linux and Windows(Run with Git Bash).
```bash
curl https://raw.githubusercontent.com/waketzheng/carstino/main/pip_conf.py|python
```
- Install it from github:
```bash
pip install --user "pip-conf-mirror @git+https://github.com/waketzheng/carstino"
```
- Clone source from github and run by python:
```bash
git clone https://github.com/waketzheng/carstino
# Or:
#git clone git@github.com:waketzheng/carstino.git
python carstino/pip_conf.py --pip qh
```
