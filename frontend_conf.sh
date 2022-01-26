# ---- For frontend development
echo "---- nodejs/npm/yarn/zx for frontend"
if [[ -n $1 ]]; then
  export NPM_MIRROR="$1"
else
  export NPM_MIRROR=http://mirrors.cloud.tencent.com/npm/
fi
which node || sudo apt install -y nodejs
which npm || (sudo apt install -y npm && sudo npm i -g npm --registry $NPM_MIRROR)
which yarn || sudo npm i -g yarn --registry $NPM_MIRROR
yarn config set registry $NPM_MIRROR -g
# https://github.com/google/zx.git
if ! command -v zx  &> /dev/null; then
  echo '`zx` not found! Start to install it by `yarn global add`'
  yarn global add zx
fi

# to be optimize: Use `zx` to make nvm installation as optional
if ! command -v nvm  &> /dev/null; then
  echo '`nvm` already installed. Skip!'
else
  echo "---- Optional install nvm to manage nodejs version"
  export NVM_NODEJS_ORG_MIRROR=https://repo.huaweicloud.com/nodejs/
  which nvm || git clone https://gitee.com/mirrors/nvm.git ~/.nvm && \
    cd ~/.nvm && \
    git checkout `git describe --abbrev=0 --tags` && \
    ./install.sh && \
    source ./nvm.sh && \
    cd - && \
    nvm install --lts && \
    npm config set registry $NPM_MIRROR
fi
