import secrets

from application.helpers.decorators import transaction
from application.helpers.exceptions import LogicException
from application.models import db, User


def get_users():
    return User.query.order_by(User.name.asc(), User.email.asc()).all()


def get_user_by_id(user_id):
    user = db.session.get(User, user_id)
    if not user:
        raise LogicException('Пользователь не найден', 404)
    return user


@transaction
def generate_user_reset_token(user):
    # Каждый выпуск ссылки делает предыдущую ссылку недействительной.
    user.reset_token = secrets.token_urlsafe(64)
    return user
