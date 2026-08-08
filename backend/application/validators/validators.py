from validate_email_address import validate_email
import re

from .common import *
from application.models import ObjectType, Form, Object


OBJECT_ATTRIBUTE_TYPES = {'string', 'text', 'number', 'date', 'file', 'link', 'select', 'checkboxes'}
OBJECT_ATTRIBUTE_KEYS = {
    'name', 'code', 'type', 'description', 'options', 'required', 'display',
    'show_off', 'group', 'is_locked', 'is_private', 'is_hidden', 'is_secret',
    'keep_history',
}
OBJECT_TYPE_PARAM_KEYS = {
    'index', 'possible_children', 'can_create', 'can_delete', 'can_fill',
    'is_hidden', 'comments_hidden', 'widgets', 'details_widgets', 'edit_description'
}
OBJECT_TYPE_WIDGETS = {'active_events', 'birthdays', 'calendar', 'portfolio_progress'}
ROLE_CODES = {'student', 'teacher', 'admin'}
CODE_PATTERN = re.compile(r'^[a-z][a-z0-9_-]{1,99}$')


def validate_object(data):
    should_have(data, 'name', min_length=1, max_length=1024)

    # Check "params" and "attributes" are JSON and optional
    if not isinstance(data.get('params', {}), dict):
        raise LogicException("Поле params должно быть объектом JSON.", 422)
    if not isinstance(data.get('attributes', {}), dict):
        raise LogicException("Поле attributes должно быть объектом JSON.", 422)

    return data


def validate_object_type(data):
    if not isinstance(data, dict):
        raise LogicException("Описание типа должно быть объектом JSON.", 422)

    should_have(data, 'name', min_length=1, max_length=100)
    should_have(data, 'code', min_length=2, max_length=100)
    if not CODE_PATTERN.fullmatch(data['code']) or data['code'] == 'types':
        raise LogicException(
            "Код типа должен начинаться с латинской буквы и содержать только a-z, 0-9, _ или -.",
            422,
            field='code',
        )

    attributes = data.get('available_attributes', [])
    if not isinstance(attributes, list):
        raise LogicException("Поле available_attributes должно быть списком.", 422)

    attribute_codes = set()
    boolean_keys = {
        'required', 'display', 'show_off', 'group', 'is_locked',
        'is_private', 'is_hidden', 'is_secret', 'keep_history'
    }
    for index, attribute in enumerate(attributes):
        if not isinstance(attribute, dict):
            raise LogicException(f"Атрибут #{index + 1} должен быть объектом JSON.", 422)

        unknown_keys = set(attribute) - OBJECT_ATTRIBUTE_KEYS
        if unknown_keys:
            raise LogicException(
                f"Неизвестные поля атрибута #{index + 1}: {', '.join(sorted(unknown_keys))}.",
                422,
            )

        for key in ('name', 'code', 'type'):
            if not isinstance(attribute.get(key), str) or not attribute[key].strip():
                raise LogicException(f"У атрибута #{index + 1} отсутствует поле {key}.", 422)

        attribute['name'] = attribute['name'].strip()
        attribute['code'] = attribute['code'].strip()
        if not CODE_PATTERN.fullmatch(attribute['code']):
            raise LogicException(f"Некорректный код атрибута {attribute['code']}.", 422, field='code')
        if attribute['code'] in attribute_codes:
            raise LogicException(f"Код атрибута {attribute['code']} повторяется.", 422, field='code')
        attribute_codes.add(attribute['code'])

        if attribute['type'] not in OBJECT_ATTRIBUTE_TYPES:
            raise LogicException(f"Неизвестный тип атрибута {attribute['type']}.", 422, field='type')
        if attribute.get('keep_history') and attribute['type'] != 'file':
            raise LogicException(
                f"Историю можно включить только для файлового атрибута {attribute['code']}.",
                422,
                field='keep_history',
            )

        for key in boolean_keys:
            if key in attribute and not isinstance(attribute[key], bool):
                raise LogicException(f"Поле {key} атрибута {attribute['code']} должно быть boolean.", 422)

        options = attribute.get('options', [])
        if not isinstance(options, list) or not all(isinstance(option, str) for option in options):
            raise LogicException(f"Опции атрибута {attribute['code']} должны быть списком строк.", 422)
        attribute['options'] = list(dict.fromkeys(option.strip() for option in options if option.strip()))

        description = attribute.get('description', '')
        if not isinstance(description, str) or len(description) > 2000:
            raise LogicException(f"Некорректное описание атрибута {attribute['code']}.", 422)

    params = data.get('params', {})
    if not isinstance(params, dict):
        raise LogicException("Поле params должно быть объектом JSON.", 422)
    unknown_params = set(params) - OBJECT_TYPE_PARAM_KEYS
    if unknown_params:
        raise LogicException(f"Неизвестные параметры типа: {', '.join(sorted(unknown_params))}.", 422)

    if 'index' in params and (not isinstance(params['index'], int) or params['index'] < 0):
        raise LogicException("Параметр index должен быть неотрицательным целым числом.", 422)
    for key in ('is_hidden', 'comments_hidden'):
        if key in params and not isinstance(params[key], bool):
            raise LogicException(f"Параметр {key} должен быть boolean.", 422)
    for key in ('possible_children', 'can_create', 'can_delete', 'can_fill', 'widgets', 'details_widgets'):
        value = params.get(key, [])
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            raise LogicException(f"Параметр {key} должен быть списком строк.", 422)
        params[key] = list(dict.fromkeys(value))
    for key in ('can_create', 'can_delete', 'can_fill'):
        invalid_roles = set(params.get(key, [])) - ROLE_CODES
        if invalid_roles:
            raise LogicException(f"Неизвестные роли в {key}: {', '.join(sorted(invalid_roles))}.", 422)
    for key in ('widgets', 'details_widgets'):
        invalid_widgets = set(params.get(key, [])) - OBJECT_TYPE_WIDGETS
        if invalid_widgets:
            raise LogicException(f"Неизвестные виджеты в {key}: {', '.join(sorted(invalid_widgets))}.", 422)
    if 'edit_description' in params and (
            not isinstance(params['edit_description'], str) or len(params['edit_description']) > 4000):
        raise LogicException("Параметр edit_description должен быть строкой до 4000 символов.", 422)

    category_ids = data.get('form_category_ids', [])
    if not isinstance(category_ids, list) or not all(isinstance(category_id, int) for category_id in category_ids):
        raise LogicException("Поле form_category_ids должно быть списком ID.", 422)
    data['form_category_ids'] = list(dict.fromkeys(category_ids))

    return data


