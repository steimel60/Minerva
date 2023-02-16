import sqlite3 as sql

def create_table(org_conn: sql.Connection):
    with org_conn:
        c = org_conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS accts (
            username TEXT NOT NULL PRIMARY KEY,
            password TEXT NOT NULL
        )""")

def drop_table(org_conn: sql.Connection):
    with org_conn:
        c = org_conn.cursor()
        c.execute("DROP TABLE IF EXISTS accts")

def insert(org_conn: sql.Connection, username: str, password: str) -> bool:
    try:
        with org_conn:
            c = org_conn.cursor()
            c.execute("INSERT INTO accts VALUES (:username, :password)"
            ,{'username':username, 'password':password})
            return True
    except Exception as e:
        print(e)
        return False

def select_by_username(org_conn: sql.Connection, username: str):
    with org_conn:
        c = org_conn.cursor()
        c.execute("""SELECT name FROM accts WHERE username =:username"""
                    ,{'username':username})
        return c.fetchone()[0]

def username_exist(org_conn: sql.Connection, username: str) -> bool:
    with org_conn:
         c = org_conn.cursor()
         c.execute("""SELECT 1 FROM accts WHERE username =:username"""
                    ,{'username':username})
         return len(c.fetchall()) > 0

def is_valid_login(org_conn: sql.Connection, username: str, password:str) -> bool:
    with org_conn:
        c = org_conn.cursor()
        c.execute("""SELECT 1 FROM accts WHERE username =:username AND password =:password"""
                    ,{'username':username, 'password':password})
        return len(c.fetchall()) > 0