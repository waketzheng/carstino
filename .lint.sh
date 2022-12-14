#!/bin/bash
CMD="isort $* && black $* && ruff --fix $* && mypy --ignore-missing-imports $*"

echo 'Run `'$CMD'`' && \
sh -c "$CMD" && \
  echo Done.
