from validate_email_address import validate_email
import re
from urllib.parse import urlsplit

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
FORM_FIELD_TYPES = {
    'number', 'string', 'text', 'date', 'datetime', 'select', 'file',
    'checkboxes', 'checkbox',
}
CODE_PATTERN = re.compile(r'^[a-z][a-z0-9_-]{1,99}$')
OAUTH_CLIENT_ID_PATTERN = re.compile(r'^[a-z][a-z0-9._-]{2,119}$')
OAUTH_SCOPES = {'openid', 'profile', 'email', 'roles', 'offline_access'}


def validate_object(data):
    should_have(data, 'name', min_length=1, max_length=1024)

    # Check "params" and "attributes" are JSON and optional
    if not isinstance(data.get('params', {}), dict):
        raise LogicException("Поле params должно быть объектом JSON.", 422)
    if not isinstance(data.get('attributes', {}), dict):
        raise LogicException("Поле attributes должно быть объектом JSON.", 422)

    return data


def _validate_oauth_uri(uri, field):
    if not isinstance(uri, str) or not uri or len(uri) > 2000:
        raise LogicException(f"Некорректный URI в поле {field}.", 422, field=field)
    parsed = urlsplit(uri)
    is_local_http = parsed.scheme == 'http' and parsed.hostname in {'localhost', '127.0.0.1'}
    if parsed.scheme != 'https' and not is_local_http:
        raise LogicException(
            f"URI в поле {field} должен использовать HTTPS; HTTP разрешён только для localhost.",
            422,
            field=field,
        )
    if not parsed.netloc or parsed.username or parsed.password or parsed.fragment:
        raise LogicException(f"Некорректный URI в поле {field}.", 422, field=field)
    return uri


def validate_oauth_client(data):
    if not isinstance(data, dict):
        raise LogicException("Описание OIDC-клиента должно быть объектом JSON.", 422)

    should_have(data, 'name', min_length=1, max_length=120)
    should_have(data, 'client_id', min_length=3, max_length=120)
    if not OAUTH_CLIENT_ID_PATTERN.fullmatch(data['client_id']):
        raise LogicException(
            "client_id должен начинаться с латинской буквы и содержать только a-z, 0-9, ., _ или -.",
            422,
            field='client_id',
        )

    description = data.get('description', '')
    if not isinstance(description, str) or len(description) > 4000:
        raise LogicException("Описание должно быть строкой до 4000 символов.", 422, field='description')

    for field in ('redirect_uris', 'post_logout_redirect_uris'):
        values = data.get(field, [])
        if not isinstance(values, list) or not all(isinstance(value, str) for value in values):
            raise LogicException(f"Поле {field} должно быть списком URI.", 422, field=field)
        values = list(dict.fromkeys(value.strip() for value in values if value.strip()))
        data[field] = [_validate_oauth_uri(value, field) for value in values]

    if not data['redirect_uris']:
        raise LogicException("Нужен хотя бы один redirect URI.", 422, field='redirect_uris')

    scopes = data.get('allowed_scopes', ['openid', 'profile', 'email', 'roles'])
    if not isinstance(scopes, list) or not all(isinstance(scope, str) for scope in scopes):
        raise LogicException("allowed_scopes должен быть списком строк.", 422, field='allowed_scopes')
    scopes = list(dict.fromkeys(scopes))
    invalid_scopes = set(scopes) - OAUTH_SCOPES
    if invalid_scopes or 'openid' not in scopes:
        raise LogicException("Клиент должен иметь scope openid и только поддерживаемые scopes.", 422)
    data['allowed_scopes'] = scopes

    roles = data.get('allowed_roles', ['student', 'teacher', 'admin'])
    if not isinstance(roles, list) or not roles or not all(isinstance(role, str) for role in roles):
        raise LogicException("Нужно выбрать хотя бы одну допустимую роль.", 422, field='allowed_roles')
    invalid_roles = set(roles) - ROLE_CODES
    if invalid_roles:
        raise LogicException(f"Неизвестные роли: {', '.join(sorted(invalid_roles))}.", 422)
    data['allowed_roles'] = list(dict.fromkeys(roles))

    for field, default in (('is_confidential', True), ('is_active', True)):
        data[field] = data.get(field, default)
        if not isinstance(data[field], bool):
            raise LogicException(f"Поле {field} должно быть boolean.", 422, field=field)

    data['name'] = data['name'].strip()
    data['description'] = description.strip()
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


def _validate_form_fields(fields, field_name):
    if not isinstance(fields, list):
        raise LogicException(f"Поле {field_name} должно быть списком.", 422, field=field_name)

    for index, field in enumerate(fields):
        if not isinstance(field, dict):
            raise LogicException(
                f"Поле формы #{index + 1} должно быть объектом JSON.",
                422,
                field=field_name,
            )

        name = field.get('name')
        if not isinstance(name, str) or not name.strip() or len(name.strip()) > 256:
            raise LogicException(
                f"Некорректное название поля формы #{index + 1}.",
                422,
                field=field_name,
            )

        field_type = field.get('type')
        if field_type not in FORM_FIELD_TYPES:
            raise LogicException(
                f"Неизвестный тип поля формы #{index + 1}.",
                422,
                field=field_name,
            )

        for boolean_key in ('required', 'showoff'):
            if boolean_key in field and not isinstance(field[boolean_key], bool):
                raise LogicException(
                    f"Параметр {boolean_key} поля формы #{index + 1} должен быть boolean.",
                    422,
                    field=field_name,
                )

        options = field.get('options', [])
        if not isinstance(options, list) or not all(isinstance(option, str) for option in options):
            raise LogicException(
                f"Варианты поля формы #{index + 1} должны быть списком строк.",
                422,
                field=field_name,
            )

        field['name'] = name.strip()
        field['options'] = list(dict.fromkeys(option.strip() for option in options if option.strip()))

    return fields


def validate_form_category(data):
    if not isinstance(data, dict):
        raise LogicException("Описание категории должно быть объектом JSON.", 422)

    name = data.get('name')
    if not isinstance(name, str) or not name.strip():
        raise LogicException("Название категории обязательно.", 400, field='name')
    if len(name.strip()) > 256:
        raise LogicException("Название категории длиннее 256 символов.", 400, field='name')
    data['name'] = name.strip()

    params = data.get('params', {})
    if not isinstance(params, dict):
        raise LogicException("Поле params должно быть объектом JSON.", 422, field='params')

    for key in ('is_hidden', 'is_private'):
        if key in params and not isinstance(params[key], bool):
            raise LogicException(f"Параметр {key} должен быть boolean.", 422, field=key)

    can_create = params.get('can_create', [])
    if not isinstance(can_create, list) or not all(isinstance(role, str) for role in can_create):
        raise LogicException("Параметр can_create должен быть списком ролей.", 422, field='can_create')
    invalid_roles = set(can_create) - ROLE_CODES
    if invalid_roles:
        raise LogicException(
            f"Неизвестные роли в can_create: {', '.join(sorted(invalid_roles))}.",
            422,
            field='can_create',
        )
    params['can_create'] = list(dict.fromkeys(can_create))

    grouping = params.get('show_off_grouping', [])
    if not isinstance(grouping, list) or not all(isinstance(item, str) for item in grouping):
        raise LogicException(
            "Параметр show_off_grouping должен быть списком названий полей.",
            422,
            field='show_off_grouping',
        )
    params['show_off_grouping'] = list(dict.fromkeys(item.strip() for item in grouping if item.strip()))

    data['params'] = params
    data['common_fields'] = _validate_form_fields(data.get('common_fields', []), 'common_fields')
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
