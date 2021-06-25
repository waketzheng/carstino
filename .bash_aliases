# python django shortcut for `python manage.py` and its completion
alias mg='~/.mg.py'
alias activate_completion="source /etc/bash_completion.d/django_manage_completion.bash"

# python poetry
alias ve="poetry shell"

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
alias gitstatus="git status"
alias gitlog="git log"
alias gitdiff="git diff"
alias gitadd="git add"
alias gitcheckout="git checkout"
alias gitcommit="git commit"

# python manage.py xxx
alias mgshell="mg shell"
alias mgrunserver="mg runserver 0:9000"
alias mgmakemigrations="mg makemigrations"
alias mgmigrate="mg migrate"

# fabric
alias fabpull='fab pull'
alias fabmigrate='fab migrate'
alias fabtest='fab test'

# for tmux
alias t0="tmux a -t 0"
alias t1="tmux a -t 1"
alias t2="tmux a -t 2"
alias t3="tmux a -t 3"

# For httpie
alias httpa="~/archives/carstino/httpa.sh"

# reformat py file
alias lint="~/.lint.sh"
