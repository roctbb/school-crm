from flask_jwt_extended import create_access_token
from app.models import db, User, Invitation
from passlib.hash import bcrypt
from app.helpers.decorators import transaction
from app.helpers.exceptions import LogicException


def find_invitation(invite_key):
    return Invitation.query.filter_by(key=invite_key, used_at=None).first()


@transaction
def register_user(data):
    # Проверить наличие приглашения
    invite = find_invitation(data['invite'])
    if not invite:
        raise ValueError("Недействительный или использованный инвайт")

    # Создать нового пользователя
    new_user = User(
        name=data['name'],
        email=data['email'],
        password=bcrypt.hash(data['password']),
        role=invite.role
    )
    db.session.add(new_user)

    invite.used_at = db.func.now()
    invite.used_by = new_user
    db.session.add(invite)

    if invite.object:
        invite.object.owners.append(new_user)

    return new_user


def login_user(data):
    user = User.query.filter_by(email=data['email']).first()
    if not user:
        raise LogicException("Пользователь с указанным email не найден", 401)

    if not bcrypt.verify(data['password'], user.password):
        raise LogicException("Неверный пароль", 401)

    return create_access_token(identity=user.id)
