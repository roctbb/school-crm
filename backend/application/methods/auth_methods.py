import secrets

from flask_jwt_extended import create_access_token
from application.models import db, User, Invitation
from application.infrastructure import bcrypt
from application.helpers.decorators import transaction
from application.helpers.exceptions import LogicException


def find_invitation(invite_key):
    return Invitation.query.filter_by(key=invite_key, used_at=None).first()


@transaction
def register_user(data):
    # Проверить наличие приглашения
    invite = find_invitation(data['invite'])
    if not invite:
        raise LogicException("Недействительный или использованный инвайт", 401)

    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    # Создать нового пользователя
    new_user = User(
        name=data['name'],
        email=data['email'],
        password=hashed_password,
        role=invite.role
    )
    db.session.add(new_user)

    invite.used_at = db.func.now()
    invite.used_by = new_user
    db.session.add(invite)

    if invite.object:
        invite.object.owners.append(new_user)

    return new_user

def get_access_token(user):
    return create_access_token(identity=str(user.id))

def login_user(data):
    user = User.query.filter_by(email=data['email']).first()
    if not user:
        raise LogicException("Пользователь с указанным email не найден", 401)

    if not bcrypt.check_password_hash(user.password, data['password']):
        raise LogicException("Неверный пароль", 401)

    return get_access_token(user)


def get_user_by_email(email):
    user = User.query.filter_by(email=email).first()
    if not user:
        raise LogicException("Пользователь с указанным email не найден", 401)

    return user

def get_user_by_reset_token(reset_token):
    user = User.query.filter_by(reset_token=reset_token).first()
    if not user:
        raise LogicException("Неверный ключ восстановления", 401)

    return user


@transaction
def set_reset_token(user):
    user.reset_token = secrets.token_urlsafe(64)
    return user


@transaction
def reset_password(user, password):
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    user.password = hashed_password
    user.reset_token = None
    return user
