# python django shortcut for `python manage.py` and its completion
alias mg='~/.mg.py'
alias mgshell="mg shell"
alias mgrunserver="mg runserver 0:9000"
alias mgmakemigrations="mg makemigrations"
alias mgmigrate="mg migrate"
alias mgcreatesuperuser="mg createsuperuser"
alias mgcollectstatic='mg collectstatic'
alias activate_completion="source /etc/bash_completion.d/django_manage_completion.bash"

# python pipenv
alias ve="pipenv shell"
alias env8="pipenv --python 3.8&&python3.8 ~/.switch_source_pipenv.py&&ve"
alias env3.8=env8
alias pgg="pipenv graph"
alias poo="pipenv open "
alias puu="pipenv uninstall "
alias pcc="pipenv check --style */*.py"
alias switch_pipenv_source="~/.switch_source_pipenv.py"

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

# for podman
alias docker=podman
