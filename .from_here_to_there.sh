#!/bin/bash
# Usage::
# DEST=$IP_OR_DOMAIN ~/archives/carstino/.from_here_to_there.sh $1 $2

if [ "$SSH_USER" ]; then
  HOST=$SSH_USER@$DEST
else
  if [ "$USER" = "root" ]; then
    HOST=$DEST
  else
    HOST=root@$DEST
  fi
fi
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
    if [ "$SCP_DIR" ]; then
      echo $SCP_DIR |grep -q '/'
      if [ $? -eq 0 ]; then
        cmd="$cmd $1 $HOST:$SCP_DIR"
      else
        cmd="$cmd $1 $HOST:~/$SCP_DIR"
      fi
    else
      cmd="$cmd $1 $HOST:~/"
    fi
  fi
else
  cmd="ssh"
  if [ $T_HOST ]; then
      cmd="$cmd -t $T_HOST"
  fi
  if [ $PRI ]; then
    cmd="$cmd -i $PRI"
  fi
  if [ $PORT ]; then
    cmd="$cmd -p $PORT"
  fi
  cmd="$cmd $HOST"
fi

if [ "$SSH_PASS" ]; then
  if [ -f /usr/bin/expect ]; then
    EXP_FILE=".do_ssh.exp"
    if [ $1 ]; then
      EXP_FILE=".do_scp.exp"
    fi
    if [ -f ~/archives/carstino/$EXP_FILE ]; then
      EXP_FILE="~/archives/carstino/$EXP_FILE"
    elif [ -f ~/$EXP_FILE ]; then
      EXP_FILE="~/$EXP_FILE"
    elif [ -f $EXP_FILE ]; then
      EXP_FILE="./$EXP_FILE"
    else
      EXP_FILE=""
    fi
    if [ "$EXP_FILE" ]; then
      cmd="$EXP_FILE '$cmd' $SSH_PASS"
    else
      echo "--> $cmd"
      echo "$SSH_PASS"
    fi
  fi
else
  echo "--> $cmd"
fi
sh -c "$cmd"
