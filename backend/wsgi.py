from application import create_app

app, celery = create_app('production')
