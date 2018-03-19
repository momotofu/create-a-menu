class Config(object):
    DEBUG = False
    TESTING = False
    DATABASE_URI = 'sqlite:///restaurantmenu.db'

    IMAGE_FOLDER = './static/images'
    ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'png', 'gif'])
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

class DevelopmentConfig(Config):
    DEBUG = True
