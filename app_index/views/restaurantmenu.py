import os

from flask import Blueprint, render_template, request, current_app as app
from flask import session as login_session
from werkzeug.utils import secure_filename

from app_index.utils import query_db
from app_index.utils.utils import allowed_file
from app_index.model import Base, Restaurant, MenuItem

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

restaurant_menu = Blueprint('restaurant_menu',
                            __name__,
                            template_folder='templates')

@restaurant_menu.route('/restaurants/<int:restaurant_id>/')
def restaurantMenu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id = restaurant_id)
    if 'username' not in login_session:
        return render_template('menu/publicmenu.html', restaurant=restaurant,
                menuItems=items)
    return render_template('menu/menu.html', restaurant=restaurant, menuItems=items)


@restaurant_menu.route('/restaurants/<int:restaurant_id>/new-item/', methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
    if 'username' not in login_session:
        return redirect(url_for('login'))

    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    if request.method == 'GET':
        return render_template('menu/newMenuItem.html', restaurant=restaurant)

    if request.method == 'POST':
        params = request.form
        if 'image' in request.files.keys():
            image = request.files['image']
        else:
            image = None

        try:
            if image and allowed_file(image.filename, app):
                filename = secure_filename(image.filename)
                print('Image path: ', os.path, os.path.join(app.config['IMAGE_FOLDER']))
                image.save(os.path.join(app.config['IMAGE_FOLDER'], filename))
            else:
                filename = 'image-filler.jpg'
            item = MenuItem(
                    name=params['name'],
                    price=params['price'],
                    course=params['course'],
                    description=params['description'],
                    image=filename,
                    user_id=login_session['user-id']
                    )
            session.add(item)
            session.commit()

            flash("new menu item created!")

            return redirect(url_for('restaurant_menu.restaurantMenu',
                restaurant_id=restaurant.id))

        except:
            session.rollback()
            raise
            return render_template('menu/newMenuItemFailed.html',
                    restaurant=restaurant)


@restaurant_menu.route(
    '/restaurants/<int:restaurant_id>/<int:menu_id>/edit',
    methods=['GET','POST']
    )
def editMenuItem(restaurant_id, menu_id):
    if 'username' not in login_session:
        return redirect(url_for('login'))

    try:
        restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
        menuItem = session.query(MenuItem).filter_by(id = menu_id).one()
    except:
        raise
        return

    if request.method == 'GET':
        return render_template('menu/editMenuItem.html', restaurant=restaurant,
                item=menuItem)

    if request.method == 'POST':
        params = request.form
        if 'image' in request.files.keys():
            image = request.files['image']
        else:
            image = None
        try:
            if menuItem.name != params['name']:
                menuItem.name = params['name']
            if menuItem.price != params['price']:
                menuItem.price = params['price']
            if menuItem.description != params['description']:
                menuItem.description = params['description']
            if menuItem.course != params['course']:
                menuItem.course = params['course']
            if image and allowed_file(image.filename, app):
                filename = secure_filename(image.filename)
                image.save(os.path.join(app.config['IMAGE_FOLDER'], filename))
                menuItem.image = filename

            session.add(menuItem)
            session.commit()

            flash("Successfuly edited %s" % menuItem.name)

            return redirect(url_for("restaurant_menu.restaurantMenu",
                restaurant_id=restaurant.id))
        except:
            session.rollback()
            print('what 2')
            raise
            return render_template('menu/editMenuItemFailed.html',
                    restaurant=restaurant, item=menuItem)

@restaurant_menu.route('/restaurants/<int:restaurant_id>/<int:menu_id>/delete/',
    methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
    if 'username' not in login_session:
        return redirect(url_for('login'))

    menuItem = query_db.get_one(session, MenuItem, menu_id)
    restaurant = query_db.get_one(session, Restaurant, restaurant_id)

    if request.method == 'GET':
        return render_template('menu/confirmMenuItemDelete.html',
                restaurant=restaurant, item=menuItem)
    if request.method == 'POST':
        restaurant_path = '/'.join(request.path.split('/')[:3])
        if request.form['should_delete'].lower() == 'yes':
            try:
                query_db.delete(session, menuItem)
                session.commit()

                flash("successfully deleted %s" % menuItem.name)

                return redirect(url_for('restaurant_menu.restaurantMenu', restaurant_id=restaurant.id))
            except:
                session.rollback()
                raise
                return render_template('menu/deleteMenuItemFailed',
                        restaurant=restaurant, item=menuItem)
        else:
            return redirect(url_for('restaurant_menu.restaurantMenu',
                restaurant_id=restaurant.id))
