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
  # boxes at https://vagrantcloud.com/search.
  config.vm.box = "ubuntu/bionic64"

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

  # Provider-specific configuration so you can fine-tune various
  # backing providers for Vagrant. These expose provider-specific options.
  # Example for VirtualBox:
  #
  config.vm.provider "virtualbox" do |vb|
    # Display the VirtualBox GUI when booting the machine
    vb.gui = true

    # Customize the amount of memory on the VM:
    vb.memory = "1024"
    vb.cpus = 2
  end
  #
  # View the documentation for the provider you are using for more
  # information on available options.

  # Enable provisioning with a shell script. Additional provisioners such as
  # Puppet, Chef, Ansible, Salt, and Docker are also available. Please see the
  # documentation for more information about their specific syntax and use.
  config.vm.provision "shell", inline: <<-SHELL

  echo "Setup repo mirror"

  sed -i "s|http://archive.ubuntu.com|https://mirrors.aliyun.com|g" /etc/apt/sources.list

  echo "Add postgresql repo"
  echo "deb https://mirrors.tuna.tsinghua.edu.cn/postgresql/repos/apt xenial-pgdg main" | tee /etc/apt/sources.list.d/postgresql.list
  wget --quiet -O - https://mirrors.tuna.tsinghua.edu.cn/postgresql/repos/apt/ACCC4CF8.asc | apt-key add -

  echo "Update Repo"
  apt-get update

  echo "Install"
  apt-get install -y rabbitmq-server
  apt-get install -y postgresql-9.6
  apt-get install -y redis-server
  apt-get install -y ruby-sass

  echo "Install python software properties"
  apt-get install -y python-software-properties

  echo "Install python development tools"
  apt-get install -y python3-pip python3-dev bzip2 libbz2-dev libxml2-dev libxslt1-dev zlib1g-dev libffi-dev libssl-dev

  echo "switch pip source to aliyun, then install pipenv and ipython"
  su vagrant -c 'mkdir ~/.pip'
  su vagrant -c 'echo "
  [global]
  index-url = https://mirrors.aliyun.com/pypi/simple/
  [install]
  trusted-host = mirrors.aliyun.com
  ">~/.pip/pip.conf'
  mkdir .pip&&cp /home/vagrant/.pip/pip.conf .pip/
  su vagrant -c 'pip3 install pipenv'
  python3 -m pip install ipython django autopep8 flake8 pylint white

  echo "Optional: custom vim config, aliases, django manage.py command auto completion"
  export repo="https://github.com/waketzheng/letstype"
  su vagrant -c 'wget $repo/raw/master/.vimrc -O ~/.vimrc'
  su vagrant -c 'wget $repo/raw/master/.switch_source_pipenv.py -O ~/.switch_source_pipenv.py'
  su vagrant -c 'wget $repo/raw/master/.bash_aliases -O ~/.bash_aliases'
  wget $repo/raw/master/django_manage.bash -O /etc/bash_completion.d/django_manage.bash

  echo "Optional: auto store git password for push to http repo"
  su vagrant -c 'git config --global credential.helper store'

  echo "Setup postgres"
  echo "[postgres] Update listen_address"
  sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/g" /etc/postgresql/9.6/main/postgresql.conf
  echo "[postgres] Update default_transaction_isolation"
  sed -i "s/#default_transaction_isolation = 'read committed'/default_transaction_isolation = 'read committed'/g" \
  /etc/postgresql/9.6/main/postgresql.conf

  echo "[postgres] Enable access from 10.0.x.x"
  echo "host all all 10.0.0.0/16 md5" >> /etc/postgresql/9.6/main/pg_hba.conf

  echo "[postgres] change default password to postgres"
  sudo -u postgres psql -U postgres -d postgres -c "alter user postgres with password 'postgres';"
  sudo -u postgres psql -U postgres -d postgres -c "create database concise_dev encoding='utf-8';"

  echo "Setup redis"
  sed -i "s/bind 127.0.0.1/bind 0.0.0.0/g" /etc/redis/redis.conf

  echo "Setup RabbitMQ"
  rabbitmqctl add_user rabbitmq rabbitmq
  rabbitmqctl add_vhost rabbitmq_vhost
  rabbitmqctl set_user_tags rabbitmq test_only
  rabbitmqctl set_permissions -p rabbitmq_vhost rabbitmq ".*" ".*" ".*"

  echo "Set auto start services"
  /lib/systemd/systemd-sysv-install enable postgresql
  /lib/systemd/systemd-sysv-install enable redis-server
  /lib/systemd/systemd-sysv-install enable rabbitmq-server

  echo "Restart services"
  systemctl restart postgresql
  systemctl restart redis-server

  echo "Over."

  SHELL
end
