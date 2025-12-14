#!/usr/bin/env -S just --justfile
# ^ A shebang isn't required, but allows a justfile to be executed
#   like a script, with `./justfile lint`, for example.

# NOTE: You can run the following command to install `just`:
#   uv tool install rust-just

system-info:
    @echo "This is an {{arch()}} machine running on {{os_family()}}"
    just --list

# Use powershell for Windows so that 'Git Bash' and 'PyCharm Terminal' get the same result
set windows-powershell := true
VENV_CREATE := "pdm venv create"
UV_PIP := "uv pip"
UV_PIP_I := UV_PIP + " install"
UV_PIP_L := UV_PIP + " list"
UV_SYNC := "uv sync --all-extras"
UV_PROD := UV_SYNC + " --no-dev"
UV_DEPS := UV_SYNC + " --all-groups"
PDM_SYNC := "pdm install --frozen"
PDM_PROD := PDM_SYNC + " --prod"
PDM_DEPS := PDM_SYNC + " -G :all"
PROD_DEPS := if os_family() == "windows" { PDM_PROD } else { UV_PROD }
INSTALL_DEPS := if os_family() == "windows" { PDM_DEPS } else { UV_DEPS }
BIN_DIR := if os_family() == "windows" { "Scripts" } else { "bin" }
WARN_OS := "echo 'WARNING: This command only support Linux!'"

[unix]
venv *args:
    @if test ! -e .venv; then {{ VENV_CREATE }} --with uv {{ args }}; fi
[windows]
venv *args:
    @if (-Not (Test-Path '.venv')) { {{ VENV_CREATE }} --with-pip {{ args }} }

venv313:
    {{ VENV_CREATE }} 3.13

deps *args: venv
    {{ INSTALL_DEPS }} {{args}}
    @just install_me
    @uv run --no-sync fast pypi --quiet

[unix]
lock *args:
    uv lock {{args}}
    @just deps --frozen
[windows]
lock *args:
    @{{WARN_OS}}

up:
    @just lock --upgrade

[unix]
clear *args:
    uv sync --all-extras --all-groups {{args}}
[windows]
clear *args:
    @echo "WARNING: It may cost 10 minutes! You can enter Crtl-C to exit."
    @if (-Not (Test-Path 'pdm.lock')) { pdm lock -G :all }
    pdm sync -G :all --clean {{args}}

run *args: venv
    .venv/{{BIN_DIR}}/{{args}}

_lint *args:
    pdm run fast lint {{args}}

lint *args: deps
    @just _lint {{args}}

fmt *args:
    @just _lint --skip-mypy {{args}}

alias _style := fmt

style *args: deps
    @just fmt {{args}}

_check *args:
    pdm run fast check {{args}}

check *args: deps
    @just _check {{args}}

_build *args:
    pdm build {{args}}

build *args: deps
    @just _build {{args}}

_test *args:
    pdm run fast test {{args}}

test *args: deps
    @just _test {{args}}

prod *args: venv
    {{ PROD_DEPS }} {{args}}

[unix]
pipi *args: venv
    {{ UV_PIP_I }} {{args}}
[windows]
pipi *args: venv
    @if (-Not (Test-Path '.venv/Scripts/pip.exe')) { UV_PIP_I {{args}} } else { @just run pip install {{args}} }

install_me:
    @just pipi -e .

start:
    pre-commit install
    @just deps

version part="patch":
    pdm run fast bump {{part}}

bump *args:
    pdm run fast bump patch --commit {{args}}

tag *args:
    pdm run fast tag {{args}}

release: venv bump tag
    git --no-pager log -1
