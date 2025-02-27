from flask import Flask, jsonify
from flask_migrate import Migrate
from werkzeug.exceptions import HTTPException
from app.infrastructure import db, jwt, bcrypt
from app.models import *
from app.config import get_config
from app.helpers.exceptions import LogicException
from app.blueprints import api_blueprint
from flask_cors import CORS


def create_app(config_name=None):
    app = Flask(__name__)

    @app.errorhandler(LogicException)
    def handle_exception(e):
        response = {"message": e.message}
        return jsonify(response), e.code

    # Обработчик стандартных HTTP ошибок (например, 404, 405)
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        if e.code == 404:
            response = {"message": "Маршрут не найден"}
        else:
            response = {"message": e.description}
        return jsonify(response), e.code

    # Обработчик для всех остальных необработанных исключений
    @app.errorhandler(Exception)
    def handle_generic_exception(e):
        print(e)  # Вывод в консоль для разработки
        response = {"message": "Произошла ошибка"}
        return jsonify(response), 500

    # Загрузка конфигурации из config.py
    app.config.from_object(get_config(config_name))

    jwt.init_app(app)
    bcrypt.init_app(app)

    # Инициализация базы данных и инструментов миграции
    db.init_app(app)
    migrate = Migrate(app, db)

    # Настройка CORS
    CORS(app)

    app.register_blueprint(api_blueprint)

    return app
