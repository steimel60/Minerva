from flask import Blueprint, request

import aux
import db.accounts
import db.organization
import db.login

bp = Blueprint("auth", __name__, url_prefix="/auth")

required_fields = [
    "organization", "username", "password",
]

@bp.route("/register", methods=[ "GET", "POST" ])
def register():
    if request.method == "POST":
        org, uname, password = aux.get_fields(request.form, required_fields)
        if not all([org, uname, password]):
            return "Bad Request: Missing form parameters", 400

        if not db.organization.exists(org):
            return f"Organization {org} does not exist", 400

        org_conn = db.organization.connect(org)     
        if db.accounts.acct_exists(org_conn, uname): # assumes accts table exists
            return f"Account with username: {uname} already exists", 400

        # THIS WILL BE DONE CLIENT SIDE IN FUTURE!!!!
        # OBVIOUSLY DO NOT SEND PLAINTEXT PASS OVER NETWORK!!!
        # ONCE THE "PASSWORD" ARRIVES AT THIS POINT, IT SHOULD JUST BE A HASH
        # AND ITS CONTENTS UNABLE TO BE EXAMINED
        if not db.login.is_pw_valid(password)[0]:
            return f"Bad password: {db.login.is_pw_valid(password)[1]}", 400
        
        if not db.accounts.insert(org_conn, uname, password):
            return "Could not create account", 500
        
        return "Created Account", 200

    return "register", 200

@bp.route("/login", methods=[ "GET", "POST" ])
def login():
    if request.method == "POST":
        org, uname, password = aux.get_fields(request.form, required_fields)
        if not all([org, uname, password]):
            return "Bad Request: Missing form parameters", 400
        
        if not db.organization.exists(org):
            return f"Organization {org} does not exist", 400            
        if not db.login.good_login(org, uname, password):
            return "Bad Login", 400
        
        return "Logged In", 200
    
    return "login", 200

@bp.route("/logout", methods=[ "GET" ])
def logout():
    return "logout", 200