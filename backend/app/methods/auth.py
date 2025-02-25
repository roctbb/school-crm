from werkzeug.security import generate_password_hash
from datetime import timedelta
from flask_jwt_extended import create_access_token

from app import LogicException
from app.models.user import User, Role
from app.models.entity import Entity
from app.database import db


def register_user(validated_data):
    """Регистрация нового пользователя."""
    # Хеширование пароля
    hashed_password = generate_password_hash(validated_data['password'])

    # Привязка к сущности или ролям через invite_code
    entities = []
    roles = []
    if 'invite_code' in validated_data and validated_data['invite_code']:
        entities = Entity.query.filter_by(invite_code=validated_data['invite_code']).all()

        if entities:
            roles = Role.query.filter(Role.invite_code is None).all()
        else:
            roles = Role.query.filter_by(invite_code=validated_data['invite_code']).all()

        if not entities and not roles:
            raise LogicException('Неверный инвайт', 400)

    # Создание нового пользователя
    new_user = User(
        name=validated_data['name'],
        email=validated_data['email'],
        password=hashed_password,
    )
    db.session.add(new_user)

    # Если нашлись роли, добавляем их пользователю
    if roles:
        new_user.roles.extend(roles)  # Добавляем список ролей пользователю
    if entities:
        new_user.entities.extend(entities)

    db.session.commit()

    return new_user
