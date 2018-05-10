#!/usr/bin/env python3.6
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


def get_db(alias="default"):
    from django.conf import settings

    dbs = settings.DATABASES
    return dbs.get(alias)


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
        raise Exception("Unknow database engine.")


def mysql(config, db_name, drop=False):
	# TODO: use MySQLdb
	import pymysql
    try:
        conn = pymysql.connect(**config)
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
        os.system(f'{who}"drop database {db_name};"')
    os.system(f'{who}"create database {db_name} {option};"')


def sqlite(config, db_name, drop=False):
    if drop:
        pass


def main():
	from argparse import ArgumentParser
	parser = ArgumentParser()
	parser.add_argument('-d', '--delete', action='store_true',
                        help='whether to recursive')
	parser.add_argument('-a', '--alias', default='default',
                        help='the alias of the database(default:default)')
	args, unknown = parser.parse_known_args()
    manage_path = configure_settings()
    sys.path.insert(0, str(manage_path.parent))
    db = get_db(args.a)
    creat_db(*getconf(db), drop=args.d)
    os.system(f"python {manage_path} migrate")


if __name__ == "__main__":
    main()
