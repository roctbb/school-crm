from flask import request
from validate_email_address import validate_email

from app import LogicException
from app.validators.helpers import should_have, should_be_unique
from app.models import User


def validate_signup(data):
    should_have(data, 'password', min_length=6, max_length=32)
    should_have(data, 'name', min_length=1, max_length=256)
    should_have(data, 'email', min_length=1, max_length=120)
    should_have(data, 'invite_code', min_length=1, max_length=120)

    if not validate_email(data.get('email')):
        raise LogicException("Поле email некорректно", 400)

    should_be_unique(data, 'email', User)
    should_be_unique(data, 'name', User)

    return data


def validate_login(data):
    should_have(data, 'email', min_length=1, max_length=120)
    should_have(data, 'password', min_length=1, max_length=32)

    return data
