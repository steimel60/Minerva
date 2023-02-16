import sqlite3

def create_organizations_table(connection):
    with connection:
        c = connection.cursor()
        c.execute("""CREATE TABLE orgs (
            org_id INTEGER NOT NULL PRIMARY KEY,
            org_name TEXT NOT NULL
        )""")

def create_accounts_table(connection):
    with connection:
        c = connection.cursor()
        c.execute("""CREATE TABLE accts (
            acct_name TEXT NOT NULL PRIMARY KEY,
            acct_pw TEXT NOT NULL
        )""")

def create_acct_org_table(connection):
    with connection:
        c = connection.cursor()
        c.execute("""CREATE TABLE works_at (
            acct_name TEXT NOT NULL,
            org_id INTEGER NOT NULL,
            CONSTRAINT PK_works_at PRIMARY KEY (acct_name, org_id)
            CONSTRAINT FK_acct_name FOREIGN KEY(acct_name)
                REFERENCES accts (acct_name),
            CONSTRAINT FK_org_id FOREIGN KEY(org_id)
                REFERENCES orgs (org_id)
        )""")

def create_all_tables(orgs_conn, accts_conn, wa_conn):
    create_organizations_table(orgs_conn)
    create_accounts_table(accts_conn)
    create_acct_org_table(wa_conn)

def drop_organizations_table(connection):
    with connection:
        c = connection.cursor()
        c.execute("""DROP TABLE IF EXISTS orgs""")

def drop_accounts_table(connection):
    with connection:
        c = connection.cursor()
        c.execute("""DROP TABLE IF EXISTS accts""")

def drop_works_at_table(connection):
    with connection:
        c = connection.cursor()
        c.execute("""DROP TABLE IF EXISTS works_at""")

def drop_all_tables(orgs_conn, accts_conn, wa_conn):
    drop_works_at_table(wa_conn)
    drop_organizations_table(orgs_conn)
    drop_accounts_table(accts_conn)

def insert_organization(connection, org_name: str) -> int:
    """
    Add organization to orgs table.
    Returns: Organization ID    
    """
    with connection:
        c = connection.cursor()
        c.execute("""SELECT COUNT(org_id) FROM orgs""")
        org_id = c.fetchone()[0]
        c.execute("INSERT INTO orgs VALUES (:org_id, :org_name)"
        ,{'org_id':org_id, 'org_name':org_name})

def insert_account(connection, acct_name: str, acct_pw: str) -> int:
    """
    Add account to accts table.
    Returns: account ID    
    """
    with connection:
        c = connection.cursor()
        c.execute("INSERT INTO accts VALUES (:acct_name, :acct_pw)"
        ,{'acct_name':acct_name, 'acct_pw':acct_pw})
        return acct_name

def insert_works_at(connection, acct_name, org_id):
    with connection:
        c = connection.cursor()
        c.execute("INSERT INTO works_at VALUES (:acct_name, :org_id)"
        ,{'acct_name':acct_name, 'org_id':org_id})

def get_organization_exists(connection, org_id) -> bool:
    with connection:
        c = connection.cursor()
        c.execute("SELECT * from orgs WHERE org_id =:org_id ",
        {'org_id':org_id})
        return len(c.fetchall()) > 0

def get_acct_exists(connection, acct_name) -> bool:
    with connection:
        c = connection.cursor()
        c.execute("""SELECT * FROM accts WHERE acct_name =:acct_name""", {'acct_name':acct_name})
        return len(c.fetchall()) > 0

def get_org_name(connection, org_id: int) -> str:
    with connection:
        c = connection.cursor()
        c.execute("""SELECT org_name FROM orgs WHERE org_id =:org_id""", {'org_id':org_id})
        return c.fetchone()[0]

def get_org_by_user(wa_conn, acct_name: str) -> int:
    with wa_conn:
        c = wa_conn.cursor()
        c.execute("""SELECT org_id FROM works_at WHERE acct_name =:acct_name""", {'acct_name':acct_name})
        return c.fetchone()[0]

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

def make_account(org_conn, acct_conn, wa_conn, org_id, acct_name, acct_pw):
    pw_check = get_is_pw_valid(acct_pw)
    if get_organization_exists(org_conn, org_id):
        if get_acct_exists(acct_conn, acct_name):
            print(f"Username, {acct_name}, already exists!")
        elif not pw_check[0]:
            print(pw_check[1])
        else:
            acct_name = insert_account(acct_conn, acct_name, acct_pw)
            insert_works_at(wa_conn, acct_name, org_id)
            print(f"Successfully created account, {acct_name}, at {get_org_name(org_conn, org_id)}!")
    else:
        print(f"Organization ID, {org_id}, does not exist!")

def print_orgs(connection):
    with connection:
        c = connection.cursor()
        c.execute("""SELECT * FROM orgs""")
        for org in c.fetchall():
            print(f"ID: {org[0]}    Name: {org[1]}")

def print_accts(connection):
    with connection:
        c = connection.cursor()
        c.execute("""SELECT * FROM accts""")
        for acct in c.fetchall():
            print(f"Username: {acct[0]}    PW: {acct[1]}")

def print_all_accounts(org_conn, acct_conn, wa_conn):
    with wa_conn:
        c = wa_conn.cursor()
        c.execute("""SELECT * FROM works_at""")
        wa = c.fetchall()
        for acct_name, org_id in wa:
            print(f"{acct_name} works at {get_org_name(org_conn, org_id)}!")

def login(acct_conn, username, pw):
    with acct_conn:
        c = acct_conn.cursor()
        c.execute("""SELECT acct_name FROM accts WHERE acct_name =:username AND acct_pw =:pw""",
        {'username':username, 'pw':pw})
    return len(c.fetchall()) > 0

if __name__ == "__main__":
    conn_orgs = sqlite3.connect('orgs.db')
    conn_accts = sqlite3.connect('accts.db')
    conn_wa   = sqlite3.connect('woks_at.db')
    drop_all_tables(conn_orgs, conn_accts, conn_wa)
    create_all_tables(conn_orgs, conn_accts, conn_wa)
    insert_organization(conn_orgs, "Primal Brewery")
    insert_organization(conn_orgs, "D9 Brewery")
    make_account(conn_orgs, conn_accts, conn_wa, 0, "steimel60", "issaPW123!")
    make_account(conn_orgs, conn_accts, conn_wa, 0, "steimel60", "issaPW123!")
    make_account(conn_orgs, conn_accts, conn_wa, 2, "steimel60", "issaPW123!")
    make_account(conn_orgs, conn_accts, conn_wa, 1, "novitt10", "!")
    print(f"get_org_by_user(steimel60) = {get_org_name(conn_orgs, get_org_by_user(conn_wa, 'steimel60'))}")
    print_orgs(conn_orgs)
    print_accts(conn_accts)
    print_all_accounts(conn_orgs, conn_accts, conn_wa)
    print(f"""Login Attempt: username:steimel60 pw: issapw123!  success: {login(conn_accts, 'steimel60', 'issapw123!')}""")
    print(f"""Login Attempt: username:steimel60 pw: issaPW123!  success: {login(conn_accts, 'steimel60', 'issaPW123!')}""")