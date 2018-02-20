from flask import Flask, request, redirect, render_template, url_for, flash
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

from html_builder import HTML_Builder as HB
import query_db

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
@app.route('/restaurants')
def allRestaurants():
    restaurants = query_db.get_all(session, Restaurant)
    return render_template('restaurants.html', restaurants=restaurants)


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
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    menuItem = session.query(MenuItem).filter_by(id = menu_id).one()
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

            flash("Successfuly edited %s's %s" % (restaurant.name,
                    menuItem.name))

            return redirect(url_for("restaurantMenu",
                restaurant_id=restaurant.id))

        except:
            session.rollback()
            raise
            return render_template('editMenuItemFailed.html',
                    restaurant=restaurant, item=menuItem)

@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/delete/',
    methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
    menuItem = query_db.get_one(session, MenuItem, menu_id)
    restaurant = query_db.get_one(session, Restaurant, restaurant_id)
    output = HB()

    if request.method == 'GET':
        output.add_html("""
            <h1>Are you sure you want to delete %s</h1>
            <form method='POST' action='%s'>
                <input type='submit' name='should_delete' value='YES'>
                <input type='submit' name='should_delete' value='NO'>
            </form>
            """ % (menuItem.name, request.path)
            )
        return output.get_html()

    if request.method == 'POST':
        restaurant_path = '/'.join(request.path.split('/')[:3])
        if request.form['should_delete'].lower() == 'yes':
            try:
                query_db.delete(session, menuItem)
                session.commit()

                output.add_html("""
                    <h1>Successfully deleted %s</h1>
                    <a href='%s'>Back to %s</a>
                    """ % (menuItem.name, restaurant_path, restaurant.name)
                    )
                return output.get_html()
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
