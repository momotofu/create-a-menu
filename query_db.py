def get_all(session, object):
    return session.query(object).all()
