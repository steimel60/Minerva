import sqlite3
import unittest
import sqlite.organizations as orgs, sqlite.accounts as accts

def good_login(org_name: str, username: str, password: str) -> bool:
    return (
        orgs.org_exists(org_name)
        and accts.is_valid_acct(
            orgs.connect_to_org(org_name), username, password
        )
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

def make_account(
    org_conn: sqlite3.Connection, 
    username: str, 
    password: str
) -> None:
    pw_results = is_pw_valid(password)
    if accts.acct_exists(org_conn, username):
        print(f"Username, {username}, already exists!")
    elif pw_results[0]:
        accts.insert_acct(org_conn, username, password)
        print(f"Successfully created account, {username}")
    else:
        print(pw_results[1])

if __name__ == "__main__":
    class Tester(unittest.TestCase):
        @classmethod
        def setUpClass(cls):
            if not orgs.organization_dbs_path.exists():
                orgs.organization_dbs_path.mkdir()

            org_name = "Primal"
            org_conn = orgs.connect_to_org(org_name)
            if org_conn is None: 
                org_conn = orgs.make_org(org_name)
            cls._org_conn = org_conn # org_conn now available as Tester._org_conn

            accts.drop_table(org_conn)
            accts.create_table(org_conn)

        def test_acct_insert(self):
            self.assertTrue(accts.insert_acct(Tester._org_conn, "Steimel60", "easy123"))
            self.assertFalse(accts.insert_acct(Tester._org_conn, "Steimel60", "easy123"))

        def test_login(self):
            self.assertTrue(good_login("Primal", "Steimel60", "easy123"))
            self.assertFalse(good_login("", "Steimel60", "easy123"))
        
        def test_make_accounts(self):
            make_account(Tester._org_conn, "Steimel60", "Easy123")
            make_account(Tester._org_conn, "User1", "password")
            make_account(Tester._org_conn, "User2", "Password1")

    unittest.main()