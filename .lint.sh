isort $* && black $* && flake8 $* && mypy --ignore-missing-imports $* && \
echo 'Run `'"isort $* && black $* && flake8 $* && mypy --ignore-missing-imports $*"'`' && \
echo Done.
