#!/usr/bin/env python3
"""
Create or drop databases for django project

Usage:
    $ ./createdatabase.py  # Just create a new database
    $ ./createdatbase.py -d  # Drop db if exists and then create a new one
    $ ./createdatabase.py -m  # Run `./manage.py migrate` after create
    $ ./createdatabase.py -dm  # drop, create, migrate
"""

import os
import subprocess
import sys
from pathlib import Path

SETTINGS_ENV = "DJANGO_SETTINGS_MODULE"
SQL = "create database {} CHARACTER SET {}"


def secho(*args, **kw):
    try:
        from click import secho
    except ImportError:
        print(*args, **kw)
    else:
        secho(" ".join(map(str, args)), **kw)


def capture_output(cmd):
    # type: (str) -> str
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True)
    except (TypeError, AttributeError):  # For python<=3.6
        with os.popen(cmd) as p:
            return p.read().strip()
    else:
        return r.stdout.decode().strip()


def configure_settings():
    p = Path("manage.py")
    MAX_NESTED = 5  # make `mg` work at sub directory
    for _ in range(MAX_NESTED):
        if p.exists():
            break
        p = Path(f"../{p}")
    else:
        raise Exception('`manage.py` not found at "." or ".."')
    s = p.read_text()
    conf_line = [i for i in s.split("\n") if SETTINGS_ENV in i][0]
    exec(conf_line.strip())
    return p


def get_db(alias="default", all_=False):
    from django.conf import settings

    dbs = settings.DATABASES
    if all_:
        return dbs.keys(), dbs.values()
    try:
        return dbs[alias]
    except KeyError:
        raise Exception(f"database NAME ``{alias}`` not found at settings.") from None


def getconf(dbconf):
    config = {
        "host": dbconf.get("HOST"),
        "user": dbconf.get("USER"),
        "passwd": dbconf.get("PASSWORD"),
        "port": dbconf.get("PORT"),
        "charset": "utf8",
    }
    config = {k: v for k, v in config.items() if v is not None}
    db_name = dbconf.get("NAME")
    engine = dbconf.get("ENGINE")
    return config, db_name, engine


def creat_db(config, db_name, engine, drop=False):
    if "mysql" in engine:
        mysql(config, db_name, drop)
    elif "postgres" in engine:
        postgres(config, db_name, drop)
    elif "sqlite" in engine:
        sqlite(config, db_name, drop)
    else:
        raise Exception(f"Not handle database engine ``{engine}`` yet..")


def mysql(config, db_name, drop=False):
    import MySQLdb

    try:
        conn = MySQLdb.connect(**config)
        cur = conn.cursor()
        if drop:
            sql = f"DROP DATABASE IF EXISTS {db_name}"
            cur.execute(sql)
            secho(f"success to execute `{sql};`")
        command = SQL.format(db_name, config["charset"])
        cur.execute(command)
        secho(f"success to execute `{command};`")
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        secho(f"SQL Error: {e}")


def using_docker(engine="postgres"):
    # type: (str) -> bool
    containers = capture_output("docker ps")
    return bool(containers) and engine in containers


def prompt_mysql_create_db(name, user, drop_db=False):
    # type: (str, str, bool) -> None
    sql = (
        f"CREATE DATABASE IF NOT EXISTS {name}"
        " DEFAULT CHARACTER SET utf8"
        " DEFAULT COLLATE utf8_general_ci;"
    )
    if drop_db:
        sql = f"DROP DATABASE IF EXISTS {name};\n" + sql
    secho(f"Run the following line inside mysql client:\n\n{sql}")
    connect_db = f"mysql -u{user} -p"
    if using_docker("mysql"):
        connect_db = "docker exec -it mysql_latest " + connect_db
    secho("\n-->", connect_db)
    os.system(connect_db)


def postgres(config, db_name, drop=False):
    man = "docker exec postgres_latest " if using_docker() else "sudo -u postgres "
    who = man + "psql -U postgres -d postgres -c "
    option = "encoding='utf-8'"
    if drop:
        cmd = f'{who}"drop database if exists {db_name};"'
        secho("\n-->", cmd, "...")
        os.system(f"cd /tmp && {cmd}")
    cmd = f'{who}"create database {db_name} {option};"'
    secho("\n-->", cmd, "...")
    os.system(f"cd /tmp && {cmd}")


def sqlite(config, db_name, drop=False):
    if drop:
        try:
            os.remove(db_name)
        except FileNotFoundError:
            secho(f"sqlite3 file `{db_name}` not exist!")
        else:
            secho(f"{db_name} was deleted.")
    else:
        secho("sqlite3 no need to create db.")


def main():
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument(
        "-d",
        "--delete",
        action="store_true",
        help="whether to delete the database if exists",
    )
    parser.add_argument(
        "-m",
        "--migrate",
        action="store_true",
        help="whether to run the migrate command",
    )
    parser.add_argument(
        "--all", action="store_true", help="whether to handle all databases"
    )
    parser.add_argument(
        "-a",
        "--alias",
        default="default",
        help="the alias of the database(default:default)",
    )
    parser.add_argument(
        "--name",
        default="auto",
        help="the db name to be created(default:auto detect from manage.py)",
    )
    parser.add_argument(
        "--user",
        default="root",
        help="the engine client user name(default:root)",
    )
    parser.add_argument(
        "--engine",
        "--client",
        dest="engine",
        default="postgres",
        choices=("mysql", "postgres", "sqlite"),
        help="What's the database engine(default:postgres)",
    )
    args, unknown = parser.parse_known_args()
    if args.name != "auto":
        if args.engine == "mysql":
            return prompt_mysql_create_db(args.name, args.user, args.delete)
        aliases = ["default"]
        dbs = [{"NAME": args.name, "ENGINE": args.engine}]
    else:
        manage_path = configure_settings()
        sys.path.insert(0, str(manage_path.parent))
        secho("Reading DATABASES configure from django settings...")
        if args.all:
            aliases, dbs = get_db(all_=True)
        else:
            aliases, dbs = [args.alias], [get_db(args.alias)]
    for db in dbs:
        creat_db(*getconf(db), drop=args.delete)
    if args.migrate:
        cmd = f"python {manage_path} makemigrations"
        secho("\n-->", cmd, "...")
        os.system(cmd)
        for alias in aliases:
            cmd = f"python {manage_path} migrate --database={alias}"
            secho("\n-->", cmd, "...")
            os.system(cmd)


if __name__ == "__main__":
    main()
