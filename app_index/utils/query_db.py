def get_all(session, object):
    return session.query(object).all()

def get_one(session, object, o_id):
    return session.query(object).filter(object.id == o_id).one()

def get_items(session, object, restaurant_id):
    return session.query(object).filter_by(restaurant_id = restaurant_id).all()

def delete(session, object):
    session.delete(object)

def update(session, object):
    session.add(object)
