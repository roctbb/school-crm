import secrets

from application.methods import get_object_type_by_code
from application.models import Invitation, Object, db
from application.helpers.decorators import transaction
from application.helpers.exceptions import LogicException


INVITATION_ROLES_BY_OBJECT_TYPE = {
    'student': 'student',
    'students': 'student',
}


def get_invitations():
    return Invitation.query.filter_by(user_id=None, used_at=None, deleted_at=None).order_by(
        Invitation.created_at.desc(), Invitation.id.desc()
    ).all()


def get_unused_invitation_by_id(invitation_id):
    invitation = Invitation.query.filter_by(
        id=invitation_id,
        user_id=None,
        used_at=None,
        deleted_at=None,
    ).first()
    if not invitation:
        raise LogicException("Инвайт не найден", 404)
    return invitation


@transaction
def create_invitation_for_object(user, object_id):
    locked_object_id = (
        db.session.query(Object.id)
        .filter_by(id=object_id, deleted_at=None)
        .with_for_update()
        .scalar()
    )
    if not locked_object_id:
        raise LogicException("Объект не найден", 404)
    obj = db.session.get(Object, locked_object_id)

    role = INVITATION_ROLES_BY_OBJECT_TYPE.get(obj.type.code)
    if not role:
        raise LogicException("Инвайт можно создать только для ученика", 422)

    existing_invitation = (
        Invitation.query
        .filter_by(object_id=obj.id, deleted_at=None)
        .order_by(Invitation.created_at.desc(), Invitation.id.desc())
        .first()
    )
    has_linked_user = bool(
        obj.identity_user
        or (
            existing_invitation
            and (existing_invitation.used_at or existing_invitation.user_id)
        )
    )
    if has_linked_user:
        raise LogicException("К ученику уже привязан пользователь", 409)
    if existing_invitation:
        raise LogicException("У ученика уже есть активный инвайт", 409)

    invitation = Invitation(
        object_id=obj.id,
        key=secrets.token_urlsafe(16),
        role=role,
        creator_id=user.id,
    )
    db.session.add(invitation)
    return invitation


@transaction
def delete_invitation(user, invitation):
    invitation.deleted_at = db.func.now()
    invitation.deleter_id = user.id


@transaction
def delete_all_unused_invitations(user):
    invitations = Invitation.query.filter_by(user_id=None, used_at=None, deleted_at=None).all()
    for invitation in invitations:
        invitation.deleted_at = db.func.now()
        invitation.deleter_id = user.id
    return len(invitations)


@transaction
def create_invitations_for(type_code, role):
    existing_invites = Invitation.query.filter_by(deleted_at=None).all()
    invited_object_ids = {inv.object_id for inv in existing_invites if inv.object_id}

    # Определяем ObjectType для студентов
    type = get_object_type_by_code(type_code)

    # Находим объекты, которым нужно добавить приглашения
    uninvited = (Object.query
                          .filter_by(type_id=type.id)
                          .filter(Object.deleted_at.is_(None))
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
