import pathlib
import sqlite3 as sql
import organizations as orgs
import accounts as accts
import roles
import permissions as perms
from relations import acct_role
from relations import role_permissions as role_perm

def login(org_name: str, username: str, password: str) -> bool:
    if orgs.org_exist(org_name):
        org_conn = orgs.connect_to_org(org_name)
        return accts.is_valid_login(org_conn, username, password)
    else: return False

def get_is_pw_valid(password: str) -> list[bool, str]:
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

def make_account(org_conn: sql.Connection, username: str, password: str):
    pw_results = get_is_pw_valid(password)
    if accts.username_exist(org_conn, username):
        print(f"Username, {username}, already exists!")
    elif pw_results[0]:
        accts.insert(org_conn, username, password)
        print(f"Successfully created account, {username}")
    else:
        print(pw_results[1])

if __name__ == "__main__":
    # Make sure local Organizations folder exists, can be deleted later
    p = pathlib.Path(__file__).parents[2] / "Organizations" 
    p.mkdir(exist_ok = True)

    org_name = "Primal"

    org_conn = orgs.connect_to_org(org_name)
    if org_conn is None: org_conn = orgs.add_organization(org_name)
    orgs.drop_all_tables(org_conn)
    orgs.create_all_tables(org_conn)
    accts.insert(org_conn, "Steimel60", "easy123")
    accts.insert(org_conn, "Steimel60", "easy123")
    make_account(org_conn, "Steimel60", "Easy123")
    make_account(org_conn, "User1", "passworD2")
    make_account(org_conn, "User2", "Password1")
    roles.insert(org_conn, "Owner")
    roles.insert(org_conn, "Sales")
    perms.insert(org_conn, "AddAccount")
    perms.insert(org_conn, "DeleteAccount")
    perms.insert(org_conn, "CreateOrder")
    role_perm.insert(org_conn, "Owner", "AddAccount")
    role_perm.insert(org_conn, "Owner", "DeleteAccount")
    role_perm.insert(org_conn, "Sales", "CreateOrder")
    acct_role.insert(org_conn, "Steimel60", "Owner")
    acct_role.insert(org_conn, "User1", "Sales")
    acct_role.insert(org_conn, "User2", "Sales")
    print(acct_role.get_users_with_role(org_conn, "Sales"))
    print(acct_role.get_users_with_role(org_conn, "Owner"))
    print("Permissions of owner:", role_perm.get_permissions_of_role(org_conn, "Owner"))
    print("Permissions of user, Steimel60: ", role_perm.get_permissions_of_user(org_conn, "Steimel60"))