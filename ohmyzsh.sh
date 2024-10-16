#!/bin/bash
echo "Use this script to install zsh and change default shell to it, then install ohmyzsh"
if [ "$USER" = "root" ]; then
  SUDO=""
else
  echo "This script need root permission."
  sudo echo "Go ahead..."
  SUDO="sudo"
fi

if [ -x "$(command -v apt)" ]; then
  $SUDO apt install -y zsh
elif [ -x "$(command -v yum)" ]; then
  $SUDO yum install -y zsh
elif [ -x "$(command -v brew)" ]; then
  brew install zsh
else
  echo You may need to install zsh manually.
fi

if [ -f /etc/pam.d/chsh ]; then
  # Make `chsh` no need to input password
  # $SUDO python -c "fn='/etc/pam.d/chsh';a,b='required','sufficient';fp=open(fn,'a+');s=fp.read();fp.truncate();fp.write(s.replace(b,a));fp.close()"
  $SUDO python -c "fn='/etc/pam.d/chsh';a,b='required','sufficient';fp=open(fn);s=fp.read();fp.close();fp=open(fn,'w');fp.write(s.replace(a,b));fp.close()"
fi
if [ -f /bin/zsh ]; then
  ZSH_EXEC=/bin/zsh
else
  ZSH_EXEC=$(which zsh)
fi
chsh -s $ZSH_EXEC

# Uncomment the following lines to expand PATH and plugins
#sh -c 'echo "[ -s \$HOME/.bash_aliases ] && source \$HOME/.bash_aliases" >> $HOME/.zshrc'
#sh -c 'echo "[ -s \$HOME/.local/bin ] && export PATH=\$HOME/.local/bin:/usr/local/bin:\$PATH" >> $HOME/.zshrc'
#sh -c 'echo "export ZSH=\$HOME/.oh-my-zsh" >>  $HOME/.zshrc'
#sh -c 'echo "ZSH_THEME=random" >>  $HOME/.zshrc'
#sh -c 'echo "plugins=(git pip python poetry)" >>  $HOME/.zshrc'
#sh -c 'echo "[ -s \$ZSH/oh-my-zsh.sh ] && source \$ZSH/oh-my-zsh.sh" >>  $HOME/.zshrc'

if [[ -v REMOTE ]]; then
    echo REMOTE value "$REMOTE" will be used to install ohmyzsh
else
    if [[ -v OMZ_REPO ]]; then
      echo use $OMZ_REPO for oh-my-zsh installing
    else
      if [[ -v USE_GITEE ]]; then
        OMZ_REPO="https://gitee.com/mirrors/oh-my-zsh"
      else
        OMZ_REPO="https://github.com/ohmyzsh/oh-my-zsh"
      fi
    fi
    if [[ $OMZ_REPO == *.git ]]; then
        export REMOTE="$OMZ_REPO"
    else
        export REMOTE="$OMZ_REPO.git"
    fi
fi

if [[ $REMOTE == http* ]]; then
  REMOTE=$REMOTE sh -c "$(curl -fsSL $OMZ_REPO/raw/master/tools/install.sh)" --keep-zshrc
elif [[ $REMOTE == ssh* ]]; then
  cd /tmp
  [ -d ohmyzsh ] || git clone $REMOTE
  REMOTE=$REMOTE ./ohmyzsh/tools/install.sh
fi

# Uncomment the following lines to add custom plugin
#export PLUGIN="zsh-autosuggestions"
#([[ -f $PLUGIN.tar.xz ]] && tar xf $PLUGIN.tar.xz) || ([[ -f $PLUGIN-master.zip ]] && unzip $PLUGIN-master.zip && mv $PLUGIN-master $PLUGIN)
#[[ -d $PLUGIN ]] || git clone ${PLUGIN_REPO:-git@github.com:zsh-users/zsh-autosuggestions.git}
#[[ -d ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/ ]] || mkdir -p ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/
#mv $PLUGIN ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/
#python -c "import os,sys;p=os.path.expanduser('~/.zshrc');f=open(p);s=f.read();f.close();v='zsh-autosuggestions';c='You can run the following command to activate plugin:\n\n    source '+p+'\n';v in s and sys.exit(c);ss=s.splitlines();a='plugins=(';t=[i for i in ss if i.startswith(a)];assert t, 'Failed to auto change, you can manually edit {}'.format(p);line=t[0].replace(a,a+v+' ');new=s.replace(t[0],line);f=open(p,'w');f.write(new);f.close();print(c)"
#source ~/.zshrc
