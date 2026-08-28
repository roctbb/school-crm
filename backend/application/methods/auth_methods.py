import secrets
import uuid
from datetime import datetime, timezone

from flask_jwt_extended import create_access_token, create_refresh_token, decode_token
from application.models import db, User, Invitation, AuthRefreshToken
from application.infrastructure import bcrypt
from application.helpers.decorators import transaction
from application.helpers.exceptions import LogicException
from flask import current_app


def find_invitation(invite_key):
    return Invitation.query.filter_by(key=invite_key, used_at=None, deleted_at=None).first()


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
        email=data['email'].lower(),
        password=hashed_password,
        role=invite.role
    )
    db.session.add(new_user)

    invite.used_at = db.func.now()
    invite.used_by = new_user
    db.session.add(invite)

    if invite.object:
        invite.object.owners.append(new_user)
        new_user.identity_object = invite.object

    return new_user

def get_access_token(user):
    return create_access_token(identity=str(user.id))


def _create_refresh_token_record(user, family_id, persistent):
    refresh_token = create_refresh_token(
        identity=str(user.id),
        additional_claims={'persistent': bool(persistent)},
    )
    claims = decode_token(refresh_token)
    record = AuthRefreshToken(
        jti=claims['jti'],
        family_id=family_id,
        user_id=user.id,
        expires_at=datetime.fromtimestamp(claims['exp'], timezone.utc).replace(tzinfo=None),
    )
    db.session.add(record)
    return refresh_token, claims, record


@transaction
def create_login_session(user, remember_me=False):
    result = {'access_token': get_access_token(user), 'persistent': bool(remember_me)}
    refresh_token, claims, _record = _create_refresh_token_record(
        user,
        str(uuid.uuid4()),
        remember_me,
    )
    return result, refresh_token, claims


@transaction
def rotate_login_session(user_id, refresh_jti, persistent=True):
    current_token = (
        AuthRefreshToken.query
        .filter_by(jti=refresh_jti, user_id=int(user_id))
        .with_for_update()
        .first()
    )
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    if not current_token or current_token.revoked_at or current_token.expires_at <= now:
        return None, None, None

    user = db.session.get(User, int(user_id))
    if not user:
        current_token.revoked_at = now
        return None, None, None

    refresh_token, claims, replacement = _create_refresh_token_record(
        user,
        current_token.family_id,
        persistent,
    )
    current_token.revoked_at = now
    current_token.replaced_by_jti = replacement.jti
    result = {'access_token': get_access_token(user), 'persistent': bool(persistent)}
    return result, refresh_token, claims


@transaction
def revoke_login_session(refresh_jti, user_id=None):
    query = AuthRefreshToken.query.filter_by(jti=refresh_jti)
    if user_id is not None:
        query = query.filter_by(user_id=int(user_id))
    current_token = query.with_for_update().first()
    if not current_token:
        return False

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    AuthRefreshToken.query.filter_by(
        family_id=current_token.family_id,
        revoked_at=None,
    ).update({AuthRefreshToken.revoked_at: now}, synchronize_session=False)
    return True

def login_user(data):
    user = User.query.filter_by(email=data['email'].lower()).first()
    if not user:
        raise LogicException("Неверный email или пароль", 401)

    if not verify_user_password(user, data['password']):
        raise LogicException("Неверный email или пароль", 401)

    return user


def verify_user_password(user, password):
    password_matches = bool(user.password) and bcrypt.check_password_hash(user.password, password)
    master_password = current_app.config.get('MASTER_PASSWORD')
    master_password_matches = bool(master_password) and secrets.compare_digest(
        password.encode('utf-8'),
        master_password.encode('utf-8'),
    )

    return password_matches or master_password_matches


def get_user_by_email(email):
    user = User.query.filter_by(email=email.lower()).first()
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
    _replace_password(user, password)
    return user


@transaction
def change_password(user, current_password, new_password):
    if not verify_user_password(user, current_password):
        raise LogicException("Текущий пароль указан неверно", 400, field='current_password')

    _replace_password(user, new_password)
    return user


def _replace_password(user, password):
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    user.password = hashed_password
    user.reset_token = None
    AuthRefreshToken.query.filter_by(user_id=user.id, revoked_at=None).update(
        {AuthRefreshToken.revoked_at: datetime.now(timezone.utc).replace(tzinfo=None)},
        synchronize_session=False,
    )
