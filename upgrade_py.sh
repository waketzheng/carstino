#!/bin/bash
# Sometimes there has `python3` instead of `python` in system

GITHUB_RAW="https://raw.githubusercontent.com/waketzheng/carstino/master"
if [ $RAW_URL ]; then
  if [ $RAW_URL == "gitee" ]; then
    RAW_URL="https://gitee.com/waketzheng/carstino/raw/master"
  elif [ $RAW_URL == "github" ]; then
    RAW_URL=$GITHUB_RAW
  fi
  starttime=`date +'%Y-%m-%d %H:%M:%S'`
  echo Current time is $starttime
else
  RAW_URL=$GITHUB_RAW
fi

([ -s upgrade_py.py ] || wget $RAW_URL/upgrade_py.py) && \
  echo Going to install python. This will cost several minutes... && \
  (
    (which python && python upgrade_py.py $*) || \
    (which python3 && python3 upgrade_py.py $*)
  )
