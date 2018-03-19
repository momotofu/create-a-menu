import os
import sys

# update system path
sys.path.append(os.path.join(sys.path[0],'utils'))

from flask import Flask, request, redirect, render_template
from flask import url_for, flash, jsonify, send_from_directory
from werkzeug.utils import secure_filename

# session token creation
from flask import session as login_session
import random, string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from flask import make_response

import httplib2
import json
import requests

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model import Base, Restaurant, MenuItem, User
from sqlalchemy.exc import DBAPIError

from html_builder import HTML_Builder as HB
import query_db


app = Flask(__name__)

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def getUserInfo(user_id):
    user = session.query(User).filter_by(id = user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email = email).one()
        return user.id
    except:
        return None


def createUser(login_session):
    newUser = User(name = login_session['username'],
                    email = login_session['email'],
                    picture = login_session['picture'])
    try:
        session.add(newUser)
        session.commit()
        user = session.query(User).filter_by(email=login_session['email']).one()
        return user.id
    except:
        raise


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
# Assets
@app.route('/images', defaults={'filename': 'filler.jpg'})
@app.route('/images/<filename>')
def image_file(filename):
    return send_from_directory(app.config['IMAGE_FOLDER'], filename)


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    short_lived_token = request.data.decode()
    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (app_id, app_secret, short_lived_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1].decode()

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.12/me"
    long_lived_token = result.split(',')[0].split(':')[1].replace('"', '')

    url = '%s?access_token=%s&fields=name,id,email' % (userinfo_url,
            long_lived_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1].decode()
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data['name']
    login_session['email'] = data['email']
    login_session['facebook_id'] = data['id']

    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = long_lived_token

    # Get user picture
    url = 'https://graph.facebook.com/v2.12/me/picture?access_token=%s&redirect=0&height=200&width=200' % long_lived_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1].decode()
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = HB()
    output.add_html("""
        <h1>Welcome %s</h1>
        <img src=%s style="width: 300px; height: 300px; border-radius: 150px"/>
        """ % (login_session['username'], login_session['picture'])
        )
    flash("You are now logged in as %s" % login_session['username'])
    return output.get_html()


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('./credentials/google_client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1].decode())
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    client_id = json.loads(open('./credentials/config.json','r').read())['oauth']['google']['client_id']

    if result['issued_to'] != client_id:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = HB()
    output.add_html("""
        <h1>Welcome %s</h1>
        <img src=%s style="width: 300px; height: 300px; border-radius: 150px"/>
        """ % (login_session['username'], login_session['picture'])
        )
    flash("You are now logged in as %s" % login_session['username'])
    return output.get_html()


@app.route('/gdisconnect')
def gdisconnect():
    """
    Revoke a current user's token and reset their login_session
    """
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response



# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('allRestaurants'))
    else:
        flash("You were not logged in")
        return redirect(url_for('allRestaurants'))


@app.route('/login')
def login():
    """
    Create a state token to prevent request forgery
    and store it in the session for later validation
    """
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x
            in range(32))
    login_session['state'] = state
    return render_template('login.html', state=state)

@app.route('/')
@app.route('/restaurants')
def allRestaurants():
    restaurants = query_db.get_all(session, Restaurant)
    if 'username' not in login_session:
        return render_template('publicRestaurants.html',
                restaurants=restaurants)
    return render_template('restaurants.html', restaurants=restaurants)


@app.route('/restaurants/new/', methods=['GET', 'POST'])
def newRestaurant():
    if 'username' not in login_session:
        return redirect(url_for('login'))

    if request.method == 'GET':
        return render_template('newRestaurant.html')
    if request.method == 'POST':
        params = request.form
        if 'name' in params.keys():
           restaurant = Restaurant(name=params['name'],
                                   user_id=login_session['user-id'])
           try:
                query_db.update(session, restaurant)
                session.commit()

                flash('Sucessfully created %s!' % restaurant.name)

                return redirect(url_for('allRestaurants'))
           except:
               raise


@app.route('/restaurants/<int:restaurant_id>/editRestaurant/', methods=['GET', 'POST'])
def editRestaurant(restaurant_id):
    if 'username' not in login_session:
        return redirect(url_for('login'))

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
    if 'username' not in login_session:
        return redirect(url_for('login'))

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
    if 'username' not in login_session:
        return render_template('publicmenu.html', restaurant=restaurant,
                menuItems=items)
    return render_template('menu.html', restaurant=restaurant, menuItems=items)


@app.route('/restaurants/<int:restaurant_id>/new-item/', methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
    if 'username' not in login_session:
        return redirect(url_for('login'))

    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    if request.method == 'GET':
        return render_template('newMenuItem.html', restaurant=restaurant)

    if request.method == 'POST':
        params = request.form
        if 'image' in request.files.keys():
            image = request.files['image']
        else:
            image = None

        try:
            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
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
    if 'username' not in login_session:
        return redirect(url_for('login'))

    try:
        restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
        menuItem = session.query(MenuItem).filter_by(id = menu_id).one()
    except:
        raise
        return

    if request.method == 'GET':
        return render_template('editMenuItem.html', restaurant=restaurant,
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
            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                image.save(os.path.join(app.config['IMAGE_FOLDER'], filename))
                menuItem.image = filename

            session.add(menuItem)
            session.commit()

            flash("Successfuly edited %s" % menuItem.name)

            return redirect(url_for("restaurantMenu",
                restaurant_id=restaurant.id))
        except:
            session.rollback()
            print('what 2')
            raise
            return render_template('editMenuItemFailed.html',
                    restaurant=restaurant, item=menuItem)

@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/delete/',
    methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
    if 'username' not in login_session:
        return redirect(url_for('login'))

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

