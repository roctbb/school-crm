from validate_email_address import validate_email

from .common import *
from app.models import ObjectType, Form, Object

def validate_object(data):
    should_have(data, 'name', min_length=1, max_length=100)
    should_have(data, 'type_id', min_length=1)

    # Check "params" and "attributes" are JSON and optional
    if not isinstance(data.get('params', {}), dict):
        raise LogicException("Поле params должно быть объектом JSON.", 422)
    if not isinstance(data.get('attributes', {}), dict):
        raise LogicException("Поле attributes должно быть объектом JSON.", 422)

    should_exist(data, 'type_id', ObjectType, 'id')

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
    should_have(data, 'form_id', min_length=1)
    should_have(data, 'object_id', min_length=1)

    # Check "params" and "answers" are JSON objects
    if not isinstance(data.get('params', {}), dict):
        raise LogicException("Поле params должно быть объектом JSON.", 422)
    if not isinstance(data.get('answers', {}), dict):
        raise LogicException("Поле answers должно быть объектом JSON.", 422)

    should_exist(data, 'form_id', Form, 'id')
    should_exist(data, 'object_id', Object, 'id')

    return data


def validate_invitation(data):
    should_have(data, 'email', min_length=1, max_length=100)
    should_have(data, 'role', min_length=1, max_length=100)

    if not validate_email(data.get('email')):
        raise ValueError("Поле email некорректно.")

    if data.get('object_id') is not None:
        should_exist(data, 'object_id', Object, 'id')

    return data
