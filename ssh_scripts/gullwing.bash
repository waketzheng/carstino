#!/usr/bin/expect
set host "USER@www.gullwing.cn"
set passwd "PASSWD"
spawn ssh $host
expect {
    "yes/no" { send "yes\r"; exp_continue}
    "password:" { send "$passwd\r" }
}
interact
