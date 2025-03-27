from flask import Flask, jsonify
from flask_limiter import Limiter
from flask_mail import Mail
from flask_migrate import Migrate
from werkzeug.exceptions import HTTPException

from application.helpers.error_handlers import setup_handlers
from application.infrastructure import db, jwt, bcrypt, mail, limiter, celery
from application.models import *
from application.config import get_config
from application.helpers.exceptions import LogicException
from application.blueprints import api_blueprint
from flask_cors import CORS


def create_app(config_name=None):
    app = Flask(__name__)

    # Загрузка конфигурации из config.py
    app.config.from_object(get_config(config_name))

    if app.config['DEBUG_QUERIES']:
        import logging

        logging.basicConfig()
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

    setup_handlers(app)
    jwt.init_app(app)
    bcrypt.init_app(app)

    # Инициализация базы данных и инструментов миграции
    db.init_app(app)
    Migrate(app, db)

    # Настройка CORS
    CORS(app)

    app.register_blueprint(api_blueprint)
    mail.init_app(app)

    celery.conf.update(app.config)
    celery.conf.broker_url = app.config['CELERY_BROKER_URL']
    celery.conf.result_backend = app.config['CELERY_BACKEND']

    limiter.init_app(app)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask

    return app, celery
