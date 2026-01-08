#!/usr/local/bin/python3.11
"""
For MacOS to manage databases/docker service
"""

import os
import subprocess
import sys
from enum import StrEnum  # ty: ignore[unresolved-import]

try:
    from ensure_import import EnsureImport as _EI  # ty: ignore[unresolved-import]
except ImportError:
    try:
        import typer  # ty: ignore[unresolved-import]
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "typer"])
        import typer  # ty: ignore[unresolved-import]
else:
    while _ei := _EI(_no_venv=True):
        with _ei:
            import typer  # ty: ignore[unresolved-import]

cli = typer.Typer()

DRY = False


class Engine(StrEnum):
    mysql = "mysql"
    postgres = "postgres"
    mssql = "mssql"
    mongo = "mongo"
    docker = "docker"


class Create(StrEnum):
    mysql = (
        "docker run -d -p 3306:3306 --name mysql_latest"
        " -e MYSQL_ROOT_PASSWORD=123456 mysql:latest"
    )
    postgres = (
        "docker run -d -p 5432:5432 --name postgres_latest"
        " -e POSTGRES_PASSWORD=123456 -e POSTGRES_USER=postgres postgres:latest"
    )
    mssql = (
        "docker run -d -p 1433:1433 --name mssql_latest"
        " -e ACCEPT_EULA=Y -e SA_PASSWORD=Abcd12345678"
        " mcr.microsoft.com/mssql/server:2019-CU15-ubuntu-20.04"
        # " mcr.microsoft.com/mssql/server:latest"
    )
    mongo = "docker run -d -p 27017:27017 --name mongo_latest mongo:latest"
    docker = "brew install colima"


class Start(StrEnum):
    mysql = "docker start mysql_latest"
    postgres = "docker start postgres_latest"
    mssql = "docker start mssql_latest"
    mongo = "docker start mongo_latest"
    # https://apple.stackexchange.com/questions/373888/how-do-i-start-the-docker-daemon-on-macos
    docker = "colima start"


def run_and_echo(cmd: str, dry=False, **kw) -> int:
    typer.echo(f"--> Executing shell command:\n {cmd}")
    if dry:
        return 0
    kw.setdefault("shell", True)
    return subprocess.run(cmd, **kw).returncode


def exit_if_run_failed(cmd: str, env=None, _exit=False, dry=False, **kw) -> None:
    if env is not None:
        env = {**os.environ, **env}
    if rc := run_and_echo(cmd, env=env, dry=dry, **kw):
        if _exit or "typer" not in locals():
            sys.exit(rc)
        raise typer.Exit(rc)


def run_shell(cmd: str) -> None:
    exit_if_run_failed(cmd, _exit=True, dry=DRY)


@cli.command()
def enable(db: Engine):
    run_shell(Create[db])


@cli.command()
def start(db: Engine):
    run_shell(Start[db])


@cli.command()
def stop(db: Engine):
    run_shell(Start[db].replace(" start", " stop"))


@cli.command()
def status(db: Engine):
    if db == Engine.docker:
        run_shell("colima status")
    else:
        run_shell(f"docker ps |grep {db}")


def main():
    if (f := "--dry") in sys.argv:
        global DRY
        DRY = True
        sys.argv.pop(sys.argv.index(f))
    cli()


if __name__ == "__main__":
    main()
