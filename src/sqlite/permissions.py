import sqlite3 as sql

def create_table(org_conn: sql.Connection) -> None:
    with org_conn:
        org_conn.cursor().execute(
            """
            CREATE TABLE IF NOT EXISTS permissions (
            perm TEXT NOT NULL PRIMARY KEY
            )
            """
        )

def drop_table(org_conn: sql.Connection) -> None:
    with org_conn:
        org_conn.cursor().execute("DROP TABLE IF EXISTS permissions")

def insert(org_conn: sql.Connection, permission: str) -> bool:
    try:
        with org_conn:
            org_conn.cursor().execute(
                "INSERT INTO permissions VALUES (:permission)"
                ,{'permission':permission})
            return True
    except Exception as e:
        print(e)
        return False
