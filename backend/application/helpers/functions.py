from flask import current_app

def url(path):
    return current_app.config['BASE_URL'] + path