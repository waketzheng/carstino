#!/bin/bash
FLAKE8=`(which pflake8 >> /dev/null) && (echo pflake8) || (echo flake8)`
CMD="isort $* && black $* && $FLAKE8 $* && mypy --ignore-missing-imports $*"

echo 'Run `'$CMD'`' && \
sh -c "$CMD" && \
  echo Done.
