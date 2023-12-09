#!/bin/bash
# ----------------------------------------
# This script resolve the following cases:
# 1. Sometimes there is no `python` command in the system,
#    but actually it does have python executable, and the name is `python3`.
# 2. When current user is not root, the py script should be run with `sudo` prefix.
# ----------------------------------------
MIRROR="repo.huaweicloud.com"

SUDO=""
if [ $USER ] && [ $USER != "root" ]; then
  SUDO="sudo"
fi
do_sed() {
  # cd to sources directory -->  backup origin file --> change mirror url
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
