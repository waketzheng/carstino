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
VENV_CREATE := "pdm venv create --with uv --with-pip"
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
    @if test ! -e .venv; then {{ VENV_CREATE }} {{ args }}; fi
[windows]
venv *args:
    @if (-Not (Test-Path '.venv')) { {{ VENV_CREATE }} {{ args }} }

venv313:
    {{ VENV_CREATE }} 3.13

uv_deps *args:
    @uv run --no-sync fast pypi --quiet --reverse
    {{ UV_DEPS }} {{args}}
    @just install_me
    @uv run --no-sync fast pypi --quiet

[unix]
deps *args: venv
    @just uv_deps {{args}}
[windows]
deps *args: venv
    if (-Not (Test-Path '~/AppData/Roaming/uv/tools/rust-just')) { echo 'Using pdm ...'; {{ PDM_DEPS }} {{ args }} } else { echo 'uv sync...'; just uv_deps {{ args }} }

uv_lock *args:
    @uv run --no-sync fast pypi --quiet --reverse
    uv lock {{args}}
    @just deps --frozen

[unix]
lock *args:
    @just uv_lock {{args}}
    @if test -e pdm.lock; then pdm lock -G :all; fi
[windows]
lock *args:
    if (-Not (Test-Path '~/AppData/Roaming/uv/tools/rust-just')) { echo 'Using pdm ...'; pdm lock -G :all {{ args }} } else { echo 'uv lock...'; just uv_lock {{ args }} }


up:
    @just lock --upgrade
    @if test -e pdm.lock; then pdm update -G :all --no-sync; fi

uv_clear *args:
    {{ UV_DEPS }} {{args}}

[unix]
clear *args:
    @just uv_clear {{args}}
[windows]
clear *args:
    @if (-Not (Test-Path 'pdm.lock')) { just uv_clear {{args}}  } else { pdm sync -G :all --clean {{args}} }

run *args: venv
    .venv/{{BIN_DIR}}/{{args}}

_lint *args:
    pdm run fast lint --ty {{args}}

lint *args: deps
    @just _lint {{args}}

fmt *args:
    @just _lint --skip-mypy {{args}}

alias _style := fmt

style *args: deps
    @just fmt {{args}}

_check *args:
    pdm run fast check --ty {{args}}

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
