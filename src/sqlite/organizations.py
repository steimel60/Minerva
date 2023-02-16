import sqlite3 as sql, os
import accounts as accts
#from relations import npc_settlement

def org_exist(org_name: str) -> bool:
    """Check if a database exists for a given organization/company name."""
    db_path = get_db_path_by_name(org_name)
    if os.path.exists(db_path): return True
    else: return False

def connect_to_org(org_name: str) -> sql.Connection:
    """
    Get sql connection for given organization/company.
    Returns None if no db exists.
    """
    if org_exist(org_name):
        conn = sql.connect(get_db_path_by_name(org_name))
        return conn
    else: return None

def add_organization(org_name: str) -> sql.Connection:
    """
    Create a database for a new organization and return sql connection.
    Returns None if DB already exists.
    """
    if org_exist(org_name): return None
    else: return sql.connect(get_db_path_by_name(org_name))

def get_db_path_by_name(org_name: str) -> str:
    return os.path.join(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', '..','Organizations')),f"{org_name}.db")

def create_all_tables(org_conn: sql.Connection, make_accts: bool = True):
    if make_accts: accts.create_table(org_conn)

def drop_all_tables(org_conn: sql.Connection, drop_accts: bool = True):
    if drop_accts: accts.drop_table(org_conn)

