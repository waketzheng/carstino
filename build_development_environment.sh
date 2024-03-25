SUDO="sudo"
if [ "$USER" = "root" ]; then
  SUDO=""
else
  echo "This script need root permission."
  sudo echo "Go ahead..."
fi
starttime=`date +'%Y-%m-%d %H:%M:%S'`

echo "---- Set default python"
which python || $SUDO ln `which python3` /usr/bin/python
echo "---- Change mirror sources"
$SUDO ./change_ubuntu_mirror_sources.sh
echo "Updating Repo and install prerequisites..."
$SUDO apt update
$SUDO apt-get install -y build-essential libssl-dev

echo "---- Install rabbitmq/postgresql/redis/pip"
$SUDO apt install -y rabbitmq-server  # for Celery
$SUDO apt install -y postgresql
$SUDO apt install -y redis-server
$SUDO apt install -y python3-pip

echo "---- [postgres] change default password to postgres"
$SUDO -u postgres psql -U postgres -d postgres -c "alter user postgres with password 'postgres';"
# $SUDO -u postgres psql -U postgres -d postgres -c "create database carstino_dev encoding='utf-8';"

echo "---- Setup RabbitMQ"
$SUDO rabbitmqctl add_user waket 123456
$SUDO rabbitmqctl set_user_tags waket administrator
# $SUDO rabbitmqctl add_vhost carstino
# $SUDO rabbitmqctl set_permissions -p carstino waket ".*" ".*" ".*"

echo "---- Set auto start services"
$SUDO systemctl enable postgresql || ($SUDO chkconfig --add postgresql && $SUDO chkconfig postgresql on)
$SUDO systemctl enable redis-server || ($SUDO chkconfig --add redis-server && $SUDO chkconfig redis-server on)
$SUDO systemctl enable rabbitmq-server || ($SUDO chkconfig --add rabbitmq-server && $SUDO chkconfig rabbitmq-server)

echo "---- Install python development tools"
$SUDO apt install -y python3-dev bzip2 libbz2-dev libxml2-dev libxslt1-dev zlib1g-dev libffi-dev

echo "---- Optional: install tree expect, etc."
$SUDO apt install -y tree httpie expect

# https://stackoverflow.com/questions/2829613/how-do-you-tell-if-a-string-contains-another-string-in-posix-sh
# contains(string, substring)
#
# Returns 0 if the specified string contains the specified substring,
# otherwise returns 1.
contains() {
    string="$1"
    substring="$2"
    if test "${string#*$substring}" != "$string"
    then
        return 0    # $substring is in $string
    else
        return 1    # $substring is not in $string
    fi
}
contains $* "--upgrade-py" && echo "---- Optional: install python3.11" && ./upgrade_py.py && python3.11 -m pip install --user -U pip -i https://pypi.tuna.tsinghua.edu.cn/simple && python3.11 -m ensurepip && export PATH="$HOME/.local/bin:/usr/local/bin:$PATH"

echo "---- Optional: install zsh"
bash ohmyzsh.sh

echo "---- Init python development environment."
python3 init_my_dev.py

echo "If you want to configure frontend development evironment, do this:"
echo "    $ ./frontend_conf.sh"

# Count cost seconds
endtime=`date +'%Y-%m-%d %H:%M:%S'`
start_seconds=$(date --date="$starttime" +%s);
end_seconds=$(date --date="$endtime" +%s);
echo "Cost: "$((end_seconds-start_seconds))"s"
