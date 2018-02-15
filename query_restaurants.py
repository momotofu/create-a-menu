from database_setup import Restaurant

def get_restaurants(session):
    return session.query(Restaurant).all()
