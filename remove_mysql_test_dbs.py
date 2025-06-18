#!/Users/mac10.12/archives/carstino/.venv/bin/python
"""
Remove MySQL databases whose name is more than 10 characters and startswith 'test_'
"""

import sys

import pymysql

try:
    from tqdm import tqdm
except ImportError:
    from collections.abc import Generator, Sequence
    from typing import TypeVar

    _T = TypeVar("_T")

    def tqdm(items: Sequence[_T]) -> Generator[_T]:  # type:ignore[no-redef]
        try:
            total = len(items)
        except TypeError:
            items = list(items)
            total = len(items)
        for i, v in enumerate(items, 1):
            print(f"Progressbar: {i}/{total} ...")
            yield v


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
        for i in tqdm(todo):
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
