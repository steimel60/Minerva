import sqlite3 as sql, os
import accounts as accts
#from relations import npc_settlement

def org_exists(org_name: str) -> bool:
    """Check if a database exists for a given organization/company name."""
    return os.path.exists(get_db_path_by_name(org_name))

def connect_to_org(org_name: str) -> sql.Connection:
    """
    Get sql connection for given organization/company.
    Returns None if no db exists.
    """
    return (
        sql.connect(get_db_path_by_name(org_name))
        if org_exists(org_name) else None
    )

def add_organization(org_name: str) -> sql.Connection:
    """
    Create a database for a new organization and return sql connection.
    Returns None if DB already exists.
    """
    return (
        sql.connect(get_db_path_by_name(org_name))
        if not org_exists(org_name) else None
    )

organization_dbs_path = os.path.abspath(os.path.join(
    os.path.dirname( __file__ ), 
    '..', 
    '..',
    'Organizations'
))

def get_db_path_by_name(org_name: str) -> str:
    return os.path.join(
        organization_dbs_path,
        f"{org_name}.db"
    )

# what is the point of the bool below?
# why are these functions in orgs?
def create_all_tables(org_conn: sql.Connection, make_accts: bool = True):
    if make_accts: accts.create_table(org_conn)

def drop_all_tables(org_conn: sql.Connection, drop_accts: bool = True):
    if drop_accts: accts.drop_table(org_conn)

