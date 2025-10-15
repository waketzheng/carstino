#!/bin/bash
# Doc: https://github.com/waketzheng/carstino#ssh-script
#SSH_USER=root
#PORT=22
#PRI=~/.ssh/id_rsa
#passwd='my password is xxx'

FILE=$0  # filename of this script (xxx_<ip>.sh)
STEM=$(basename $FILE .sh)  # parse file stem (xxx_<ip>)
if [ -f /usr/bin/rev ]; then
    IP_OR_DOMAIN=$(echo $STEM | rev | cut -d '_' -f 1 | rev)  # split by '_' and get the last element (<ip>)
else
    IP_OR_DOMAIN=$(STEM=$STEM python -c "import os;stem=os.getenv('STEM');ip=stem.split('_')[-1];print(ip,end='')")
fi

SSH_USER=$SSH_USER SSH_PASS=$passwd DEST=$IP_OR_DOMAIN PRI=$PRI PORT=$PORT sh ~/archives/carstino/.from_here_to_there.sh $1 $2
