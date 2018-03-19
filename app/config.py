class Config(object):
    DEBUG = False
    TESTING = False
    DATABASE_URI = 'sqlite:///restaurantmenu.db'

class DevelopmentConfig(Config):
    DEBUG = True
