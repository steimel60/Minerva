from typing import Optional
import pathlib
import sqlite3

from db import dbs_dir


def db_path(org_name: str) -> str:
    return pathlib.Path(dbs_dir, f"{org_name}.db")


def exists(org_name: str) -> bool:
    """Check if a database exists for a given organization/company name."""
    return pathlib.Path(db_path(org_name)).exists()


def connect(org_name: str) -> Optional[sqlite3.Connection]:
    """
    Get sql connection for given organization/company.
    Returns None if no db exists.
    """
    return sqlite3.connect(db_path(org_name)) if exists(org_name) else None
