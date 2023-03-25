import sqlite3 as sql

def create_table(org_conn: sql.Connection) -> None:
    with org_conn:
        org_conn.cursor().execute(
            """
            CREATE TABLE IF NOT EXISTS roles (
            role TEXT NOT NULL PRIMARY KEY
            )
            """
        )

def drop_table(org_conn: sql.Connection) -> None:
    with org_conn:
        org_conn.cursor().execute("DROP TABLE IF EXISTS roles")

def insert(org_conn: sql.Connection, role: str) -> bool:
    try:
        with org_conn:
            org_conn.cursor().execute(
                "INSERT INTO roles VALUES (:role)",
                {
                    'role':role
                }
            )
            return True
    except Exception as e:
        print(e)
        return False
