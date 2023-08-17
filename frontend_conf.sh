# ---- For frontend development
echo "---- Initial nodejs/npm/yarn/pnpm/zx for frontend"

# which node || sudo apt install -y nodejs
# which npm || (sudo apt install -y npm && sudo npm i -g npm --registry $NPM_MIRROR)
# which yarn || sudo npm i -g yarn --registry $NPM_MIRROR
# yarn config set registry $NPM_MIRROR -g
# which pnpm || sudo npm i -g pnpm --registry $NPM_MIRROR
# pnpm config set registry $NPM_MIRROR -g

# to be optimize: Use `zx` to make nvm installation as optional
if ! command -v nvm  &> /dev/null; then
  if [[ -n $1 ]]; then
    export NPM_MIRROR="$1"
    echo Using $1 as npm mirror
  elif [[ $NPM_MIRROR == "tx" ]]; then
    export NPM_MIRROR=http://mirrors.cloud.tencent.com/npm/
  elif [ $NPM_MIRROR ]; then
    echo npm mirror is $NPM_MIRROR
  else
    export NPM_MIRROR=http://repo.huaweicloud.com/repository/npm/
  fi
  echo "---- Installing nvm to manage nodejs version"
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
    git clone $NVM_REPO_URL "$NVM_DIR"
    cd "$NVM_DIR"
    git checkout `git describe --abbrev=0 --tags --match "v[0-9]*" $(git rev-list --tags --max-count=1)`
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
  if ! command -v npm  &> /dev/null; then
    echo npm not ready yet.
  else
    npm config set registry $NPM_MIRROR
    npm config set disturl $NVM_NODEJS_ORG_MIRROR
    npm -v
    npm i -g yarn pnpm
    yarn config set registry $NPM_MIRROR -g
    pnpm config set registry $NPM_MIRROR -g
    # https://github.com/google/zx.git
    if ! command -v zx  &> /dev/null; then
      echo '`zx` not found! Start to install it by `yarn global add`'
      yarn global add zx
    fi
  fi
else
  echo '`nvm` already installed. Skip!'
fi
