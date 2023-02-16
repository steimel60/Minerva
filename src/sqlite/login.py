import sqlite3 as sql, os
import organizations as orgs, accounts as accts

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
    if not os.path.exists(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', '..','Organizations'))):
        os.mkdir(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', '..','Organizations')))

    org_name = "Primal"

    org_conn = orgs.connect_to_org(org_name)
    if org_conn is None: org_conn = orgs.add_organization(org_name)
    orgs.drop_all_tables(org_conn)
    orgs.create_all_tables(org_conn)
    accts.insert(org_conn, "Steimel60", "easy123")
    accts.insert(org_conn, "Steimel60", "easy123")
    print(login("Primal", "Steimel60", "easy123"))
    make_account(org_conn, "Steimel60", "Easy123")
    make_account(org_conn, "User1", "password")
    make_account(org_conn, "User2", "Password1")