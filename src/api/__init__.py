import tomllib
import flask

def factory(config):
    app = flask.Flask(__name__)
    with open(config, "rb") as fh:
        app.config.from_mapping(tomllib.load(fh))

    from . import auth
    auth.setup()
    app.register_blueprint(auth.bp)

    return app

