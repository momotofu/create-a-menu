class query_db(self):
    """
    Query object to expose common queries.
    """

    def get_all(session, p_class):
        return session.query(Restaurant).all()
