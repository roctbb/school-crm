from copy import deepcopy

from application.helpers.decorators import transaction
from application.helpers.exceptions import LogicException
from application.models import FormCategory, Object, ObjectType, ObjectTypeRevision, db


def get_object_type_by_id(object_type_id):
    object_type = db.session.get(ObjectType, object_type_id)
    if not object_type:
        raise LogicException("Тип объекта не найден", 404)
    return object_type


def get_object_type_usage(object_type):
    objects = Object.query.filter_by(type_id=object_type.id, deleted_at=None).all()
    attribute_usage = {}
    for obj in objects:
        for code in (obj.attributes or {}).keys():
            attribute_usage[code] = attribute_usage.get(code, 0) + 1

    configured_codes = {
        attribute.get('code') for attribute in (object_type.available_attributes or []) if attribute.get('code')
    }
    orphan_attributes = {
        code: count for code, count in attribute_usage.items() if code not in configured_codes
    }
    return {
        'object_count': len(objects),
        'attribute_usage': attribute_usage,
        'orphan_attributes': orphan_attributes,
        'revision_count': ObjectTypeRevision.query.filter_by(object_type_id=object_type.id).count(),
    }


def _get_categories(category_ids):
    categories = FormCategory.query.filter(
        FormCategory.id.in_(category_ids),
        FormCategory.deleted_at.is_(None),
    ).all() if category_ids else []
    if len(categories) != len(category_ids):
        raise LogicException("Некоторые категории форм не найдены.", 422, field='form_category_ids')
    return categories


def _validate_child_types(type_code, params):
    possible_children = params.get('possible_children', [])
    known_codes = {row.code for row in ObjectType.query.all()} | {type_code}
    missing_codes = set(possible_children) - known_codes
    if missing_codes:
        raise LogicException(
            f"Неизвестные дочерние типы: {', '.join(sorted(missing_codes))}.",
            422,
            field='possible_children',
        )


def _snapshot_object_type(object_type):
    return {
        'name': object_type.name,
        'code': object_type.code,
        'available_attributes': deepcopy(object_type.available_attributes or []),
        'available_params': deepcopy(object_type.available_params or []),
        'params': deepcopy(object_type.params or {}),
        'form_category_ids': [category.id for category in object_type.form_categories],
    }


@transaction
def create_object_type(user, data):
    if ObjectType.query.filter_by(code=data['code']).first():
        raise LogicException("Тип с таким кодом уже существует.", 409, field='code')

    _validate_child_types(data['code'], data.get('params', {}))
    object_type = ObjectType(
        name=data['name'].strip(),
        code=data['code'],
        available_attributes=deepcopy(data.get('available_attributes', [])),
        available_params=[],
        params=deepcopy(data.get('params', {})),
        form_categories=_get_categories(data.get('form_category_ids', [])),
    )
    db.session.add(object_type)
    return object_type


@transaction
def update_object_type(user, object_type, data):
    if data['code'] != object_type.code:
        raise LogicException("Код существующего типа изменять нельзя.", 409, field='code')

    _validate_child_types(object_type.code, data.get('params', {}))
    new_attributes = deepcopy(data.get('available_attributes', []))
    new_codes = {attribute['code'] for attribute in new_attributes}
    current_attributes = {
        attribute.get('code'): attribute
        for attribute in (object_type.available_attributes or [])
        if attribute.get('code')
    }
    current_codes = set(current_attributes)
    removed_codes = current_codes - new_codes
    usage = get_object_type_usage(object_type)['attribute_usage']
    used_removed_codes = {code: usage[code] for code in removed_codes if usage.get(code)}
    if used_removed_codes:
        details = ', '.join(f"{code} ({count})" for code, count in sorted(used_removed_codes.items()))
        raise LogicException(
            f"Нельзя удалить используемые атрибуты: {details}.",
            409,
            field='available_attributes',
        )

    new_attributes_by_code = {attribute['code']: attribute for attribute in new_attributes}
    changed_used_types = [
        code for code, count in usage.items()
        if count
        and code in current_attributes
        and code in new_attributes_by_code
        and current_attributes[code].get('type') != new_attributes_by_code[code].get('type')
    ]
    if changed_used_types:
        raise LogicException(
            f"Нельзя менять тип используемых атрибутов: {', '.join(sorted(changed_used_types))}.",
            409,
            field='available_attributes',
        )

    db.session.add(ObjectTypeRevision(
        object_type_id=object_type.id,
        editor_id=user.id,
        snapshot=_snapshot_object_type(object_type),
    ))
    object_type.name = data['name'].strip()
    object_type.available_attributes = new_attributes
    object_type.params = deepcopy(data.get('params', {}))
    object_type.form_categories = _get_categories(data.get('form_category_ids', []))
    return object_type


def get_object_type_revisions(object_type):
    return ObjectTypeRevision.query.filter_by(object_type_id=object_type.id).order_by(
        ObjectTypeRevision.created_at.desc()
    ).limit(50).all()
