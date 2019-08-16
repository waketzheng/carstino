#!/usr/bin/env python3
"""
Create or drop databases for django project

Usage:
    $ ./createdatabase  # Just create a new database
    $ ./createdatbase -d  # Drop db if exists and then create a new one
    $ ./createdatabase -dm  # Run `./manage.py migrate` after create
"""
import os
import sys
from pathlib import Path

SETTINGS_ENV = "DJANGO_SETTINGS_MODULE"
SQL = "create database {} DEFAULT CHARACTER SET {} COLLATE utf8_general_ci"


def configure_settings():
    p = Path("manage.py")
    for _ in range(5):
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
        raise Exception(f"database NAME ``{alias}`` not found at settings.")


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
    elif "sqlite3" in engine:
        sqlite(config, db_name, drop)
    else:
        raise Exception(f"Not handle database engine ``{engine}`` yet..")


def mysql(config, db_name, drop=False):
    import MySQLdb

    try:
        conn = MySQLdb.connect(**config)
        cur = conn.cursor()
        if drop:
            cur.execute(f"drop database {db_name}")
            print(f"success to execute `drop database {db_name};`")
        command = SQL.format(db_name, config["charset"])
        cur.execute(command)
        print(f"success to execute `{command};`")
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"SQL Error: {e}")


def postgres(config, db_name, drop=False):
    who = "sudo -u postgres psql -U postgres -d postgres -c "
    option = "encoding='utf-8'"
    if drop:
        cmd = f'{who}"drop database {db_name};"'
        print("\n-->", cmd, "...")
        os.system(f"cd /tmp && {cmd}")
    cmd = f'{who}"create database {db_name} {option};"'
    print("\n-->", cmd, "...")
    os.system(f"cd /tmp && {cmd}")


def sqlite(config, db_name, drop=False):
    if drop:
        os.remove(db_name)
        print(f"{db_name} was deleted.")


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
    args, unknown = parser.parse_known_args()
    manage_path = configure_settings()
    sys.path.insert(0, str(manage_path.parent))
    print("Reading DATABASES configure from django settings...")
    if args.all:
        aliases, dbs = get_db(all_=True)
    else:
        aliases, dbs = [args.alias], [get_db(args.alias)]
    for db in dbs:
        creat_db(*getconf(db), drop=args.delete)
    if args.migrate:
        cmd = f"python {manage_path} makemigrations"
        print("\n-->", cmd, "...")
        os.system(cmd)
        for alias in aliases:
            cmd = f"python {manage_path} migrate --database={alias}"
            print("\n-->", cmd, "...")
            os.system(cmd)


if __name__ == "__main__":
    main()
