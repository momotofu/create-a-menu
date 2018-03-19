from flask import Flask


def create_app():
    app = Flask(__name__)
    return app


def configure_app(app, config=None):
    pass

