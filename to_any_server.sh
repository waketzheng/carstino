#!/bin/bash
# Doc: https://github.com/waketzheng/carstino#ssh-script
IP_OR_DOMAIN=$1
#SSH_USER=root
#PORT=22
#PRI=~/.ssh/id_rsa
#passwd='my password is xxx'

SSH_USER=$SSH_USER SSH_PASS=$passwd DEST=$IP_OR_DOMAIN PRI=$PRI PORT=$PORT sh ~/archives/carstino/.from_here_to_there.sh $2 $3
