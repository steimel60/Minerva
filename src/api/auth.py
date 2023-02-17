from flask import (
    Blueprint,
    url_for,
    request,
    render_template,
    flash, g, redirect, session
)

bp = Blueprint("auth", __name__, url_prefix="/auth")

@bp.route("/register", methods=[ "GET", "POST" ])
def register():
    if request.method == "POST":
        pass

    return "register", 200

@bp.route("/login", methods=[ "GET", "POST" ])
def login():
    if request.method == "POST":
        pass

    return "login", 200

@bp.route("/logout", methods=[ "GET" ])
def logout():
    return "logout", 200

