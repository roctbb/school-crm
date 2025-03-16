from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User
from app.infrastructure import db


# Декоратор для валидации данных
def validate_request_with(validator):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(validator(request.json), *args, **kwargs)

        return wrapper

    return decorator


def requires_user(func):
    @wraps(func)
    @jwt_required()  # Проверка токена
    def wrapper(*args, **kwargs):
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return jsonify({'error': 'Неавторизованный доступ'}), 401

        # Получение пользователя из базы данных
        user = db.session.get(User, current_user_id)
        if not user:
            return jsonify({'error': 'Пользователь не найден'}), 401

        # Передача объекта пользователя в функцию
        return func(user, *args, **kwargs)

    return wrapper

def requires_roles(roles):
    """
    Декоратор для проверки роли пользователя. Принимает список ролей.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(user, *args, **kwargs):
            if user.role not in roles:
                return jsonify({'error': 'Недостаточно прав'}), 403
            return func(user, *args, **kwargs)

        return wrapper

    return decorator

def transaction(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            db.session.commit()
            return result
        except Exception as e:
            db.session.rollback()
            raise e

    return wrapper
