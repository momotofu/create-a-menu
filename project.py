from flask import Flask, request, redirect, render_template
from flask import url_for, flash, jsonify
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem
from sqlalchemy.exc import DBAPIError

from html_builder import HTML_Builder as HB
import query_db

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# API endpoints
@app.route('/restaurants/JSON')
def getRestaurantsJSON():
    try:
        restaurants = query_db.get_all(session, Restaurant)
        return jsonify(Restaurants=[restaurant.serialize for restaurant in
            restaurants])
    except:
        raise


@app.route('/restaurants/<int:restaurant_id>/JSON')
def getRestaurantJSON(restaurant_id):
    try:
        restaurant = query_db.get_one(session, Restaurant, restaurant_id)
        return jsonify(restaurant.serialize)
    except:
        raise


@app.route('/restaurants/<int:restaurant_id>/menu/JSON')
def getRestaurantMenuJSON(restaurant_id):
    try:
        restaurant = query_db.get_one(session, Restaurant, restaurant_id)
        items = query_db.get_items(session, MenuItem, restaurant_id)
        return jsonify(MenuItems=[item.serialize for item in items])
    except:
        raise


@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def getRestaurantMenuItemJSON(restaurant_id, menu_id):
    try:
        item = query_db.get_one(session, MenuItem, restaurant_id)
        return jsonify(item.serialize)
    except:
        raise


# Routes
@app.route('/')
@app.route('/restaurants')
def allRestaurants():
    restaurants = query_db.get_all(session, Restaurant)
    return render_template('restaurants.html', restaurants=restaurants)

@app.route('/restaurants/new/', methods=['GET', 'POST'])
def newRestaurant():
    if request.method == 'GET':
        return render_template('newRestaurant.html')
    if request.method == 'POST':
        params = request.form
        if 'name' in params.keys():
           restaurant = Restaurant(name=params['name'])
           try:
                query_db.update(session, restaurant)
                session.commit()

                flash('Sucessfully created %s!' % restaurant.name)

                return redirect(url_for('allRestaurants'))
           except:
               raise


@app.route('/restaurants/<int:restaurant_id>/editRestaurant/', methods=['GET', 'POST'])
def editRestaurant(restaurant_id):
    restaurant = query_db.get_one(session, Restaurant, restaurant_id)

    if request.method == 'GET':
        return render_template('editRestaurant.html', restaurant=restaurant)
    if request.method == 'POST':
        params = request.form
        if 'name' in params.keys():
            restaurant.name = params['name']
        try:
            query_db.update(session, restaurant)
            session.commit()

            flash("Successfully updated %s!" % restaurant.name)

            return redirect(url_for('allRestaurants'))
        except:
            session.rollback()
            redirect(url_for('allRestaurants'))
            raise


@app.route('/restaurants/<int:restaurant_id>/deleteRestaurant/', methods=['GET', 'POST'])
def deleteRestaurant(restaurant_id):
    try:
        restaurant = query_db.get_one(session, Restaurant, restaurant_id)
    except:
        raise

    if request.method == 'GET':
        return render_template('confirmRestaurantDelete.html',
                restaurant=restaurant)
    if request.method == 'POST':
        params = request.form

        if 'should_delete' in params:
            if params['should_delete']:
                try:
                    query_db.delete(session, restaurant)
                    session.commit()

                    flash("Successfuly deleted %s" % restaurant.name)

                    return redirect(url_for('allRestaurants'))
                except:
                    session.rollback()
                    raise



@app.route('/restaurants/<int:restaurant_id>/')
def restaurantMenu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id = restaurant_id)
    return render_template('menu.html', restaurant=restaurant, menuItems=items)


@app.route('/restaurants/<int:restaurant_id>/new-item/', methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    if request.method == 'GET':
        return render_template('newMenuItem.html', restaurant=restaurant)

    if request.method == 'POST':
        params = request.form
        # TODO: form validation
        try:
            item = MenuItem(
                    name=params['name'],
                    price=params['price'],
                    course=params['course'],
                    description=params['description'],
                    restaurant=restaurant
                    )
            session.add(item)
            session.commit()

            flash("new menu item created!")

            return redirect(url_for('restaurantMenu',
                restaurant_id=restaurant.id))

        except:
            session.rollback()
            raise
            return render_template('newMenuItemFailed.html',
                    restaurant=restaurant)


@app.route(
    '/restaurants/<int:restaurant_id>/<int:menu_id>/edit',
    methods=['GET','POST']
    )
def editMenuItem(restaurant_id, menu_id):
    print('requested')
    try:
        restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
        menuItem = session.query(MenuItem).filter_by(id = menu_id).one()
    except:
        raise
        return

    print('continued')
    if request.method == 'GET':
        return render_template('editMenuItem.html', restaurant=restaurant,
                item=menuItem)

    if request.method == 'POST':
        params = request.form
        try:
            if menuItem.name != params['name']:
                menuItem.name = params['name']
            if menuItem.price != params['price']:
                menuItem.price = params['price']
            if menuItem.description != params['description']:
                menuItem.description = params['description']
            if menuItem.course != params['course']:
                menuItem.course = params['course']

            session.add(menuItem)
            session.commit()

            flash("Successfuly edited %s" % menuItem.name)

            return redirect(url_for("restaurantMenu",
                restaurant_id=restaurant.id))
        except DBAPIError or BaseException:
            print('error')
            session.rollback()
            print('error: ', DBAPIError)
            # raise
            return render_template('editMenuItemFailed.html',
                    restaurant=restaurant, item=menuItem)

@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/delete/',
    methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
    menuItem = query_db.get_one(session, MenuItem, menu_id)
    restaurant = query_db.get_one(session, Restaurant, restaurant_id)

    if request.method == 'GET':
        return render_template('confirmMenuItemDelete.html',
                restaurant=restaurant, item=menuItem)
    if request.method == 'POST':
        restaurant_path = '/'.join(request.path.split('/')[:3])
        if request.form['should_delete'].lower() == 'yes':
            try:
                query_db.delete(session, menuItem)
                session.commit()

                flash("successfully deleted %s" % menuItem.name)

                return redirect(url_for('restaurantMenu', restaurant_id=restaurant.id))
            except:
                session.rollback()
                raise
                return render_template('deleteMenuItemFailed',
                        restaurant=restaurant, item=menuItem)
        else:
            return redirect(url_for('restaurantMenu',
                restaurant_id=restaurant.id))

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port=5000)
