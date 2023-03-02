from flask import (
    Blueprint,
    url_for,
    request,
    render_template,
    flash, g, redirect, session
)
import pathlib
import sqlite.accounts as accts
import sqlite.organizations as orgs
import sqlite.login as _login

def setup():
    db_dir = pathlib.Path.cwd() / "Organizations"
    if not db_dir.exists():
        db_dir.mkdir()

    orgs.organization_dbs_path = db_dir # overwrites global
    orgs.make_org("Primal")
    accts.create_table(orgs.connect_to_org("Primal"))

def parse_form(form):
    return tuple([
        request.form.get(field, None) for field in [
            "organization", "username", "password",
        ]
    ])

bp = Blueprint("auth", __name__, url_prefix="/auth")

@bp.route("/register", methods=[ "GET", "POST" ])
def register():
    if request.method == "POST":
        org, uname, password = parse_form(request.form)
        if not all([org, uname, password]):
            return "Bad Request: Missing form parameters", 400

        if not orgs.org_exists(org):
            return f"Organization {org} does not exist", 400
        
        org_conn = orgs.connect_to_org(org)     
        if accts.acct_exists(org_conn, uname): # assumes accts table exists
            return f"Account with username: {uname} already exists", 400
        
        # THIS WILL BE DONE CLIENT SIDE IN FUTURE!!!!
        # OBVIOUSLY DO NOT SEND PLAINTEXT PASS OVER NETWORK!!!
        # ONCE THE "PASSWORD" ARRIVES AT THIS POINT, IT SHOULD JUST BE A HASH
        # AND ITS CONTENTS UNABLE TO BE EXAMINED
        if not _login.is_pw_valid(password)[0]:
            return f"Bad password: {_login.is_pw_valid(password)[1]}", 400
        
        if not accts.insert_acct(org_conn, uname, password):
            return "Could not create account", 500
        
        return "Created Account", 200

    return "register", 200

@bp.route("/login", methods=[ "GET", "POST" ])
def login():
    if request.method == "POST":
        org, uname, password = parse_form(request.form)
        if not all([org, uname, password]):
            return "Bad Request: Missing form parameters", 400
        
        if not orgs.org_exists(org):
            return f"Organization {org} does not exist", 400            
        if not _login.good_login(org, uname, password):
            return "Bad Login", 400
        
        return "Logged In", 200
    
    return "login", 200

@bp.route("/logout", methods=[ "GET" ])
def logout():
    return "logout", 200