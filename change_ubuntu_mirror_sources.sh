#!/bin/bash
SUDO=""
if [ $USER ] && [ $USER != "root" ]; then
  SUDO="sudo"
fi
MIRROR="repo.huaweicloud.com"

do_sed() {
  # cd到源列表所在目录 -->  备份原文件 --> 替换为华为源
  cd /etc/apt  && \
    ([ -f sources.list.origin ] || ${SUDO} cp sources.list sources.list.origin ) && \
    ${SUDO} sed -i 's/^\(deb\|deb-src\) \([^ ]*\) \(.*\)/\1 http:\/\/'$MIRROR'\/ubuntu\/ \3/' sources.list
}

if [ -f change_ubuntu_mirror_sources.py ]; then
  (${SUDO} which python && ${SUDO} python change_ubuntu_mirror_sources.py $*) || \
  (${SUDO} which python3 && ${SUDO} python3 change_ubuntu_mirror_sources.py $*) || \
  $(do_sed) && echo "Mirrors in /etc/apt/sources.list was set to be '$MIRROR'"
else
  $(do_sed) && echo "Mirrors in /etc/apt/sources.list was set to be '$MIRROR'"
fi
