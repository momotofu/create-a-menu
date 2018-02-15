def get_all(session, p_class):
    return session.query(Restaurant).all()
