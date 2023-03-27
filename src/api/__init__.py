import logging
import pathlib
import tomllib
import flask

import db

logging.basicConfig(filename="minerva.log", level=logging.DEBUG)

DEBUG = True

def factory(config):
    app = flask.Flask(__name__)
    with open(config, "rb") as fh:
        config = tomllib.load(fh)

    work_dir = pathlib.Path.cwd()

    if not DEBUG:
        sql_init_files = list((work_dir / "db").glob("*.sql"))  
    else:
        sql_init_files = list((work_dir / "src" / "db").glob("*.sql"))
        sql_init_files.append(
            work_dir / "tests" / "populate_tables.sql"
        )

    db.setup(
        work_dir,
        config["db"]["orgs"],
        sql_init_files,
    )
    
    from . import auth
    app.register_blueprint(auth.bp)

    from . import sales
    app.register_blueprint(sales.bp)

    return app

