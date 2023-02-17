import sqlite3 as sql

def create_table(org_conn: sql.Connection):
    with org_conn:
        c = org_conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS roles (
            role TEXT NOT NULL PRIMARY KEY
        )""")

def drop_table(org_conn: sql.Connection):
    with org_conn:
        c = org_conn.cursor()
        c.execute("DROP TABLE IF EXISTS roles")

def insert(org_conn: sql.Connection, role: str) -> bool:
    try:
        with org_conn:
            c = org_conn.cursor()
            c.execute("INSERT INTO roles VALUES (:role)"
            ,{'role':role})
            return True
    except Exception as e:
        print(e)
        return False
