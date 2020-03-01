# TODO: check whether it work as expected.
echo "This script need root permission."
sudo echo "Go ahead..."

echo "---- Set default python"
which python || sudo ln `which python3` /usr/bin/python
sudo ./change_ubuntu_mirror_sources.py
echo "Updating Repo..."
sudo apt update
sudo apt-get install -y build-essential libssl-dev

echo "---- Install rabbitmq/postgresql/redis/sass/pip/nodejs/npm"
sudo apt install -y rabbitmq-server  # for Celery
sudo apt install -y postgresql
sudo apt install -y redis-server
sudo apt install -y ruby-sass  # for Django compress
sudo apt install -y python3-pip

echo "---- [postgres] change default password to postgres"
sudo -u postgres psql -U postgres -d postgres -c "alter user postgres with password 'postgres';"
sudo -u postgres psql -U postgres -d postgres -c "create database carstino_dev encoding='utf-8';"

echo "---- Setup RabbitMQ"
sudo rabbitmqctl add_user waket 123456
sudo rabbitmqctl add_vhost carstino
sudo rabbitmqctl set_user_tags waket administrator
sudo rabbitmqctl set_permissions -p carstino waket ".*" ".*" ".*"

echo "---- Set auto start services"
sudo systemctl enable postgresql
sudo systemctl enable redis-server
sudo systemctl enable rabbitmq-server

echo "---- Install python development tools"
sudo apt install -y python3-dev bzip2 libbz2-dev libxml2-dev libxslt1-dev zlib1g-dev libffi-dev

echo "---- nodejs/npm/yarn/vue for frontend"
sudo apt install -y nodejs
sudo apt install -y npm
npm config set registry https://registry.npm.taobao.org
sudo npm i -g npm
sudo npm i -g yarn
yarn config set registry https://registry.npm.taobao.org -g
yarn config set sass_binary_site http://cdn.npm.taobao.org/dist/node-sass -g
yarn global add @vue/cli

echo "---- Optional install nvm to manage nodejs version"
git clone https://gitee.com/waketzheng/nvm.git ~/.nvm && cd ~/.nvm && git checkout `git describe --abbrev=0 --tags`
./install.sh
source ./nvm.sh
cd -
nvm node_mirror https://npm.taobao.org/mirrors/node/
nvm npm_mirror https://npm.taobao.org/mirrors/npm/

echo "---- Optional: install tree tmux, etc."
sudo apt install -y tree tmux httpie expect

echo "---- Optional: install python3.8"
./upgrade_py.py

echo "---- Init python development environment."
./init_my_dev.py

echo "---- Optional: install zsh"
sudo apt install -y zsh
sudo python -c "fn='/etc/pam.d/chsh';a,b='required','sufficient';fp=open(fn);s=fp.read();fp.close();fp=open(fn,'w');fp.write(s.replace(a,b));fp.close()"
# sudo python -c "fn='/etc/pam.d/chsh';a,b='required','sufficient';fp=open(fn,'a+');s=fp.read();fp.truncate();fp.write(s.replace(b,a));fp.close()"
chsh -s $(which zsh)
sh -c 'echo "[ -s \$HOME/.bash_aliases ] && source \$HOME/.bash_aliases" >> $HOME/.zshrc'
sh -c 'echo "[ -s \$HOME/.local/bin ] && export PATH=\$HOME/.local/bin:/usr/local/bin:\$PATH" >> $HOME/.zshrc'
sh -c "$(curl -fsSL https://www.shequyi.fun/media/install-oh-my-zsh.sh)"
