from flask import Flask
from app_index.config import Config as default_config


def create_app(app_name, config=None):
    app = configure_app(Flask(__name__), config)
    configure_blueprints(app)
    return app


def configure_app(app, config_object=None):
    if config_object:
        app.config.from_object(config_object)
    else:
        app.config.from_object(default_config)

    return app


def configure_blueprints(app):
    from .views.restaurants import restaurants
    from .views.restaurantmenu import restaurant_menu
    from .views.login import login

    for blueprint in [restaurants, restaurant_menu, login]:
        print('type: ', type(blueprint))
        app.register_blueprint(blueprint)

    return app
