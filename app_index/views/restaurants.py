from flask import Blueprint, render_template

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
