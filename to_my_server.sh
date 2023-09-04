#!/bin/bash
#IP_OR_DOMAIN=www.mydomain.com
IP_OR_DOMAIN=43.139.125.122
USER=ubuntu
#PORT=22
#PRI=~/.ssh/id_rsa
#passwd='my password is xxx'

if [ "$passwd" ]; then
  echo "$passwd"
fi

HOST=$USER@$IP_OR_DOMAIN
if [ $1 ]; then
  cmd="scp -r"
  if [ $PRI ]; then
    cmd="$cmd -i $PRI"
  fi
  if [ $PORT ]; then
    cmd="$cmd -P $PORT"
  fi
  if [ $2 ]; then
    echo $1 |grep -q '/'
    if [ $? -eq 0 ]; then
      cmd="$cmd $HOST:$1 $2"
    else
      cmd="$cmd $HOST:~/$1 $2"
    fi
  else
    cmd="$cmd $1 $HOST:~"
  fi
else
  cmd="ssh"
  if [ $PRI ]; then
    cmd="$cmd -i $PRI"
  fi
  if [ $PORT ]; then
    cmd="$cmd -p $PORT"
  fi
  cmd="$cmd $HOST"
fi

echo "--> $cmd"
sh -c "$cmd"
