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
	@just up

lock:
	@just lock

deps:
	@just deps $(options)

_check:
	@just _check
check: deps _check

_lint:
	@just _lint
lint: deps _lint

_test:
	@just _test
test: deps _test

_style:
	@just fmt
style: deps _style

# Usage::
#   make venv version=3.12
venv:
ifeq ($(wildcard .venv),)
	uv venv --python=$(version) --prompt=carstino-$(version)
	$(MAKE) deps
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

publish:
	# pdm publish
	@echo "Do not publish by command line, use '.github/workflow/publish.yml' instead."
	@echo "Just push a new tag, and the github action will auto publish it to pypi.org"

bump:
	python edit_pip_conf_updated_at.py
	fast bump patch --commit
