#!/bin/bash
# ----------------------------------------
# This script resolve the following cases:
# 1. Sometimes there is no `python` command in the system,
#    but actually it does have python executable, and the name is `python3`.
# 2. When the py script not exist, wget it from HTTP.
# ----------------------------------------

GITHUB_RAW="https://raw.githubusercontent.com/waketzheng/carstino/main"
if [[ $RAW_URL ]]; then
  if [[ $RAW_URL == "gitee" ]]; then
    RAW_URL="https://gitee.com/waketzheng/carstino/raw/master"
  elif [[ $RAW_URL == "github" ]]; then
    RAW_URL=$GITHUB_RAW
  fi
  starttime=`date +'%Y-%m-%d %H:%M:%S'`
  echo Current time is $starttime
elif [[ $RAW_HOST ]]; then
  RAW_URL="$RAW_HOST/waketzheng/carstino/main"
else
  RAW_URL=$GITHUB_RAW
fi

([ -s upgrade_py.py ] || wget $RAW_URL/upgrade_py.py) && \
  echo Going to install python. This will cost several minutes... && \
  (
    (which python && python upgrade_py.py $*) || \
    (which python3 && python3 upgrade_py.py $*)
  )
