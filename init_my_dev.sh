cp .bash_aliases ~   # shortcuts for pipenv and django manage
cp .switch_source_pipenv.py ~   # auto switch source to aliyun when pipenv create new env
cp .vimrc ~   # custom vim
git config --global credential.helper store  # git push auto fill in username and password after first time
sudo cp django_manage.bash /etc/bash_completion.d/   # auto complete for command `mg`
