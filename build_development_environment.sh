# TODO: check whether it work as expected.
echo "This script need root permission."
sudo echo "---- Add yarn repo"
curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list

echo "---- Set default python"
which python || sudo ln /usr/bin/python `which python3`
sudo ./change_ubuntu_mirror_sources.py
echo "Updating Repo..."
sudo apt update

echo "---- Install rabbitmq/postgresql/redis/sass/pip/yarn"
sudo apt install -y rabbitmq-server
sudo apt install -y postgresql
sudo apt install -y redis-server
sudo apt install -y ruby-sass
sudo apt install -y python3-pip
sudo apt install -y yarn

echo "---- [postgres] change default password to postgres"
sudo -u postgres psql -U postgres -d postgres -c "alter user postgres with password 'postgres';"
sudo -u postgres psql -U postgres -d postgres -c "create database carstino_dev encoding='utf-8';"

echo "---- Setup RabbitMQ"
sudo rabbitmqctl add_user your_name password
sudo rabbitmqctl add_vhost rabbitmq_vhost
sudo rabbitmqctl set_user_tags your_name test_only
sudo rabbitmqctl set_permissions -p rabbitmq_vhost your_name ".*" ".*" ".*"
# Example:
# sudo rabbitmqctl add_user waket 123456
# sudo rabbitmqctl add_vhost carstino
# sudo rabbitmqctl set_user_tags waket administrator
# sudo rabbitmqctl set_permissions -p carstino waket ".*" ".*" ".*"

echo "---- Set auto start services"
sudo systemctl enable postgresql
sudo systemctl enable redis-server
sudo systemctl enable rabbitmq-server

echo "---- Set yarn registry"
yarn config set registry https://registry.npm.taobao.org -g
yarn config set sass_binary_site http://cdn.npm.taobao.org/dist/node-sass -g

echo "---- Add global vue-cli"
yarn global add @vue/cli

echo "---- Install python development tools"
sudo apt install -y python3-dev bzip2 libbz2-dev libxml2-dev libxslt1-dev zlib1g-dev libffi-dev libssl-dev

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