def validate_form(data):
    should_have(data, 'name', min_length=1, max_length=100)

    # Ensure "available_params" and "fields" are JSON lists
    if not isinstance(data.get('available_params', []), list):
        raise LogicException("Поле available_params должно быть списком.", 422)
    if not isinstance(data.get('fields', []), list):
        raise LogicException("Поле fields должно быть списком.", 422)

    return data


def validate_submission(data):
    # params, answers должны быть словарями
    if not isinstance(data.get('params', {}), dict):
        raise LogicException("Поле params должно быть объектом JSON.", 422)
    if not isinstance(data.get('fields', []), list):
        raise LogicException("Поле fields должно быть объектом JSON.", 422)

    return data


def validate_invitation(data):
    should_have(data, 'email', min_length=1, max_length=100)
    should_have(data, 'role', min_length=1, max_length=100)

    if not validate_email(data.get('email')):
        raise ValueError("Поле email некорректно.")

    if data.get('object_id') is not None:
        should_exist(data, 'object_id', Object, 'id')

    return data


def validate_comment(data):
    should_have(data, 'text', min_length=1, max_length=1000)

    return data


def validate_object_children(data):
    children = data.get('children', [])
    if not isinstance(children, list):
        raise LogicException("Поле children должно быть списком IDs.", 422)
    if not all(isinstance(child_id, int) for child_id in children):
        raise LogicException("Каждый элемент в поле children должен быть числом.", 422)
    return data


def validate_invitations_request(data):
    should_have(data, 'role', options=['student', 'teacher', 'admin'])

    return data
