def get_all(session, object):
    return session.query(object).all()

def get_one(session, object, o_id):
    return session.query(object).filter(object.id == o_id).one()
