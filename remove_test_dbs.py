#!/usr/bin/env python
import sys

import pymysql

pymysql.install_as_MySQLdb()


def show_databases(cur, conn) -> list[str]:
    sql = "show databases;"
    cur.execute(sql)
    conn.commit()
    res = cur.fetchall()
    return [i[0] for i in res]


def run(cur, conn):
    dbs = show_databases(cur, conn)
    print(f"{len(dbs) = }")
    todo = [i for i in dbs if i.startswith("test_") if len(i) > 10]
    if "--show" not in sys.argv:
        for i in todo:
            command = f"DROP DATABASE {i};"
            cur.execute(command)
        conn.commit()
    print(f"{show_databases(cur, conn) = }")


def main():
    import MySQLdb

    conn = MySQLdb.connect(user="root", passwd="123456")
    cur = conn.cursor()
    run(cur, conn)
    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
