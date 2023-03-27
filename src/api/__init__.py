import logging
import pathlib
import tomllib
import flask

import db

def factory(config):
    app = flask.Flask(__name__)
    with open(config, "rb") as fh:
        config = tomllib.load(fh)

    work_dir = pathlib.Path.cwd()
    db.setup(
        work_dir,
        config["db"]["orgs"],
        (work_dir / "db").glob("*.sql"),
    )
    
    from . import auth
    app.register_blueprint(auth.bp)

    from . import sales
    app.register_blueprint(sales.bp)

    return app

