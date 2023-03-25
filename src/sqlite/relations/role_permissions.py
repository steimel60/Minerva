import sqlite3 as sql

def create_table(org_conn: sql.Connection) -> None:
    with org_conn:
        org_conn.cursor().execute(
            """
            CREATE TABLE IF NOT EXISTS role_perms (
            role TEXT NOT NULL,
            perm TEXT NOT NULL,
            CONSTRAINT PK_role_perm PRIMARY KEY (role, perm),
            CONSTRAINT FK_role FOREIGN KEY (role)
                REFERENCES roles (role),
            CONSTRAINT FK_perm FOREIGN KEY (perm)
                REFERENCES permissions (perm)
            )
            """
        )

def drop_table(org_conn: sql.Connection) -> None:
    with org_conn:
        org_conn.cursor().execute("DROP TABLE IF EXISTS role_perms")

def insert(org_conn: sql.Connection, role: str, perm: str) -> bool:
    try:
        with org_conn:
            org_conn.cursor().execute(
                "INSERT INTO role_perms VALUES (:role ,:perm)",
                {
                    'role':role,
                    'perm':perm
                }
            )
            return True
    except Exception as e:
        print(e)
        return False
    
def get_permissions_of_role(org_conn: sql.Connection, role: str) -> list[str]:
    with org_conn:
        return org_conn.cursor().execute(
            "SELECT perm FROM role_perms WHERE role =:role",
            {
                'role':role
            }
        ).fetchall()

def get_permissions_of_user(org_conn: sql.Connection, username: str) -> list[str]:
    with org_conn:
        return org_conn.cursor().execute(
            """
            SELECT perm
            FROM role_perms
            WHERE role IN (
                SELECT role FROM acct_role WHERE username =:username
            )
            """,
            {
                'username': username
            }
        ).fetchall()