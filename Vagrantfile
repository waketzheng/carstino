#!/usr/bin/env bash
# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure("2") do |config|
  # The most common configuration options are documented and commented below.
  # For a complete reference, please see the online documentation at
  # https://docs.vagrantup.com.

  # Every Vagrant development environment requires a box. You can search for
  # boxes at https://vagrantcloud.com/search or https://mirrors.tuna.tsinghua.edu.cn
  # Add required box of this vagrant file by the following line:
  # vagrant box add https://mirrors.tuna.tsinghua.edu.cn/ubuntu-cloud-images/eoan/current/eoan-server-cloudimg-amd64-vagrant.box --name ubuntu/eoan
  config.vm.box = "ubuntu/eoan"

  config.vm.hostname = "carstino"

  # If get this error `/sbin/mount.vboxsf: mounting failed with the error:`
  # look at this: https://github.com/scotch-io/scotch-box/issues/296
  # which suggest to run the following commands:
  # vagrant plugin install vagrant-vbguest && vagrant vbguest && vagrant reload
  config.vm.synced_folder ".", "/carstino", type: "rsync"

  config.vm.boot_timeout = 600

  # Disable automatic box update checking. If you disable this, then
  # boxes will only be checked for updates when the user runs
  # `vagrant box outdated`. This is not recommended.
  # config.vm.box_check_update = false

  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine. In the example below,
  # accessing "localhost:8080" will access port 80 on the guest machine.
  # NOTE: This will enable public access to the opened port
  # config.vm.network "forwarded_port", guest: 80, host: 8080

  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine and only allow access
  # via 127.0.0.1 to disable public access

  # 9000 for django debug
  config.vm.network "forwarded_port", guest: 9000, host: 9000

  # 5002 for flask debug
  config.vm.network "forwarded_port", guest: 5002, host: 5002

  # for vue
  config.vm.network "forwarded_port", guest: 8080, host: 8088

  # forwarded redis
  config.vm.network "forwarded_port", guest: 6379, host: 6379, host_ip: "127.0.0.1"
  # forwarded postgresql
  config.vm.network "forwarded_port", guest: 5432, host: 5432, host_ip: "127.0.0.1"
  # forwarded rabbitmq
  config.vm.network "forwarded_port", guest: 5672, host: 5672, host_ip: "127.0.0.1"

  # Create a private network, which allows host-only access to the machine
  # using a specific IP.
  # config.vm.network "private_network", ip: "192.168.33.10"

  # Create a public network, which generally matched to bridged network.
  # Bridged networks make the machine appear as another physical device on
  # your network.
  # config.vm.network "public_network"

  # Share an additional folder to the guest VM. The first argument is
  # the path on the host to the actual folder. The second argument is
  # the path on the guest to mount the folder. And the optional third
  # argument is a set of non-required options.
  # config.vm.synced_folder "../data", "/vagrant_data"

  # To set disksize, you may need to run:
  # vagrant plugin install vagrant-disksize
  config.disksize.size = '20GB'

  # Provider-specific configuration so you can fine-tune various
  # backing providers for Vagrant. These expose provider-specific options.
  # Example for VirtualBox:
  config.vm.provider "virtualbox" do |vb|
    # Display the VirtualBox GUI when booting the machine
    #vb.gui = true

    # Customize the amount of memory on the VM:
    vb.memory = "4096"
    vb.cpus = 2
  end
  #
  # View the documentation for the provider you are using for more
  # information on available options.

  # Enable provisioning with a shell script. Additional provisioners such as
  # Puppet, Chef, Ansible, Salt, and Docker are also available. Please see the
  # documentation for more information about their specific syntax and use.
  config.vm.provision "shell", inline: <<-SHELL

  echo "---- Setup repo mirror to qinghua sources."
  cp /etc/apt/sources.list /etc/apt/sources.list.bak
  sed -i "s|http://archive.ubuntu.com|https://mirrors.tuna.tsinghua.edu.cn|g" /etc/apt/sources.list
  sed -i "s|http://security.ubuntu.com|https://mirrors.tuna.tsinghua.edu.cn|g" /etc/apt/sources.list

  echo "---- Add yarn repo"
  curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add -
  echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list
  echo "Updating Repo..."
  apt update

  echo "---- Install rabbitmq/postgresql/redis/sass/pip/yarn"
  apt install -y rabbitmq-server
  apt install -y postgresql
  apt install -y redis-server
  apt install -y ruby-sass
  apt install -y python3-pip
  apt install -y yarn

  echo "---- Set yarn registry"
  yarn config set registry https://mirrors.huaweicloud.com/yarn/

  echo "---- Add global vue-cli"
  yarn global add @vue/cli

  echo "---- Install python development tools"
  apt install -y python3-dev bzip2 libbz2-dev libxml2-dev libxslt1-dev zlib1g-dev libffi-dev libssl-dev

  echo "---- Switch pip source to qinghua, then install pipenv"
  pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple pip -U
  pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
  su vagrant -c 'pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple'
  su vagrant -c 'pip install pipenv --user'

  echo "---- Set default python"
  which python || sudo ln -s `which python3` /usr/bin/python

  echo "---- Optinal: install zsh"
  apt install -y zsh
  sed s/required/sufficient/g -i /etc/pam.d/chsh
  chsh -s $(which zsh)
  su vagrant -c "$(curl -fsSL https://raw.githubusercontent.com/robbyrussell/oh-my-zsh/master/tools/install.sh)"
  su vagrant -c 'echo "[ -s \$HOME/.bash_aliases ] && source \$HOME/.bash_aliases" >> $HOME/.zshrc'
  su vagrant -c 'echo "[ -s \$HOME/.local/bin ] && export PATH=\$HOME/.local/bin:/usr/local/bin:\$PATH" >> $HOME/.zshrc'
  echo "You may need to run 'chsh -s $(which zsh)' and then reboot"

  echo "---- Optional: custom vim config, aliases, django manage.py command auto completion"
  export repo="https://github.com/waketzheng/carstino"
  su vagrant -c 'wget $repo/raw/master/.vimrc -O ~/.vimrc'
  su vagrant -c 'wget $repo/raw/master/.switch_source_pipenv.py -O ~/.switch_source_pipenv.py'
  su vagrant -c 'wget $repo/raw/master/.mg.py -O ~/.mg.py'
  su vagrant -c 'wget $repo/raw/master/.bash_aliases -O ~/.bash_aliases'
  wget $repo/raw/master/django_manage_completion.bash -O /etc/bash_completion.d/django_manage_completion.bash

  echo "---- Optional: install tree tmux, etc."
  apt install -y tree tmux httpie expect
  su vagrant -c "pip install flake8 white black isort --user"
  ln -s $(which python3) /usr/bin/python

  echo "---- Optional: auto store git password for push to http repo"
  su vagrant -c 'git config --global credential.helper store'

  echo "---- Setup postgres"
  echo "[postgres] Update listen_address"
  sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/g" /etc/postgresql/11/main/postgresql.conf
  echo "[postgres] Update default_transaction_isolation"
  sed -i "s/#default_transaction_isolation = 'read committed'/default_transaction_isolation = 'read committed'/g" \
  /etc/postgresql/11/main/postgresql.conf

  echo "---- [postgres] Enable access from 10.0.x.x"
  echo "host all all 10.0.0.0/16 md5" >> /etc/postgresql/11/main/pg_hba.conf

  echo "---- [postgres] change default password to postgres"
  sudo -u postgres psql -U postgres -d postgres -c "alter user postgres with password 'postgres';"
  sudo -u postgres psql -U postgres -d postgres -c "create database carstino_dev encoding='utf-8';"

  echo "---- Setup redis"
  sed -i "s/bind 127.0.0.1/bind 0.0.0.0/g" /etc/redis/redis.conf

  echo "---- Setup RabbitMQ"
  rabbitmqctl add_user rabbitmq rabbitmq
  rabbitmqctl add_vhost rabbitmq_vhost
  rabbitmqctl set_user_tags rabbitmq test_only
  rabbitmqctl set_permissions -p rabbitmq_vhost rabbitmq ".*" ".*" ".*"

  echo "---- Set auto start services"
  systemctl enable postgresql
  systemctl enable redis-server
  systemctl enable rabbitmq-server

  echo "---- Restart services"
  systemctl restart postgresql
  systemctl restart redis-server

  echo "Done."

  SHELL
end
