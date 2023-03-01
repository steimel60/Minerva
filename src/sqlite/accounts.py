import sqlite3

def create_table(conn: sqlite3.Connection) -> None:
    with conn:
        conn.cursor().execute(
            """
            CREATE TABLE IF NOT EXISTS accts (
                username TEXT NOT NULL PRIMARY KEY,
                password TEXT NOT NULL
            )
            """
        )

def drop_table(conn: sqlite3.Connection) -> None:
    with conn:
        conn.cursor().execute("DROP TABLE IF EXISTS accts")

def insert_acct(
    conn: sqlite3.Connection, 
    username: str, 
    password: str
) -> bool:
    try:
        with conn:
            conn.cursor().execute(
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

def get_acct(conn: sqlite3.Connection, username: str) -> str:
    with conn:
        return conn.cursor().execute(
            "SELECT name FROM accts WHERE username =:username",
            {
                "username": username,
            }
        ).fetchone()[0]

def acct_exists(conn: sqlite3.Connection, username: str) -> bool:
    with conn:
        return len(
            conn.cursor().execute(
                "SELECT 1 FROM accts WHERE username =:username",
                {
                    "username": username,
                }
            ).fetchall()
        ) > 0

def is_valid_acct(
    conn: sqlite3.Connection,
    username: str,
    password: str
) -> bool:
    with conn:
        return len(
            conn.cursor().execute(
                "SELECT 1 FROM accts WHERE username =:username "
                "AND password =:password",
                {
                    "username": username, 
                    "password": password,
                }
            ).fetchall()
        ) > 0