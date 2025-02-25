from flask import Blueprint, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models.user import User
from app.methods import register_user
from app.schemas.auth import SignupSchema, LoginSchema, UserResponseSchema
from app.decorators import validate_schema, requires_user
from datetime import timedelta

auth_blueprint = Blueprint('auth', __name__)

signup_schema = SignupSchema()
login_schema = LoginSchema()
user_response_schema = UserResponseSchema()


@auth_blueprint.route('/signup', methods=['POST'])
@validate_schema(signup_schema)
def signup(validated_data):
    """Маршрут для регистрации пользователя."""
    user = register_user(validated_data)
    token = create_access_token(identity=user.id, expires_delta=timedelta(hours=12))

    return jsonify({
        'message': 'Пользователь успешно зарегистрирован',
        'access_token': token
    }), 201


# Вход пользователя (создание токена)
@auth_blueprint.route('/login', methods=['POST'])
@validate_schema(login_schema)  # Применяем декоратор
def login(validated_data):
    # Поиск пользователя по email
    user = User.query.filter_by(email=validated_data['email']).first()

    # Проверка пароля
    if not user or not check_password_hash(user.password, validated_data['password']):
        return jsonify({'error': 'Неверный email или пароль'}), 401

    # Создание токена
    access_token = create_access_token(
        identity=user.id, expires_delta=timedelta(hours=1)
    )
    return jsonify({'access_token': access_token}), 200


# Получение информации о текущем пользователе
@auth_blueprint.route('/me', methods=['GET'])
@requires_user
def get_current_user(user):
    return jsonify(user_response_schema.dump(user))
