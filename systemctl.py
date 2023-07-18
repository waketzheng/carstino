#!/usr/bin/env python3.11
"""
For MacOS to manage databases
"""
import subprocess
from enum import StrEnum

import typer

cli = typer.Typer()


class Engine(StrEnum):
    mysql = "mysql"
    postgres = "postgres"
    mssql = "mssql"


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
        " -e ACCEPT_EULA=Y -e SA_PASSWORD: Abcd12345678"
        " mcr.microsoft.com/mssql/server:latest"
    )


class Start(StrEnum):
    mysql = "docker start mysql_latest"
    postgres = "docker start postgres_latest"
    mssql = "docker start mssql_latest"


def run_shell(cmd: str) -> None:
    print("--> Executing shell command:\n", cmd, flush=True)
    subprocess.run(cmd, shell=True)


@cli.command()
def enable(db: Engine):
    run_shell(Create[db])


@cli.command()
def start(db: Engine):
    run_shell(Start[db])


if __name__ == "__main__":
    cli()
