isort -rc $* && white $* && flake8 $*
echo 'Run `'"isort -rc $* && white $* && flake8 $*"'`'
echo Done.
