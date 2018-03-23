from flask import Blueprint, render_template, send_from_directory, jsonify
from flask import make_response, request, current_app as app

from app_index.utils import query_db
from app_index.model import Base, Restaurant, MenuItem
from app_index.api import utils

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


@api.route('/restaurants/JSON', methods=['GET', 'POST', 'DELETE'])
def restaurantsJSON():
    restaurants = query_db.get_all(session, Restaurant)

    if request.method == 'GET':
        try:
            return jsonify(Restaurants=[restaurant.serialize for restaurant in
                restaurants])
        except:
            raise
    elif request.method == 'POST':
        restaurant = Restaurant(name=request.form['name'])

        if 'user_id' in request.form:
            restaurant.user_id = request.args.get('user_id')
        else:
            restaurant.user_id = 1
        try:
            query_db.update(session, restaurant)
            session.commit()
            return jsonify(Restaurants=[restaurant.serialize for restaurant in
                restaurants])
        except:
            session.rollback()
            raise
    elif request.method == 'DELETE':
        try:
            restaurant = query_db.get_one(session, Restaurant,
                    request.form['id'])
            query_db.delete(session, restaurant)
            session.commit()

            return make_response('succes', 200)
        except:
            session.rollback()
            return make_response('error', 404)

@api.route('/newRestaurant/JSON', methods=['POST'])
def newRestaurant():
    print('hit')
    address = request.args.get('address', '')
    meal_type = request.args.get('meal_type', '')
    print('address: ', address, 'meal_type: ', meal_type)
    restaurant_info = utils.findRestaurant(address, meal_type)

    if restaurant_info != "No results found":
        restaurant = Restaurant(name=restaurant_info['name'])
        try:
            query_db.update(session, restaurant)
            session.commit()
        except:
            session.rollback()
            raise
            return make_response('Error: ', 404)
    else:
        return make_response('No restaurants found for %s in %s' % (meal_type,
            location), 404)


@api.route('/restaurants/<int:restaurant_id>/JSON')
def restaurantJSON(restaurant_id):
    try:
        restaurant = query_db.get_one(session, Restaurant, restaurant_id)
        return jsonify(restaurant.serialize)
    except:
        raise


@api.route('/restaurants/<int:restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
    try:
        restaurant = query_db.get_one(session, Restaurant, restaurant_id)
        items = query_db.get_items(session, MenuItem, restaurant_id)
        return jsonify(MenuItems=[item.serialize for item in items])
    except:
        raise


@api.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def restaurantMenuItemJSON(restaurant_id, menu_id):
    try:
        item = query_db.get_one(session, MenuItem, restaurant_id)
        return jsonify(item.serialize)
    except:
        raise


