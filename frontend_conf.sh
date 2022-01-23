# ---- For frontend development
echo "---- nodejs/npm/yarn/vue for frontend"
export NPM_MIRROR=http://mirrors.cloud.tencent.com/npm/
sudo apt install -y nodejs
sudo apt install -y npm
sudo npm i -g npm --registry $NPM_MIRROR
sudo npm i -g yarn --registry $NPM_MIRROR
yarn config set registry $NPM_MIRROR -g
# https://github.com/google/zx.git
yarn global add zx

# to be optimize: Use `zx` to make nvm installation as optional
echo "---- Optional install nvm to manage nodejs version"
export NVM_NODEJS_ORG_MIRROR=https://repo.huaweicloud.com/nodejs/
git clone https://gitee.com/mirrors/nvm.git ~/.nvm && \
  cd ~/.nvm && \
  git checkout `git describe --abbrev=0 --tags` && \
  ./install.sh && \
  source ./nvm.sh && \
  cd - && \
  nvm install --lts && \
  npm config set registry $NPM_MIRROR
# ---- End For

