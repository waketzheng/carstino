echo "This script need root permission."
sudo echo "Go ahead..."
starttime=`date +'%Y-%m-%d %H:%M:%S'`

echo "---- Set default python"
which python || sudo ln `which python3` /usr/bin/python
echo "---- Change mirror sources"
sudo ./change_ubuntu_mirror_sources.sh
echo "Updating Repo and install prerequisites..."
sudo apt update
sudo apt-get install -y build-essential libssl-dev

echo "---- Install rabbitmq/postgresql/redis/pip"
sudo apt install -y rabbitmq-server  # for Celery
sudo apt install -y postgresql
sudo apt install -y redis-server
sudo apt install -y python3-pip

echo "---- [postgres] change default password to postgres"
sudo -u postgres psql -U postgres -d postgres -c "alter user postgres with password 'postgres';"
# sudo -u postgres psql -U postgres -d postgres -c "create database carstino_dev encoding='utf-8';"

echo "---- Setup RabbitMQ"
sudo rabbitmqctl add_user waket 123456
sudo rabbitmqctl set_user_tags waket administrator
# sudo rabbitmqctl add_vhost carstino
# sudo rabbitmqctl set_permissions -p carstino waket ".*" ".*" ".*"

echo "---- Set auto start services"
sudo systemctl enable postgresql || (sudo chkconfig --add postgresql && sudo chkconfig postgresql on)
sudo systemctl enable redis-server || (sudo chkconfig --add redis-server && sudo chkconfig redis-server on)
sudo systemctl enable rabbitmq-server || (sudo chkconfig --add rabbitmq-server && sudo chkconfig rabbitmq-server)

echo "---- Install python development tools"
sudo apt install -y python3-dev bzip2 libbz2-dev libxml2-dev libxslt1-dev zlib1g-dev libffi-dev

echo "---- Optional: install tree expect, etc."
sudo apt install -y tree httpie expect

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
sudo apt install -y zsh
sudo python -c "fn='/etc/pam.d/chsh';a,b='required','sufficient';fp=open(fn);s=fp.read();fp.close();fp=open(fn,'w');fp.write(s.replace(a,b));fp.close()"
# sudo python -c "fn='/etc/pam.d/chsh';a,b='required','sufficient';fp=open(fn,'a+');s=fp.read();fp.truncate();fp.write(s.replace(b,a));fp.close()"
chsh -s $(which zsh)
sh -c 'echo "[ -s \$HOME/.bash_aliases ] && source \$HOME/.bash_aliases" >> $HOME/.zshrc'
sh -c 'echo "[ -s \$HOME/.local/bin ] && export PATH=\$HOME/.local/bin:/usr/local/bin:\$PATH" >> $HOME/.zshrc'
sh -c 'echo "export ZSH=\$HOME/.oh-my-zsh" >>  $HOME/.zshrc'
sh -c 'echo "ZSH_THEME=random" >>  $HOME/.zshrc'
sh -c 'echo "plugins=(git pip python pipenv)" >>  $HOME/.zshrc'
sh -c 'echo "[ -s \$ZSH/oh-my-zsh.sh ] && source \$ZSH/oh-my-zsh.sh" >>  $HOME/.zshrc'

export REMOTE="https://gitee.com/mirrors/oh-my-zsh.git" && sh -c "$(curl -fsSL https://gitee.com/mirrors/oh-my-zsh/raw/master/tools/install.sh)" --keep-zshrc


echo "---- Init python development environment."
./init_my_dev.py

echo "If you want to configure frontend development evironment, do this:"
echo "    $ ./frontend_conf.sh"

# Count cost seconds
endtime=`date +'%Y-%m-%d %H:%M:%S'`
start_seconds=$(date --date="$starttime" +%s);
end_seconds=$(date --date="$endtime" +%s);
echo "Cost: "$((end_seconds-start_seconds))"s"
