import pathlib
import sqlite3

def org_exists(org_name: str) -> bool:
    """Check if a database exists for a given organization/company name."""
    return pathlib.Path(get_org_db_path(org_name)).exists()

def connect_to_org(org_name: str) -> sqlite3.Connection:
    """
    Get sql connection for given organization/company.
    Returns None if no db exists.
    """
    return (
        sqlite3.connect(get_org_db_path(org_name))
        if org_exists(org_name) else None
    )

def make_org(org_name: str) -> sqlite3.Connection:
    """
    Create a database for a new organization and return sql connection.
    Returns None if DB already exists.
    """
    return (
        sqlite3.connect(get_org_db_path(org_name))
        if not org_exists(org_name) else None
    )

# global that may be overwritten
organization_dbs_path = pathlib.Path.cwd().parent.parent / "Organizations"

def get_org_db_path(org_name: str) -> str:
    return pathlib.Path(organization_dbs_path, f"{org_name}.db")