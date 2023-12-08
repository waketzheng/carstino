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
$SUDO apt install -y zsh
if [ -f /etc/pam.d/chsh ]; then
  # Make `chsh` no need to input password
  # $SUDO python -c "fn='/etc/pam.d/chsh';a,b='required','sufficient';fp=open(fn,'a+');s=fp.read();fp.truncate();fp.write(s.replace(b,a));fp.close()"
  $SUDO python -c "fn='/etc/pam.d/chsh';a,b='required','sufficient';fp=open(fn);s=fp.read();fp.close();fp=open(fn,'w');fp.write(s.replace(a,b));fp.close()"
fi
chsh -s $(which zsh)
sh -c 'echo "[ -s \$HOME/.bash_aliases ] && source \$HOME/.bash_aliases" >> $HOME/.zshrc'
sh -c 'echo "[ -s \$HOME/.local/bin ] && export PATH=\$HOME/.local/bin:/usr/local/bin:\$PATH" >> $HOME/.zshrc'
sh -c 'echo "export ZSH=\$HOME/.oh-my-zsh" >>  $HOME/.zshrc'
sh -c 'echo "ZSH_THEME=random" >>  $HOME/.zshrc'
sh -c 'echo "plugins=(git pip python poetry)" >>  $HOME/.zshrc'
sh -c 'echo "[ -s \$ZSH/oh-my-zsh.sh ] && source \$ZSH/oh-my-zsh.sh" >>  $HOME/.zshrc'

if [ -v OMZ_REPO ]; then
  echo use $OMZ_REPO for oh-my-zsh installing
else
  if [ -v USE_GITHUB ]; then
    OMZ_REPO="https://github.com/ohmyzsh/oh-my-zsh"
  else
    OMZ_REPO="https://gitee.com/mirrors/oh-my-zsh"
  fi
fi
export REMOTE="$OMZ_REPO.git" && sh -c "$(curl -fsSL $OMZ_REPO/raw/master/tools/install.sh)" --keep-zshrc


echo "---- Init python development environment."
./init_my_dev.py

echo "If you want to configure frontend development evironment, do this:"
echo "    $ ./frontend_conf.sh"

# Count cost seconds
endtime=`date +'%Y-%m-%d %H:%M:%S'`
start_seconds=$(date --date="$starttime" +%s);
end_seconds=$(date --date="$endtime" +%s);
echo "Cost: "$((end_seconds-start_seconds))"s"
