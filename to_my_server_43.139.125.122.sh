#!/bin/bash
# Doc: https://github.com/waketzheng/carstino#ssh-script
#SSH_USER=root
#PORT=22
#PRI=~/.ssh/id_rsa
#passwd='my password is xxx'

FILE=$0  # filename of this script (xxx_<ip>.sh)
STEM=$(basename $FILE .sh)  # parse file stem (xxx_<ip>)
IP_OR_DOMAIN=$(echo $STEM | rev | cut -d '_' -f 1 | rev)  # split by '_' and get the last element (<ip>)

SSH_USER=$SSH_USER SSH_PASS=$passwd DEST=$IP_OR_DOMAIN PRI=$PRI PORT=$PORT sh ~/archives/carstino/.from_here_to_there.sh $1 $2
