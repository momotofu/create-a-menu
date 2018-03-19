from flask import Flask


def create_app():
    app = config_app(Flask(__name__))
    return app


def configure_app(app, config_object=None):
    from config import Config as default_config

    if config_object:
        app.config.from_object(config_object)
    else:
        app.config.from_object(default_config)

    return app
