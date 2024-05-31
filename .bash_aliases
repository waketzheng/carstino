# Shortcuts for `python manage.py` and its completion
alias mg='python ~/.mg.py'
alias mgshell="mg shell"
alias mgtest="mg test"
alias mgrunserver="mg runserver 0.0.0.0:9000"
alias mgmakemigrations="mg makemigrations"
alias mgmigrate="mg migrate"
alias mgcreatesuperuser="mg createsuperuser"
alias mgcollectstatic='mg collectstatic'

# Tool directory path
export CARST_PATH='~/archives/carstino'

# python poetry
alias peotry="poetry"
alias poerty="poetry"
alias poetryrun='poetry run'
alias poetryinstall='poetry install'
alias prun='poetry run'
# `poetry install` not work at GitBash for Windows, so add psync to install dependencies
alias poetrysync='poetry export --with=dev --without-hashes -o dev_requirements.txt && pip install -r dev_requirements.txt'
alias psync='poetrysync'
getVenv() {
  if [ -f $CARST_PATH/get_venv.py ]; then
    python $CARST_PATH/get_venv.py
  else
    echo 'poetry shell'
  fi
}
alias ve='echo "--> $(getVenv)" && $(getVenv)'
alias vv='echo "--> source venv/*/activate" && source venv/*/activate'

# trim the space at the right side of every line
alias rstrip="python $CARST_PATH/rstrip.py"

# some useful aliases
alias cd..="cd .."
alias cd-="cd -"
alias ls..="ls .."
alias cl="clear"

# Git
alias gitpush="git push"
alias gitpull="git pull"
alias gittag="git tag"
alias gitstatus="git status"
alias gitlog="git log"
alias gitdiff='git diff ":!*.lock"'
alias gitadd="git add"
alias gitcheckout="git checkout"
alias gitcommit="git commit"

# fabric
alias fabpull='fab pull'
alias fabmigrate='fab migrate'
alias fabtest='fab test'

# for tmux
alias t0="tmux a -t 0"
alias t1="tmux a -t 1"
alias t2="tmux a -t 2"
alias t3="tmux a -t 3"
alias t4="tmux a -t 4"
alias t5="tmux a -t 5"
alias tw="tmux select-window -t"
alias ts="tmux switch -t"
alias rw="tmux rename-window"
alias rs="tmux rename-session"

# For httpie
alias httpa="sh $CARST_PATH/httpa.sh"

# reformat py file
alias lint="sh ~/.lint.sh"

# For windows to open directory
if [ -f /usr/bin/open ]; then
  alias explorer="open"
  alias py="python3"
  alias pipi="python $CARST_PATH/.pipi.py"
else
  alias pipi="python -m pip install"
  alias open="explorer"
fi

if [ -f /sbin/shutdown ]; then
  if [ -f /sbin/poweroff ]; then
    alias poweroff='python -c "import this;print()" && echo "Lets say that we have a dream ..."'
  else
    # For mac to shutdown
    alias poweroff='echo Shutdown need root privilege, FBA WARNING: DONT forgot to save files!;sudo shutdown -h now'
  fi
fi

# For MacOS to manage databases
if [ -f $HOME/.systemctl.py ]; then
  alias systemctl="python $HOME/.systemctl.py"
fi
