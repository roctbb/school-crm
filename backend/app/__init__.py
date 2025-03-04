from flask import Flask, jsonify
from flask_migrate import Migrate
from werkzeug.exceptions import HTTPException

from app.helpers.error_handlers import setup_handlers
from app.infrastructure import db, jwt, bcrypt
from app.models import *
from app.config import get_config
from app.helpers.exceptions import LogicException
from app.blueprints import api_blueprint
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
    migrate = Migrate(app, db)

    # Настройка CORS
    CORS(app)

    app.register_blueprint(api_blueprint)

    return app
