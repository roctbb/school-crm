from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.methods import register_user, get_user_by_credentials
from app.decorators import validate_request, requires_user
from app.presenters import present_user
from app.validators import validate_signup, validate_login
from datetime import timedelta

auth_blueprint = Blueprint('auth', __name__)


@auth_blueprint.route('/signup', methods=['POST'])
@validate_request(validate_signup)
def signup(user_description):
    """Маршрут для регистрации пользователя."""
    user = register_user(user_description)
    token = create_access_token(identity=user.id, expires_delta=timedelta(hours=12))

    return jsonify({
        'message': 'Пользователь успешно зарегистрирован',
        'access_token': token
    }), 201


# Вход пользователя (создание токена)
@auth_blueprint.route('/login', methods=['POST'])
@validate_request(validate_login)  # Применяем декоратор
def login(creadentials):
    user = get_user_by_credentials(creadentials)
    access_token = create_access_token(
        identity=user.id, expires_delta=timedelta(hours=1)
    )
    return jsonify({'access_token': access_token}), 200


# Получение информации о текущем пользователе
@auth_blueprint.route('/me', methods=['GET'])
@requires_user
def get_current_user(user):
    return jsonify(present_user(user))
