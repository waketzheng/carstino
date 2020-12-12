([ -s upgrade_py.py ] || wget https://gitee.com/waketzheng/carstino/raw/master/upgrade_py.py) && \
  echo Going to install python. This will cost several minutes... && \
  (
    (which python && python upgrade_py.py $*) || \
    (which python3 && python3 upgrade_py.py $*)
  )
