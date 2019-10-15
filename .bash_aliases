# python django shortcut for `python manage.py` and its completion
alias mg='~/.mg.py'
alias activate_completion="source /etc/bash_completion.d/django_manage_completion.bash"

# python pipenv
alias ve="pipenv shell"
alias env6="pipenv --python 3.6&&python3 ~/.switch_source_pipenv.py&&ve"
alias env3.6=env6
alias env3="pipenv --three&&python3 ~/.switch_source_pipenv.py&&ve"
alias env7="pipenv --python 3.7&&python3.7 ~/.switch_source_pipenv.py&&ve"
alias env3.7=env7
alias env8="pipenv --python 3.8&&python3.8 ~/.switch_source_pipenv.py&&ve"
alias env3.8=env8
alias env2="pipenv --two&&python3 ~/.switch_source_pipenv.py&&ve"
alias pgg="pipenv graph"
alias pii="~/.pipenv_install_while_lock_at_another_process.py"
alias poo="pipenv open "
alias puu="pipenv uninstall "
alias pcc="pipenv check --style */*.py"
alias switch_pipenv_source="~/.switch_source_pipenv.py"

# trim the space at the right side of every line
alias rstrip="~/carstino/rstrip.py"

# some useful aliases
alias cd..="cd .."
alias cd-="cd -"
alias ls..="ls .."
alias cl="clear"
alias gitpush="git push"
alias gitpull="git pull"
alias mgshell="mg shell"
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
# to frontend
alias myarn="tmux new -t yarn"
alias toyarn="tmux a -t yarn"
# to backend tty
alias mback="tmux new -t back"
alias toback="tmux a -t back"

# reformat py file
alias lint="~/.lint.sh"
