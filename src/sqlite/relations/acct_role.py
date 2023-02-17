import sqlite3 as sql

def create_table(org_conn: sql.Connection):
    with org_conn:
        c = org_conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS acct_role (
            username TEXT NOT NULL,
            role TEXT NOT NULL,
            CONSTRAINT PK_user_role PRIMARY KEY (username, role),
            CONSTRAINT FK_username FOREIGN KEY (username)
                REFERENCES accts (username),
            CONSTRAINT FK_role FOREIGN KEY (role)
                REFERENCES role (role)
        )""")

def drop_table(org_conn: sql.Connection):
    with org_conn:
        c = org_conn.cursor()
        c.execute("DROP TABLE IF EXISTS acct_role")

def insert(org_conn: sql.Connection, username: str, role: str) -> bool:
    try:
        with org_conn:
            c = org_conn.cursor()
            c.execute("INSERT INTO acct_role VALUES (:username ,:role)"
            ,{'username':username, 'role':role})
            return True
    except Exception as e:
        print(e)
        return False
    
def get_users_with_role(org_conn: sql.Connection, role: str) -> list[str]:
    with org_conn:
        c = org_conn.cursor()
        c.execute("""SELECT username FROM acct_role WHERE role =:role"""
                  , {'role':role})
        return c.fetchall()