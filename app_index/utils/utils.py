def allowed_file(filename, app):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in
            app.config['ALLOWED_EXTENSIONS']
