from validate_email_address import validate_email

from .common import *
from application.models import ObjectType, Form, Object


def validate_object(data):
    should_have(data, 'name', min_length=1, max_length=1024)

    # Check "params" and "attributes" are JSON and optional
    if not isinstance(data.get('params', {}), dict):
        raise LogicException("Поле params должно быть объектом JSON.", 422)
    if not isinstance(data.get('attributes', {}), dict):
        raise LogicException("Поле attributes должно быть объектом JSON.", 422)

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

