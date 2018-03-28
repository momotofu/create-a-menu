import random, string

def allowed_file(filename, app):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def get_rand_string():
    return ''.join(random.choice(string.ascii_uppercase + string.digits +
        string.ascii_lowercase) for x in range(32))
