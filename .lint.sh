isort $* && black $* && flake8 $*  && \
echo 'Run `'"isort $* && black $* && flake8 $*"'`'  && \
echo Done.
