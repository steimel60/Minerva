import sqlite3
import db.organization as orgs, db.accounts as accts


def good_login(org_name: str, username: str, password: str) -> bool:
    return orgs.exists(org_name) and accts.is_valid_acct(
        orgs.connect(org_name), username, password
    )


def is_pw_valid(password: str) -> list[bool, str]:
    valid = True
    msg = "[ERROR] Invalid Password."
    if len(password) < 6:
        valid = False
        msg += "\n\t- Password must have at least 6 characters."
    if not any([a.isupper() for a in password]):
        valid = False
        msg += "\n\t- At least 1 uppercase letter required."
    if not any([a.islower() for a in password]):
        valid = False
        msg += "\n\t- At least 1 lowercase letter required."
    if not any([a.isnumeric() for a in password]):
        valid = False
        msg += "\n\t- At least 1 numeric value required."
    return [valid, msg]


def make_account(org_conn: sqlite3.Connection, username: str, password: str) -> None:
    pw_results = is_pw_valid(password)
    if accts.acct_exists(org_conn, username):
        print(f"Username, {username}, already exists!")
    elif pw_results[0]:
        accts.insert(org_conn, username, password)
        print(f"Successfully created account, {username}")
    else:
        print(pw_results[1])
