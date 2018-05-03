# python django
alias mg='python manage.py'

# python pipenv
alias ve="pipenv shell"
alias env="pipenv --three&&python3.6 ~/.switch_source_pipenv.py&&ve"
alias env2="pipenv --two&&python3.6 ~/.switch_source_pipenv.py&&ve"
alias pgg="pipenv graph"
alias pii="pipenv install"
alias poo="pipenv open "
alias puu="pipenv uninstall "
alias pcc="pipenv check --style */*.py"

# auto pep8
alias runpep8="autopep8 -a -a -i *.py"

# trim the space at the right side of every line
rstrip="~/letstype/rstrip.py"

# auto completion for pipenv
eval "$(pipenv --completion)"
