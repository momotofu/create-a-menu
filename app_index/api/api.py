from flask import Blueprint, render_template

api = Blueprint('api', __name__)


# API endpoints
@api.route('/images', defaults={'filename': 'filler.jpg'})
@api.route('/images/<filename>')
def image_file(filename):
    return send_from_directory(api.config['IMAGE_FOLDER'], filename)


@api.route('/restaurants/JSON')
def getRestaurantsJSON():
    try:
        restaurants = query_db.get_all(session, Restaurant)
        return jsonify(Restaurants=[restaurant.serialize for restaurant in
            restaurants])
    except:
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


# Routes
