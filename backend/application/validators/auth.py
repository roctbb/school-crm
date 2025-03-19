from .common import *
from validate_email_address import validate_email
from application.models import User, Invitation


def validate_signup(data):
    should_have(data, 'password', min_length=6, max_length=32)
    should_have(data, 'name', min_length=1, max_length=256)
    should_have(data, 'email', min_length=1, max_length=120)
    should_have(data, 'invite', min_length=1, max_length=120)

    should_exist(data, 'invite', Invitation, 'key')

    if not validate_email(data.get('email')):
        raise LogicException("Поле email некорректно", 400)

    should_be_unique(data, 'email', User)
    should_be_unique(data, 'name', User)

    return data


def validate_login(data):
    should_have(data, 'email', min_length=1, max_length=120)
    should_have(data, 'password', min_length=6, max_length=32)

    return data


def validate_reset_email_request(data):
    should_have(data, 'email', min_length=1, max_length=120)

    if not validate_email(data.get('email')):
        raise LogicException("Поле email некорректно", 400)

    should_exist(data, 'email', User)

    return data


def validate_reset_request(data):
    should_have(data, 'password', min_length=6, max_length=32)
    should_have(data, 'reset_token', min_length=6, max_length=100)

    return data
