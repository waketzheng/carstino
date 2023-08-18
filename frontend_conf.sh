#!/bin/bash
# ---- For frontend development
SUDO=""
if [ $USER ] && [ $USER != "root" ]; then
  SUDO="sudo"
fi

if [[ $NPM_MIRROR == "tx" ]]; then
  export NPM_MIRROR="http://mirrors.cloud.tencent.com/npm/"
elif [[ $NPM_MIRROR == "hw" ]]; then
  export NPM_MIRROR=http://mirrors.tools.huawei.com/npm/
elif [[ $NPM_MIRROR == "ali" ]]; then
  export NPM_MIRROR=https://registry.npm.taobao.org
elif [ $NPM_MIRROR ]; then
  echo npm mirror is $NPM_MIRROR
else
  export NPM_MIRROR=http://repo.huaweicloud.com/repository/npm/
fi

(echo "---- Initial nodejs/npm/yarn/pnpm/zx for frontend")
if [[ $1 == "apt" ]] || [[ $1 == "yum" ]]; then
  if ! command -v node  &> /dev/null; then
    $SUDO $1 install -y nodejs
  fi
  if ! command -v npm  &> /dev/null; then
    $SUDO $1 install -y npm
  fi
elif ! command -v nvm  &> /dev/null; then
  (echo "---- Installing nvm to manage nodejs version")
  if [ $NVM_NODEJS_ORG_MIRROR ]; then
    echo NVM_NODEJS_ORG_MIRROR is $NVM_NODEJS_ORG_MIRROR
  else
    export NVM_NODEJS_ORG_MIRROR=http://repo.huaweicloud.com/nodejs/
  fi
  if [[ $NVM_REPO_URL == "github.com" ]]; then
    export NVM_REPO_URL="https://github.com/nvm-sh/nvm.git"
  elif [[ $NVM_REPO_URL == "github" ]]; then
    export NVM_REPO_URL="git@github.com:nvm-sh/nvm.git"
  elif [ $NVM_REPO_URL ]; then
    echo Nvm repo url: $NVM_REPO_URL
  else
    export NVM_REPO_URL="https://gitee.com/mirrors/nvm.git"
  fi
  export NVM_DIR="$HOME/.nvm" && (
    [ -f nvm-master.zip ] && unzip nvm-master.zip && mv nvm-master $NVM_DIR || git clone $NVM_REPO_URL "$NVM_DIR"
    cd "$NVM_DIR"
    [ -f .git/index ] && git checkout `git describe --abbrev=0 --tags --match "v[0-9]*" $(git rev-list --tags --max-count=1)`
  ) && \. "$NVM_DIR/nvm.sh"
  RC_FILE=$HOME/.bashrc
  if [ -f $HOME/.zshrc ]; then
    RC_FILE=$HOME/.zshrc
  fi
  echo '
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion
' >> $RC_FILE
  source $RC_FILE
  nvm install --lts && node -v
else
  echo '`nvm` already installed. Skip!'
fi

if command -v npm  &> /dev/null; then
  npm i -g npm@latest --registry $NPM_MIRROR
  npm config set registry $NPM_MIRROR -g
  if ! command -v yarn  &> /dev/null; then
    $SUDO npm i -g yarn --registry $NPM_MIRROR
  fi
  if ! command -v pnpm  &> /dev/null; then
    $SUDO npm i -g pnpm --registry $NPM_MIRROR
  fi
  yarn config set registry $NPM_MIRROR -g
  pnpm config set registry $NPM_MIRROR -g
fi
