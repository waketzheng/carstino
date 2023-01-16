# Shortcuts for `python manage.py` and its completion
alias mg='~/.mg.py'
alias mgshell="mg shell"
alias mgtest="mg test"
alias mgrunserver="mg runserver 0.0.0.0:9000"
alias mgmakemigrations="mg makemigrations"
alias mgmigrate="mg migrate"
alias mgcreatesuperuser="mg createsuperuser"
alias mgcollectstatic='mg collectstatic'

# python poetry
alias peotry=poetry
alias poerty=poetry
getVenv() {
  if [ -f ~/archives/carstino/get_venv.py ]; then
    python ~/archives/carstino/get_venv.py
  else
    echo 'poetry shell'
  fi
}
alias ve='echo "--> $(getVenv)" && $(getVenv)'
alias vv='echo "--> source venv/*/activate" && source venv/*/activate'

# trim the space at the right side of every line
alias rstrip="~/archives/carstino/rstrip.py"

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
alias gitdiff="git diff"
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
alias httpa="~/archives/carstino/httpa.sh"

# reformat py file
alias lint="~/.lint.sh"
