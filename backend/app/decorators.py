from functools import wraps
from flask import request, jsonify
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User


# Декоратор для валидации данных
def validate_schema(schema):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Валидация данных с использованием переданной схемы
                validated_data = schema.load(request.json)
            except ValidationError as err:
                return jsonify({"errors": err.messages}), 400

            # Передаем валидированные данные в обработчик в виде аргумента
            return func(validated_data, *args, **kwargs)

        return wrapper

    return decorator


def requires_user(required_role=None):
    def decorator(func):
        @wraps(func)
        @jwt_required()  # Проверка токена
        def wrapper(*args, **kwargs):
            current_user_id = get_jwt_identity()
            if not current_user_id:
                return jsonify({'error': 'Неавторизованный доступ'}), 401

            # Получение пользователя из базы данных
            user = User.query.get(current_user_id)
            if not user:
                return jsonify({'error': 'Пользователь не найден'}), 404

            # Проверка роли пользователя
            if required_role and required_role not in [role.name for role in user.roles]:
                return jsonify({'error': 'Доступ запрещен'}), 403

            # Передача объекта пользователя в функцию
            return func(user, *args, **kwargs)

        return wrapper

    return decorator

