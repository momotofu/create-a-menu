def get_all(session, object):
    return session.query(object).all()

def get_one_restaurant(session, object, restaurant_id):
    return session.query(object).filter(object.id == restaurant_id).one()
