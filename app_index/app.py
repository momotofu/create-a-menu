from flask import Flask
from app_index.config import Config as default_config


def create_app(app_name, config=None):
    app = configure_app(Flask(__name__), config)
    return app


def configure_app(app, config_object=None):

    if config_object:
        app.config.from_object(config_object)
    else:
        app.config.from_object(default_config)

    return app
