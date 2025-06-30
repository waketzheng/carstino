help:
	@echo  "Carstino development makefile"
	@echo
	@echo  "Usage: make <target>"
	@echo  "Targets:"
	@echo  "    up      Updates dev/test dependencies"
	@echo  "    deps    Ensure dev/test dependencies are installed"
	@echo  "    check   Checks that build is sane"
	@echo  "    test    Runs all tests"
	@echo  "    style   Auto-formats the code"
	@echo  "    lint    Auto-formats the code and check type hints"
	@echo  "    venv    Create local virtual environment at .venv"

version ?= 3.12

up:
	pdm update --verbose
	$(MAKE) deps

deps:
	pdm install --frozen

_check:
	pdm run fast check
check: deps _check

_lint:
	pdm run fast lint
lint: deps _lint

_test:
	pdm run fast test
test: deps _test

_style:
	pdm run fast lint --skip-mypy
style: deps _style

# Usage::
#   make venv version=3.12
venv:
ifeq ($(wildcard .venv),)
	uv venv --python=$(version) --prompt=carstino-$(version)
	$(MAKE) deps version=$(version)
else
	@echo "'.venv'" exists, skip virtual environment creating"("uv venv --python=$(version) --prompt=carstino-$(version)")".
	./.venv/bin/python -V
endif

venv311:
	uv venv --python=3.11 --prompt=carstino-311

venv312:
	$(MAKE) venv version=3.12

venv313:
	$(MAKE) venv version=3.13
