import secrets

from application.methods import get_object_type_by_code
from application.models import Invitation, ObjectType, Object, db
from application.helpers.decorators import transaction


def get_invitations():
    return Invitation.query.filter_by(user_id=None).all()


@transaction
def create_invitations_for(type_code, role):
    existing_invites = Invitation.query.all()
    invited_object_ids = {inv.object_id for inv in existing_invites if inv.object_id}

    # Определяем ObjectType для студентов
    type = get_object_type_by_code(type_code)

    # Находим объекты, которым нужно добавить приглашения
    uninvited = (Object.query
                          .filter_by(type_id=type.id)
                          .filter(~Object.id.in_(invited_object_ids))
                          .all())

    # Создаем приглашения для каждого студента без существующего инвайта
    invites = []
    for object in uninvited:
        invite_key = secrets.token_urlsafe(16)

        new_invite = Invitation(
            object_id=object.id,
            key=invite_key,
            role=role
        )
        db.session.add(new_invite)
        invites.append(new_invite)

    return invites
