from flask import Blueprint, render_template, send_from_directory, jsonify
from flask import request, current_app as app

from app_index.utils import query_db
from app_index.model import Base, Restaurant, MenuItem

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

api = Blueprint('api', __name__)


# API endpoints
@api.route('/images', defaults={'filename': 'filler.jpg'})
@api.route('/images/<filename>')
def image_file(filename):
    return send_from_directory('static/images', filename)


@api.route('/restaurants/JSON', methods=['GET', 'POST'])
def getRestaurantsJSON():
    if request.method == 'GET':
        try:
            restaurants = query_db.get_all(session, Restaurant)
            return jsonify(Restaurants=[restaurant.serialize for restaurant in
                restaurants])
        except:
            raise
    elif request.method == 'POST':
        restaurant = Restaurant(name=request.args.get('name'))

        try:
            query_db.update(session, restaurant)
            session.commit()
            return jsonify(Restaurants=[restaurant.serialize for restaurant in
                restaurants])
        except:
            session.rollback()
            raise


@api.route('/restaurants/<int:restaurant_id>/JSON')
def getRestaurantJSON(restaurant_id):
    try:
        restaurant = query_db.get_one(session, Restaurant, restaurant_id)
        return jsonify(restaurant.serialize)
    except:
        raise


@api.route('/restaurants/<int:restaurant_id>/menu/JSON')
def getRestaurantMenuJSON(restaurant_id):
    try:
        restaurant = query_db.get_one(session, Restaurant, restaurant_id)
        items = query_db.get_items(session, MenuItem, restaurant_id)
        return jsonify(MenuItems=[item.serialize for item in items])
    except:
        raise


@api.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def getRestaurantMenuItemJSON(restaurant_id, menu_id):
    try:
        item = query_db.get_one(session, MenuItem, restaurant_id)
        return jsonify(item.serialize)
    except:
        raise


