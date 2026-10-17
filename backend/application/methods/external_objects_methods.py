from sqlalchemy.orm import joinedload, lazyload, load_only
from flask import url_for

from application.helpers.exceptions import LogicException
from application.models import Object, ObjectType
from application.methods.files_methods import get_object_avatar_file
from application.oidc import get_oidc_identity_grade, get_oidc_issuer


def _integer_parameter(args, name, default, minimum, maximum):
    value = args.get(name, str(default))
    if not value.isascii() or not value.isdigit() or len(value) > 10:
        raise LogicException(f'Параметр {name} должен быть целым числом.', 422, field=name)
    value = int(value)
    if not minimum <= value <= maximum:
        raise LogicException(
            f'Параметр {name} должен быть от {minimum} до {maximum}.', 422, field=name,
        )
    return value


def _get_external_object_type(client, type_code):
    if type_code not in (client.allowed_object_types or []):
        raise LogicException('Клиенту запрещено читать этот тип объектов.', 403)
    object_type = ObjectType.query.options(lazyload('*')).filter_by(code=type_code).first()
    if not object_type or (object_type.params or {}).get('is_hidden'):
        raise LogicException('Тип объектов не найден.', 404)
    return object_type


def _visible_objects_query():
    # Do not load accounts, invitations, comments or other private relationships.
    return Object.query.options(
        load_only(Object.id, Object.sso_subject, Object.name, Object.attributes),
        joinedload(Object.type).load_only(ObjectType.code, ObjectType.available_attributes),
        lazyload('*'),
    ).filter(Object.deleted_at.is_(None), Object.is_hidden.is_(False))


def get_external_object_avatar(client, type_code, subject):
    object_type = _get_external_object_type(client, type_code)
    if 'avatar' not in (client.allowed_scopes or []):
        raise LogicException('Клиенту запрещено получать аватары.', 403)
    obj = _visible_objects_query().filter_by(
        type_id=object_type.id, sso_subject=subject,
    ).first()
    uploaded_file = get_object_avatar_file(obj)
    if not uploaded_file:
        raise LogicException('Аватар не найден.', 404)
    return uploaded_file


def get_external_objects(client, type_code, args):
    object_type = _get_external_object_type(client, type_code)
    limit = _integer_parameter(args, 'limit', 100, 1, 200)
    after_id = _integer_parameter(args, 'after_id', 0, 0, 2147483647)
    search = args.get('q', '').strip()
    if len(search) > 200:
        raise LogicException('Поисковый запрос должен быть не длиннее 200 символов.', 422, field='q')

    query = _visible_objects_query().filter(
        Object.type_id == object_type.id,
        Object.id > after_id,
    )
    if search:
        # The database's C locale does not fold Cyrillic case. PostgreSQL 16's
        # language-neutral ICU collation makes name search work in every locale.
        query = query.filter(Object.name.collate('und-x-icu').icontains(search, autoescape=True))
    objects = query.order_by(Object.id).limit(limit + 1).all()
    has_more = len(objects) > limit
    objects = objects[:limit]
    items = []
    for obj in objects:
        picture = None
        if 'avatar' in (client.allowed_scopes or []) and get_object_avatar_file(obj):
            picture = get_oidc_issuer() + url_for(
                'api.external_objects.external_object_avatar',
                type_code=type_code, subject=obj.sso_subject,
            )
        items.append({
            'sub': obj.sso_subject,
            'object_id': obj.id,
            'object_type': type_code,
            'name': obj.name,
            'grade': get_oidc_identity_grade(obj),
            'picture': picture,
        })
    return {
        'items': items,
        'next_after_id': objects[-1].id if has_more else None,
    }
