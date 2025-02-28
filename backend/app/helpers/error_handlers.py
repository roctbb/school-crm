from flask import jsonify
from werkzeug.exceptions import HTTPException

from .exceptions import LogicException


def setup_handlers(app):
    @app.errorhandler(LogicException)
    def handle_exception(e):
        response = {"message": e.message}
        if e.field:
            response["field"] = e.field
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
