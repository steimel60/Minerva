import sqlite3

def create_table(org_conn: sqlite3.Connection) -> None:
    with org_conn:
        org_conn.cursor().execute(
            """
            CREATE TABLE IF NOT EXISTS accts (
                username TEXT NOT NULL PRIMARY KEY,
                password TEXT NOT NULL
            )
            """
        )

def drop_table(org_conn: sqlite3.Connection) -> None:
    with org_conn:
        org_conn.cursor().execute("DROP TABLE IF EXISTS accts")

def insert_acct(
    org_conn: sqlite3.Connection, 
    username: str, 
    password: str
) -> bool:
    try:
        with org_conn:
            org_conn.cursor().execute(
                "INSERT INTO accts VALUES (:username, :password)",
                {
                    "username": username, 
                    "password": password,
                }
            )
    except Exception as e:
        print(e)
        return False

    return True

def get_acct(org_conn: sqlite3.Connection, username: str) -> str:
    with org_conn:
        return org_conn.cursor().execute(
            "SELECT name FROM accts WHERE username =:username",
            {
                "username": username,
            }
        ).fetchone()[0]

def username_exists(org_conn: sqlite3.Connection, username: str) -> bool:
    with org_conn:
        return len(
            org_conn.cursor().execute(
                "SELECT 1 FROM accts WHERE username =:username",
                {
                    "username": username,
                }
            ).fetchall()
        ) > 0

def is_valid_login(
    org_conn: sqlite3.Connection,
    username: str,
    password: str
) -> bool:
    with org_conn:
        return len(
            org_conn.cursor().execute(
                "SELECT 1 FROM accts WHERE username =:username "
                "AND password =:password",
                {
                    "username": username, 
                    "password": password,
                }
            ).fetchall()
        ) > 0