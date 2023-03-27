import sqlite3

def insert(
    conn: sqlite3.Connection, 
    username: str, 
    password: str
) -> bool:
    try:
        with conn:
            conn.cursor().execute(
                "INSERT INTO account VALUES (:username, :password)",
                {
                    "username": username, 
                    "password": password,
                }
            )
    except Exception as e:
        print(e)
        return False

    return True

def get(conn: sqlite3.Connection, username: str) -> str:
    with conn:
        return conn.cursor().execute(
            "SELECT name FROM account WHERE username =:username",
            {
                "username": username,
            }
        ).fetchone()[0]

def acct_exists(conn: sqlite3.Connection, username: str) -> bool:
    try:
        with conn:
            return len(
                conn.cursor().execute(
                    "SELECT * FROM account WHERE username =:username",
                    {
                        "username": username,
                    }
                ).fetchall()
            ) > 0
    except Exception as e:
        print(e)
        return False

def is_valid_acct(
    conn: sqlite3.Connection,
    username: str,
    password: str
) -> bool:
    with conn:
        return len(
            conn.cursor().execute(
                "SELECT 1 FROM account WHERE username =:username "
                "AND password =:password",
                {
                    "username": username, 
                    "password": password,
                }
            ).fetchall()
        ) > 0