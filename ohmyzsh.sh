#!/bin/bash
"""Use this script to install zsh and change default shell to it, then install ohmyzsh"""
if [ "$USER" = "root" ]; then
  SUDO=""
else
  echo "This script need root permission."
  sudo echo "Go ahead..."
  SUDO="sudo"
fi
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

if [[ -v OMZ_REPO ]]; then
  echo use $OMZ_REPO for oh-my-zsh installing
else
  if [[ -v USE_GITEE ]]; then
    OMZ_REPO="https://gitee.com/mirrors/oh-my-zsh"
  else
    OMZ_REPO="https://github.com/ohmyzsh/oh-my-zsh"
  fi
fi
export REMOTE="$OMZ_REPO.git" && sh -c "$(curl -fsSL $OMZ_REPO/raw/master/tools/install.sh)" --keep-zshrc
